"""Scalar vector expressions model the structure of algebra30 exercise 72."""

import pytest
import sympy as sp

from app.engine.generators.eigen_geometry import ScalarVectorExpression, scalar_expression_seed
from app.engine.opening import rebuild
from app.math_input import parse_math_input


@pytest.mark.parametrize("level", (1, 2, 3))
def test_scalar_expression_is_exact_reproducible_and_illustrated(level: int) -> None:
    generator = ScalarVectorExpression()
    for variation in range(8):
        params = generator.draw(scalar_expression_seed(level, variation))
        task = generator.build(params)
        u, v, w = (sp.Matrix(vector) for vector in (params.u, params.v, params.w))
        middle = sp.sqrt(w.dot(w)) - v.dot(w) if params.seed % 2 else u.dot(w - v)
        basic = u.dot(w) if params.seed % 2 else sp.sqrt(v.dot(v))
        expected = (basic, middle, u.cross(v).dot(w))[level - 1]
        assert sp.simplify(task.answer.expected - expected) == 0
        assert (
            task.answer.check(parse_math_input(sp.sstr(expected).replace("**", "^"))) == "correct"
        )
        opened = rebuild(task.code)
        assert (opened.topic, opened.difficulty) == ("vectors", level)
        issued = opened.problem.issued()
        assert issued.statement_visual is not None
        assert all(step.get("visual") and step.get("rules") for step in issued.steps)
        assert all(line["tone"] == "given" for line in issued.statement_visual["lines"])
