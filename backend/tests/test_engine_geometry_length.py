"""Vector lengths from perpendicularity, angles and the parallelogram identity."""

import pytest
import sympy as sp

from app.engine.generators.eigen_geometry import VectorLengthPractice, length_seed
from app.engine.opening import rebuild
from app.math_input import parse_math_input


@pytest.mark.parametrize("level", (1, 2, 3))
def test_vector_length_is_exact_and_has_consistent_diagrams(level: int) -> None:
    generator = VectorLengthPractice()
    for variation in range(8):
        params = generator.draw(length_seed(level, variation))
        task = generator.build(params)
        theta = sp.pi * params.angle / 180
        expected = sp.sqrt(params.a**2 + params.b**2 - 2 * params.a * params.b * sp.cos(theta))
        assert sp.simplify(task.answer.expected - expected) == 0
        source = sp.sstr(expected).replace("**", "^")
        assert task.answer.check(parse_math_input(source)) == "correct"
        assert task.answer.check(parse_math_input(f"2*({source})/2")) == "correct"
        assert task.answer.check(parse_math_input(f"({source})+1")) == "incorrect"
        opened = rebuild(task.code)
        assert (opened.topic, opened.difficulty) == ("vectors", level)
        issued = opened.problem.issued()
        assert issued.statement_visual is not None
        assert all(step.get("visual") and step.get("rules") for step in issued.steps)
        assert all(line["label"] != "u-v" for line in issued.statement_visual["lines"])
        assert any(line["label"] == "u-v" for line in issued.steps[-1]["visual"]["lines"])
