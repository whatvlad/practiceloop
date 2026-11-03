"""Global real IVPs with exact residual/initial data and Laplace certificates."""

from functools import cache
from typing import Any

import sympy as sp

from app.engine.blocks.analysis_two import AnalysisTwoData, AnalysisTwoForm, X, finish

S = sp.Symbol("s", positive=True)


def laplace_table(solution: Any) -> Any:
    """Linear real exponential/sine/cosine table; no parsing or numerical solver."""
    result = sp.S.Zero
    for term in sp.Add.make_args(sp.expand(solution)):
        coefficient, rest = term.as_independent(X, as_Add=False)
        if rest == 1:
            result += coefficient / S
            continue
        if rest.func not in (sp.exp, sp.sin, sp.cos):
            raise ValueError("Unsupported Laplace table entry")
        frequency = sp.diff(rest.args[0], X)
        if frequency.free_symbols or sp.simplify(rest.args[0] - frequency * X) != 0:
            raise ValueError("Laplace argument must be linear with no shift")
        if rest.func == sp.exp:
            result += coefficient / (S - frequency)
        elif rest.func == sp.sin:
            result += coefficient * frequency / (S**2 + frequency**2)
        else:
            result += coefficient * S / (S**2 + frequency**2)
    return sp.cancel(result)


@cache
def evaluate(kind: str, form: AnalysisTwoForm) -> AnalysisTwoData:
    a, b, c = map(sp.Integer, (form.a, form.b, form.c))
    details: tuple[str, ...]
    derivative_initial: Any = None
    if kind == "ode-separable-exponential":
        solution = b * sp.exp(a * X**2 / 2)
        initial = b
        residual = sp.diff(solution, X) - a * X * solution
        prompt = rf"Solve \(y'={a}xy,\ y(0)={b}\) on R. Enter \(y(x)\)."
        details = (
            rf"\frac{{dy}}{{y}}={a}x\,dx",
            rf"\ln|y|={sp.latex(a / 2)}x^2+C",
            rf"y(0)={b}>0\implies y={b}e^{{{sp.latex(a / 2)}x^2}}",
        )
    elif kind == "ode-separable-root":
        solution = sp.sqrt(a * X**2 + b**2)
        initial = b
        residual = solution * sp.diff(solution, X) - a * X
        if (a * X**2 + b**2).is_positive is not True:
            raise ValueError("Positive IVP branch must exist on all R")
        prompt = (
            rf"Solve \(y'={a}x/y,\ y(0)={b}\). "
            "Give the positive solution on all R."
        )
        details = (
            rf"y\,dy={a}x\,dx",
            rf"y^2={a}x^2+C,\quad C={b**2}",
            rf"{a}x^2+{b**2}>0\text{{ for all real }}x",
        )
    elif kind == "ode-linear":
        particular = b / a * X + (c * a - b) / a**2
        solution = particular + (c - particular.subs(X, 0)) * sp.exp(-a * X)
        initial = c
        residual = sp.diff(solution, X) + a * solution - b * X - c
        prompt = (
            rf"Solve \(y'+{a}y={b}x+{c},\ y(0)={c}\) "
            r"on R. Enter \(y(x)\)."
        )
        details = (
            rf"\mu(x)=e^{{{a}x}}",
            rf"(e^{{{a}x}}y)'=e^{{{a}x}}({b}x+{c})",
            rf"y_p={sp.latex(particular)},\quad y=y_p+Ce^{{-{a}x}}",
            rf"C={sp.latex(c - particular.subs(X, 0))}",
        )
    elif kind == "ode-linear-variable":
        solution = (b + c / (2 * a)) * sp.exp(a * X**2) - c / (2 * a)
        initial = b
        residual = sp.diff(solution, X) - 2 * a * X * solution - c * X
        prompt = (
            rf"Solve \(y'-{2 * a}xy={c}x,\ y(0)={b}\) "
            r"on R. Enter \(y(x)\)."
        )
        details = (
            rf"\mu(x)=e^{{-{a}x^2}}",
            rf"(\mu y)'={c}xe^{{-{a}x^2}}",
            rf"\mu y=-{sp.latex(c / (2 * a))}e^{{-{a}x^2}}+C",
            rf"C={sp.latex(b + c / (2 * a))}",
        )
    elif kind == "ode-harmonic":
        solution = b * sp.cos(a * X) + c * sp.sin(a * X)
        initial, derivative_initial = b, a * c
        residual = sp.diff(solution, X, 2) + a**2 * solution
        prompt = (
            rf"Solve \(y''+{a**2}y=0,\ y(0)={b},\ y'(0)={a * c}\). "
            r"Enter \(y(x)\) on R."
        )
        details = (rf"y=C_1\cos({a}x)+C_2\sin({a}x)", rf"C_1={b},\quad {a}C_2={a * c}")
    elif kind == "ode-distinct-roots":
        solution = (b + c / 2) * sp.exp(a * X) - c / 2 * sp.exp(-a * X)
        initial, derivative_initial = b, a * (b + c)
        residual = sp.diff(solution, X, 2) - a**2 * solution
        prompt = (
            rf"Solve \(y''-{a**2}y=0,\ y(0)={b},\ y'(0)={a * (b + c)}\). "
            r"Enter \(y(x)\) on R."
        )
        details = (
            rf"r^2-{a**2}=0\implies r=\pm {a}",
            rf"y=C_1e^{{{a}x}}+C_2e^{{-{a}x}}",
            rf"C_1+C_2={b},\quad {a}(C_1-C_2)={a * (b + c)}",
        )
    elif kind == "ode-repeated-root":
        solution = (b + c * X) * sp.exp(a * X)
        initial, derivative_initial = b, a * b + c
        residual = sp.diff(solution, X, 2) - 2 * a * sp.diff(solution, X) + a**2 * solution
        prompt = (
            rf"Solve \(y''-{2 * a}y'+{a**2}y=0,\ y(0)={b},\ "
            rf"y'(0)={a * b + c}\). Enter \(y(x)\) on R."
        )
        details = (
            rf"(r-{a})^2=0",
            rf"y=(C_1+C_2x)e^{{{a}x}}",
            rf"C_1={b},\quad {a}C_1+C_2={a * b + c}",
        )
    elif kind == "ode-resonance":
        solution = (
            c * sp.cos(a * X) + b / (2 * a**2) * sp.sin(a * X) - b / (2 * a) * X * sp.cos(a * X)
        )
        initial, derivative_initial = c, sp.Integer(0)
        residual = sp.diff(solution, X, 2) + a**2 * solution - b * sp.sin(a * X)
        prompt = (
            rf"Solve \(y''+{a**2}y={b}\sin({a}x),\ y(0)={c},\ "
            r"y'(0)=0\). Enter \(y(x)\) on R."
        )
        details = (
            rf"y_p=-{sp.latex(b / (2 * a))}x\cos({a}x)",
            rf"y=C_1\cos({a}x)+C_2\sin({a}x)+y_p",
            rf"C_1={c},\quad C_2={sp.latex(b / (2 * a**2))}",
        )
    elif kind == "ode-laplace-exponential":
        solution = b / (a + c) * sp.exp(c * X) + (b - b / (a + c)) * sp.exp(-a * X)
        initial = b
        residual = sp.diff(solution, X) + a * solution - b * sp.exp(c * X)
        transform = (b + b / (S - c)) / (S + a)
        if sp.cancel(laplace_table(solution) - transform) != 0:
            raise ValueError("Laplace transform certificate failed")
        prompt = (
            rf"Use Laplace transforms to solve \(y'+{a}y={b}e^{{{c}x}},\ "
            rf"y(0)={b}\). Enter \(y(x)\) on R."
        )
        details = (
            rf"(s+{a})Y(s)-{b}=\frac{{{b}}}{{s-{c}}},\quad s>{c}",
            rf"Y(s)={sp.latex(transform)}",
            rf"Y(s)={sp.latex(sp.apart(transform, S))}",
            r"\mathcal L^{-1}\{1/(s-k)\}=e^{kx}",
        )
    elif kind == "ode-laplace-oscillator":
        solution = b / a**2 * (1 - sp.cos(a * X)) + c / a * sp.sin(a * X)
        initial, derivative_initial = sp.Integer(0), c
        residual = sp.diff(solution, X, 2) + a**2 * solution - b
        transform = (c + b / S) / (S**2 + a**2)
        if sp.cancel(laplace_table(solution) - transform) != 0:
            raise ValueError("Second-order Laplace transform certificate failed")
        prompt = (
            rf"Use Laplace transforms to solve \(y''+{a**2}y={b},\ "
            rf"y(0)=0,\ y'(0)={c}\). Enter \(y(x)\) on R."
        )
        details = (
            rf"(s^2+{a**2})Y(s)-{c}={b}/s,\quad s>0",
            rf"Y(s)={sp.latex(transform)}",
            rf"Y(s)={sp.latex(sp.apart(transform, S))}",
            r"\mathcal L\{\cos(ax)\}=s/(s^2+a^2),\quad\mathcal L\{\sin(ax)\}=a/(s^2+a^2)",
        )
    else:
        raise ValueError("Unknown differential-equation form")
    if sp.simplify(residual) != 0 or sp.simplify(solution.subs(X, 0) - initial) != 0:
        raise ValueError("ODE residual or initial value failed")
    if derivative_initial is not None:
        if sp.simplify(sp.diff(solution, X).subs(X, 0) - derivative_initial) != 0:
            raise ValueError("ODE initial derivative failed")
    return finish(prompt, solution, solution, details, symbolic=True)
