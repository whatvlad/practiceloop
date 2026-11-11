"""Source-style angles: degrees, three structures, and reproducible diagrams."""

import pytest
import sympy as sp

from app.engine.generators.eigen_geometry import AngleParameters, TriangleAngleDegrees, angle_seed
from app.engine.opening import rebuild
from app.math_input import parse_math_input


@pytest.mark.parametrize("level", (1, 2, 3))
def test_angle_levels_replay_and_measure_the_angle_in_degrees(level: int) -> None:
    generator = TriangleAngleDegrees()
    for variation in range(8):
        params = generator.draw(angle_seed(level, variation))
        task = generator.build(params)
        a, b, c = (sp.Matrix(point) for point in params.points)
        u, v = (b - a, (b + c) / 2 - a) if level == 3 else (a - b, c - b)
        cosine = u.dot(v) / (sp.sqrt(u.dot(u)) * sp.sqrt(v.dot(v)))
        assert sp.simplify(sp.cos(sp.pi * task.answer.expected / 180) - cosine) == 0
        assert task.answer.expected in (45, 60, 90, 120, 135)
        assert task.answer.check(parse_math_input(str(task.answer.expected))) == "correct"
        assert task.answer.check(parse_math_input(str(task.answer.expected + 1))) == "incorrect"
        opened = rebuild(task.code)
        assert (opened.topic, opened.difficulty) == ("vectors", level)
        issued = opened.problem.issued()
        assert issued.statement_visual is not None
        assert len(issued.steps) == len(task.steps)
        assert all(step.get("visual") and step.get("rules") for step in issued.steps)
        if level == 3:
            assert "M" not in {point["label"] for point in issued.statement_visual["points"]}
            assert "M" in {point["label"] for point in issued.steps[0]["visual"]["points"]}


def test_angle_difficulty_adds_geometric_constructions() -> None:
    generator = TriangleAngleDegrees()
    tasks = [generator.build(generator.draw(angle_seed(level, 0))) for level in (1, 2, 3)]
    assert [len(task.steps) for task in tasks] == [3, 4, 5]
    assert "vectors" in tasks[0].statement
    assert "triangle" in tasks[1].statement
    assert "midpoint" in tasks[2].statement


def test_source_triangle_requests_the_angle_not_only_its_cosine() -> None:
    params = AngleParameters(
        seed=angle_seed(2, 0),
        level=2,
        points=((-1, -2, 4), (-4, -2, 0), (3, -2, 1)),
    )
    task = TriangleAngleDegrees().build(params)
    assert task.answer.check(parse_math_input("45")) == "correct"
    assert task.answer.check(parse_math_input("sqrt(2)/2")) == "incorrect"
