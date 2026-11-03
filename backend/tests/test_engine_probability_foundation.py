"""Independent mathematics and adversarial input tests for #200."""

import json
from fractions import Fraction as F
from pathlib import Path
from statistics import covariance, mean, median, pvariance, variance

import mpmath as mp
import pytest
import sympy as sp

from app.engine.answers.structured import (
    BooleanAnswer,
    FiniteSetAnswer,
    IntervalAnswer,
    RealScalarAnswer,
)
from app.engine.blocks.distribution import (
    DensitySegment,
    ExponentialDistribution,
    FiniteDistribution,
    JointDistribution,
    NormalDistribution,
    PolynomialDensity,
    StandardDistribution,
    UniformDistribution,
)
from app.engine.blocks.statistics import (
    NORMAL_CDF,
    T95,
    Z_TWO_SIDED,
    PairedSample,
    Sample,
    mean_interval,
    mean_statistic,
    reject,
)
from app.math_input import (
    MathInputError,
    MathInputTooLong,
    build_expression,
    parse_answer_input,
    parse_math_input,
)


@pytest.mark.parametrize(
    "answer,text,expected",
    [
        (BooleanAnswer(True), "true", "correct"),
        (BooleanAnswer(False), "true", "incorrect"),
        (FiniteSetAnswer((F(1, 2), sp.sqrt(2))), "{sqrt(8)/2,2/4,1/2}", "correct"),
        (FiniteSetAnswer(()), "{}", "correct"),
        (FiniteSetAnswer((1, 2)), "{2,1}", "correct"),
        (FiniteSetAnswer((1, 2)), "{1,3}", "incorrect"),
        (FiniteSetAnswer((0,)), "{0*(1/0)}", "invalid"),
        (FiniteSetAnswer((0,)), "{sqrt(-1)}", "invalid"),
        (IntervalAnswer(F(1, 2), sp.sqrt(2)), "[2/4,sqrt(8)/2]", "correct"),
        (IntervalAnswer(0, 1), "(0,1)", "incorrect"),
        (IntervalAnswer(0, 1), "[1,0]", "invalid"),
        (IntervalAnswer(0, 1), "[0,0]", "incorrect"),
        (IntervalAnswer(0, 0), "[0,0]", "correct"),
        (IntervalAnswer(0, 1), "(0,0)", "invalid"),
        (RealScalarAnswer(-1, {}), "sqrt(-1)^2", "invalid"),
        (FiniteSetAnswer((0,)), "{0*sqrt(-1)}", "invalid"),
        (IntervalAnswer(-sp.oo, 2, True, False), "(-inf,2]", "correct"),
        (IntervalAnswer(0, sp.oo, False, True), "[0,∞)", "correct"),
        (IntervalAnswer(0, 1), "[0,1+0*(1/0)]", "invalid"),
    ],
)
def test_structured_answers(answer, text, expected):
    try:
        tree = parse_answer_input(text, answer.kind)
    except MathInputError:
        assert expected == "invalid"
    else:
        assert answer.check(tree) == expected


@pytest.mark.parametrize(
    "kind,text",
    [
        ("boolean", "1"),
        ("boolean", "Yes"),
        ("boolean", "true or false"),
        ("finite_set", "{x-x}"),
        ("finite_set", "{1,}"),
        ("finite_set", "{1,{2}}"),
        ("finite_set", "{1,2,3,4,5,6,7,8,9}"),
        ("interval", "[-inf,2]"),
        ("interval", "(inf,2]"),
        ("interval", "[0,inf]"),
        ("interval", "[0,1,2]"),
        ("interval", "[0,1] union [2,3]"),
        ("interval", "[0,__import__(x)]"),
    ],
)
def test_new_grammars_reject_invalid_input(kind, text):
    with pytest.raises(MathInputError):
        parse_answer_input(text, kind)


def test_global_budgets_and_unchanged_scalar_parser():
    with pytest.raises(MathInputTooLong):
        parse_answer_input("{" + "1" * 257 + "}", "finite_set")
    with pytest.raises(MathInputError):
        parse_answer_input("{" + ",".join("sin(cos(sin(1)))" for _ in range(8)) + "}", "finite_set")
    for text in ("3/5", "sqrt(2)+pi", "sin(x)+C", "exp(2)"):
        assert parse_answer_input(text, "expression") == parse_math_input(text)
    with pytest.raises(ValueError):
        build_expression(parse_answer_input("true", "boolean"))


def test_finite_distribution_and_pushforward_by_independent_enumeration():
    d = FiniteDistribution.from_weights((-2, 0, 2), (1, 2, 3))
    outcomes = [-2, 0, 0, 2, 2, 2]
    assert d.moment(1) == mean(tuple(map(F, outcomes)))
    assert d.variance == pvariance(tuple(map(F, outcomes)))
    assert d.cdf(F(0)) == F(3, 6)
    image = d.pushforward(tuple(x * x for x in d.values))
    assert image.values == (F(0), F(4)) and image.masses == (F(1, 3), F(2, 3))
    assert image.moment(1) == mean(tuple(F(x * x) for x in outcomes))


def test_joint_marginals_conditionals_covariance_independence():
    d = JointDistribution(
        x=(F(0), F(1)), y=(F(0), F(2)), masses=((F(1, 8), F(3, 8)), (F(1, 8), F(3, 8)))
    )
    assert d.independent and d.covariance == 0 and d.conditional(1, 1) == F(1, 2)
    dependent = JointDistribution(x=d.x, y=d.y, masses=((F(1, 4), F(1, 4)), (F(0), F(1, 2))))
    assert not dependent.independent and dependent.covariance == F(1, 4)
    zero = JointDistribution(x=(F(0),), y=(F(0), F(1)), masses=((F(1), F(0)),))
    with pytest.raises(ValueError):
        zero.conditional(0, 1)


@pytest.mark.parametrize(
    "kind", ["bernoulli", "binomial", "geometric", "hypergeometric", "poisson"]
)
def test_standard_distribution_normalization_and_moments(kind):
    d = StandardDistribution(kind=kind, n=5, numerator=2, denominator=5, rate=3)
    k = sp.Symbol("k", integer=True, nonnegative=True)
    if kind in {"bernoulli", "binomial", "hypergeometric"}:
        masses = [d.pmf(j) for j in range(13)]
        assert sum(masses) == 1
        assert sum(j * p for j, p in enumerate(masses)) == d.mean
        assert sum((F(j) - d.mean) ** 2 * p for j, p in enumerate(masses)) == d.variance
    else:
        term = (
            sp.Rational(d.p) * (1 - sp.Rational(d.p)) ** k
            if kind == "geometric"
            else sp.exp(-3) * 3**k / sp.factorial(k)
        )
        offset = 1 if kind == "geometric" else 0
        assert sp.summation(term, (k, 0, sp.oo)) == 1
        assert sp.summation((k + offset) * term, (k, 0, sp.oo)) == sp.Rational(d.mean)
        assert sp.simplify(
            sp.summation((k + offset) ** 2 * term, (k, 0, sp.oo)) - sp.Rational(d.mean) ** 2
        ) == sp.Rational(d.variance)
    assert d.cdf(3) == sum(d.pmf(j) for j in range(4))


@pytest.mark.parametrize("degree", range(4))
def test_polynomial_density_against_symbolic_integration(degree):
    segments = (
        DensitySegment(lower=-2, upper=0, coefficients=(1,) * (degree + 1)),
        DensitySegment(lower=0, upper=3, coefficients=(2, 1)),
    )
    d = PolynomialDensity(segments=segments)
    x = sp.Symbol("x", real=True)
    normalizer = sum(sp.integrate(s.expression(x), (x, s.lower, s.upper)) for s in segments)
    assert normalizer == d.normalizer and d.probability(F(-12), F(12)) == 1
    for order in (0, 1, 2):
        assert sum(
            sp.integrate(x**order * s.expression(x) / normalizer, (x, s.lower, s.upper))
            for s in segments
        ) == d.moment(order)
    assert d.probability(F(-1), F(2)) == sum(
        sp.integrate(s.expression(x) / normalizer, (x, max(-1, s.lower), min(2, s.upper)))
        for s in segments
    )


def test_uniform_exponential_normal_forms():
    assert UniformDistribution(lower=-2, upper=3).probability(F(-4), F(1)) == F(3, 5)
    d = ExponentialDistribution(rate=F(2, 3))
    x = sp.Symbol("x", nonnegative=True)
    assert sp.integrate(sp.Rational(2, 3) * sp.exp(-2 * x / 3), (x, 0, sp.oo)) == 1
    assert sp.simplify(d.survival(F(2)) / d.survival(F(1)) - d.survival(F(1))) == 0
    assert sp.simplify(1 - sp.exp(-sp.Rational(d.rate) * d.quantile(F(3, 5))) - F(3, 5)) == 0
    assert NormalDistribution(mean=2, sigma=3).standardize(F(5)) == 1


def test_sample_statistics_against_standard_library_and_normal_equations():
    x = Sample(values=(-2, 1, 1, 3, 4, 4))
    y = Sample(values=(1, -2, 2, 4, 1, 5))
    p = PairedSample(x=x, y=y)
    xv, yv = tuple(map(F, x.values)), tuple(map(F, y.values))
    assert x.mean == mean(xv) and x.median == median(xv)
    assert x.variance() == variance(xv) and x.variance(False) == pvariance(xv)
    assert x.modes == (1, 4) and x.quartiles == (F(1), F(4))
    assert p.centered_product / (len(x.values) - 1) == F(83, 30)
    assert float(F(83, 30)) == pytest.approx(covariance(xv, yv))
    residuals = [F(v) - p.intercept - p.slope * u for u, v in zip(x.values, y.values, strict=True)]
    assert sum(residuals) == 0 and sum(u * r for u, r in zip(x.values, residuals, strict=True)) == 0


def test_supplied_rounded_reference_tables_have_certified_precision():
    with mp.workdps(40):

        def phi(z):
            return (1 + mp.erf(z / mp.sqrt(2))) / 2

        for z, value in NORMAL_CDF.items():
            assert abs(
                phi(mp.mpf(z.numerator) / z.denominator)
                - mp.mpf(value.numerator) / value.denominator
            ) < mp.mpf("0.000005")
        for coverage, z in Z_TWO_SIDED:
            q = mp.mpf(z.numerator) / z.denominator
            target = (1 + mp.mpf(coverage) / 100) / 2
            assert phi(q - mp.mpf(".0005")) < target < phi(q + mp.mpf(".0005"))
        for df, value in T95.items():

            def cdf(t, degrees=df):
                return (
                    1
                    - mp.betainc(
                        mp.mpf(degrees) / 2,
                        mp.mpf(".5"),
                        0,
                        degrees / (degrees + t * t),
                        regularized=True,
                    )
                    / 2
                )

            q = mp.mpf(value.numerator) / value.denominator
            assert cdf(q - mp.mpf(".0005")) < mp.mpf(".975") < cdf(q + mp.mpf(".0005"))


def test_inference_boundaries_and_center_width():
    lo, hi = mean_interval(sp.Rational(3), sp.Rational(2), 16, F(49, 25))
    assert (lo + hi) / 2 == 3 and hi - lo == sp.Rational(49, 25)
    assert mean_statistic(sp.Rational(5), sp.Rational(3), sp.Rational(2), 16) == 4
    for tail, value in (("two", F(-2)), ("upper", F(2)), ("lower", F(-2))):
        assert not reject(sp.Rational(value), F(2), tail)
        assert reject(sp.Rational(value * 2), F(2), tail)


@pytest.mark.parametrize(
    "make",
    [
        lambda: FiniteDistribution(values=(F(1), F(1)), masses=(F(1, 2), F(1, 2))),
        lambda: FiniteDistribution(values=(F(1),), masses=(F(-1),)),
        lambda: FiniteDistribution.from_weights((True,), (1,)),
        lambda: StandardDistribution(kind="binomial", n=True),
        lambda: StandardDistribution(kind="hypergeometric", population=3, draws=4),
        lambda: StandardDistribution(kind="geometric", numerator=3, denominator=3),
        lambda: DensitySegment(lower=0, upper=2, coefficients=(1, -1)),
        lambda: Sample(values=(1, 2, True)),
        lambda: ExponentialDistribution(rate=F(0)),
        lambda: UniformDistribution(lower=3, upper=2),
    ],
)
def test_strict_bounded_forms_reject_invalid_parameters(make):
    with pytest.raises(ValueError):
        make()


@pytest.mark.parametrize(
    "row",
    json.loads(
        (Path(__file__).parent / "fixtures/structured_answer_syntax.json").read_text(
            encoding="utf-8"
        )
    ),
)
def test_shared_structured_syntax_corpus(row):
    if row["valid"]:
        parse_answer_input(row["text"], row["kind"])
    else:
        with pytest.raises(MathInputError):
            parse_answer_input(row["text"], row["kind"])
