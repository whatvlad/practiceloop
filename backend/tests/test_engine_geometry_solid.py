"""Volumes, heights and surface areas independently checked for every level."""

import pytest
import sympy as sp

from app.engine.generators.eigen_geometry import SolidPractice, solid_seed
from app.engine.opening import rebuild
from app.math_input import parse_math_input


@pytest.mark.parametrize(
    "mode", ("tetrahedron-volume", "tetrahedron-height", "parallelepiped-area")
)
@pytest.mark.parametrize("level", (1, 2, 3))
def test_solid_modes_are_reproducible_exact_and_explained(mode: str, level: int) -> None:
    generator = SolidPractice()
    for variation in range(8):
        params = generator.draw(solid_seed(level, mode, variation))
        task = generator.build(params)
        a, b, c, d = (sp.Matrix(point) for point in params.points)
        target = (c + d) / 2 if level == 3 else d
        u, v, w = b - a, c - a, target - a

        def norm(vector):
            return sp.sqrt(sum(value * value for value in vector))

        triple = sp.det(sp.Matrix.hstack(u, v, w))
        if mode == "tetrahedron-volume":
            expected = abs(triple) / 6
        elif mode == "tetrahedron-height":
            expected = abs(triple) / norm(u.cross(v))
        else:
            expected = 2 * (norm(u.cross(v)) + norm(u.cross(w)) + norm(v.cross(w)))
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
        if level == 3:
            assert "N" not in {p["label"] for p in issued.statement_visual["points"]}
            assert "N" in {p["label"] for p in issued.steps[0]["visual"]["points"]}
            if mode == "parallelepiped-area":
                assert "CD" in {line["label"] for line in issued.statement_visual["lines"]}
        if mode == "tetrahedron-height":
            last = issued.steps[-1]["visual"]
            labels = {p["label"]: sp.Matrix(p["at"]) for p in last["points"]}
            assert "H" in labels
            altitude = labels["N" if level == 3 else "D"] - labels["H"]
            assert (
                abs(float(altitude.dot(sp.Matrix(params.points[1]) - sp.Matrix(params.points[0]))))
                < 1e-6
            )
            assert (
                abs(float(altitude.dot(sp.Matrix(params.points[2]) - sp.Matrix(params.points[0]))))
                < 1e-6
            )
