"""Definition, comparison and unbounded applications of improper integrals (#271)."""

import math
from dataclasses import replace

import sympy as sp

from app.engine.answers.computational import (
    CategoryAnswer,
    FormulaAnswer,
    LimitAnswer,
    OrderedAnswer,
)
from app.engine.blocks.analysis_one import X
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import path, plot
from app.engine.generators._sequence_limits import finish

CONVERGENCE = ("converges", "diverges")
FINITUDE = ("finite", "infinite")
VALUE_LABELS = ("Convergence", "Integral value")
TAIL_LABELS = ("Convergence", "Left tail", "Right tail", "Integral value")


def definition(
    integrand: sp.Expr, lo: sp.Expr | int, value: sp.Expr | str, method: str, work: str
) -> Built:
    converges = value not in (sp.oo, -sp.oo, "does_not_exist")
    answer = OrderedAnswer(
        (CategoryAnswer("converges" if converges else "diverges", CONVERGENCE), LimitAnswer(value)),
        VALUE_LABELS,
    )
    return finish(
        rf"\text{{Using the improper definition, classify "
        rf"}}\int_{{{tex(lo)}}}^\infty {tex(integrand)}\,dx."
        r"\text{ Give (converges or diverges; value). Use inf, -inf or dne for divergent limits.}",
        answer,
        method,
        work,
    )


def both_tails(
    integrand: sp.Expr, left: sp.Expr, right: sp.Expr, total: sp.Expr, method: str, work: str
) -> Built:
    converges = left not in (sp.oo, -sp.oo) and right not in (sp.oo, -sp.oo)
    answer = OrderedAnswer(
        (
            CategoryAnswer("converges" if converges else "diverges", CONVERGENCE),
            LimitAnswer(left),
            LimitAnswer(right),
            LimitAnswer(total),
        ),
        TAIL_LABELS,
    )
    return finish(
        rf"\text{{Classify }}\int_{{-\infty}}^\infty "
        rf"{tex(integrand)}\,dx\text{{ by splitting at zero.}}"
        r"\text{ Give (convergence; left-tail value; right-tail "
        r"value; full value). Each tail must converge independently.}",
        answer,
        method,
        work,
    )


def comparison(
    integrand: sp.Expr, lo: sp.Expr | int, converges: bool, method: str, certificate: str
) -> Built:
    return finish(
        rf"\text{{Use the stated comparison method to classify "
        rf"}}\int_{{{tex(lo)}}}^\infty {tex(integrand)}\,dx"
        r"\text{ as converges or diverges.}",
        CategoryAnswer("converges" if converges else "diverges", CONVERGENCE),
        method,
        certificate,
    )


def rational_tail_definition(a: int, b: int, c: int) -> Built:
    lo = b + c
    primitive = sp.Rational(a, b) * (sp.log(X - b) - sp.log(X))
    value = sp.Rational(a, b) * sp.log(sp.Rational(lo, c))
    return definition(
        a / (X * (X - b)),
        lo,
        value,
        rf"\frac{{{a}}}{{x(x-{b})}}=\frac{{{a}}}{{{b}}}\left(\frac1{{x-{b}}}-\frac1x\right).",
        rf"F(x)={tex(primitive)},\quad\lim_{{R\to\infty}}F(R)=0.\quad"
        rf"I=0-F({lo})={tex(value)}.",
    )


def root_quotient_divergence(a: int, b: int, c: int) -> Built:
    lo = (c + 1) ** 2
    primitive = 2 * b * (sp.sqrt(X) - sp.sqrt(a) * sp.atan(sp.sqrt(X / a)))
    return definition(
        b * sp.sqrt(X) / (X + a),
        lo,
        sp.oo,
        rf"t=\sqrt x,\quad dx=2t\,dt,\quad "
        rf"\frac{{{2 * b}t^2}}{{t^2+{a}}}={2 * b}-\frac{{{2 * a * b}}}{{t^2+{a}}}.",
        rf"F(x)={tex(primitive)}.\quad\arctan\sqrt{{x/{a}}}"
        rf"\text{{ is bounded while }}\sqrt x\to\infty"
        r"\text{, so the upper-endpoint limit is infinity.}",
    )


def oscillatory_linear_tail(a: int, b: int, c: int) -> Built:
    lo = 2 * sp.pi / b
    built = definition(
        a * X * sp.cos(b * X),
        lo,
        "does_not_exist",
        rf"\text{{Integration by parts gives }}F(R)=\frac{{{a}R\sin({b}R)}}{{{b}}}"
        rf"+\frac{{{a}\cos({b}R)}}{{{b * b}}}.",
        rf"R_n=2\pi n/{b}\Longrightarrow F(R_n)-F({tex(lo)})=0.\quad"
        rf"T_n=(2\pi n+\pi/2)/{b}\Longrightarrow F(T_n)-F({tex(lo)})"
        rf"=\frac{{{a}T_n}}{{{b}}}-\frac{{{a}}}{{{b * b}}}\to"
        rf"\infty.\quad\text{{The improper limit does not exist.}}",
    )
    visual = plot(
        "Oscillating truncated integral",
        "The truncated integral returns to zero on one endpoint sequence and grows on another.",
        [
            path(
                "Truncated integral",
                float(lo),
                float(lo + 6 * sp.pi / b),
                lambda r: a * r * math.sin(b * r) / b + a * (math.cos(b * r) - 1) / (b * b),
            )
        ],
    )
    return replace(built, visual=visual)


def exponential_root_tail(a: int, b: int, c: int) -> Built:
    primitive = -sp.Rational(2 * a, b) * sp.sqrt(c + sp.exp(-b * X))
    value = sp.Rational(2 * a, b) * (sp.sqrt(c + 1) - sp.sqrt(c))
    return definition(
        a * sp.exp(-b * X) / sp.sqrt(c + sp.exp(-b * X)),
        0,
        value,
        rf"u={c}+e^{{-{b}x}},\quad du=-{b}e^{{-{b}x}}\,dx.",
        rf"F(x)={tex(primitive)},\quad F(\infty)=-\frac{{{2 * a}\sqrt{{{c}}}}}{{{b}}}."
        rf"\quad I=F(\infty)-F(0)={tex(value)}.",
    )


def two_sided_quadratic_tail(a: int, b: int, c: int) -> Built:
    left = sp.Rational(a, c) * (sp.pi / 2 + sp.atan(sp.Rational(b, c)))
    right = sp.Rational(a, c) * (sp.pi / 2 - sp.atan(sp.Rational(b, c)))
    return both_tails(
        a / ((X + b) ** 2 + c * c),
        left,
        right,
        sp.pi * a / c,
        rf"F(x)=\frac{{{a}}}{{{c}}}\arctan\frac{{x+{b}}}{{{c}}}.\quad"
        r"\text{Take the limits at negative and positive infinity separately.}",
        rf"I_-={tex(left)},\quad I_+={tex(right)},\quad I=I_-+I_+={tex(sp.pi * a / c)}.",
    )


def two_sided_exponential_linear(a: int, b: int, c: int) -> Built:
    left = -sp.Rational(a, b * b)
    return both_tails(
        a * X * sp.exp(b * X),
        left,
        sp.oo,
        sp.oo,
        rf"F(x)=\frac{{{a}}}{{{b * b}}}e^{{{b}x}}({b}x-1).",
        rf"\lim_{{x\to-\infty}}F(x)=0,\quad F(0)={tex(left)},\quad"
        r"\lim_{x\to\infty}F(x)=\infty.\quad\text{The "
        r"left tail is finite and the right tail diverges.}",
    )


def root_product_comparison(a: int, b: int, c: int) -> Built:
    return comparison(
        a / (X * (sp.sqrt(X) + b)),
        1,
        True,
        r"\text{Use direct upper comparison with a convergent power integral.}",
        rf"0<\frac{{{a}}}{{x(\sqrt x+{b})}}\le\frac{{{a}}}{{x^{{3/2}}}}\quad(x\ge1)."
        r"\quad\int_1^\infty x^{-3/2}\,dx=2<\infty.",
    )


def squared_root_denominator_comparison(a: int, b: int, c: int) -> Built:
    return comparison(
        a / (sp.sqrt(X) + b) ** 2,
        (b + 1) ** 2,
        False,
        r"\text{Use a divergent harmonic lower comparison.}",
        rf"\sqrt x\ge{b}\Longrightarrow(\sqrt x+{b})^2\le4x.\quad"
        rf"\frac{{{a}}}{{(\sqrt x+{b})^2}}\ge\frac{{{a}}}{{4x}}."
        rf"\quad\int^\infty\frac{{dx}}x=\infty.",
    )


def polynomial_quotient_comparison(a: int, b: int, c: int) -> Built:
    return comparison(
        a * X * (X + b) / (X**4 + X + c),
        1,
        True,
        r"\text{Bound the numerator and denominator separately for }x\ge1.",
        rf"0<f(x)\le\frac{{{a}x(x+{b})}}{{x^4}}\le\frac{{{a * (1 + b)}}}{{x^2}}."
        r"\quad\int_1^\infty x^{-2}\,dx=1<\infty.",
    )


def exponential_ratio_comparison(a: int, b: int, c: int) -> Built:
    numerator_base = c + 1
    denominator_base = numerator_base + b
    rate = sp.Rational(numerator_base, denominator_base)
    return comparison(
        a * (numerator_base**X + 1) / (denominator_base**X + 1),
        0,
        True,
        r"\text{Compare above with a decaying exponential.}",
        rf"0<f(x)\le {2 * a}\left({tex(rate)}\right)^x\quad(x\ge0),\quad0<{tex(rate)}<1."
        rf"\quad\int_0^\infty\left({tex(rate)}\right)^x dx=-\frac1{{\ln({tex(rate)})}}<\infty.",
    )


def oscillatory_numerator_comparison(a: int, b: int, c: int) -> Built:
    return comparison(
        (a * X + sp.sin(b * X)) / X**3,
        c + 2,
        True,
        r"|\sin u|\le1\text{ gives an integrable positive upper bound.}",
        rf"x\ge{c + 2}\Longrightarrow0<f(x)\le\frac{{{a}}}{{x^2}}+\frac1{{x^3}}."
        r"\quad\text{Both comparison powers have exponent greater than one.}",
    )


def bounded_numerator_root_comparison(a: int, b: int, c: int) -> Built:
    baseline = a + c + 1
    return comparison(
        (baseline + a * sp.cos(b * X)) / (sp.sqrt(X) + c + 1),
        (c + 1) ** 2,
        False,
        r"\text{Use the positive lower bound on the "
        r"numerator and an upper bound on the denominator.}",
        rf"{baseline}+{a}\cos({b}x)\ge{c + 1},\quad\sqrt x+{c + 1}\le2\sqrt x."
        rf"\quad f(x)\ge\frac{{{c + 1}}}{{2\sqrt x}},\quad\int^\infty x^{{-1/2}}dx=\infty.",
    )


def root_linear_limit_comparison(a: int, b: int, c: int) -> Built:
    return comparison(
        (a * sp.sqrt(X) + b) / (X * (X + c)),
        1,
        True,
        r"\text{Use limit comparison with }g(x)=x^{-3/2}.",
        rf"\lim_{{x\to\infty}}\frac{{f(x)}}{{x^{{-3/2}}}}"
        rf"=\lim_{{x\to\infty}}\frac{{{a}+{b}/\sqrt x}}{{1+{c}/x}}={a}\in(0,\infty)."
        r"\quad\int_1^\infty x^{-3/2}dx<\infty.",
    )


def quintic_square_root_limit_comparison(a: int, b: int, c: int) -> Built:
    return comparison(
        a * X**2 / sp.sqrt(X**5 - b),
        b + 1,
        False,
        r"\text{Use limit comparison with }g(x)=x^{-1/2}\text{ on the stated nonsingular tail.}",
        rf"\lim_{{x\to\infty}}\frac{{f(x)}}{{x^{{-1/2}}}}"
        rf"=\lim_{{x\to\infty}}\frac{{{a}}}{{\sqrt{{1-{b}/x^5}}}}={a}>0."
        r"\quad\int^\infty x^{-1/2}dx=\infty.",
    )


def exponential_reciprocal_limit_comparison(a: int, b: int, c: int) -> Built:
    return comparison(
        sp.exp(a / X) - 1,
        b + 1,
        False,
        r"\text{Use }(e^t-1)/t\to1\text{ and compare with }1/x.",
        rf"t={a}/x\to0:\quad\lim_{{x\to\infty}}x(e^{{{a}/x}}-1)={a}>0."
        r"\quad\int^\infty dx/x=\infty.",
    )


def squared_sine_limit_comparison(a: int, b: int, c: int) -> Built:
    return comparison(
        sp.sin(a / X) ** 2,
        b + 1,
        True,
        r"\text{Use }\sin t/t\to1\text{ and compare with }x^{-2}.",
        rf"\lim_{{x\to\infty}}x^2\sin^2({a}/x)={a * a}\in(0,\infty)."
        r"\quad\int^\infty x^{-2}dx<\infty.",
    )


def cubic_oscillatory_limit_comparison(a: int, b: int, c: int) -> Built:
    return comparison(
        a * X**2 / (X**3 - b * sp.sin(c * X)),
        b + c + 1,
        False,
        r"\text{The denominator is positive on the stated tail. Compare with }1/x.",
        rf"\frac{{f(x)}}{{1/x}}=\frac{{{a}}}{{1-{b}\sin({c}x)/x^3}}\to{a}>0."
        r"\quad\int^\infty dx/x=\infty.",
    )


def unbounded_quadratic_area(a: int, b: int, c: int) -> Built:
    f = a / (X * X + b * b)
    value = sp.pi * a / b
    visual = plot(
        "Area beneath an unbounded-domain profile",
        "The displayed interval truncates both tails. The "
        "original region extends over the whole real line.",
        [
            path("Upper boundary", -6 * b, 6 * b, lambda x: a / (x * x + b * b)),
            {"label": "Horizontal axis", "points": [[-6 * b, 0], [6 * b, 0]]},
        ],
    )
    built = finish(
        rf"\text{{Find the area between }}y={tex(f)}"
        rf"\text{{ and the }}x\text{{-axis for all real }}x.",
        FormulaAnswer(value),
        r"\text{The integrand is positive and even. Evaluate the two improper tails.}",
        rf"A=2\int_0^\infty {tex(f)}\,dx=\frac{{{2 * a}}}{{{b}}}"
        rf"\left[\arctan(x/{b})\right]_0^\infty={tex(value)}.",
    )
    return replace(built, visual=visual)


def unbounded_exponential_volume(a: int, b: int, c: int) -> Built:
    f = a * sp.exp(-b * X)
    value = sp.pi * a * a / (2 * b)
    visual = plot(
        "Unbounded solid generating profile",
        "The displayed profile truncates the positive tail. "
        "Rotate the full region about the horizontal axis.",
        [
            path("Upper boundary", 0, 6 / b, lambda x: a * math.exp(-b * x)),
            {"label": "Rotation axis", "points": [[0, 0], [6 / b, 0]]},
        ],
    )
    built = finish(
        rf"\text{{Rotate }}x\ge0,\quad0\le y\le{tex(f)}\text{{ "
        rf"about the }}x\text{{-axis. Find the volume.}}",
        FormulaAnswer(value),
        r"\text{Use the improper integral of disc areas.}",
        rf"V=\pi\int_0^\infty {a * a}e^{{-{2 * b}x}}\,dx"
        rf"=\pi\left[-\frac{{{a * a}}}{{{2 * b}}}e^{{-{2 * b}x}}\right]_0^\infty={tex(value)}.",
    )
    return replace(built, visual=visual)


def surface_finitude_comparison(a: int, b: int, c: int) -> Built:
    power = sp.Rational(b + 1, 2)
    finite = power > 1
    classification = "finite" if finite else "infinite"
    f = a / X**power
    factor = sp.sqrt(1 + (a * power) ** 2)
    visual = plot(
        "Surface generating profile on an infinite tail",
        "The plotted segment truncates the unbounded "
        "tail. The horizontal line is the rotation axis.",
        [
            path("Generating curve", 1, 8, lambda x: a / x ** float(power)),
            {"label": "Rotation axis", "points": [[1, 0], [8, 0]]},
        ],
    )
    density = 2 * sp.pi * a * X ** (-power) * sp.sqrt(1 + (a * power) ** 2 * X ** (-2 * power - 2))
    proof = (
        rf"1\le\sqrt{{1+({tex(a * power)})^2x^{{-{tex(2 * power + 2)}}}}}\le{tex(factor)}.\quad"
        rf"2\pi\int_1^\infty r\,ds\text{{ has the same "
        rf"convergence as }}\int_1^\infty x^{{-{tex(power)}}}dx."
    )
    built = finish(
        rf"\text{{Rotate }}y={tex(f)},\quad x\ge1\text{{ about the }}x\text{{-axis.}}"
        r"\text{ Classify its lateral surface area as finite or infinite.}",
        CategoryAnswer(classification, FINITUDE),
        rf"S=\int_1^\infty {tex(density)}\,dx.\quad\text{{Use a two-sided comparison.}}",
        proof + rf"\quad p={tex(power)}\text{{, so the area is }}\text{{{classification}}}.",
    )
    return replace(built, visual=visual)
