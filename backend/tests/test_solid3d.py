"""#114: every triple-v1 record has a solid3d visual that matches its solution set-up."""

import json
import math
from typing import Any

import pytest
import sympy as sp

from app.generators import triple
from app.generators.triple import records, solution_setup
from app.visuals.expression import evaluate
from app.visuals.solid3d import solid_points
from app.visuals.spec import build_visual

ALL = [record for level in range(1, 6) for record in records(level)]
# One coefficient per variant is enough for the slower numerical checks.
UNSCALED = [record for record in ALL if record["coefficient"] == 1]


def solid3d(record: dict[str, object]) -> dict[str, Any]:
    spec = build_visual(record)
    assert spec is not None
    return spec


def _name(record: dict[str, object]) -> str:
    return f"{record['template']}-{record['variant']}-{record['coefficient']}"


@pytest.mark.parametrize("record", ALL, ids=_name)
def test_every_record_builds_a_small_valid_spec(record: dict[str, object]) -> None:
    spec = solid3d(record)
    setup = solution_setup(record)
    assert spec["kind"] == "solid3d" and spec["version"] == 1
    assert spec["system"] == setup.system
    assert [bound[0] for bound in spec["bounds"]] == [str(b[0]) for b in setup.bounds]
    assert spec["bounds"][0][0] == "z"
    assert len(json.dumps(spec)) <= 8 * 1024
    for axis in ("x", "y", "z"):
        low, high = spec["window"][axis]
        assert math.isfinite(low) and math.isfinite(high) and low < high


@pytest.mark.parametrize("record", ALL, ids=_name)
def test_the_integrand_is_not_in_the_spec(record: dict[str, object]) -> None:
    assert set(solid3d(record)) == {"kind", "version", "system", "bounds", "window", "solid"}


@pytest.mark.parametrize("record", UNSCALED, ids=_name)
def test_trees_round_trip_against_sympy(record: dict[str, object]) -> None:
    spec = solid3d(record)
    setup = solution_setup(record)
    (z, z_low, z_high), (middle, low, high), (outer, a, b) = (
        tuple(sp.sympify(part) for part in bound) for bound in setup.bounds
    )
    assert evaluate(spec["bounds"][2][1], {}) == pytest.approx(float(a))
    assert evaluate(spec["bounds"][2][2], {}) == pytest.approx(float(b))
    for u in (0.13, 0.5, 0.87):
        u_value = float(a + (b - a) * u)
        env = {str(outer): u_value}
        v_low, v_high = float(low.subs(outer, u_value)), float(high.subs(outer, u_value))
        assert evaluate(spec["bounds"][1][1], env) == pytest.approx(v_low)
        assert evaluate(spec["bounds"][1][2], env) == pytest.approx(v_high)
        env[str(middle)] = v_value = v_low + (v_high - v_low) / 3
        point = {middle: v_value, outer: u_value}
        assert evaluate(spec["bounds"][0][1], env) == pytest.approx(float(z_low.subs(point)))
        assert evaluate(spec["bounds"][0][2], env) == pytest.approx(float(z_high.subs(point)))


@pytest.mark.parametrize("record", UNSCALED, ids=_name)
def test_the_window_contains_the_solid(record: dict[str, object]) -> None:
    spec = solid3d(record)
    for point in solid_points(solution_setup(record), samples=9):
        for value, axis in zip(point, "xyz", strict=True):
            low, high = spec["window"][axis]
            assert low < value < high


def test_the_spec_ignores_the_coefficient() -> None:
    base = {"generator_version": "triple-v1", "template": "cylinder", "variant": 0}
    assert solid3d({**base, "coefficient": 2}) == solid3d({**base, "coefficient": -3})


def test_every_template_is_covered() -> None:
    assert {record["template"] for record in ALL} == set(triple.TEMPLATES)
    assert {spec["system"] for spec in map(solid3d, UNSCALED)} == {"cartesian", "cylindrical"}
