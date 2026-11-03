"""#221: matrix sums, transposes and products (algebra30 exercises 8-9)."""

import sys

import pytest
import sympy as sp
from pydantic import ValidationError

from app.engine.generators.matrix_operations import (
    MatrixCombination,
    MatrixCommutator,
    MatrixProduct,
    OperationParams,
    generators,
)
from app.engine.opening import rebuild
from app.engine.practice import input_variables, replay
from app.engine.topics.catalogue import topics
from app.math_input import parse_math_input
from app.services.math_worker import check_answer

TOPIC_OF = {
    MatrixCombination.version: 1,
    MatrixProduct.version: 2,
    MatrixCommutator.version: 3,
}


@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.version)
def test_tasks_are_offered_replay_and_accept_only_their_own_answer(generator) -> None:
    level = TOPIC_OF[generator.version]
    assert generator.version in {
        choice.generator for choice in topics()["matrix-operations"].levels[level]
    }
    for seed in range(200):
        params = generator.draw(seed)
        task = generator.build(params)
        assert task == generator.build(type(params).model_validate_json(params.model_dump_json()))
        expected = str(task.answer.expected)
        assert task.answer.check(parse_math_input(expected)) == "correct"
        assert task.answer.check(parse_math_input(f"{expected}+1")) == "incorrect"
    opened = rebuild(task.code)
    assert (opened.topic, opened.difficulty) == ("matrix-operations", level)
    assert replay(opened.problem.issued().record) == task
    assert input_variables(opened.problem.issued().record) is None


def test_operations_match_pdf_exercises_8_and_9a() -> None:
    a = ((1, 4, -3), (6, 3, 0))
    c = ((2, 4), (4, 0), (-2, 2))
    # 8: C - 2A^T has the entry 4 - 2*6 = -8 in row 1, column 2.
    combination = MatrixCombination().build(
        OperationParams(seed=0, first=a, second=c, scales=(-2, 1), row=0, column=1)
    )
    assert combination.answer.expected == 4 - 2 * 6
    # 9(a): AB - BA for A = [[1, 3], [-1, 2]], B = [[4, 0], [5, 1]].
    commutator = MatrixCommutator().build(
        OperationParams(
            seed=0, first=((1, 3), (-1, 2)), second=((4, 0), (5, 1)), scales=(1, 1), row=0, column=0
        )
    )
    first, second = sp.Matrix([[1, 3], [-1, 2]]), sp.Matrix([[4, 0], [5, 1]])
    assert commutator.answer.expected == (first * second - second * first)[0, 0]
    with pytest.raises(ValidationError):
        OperationParams(seed=0, first=a, second=c, scales=(0, 1), row=0, column=0)


def test_products_match_sympy() -> None:
    for seed in range(200):
        params = MatrixProduct().draw(seed)
        product = sp.Matrix(params.first) * sp.Matrix(params.second)
        task = MatrixProduct().build(params)
        assert task.answer.expected == product[params.row, params.column]


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.version)
def test_matrix_answers_are_checked_in_the_limited_worker(generator) -> None:
    task = generator.build(generator.draw(147))
    record = {"generator_version": generator.version, "code": task.code}
    answer = str(task.answer.expected)
    assert check_answer(answer, record).result == "correct"
    assert check_answer(f"{answer}+1", record).result == "incorrect"
