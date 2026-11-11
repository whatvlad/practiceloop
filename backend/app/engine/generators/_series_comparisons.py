"""Partial sums and integral/direct/limit comparison tests for series (#272)."""

from dataclasses import replace

import sympy as sp

from app.engine.answers.computational import (
    CategoryAnswer,
    FormulaAnswer,
    LimitAnswer,
    OrderedAnswer,
)
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._improper_integrals import CONVERGENCE
from app.engine.generators._limit_visuals import plot, point
from app.engine.generators._sequence_limits import finish

N = sp.Symbol("n", integer=True, positive=True)
K = sp.Symbol("N", integer=True, positive=True)
PARTIAL_ONE_LABELS = ("A", "Convergence", "Series sum")
PARTIAL_TWO_LABELS = ("A", "B", "Convergence", "Series sum")


def classify(term: sp.Expr, start: int, converges: bool, method: str, proof: str) -> Built:
    return finish(
        rf"\text{{Classify }}\sum_{{n={start}}}^\infty {tex(term)}"
        rf"\text{{ as converges or diverges, using the stated method.}}",
        CategoryAnswer("converges" if converges else "diverges", CONVERGENCE),
        method,
        proof,
    )


def partial_sum(
    term: sp.Expr,
    start: int,
    template: str,
    coefficients: tuple[sp.Expr, ...],
    expression: sp.Expr,
    total: sp.Expr,
    proof: str,
) -> Built:
    converges = total != sp.oo
    category = CategoryAnswer("converges" if converges else "diverges", CONVERGENCE)
    answer = OrderedAnswer(
        (*[FormulaAnswer(value) for value in coefficients], category, LimitAnswer(total)),
        PARTIAL_ONE_LABELS if len(coefficients) == 1 else PARTIAL_TWO_LABELS,
    )
    values = [float(expression.subs(K, index)) for index in range(start, start + 10)]
    markers = [
        point(f"Partial sum {index}", index, value, included=True)
        for index, value in zip(range(start, start + 10), values, strict=True)
    ]
    paths = [
        {
            "label": "Partial sums",
            "points": [
                [index, value]
                for index, value in zip(range(start, start + 10), values, strict=True)
            ],
        }
    ]
    if converges:
        paths.append(
            {"label": "Series sum", "points": [[start, float(total)], [start + 9, float(total)]]}
        )
    visual = plot(
        "Partial sums at integer endpoints",
        "Markers are the finite partial sums at the displayed integer indices.",
        paths,
        markers,
    )
    coefficient_names = "A" if len(coefficients) == 1 else "A; B"
    built = finish(
        rf"\text{{For }}\sum_{{n={start}}}^\infty {tex(term)},"
        rf"\quad S_N=\sum_{{n={start}}}^N {tex(term)},"
        rf"\quad N\ge{start},\text{{ determine the exact coefficients in }}S_N={template}."
        rf"\text{{ Give }}({coefficient_names};\text{{convergence}};\text{{series sum}})."
        r"\text{ Use inf for a divergent positive sum.}",
        answer,
        proof,
        rf"S_N={tex(expression)}.\quad\lim_{{N\to\infty}}S_N={tex(total)}.",
    )
    return replace(built, visual=visual)


def geometric_partial_sums(a: int, b: int, c: int) -> Built:
    ratio = sp.Rational(a + b, a + b + c)
    coefficient = 1 / (1 - ratio)
    expression = coefficient * (1 - ratio ** (K + 1))
    return partial_sum(
        ratio**N,
        0,
        rf"A\left(1-({tex(ratio)})^{{N+1}}\right)",
        (coefficient,),
        expression,
        coefficient,
        r"qS_N=q+q^2+\cdots+q^{N+1}.\quad (1-q)S_N=1-q^{N+1},\quad0<q<1.",
    )


def rational_telescoping_partial_sums(a: int, b: int, c: int) -> Built:
    start = c + 1
    coefficient = sp.Rational(a, start + b)
    expression = coefficient - a / (K + b + 1)
    return partial_sum(
        a / ((N + b) * (N + b + 1)),
        start,
        rf"A-\frac{{B}}{{N+{b + 1}}}",
        (coefficient, sp.Integer(a)),
        expression,
        coefficient,
        rf"\frac{{{a}}}{{(n+{b})(n+{b + 1})}}=\frac{{{a}}}{{n+{b}}}-\frac{{{a}}}{{n+{b + 1}}}."
        r"\quad\text{All interior terms cancel in the finite partial sum.}",
    )


def factorial_telescoping_partial_sums(a: int, b: int, c: int) -> Built:
    expression = a - a / sp.factorial(K)
    return partial_sum(
        a * (N - 1) / sp.factorial(N),
        2,
        r"A-\frac{B}{N!}",
        (sp.Integer(a), sp.Integer(a)),
        expression,
        sp.Integer(a),
        rf"\frac{{{a}(n-1)}}{{n!}}=\frac{{{a}}}{{(n-1)!}}-\frac{{{a}}}{{n!}}."
        r"\quad\text{Telescope from }n=2\text{ and use }1/N!\to0.",
    )


def root_telescoping_partial_sums(a: int, b: int, c: int) -> Built:
    constant = a * sp.sqrt(b + 1)
    expression = a * sp.sqrt(K + b + 1) - constant
    term = a / (sp.sqrt(N + b + 1) + sp.sqrt(N + b))
    return partial_sum(
        term,
        1,
        rf"A\sqrt{{N+{b + 1}}}-B",
        (sp.Integer(a), constant),
        expression,
        sp.oo,
        rf"{tex(term)}"
        rf"={a}(\sqrt{{n+{b + 1}}}-\sqrt{{n+{b}}}).\quad\text{{The finite sum telescopes.}}",
    )


def quadratic_integral_test(a: int, b: int, c: int) -> Built:
    return classify(
        a / (N * N + b * b),
        c,
        True,
        r"\text{The continuous interpolation is positive and decreasing. Apply the integral test.}",
        rf"f'(x)=\frac{{-{2 * a}x}}{{(x^2+{b * b})^2}}<0.\quad"
        rf"\int_{{{c}}}^\infty\frac{{{a}}}{{x^2+{b * b}}}dx"
        rf"=\frac{{{a}}}{{{b}}}\left(\frac\pi2-\arctan({tex(sp.Rational(c, b))})\right)<\infty.",
    )


def harmonic_quotient_integral_test(a: int, b: int, c: int) -> Built:
    start = 3 * b
    return classify(
        a * (N - b) / (N * (N + b)),
        start,
        False,
        rf"x\ge{start}\text{{ gives positivity and eventual decrease, so use the integral test.}}",
        rf"f'(x)=\frac{{{a}}}{{x^2}}-\frac{{{2 * a}}}{{(x+{b})^2}}<0.\quad"
        rf"F(x)=-{a}\ln x+{2 * a}\ln(x+{b})={a}\ln x+{2 * a}\ln(1+{b}/x)\to\infty.",
    )


def logarithmic_integral_test(a: int, b: int, c: int) -> Built:
    power = 2 + c % 2
    start = b + 2
    return classify(
        a * sp.log(N) / N**power,
        start,
        True,
        r"\text{The interpolation is positive and decreasing "
        r"on the stated tail. Apply the integral test.}",
        rf"f'(x)=\frac{{{a}(1-{power}\ln x)}}{{x^{{{power + 1}}}}}<0.\quad"
        rf"F(x)=-\frac{{{a}}}{{x^{{{power - 1}}}}}\left(\frac{{\ln "
        rf"x}}{{{power - 1}}}+\frac1{{{(power - 1) ** 2}}}\right)"
        r"\to0\text{, so the improper integral is finite.}",
    )


def root_integral_test(a: int, b: int, c: int) -> Built:
    return classify(
        a / (N * sp.sqrt(N + b)),
        c,
        True,
        r"\text{The interpolation is positive and decreasing. "
        r"Put }t=\sqrt{x+b}\text{ in its integral.}",
        rf"\int\frac{{{a}}}{{x\sqrt{{x+{b}}}}}dx"
        rf"=\frac{{{a}}}{{\sqrt{{{b}}}}}\ln\frac{{\sqrt{{x+{b}}}-"
        rf"\sqrt{{{b}}}}}{{\sqrt{{x+{b}}}+\sqrt{{{b}}}}}."
        r"\quad\text{The primitive tends to zero and is finite at the lower endpoint.}",
    )


def exponential_integral_test(a: int, b: int, c: int) -> Built:
    return classify(
        a * sp.exp(b * N) / (sp.exp(2 * b * N) + c * c),
        c,
        True,
        rf"x\ge{c}\Longrightarrow e^{{{b}x}}\ge{c}.\quad"
        rf"\text{{The interpolation is positive and decreasing.}}",
        rf"f'(x)="
        rf"\frac{{{a * b}e^{{{b}x}}({c * c}-e^{{{2 * b}x}})}}{{(e^{{{2 * b}x}}+{c * c})^2}}\le0."
        rf"\quad F(x)=\frac{{{a}}}{{{b * c}}}"
        rf"\arctan(e^{{{b}x}}/{c})\to\frac{{{a}\pi}}{{{2 * b * c}}}.",
    )


def polynomial_direct_comparison(a: int, b: int, c: int) -> Built:
    return classify(
        (a * N + b) / (N**3 + c),
        1,
        True,
        r"\text{Use direct upper comparison with a convergent p-series.}",
        rf"0<\frac{{{a}n+{b}}}{{n^3+{c}}}\le\frac{{{a + b}}}{{n^2}},\quad n\ge1."
        r"\quad\sum n^{-2}\text{ converges.}",
    )


def root_direct_comparison(a: int, b: int, c: int) -> Built:
    return classify(
        a * sp.sqrt(N * N + b) / (N * N + c),
        1,
        False,
        r"\text{Use a divergent harmonic lower comparison.}",
        rf"\sqrt{{n^2+{b}}}\ge n,\quad n^2+{c}\le{1 + c}n^2.\quad"
        rf"a_n\ge\frac{{{a}}}{{{1 + c}n}}\text{{ and the harmonic series diverges.}}",
    )


def sine_direct_comparison(a: int, b: int, c: int) -> Built:
    angle = sp.pi / (a + 1)
    base = b + 1
    return classify(
        c * sp.sin(angle / base**N),
        1,
        True,
        r"0<\sin t\le t\text{ gives a geometric upper comparison.}",
        rf"0<a_n\le\frac{{{c}\pi}}{{{a + 1}}}\left(\frac1{{{base}}}\right)^n."
        rf"\quad0<1/{base}<1\text{{, so the comparison series converges.}}",
    )


def exponential_direct_comparison(a: int, b: int, c: int) -> Built:
    base = a + 2
    return classify(
        c * ((a + 1) ** N + sp.exp(N)) / (sp.exp(N) + base**N),
        0,
        True,
        r"\text{Bound the denominator below by its dominant exponential.}",
        rf"0<a_n\le{c}\left[\left(\frac{{{a + 1}}}{{{base}}}\right)^n"
        rf"+\left(\frac e{{{base}}}\right)^n\right].\quad"
        rf"{base}\ge3>e\text{{ and both geometric ratios are below one.}}",
    )


def harmonic_exponential_direct_comparison(a: int, b: int, c: int) -> Built:
    base = a + b + 1
    lower = a + 1
    return classify(
        c * (base**N + N) / (N * base**N + lower**N),
        1,
        False,
        r"\text{Use a harmonic lower bound for the positive terms.}",
        rf"{lower}<{base},\quad n{base}^n+{lower}^n\le(n+1){base}^n\le2n{base}^n."
        rf"\quad a_n\ge\frac{{{c}}}{{2n}}\text{{, so the series diverges.}}",
    )


def root_cubic_limit_comparison(a: int, b: int, c: int) -> Built:
    return classify(
        a * (N * N + b) / sp.sqrt(c * N**6 - 1),
        2,
        False,
        r"\text{Compare in the limit with }1/n.",
        rf"\lim_{{n\to\infty}}\frac{{a_n}}{{1/n}}=\frac{{{a}}}{{\sqrt{{{c}}}}}\in(0,\infty)."
        r"\quad\sum1/n\text{ diverges.}",
    )


def rational_square_limit_comparison(a: int, b: int, c: int) -> Built:
    return classify(
        (a * N * N + b) / (N**4 + c),
        1,
        True,
        r"\text{Compare in the limit with }1/n^2.",
        rf"\lim_{{n\to\infty}}\frac{{a_n}}{{1/n^2}}={a}>0.\quad\sum1/n^2\text{{ converges.}}",
    )


def exponential_limit_comparison(a: int, b: int, c: int) -> Built:
    base = b + 2
    return classify(
        a * (sp.exp(N) - 1) / (base**N - 1),
        1,
        True,
        rf"\text{{Compare with }}(e/{base})^n\text{{, whose ratio is below one.}}",
        rf"\frac{{a_n}}{{(e/{base})^n}}={a}\frac{{1-e^{{-n}}}}{{1-{base}^{{-n}}}}\to{a}>0.",
    )


def growing_geometric_limit_comparison(a: int, b: int, c: int) -> Built:
    base = a + 1
    other = b + 1
    return classify(
        c * base**N * (1 + other ** (-N)),
        0,
        False,
        rf"\text{{Compare with }}{base}^n\text{{, which fails the necessary term test.}}",
        rf"\frac{{a_n}}{{{base}^n}}={c}(1+{other}^{{-n}})\to{c}>0."
        r"\quad\text{The positive terms grow instead of tending to zero.}",
    )


def sine_quotient_limit_comparison(a: int, b: int, c: int) -> Built:
    numerator = sp.pi / (a + 1)
    denominator = sp.pi / (b + 1)
    return classify(
        c * sp.sin(numerator / N**2) / sp.sin(denominator / N),
        1,
        False,
        r"\text{Use }\sin t/t\to1\text{ and compare with }1/n.",
        rf"\lim_{{n\to\infty}}n a_n={tex(sp.Rational(c * (b + 1), a + 1))}\in(0,\infty)."
        r"\quad\sum1/n\text{ diverges.}",
    )


def factorial_limit_comparison(a: int, b: int, c: int) -> Built:
    shift = 2 + c % 2
    return classify(
        a * (sp.factorial(N) + b) / sp.factorial(N + shift),
        0,
        True,
        rf"\text{{Compare with }}1/n^{{{shift}}}\text{{ and cancel the factorial quotient.}}",
        rf"\frac{{a_n}}{{1/n^{{{shift}}}}}={a}\left(1+\frac{{{b}}}{{n!}}\right)"
        rf"\frac{{n^{{{shift}}}}}{{(n+1)\cdots(n+{shift})}}\to{a}>0."
        rf"\quad {shift}>1\text{{, so the comparison p-series converges.}}",
    )
