"""Leibniz, absolute/conditional convergence and full power-series domains (#274)."""

from dataclasses import replace
from typing import Any

import sympy as sp

from app.engine.answers.computational import CategoryAnswer, RealSetAnswer
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import plot, point
from app.engine.generators._sequence_limits import finish
from app.engine.generators._series_comparisons import classify

N = sp.Symbol("n", integer=True, positive=True)
X = sp.Symbol("x", real=True)
ABSOLUTE_CHOICES = ("absolute", "conditional", "diverges")


def root_difference_leibniz(a: int, b: int, c: int) -> Built:
    term = (-1) ** (N + c) * b * (sp.sqrt(N * N + a * a) - N)
    return classify(
        term,
        0,
        True,
        r"\text{Apply the alternating-series criterion to the positive magnitudes.}",
        rf"b_n=\frac{{{b * a * a}}}{{\sqrt{{n^2+{a * a}}}+n}}>0.\quad"
        r"\text{The denominator increases, hence }b_n\downarrow0"
        r"\text{ and the alternating series converges.}",
    )


def exponential_quotient_leibniz(a: int, b: int, c: int) -> Built:
    small = a + 1
    middle = small + b
    large = middle + c
    return classify(
        (-1) ** N * small**N / (middle**N + large**N),
        0,
        True,
        r"\text{Apply the alternating-series criterion.}",
        rf"b_n="
        rf"\frac1{{({tex(sp.Rational(middle, small))})^n+({tex(sp.Rational(large, small))})^n}}."
        r"\quad\text{Both denominator bases exceed one, so }b_n\downarrow0.",
    )


def sine_reciprocal_leibniz(a: int, b: int, c: int) -> Built:
    angle = sp.pi / (a + 2)
    return classify(
        sp.sin((-1) ** (N + c) * angle / N),
        b + 1,
        True,
        r"\text{Use oddness of sine, then the alternating-series criterion.}",
        rf"a_n=(-1)^{{n+{c}}}\sin\frac{{\pi}}{{{a + 2}n}}."
        rf"\quad0<\frac{{\pi}}{{{a + 2}n}}\le\pi/2\text{{ and the arguments decrease to zero.}}"
        r"\quad\text{Sine is increasing on this range, so the magnitudes decrease to zero.}",
    )


def factorial_leibniz(a: int, b: int, c: int) -> Built:
    base = a + 1
    return classify(
        (-1) ** (N + c) * b * base**N / sp.factorial(N),
        1,
        True,
        r"\text{Ignore the finite initial segment and apply the alternating-series criterion.}",
        rf"\frac{{b_{{n+1}}}}{{b_n}}=\frac{{{base}}}{{n+1}}<1\quad(n\ge{base})."
        r"\quad\text{This ratio tends to zero, so the positive "
        r"magnitudes tend to zero and are eventually decreasing.}",
    )


def absolute_classification(
    term: sp.Expr, start: int, classification: str, method: str, proof: str
) -> Built:
    return finish(
        rf"\text{{Classify }}\sum_{{n={start}}}^\infty {tex(term)}"
        r"\text{ as absolute, conditional, or diverges.}",
        CategoryAnswer(classification, ABSOLUTE_CHOICES),
        method,
        proof,
    )


def alternating_geometric_absolute(a: int, b: int, c: int) -> Built:
    base = a + 1
    return absolute_classification(
        (-1) ** N * c / (base**N + b),
        0,
        "absolute",
        r"\text{Compare the absolute values with a geometric series.}",
        rf"|a_n|\le\frac{{{c}}}{{{base}^n}},\quad1/{base}<1.\quad\sum|a_n|<\infty.",
    )


def alternating_harmonic_conditional(a: int, b: int, c: int) -> Built:
    return absolute_classification(
        (-1) ** (N + c) * a * N / (N * N + b * b),
        b + c,
        "conditional",
        r"\text{Use Leibniz for convergence and harmonic "
        r"limit comparison for absolute convergence.}",
        rf"b_n=\frac{{{a}n}}{{n^2+{b * b}}}\downarrow0\quad(n>{b}),"
        rf"\quad\lim_{{n\to\infty}}n b_n={a}>0."
        r"\quad\text{The alternating sum converges but the absolute series diverges.}",
    )


def negative_rational_power_classification(a: int, b: int, c: int) -> Built:
    classification = "absolute" if a < b else "diverges"
    proof = rf"\sqrt[n]{{|a_n|}}=\frac{{{a}n}}{{{b}n+{c}}}\to\frac{{{a}}}{{{b}}}."
    if a == b:
        proof += (
            rf"\quad |a_n|=(1+{tex(sp.Rational(c, a))}/n)^{{-n}}"
            rf"\to e^{{-{tex(sp.Rational(c, a))}}}>0."
        )
        proof += r"\quad\text{The terms fail to tend to zero.}"
    elif a > b:
        proof += (
            r"\quad\text{The root limit exceeds one, so the terms fail the necessary condition.}"
        )
    else:
        proof += r"\quad\text{The root limit is below one, so the absolute series converges.}"
    return absolute_classification(
        (-a * N / (b * N + c)) ** N,
        1,
        classification,
        r"\text{Apply the root test to the absolute values.}",
        proof,
    )


def alternating_exponential_conditional(a: int, b: int, c: int) -> Built:
    return absolute_classification(
        (-1) ** (N + c) * b * (sp.exp(a / N) - 1),
        1,
        "conditional",
        r"\text{Use Leibniz and a harmonic limit comparison.}",
        rf"b_n={b}(e^{{{a}/n}}-1)\downarrow0,\quad\lim_{{n\to\infty}}n b_n={a * b}>0."
        r"\quad\text{The alternating sum converges and the series of absolute values diverges.}",
    )


def damped_sine_absolute(a: int, b: int, c: int) -> Built:
    base = b + 1
    return absolute_classification(
        sp.sin(a * N + c) / base**N,
        1,
        "absolute",
        r"|\sin u|\le1\text{ gives geometric domination.}",
        rf"|a_n|\le1/{base}^n,\quad\sum_{{n=1}}^\infty1/{base}^n<\infty.",
    )


def convergence_visual(domain: sp.Set) -> dict[str, Any]:
    paths: list[dict[str, Any]]
    if domain != sp.S.Reals and isinstance(domain, sp.Interval):
        lo, hi = float(domain.start), float(domain.end)
        paths = [{"label": "Convergent interior", "points": [[lo, 0], [hi, 0]]}]
        markers = [
            point("Left endpoint", lo, 0, included=not domain.left_open),
            point("Right endpoint", hi, 0, included=not domain.right_open),
        ]
        description = "Endpoint markers show inclusion in the complete convergence set."
    else:
        paths = [
            {"label": "All negative x", "points": [[0, 0], [-5, 0]], "arrow": True},
            {"label": "All positive x", "points": [[0, 0], [5, 0]], "arrow": True},
        ]
        markers = []
        description = "Every real x is included. The arrows continue in both directions."
    return plot("Power series convergence set", description, paths, markers)


def power_set(term: sp.Expr, start: int, domain: sp.Set, method: str, proof: str) -> Built:
    built = finish(
        rf"\text{{Find the full real convergence set, including "
        rf"endpoints, of }}\sum_{{n={start}}}^\infty {tex(term)}.",
        RealSetAnswer(domain),
        method,
        proof + rf"\quad D={tex(domain)}.",
    )
    return replace(built, visual=convergence_visual(domain))


def logarithmic_power_domain(a: int, b: int, c: int) -> Built:
    radius = b * sp.E
    power = 1 + c % 2
    domain = sp.Interval(a - radius, a + radius, left_open=False, right_open=power == 1)
    return power_set(
        (X - a) ** N / (N**power * radius**N),
        1,
        domain,
        rf"\text{{The root limit gives }}|x-{a}|<{tex(radius)}"
        rf"\text{{. Check both boundary series.}}",
        rf"x={tex(a - radius)}:\quad\sum(-1)^n/n^{{{power}}}\text{{ converges by Leibniz.}}"
        rf"\quad x={tex(a + radius)}:\quad\sum1/n^{{{power}}}"
        rf"\text{{ {'diverges' if power == 1 else 'converges'} by the p-series test.}}",
    )


def geometric_power_domain(a: int, b: int, c: int) -> Built:
    domain = sp.Interval.open(sp.Rational(b - 1, a), sp.Rational(b + 1, a))
    return power_set(
        (a * X - b) ** N,
        0,
        domain,
        rf"|{a}x-{b}|<1\text{{ is the geometric convergence condition.}}",
        r"\text{At either boundary the terms have magnitude one and fail to tend to zero.}",
    )


def factorial_power_domain(a: int, b: int, c: int) -> Built:
    return power_set(
        c**N * (X - a) ** N / sp.factorial(N),
        1,
        sp.S.Reals,
        r"\text{Use the ratio test at any fixed real }x.",
        rf"\left|\frac{{a_{{n+1}}}}{{a_n}}\right|=\frac{{{c}|x-{a}|}}{{n+1}}\to0<1."
        r"\quad\text{The series converges absolutely for every real }x.",
    )


def exponential_difference_power_domain(a: int, b: int, c: int) -> Built:
    large = c + 2
    small = large - 1
    domain = sp.Interval.open(-b - sp.Rational(large, a), -b + sp.Rational(large, a))
    return power_set(
        (a * (X + b)) ** N / (large**N - small**N),
        1,
        domain,
        rf"\sqrt[n]{{{large}^n-{small}^n}}\to{large}.\quad |{a}(x+{b})|<{large}.",
        rf"\text{{At each boundary the terms are }}(\pm1)^n"
        rf"\frac1{{1-({tex(sp.Rational(small, large))})^n}}"
        r"\text{ and do not tend to zero.}",
    )


def even_power_domain(a: int, b: int, c: int) -> Built:
    radius = sp.sqrt(b + 1)
    domain = sp.Interval.open(-a - radius, -a + radius)
    return power_set(
        N * (X + a) ** (2 * N) / ((b + 1) ** N + c),
        1,
        domain,
        rf"\sqrt[n]{{|a_n|}}\to\frac{{(x+{a})^2}}{{{b + 1}}}.\quad |x+{a}|<{tex(radius)}.",
        rf"\text{{At both endpoints, }}a_n=\frac{{n}}{{1+{c}/{b + 1}^n}}"
        rf"\sim n\text{{ and the term condition fails.}}",
    )
