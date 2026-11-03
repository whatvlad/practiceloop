"""Bounded Analysis I forms; all computations are exact except certified bisection.

Classification exercises explicitly request a numeric code. Expressions and values
use the existing bounded expression grammar, without teaching the parser infinity,
intervals or prose. Worked solutions still display the complete mathematical claim.
"""

from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from typing import Any

import sympy as sp
from pydantic import Field

from app.engine.models import Parameters, Step
from app.math_input import VariableDomain

X = sp.Symbol("x", real=True)
N = sp.Symbol("n", positive=True, integer=True)
H = sp.Symbol("h", real=True)


class AnalysisOneForm(Parameters):
    a: int = Field(ge=1, le=5)
    b: int = Field(ge=1, le=5)
    c: int = Field(ge=1, le=5)


@dataclass(frozen=True)
class AnalysisOneData:
    statement: str
    expected: Any
    variables: dict[str, VariableDomain]
    steps: tuple[Step, ...]


def exp_bounds(x: Fraction) -> tuple[Fraction, Fraction]:
    """Positive rational Taylor enclosure: tail ratios <= x/82 after term 80."""
    if not 0 <= x <= 5:
        raise ValueError("Bisection exponent is outside [0,5]")
    term = total = Fraction(1)
    for k in range(1, 81):
        term *= x / k
        total += term
    next_term = term * x / 81
    return total, total + next_term / (1 - x / 82)


def bisect_exp(a: int) -> tuple[Fraction, tuple[tuple[Fraction, Fraction], ...]]:
    """Six certified bisections of exp(x)+x=a+1 on [0,a]."""
    if type(a) is not int or not 1 <= a <= 5:
        raise ValueError("Bisection parameter is outside [1,5]")
    lo, hi = Fraction(0), Fraction(a)
    intervals = []
    for _ in range(6):
        mid = (lo + hi) / 2
        lower, upper = exp_bounds(mid)
        if lower + mid > a + 1:
            hi = mid
        elif upper + mid < a + 1:
            lo = mid
        else:
            raise ValueError("Taylor bounds cannot certify the bisection sign")
        intervals.append((lo, hi))
    return (lo + hi) / 2, tuple(intervals)


@cache
def evaluate(kind: str, p: AnalysisOneForm) -> AnalysisOneData:
    a, b, c = map(sp.Integer, (p.a, p.b, p.c))
    variables: dict[str, VariableDomain] = {}
    proof: Any
    details: tuple[str, ...]
    if kind == "parity":
        power = 2 if p.b % 2 else 3
        f = a * X**power
        expected = sp.Integer(1 if power == 2 else -1)
        proof = sp.Integer(1 if sp.expand(f.subs(X, -X) - f) == 0 else -1)
        if sp.expand(f.subs(X, -X) - expected * f) != 0:
            raise ValueError("Parity identity failed")
        prompt = rf"Classify \(f(x)={sp.latex(f)}\) on the real line: enter 1 for even, -1 for odd."
        details = (rf"f(-x)={sp.latex(f.subs(X, -X))}", rf"f(-x)={sp.latex(expected)}f(x)")
    elif kind == "domain":
        expected = b
        proof = sp.solve(X - b, X)[0]
        prompt = rf"Find the left endpoint of the real domain of \(f(x)=\sqrt{{x-{b}}}\)."
        details = (rf"x-{b}\geq0", rf"D=[{b},\infty)")
    elif kind == "composition":
        expected = a * (X**2 + c) + b
        proof = (a * X + b).subs(X, X**2 + c)
        prompt = rf"Find \(f(g(x))\) for \(f(x)={a}x+{b},\ g(x)=x^2+{c},\ x\in\mathbb R\)."
        variables = {"x": "real"}
        details = (rf"f(g(x))={a}(x^2+{c})+{b}",)
    elif kind == "inverse":
        expected = (X - b) / a
        proof = sp.solve(a * H + b - X, H)[0]
        if sp.simplify(a * expected + b - X) != 0:
            raise ValueError("Inverse failed composition")
        prompt = rf"Find \(f^{{-1}}(x)\) for the bijection \(f(x)={a}x+{b}\) from R to R."
        variables = {"x": "real"}
        details = (rf"y={a}x+{b}\iff x=\frac{{y-{b}}}{{{a}}}",)
    elif kind == "sequence-increment":
        seq = a - b / N
        expected = b / (c * (c + 1))
        proof = (seq.subs(N, c + 1) - seq.subs(N, c)).simplify()
        prompt = (
            rf"For \(u_n={a}-{b}/n,\ n\geq1\), calculate "
            rf"\(u_{{{c + 1}}}-u_{{{c}}}\). Use its sign to study monotonicity."
        )
        details = (rf"u_{{n+1}}-u_n=\frac{{{b}}}{{n(n+1)}}>0",)
    elif kind == "sequence-bound":
        expected = a
        proof = sp.limit(a * N / (N + b), N, sp.oo)
        prompt = rf"Find the least upper bound of \(u_n={a}n/(n+{b}),\ n\geq1\)."
        details = (rf"{a}-u_n=\frac{{{a * b}}}{{n+{b}}}>0", rf"u_n\longrightarrow {a}")
    elif kind == "sequence-rational":
        expected = a / c
        proof = sp.limit((a * N + b) / (c * N + 1), N, sp.oo)
        prompt = rf"Find \(\lim_{{n\to\infty}}\frac{{{a}n+{b}}}{{{c}n+1}}\)."
        details = (rf"\frac{{{a}+{b}/n}}{{{c}+1/n}}\longrightarrow\frac{{{a}}}{{{c}}}",)
    elif kind == "sequence-oscillation":
        expected = sp.Integer(0)
        proof = sp.Integer(int(b + a == b - a))
        prompt = rf"Does \(u_n={b}+{a}(-1)^n\) converge? Enter 1 for yes, 0 for no."
        details = (
            rf"u_{{2n}}={b + a},\quad u_{{2n+1}}={b - a}",
            rf"{b + a}\ne {b - a}\implies\text{{divergence}}",
        )
    elif kind == "sequence-unbounded":
        expected = sp.Integer(0)
        proof = sp.Integer(int(sp.limit(a * N + b, N, sp.oo).is_finite is True))
        prompt = rf"Is \(u_n={a}n+{b},\ n\geq1\), bounded? Enter 1 for yes, 0 for no."
        details = (r"u_n\longrightarrow+\infty",)
    elif kind == "sequence-exponential":
        expected = sp.exp(a)
        proof = sp.exp(sp.limit(N * sp.log(1 + a / N), N, sp.oo))
        prompt = rf"Find \(\lim_{{n\to\infty}}(1+{a}/n)^n\)."
        details = (rf"\log u_n=n\log(1+{a}/n)\longrightarrow {a}",)
    elif kind == "sequence-radical":
        expected = a / 2
        proof = sp.limit(sp.sqrt(N**2 + a * N) - N, N, sp.oo)
        prompt = rf"Find \(\lim_{{n\to\infty}}(\sqrt{{n^2+{a}n}}-n)\)."
        details = (rf"\sqrt{{n^2+{a}n}}-n=\frac{{{a}}}{{\sqrt{{1+{a}/n}}+1}}",)
    elif kind == "limit-polynomial":
        f = a * X**2 + b * X + c
        expected = a * b**2 + b**2 + c
        proof = sp.limit(f, X, b)
        prompt = rf"Find \(\lim_{{x\to{b}}}({sp.latex(f)})\)."
        details = (rf"\lim_{{x\to{b}}}f(x)=f({b})",)
    elif kind == "limit-cancel":
        f = (X**2 - b**2) / (X - b)
        expected = 2 * b
        proof = sp.limit(f, X, b)
        prompt = rf"Find \(\lim_{{x\to{b}}}\frac{{x^2-{b**2}}}{{x-{b}}}\)."
        details = (rf"x\ne {b}:\quad\frac{{x^2-{b**2}}}{{x-{b}}}=x+{b}",)
    elif kind in {"limit-sine", "limit-exponential"}:
        f = sp.sin(a * X) / X if kind == "limit-sine" else (sp.exp(a * X) - 1) / X
        expected = a
        proof = sp.limit(f, X, 0)
        prompt = rf"Use a standard limit to find \(\lim_{{x\to0}}{sp.latex(f)}\)."
        details = (
            rf"t={a}x,\quad {sp.latex(f)}={a}\cdot "
            + (r"\frac{\sin t}{t}" if kind == "limit-sine" else r"\frac{e^t-1}{t}"),
        )
    elif kind in {"limit-left", "limit-right"}:
        direction = "-" if kind == "limit-left" else "+"
        expected = sp.Integer(-1 if direction == "-" else 1)
        proof = sp.limit(sp.Abs(X - b) / (X - b), X, b, dir=direction)
        prompt = rf"Find \(\lim_{{x\to {b}^{{{direction}}}}}\frac{{|x-{b}|}}{{x-{b}}}\)."
        details = (rf"x\to {b}^{{{direction}}}:\quad |x-{b}|=({expected})(x-{b})",)
    elif kind == "limit-infinite":
        expected = sp.Integer(1)
        proof = sp.Integer(int(sp.limit(a / (X - b) ** 2, X, b) == sp.oo))
        prompt = (
            rf"Classify \(\lim_{{x\to {b}}}{a}/(x-{b})^2\): "
            "enter 1 for positive infinity, -1 for negative infinity, 0 for finite."
        )
        details = (rf"(x-{b})^2\to0^+,\quad\frac{{{a}}}{{(x-{b})^2}}\to+\infty",)
    elif kind == "limit-infinity":
        expected = a / c
        proof = sp.limit((a * X**2 + b) / (c * X**2 + 1), X, sp.oo)
        prompt = rf"Find \(\lim_{{x\to\infty}}\frac{{{a}x^2+{b}}}{{{c}x^2+1}}\)."
        details = (rf"\frac{{{a}+{b}/x^2}}{{{c}+1/x^2}}\longrightarrow {sp.latex(expected)}",)
    elif kind == "asymptote":
        expected = a * X + b
        proof = sp.div(a * X**2 + b * X + c, X)[0]
        if sp.limit(c / X, X, sp.oo) != 0:
            raise ValueError("Asymptote remainder did not vanish")
        variables = {"x": "real"}
        prompt = (
            r"Find the oblique asymptote \(y(x)\) at positive infinity of "
            rf"\(f(x)=({a}x^2+{b}x+{c})/x,\ x\ne0\)."
        )
        details = (rf"f(x)={a}x+{b}+{c}/x", rf"f(x)-({a}x+{b})\to0")
    elif kind == "continuity":
        expected = a * c + b
        proof = (a * X + b).subs(X, c)
        prompt = (
            rf"Choose \(k\) so \(f(x)=\begin{{cases}}{a}x+{b}&x<{c}\\"
            rf"k&x={c}\\{a}x+{b}&x>{c}\end{{cases}}\) is continuous."
        )
        details = (rf"\lim_{{x\to{c}^-}}f=\lim_{{x\to{c}^+}}f={a * c + b}=k",)
    elif kind == "lhopital":
        f = (sp.exp(a * X) - 1 - a * X) / X**2
        expected = a**2 / 2
        proof = sp.limit(f, X, 0)
        prompt = rf"Apply lHopital's rule to \(\lim_{{x\to0}}\frac{{e^{{{a}x}}-1-{a}x}}{{x^2}}\)."
        details = (
            rf"\frac{{{a}e^{{{a}x}}-{a}}}{{2x}}\quad(0/0)",
            rf"\frac{{{a**2}e^{{{a}x}}}}{{2}}\longrightarrow {sp.latex(expected)}",
        )
    elif kind == "bisection":
        mid, intervals = bisect_exp(p.a)
        expected = sp.Rational(mid.numerator, mid.denominator)
        proof = expected
        prompt = (
            rf"Solve \(e^x+x={a + 1}\) approximately: start with \([0,{a}]\), "
            "perform six bisections, and enter the midpoint of the remaining interval."
        )
        details = (
            (rf"F(0)=-{a}<0,\ F({a})>0,\ F'(x)=e^x+1>0",)
            + tuple(
                rf"I_{{{i + 1}}}=[{sp.latex(sp.Rational(lo))},{sp.latex(sp.Rational(hi))}]"
                for i, (lo, hi) in enumerate(intervals)
            )
            + (rf"|x_*-{sp.latex(expected)}|\leq {sp.latex(a / 128)}",)
        )
    elif kind in {"derivative-definition", "tangent"}:
        f = a * X**2 + b
        expected = 2 * a * c
        proof = sp.limit((f.subs(X, c + H) - f.subs(X, c)) / H, H, 0)
        prompt = (
            "Use the derivative definition to find "
            if kind == "derivative-definition"
            else "Find the tangent slope "
        ) + rf"\(f'({c})\) for \(f(x)={sp.latex(f)},\ x\in\mathbb R\)."
        details = (rf"\frac{{f({c}+h)-f({c})}}{{h}}={2 * a * c}+{a}h",)
    elif kind == "differential":
        expected = 3 * a * b**2 / c
        proof = sp.diff(a * X**3, X).subs(X, b) / c
        prompt = rf"For \(y={a}x^3\), find the differential \(dy\) at \(x={b}\) with \(dx=1/{c}\)."
        details = (rf"dy={3 * a}x^2\,dx", rf"dy={3 * a * b**2}\cdot\frac1{{{c}}}")
    elif kind == "chain":
        expected = 2 * a * X * sp.exp(a * X**2 + b)
        proof = sp.diff(sp.exp(a * X**2 + b), X)
        variables = {"x": "real"}
        prompt = rf"Differentiate \(f(x)=e^{{{a}x^2+{b}}},\ x\in\mathbb R\)."
        details = (rf"u={a}x^2+{b},\quad u'={2 * a}x",)
    elif kind == "mean-value":
        expected = c / 2
        f = a * X**2 + b * X
        proof = sp.solve(sp.diff(f, X) - (f.subs(X, c) - f.subs(X, 0)) / c, X)[0]
        prompt = (
            rf"For \(f(x)={sp.latex(f)}\) on \([0,{c}]\), "
            "find the point from Lagrange's mean value theorem."
        )
        details = (
            rf"f\in C[0,{c}]\cap C^1(0,{c})",
            rf"f'(x)={2 * a}x+{b}={a * c + b}\iff x={sp.latex(expected)}",
        )
    elif kind == "monotonicity":
        expected = a
        proof = max(sp.solve(sp.diff(X**3 - 3 * a**2 * X, X), X))
        prompt = (
            rf"For \(f(x)=x^3-{3 * a**2}x\), find the left endpoint "
            "of the rightmost interval of strict increase."
        )
        details = (
            rf"f'(x)=3(x-{a})(x+{a})",
            rf"f'>0:\ (-\infty,-{a})\cup({a},\infty);\quad f'<0:\ (-{a},{a})",
        )
    elif kind == "local-extremum":
        expected = c
        f = -a * (X - b) ** 2 + c
        proof = f.subs(X, sp.solve(sp.diff(f, X), X)[0])
        prompt = rf"Find the local maximum value of \(f(x)={sp.latex(f)},\ x\in\mathbb R\)."
        details = (rf"f'(x)=-{2 * a}(x-{b})=0\iff x={b}", rf"f''=-{2 * a}<0,\quad f({b})={c}")
    elif kind == "global-extremum":
        f = X**3 - 3 * a**2 * X
        expected = -2 * a**3
        proof = min(f.subs(X, k) for k in (0, a, 2 * a))
        prompt = rf"Find the global minimum value of \(f(x)=x^3-{3 * a**2}x\) on \([0,{2 * a}]\)."
        details = (
            rf"f'(x)=3(x-{a})(x+{a})",
            rf"f(0)=0,\ f({a})={-2 * a**3},\ f({2 * a})={2 * a**3}",
        )
    elif kind == "rectangle":
        expected = a**2 / 4
        area = X * (a - X)
        proof = area.subs(X, sp.solve(sp.diff(area, X), X)[0])
        prompt = rf"A rectangle has perimeter \({2 * a}\). Find its greatest possible area."
        details = (
            rf"A(w)=w({a}-w),\quad0<w<{a}",
            rf"A'(w)={a}-2w=0\iff w={sp.latex(a / 2)};\quad A''=-2<0",
        )
    elif kind == "box":
        volume = X * (a - 2 * X) ** 2
        expected = 2 * a**3 / 27
        candidates = [0, a / 2] + [v for v in sp.solve(sp.diff(volume, X), X) if 0 < v < a / 2]
        proof = max(volume.subs(X, v) for v in candidates)
        if sp.diff(volume, X).subs(X, a / 6) != 0:
            raise ValueError("Box stationary point failed")
        prompt = (
            rf"Cut squares of side \(x\) from a square card of side \({a}\), "
            "then fold an open box. Find its maximum volume for "
            rf"\(0<x<{sp.latex(a / 2)}\)."
        )
        details = (
            rf"V=x({a}-2x)^2",
            rf"V'=({a}-2x)({a}-6x);\quad x={sp.latex(a / 6)}",
            rf"V(0)=V({sp.latex(a / 2)})=0;\quad V({sp.latex(a / 6)})={sp.latex(expected)}",
        )
    else:
        raise ValueError(f"Unknown Analysis I form: {kind}")
    if sp.simplify(proof - expected) != 0 or expected.is_finite is False:
        raise ValueError(f"Analysis I proof failed: {kind}")
    steps = tuple(Step("reason", d) for d in details) + (Step("result", sp.latex(expected)),)
    return AnalysisOneData(prompt, expected, variables, steps)
