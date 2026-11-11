"""Corrected series identities and exact numerical sums (#276)."""

from dataclasses import replace

import sympy as sp

from app.engine.answers.computational import FormulaAnswer
from app.engine.answers.domain_formula import DomainFormulaAnswer
from app.engine.generators._alternating_power_series import convergence_visual
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._sequence_limits import finish

X = sp.Symbol("x", real=True)
N = sp.Symbol("n", integer=True, nonnegative=True)


def identity(term: sp.Expr, value: sp.Expr, domain: sp.Set, method: str, proof: str) -> Built:
    built = finish(
        rf"\text{{Find a closed form in }}x\text{{ for }}"
        rf"\sum_{{n=1}}^\infty {tex(term)},\quad x\in{tex(domain)}.",
        DomainFormulaAnswer(value, domain),
        method,
        proof + rf"\quad\sum_{{n=1}}^\infty {tex(term)}={tex(value)}.",
    )
    return replace(built, visual=convergence_visual(domain))


def weighted_geometric_identity(a: int, b: int, c: int) -> Built:
    return identity(
        a * N * (b * X) ** N,
        a * b * X / (1 - b * X) ** 2,
        sp.Interval.open(-sp.Rational(1, b), sp.Rational(1, b)),
        r"\sum_{n=0}^\infty t^n=(1-t)^{-1}.\quad"
        r"\text{Differentiate inside the radius and multiply by }t.",
        rf"t\frac d{{dt}}\frac1{{1-t}}=\frac t{{(1-t)^2}}."
        rf"\quad t={b}x\text{{ and multiply by }}{a}.",
    )


def quadratic_geometric_identity(a: int, b: int, c: int) -> Built:
    return identity(
        a * N * (N + 1) * (b * X) ** N,
        2 * a * b * X / (1 - b * X) ** 3,
        sp.Interval.open(-sp.Rational(1, b), sp.Rational(1, b)),
        r"\frac{t^2}{1-t}=\sum_{n=1}^\infty t^{n+1}.\quad"
        r"\text{Differentiate twice and multiply by }t.",
        rf"t\frac{{d^2}}{{dt^2}}\frac{{t^2}}{{1-t}}=\frac{{2t}}{{(1-t)^3}}."
        rf"\quad t={b}x\text{{ and multiply by }}{a}.",
    )


def corrected_factorial_identity(a: int, b: int, c: int) -> Built:
    return identity(
        a * (b * X) ** N / sp.factorial(N),
        a * (sp.exp(b * X) - 1),
        sp.S.Reals,
        r"e^t=\sum_{n=0}^\infty t^n/n!.\quad\text{Remove the constant term before rescaling.}",
        rf"\sum_{{n=1}}^\infty\frac{{t^n}}{{n!}}=e^t-1.\quad t={b}x\text{{ and multiply by }}{a}."
        r"\quad\text{The factorial series converges for every real }x.",
    )


def numerical_sum(term: sp.Expr, start: int, value: sp.Expr, method: str, proof: str) -> Built:
    return finish(
        rf"\text{{Evaluate the exact sum }}\sum_{{n={start}}}^\infty {tex(term)}.",
        FormulaAnswer(value),
        method,
        proof + rf"\quad S={tex(value)}.",
    )


def logarithmic_shift_sum(a: int, b: int, c: int) -> Built:
    base = b + 1
    ratio = sp.Rational(1, base)
    value = -a * base * sp.log(1 - ratio)
    return numerical_sum(
        a / ((N + 1) * base**N),
        0,
        value,
        r"\text{Integrate the geometric series to obtain }\sum_{k=1}^\infty r^k/k=-\ln(1-r).",
        rf"r=1/{base},\quad S=\frac{{{a}}}r\sum_{{k=1}}^"
        rf"\infty\frac{{r^k}}k=-\frac{{{a}}}r\ln(1-r).",
    )


def linear_weighted_sum(a: int, b: int, c: int) -> Built:
    offset = 1 + (b - 1) % a
    base = c + 1
    ratio = sp.Rational(1, base)
    value = sp.factor(
        a * ratio / (1 - ratio) ** 2 - offset * ratio / (1 - ratio) - (a - offset) * ratio
    )
    return numerical_sum(
        (a * N - offset) / base**N,
        2,
        value,
        r"\sum_{n=1}^\infty nr^n=\frac r{(1-r)^2},\quad\sum_{n=1}^\infty r^n=\frac r{1-r}.",
        rf"r=1/{base}.\quad\text{{Form }}{a}\sum nr^n-{offset}\sum r^n"
        rf"\text{{ and subtract its }}n=1\text{{ term }}({a}-{offset})r.",
    )


def quadratic_weighted_sum(a: int, b: int, c: int) -> Built:
    base = b + c + 1
    value = sp.Rational(2 * a * base * base, (base - 1) ** 3)
    return numerical_sum(
        a * N * (N + 1) / base**N,
        1,
        value,
        r"\sum_{n=1}^\infty n(n+1)r^n=\frac{2r}{(1-r)^3}.",
        rf"r=1/{base},\quad S={a}\frac{{2/{base}}}{{(1-1/{base})^3}}.",
    )


def weighted_logarithmic_sum(a: int, b: int, c: int) -> Built:
    base = b + c + 1
    ratio = sp.Rational(1, base)
    value = sp.Rational(a * base, base - 1) + a * base * sp.log(1 - ratio)
    return numerical_sum(
        a * N / ((N + 1) * base**N),
        1,
        value,
        r"\frac n{n+1}=1-\frac1{n+1}.\quad\text{Use a "
        r"geometric sum and the integrated geometric series.}",
        rf"r=1/{base},\quad S={a}\left[\frac r{{1-r}}-\left(-\frac{{\ln(1-r)}}r-1\right)\right]"
        rf"={a}\left[\frac1{{1-r}}+\frac{{\ln(1-r)}}r\right].",
    )
