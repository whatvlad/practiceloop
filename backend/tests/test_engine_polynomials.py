"""#221: binomial theorem, polynomial roots, remainders and partial fractions."""

import sys

import pytest
import sympy as sp
from pydantic import ValidationError

from app.engine.generators.polynomials import (
    BinomialCoefficient,
    BinomialConstantTerm,
    BinomialExponent,
    CoefficientParams,
    ConstantTermParams,
    CubicRemainder,
    Divisibility,
    DivisibilityParams,
    ExponentParams,
    FactorParams,
    IrreducibleFactor,
    KnownComplexRoot,
    KnownRootParams,
    PartialCoefficientParams,
    PartialFractionCoefficient,
    PowerRemainderParams,
    RationalRootParams,
    RationalRoots,
    RemainderConditionParams,
    RemainderConditions,
    generators,
)
from app.engine.opening import rebuild
from app.engine.practice import input_variables, replay
from app.engine.topics.catalogue import topics
from app.math_input import parse_math_input
from app.services.math_worker import check_answer

X = sp.Symbol("x", real=True)
TOPIC_OF = {
    BinomialCoefficient.version: ("binomial-theorem", 1),
    BinomialConstantTerm.version: ("binomial-theorem", 2),
    BinomialExponent.version: ("binomial-theorem", 3),
    RationalRoots.version: ("polynomial-roots", 1),
    KnownComplexRoot.version: ("polynomial-roots", 2),
    IrreducibleFactor.version: ("polynomial-roots", 3),
    RemainderConditions.version: ("polynomial-division", 3),
    Divisibility.version: ("polynomial-division", 4),
    CubicRemainder.version: ("polynomial-division", 5),
    PartialFractionCoefficient.version: ("partial-fractions", 4),
}


def text(value: sp.Expr) -> str:
    return sp.sstr(value).replace("**", "^")


def check(generator, task, answer: str) -> str:
    variables = {"x"} if generator.polynomial_answer else None
    return task.answer.check(parse_math_input(answer, variables))


def test_every_generator_is_offered_at_its_declared_level() -> None:
    declared = topics()
    assert {g.version for g in generators()} == set(TOPIC_OF)
    for version, (slug, level) in TOPIC_OF.items():
        assert version in {choice.generator for choice in declared[slug].levels[level]}
        assert declared[slug].mixed_weight == 1


@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.version)
def test_tasks_replay_open_and_accept_only_their_own_answer(generator) -> None:
    slug, level = TOPIC_OF[generator.version]
    for seed in range(150):
        params = generator.draw(seed)
        task = generator.build(params)
        assert task == generator.build(type(params).model_validate_json(params.model_dump_json()))
        assert task.metadata["difficulty"] == level
        expected = text(task.answer.expected)
        assert check(generator, task, expected) == "correct"
        assert check(generator, task, f"({expected})+1") == "incorrect"
    opened = rebuild(task.code)
    assert opened.topic == slug
    assert replay(opened.problem.issued().record) == task
    # The worker reads the grammar from the code before parsing an answer.
    input_variables(opened.problem.issued().record)


def test_binomial_tasks_match_pdf_exercises_5_and_7() -> None:
    # 5(a): the coefficient of b^3 in (b + 4)^5 is C(5, 3) 4^2 = 160.
    task = BinomialCoefficient().build(CoefficientParams(seed=0, a=1, b=4, n=5, k=3))
    assert task.answer.expected == 160
    # 5(c) style: the constant term of (2x - 1/x)^6 is C(6, 3) 2^3 (-1)^3 = -160.
    constant = BinomialConstantTerm().build(ConstantTermParams(seed=0, a=2, b=-1, p=1, q=1, n=6))
    assert constant.answer.expected == -160
    # 7: the coefficient of x^2 in (1 - 3x)^n is 90, so n = 5.
    exponent = BinomialExponent().build(ExponentParams(seed=0, a=-3, n=5))
    assert "is 90" in exponent.statement and exponent.answer.expected == 5
    with pytest.raises(ValidationError):
        ConstantTermParams(seed=0, a=1, b=1, p=1, q=1, n=5)


def test_binomial_results_match_the_expansion() -> None:
    for seed in range(200):
        params = BinomialConstantTerm().draw(seed)
        expansion = sp.expand((params.a * X**params.p + params.b / X**params.q) ** params.n)
        task = BinomialConstantTerm().build(params)
        assert task.answer.expected == expansion.as_coefficients_dict()[sp.Integer(1)]


def test_roots_and_factors_match_pdf_exercises_55_57_and_58() -> None:
    rational = RationalRoots().build(
        RationalRootParams(seed=0, roots=((-1, 3), (2, 1)), quadratic=(0, 1))
    )
    assert rational.answer.expected == 2
    known = KnownComplexRoot().build(KnownRootParams(seed=0, real=2, complex_root=(1, -1)))
    assert known.answer.expected == 2
    factor = IrreducibleFactor().build(FactorParams(seed=0, root=3, quadratic=(2, 3), leading=1))
    # 58(b, c) style: x^3 - x^2 - 3x - 9 = (x - 3)(x^2 + 2x + 3).
    assert sp.expand(factor.answer.expected - (X**2 + 2 * X + 3)) == 0
    with pytest.raises(ValidationError):
        RationalRootParams(seed=0, roots=((1, 2), (2, 4)), quadratic=(0, 1))
    with pytest.raises(ValidationError):
        FactorParams(seed=0, root=1, quadratic=(4, 3), leading=1)


def test_rational_roots_are_all_the_rational_roots() -> None:
    for seed in range(200):
        params = RationalRoots().draw(seed)
        task = RationalRoots().build(params)
        (p1, q1), (p2, q2) = params.roots
        b, c = params.quadratic
        polynomial = (q1 * X - p1) * (q2 * X - p2) * (X**2 + b * X + c)
        real = [r for r in sp.real_roots(sp.Poly(sp.expand(polynomial), X))]
        assert task.answer.expected == max(real)


def test_remainder_tasks_match_pdf_exercises_61_62_and_63c() -> None:
    # 61: 2x^3 + ax^2 + bx + 1 leaves 4 at x = 1 and 15 at x = 2.
    params = RemainderConditionParams(seed=0, a=-2, b=3, leading=2, constant=1, points=(1, 2, -1))
    task = RemainderConditions().build(params)
    assert "remainder 4" in task.statement and "remainder 15" in task.statement
    assert task.answer.expected == -6
    # 62: ax^3 + bx^2 + 11x - 6 divisible by x^2 - 4x + 3: a = 1, b = -6.
    divisible = Divisibility().build(
        DivisibilityParams(seed=0, roots=(1, 3), a=1, b=-2, target="b")
    )
    assert "+11x-6" in divisible.statement and divisible.answer.expected == -6
    # 63(c): x^81 + x^49 + x^25 leaves 3x modulo x^3 - x.
    cubic = CubicRemainder().build(
        PowerRemainderParams(seed=0, exponents=(81, 49, 25), coefficients=(1, 1, 1))
    )
    assert sp.expand(cubic.answer.expected - 3 * X) == 0
    assert cubic.answer.check(parse_math_input("3x", {"x"})) == "correct"
    with pytest.raises(ValidationError):
        RemainderConditionParams(seed=0, a=1, b=1, leading=1, constant=1, points=(0, 1, 2))


def test_cubic_remainders_match_division() -> None:
    for seed in range(200):
        params = CubicRemainder().draw(seed)
        polynomial = sum(
            c * X**e for c, e in zip(params.coefficients, params.exponents, strict=True)
        )
        task = CubicRemainder().build(params)
        assert sp.expand(task.answer.expected - sp.rem(polynomial, X**3 - X, X)) == 0


def test_partial_fraction_constants_match_apart() -> None:
    task = PartialFractionCoefficient().build(
        PartialCoefficientParams(
            seed=0, pole=0, other=-1, numerators=(1, -1, 2), quadratic=False, target=2
        )
    )
    assert task.answer.expected == 2
    for seed in range(100):
        params = PartialFractionCoefficient().draw(seed)
        assert (
            PartialFractionCoefficient().build(params).answer.expected
            == (params.numerators[params.target])
        )
    with pytest.raises(ValidationError):
        PartialCoefficientParams(
            seed=0, pole=1, other=1, numerators=(1, 1, 1), quadratic=False, target=0
        )


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.version)
def test_polynomial_answers_are_checked_in_the_limited_worker(generator) -> None:
    task = generator.build(generator.draw(147))
    record = {"generator_version": generator.version, "code": task.code}
    answer = text(task.answer.expected)
    assert check_answer(answer, record).result == "correct"
    assert check_answer(f"({answer})+1", record).result == "incorrect"
