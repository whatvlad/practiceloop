"""The actual killable Linux worker checks each new geometry type and level."""

import sys

import pytest
import sympy as sp
from test_geometry_practice import answer_text

from app.engine.answers.computational import CategoryAnswer, FormulaAnswer, OrderedAnswer
from app.engine.answers.geometry import (
    ParametricGeometryAnswer,
    PlaneEquationAnswer,
    VectorSetAnswer,
)
from app.engine.generators.geometry_practice import MODES, GeometryPractice, geometry_seed
from app.services.math_worker import check_answer

pytestmark = pytest.mark.skipif(
    sys.platform != "linux", reason="Real worker requires Linux resource limits"
)


def wrong_answer(answer):
    if isinstance(answer, FormulaAnswer):
        return answer_text(FormulaAnswer(answer.expected + 1))
    if isinstance(answer, CategoryAnswer):
        return next(choice for choice in answer.choices if choice != answer.expected)
    if isinstance(answer, PlaneEquationAnswer):
        return answer_text(PlaneEquationAnswer(answer.normal, answer.offset + 1))
    if isinstance(answer, ParametricGeometryAnswer):
        direction = sp.Matrix(answer.directions[0])
        if len(answer.directions) == 2:
            shift = direction.cross(sp.Matrix(answer.directions[1]))
        else:
            axis = next(
                sp.eye(3)[:, i]
                for i in range(3)
                if direction.cross(sp.eye(3)[:, i]) != sp.zeros(3, 1)
            )
            shift = direction.cross(axis)
        return answer_text(
            ParametricGeometryAnswer(tuple(sp.Matrix(answer.point) + shift), answer.directions)
        )
    if isinstance(answer, VectorSetAnswer):
        row = "(" + ";".join(sp.sstr(x).replace("**", "^") for x in answer.vectors[0]) + ")"
        return "(" + row + ";" + row + ")"
    assert isinstance(answer, OrderedAnswer)
    first, *rest = answer.components
    return answer_text(OrderedAnswer((FormulaAnswer(first.expected + 1), *rest), answer.labels))


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("level", [1, 2, 3])
def test_real_worker_accepts_exact_answers_and_rejects_wrong_geometry(mode, level):
    generator = GeometryPractice(mode)
    task = generator.build(generator.draw(geometry_seed(level, 2)))
    record = {"generator_version": task.generator_version, "code": task.code}
    assert check_answer(answer_text(task.answer), record).result == "correct"
    assert check_answer(wrong_answer(task.answer), record).result == "incorrect"


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("level", [1, 2, 3])
def test_unpooled_geometry_code_rebuilds_its_full_solution_in_the_limited_worker(mode, level):
    from app.engine.opening import OpenedCode
    from app.services.math_worker import open_problem_code

    generator = GeometryPractice(mode)
    task = generator.build(generator.draw(geometry_seed(level, 7)))
    opened = OpenedCode.model_validate_json(open_problem_code(task.code))
    assert opened.problem.code == task.code
    assert opened.difficulty == level
    assert opened.problem.statement_visual
    assert all(step.visual and step.rules for step in opened.problem.steps)
