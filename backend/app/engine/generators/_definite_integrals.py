"""Definite integrals, Riemann sums, parts and substitution (#268)."""

import sympy as sp

from app.engine.answers.computational import FormulaAnswer
from app.engine.blocks.analysis_one import X
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._sequence_limits import finish


def definite(
    integrand: sp.Expr,
    primitive: sp.Expr,
    lo: sp.Expr | int,
    hi: sp.Expr | int,
    method: str,
    work: str = "",
    *,
    endpoint_limit: bool = False,
) -> Built:
    lower_value = sp.limit(primitive, X, lo, dir="+") if endpoint_limit else primitive.subs(X, lo)
    upper_value = primitive.subs(X, hi)
    # Keep small logarithm arguments instead of combining them into large integer powers.
    value = sp.expand(sp.expand_log(upper_value - lower_value))
    bounds = rf"_{{{tex(lo)}}}^{{{tex(hi)}}}"
    calculation = (
        rf"\left[{tex(primitive)}\right]{bounds}"
        rf"=\left({tex(upper_value)}\right)-\left({tex(lower_value)}\right)={tex(value)}."
    )
    return finish(
        rf"\text{{Evaluate }}\int{bounds}{tex(integrand)}\,dx.",
        FormulaAnswer(value),
        method,
        rf"{work},\quad {calculation}" if work else calculation,
    )


NEWTON_LEIBNIZ = r"\text{Find a primitive and apply the Newton--Leibniz formula.}"


def root_and_reciprocal_root(a: int, b: int, c: int) -> Built:
    return definite(
        a * sp.sqrt(X) + b / sp.sqrt(X),
        2 * a * X ** sp.Rational(3, 2) / 3 + 2 * b * sp.sqrt(X),
        c,
        c + 2,
        r"\text{Integrate the powers }x^{1/2}\text{ and }x^{-1/2}\text{ separately.}",
    )


def linear_quotient_value(a: int, b: int, c: int) -> Built:
    f = (X - a) / (X + b)
    reduced = 1 - (a + b) / (X + b)
    return definite(
        f,
        X - (a + b) * sp.log(X + b),
        0,
        c + 1,
        rf"{tex(f)}={tex(reduced)}.\quad {NEWTON_LEIBNIZ}",
    )


def arctangent_value(a: int, b: int, c: int) -> Built:
    return definite(
        c / (X**2 + a**2),
        sp.Rational(c, a) * sp.atan(X / a),
        0,
        b + 1,
        rf"\text{{Scale the arctangent rule with }}u=x/{a}.\quad {NEWTON_LEIBNIZ}",
    )


def polynomial_product_value(a: int, b: int, c: int) -> Built:
    return definite(
        X * (a + b * X**3),
        a * X**2 / 2 + b * X**5 / 5,
        -a,
        c,
        rf"\text{{Distribute the factor }}x\text{{ and integrate }}{tex(a * X + b * X**4)}.",
    )


def reciprocal_powers_value(a: int, b: int, c: int) -> Built:
    return definite(
        a / X**3 - b / X**2 + c / X**4,
        -a / (2 * X**2) + b / X - c / (3 * X**3),
        1,
        a + 1,
        r"\text{Use the power rule termwise on the positive interval.}",
    )


def tangent_square_value(a: int, b: int, c: int) -> Built:
    return definite(
        a * sp.tan(b * X) ** 2,
        sp.Rational(a, b) * sp.tan(b * X) - a * X,
        0,
        sp.pi / (3 * b),
        r"\tan^2u=\sec^2u-1.\quad \text{Integrate both terms.}",
    )


def riemann(sum_tex: str, integrand: sp.Expr, primitive: sp.Expr) -> Built:
    value = sp.simplify(primitive.subs(X, 1) - primitive.subs(X, 0))
    return finish(
        rf"\text{{Evaluate }}\lim_{{n\to\infty}}\left({sum_tex}\right).",
        FormulaAnswer(value),
        r"\text{The integrand is continuous on }[0,1]\text{. Use right endpoints }x_k=k/n"
        r"\text{ and width }\Delta x=1/n\text{, so the sums converge to its integral.}",
        rf"\int_0^1{tex(integrand)}\,dx=\left[{tex(primitive)}\right]_0^1={tex(value)}.",
    )


def riemann_power_function(a: int, b: int, c: int) -> sp.Expr:
    return a * X ** (c + 1)


def riemann_cosine_function(a: int, b: int, c: int) -> sp.Expr:
    return b * sp.cos(sp.pi * X / (a + 2))


def riemann_root_function(a: int, b: int, c: int) -> sp.Expr:
    return a * sp.sqrt(b + c * X)


def riemann_power(a: int, b: int, c: int) -> Built:
    power = c + 1
    return riemann(
        rf"\frac{{{a}}}{{n^{{{power + 1}}}}}\sum_{{k=1}}^n k^{{{power}}}",
        riemann_power_function(a, b, c),
        a * X ** (power + 1) / (power + 1),
    )


def riemann_cosine(a: int, b: int, c: int) -> Built:
    angle = sp.pi / (a + 2)
    return riemann(
        rf"\frac{{{b}}}{{n}}\sum_{{k=1}}^n\cos\!\left(\frac{{\pi k}}{{{a + 2}n}}\right)",
        riemann_cosine_function(a, b, c),
        b * sp.sin(angle * X) / angle,
    )


def riemann_shifted_root(a: int, b: int, c: int) -> Built:
    return riemann(
        rf"\frac{{{a}}}{{n\sqrt n}}\sum_{{k=1}}^n\sqrt{{{b}n+{c}k}}",
        riemann_root_function(a, b, c),
        2 * a * (b + c * X) ** sp.Rational(3, 2) / (3 * c),
    )


def parts_linear_exponential_value(a: int, b: int, c: int) -> Built:
    exponential = sp.exp(-a * X)
    primitive = -sp.Rational(c, a) * (X + sp.Rational(1, a)) * exponential
    return definite(
        c * X * exponential,
        primitive,
        -b,
        1,
        rf"u=x,\quad dv={tex(c * exponential)}\,dx,"
        rf"\quad v={tex(-sp.Rational(c, a) * exponential)}.",
        rf"uv-\int v\,du=-\frac{{{c}x}}{{{a}}}{tex(exponential)}"
        rf"+\frac{{{c}}}{{{a}}}\int{tex(exponential)}\,dx",
    )


def parts_square_exponential_value(a: int, b: int, c: int) -> Built:
    exponential = sp.exp(a * X)
    primitive = c * exponential * (X**2 / a - 2 * X / a**2 + sp.Rational(2, a**3))
    return definite(
        c * X**2 * exponential,
        primitive,
        0,
        b,
        rf"u=x^2,\quad dv={tex(c * exponential)}\,dx.\quad"
        r"\text{Apply parts again with }u=x.",
        rf"uv-\int v\,du=\frac{{{c}x^2}}{{{a}}}{tex(exponential)}"
        rf"-\frac{{{2 * c}}}{{{a}}}\int x{tex(exponential)}\,dx",
    )


def parts_logarithm_reciprocal_square(a: int, b: int, c: int) -> Built:
    return definite(
        c * sp.log(X) / X**2,
        -c * (sp.log(X) + 1) / X,
        sp.exp(sp.Rational(1, a + 1)),
        sp.exp(b),
        rf"u=\ln x,\quad dv=\frac{{{c}}}{{x^2}}\,dx,\quad v=-\frac{{{c}}}x.",
        rf"uv-\int v\,du=-\frac{{{c}\ln x}}x+\int\frac{{{c}}}{{x^2}}\,dx",
    )


def parts_linear_sine_value(a: int, b: int, c: int) -> Built:
    return definite(
        a * X * sp.sin(b * X),
        -a * X * sp.cos(b * X) / b + sp.Rational(a, b**2) * sp.sin(b * X),
        0,
        sp.pi / ((c + 2) * b),
        rf"u=x,\quad dv={tex(a * sp.sin(b * X))}\,dx,\quad"
        rf"v={tex(-sp.Rational(a, b) * sp.cos(b * X))}.",
        rf"uv-\int v\,du=uv+\frac{{{a}}}{{{b}}}\int\cos({tex(b * X)})\,dx",
    )


def parts_linear_one_plus_cosine(a: int, b: int, c: int) -> Built:
    return definite(
        a * X * (c + sp.cos(b * X)),
        a * (c * X**2 / 2 + X * sp.sin(b * X) / b + sp.cos(b * X) / b**2),
        0,
        sp.pi / b,
        r"\text{Split the polynomial term off. Use parts on the cosine term with }u=x.",
        rf"\int {a}x\cos({tex(b * X)})\,dx"
        rf"=\frac{{{a}x\sin({tex(b * X)})}}{{{b}}}"
        rf"-\frac{{{a}}}{{{b}}}\int\sin({tex(b * X)})\,dx",
    )


def parts_arcsine_value(a: int, b: int, c: int) -> Built:
    inverse = sp.asin(X / b)
    return definite(
        a * inverse,
        a * (X * inverse + sp.sqrt(b**2 - X**2)),
        0,
        b,
        rf"u={tex(inverse)},\quad dv={a}\,dx,\quad du=\frac{{dx}}{{\sqrt{{{b**2}-x^2}}}}.",
        rf"uv-\int v\,du={a}x\arcsin(x/{b})"
        rf"-\int\frac{{{a}x}}{{\sqrt{{{b**2}-x^2}}}}\,dx",
    )


def substitute_cosine_value(a: int, b: int, c: int) -> Built:
    exponential = sp.exp(c * sp.cos(b * X))
    return definite(
        a * sp.sin(b * X) * exponential,
        -sp.Rational(a, b * c) * exponential,
        0,
        sp.pi / b,
        rf"t=\cos({tex(b * X)}),\quad dt=-{b}\sin({tex(b * X)})\,dx,\quad t:1\to-1.",
        rf"-\frac{{{a}}}{{{b}}}\int_1^{{-1}}e^{{{c}t}}\,dt",
    )


def substitute_shifted_root_denominator(a: int, b: int, c: int) -> Built:
    t = X + b
    return definite(
        a * X / sp.sqrt(t),
        a * (2 * t ** sp.Rational(3, 2) / 3 - 2 * b * sp.sqrt(t)),
        1,
        c + 2,
        rf"t=x+{b},\quad dt=dx,\quad t:{b + 1}\to{b + c + 2}.",
        rf"{a}\int_{{{b + 1}}}^{{{b + c + 2}}}\frac{{t-{b}}}{{\sqrt t}}\,dt",
    )


def substitute_shifted_root_product(a: int, b: int, c: int) -> Built:
    t = sp.sqrt(X + b)
    return definite(
        a * X * t,
        2 * a * (t**5 / 5 - b * t**3 / 3),
        0,
        c + 1,
        rf"t=\sqrt{{x+{b}}},\quad x=t^2-{b},\quad dx=2t\,dt.",
        rf"{2 * a}\int_{{\sqrt{{{b}}}}}^{{\sqrt{{{b + c + 1}}}}}(t^4-{b}t^2)\,dt",
    )


def substitute_logarithm_value(a: int, b: int, c: int) -> Built:
    return definite(
        a * sp.log(X),
        a * (X * sp.log(X) - X),
        1,
        sp.exp(b),
        rf"t=\ln x,\quad x=e^t,\quad dx=e^t\,dt,\quad t:0\to{b}.",
        rf"{a}\int_0^{{{b}}}te^t\,dt={a}\left[(t-1)e^t\right]_0^{{{b}}}",
    )


def substitute_square_at_endpoint(a: int, b: int, c: int) -> Built:
    t = sp.sqrt(X)
    width = sp.sqrt(b)
    end = sp.Rational(b, (c + 1) ** 2)
    primitive = a * sp.log((width + t) / (width - t)) / width
    return definite(
        a / (t * (b - X)),
        primitive,
        0,
        end,
        r"x=t^2,\quad dx=2t\,dt.\quad \text{Take the lower endpoint as a right-hand limit.}",
        rf"\lim_{{\varepsilon\to0^+}}\int_{{\sqrt\varepsilon}}^{{{tex(sp.sqrt(end))}}}"
        rf"\frac{{{2 * a}}}{{{b}-t^2}}\,dt",
        endpoint_limit=True,
    )


def substitute_quarter_circle(a: int, b: int, c: int) -> Built:
    f = a * sp.sqrt(b**2 - X**2)
    primitive = (X * f + a * b**2 * sp.asin(X / b)) / 2
    return definite(
        f,
        primitive,
        0,
        b,
        rf"x={b}\sin t,\quad dx={b}\cos t\,dt,\quad 0\le t\le\pi/2.",
        rf"{a * b**2}\int_0^{{\pi/2}}\cos^2t\,dt"
        rf"={a * b**2}\left[\frac t2+\frac{{\sin 2t}}4\right]_0^{{\pi/2}}",
    )


def substitute_exponential_value(a: int, b: int, c: int) -> Built:
    t = sp.exp(b * X)
    return definite(
        a * t / (t**2 + c**2),
        sp.Rational(a, b * c) * sp.atan(t / c),
        0,
        sp.log(c + 1) / b,
        rf"t=e^{{{tex(b * X)}}},\quad dt={b}t\,dx,\quad t:1\to{c + 1}.",
        rf"\frac{{{a}}}{{{b}}}\int_1^{{{c + 1}}}\frac{{dt}}{{t^2+{c**2}}}",
    )


def parts_linear_cosine_exam(a: int, b: int, c: int) -> Built:
    return definite(
        a * X * sp.cos(b * X),
        a * X * sp.sin(b * X) / b + sp.Rational(a, b**2) * sp.cos(b * X),
        0,
        sp.pi / b,
        rf"u=x,\quad dv={tex(a * sp.cos(b * X))}\,dx,\quad"
        rf"v={tex(sp.Rational(a, b) * sp.sin(b * X))}.",
        rf"uv-\int v\,du=uv-\frac{{{a}}}{{{b}}}\int\sin({tex(b * X)})\,dx",
    )
