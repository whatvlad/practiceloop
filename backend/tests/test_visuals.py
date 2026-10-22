"""ADR-006 visual specs (#112): every catalogue record decides, and specs mean their source."""

import json
import math

import pytest
import sympy as sp

from app.api.practice import TOPICS
from app.generators.basic import X
from app.generators.core import catalogue
from app.generators.definite import replay_definite, value_latex
from app.visuals.expression import HEADS, UnsupportedExpression, evaluate, to_tree
from app.visuals.spec import BUILDERS, MAX_BYTES, NO_VISUAL, build_visual, solution_payload

SINGLE = ("basic-integrals", "substitution", "integration-by-parts")
SINGLE += ("rational-functions", "trigonometric-integrals")
POINT_KINDS = {"zero", "extremum", "inflection", "pole"}


def single_records() -> list[dict[str, object]]:
    return [
        exercise.record
        for topic in SINGLE
        for level in TOPICS[topic].levels
        for exercise in catalogue(topic, level)
    ]


def heads(tree: object) -> set[str]:
    if isinstance(tree, list):
        return {tree[0]}.union(*(heads(arg) for arg in tree[1:]))
    return set()


def assert_means(tree: object, expr: object, xs: list[float]) -> None:
    """The tree and its SymPy source agree wherever the source is real and finite."""
    compared = 0
    for x in xs:
        exact = complex(sp.N(sp.sympify(expr).subs(X, x)))
        got = evaluate(tree, {"x": x})  # type: ignore[arg-type]
        if abs(exact.imag) > 1e-12 or not math.isfinite(exact.real):
            assert math.isnan(got)
            continue
        assert got == pytest.approx(exact.real, rel=1e-9, abs=1e-9)
        compared += 1
    assert compared


def test_every_catalogue_version_declares_a_visual_or_none() -> None:
    versions = {
        str(exercise.record["generator_version"])
        for topic, cell in TOPICS.items()
        for level in cell.levels
        for exercise in catalogue(topic, level)
    }
    assert not set(BUILDERS) & NO_VISUAL
    assert versions <= set(BUILDERS) | NO_VISUAL


def test_every_single_integral_record_builds_a_valid_spec() -> None:
    for record in single_records():
        spec = build_visual(record)
        assert spec is not None, record
        assert spec["version"] == 1
        assert len(json.dumps(spec, separators=(",", ":"))) <= MAX_BYTES
        trees = [spec["f"]] + ([spec["F"]] if "F" in spec else [])
        assert all(heads(tree) <= HEADS for tree in trees)
        if record["generator_version"] == "definite-v1":
            assert_definite(record, spec)
        else:
            assert_indefinite(spec)


def assert_definite(record: dict[str, object], spec: dict[str, object]) -> None:
    problem = replay_definite(record)
    assert spec["kind"] == "definite"
    assert set(spec) == {"kind", "version", "f", "a", "b", "aLatex", "bLatex"} | {
        "range",
        "y",
        "value",
    }
    lo, hi = spec["range"]  # type: ignore[misc]
    a, b = spec["a"], spec["b"]
    assert lo < a < b < hi  # type: ignore[operator]
    assert a == pytest.approx(float(problem.lower)) and b == pytest.approx(float(problem.upper))
    assert spec["value"] == value_latex(problem.value)
    # The sliders may go anywhere in `range`: the integrand is continuous there.
    xs = [lo + (hi - lo) * i / 400 for i in range(401)]
    assert all(math.isfinite(evaluate(spec["f"], {"x": x})) for x in xs)  # type: ignore[arg-type]
    interval = sp.Interval(lo, hi)
    domain = sp.calculus.util.continuous_domain(problem.integrand, X, sp.S.Reals)
    assert interval.is_subset(domain)
    assert_means(spec["f"], problem.integrand, xs[::50])


def assert_indefinite(spec: dict[str, object]) -> None:
    assert spec["kind"] == "indefinite"
    assert set(spec) == {"kind", "version", "f", "F", "x", "y", "points"}
    lo, hi = spec["x"]  # type: ignore[misc]
    bottom, top = spec["y"]  # type: ignore[misc]
    assert lo < hi and bottom < 0 < top
    for point in spec["points"]:  # type: ignore[attr-defined]
        assert point["kind"] in POINT_KINDS and lo <= point["x"] <= hi
        value = evaluate(spec["f"], {"x": point["x"]})  # type: ignore[arg-type]
        if point["kind"] in ("zero", "extremum"):
            assert value == pytest.approx(0, abs=1e-7)
        if point["kind"] == "pole":
            near = evaluate(spec["f"], {"x": point["x"] + 1e-6})  # type: ignore[arg-type]
            assert math.isnan(value) and (math.isnan(near) or abs(near) > 500)


def test_trees_round_trip_against_sympy() -> None:
    for exercise in catalogue("rational-functions", 2) + catalogue("trigonometric-integrals", 3):
        spec = build_visual(exercise.record)
        assert spec is not None
        xs = [-3.7, -1.3, -0.4, 0.6, 1.9, 2.8]
        assert_means(spec["f"], exercise.integrand, xs)
        if "F" in spec:
            assert_means(spec["F"], exercise.primitive, xs)


def test_indefinite_marks_zeros_extrema_inflections_and_poles() -> None:
    record = {
        "generator_version": "basic-v1",
        "template": "expand_and_split",
        "coefficient": 1,
        "secondary": 1,
        "power": 2,
    }
    spec = build_visual(record)
    assert spec is not None
    # f = (x + 1)^2 + (x + 1)/x: zero and sign change at -1, pole at 0.
    marked = {(round(p["x"], 6), p["kind"]) for p in spec["points"]}
    assert {(-1.0, "zero"), (-1.0, "extremum"), (0.0, "pole")} <= marked
    assert any(kind == "inflection" for _, kind in marked)


def test_derivatives_have_no_visual() -> None:
    for topic in ("derivatives", "partial-derivatives"):
        record = catalogue(topic, TOPICS[topic].levels[0])[0].record
        assert build_visual(record) is None
        assert solution_payload([{"say": "s", "latex": "l"}], record) == {
            "steps": [{"say": "s", "latex": "l"}]
        }


def test_unknown_versions_are_an_error_not_a_silent_omission() -> None:
    with pytest.raises(ValueError, match="no visual decision"):
        build_visual({"generator_version": "future-v9"})


def test_expression_trees_use_only_the_listed_heads() -> None:
    x = X
    assert to_tree(sp.sqrt(x) * sp.pi + sp.E) in (
        ["add", "e", ["mul", "pi", ["sqrt", "x"]]],
        ["add", ["mul", "pi", ["sqrt", "x"]], "e"],
    )
    assert to_tree(sp.exp(x) * sp.Abs(x)) in (
        ["mul", ["exp", "x"], ["abs", "x"]],
        ["mul", ["abs", "x"], ["exp", "x"]],
    )
    assert to_tree(sp.Rational(1, 4)) == 0.25
    for unsupported in (sp.atan(x), sp.Symbol("u"), sp.I * x, sp.oo):
        with pytest.raises(UnsupportedExpression):
            to_tree(unsupported)


def test_python_evaluator_leaves_gaps_and_rejects_unknown_heads() -> None:
    for tree in (["log", -1], ["sqrt", -1], ["pow", 0, -1], ["exp", 1000]):
        assert math.isnan(evaluate(tree, {}))
    assert evaluate(["add", "pi", ["mul", 2, "x"]], {"x": 1.5}) == pytest.approx(math.pi + 3)
    for bad in (["eval", 1], ["pow", 1], ["sin", 1, 2], True, "u"):
        with pytest.raises(TypeError):
            evaluate(bad, {})  # type: ignore[arg-type]
