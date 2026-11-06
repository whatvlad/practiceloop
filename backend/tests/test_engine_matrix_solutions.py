"""Detailed matrix solutions must show the calculations behind the result."""

import pytest

from app.engine.generators.matrix_full import detailed_generators
from app.engine.opening import rebuild
from app.engine.practice import input_contract, replay
from app.math_input.structured import parse_answer_input


@pytest.mark.parametrize("generator", detailed_generators(), ids=lambda item: item.version)
def test_detailed_solution_is_correct_and_replayable(generator) -> None:
    for seed in range(8):
        task = generator.build(generator.draw(seed))
        assert len(task.steps) >= 2
        assert any(step.text_key == "expand" for step in task.steps)
        assert task.answer.latex() in task.steps[-1].latex
        record = {"generator_version": task.generator_version, "code": task.code}
        assert replay(record) == task
        assert rebuild(task.code).problem.code == task.code
        expected = (
            "("
            + ";".join(
                "(" + ";".join(str(entry).replace("**", "^") for entry in row) + ")"
                for row in task.answer.expected
            )
            + ")"
        )
        assert (
            task.answer.check(
                parse_answer_input(expected, "tuple", contract=input_contract(record))
            )
            == "correct"
        )


def test_product_expansion_shows_every_result_cell() -> None:
    from app.engine.generators.matrix_full import DetailedMatrixProduct

    generator = DetailedMatrixProduct()
    task = generator.build(generator.draw(12))
    expanded = next(step.latex for step in task.steps if step.text_key == "expand")
    assert expanded.count(r"\cdot") == 12


def test_sum_expansion_shows_every_addition_or_subtraction() -> None:
    from app.engine.generators.matrix_full import DetailedMatrixSum

    generator = DetailedMatrixSum()
    params = generator.draw(12)
    task = generator.build(params)
    expanded = next(step.latex for step in task.steps if step.text_key == "expand")
    assert expanded.count("+" if params.sign == 1 else "-") >= len(params.first) ** 2
