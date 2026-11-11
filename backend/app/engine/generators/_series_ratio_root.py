"""Ratio/root tests and sequence limits deduced from series (#273)."""

import sympy as sp

from app.engine.answers.computational import CategoryAnswer, LimitAnswer, OrderedAnswer
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._improper_integrals import CONVERGENCE
from app.engine.generators._sequence_limits import finish

N = sp.Symbol("n", integer=True, positive=True)
TEST_LABELS = ("Test limit", "Convergence")


def test_problem(
    term: sp.Expr, limit: sp.Expr, converges: bool, test_name: str, work: str
) -> Built:
    classification = "converges" if converges else "diverges"
    answer = OrderedAnswer(
        (LimitAnswer(limit), CategoryAnswer(classification, CONVERGENCE)),
        TEST_LABELS,
    )
    return finish(
        rf"\text{{Use the {test_name} test on }}\sum_{{n=1}}^\infty {tex(term)}."
        r"\text{ Give (test limit; converges or diverges). If "
        r"the test limit is one, also use the term condition.}",
        answer,
        (
            r"L=\lim_{n\to\infty}|a_{n+1}/a_n|."
            if test_name == "ratio"
            else r"L=\lim_{n\to\infty}\sqrt[n]{|a_n|}."
        ),
        work + rf"\quad L={tex(limit)}\text{{ and the series }}\text{{{classification}}}.",
    )


def exponential_over_multiple_factorial(a: int, b: int, c: int) -> Built:
    base = a + b + 1
    multiple = 2 + c % 2
    return test_problem(
        base**N / sp.factorial(multiple * N),
        sp.S.Zero,
        True,
        "ratio",
        rf"\frac{{a_{{n+1}}}}{{a_n}}=\frac{{{base}}}{{({multiple}n+1)"
        rf"\cdots({multiple}n+{multiple})}}\to0<1.",
    )


def exponential_over_polynomial(a: int, b: int, c: int) -> Built:
    base = a + 1
    power = c + 2
    return test_problem(
        (base**N + b) / (N**power + 1),
        sp.Integer(base),
        False,
        "ratio",
        rf"\frac{{a_{{n+1}}}}{{a_n}}=\frac{{{base}^{{n+1}}+{b}}}{{{base}^n+{b}}}"
        rf"\frac{{n^{{{power}}}+1}}{{(n+1)^{{{power}}}+1}}\to{base}>1.",
    )


def factorial_over_self_power(a: int, b: int, c: int) -> Built:
    limit = a / sp.E
    return test_problem(
        b * a**N * sp.factorial(N) / N**N,
        limit,
        a <= 2,
        "ratio",
        rf"\frac{{a_{{n+1}}}}{{a_n}}={a}\left(\frac n{{n+1}}\right)^n\to\frac{{{a}}}e."
        rf"\quad 2<e<3\text{{ decides which side of one this limit lies on.}}",
    )


def self_power_over_factorial(a: int, b: int, c: int) -> Built:
    base = a + 1
    limit = sp.E / base
    return test_problem(
        c * N**N / (base**N * sp.factorial(N)),
        limit,
        base >= 3,
        "ratio",
        rf"\frac{{a_{{n+1}}}}{{a_n}}=\frac1{{{base}}}\left(1+\frac1n\right)^n\to\frac e{{{base}}}."
        r"\quad 2<e<3\text{ decides the comparison with one.}",
    )


def central_binomial_ratio(a: int, b: int, c: int) -> Built:
    limit = sp.Rational(a, 4)
    work = rf"\frac{{a_{{n+1}}}}{{a_n}}=\frac{{{a}(n+1)^2}}{{(2n+2)(2n+1)}}\to\frac{{{a}}}4."
    if a == 4:
        work += r"\quad\binom{2n}n\le\sum_{k=0}^{2n}\binom{2n}k=4^n."
        work += (
            rf"\quad a_n={c}\frac{{4^n}}{{\binom{{2n}}n}}\ge{c}>0"
            r"\text{, so the terms do not tend to zero.}"
        )
    return test_problem(
        c * a**N * sp.factorial(N) ** 2 / sp.factorial(2 * N),
        limit,
        a < 4,
        "ratio",
        work,
    )


def quadratic_self_power_root(a: int, b: int, c: int) -> Built:
    limit = sp.Rational(a * a, c)
    work = rf"\sqrt[n]{{a_n}}=\frac{{({a}n+{b})^2}}{{{c}n^2+1}}\to\frac{{{a * a}}}{{{c}}}."
    if a * a == c:
        work += rf"\quad a_n=\left(1+\frac{{{2 * a * b}n+{b * b - 1}}}{{{a * a}n^2+1}}\right)^n"
        work += rf"\to e^{{{tex(sp.Rational(2 * b, a))}}}>0\text{{, so the term condition fails.}}"
    return test_problem(
        (a * N + b) ** (2 * N) / (c * N * N + 1) ** N, limit, a * a < c, "root", work
    )


def exponential_quotient_root(a: int, b: int, c: int) -> Built:
    small = a + 1
    middle = small + b
    large = middle + c
    limit = sp.Rational(middle, large)
    return test_problem(
        (small**N + middle**N) / (middle**N + large**N),
        limit,
        True,
        "root",
        rf"\sqrt[n]{{a_n}}=\frac{{{middle}}}{{{large}}}"
        rf"\left(\frac{{1+({tex(sp.Rational(small, middle))})^n}}{{1+({tex(limit)})^n}}"
        rf"\right)^{{1/n}}"
        rf"\to{tex(limit)}<1.",
    )


def power_quotient_root(a: int, b: int, c: int) -> Built:
    limit = a * sp.exp(-b)
    return test_problem(
        a**N * (N / (N + b)) ** (N * N),
        limit,
        b >= 2 or a <= 2,
        "root",
        rf"\sqrt[n]{{a_n}}={a}\left(\frac n{{n+{b}}}\right)^n"
        rf"={a}(1+{b}/n)^{{-n}}\to {a}e^{{-{b}}}.\quad "
        rf"5/2<e<3\text{{ decides the comparison with one.}}",
    )


def arctangent_power_root(a: int, b: int, c: int) -> Built:
    limit = sp.atan(a)
    comparison = (
        r"\arctan1=\pi/4<1."
        if a == 1
        else rf"\arctan({a})\ge\arctan2=\pi/2-\arctan(1/2)>3/2-1/2=1."
    )
    return test_problem(
        c * sp.atan(a * N / (N + b)) ** N,
        limit,
        a == 1,
        "root",
        rf"\sqrt[n]{{a_n}}={c}^{{1/n}}\arctan\frac{{{a}n}}{{n+{b}}}\to\arctan({a}).\quad"
        + comparison,
    )


def sequence_limit(term: sp.Expr, value: sp.Expr, proof: str) -> Built:
    return finish(
        rf"\text{{Using a suitable series and the necessary term "
        rf"condition, evaluate }}\lim_{{n\to\infty}}{tex(term)}.",
        LimitAnswer(value),
        r"\text{Prove convergence of the associated "
        r"positive-term series, then use its term limit.}",
        proof,
    )


def polynomial_exponential_sequence_limit(a: int, b: int, c: int) -> Built:
    power = (a + 1) * (c + 1)
    base = b + 1
    return sequence_limit(
        c * N**power / base**N,
        sp.S.Zero,
        rf"u_n=\frac{{{c}n^{{{power}}}}}{{{base}^n}}>0,\quad"
        rf"\frac{{u_{{n+1}}}}{{u_n}}=\frac1{{{base}}}(1+1/n)^{{{power}}}\to1/{base}<1."
        r"\quad\sum u_n\text{ converges, hence }u_n\to0.",
    )


def self_power_squared_factorial_limit(a: int, b: int, c: int) -> Built:
    return sequence_limit(
        b * a**N * N**N / sp.factorial(N) ** 2,
        sp.S.Zero,
        rf"u_n=\frac{{{b}\,{a}^n n^n}}{{(n!)^2}},\quad"
        rf"\frac{{u_{{n+1}}}}{{u_n}}=\frac{{{a}}}{{n+1}}(1+1/n)^n\to0<1."
        r"\quad\sum u_n\text{ converges, so }u_n\to0.",
    )


def self_power_factorial_infinite_limit(a: int, b: int, c: int) -> Built:
    return sequence_limit(
        c * a**N * N**N / sp.factorial(N),
        sp.oo,
        rf"v_n=\frac{{n!}}{{{a}^n n^n}}>0,\quad"
        rf"\frac{{v_{{n+1}}}}{{v_n}}=\frac1{{{a}}}\left(\frac n{{n+1}}\right)^n\to\frac1{{{a}e}}<1."
        rf"\quad v_n\to0^+,\quad u_n={c}/v_n\to\infty.",
    )


def balanced_factorial_sequence_limit(a: int, b: int, c: int) -> Built:
    small = a
    first = a + b
    second = a + c
    large = a + b + c
    ratio = sp.Rational(first**first * second**second, large**large * small**small)
    return sequence_limit(
        sp.factorial(first * N)
        * sp.factorial(second * N)
        / (sp.factorial(large * N) * sp.factorial(small * N)),
        sp.S.Zero,
        rf"p={first},\ q={second},\ r={large},\ s={small},\quad p+q=r+s."
        rf"\quad\lim\frac{{u_{{n+1}}}}{{u_n}}=\frac{{p^p q^q}}{{r^r s^s}}={tex(ratio)}<1."
        r"\quad\text{Strict convexity of }t\ln t\text{ gives }r\ln r+s\ln s>p\ln p+q\ln q."
        r"\quad\sum u_n\text{ converges, hence }u_n\to0.",
    )
