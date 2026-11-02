"""PDF exercises 1(a) and 3(a): exact radical simplification."""

import sys

import pytest
import sympy as sp
from pydantic import ValidationError

from app.engine.generators.algebra_expressions import (
    RadicalParams,
    RationalizeDenominator,
    RationalizeParams,
    SimplifyRadicals,
)
from app.engine.opening import rebuild
from app.math_input import parse_math_input
from app.services.math_worker import check_answer


@pytest.mark.parametrize("generator", [SimplifyRadicals(), RationalizeDenominator()])
def test_radical_exercises_check_equivalent_answers_and_replay(generator) -> None:
    for seed in range(64):
        params = generator.draw(seed)
        task = generator.build(params)
        assert task == generator.build(type(params).model_validate_json(params.model_dump_json()))
        expected = sp.sstr(task.answer.expected).replace("**", "^")
        assert task.answer.check(parse_math_input(expected)) == "correct"
        assert task.answer.check(parse_math_input(f"({expected})+1")) == "incorrect"
        opened = rebuild(task.code)
        assert opened.topic == "algebraic-expressions"
        assert opened.difficulty == task.metadata["difficulty"]


def test_radical_examples_match_the_pdf() -> None:
    simplified = SimplifyRadicals().build(
        RadicalParams(seed=0, coefficient=2, factor=3, radicand=3)
    )
    assert sp.simplify(simplified.answer.expected + sp.sqrt(3)) == 0
    assert simplified.answer.check(parse_math_input("-sqrt(3)")) == "correct"
    assert simplified.answer.check(parse_math_input("2sqrt(3)-sqrt(27)")) == "incorrect"
    assert simplified.answer.check(parse_math_input("2sqrt(3)-3sqrt(3)")) == "incorrect"
    assert simplified.answer.check(parse_math_input("2sqrt(3)-2sqrt(27/4)")) == "incorrect"
    assert simplified.answer.check(parse_math_input("-2sqrt(3/4)")) == "incorrect"
    assert simplified.answer.check(parse_math_input("2sqrt(3)-27^(3/2)/27")) == "incorrect"
    assert simplified.answer.check(parse_math_input("-3^(1/2)")) == "correct"
    rationalized = RationalizeDenominator().build(
        RationalizeParams(seed=0, coefficient=2, radicand=3)
    )
    assert sp.simplify(rationalized.answer.expected - (2 - sp.sqrt(3))) == 0
    assert rationalized.answer.check(parse_math_input("2-sqrt(3)")) == "correct"
    assert rationalized.answer.check(parse_math_input("(4-2sqrt(3))/2")) == "correct"
    assert rationalized.answer.check(parse_math_input("1/(2+sqrt(3))")) == "incorrect"
    assert rationalized.answer.check(parse_math_input("(2+sqrt(3))^(-1)")) == "incorrect"


@pytest.mark.parametrize("radicand", [2.0, True, 4, 999999999])
def test_radical_parameters_reject_noncanonical_radicands(radicand: object) -> None:
    with pytest.raises(ValidationError):
        RadicalParams(seed=0, coefficient=2, factor=3, radicand=radicand)
    with pytest.raises(ValidationError):
        RationalizeParams(seed=0, coefficient=2, radicand=radicand)


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize("generator", [SimplifyRadicals(), RationalizeDenominator()])
def test_radical_exercises_use_the_limited_worker(generator) -> None:
    task = generator.build(generator.draw(221))
    record = {"generator_version": generator.version, "code": task.code}
    answer = sp.sstr(task.answer.expected).replace("**", "^")
    assert check_answer(answer, record).result == "correct"
    assert check_answer(f"({answer})+1", record).result == "incorrect"
