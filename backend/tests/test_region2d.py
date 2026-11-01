"""#113: every double-v1 record has a region2d visual that matches its solution set-up."""

import json
import math
from typing import Any

import pytest
import sympy as sp
from engine_fixtures import multiple_record, native_data, native_params

from app.engine.blocks.multiple import double
from app.visuals.expression import evaluate
from app.visuals.region2d import parameter_points, to_xy
from app.visuals.spec import build_visual

ALL = [
    multiple_record(2, n, i, c)
    for n, t in double.TEMPLATES.items()
    for i in range(len(t.variants))
    for c in (-3, -2, -1, 1, 2, 3)
]


def solution_setup(record):
    return native_data(record).setup


# One coefficient per variant is enough for the slower numerical checks.
UNSCALED = [record for record in ALL if native_params(record).form.coefficient == 1]


def _spec(record: dict[str, object]) -> dict[str, Any]:
    spec = build_visual(record)
    assert spec is not None
    return spec


def _name(record: dict[str, object]) -> str:
    form = native_params(record).form
    return f"{form.template}-{form.variant}-{form.coefficient}"


@pytest.mark.parametrize("record", ALL, ids=_name)
def test_every_record_builds_a_small_valid_spec(record: dict[str, object]) -> None:
    spec = _spec(record)
    setup = solution_setup(record)
    assert spec["kind"] == "region2d" and spec["version"] == 1
    assert spec["system"] == setup.system
    assert [bound[0] for bound in spec["bounds"]] == [str(b[0]) for b in setup.bounds]
    assert len(json.dumps(spec)) <= 8 * 1024
    for axis in ("x", "y", "z"):
        low, high = spec["window"][axis]
        assert math.isfinite(low) and math.isfinite(high) and low < high


@pytest.mark.parametrize("record", UNSCALED, ids=_name)
def test_trees_round_trip_against_sympy(record: dict[str, object]) -> None:
    spec = _spec(record)
    setup = solution_setup(record)
    (inner, low, high), (outer, a, b) = setup.bounds
    low, high = sp.sympify(low), sp.sympify(high)
    for u in (0.13, 0.5, 0.87):
        u_value = float(a) + (float(b) - float(a)) * u
        env = {str(outer): u_value}
        assert evaluate(spec["bounds"][0][1], env) == pytest.approx(float(low.subs(outer, u_value)))
        assert evaluate(spec["bounds"][0][2], env) == pytest.approx(
            float(high.subs(outer, u_value))
        )
        v_value = float((low + (high - low) / 3).subs(outer, u_value))
        env[str(inner)] = v_value
        expected = float(setup.integrand.subs({inner: v_value, outer: u_value}))
        assert evaluate(spec["f"], env) == pytest.approx(expected, rel=1e-9)
    assert evaluate(spec["bounds"][1][1], {}) == pytest.approx(float(a))
    assert evaluate(spec["bounds"][1][2], {}) == pytest.approx(float(b))


@pytest.mark.parametrize("record", UNSCALED, ids=_name)
def test_the_window_contains_the_region(record: dict[str, object]) -> None:
    spec = _spec(record)
    setup = solution_setup(record)
    (x0, x1), (y0, y1) = spec["window"]["x"], spec["window"]["y"]
    for v, u in parameter_points(setup, samples=9):
        x, y = to_xy(setup, v, u)
        assert x0 < x < x1 and y0 < y < y1


def test_the_spec_follows_the_coefficient() -> None:
    up = _spec(multiple_record(2, "polar_sector", 0, 2))
    down = _spec(multiple_record(2, "polar_sector", 0, -2))
    env = {"r": 1.0, "theta": 0.3}
    assert evaluate(up["f"], env) == pytest.approx(-evaluate(down["f"], env))
    assert down["window"]["z"][0] < 0 <= down["window"]["z"][1]


def test_every_template_is_covered() -> None:
    assert {native_params(record).form.template for record in ALL} == set(double.TEMPLATES)
    assert {spec["system"] for spec in map(_spec, UNSCALED)} == {"cartesian", "polar"}
    assert sp.Symbol("x", real=True) in {b[0] for r in UNSCALED for b in solution_setup(r).bounds}
