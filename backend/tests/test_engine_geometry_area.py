"""Areas from independent cross-product magnitudes, at three levels."""

import pytest
import sympy as sp

from app.engine.generators.eigen_geometry import AreaPractice, area_seed
from app.engine.opening import rebuild
from app.math_input import parse_math_input


@pytest.mark.parametrize("mode", ("triangle-area", "parallelogram-area"))
@pytest.mark.parametrize("level", (1, 2, 3))
def test_area_modes_have_exact_answers_steps_and_drawings(mode: str, level: int) -> None:
    generator = AreaPractice()
    for variation in range(8):
        params = generator.draw(area_seed(level, mode, variation))
        task = generator.build(params)
        a, b, c = (sp.Matrix(point) for point in params.points)
        u, v = (
            (a - b, c - b)
            if level == 1
            else (b - a, (b + c) / 2 - a)
            if level == 3
            else (b - a, c - a)
        )
        norm = sp.sqrt(sum(x * x for x in u.cross(v)))
        expected = norm / 2 if mode == "triangle-area" else norm
        assert sp.simplify(task.answer.expected - expected) == 0
        assert (
            task.answer.check(parse_math_input(sp.sstr(expected).replace("**", "^"))) == "correct"
        )
        assert (
            task.answer.check(parse_math_input(sp.sstr(expected + 1).replace("**", "^")))
            == "incorrect"
        )
        opened = rebuild(task.code)
        assert (opened.topic, opened.difficulty) == ("vectors", level)
        issued = opened.problem.issued()
        assert issued.statement_visual is not None
        assert not issued.statement_visual["faces"]
        assert all(step.get("visual") and step.get("rules") for step in issued.steps)
        assert issued.steps[-1]["visual"]["faces"]
        if level == 3:
            assert "M" not in {point["label"] for point in issued.statement_visual["points"]}
            assert "M" in {point["label"] for point in issued.steps[0]["visual"]["points"]}
