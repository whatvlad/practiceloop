"""Ordered vector results and source-style operations at three levels."""

import pytest
import sympy as sp

from app.engine.generators.eigen_geometry import VectorExpression, vector_expression_seed
from app.engine.opening import rebuild
from app.math_input import MathInputError, parse_answer_input


@pytest.mark.parametrize("level", (1, 2, 3))
def test_vector_expression_checks_every_component_and_replays(level: int) -> None:
    generator = VectorExpression()
    for variation in range(8):
        params = generator.draw(vector_expression_seed(level, variation))
        task = generator.build(params)
        u, v, w = (sp.Matrix(vector) for vector in (params.u, params.v, params.w))
        middle = u.norm() * v - w if params.seed % 2 else u.cross(w) - v
        expected = (u - v, middle, (2 * u - v).cross(w))[level - 1]
        answer = task.answer
        contract = generator.input_contract(params)
        source = "(" + ";".join(sp.sstr(value).replace("**", "^") for value in expected) + ")"
        tree = parse_answer_input(source, answer.kind, contract=contract)
        assert answer.check(tree) == "correct"
        alternative = (
            "("
            + ";".join(f"({sp.sstr(2 * value).replace('**', '^')})/2" for value in expected)
            + ")"
        )
        assert (
            answer.check(parse_answer_input(alternative, answer.kind, contract=contract))
            == "correct"
        )
        incorrect = (
            "("
            + ";".join(
                sp.sstr(value + int(i == 1)).replace("**", "^") for i, value in enumerate(expected)
            )
            + ")"
        )
        assert (
            answer.check(parse_answer_input(incorrect, answer.kind, contract=contract))
            == "incorrect"
        )
        with pytest.raises(MathInputError):
            parse_answer_input("(1;2)", answer.kind, contract=contract)
        opened = rebuild(task.code)
        assert (opened.topic, opened.difficulty) == ("vectors", level)
        issued = opened.problem.issued()
        assert issued.statement_visual is not None
        assert all(step.get("visual") and step.get("rules") for step in issued.steps)
        assert all(line["tone"] == "given" for line in issued.statement_visual["lines"])


def test_vector_expression_levels_use_progressively_composite_operations() -> None:
    generator = VectorExpression()
    tasks = [
        generator.build(generator.draw(vector_expression_seed(level, 0))) for level in (1, 2, 3)
    ]
    assert [len(task.steps) for task in tasks] == [1, 2, 2]
    assert "\\times" not in tasks[0].statement
    assert "\\times" in tasks[1].statement
    assert "2u-v" in tasks[2].statement
