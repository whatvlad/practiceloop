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


def sequence_limit(expr: sp.Expr | str, expected: object, method: str, derivation: str) -> Built:
    """Ask for a limit; a string is a ready display, already grouped where needed."""
    shown = expr if isinstance(expr, str) else tex(expr)
    return finish(
        r"\text{Evaluate for positive integer }n:\quad \lim_{n\to\infty}" + shown,
        LimitAnswer(expected),
        method,
        derivation,
    )


def grouped(expr: sp.Expr) -> str:
    return r"\left(" + tex(expr) + r"\right)"


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


# #257: the remaining sequence-side source references of #236.


def bound_root_exponential(a: int, b: int, c: int) -> Built:
    base, shift = a + 1, 1 + (b - 1) % a
    expr = (base**N - shift) ** (1 / N)
    return finish(
        r"\text{Classify boundedness and give the greatest lower bound and least upper bound:}"
        r"\quad a_n=" + tex(expr) + r",\quad n\ge1.",
        OrderedAnswer(
            (CategoryAnswer("both", BOUNDS), FormulaAnswer(base - shift), FormulaAnswer(base)),
            BOUND_LABELS,
        ),
        rf"\text{{Compare the radicand with }}{base - shift}^n\text{{ and }}{base}^n.",
        rf"{base}^n-{base - shift}^n={shift}\sum_{{k=0}}^{{n-1}}{base}^{{n-1-k}}"
        rf"\cdot{base - shift}^k\ge{shift},\quad\text{{so}}\quad "
        rf"{base - shift}^n\le {base}^n-{shift}<{base}^n"
        rf"\quad\text{{and}}\quad {base - shift}\le a_n<{base}."
        rf"\quad a_1={base - shift},\quad a_n={base}\left(1-{shift}/{base}^n\right)^{{1/n}}"
        rf"\to{base}.",
    )


def bound_geometric_sum(a: int, b: int, c: int) -> Built:
    base = a + 1
    k = sp.Symbol("k", integer=True, positive=True)
    expr = sp.Sum(c / (base**k + b * k), (k, 1, N))
    lower, upper = sp.Rational(c, base + b), sp.Rational(c, base - 1)
    return finish(
        r"\text{Classify boundedness. Give the greatest lower bound and the upper bound from}"
        r"\text{ comparison with the geometric series }\sum_{k\ge1}"
        + tex(c / base**k)
        + r":\quad a_n="
        + tex(expr)
        + r",\quad n\ge1.",
        OrderedAnswer(
            (CategoryAnswer("both", BOUNDS), FormulaAnswer(lower), FormulaAnswer(upper)),
            BOUND_LABELS,
        ),
        r"\text{The summands are positive, so the partial sums increase.}",
        rf"a_n\ge a_1={tex(lower)},\qquad "
        rf"\frac{{{c}}}{{{base}^k+{b}k}}<\frac{{{c}}}{{{base}^k}}\ \Rightarrow\ "
        rf"a_n<\sum_{{k=1}}^\infty\frac{{{c}}}{{{base}^k}}=\frac{{{c}}}{{{base - 1}}}.",
    )


def monotone_exponential_difference(a: int, b: int, c: int) -> Built:
    small, large, scale = a + 1, a + 1 + (b + 1) // 2, b * c
    first = next(
        n for n in range(1, 200) if large**n * (large - 1) > scale * small**n * (small - 1)
    )
    threshold = sp.Rational(scale * (small - 1), large - 1)
    return finish(
        r"\text{Give the eventual strict direction and the least }N\ge1"
        r"\text{ for which it holds at every step }n\ge N:\quad a_n="
        + rf"{large}^n-{scale}\cdot{small}^n",
        OrderedAnswer(
            (CategoryAnswer("increasing", MONOTONICITY), FormulaAnswer(first)),
            MONOTONICITY_LABELS,
        ),
        r"\text{Compare consecutive terms. The ratio of the bases exceeds }1.",
        rf"a_{{n+1}}-a_n={large - 1}\cdot{large}^n-{scale * (small - 1)}\cdot{small}^n>0"
        rf"\iff\left(\frac{{{large}}}{{{small}}}\right)^n>{tex(threshold)}."
        rf"\quad\text{{The left side increases with }}n,\quad N={first}.",
    )


def monotone_rational(a: int, b: int, c: int) -> Built:
    shift = a * c * (a + c)
    expr = b * N / (N**2 + shift)
    first = next(n for n in range(1, 200) if n * (n + 1) > shift)
    return finish(
        r"\text{Give the eventual strict direction and the least }N\ge1"
        r"\text{ for which it holds at every step }n\ge N:\quad a_n=" + tex(expr),
        OrderedAnswer(
            (CategoryAnswer("decreasing", MONOTONICITY), FormulaAnswer(first)),
            MONOTONICITY_LABELS,
        ),
        r"\text{Bring the difference of consecutive terms to a common denominator.}",
        rf"a_{{n+1}}-a_n=\frac{{{b}\left({shift}-n(n+1)\right)}}"
        rf"{{(n^2+{shift})((n+1)^2+{shift})}}<0\iff n(n+1)>{shift},"
        rf"\qquad N={first}.",
    )


def monotone_conjugate(a: int, b: int, c: int) -> Built:
    radical = tex(sp.sqrt(N**2 + 2 * b * N + b * b + a))
    scale = "" if c == 1 else str(c)
    return finish(
        r"\text{Give the eventual strict direction and the least }N\ge1"
        r"\text{ for which it holds at every step }n\ge N:\quad a_n="
        + scale
        + r"\left("
        + radical
        + r"-n\right)",
        OrderedAnswer(
            (CategoryAnswer("decreasing", MONOTONICITY), FormulaAnswer(1)),
            MONOTONICITY_LABELS,
        ),
        rf"\text{{Write the radicand as }}(n+{b})^2+{a}\text{{ and rationalize.}}",
        rf"a_n={b * c}+\frac{{{a * c}}}{{\sqrt{{(n+{b})^2+{a}}}+n+{b}}}."
        r"\quad\text{The positive denominator strictly increases, so }N=1.",
    )


def definition_root(a: int, b: int, c: int) -> Built:
    return sequence_limit(
        grouped(a + c / sp.sqrt(N + b)),
        a,
        r"\text{Use the definition with an arbitrary }\varepsilon>0.",
        rf"|a_n-{a}|=\frac{{{c}}}{{\sqrt{{n+{b}}}}}<\varepsilon"
        rf"\quad\text{{if }}n>\frac{{{c * c}}}{{\varepsilon^2}}-{b}.",
    )


def definition_exponential(a: int, b: int, c: int) -> Built:
    base = a + 1
    bound = f"M+{b}" if c == 1 else rf"\frac{{M+{b}}}{{{c}}}"
    return sequence_limit(
        grouped(c * base**N - b),
        sp.oo,
        r"\text{For every real threshold }M\text{ choose an index after which }a_n>M.",
        rf"a_n>M\iff {base}^n>{bound}"
        rf"\quad\text{{if }}n>\log_{{{base}}}\max\left(1,{bound}\right).",
    )


def product_leading_orders(a: int, b: int, c: int) -> Built:
    expr = (a * N + 1) ** 2 * (b * N + 1) ** 4 / (c * N**2 + 1) ** 3
    value = sp.Rational(a**2 * b**4, c**3)
    return sequence_limit(
        expr,
        value,
        r"\text{Both sides have degree }6.\text{ Divide every factor by its power of }n.",
        rf"a_n=\frac{{({a}+1/n)^2({b}+1/n)^4}}{{({c}+1/n^2)^3}}"
        rf"\to\frac{{{a}^2\cdot{b}^4}}{{{c}^3}}={tex(value)}.",
    )


def competing_exponentials(a: int, b: int, c: int) -> Built:
    small, large = a + 1, a + b + 1
    expr = (large ** (N + 1) - small ** (N + 2)) / (c * large**N - small**N)
    value = sp.Rational(large, c)
    ratio = rf"\left(\frac{{{small}}}{{{large}}}\right)^n"
    return sequence_limit(
        expr,
        value,
        rf"\text{{Divide the numerator and denominator by the dominant power }}{large}^n.",
        rf"a_n=\frac{{{large}-{small * small}{ratio}}}{{{c}-{ratio}}}\to{tex(value)},"
        rf"\qquad{ratio}\to0.",
    )


def radical_degree(a: int, b: int, c: int) -> Built:
    value = a / sp.sqrt(c)
    return sequence_limit(
        rf"\frac{{{a if a > 1 else ''}n\sqrt{{n}}+{b}}}{{{tex(sp.sqrt(c * N**3 + 1))}}}",
        value,
        r"\text{Divide the numerator and denominator by }n^{3/2}.",
        rf"a_n=\frac{{{a}+{b}/n^{{3/2}}}}{{\sqrt{{{c}+1/n^3}}}}\to{tex(value)}.",
    )


def root_rational_sum(a: int, b: int, c: int) -> Built:
    inner = a / N + b / N**2 + c / N**3
    return sequence_limit(
        inner ** (1 / N),
        1,
        r"\text{Bound the positive radicand by multiples of }1/n.",
        rf"\frac{{\sqrt[n]{{{a}}}}}{{\sqrt[n]{{n}}}}\le a_n\le"
        rf"\frac{{\sqrt[n]{{{a + b + c}}}}}{{\sqrt[n]{{n}}}},\qquad"
        r"\sqrt[n]{d}\to1\ (d>0),\quad\sqrt[n]{n}\to1.",
    )


def negative_growing_power(a: int, b: int, c: int) -> Built:
    expr = ((N + a + b) / (N + a)) ** (a - c * N)
    return sequence_limit(
        expr,
        sp.exp(-b * c),
        r"\text{Take logarithms. The base is }1+u_n\text{ with }u_n\to0.",
        rf"\log a_n=({a}-{c}n)\log(1+u_n),\quad u_n=\frac{{{b}}}{{n+{a}}},"
        rf"\quad ({a}-{c}n)u_n\to-{b * c},\quad\frac{{\log(1+u_n)}}{{u_n}}\to1.",
    )


def product_of_powers(a: int, b: int, c: int) -> Built:
    low, high = a, a + b
    expr = ((low * N + 1) / (high * N)) ** N * ((high * N + c) / (low * N)) ** N
    return sequence_limit(
        expr,
        sp.exp(sp.Rational(1, low) + sp.Rational(c, high)),
        r"\text{Separately the factors tend to }0\text{ and }\infty."
        r"\text{ Multiply the bases first.}",
        rf"a_n=\left(1+\frac{{1}}{{{low}n}}\right)^n\left(1+\frac{{{c}}}{{{high}n}}\right)^n"
        rf"\to e^{{1/{low}}}e^{{{c}/{high}}}.",
    )


def reciprocal_power(a: int, b: int, c: int) -> Built:
    expr = (a * N / (a * N + b)) ** (c * N)
    power = rf"\left(1+\frac{{{b}}}{{{a}n}}\right)^{{{a}n/{b}}}"
    return sequence_limit(
        expr,
        sp.exp(-sp.Rational(b * c, a)),
        r"\text{Invert the base and use }(1+1/m)^m\to e.",
        rf"a_n=\left(1+\frac{{{b}}}{{{a}n}}\right)^{{-{c}n}}={power}^{{-{b * c}/{a}}},"
        rf"\qquad{power}\to e.",
    )


def rational_growth(a: int, b: int, c: int) -> Built:
    sign = 1 if (a + b + c) % 2 == 0 else -1
    expr = (sign * a * N**2 + b) / (c * N + 1)
    return sequence_limit(
        expr,
        sign * sp.oo,
        r"\text{The numerator has the higher degree. Divide by }n.",
        rf"a_n=\frac{{{tex(sign * a * N)}+{b}/n}}{{{c}+1/n}},"
        rf"\quad\text{{the numerator tends to }}{'+' if sign > 0 else '-'}\infty"
        rf"\text{{ and the denominator to }}{c}.",
    )


def radical_difference_growth(a: int, b: int, c: int) -> Built:
    slope = c + 1
    square = slope**2 + a - 3
    gap = a - 3
    expected = 0 if gap == 0 else sp.oo if gap > 0 else -sp.oo
    conclusion = (
        rf"\le\frac{{{b}}}{{{2 * slope}n}}\to0"
        if gap == 0
        else r"=\frac{"
        + tex(gap * N + b / N)
        + r"}{\sqrt{"
        + f"{square}+{b}/n^2"
        + r"}+"
        + str(slope)
        + r"}\to"
        + tex(expected)
    )
    return sequence_limit(
        r"\left(" + tex(sp.sqrt(square * N**2 + b)) + "-" + tex(slope * N) + r"\right)",
        expected,
        r"\text{Multiply and divide by the sum of the radical and }"
        + tex(slope * N)
        + r"\text{, then compare degrees.}",
        rf"a_n=\frac{{{tex(gap * N**2 + b)}}}{{\sqrt{{{square}n^2+{b}}}+{slope}n}}{conclusion}.",
    )


def inverse_trig_ratio(a: int, b: int, c: int) -> Built:
    top = a * sp.pi / 2 - b
    expected = sp.oo if top > 0 else -sp.oo
    scale = "" if a == 1 else str(a)
    return sequence_limit(
        rf"\frac{{{scale}\arctan n-{b}}}{{\operatorname{{arccot}}({tex(c * N)})}}",
        expected,
        r"\text{Find the limits of the numerator and of the positive denominator separately.}",
        rf"{a}\arctan n-{b}\to{tex(top)}{'>' if top > 0 else '<'}0,"
        rf"\qquad\operatorname{{arccot}}({tex(c * N)})\to0^+.",
    )


# #257: deduplicated exam forms of the sequence families.


def root_exponential_sum(a: int, b: int, c: int) -> Built:
    small, large = a + 1, a + b + 1
    return sequence_limit(
        rf"\sqrt[n]{{{small}^{{n+{c}}}+{large}^{{n+1}}}}",
        large,
        r"\text{Squeeze the radicand between multiples of the dominant power }" + rf"{large}^n.",
        rf"{large}^{{n+1}}\le {small}^{{n+{c}}}+{large}^{{n+1}}\le"
        rf"({small}^{{{c}}}+{large})\,{large}^n,\qquad"
        rf"{large}\sqrt[n]{{{large}}}\le a_n\le{large}\sqrt[n]{{{small**c + large}}}\to{large}.",
    )


def root_polynomial(a: int, b: int, c: int) -> Built:
    degree = b + 1
    scale = "" if a == 1 else str(a)
    return sequence_limit(
        rf"\sqrt[n]{{{scale}n^{{{degree}}}+{c}n+1}}",
        1,
        rf"\text{{Squeeze the radicand between }}n^{{{degree}}}"
        rf"\text{{ and }}{a + c + 1}n^{{{degree}}}.",
        rf"\left(\sqrt[n]{{n}}\right)^{{{degree}}}\le a_n\le\sqrt[n]{{{a + c + 1}}}"
        rf"\left(\sqrt[n]{{n}}\right)^{{{degree}}},\qquad\sqrt[n]{{n}}\to1.",
    )


def quartic_conjugate(a: int, b: int, c: int) -> Built:
    lead = "" if a == 1 else str(a)
    return sequence_limit(
        r"\left(" + tex(sp.sqrt(a * a * N**4 + b * N**3 + c)) + rf"-{lead}n^2\right)",
        sp.oo,
        r"\text{Multiply and divide by the sum, then divide by }n^2.",
        rf"a_n=\frac{{{b}n^3+{c}}}{{\sqrt{{{a * a}n^4+{b}n^3+{c}}}+{lead}n^2}}"
        rf"=\frac{{{b}n+{c}/n^2}}{{\sqrt{{{a * a}+{b}/n+{c}/n^4}}+{a}}}\to\infty"
        rf"\quad\text{{since the numerator grows like }}{b}n.",
    )


def conjugate_ratio(a: int, b: int, c: int) -> Built:
    top, bottom = a + b, c
    value = sp.Rational(top, bottom)
    return sequence_limit(
        rf"\frac{{\sqrt{{n^2+{top}}}-n}}{{\sqrt{{n^2+{bottom}}}-n}}",
        value,
        r"\text{Rationalize the numerator and the denominator separately.}",
        rf"a_n=\frac{{{top}}}{{{bottom}}}\cdot\frac{{\sqrt{{n^2+{bottom}}}+n}}"
        rf"{{\sqrt{{n^2+{top}}}+n}},\qquad\frac{{\sqrt{{n^2+{bottom}}}+n}}"
        rf"{{\sqrt{{n^2+{top}}}+n}}\to1.",
    )


def factorial_degree_ratio(a: int, b: int, c: int) -> Built:
    scale = "" if a == 1 else str(a)
    return sequence_limit(
        rf"\frac{{({scale}n+{b})(n+1)!}}{{n^2(n!+{c})}}",
        a,
        r"\text{Use }(n+1)!=(n+1)\,n!\text{ and divide by }n!.",
        rf"a_n=\frac{{({scale}n+{b})(n+1)}}{{n^2(1+{c}/n!)}}"
        rf"=\frac{{({a}+{b}/n)(1+1/n)}}{{1+{c}/n!}}\to{a}.",
    )


def exponential_product_ratio(a: int, b: int, c: int) -> Built:
    first, second = a + 1, b + 1
    return sequence_limit(
        rf"\frac{{({first}^n+1)({second}^{{n+1}}+{c})}}{{{first * second}^n+{a}}}",
        second,
        rf"\text{{Divide the numerator and denominator by }}{first * second}^n"
        rf"={first}^n\cdot{second}^n.",
        rf"a_n=\frac{{(1+{first}^{{-n}})({second}+{c}\cdot{second}^{{-n}})}}"
        rf"{{1+{a}\cdot{first * second}^{{-n}}}}\to{second}.",
    )


def reciprocal_exponential_conjugate(a: int, b: int, c: int) -> Built:
    base = a + 1
    value = sp.Rational(2 * b, c)
    return sequence_limit(
        rf"\frac{{{b}}}{{{base}^n\left(\sqrt{{{base * base}^n+{c}}}-{base}^n\right)}}",
        value,
        rf"\text{{Rationalize, using }}{base * base}^n=({base}^n)^2.",
        rf"a_n=\frac{{{b}\left(\sqrt{{{base * base}^n+{c}}}+{base}^n\right)}}{{{c}\cdot{base}^n}}"
        rf"=\frac{{{b}}}{{{c}}}\left(\sqrt{{1+{c}\cdot{base * base}^{{-n}}}}+1\right)"
        rf"\to{tex(value)}.",
    )


def product_radical(a: int, b: int, c: int) -> Built:
    value = sp.Rational(c * (a + b), 2)
    scale = "" if c == 1 else str(c)
    return sequence_limit(
        rf"{scale}\left(\sqrt{{(n+{a})(n+{b})}}-n\right)",
        value,
        r"\text{Multiply and divide by the sum, then divide by }n.",
        rf"a_n=\frac{{{scale}({a + b}n+{a * b})}}{{\sqrt{{(n+{a})(n+{b})}}+n}}"
        rf"=\frac{{{scale}({a + b}+{a * b}/n)}}{{\sqrt{{(1+{a}/n)(1+{b}/n)}}+1}}"
        rf"\to{tex(value)}.",
    )
