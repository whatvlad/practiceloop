"""Bounded sequence computations and their parameter-specific derivations."""

import sympy as sp

from app.engine.answers.computational import (
    CategoryAnswer,
    FormulaAnswer,
    LimitAnswer,
    OrderedAnswer,
)
from app.engine.blocks.analysis_one import N
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._elementary_common import finish as finish_inline
from app.engine.models import Answer

BOUNDS = ("both", "lower_only", "upper_only", "neither")
BOUND_LABELS = ("Boundedness", "Lower bound", "Upper bound")
UPPER_LABELS = ("Boundedness", "Upper bound")
MONOTONICITY = ("increasing", "decreasing")
MONOTONICITY_LABELS = ("Direction", "First index of the strict tail")


def bound_trigonometric(a: int, b: int, c: int) -> Built:
    numerator = a + 1 + sp.sin(N)
    denominator = b + c + 1 - c * sp.cos(N)
    lower = sp.Rational(a, b + 2 * c + 1)
    upper = sp.Rational(a + 2, b + 1)
    return finish(
        r"\text{Classify boundedness and give the two bounds from separate numerator and}"
        r"\text{ denominator bounds using } -1\le\sin n,\cos n\le1:\quad a_n="
        + tex(numerator / denominator)
        + r",\quad n\ge1.",
        OrderedAnswer(
            (CategoryAnswer("both", BOUNDS), FormulaAnswer(lower), FormulaAnswer(upper)),
            BOUND_LABELS,
        ),
        r"\text{Bound numerator and denominator separately using }-1\le\sin n,\cos n\le1.",
        tex(lower) + r"\le a_n\le" + tex(upper),
    )


def bound_radical(a: int, b: int, c: int) -> Built:
    expr = a - b * sp.sqrt(N + c)
    upper = expr.subs(N, 1)
    return finish(
        r"\text{Classify boundedness and give the least upper bound:}\quad a_n="
        + tex(expr)
        + r",\quad n\ge1.",
        OrderedAnswer((CategoryAnswer("upper_only", BOUNDS), FormulaAnswer(upper)), UPPER_LABELS),
        r"\text{The square root increases without bound as }n\to\infty.",
        r"a_n\le a_1=" + tex(upper) + r",\qquad a_n\to-\infty.",
    )


def monotone_factorial(a: int, b: int, c: int) -> Built:
    base = a + 2
    expr = b * base**N / sp.factorial(N + c)
    first = max(1, base - c)
    return finish(
        r"\text{Give the eventual strict direction and the least }N\ge1"
        r"\text{ for which it holds at every step }n\ge N:\quad a_n=" + tex(expr),
        OrderedAnswer(
            (CategoryAnswer("decreasing", MONOTONICITY), FormulaAnswer(first)),
            MONOTONICITY_LABELS,
        ),
        r"\text{The terms are positive, so compare their consecutive ratio with }1.",
        rf"\frac{{a_{{n+1}}}}{{a_n}}=\frac{{{base}}}{{n+{c + 1}}}<1"
        rf"\iff n>{base - c - 1},\qquad N={first}.",
    )


def monotone_radical(a: int, b: int, c: int) -> Built:
    expr = sp.sqrt((N - a - 1) ** 2 + b) + c
    return finish(
        r"\text{Give the eventual strict direction and the least }N\ge1"
        r"\text{ for which it holds at every step }n\ge N:\quad a_n=" + tex(expr),
        OrderedAnswer(
            (CategoryAnswer("increasing", MONOTONICITY), FormulaAnswer(a + 1)),
            MONOTONICITY_LABELS,
        ),
        r"\text{Compare radicands because the square root is strictly increasing.}",
        rf"((n-{a})^2+{b})-((n-{a + 1})^2+{b})=2n-{2 * a + 1}>0"
        rf"\iff n\ge {a + 1}\quad(n\in\mathbb{{Z}}).",
    )


def definition_reciprocal(a: int, b: int, c: int) -> Built:
    expr = a + b / (N + c)
    return sequence_limit(
        expr,
        a,
        r"\text{Use the definition with an arbitrary }\varepsilon>0.",
        rf"|a_n-{a}|=\frac{{{b}}}{{n+{c}}}<\varepsilon"
        rf"\quad\text{{if }}n>\frac{{{b}}}{{\varepsilon}}.",
    )


def definition_growth(a: int, b: int, c: int) -> Built:
    return sequence_limit(
        a * N**2 + b * N - c,
        sp.oo,
        r"\text{For every real threshold }M\text{ choose an index after which }a_n>M.",
        rf"a_n\ge {a}n^2-{c}>M\quad "
        rf"\text{{if }}n>\sqrt{{\max(0,(M+{c})/{a})}}.",
    )


def rational_leading(a: int, b: int, c: int) -> Built:
    expr = (a * N**3 + b * N + c) / (N - (c + 1) * N**3)
    return sequence_limit(
        expr,
        -sp.Rational(a, c + 1),
        r"\text{Divide the numerator and denominator by }n^3.",
        rf"a_n=\frac{{{a}+{b}/n^2+{c}/n^3}}{{1/n^2-{c + 1}}}"
        rf"\to\frac{{{a}}}{{-{c + 1}}}.",
    )


def factorial_limit(a: int, b: int, c: int) -> Built:
    expr = (a * N**2 + b) * sp.factorial(N) / ((c * N + 1) * sp.factorial(N + 1))
    return sequence_limit(
        expr,
        sp.Rational(a, c),
        r"\text{Cancel }n!\text{ using }(n+1)!=(n+1)n!.",
        rf"a_n=\frac{{{a}n^2+{b}}}{{({c}n+1)(n+1)}}"
        rf"=\frac{{{a}+{b}/n^2}}{{({c}+1/n)(1+1/n)}}\to\frac{{{a}}}{{{c}}}.",
    )


def conjugate_sequence(a: int, b: int, c: int) -> Built:
    left = sp.sqrt(N**2 + 2 * (a + b) * N + c)
    right = sp.sqrt(N**2 + 2 * b * N)
    return sequence_limit(
        left - right,
        a,
        r"\text{Multiply and divide by the sum of the radicals.}",
        rf"a_n=\frac{{{2 * a}n+{c}}}{{{tex(left + right)}}}"
        rf"\to\frac{{{2 * a}}}{{2}}\quad\text{{after division by }}n.",
    )


def squeeze_oscillation(a: int, b: int, c: int) -> Built:
    expr = (a * N + (-1) ** N) / (b * N + c)
    return sequence_limit(
        expr,
        sp.Rational(a, b),
        r"\text{Use }-1\le(-1)^n\le1\text{ and the positive denominator.}",
        rf"\frac{{{a}n-1}}{{{b}n+{c}}}\le a_n\le"
        rf"\frac{{{a}n+1}}{{{b}n+{c}}},\qquad "
        rf"\text{{both bounds tend to }}\frac{{{a}}}{{{b}}}.",
    )


def squeeze_floor(a: int, b: int, c: int) -> Built:
    top_slope = sp.sqrt(a + 1)
    bottom_slope = b * sp.sqrt(c + 1)
    expr = (sp.floor(N * top_slope) + c) / (sp.floor(N * bottom_slope) + c)
    top = tex(top_slope)
    bottom = tex(bottom_slope)
    return sequence_limit(
        expr,
        top_slope / bottom_slope,
        r"\text{For real }t,\ t-1<\lfloor t\rfloor\le t."
        r"\quad\text{The lower bounds on numerator and denominator are positive.}",
        rf"\frac{{({top})n+{c}-1}}{{({bottom})n+{c}}}<a_n<"
        rf"\frac{{({top})n+{c}}}{{({bottom})n+{c}-1}}."
        r"\quad\text{Divide through by }n\text{ on both sides.}",
    )


def squeeze_root(a: int, b: int, c: int) -> Built:
    offset = a + c + 1
    expr = (offset + sp.cos(b * N)) ** (1 / N)
    return sequence_limit(
        expr,
        1,
        r"\text{Bound the cosine before taking the positive }n\text{th root.}",
        rf"{offset - 1}^{{1/n}}\le a_n\le {offset + 1}^{{1/n}},\qquad "
        r"d^{1/n}=\exp((\log d)/n)\to1\quad(d>0).",
    )


def squeeze_sum(a: int, b: int, c: int) -> Built:
    k = sp.Symbol("k", integer=True, positive=True)
    expr = sp.Sum(1 / (a * N**2 + b * k + c), (k, 1, N))
    return sequence_limit(
        expr,
        0,
        r"\text{Each of the }n\text{ positive summands is at most }1/(an^2)"
        rf"\text{{ with }}a={a}.",
        rf"0<a_n\le\frac{{n}}{{{a}n^2}}=\frac{{1}}{{{a}n}}\to0.",
    )


def exponential_power(a: int, b: int, c: int) -> Built:
    base = 1 + sp.Rational(a, 1) / (N + b)
    return sequence_limit(
        base ** (c * N - a),
        sp.exp(a * c),
        r"\text{Take logarithms. The base is positive and tends to }1.",
        rf"\log a_n=\frac{{\log(1+u_n)}}{{u_n}}\,( {c}n-{a})u_n,"
        rf"\qquad u_n=\frac{{{a}}}{{n+{b}}},\quad ({c}n-{a})u_n\to {a * c}.",
    )


def exponential_difference(a: int, b: int, c: int) -> Built:
    expr = ((N + a) ** N - (N + a + b) ** N) / ((N + a + b) ** N - (N + a + b + c) ** N)
    return sequence_limit(
        expr,
        (1 - sp.exp(b)) / (sp.exp(b) - sp.exp(b + c)),
        r"\text{Divide each power by }(n+a)^n\text{ and use }(1+d/(n+a))^n\to e^d.",
        rf"\frac{{1-(1+{b}/(n+{a}))^n}}{{(1+{b}/(n+{a}))^n-(1+{b + c}/(n+{a}))^n}}"
        rf"\to\frac{{1-e^{{{b}}}}}{{e^{{{b}}}-e^{{{b + c}}}}}.",
    )


def infinite_exponential(a: int, b: int, c: int) -> Built:
    large = a + b + 2
    small = a + 1
    return sequence_limit(
        c + small**N - large**N,
        -sp.oo,
        r"\text{Factor the dominant exponential, which grows without bound.}",
        rf"a_n={large}^n\left({c}/{large}^n+({small}/{large})^n-1\right),"
        r"\quad\text{the factor in parentheses tends to }-1.",
    )


def sequence_limit(expr: sp.Expr, expected: object, method: str, derivation: str) -> Built:
    return finish(
        r"\text{Evaluate for positive integer }n:\quad \lim_{n\to\infty}" + tex(expr),
        LimitAnswer(expected),
        method,
        derivation,
    )


def finish(statement: str, answer: Answer, method: str, derivation: str) -> Built:
    return finish_inline(r"\(" + statement + r"\)", answer, method, derivation)


def bound_conjugate(a: int, b: int, c: int) -> Built:
    left, right = sp.sqrt(N + a + b), sp.sqrt(N + b)
    upper = c * (left - right).subs(N, 1)
    return finish(
        r"\text{Classify boundedness and give the greatest lower bound and least upper bound:}"
        r"\quad a_n=" + tex(c * (left - right)) + r",\quad n\ge1.",
        OrderedAnswer(
            (CategoryAnswer("both", BOUNDS), FormulaAnswer(0), FormulaAnswer(upper)), BOUND_LABELS
        ),
        r"\text{Rationalize. Both radicals in the denominator increase without bound.}",
        rf"0<a_n=\frac{{{a * c}}}{{{tex(left + right)}}}"
        rf"\le a_1={tex(upper)}.",
    )


def monotone_ratio(a: int, b: int, c: int) -> Built:
    lower, upper = a + 1, a + b + 2
    expr = upper**N / (lower**N + c * (upper - 1) ** N)
    return finish(
        r"\text{Give the eventual strict direction and the least }N\ge1"
        r"\text{ for which it holds at every step }n\ge N:\quad a_n=" + tex(expr),
        OrderedAnswer(
            (CategoryAnswer("increasing", MONOTONICITY), FormulaAnswer(1)), MONOTONICITY_LABELS
        ),
        r"\text{Divide numerator and denominator by the numerator.}",
        rf"a_n=\frac1{{({lower}/{upper})^n+{c}({upper - 1}/{upper})^n}}."
        r"\quad\text{Both ratios lie in }(0,1)\text{, so the positive denominator decreases.}",
    )


def rational_zero(a: int, b: int, c: int) -> Built:
    return sequence_limit(
        (a * N + b) / (c * N**2 + 1),
        0,
        r"\text{The denominator has the higher degree. Divide by }n^2.",
        rf"a_n=\frac{{{a}/n+{b}/n^2}}{{{c}+1/n^2}}\to 0.",
    )


def arithmetic_sum_ratio(a: int, b: int, c: int) -> Built:
    k = sp.Symbol("k", integer=True, positive=True)
    top = sp.Sum(a * k + b, (k, 1, N))
    bottom = sp.Sum(c * k + 1, (k, 1, N))
    return sequence_limit(
        top / bottom,
        sp.Rational(a, c),
        r"\text{Use the finite arithmetic sum formula in both sums.}",
        rf"a_n=\frac{{{a}n(n+1)/2+{b}n}}{{{c}n(n+1)/2+n}}\to\frac{{{a}}}{{{c}}}.",
    )


def root_exponential_ratio(a: int, b: int, c: int) -> Built:
    small, medium, large = a + 1, a + b + 2, a + b + c + 3
    expr = ((medium**N + small**N) / (large**N + medium**N)) ** (1 / N)
    return sequence_limit(
        expr,
        sp.Rational(medium, large),
        r"\text{Factor the largest base power from each sum.}",
        rf"a_n=\frac{{{medium}}}{{{large}}}"
        rf"\left(\frac{{1+({small}/{medium})^n}}{{1+({medium}/{large})^n}}\right)^{{1/n}}."
        r"\quad\text{The factor in parentheses is between }1/2\text{ and }2.",
    )


def logarithmic_power(a: int, b: int, c: int) -> Built:
    log = sp.log(N + c)
    return sequence_limit(
        (1 + a / log) ** (b * log),
        sp.exp(a * b),
        r"\text{Take logarithms and use }\log(1+u)/u\to1.",
        rf"\log a_n={a * b}\frac{{\log(1+u_n)}}{{u_n}}\to {a * b},"
        rf"\qquad u_n={a}/\log(n+{c})\to0.",
    )


def infinite_factorial(a: int, b: int, c: int) -> Built:
    numerator = b - a * sp.factorial(N + 1)
    denominator = sp.factorial(N) + c
    return sequence_limit(
        numerator / denominator,
        -sp.oo,
        r"\text{Use }(n+1)!=(n+1)n!\text{ and divide by }n!.",
        rf"a_n=\frac{{{b}/n!-{a}(n+1)}}{{1+{c}/n!}}."
        r"\quad\text{The numerator tends to }-\infty\text{ and the denominator tends to }1.",
    )


def divergent_oscillation(a: int, b: int, c: int) -> Built:
    return sequence_limit(
        b + a * (-1) ** N + c / N,
        "does_not_exist",
        r"\text{A convergent sequence must have the same limit along every subsequence.}",
        rf"a_{{2k}}\to {a + b},\qquad a_{{2k+1}}\to {b - a},\qquad {a + b}\ne {b - a}.",
    )


def scaled_conjugate(a: int, b: int, c: int) -> Built:
    base = a * N
    expr = b * N * (sp.sqrt(base**2 - c) - base)
    # Start at n=3 so all sampled radicands are strictly positive.
    return finish(
        r"\text{Evaluate for integers }n\ge3:\quad\lim_{n\to\infty}" + tex(expr),
        LimitAnswer(-sp.Rational(b * c, 2 * a)),
        r"\text{Rationalize the difference and divide the denominator by }n.",
        rf"\frac{{-{b * c}n}}{{\sqrt{{{a * a}n^2-{c}}}+{a}n}}"
        rf"=\frac{{-{b * c}}}{{\sqrt{{{a * a}-{c}/n^2}}+{a}}}\to-\frac{{{b * c}}}{{{2 * a}}}.",
    )
