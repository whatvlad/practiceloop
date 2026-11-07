"""Regression checks for new, versioned algebra practice."""

import sys

import pytest
import sympy as sp
from pydantic import ValidationError
from seed_sweep import sweep

from app.engine.generators.algebra_expansion import (
    PolynomialQuotient,
    QuadraticRemainder,
    QuadraticRemainderParams,
    RemainderParams,
    RemainderTheorem,
)
from app.engine.opening import rebuild
from app.engine.practice import replay
from app.engine.topics.catalogue import topics
from app.math_input import parse_math_input
from app.services.math_worker import check_answer


def test_quadratic_remainder_matches_pdf_example_and_replays() -> None:
    generator = QuadraticRemainder()
    params = QuadraticRemainderParams(seed=0, first=1, second=2, exponent=100)
    task = generator.build(params)
    x = sp.Symbol("x", real=True)
    expected = (2**100 - 1) * x + 2 - 2**100
    assert sp.expand(task.answer.expected - expected) == 0
    answer = "((2^10)^10-1)*x+2-(2^10)^10"
    assert task.answer.check(parse_math_input(answer, {"x"})) == "correct"
    assert task.answer.check(parse_math_input(f"({answer})+1", {"x"})) == "incorrect"
    assert task == generator.build(
        QuadraticRemainderParams.model_validate_json(params.model_dump_json())
    )


def test_quadratic_remainders_match_division_and_open_for_1000_seeds() -> None:
    generator = QuadraticRemainder()
    x = sp.Symbol("x", real=True)
    for seed in sweep(1000):
        params = generator.draw(seed)
        task = generator.build(params)
        divisor = (x - params.first) * (x - params.second)
        assert task.answer.expected == sp.rem(x**params.exponent, divisor, x)
        assert rebuild(task.code).difficulty == 2
        assert task.answer.check(parse_math_input(str(task.answer.expected), {"x"})) == "correct"


def test_quadratic_remainder_rejects_equal_roots() -> None:
    with pytest.raises(ValidationError):
        QuadraticRemainderParams(seed=0, first=1, second=1, exponent=3)


def test_quadratic_remainder_is_offered_and_replays() -> None:
    assert QuadraticRemainder.version in {
        choice.generator for choice in topics()["polynomial-division"].levels[2]
    }
    generator = QuadraticRemainder()
    task = generator.build(generator.draw(147))
    opened = rebuild(task.code)
    assert opened.topic == "polynomial-division"
    assert replay(opened.problem.issued().record) == task


def test_remainder_theorem_uses_exact_polynomial_evaluation_and_replays() -> None:
    generator = RemainderTheorem()
    params = generator.draw(147)
    task = generator.build(params)
    x = sp.Symbol("x", real=True)
    polynomial = params.a * x**2 + params.b * x + params.c
    assert task.answer.expected == polynomial.subs(x, params.root)
    assert task == generator.build(type(params).model_validate_json(params.model_dump_json()))
    assert task.steps and task.code and task.generator_version == generator.version


def test_remainder_theorem_is_offered_in_algebra_practice() -> None:
    choices = topics()["polynomial-division"].levels[1]
    assert RemainderTheorem.version in {choice.generator for choice in choices}
    assert PolynomialQuotient.version in {
        choice.generator for choice in topics()["polynomial-division"].levels[2]
    }
    assert RemainderTheorem.version not in {
        choice.generator for choice in topics()["fundamental-theorem-algebra"].levels[1]
    }


def test_remainder_theorem_accepts_own_answer_for_many_seeds() -> None:
    generator = RemainderTheorem()
    x = sp.Symbol("x", real=True)
    for seed in sweep(1000):
        params = generator.draw(seed)
        task = generator.build(params)
        polynomial = params.a * x**2 + params.b * x + params.c
        assert task.answer.expected == sp.rem(polynomial, x - params.root, x)
        assert task.answer.check(parse_math_input(str(task.answer.expected))) == "correct"
        assert task.answer.check(parse_math_input(str(task.answer.expected + 1))) == "incorrect"


def test_remainder_parameters_reject_out_of_range_values() -> None:
    with pytest.raises(ValidationError):
        RemainderParams(seed=0, a=0, b=0, c=0, root=0)


def test_remainder_code_opens_and_replays() -> None:
    generator = RemainderTheorem()
    task = generator.build(generator.draw(147))
    opened = rebuild(task.code)
    assert opened.topic == "polynomial-division"
    assert opened.difficulty == 1
    assert opened.problem.issued().record == {
        "generator_version": generator.version,
        "code": task.code,
    }
    assert replay(opened.problem.issued().record) == task


def test_polynomial_division_returns_quotient_of_dividend() -> None:
    generator = PolynomialQuotient()
    params = generator.draw(147)
    task = generator.build(params)
    x = sp.Symbol("x", real=True)
    dividend = params.a * x**2 + params.b * x + params.c
    assert sp.expand(task.answer.expected - sp.div(dividend, x - params.root, x)[0]) == 0


def test_polynomial_division_replays_and_checks_1000_draws() -> None:
    generator = PolynomialQuotient()
    x = sp.Symbol("x", real=True)
    for seed in sweep(1000):
        params = generator.draw(seed)
        task = generator.build(params)
        dividend = params.a * x**2 + params.b * x + params.c
        assert task.answer.expected == sp.div(dividend, x - params.root, x)[0]
        assert task.answer.check(parse_math_input(str(task.answer.expected), {"x"})) == "correct"
        assert rebuild(task.code).difficulty == 2


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize(
    "generator", [RemainderTheorem(), PolynomialQuotient(), QuadraticRemainder()]
)
def test_polynomial_answers_are_checked_in_the_limited_worker(generator) -> None:
    task = generator.build(generator.draw(147))
    record = {"generator_version": generator.version, "code": task.code}
    answer = sp.sstr(task.answer.expected).replace("**", "^")
    assert check_answer(answer, record).result == "correct"
    assert check_answer(f"({answer})+1", record).result == "incorrect"
