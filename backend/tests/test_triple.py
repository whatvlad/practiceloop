"""Acceptance corpus for #100 triple-v1: values, statements, rejection and checking."""

import json
import sys
import time
from dataclasses import replace
from itertools import product

import pytest
import sympy as sp

from app.generators.core import catalogue
from app.generators.core import replay as replay_exercise
from app.generators.definite import is_clean_value
from app.generators.multiple import integrate_setup
from app.generators.triple import (
    COEFFICIENTS,
    TEMPLATES,
    TOPIC,
    Z,
    _wrong_z,
    records,
    replay_triple,
    replay_value,
    verify_variant,
)
from app.services.answer_check import check_and_diagnose, check_tree, replay_problem
from app.services.math_parser import parse_math_input
from app.services.math_worker import AnswerCheck, check_answer

PI, E = sp.pi, sp.E
# (template, variant) -> (level, value, missing-r value, wrong-z value) at coefficient 1,
# fixed by hand from ADR-005 and elementary geometry (cone 8π/3, paraboloid 8π, ...).
CASES = {
    ("box_product", 0): (1, sp.Rational(1, 2), None, None),
    ("box_product", 1): (1, sp.Integer(3), None, None),
    ("box_product", 2): (1, sp.Integer(9), None, None),
    ("box_sum", 0): (2, sp.Integer(2), None, None),
    ("box_sum", 1): (2, sp.Integer(4), None, None),
    ("simplex", 0): (3, sp.Rational(2, 3), None, sp.Rational(8, 3)),
    ("simplex", 1): (3, sp.Rational(1, 6), None, sp.Rational(1, 2)),
    ("cylinder", 0): (3, 3 * PI / 2, 2 * PI, None),
    ("cylinder", 1): (3, 2 * PI, 4 * PI, None),
    ("solid_of_revolution", 0): (4, 8 * PI / 3, 4 * PI, 8 * PI),
    ("solid_of_revolution", 1): (4, 8 * PI, 32 * PI / 3, 16 * PI),
    ("tetrahedron", 0): (4, sp.Rational(2, 3), None, sp.Integer(2)),
    ("tetrahedron", 1): (4, sp.Integer(6), None, sp.Integer(18)),
    ("cylindrical_conversion", 0): (5, PI * (E - 1) / 2, None, None),
    ("cylindrical_conversion", 1): (5, PI * sp.log(2) / 2, PI**2 / 4, None),
}


def record(name: str, variant: int = 0, coefficient: int = 1) -> dict[str, object]:
    return {
        "generator_version": "triple-v1",
        "template": name,
        "variant": variant,
        "coefficient": coefficient,
    }


def source(value: sp.Expr) -> str:
    """The value written in the learner input grammar."""
    return str(value).replace("**", "^").replace("E", "e").replace("log", "ln")


def test_cases_cover_every_variant_and_every_level() -> None:
    assert set(CASES) == {
        (name, index) for name, t in TEMPLATES.items() for index in range(len(t.variants))
    }
    assert {level for level, *_ in CASES.values()} == {1, 2, 3, 4, 5}
    # ADR-005: level 3 offers a Cartesian simplex and a cylindrical cylinder; level 4
    # a cone, a paraboloid and a tetrahedron.
    systems = {
        level: {
            TEMPLATES[n].variants[i].solution.system
            for (n, i), (lv, *_) in CASES.items()
            if lv == level
        }
        for level in range(1, 6)
    }
    assert systems[3] == systems[4] == {"cartesian", "cylindrical"}
    assert systems[5] == {"cylindrical"}


@pytest.mark.parametrize("case", sorted(CASES))
def test_declared_values_are_recomputed_and_cross_checked(case) -> None:
    name, index = case
    level, value, missing_r, wrong_z = CASES[case]
    verify_variant(name, index)
    variant = TEMPLATES[name].variants[index]
    assert TEMPLATES[name].difficulty == level
    assert sp.simplify(variant.value - value) == 0
    assert sp.simplify(integrate_setup(variant.solution) - value) == 0
    if missing_r is None:
        assert variant.missing_r is None
    else:
        assert sp.simplify(variant.missing_r - missing_r) == 0
    if wrong_z is None:
        assert variant.wrong_z is None
    else:
        assert sp.simplify(integrate_setup(_wrong_z(variant)) - wrong_z) == 0
    # Every cylindrical solid has a Cartesian set-up of the same solid as a check.
    if variant.solution.system == "cylindrical":
        others = (variant.stated, *variant.checks) if variant.stated else variant.checks
        assert any(other.system == "cartesian" for other in others)


@pytest.mark.parametrize("case,coefficient", tuple(product(sorted(CASES), COEFFICIENTS)))
def test_complete_triple_corpus(case, coefficient) -> None:
    name, index = case
    level, value, missing_r, wrong_z = CASES[case]
    item = record(name, index, coefficient)
    problem = replay_triple(item)
    assert (problem.problem.topic, problem.problem.difficulty) == (TOPIC, level)
    assert sp.simplify(problem.problem.value - coefficient * value) == 0
    assert is_clean_value(problem.problem.value)
    assert problem.solution_steps[-1]["latex"] == problem.answer_latex
    assert replay_triple(json.loads(json.dumps(item))) == problem
    worker = replay_problem(item)
    assert check_tree(parse_math_input(source(problem.problem.value)), worker) == "correct"
    for code, wrong in (("missing_jacobian", missing_r), ("z_bounds", wrong_z)):
        if wrong is not None:
            tree = parse_math_input(source(coefficient * wrong))
            assert check_and_diagnose(tree, worker, item) == ("incorrect", code)
    reversed_bounds = parse_math_input(source(-coefficient * value))
    assert check_and_diagnose(reversed_bounds, worker, item) == ("incorrect", "bounds_reversed")


def test_statements_name_the_system_only_at_levels_one_to_three() -> None:
    for name, template in TEMPLATES.items():
        for index, variant in enumerate(template.variants):
            statement = replay_triple(record(name, index, 2)).statement
            named = r"\text{(" in statement
            if variant.stated is None:
                assert statement.startswith(r"\iiint_E") and "E = " in statement
                assert named == (template.difficulty <= 3)
            else:
                # An iterated dz dy dx integral is Cartesian by its own notation.
                assert statement.startswith(r"\int_") and not named
                assert statement.count(r"\int_") == 3 and r"\,dz\,dy\,dx" in statement
            if template.named == "cylindrical":
                assert r"\text{(cylindrical coordinates)}" in statement


def test_solution_steps_show_solid_jacobian_and_each_integration() -> None:
    for name, template in TEMPLATES.items():
        for index, variant in enumerate(template.variants):
            steps = replay_triple(record(name, index)).solution_steps
            text = " ".join(step["latex"] for step in steps)
            integrations = [s for s in steps if s["say"].startswith("Integrate the")]
            assert len(integrations) == 3
            assert [s["latex"].split(r"\,d")[-1][:1] for s in integrations][0] == "z"
            if variant.solution.system == "cylindrical":
                assert r"\,dz\,r\,dr\,d\theta" in text
                assert steps[1]["say"].startswith("Change to cylindrical coordinates")
            if variant.stated is None or variant.stated.bounds != variant.solution.bounds:
                assert steps[0]["say"].startswith("Describe the solid")
                assert r"\le z \le" in steps[0]["latex"]
            if variant.checks or variant.stated is not None:
                assert any(s["say"].startswith("Check the value") for s in steps)


def test_catalogue_offers_every_level() -> None:
    for level in range(1, 6):
        exercises = catalogue(TOPIC, level)
        assert len(exercises) == len(records(level)) > 0
        for item in exercises:
            assert item.topic == TOPIC and item.difficulty == level
            assert item.answer == replay_triple(item.record).answer_latex
            assert not item.answer.endswith("+ C")
            assert replay_exercise(item.record) == item


@pytest.mark.parametrize(
    "bad",
    [
        {**record("cylinder"), "extra": 1},
        {"generator_version": "triple-v1", "template": "cylinder", "coefficient": 1},
        {**record("cylinder"), "generator_version": "double-v1"},
        {**record("cylinder"), "generator_version": "triple-v2"},
        {**record("cylinder"), "coefficient": 0},
        {**record("cylinder"), "coefficient": 4},
        {**record("cylinder"), "coefficient": True},
        {**record("cylinder"), "coefficient": 1.0},
        {**record("cylinder"), "variant": "0"},
        {**record("cylinder"), "variant": -1},
        record("cylinder", 2),
        record("cylinder", 10),
        record("sphere"),
        {**record("cylinder"), "template": "x" * 33},
    ],
)
def test_replay_rejects_bad_records(bad) -> None:
    with pytest.raises(ValueError):
        replay_value(bad)
    with pytest.raises(ValueError):
        replay_triple(bad)


def _verify(template: str, variant: object) -> None:
    import app.generators.triple as triple

    patched = replace(TEMPLATES[template], variants=(variant,))
    original = triple.TEMPLATES[template]
    triple.TEMPLATES[template] = patched
    try:
        verify_variant.__wrapped__(template, 0)
    finally:
        triple.TEMPLATES[template] = original


def test_verification_rejects_wrong_unclean_and_inconsistent_variants() -> None:
    cone = TEMPLATES["solid_of_revolution"].variants[0]
    cases = [
        replace(cone, value=3 * PI),  # wrong value
        replace(cone, missing_r=PI),  # wrong missing-r value
        replace(cone, missing_r=None),  # a clean missing-r value must be declared
        replace(cone, wrong_z=((0, 2), 4 * PI)),  # wrong wrong-z value
        replace(cone, wrong_z=((0, 2), cone.value)),  # a "mistake" that is right
        replace(cone, integrand=Z),  # solution integrand differs from the statement
        replace(cone, checks=()),  # a cylindrical solid needs a Cartesian check
        replace(
            cone, checks=(replace(cone.checks[0], bounds=((Z, 0, 2), *cone.checks[0].bounds[1:])),)
        ),
    ]
    for variant in cases:
        with pytest.raises(RuntimeError):
            _verify("solid_of_revolution", variant)
    _verify("solid_of_revolution", cone)
    box = TEMPLATES["box_sum"].variants[1]
    # 37/24 at coefficient 1 is not clean.
    unclean = replace(
        box, solution=box.solution.scaled(sp.Rational(37, 96)), value=sp.Rational(37, 24)
    )
    with pytest.raises(RuntimeError):
        _verify("box_sum", unclean)


@pytest.mark.parametrize(
    "name,variant,answer,expected",
    [
        ("solid_of_revolution", 0, "8pi/3", "correct"),
        ("solid_of_revolution", 0, "(8/3)*pi", "correct"),
        ("solid_of_revolution", 0, "16pi/6", "correct"),
        ("solid_of_revolution", 0, "8.37758", "incorrect"),  # a decimal is not exact
        ("solid_of_revolution", 0, "8pi/3 + C", "incorrect"),
        ("solid_of_revolution", 0, "z", "incorrect"),
        ("solid_of_revolution", 0, "8pi/3 + ln(0)", "invalid"),
        ("cylinder", 0, "3pi/2", "correct"),
        ("cylinder", 0, "1.5*pi", "correct"),  # 1.5 is exactly 3/2
        ("box_product", 0, "1/2", "correct"),
        ("box_product", 0, "0.5", "correct"),
        ("cylindrical_conversion", 0, "pi*e/2 - pi/2", "correct"),
        ("cylindrical_conversion", 1, "pi*ln(sqrt(2))", "correct"),
        ("cylindrical_conversion", 1, "pi*ln(4)/4", "correct"),
        ("tetrahedron", 1, "6", "correct"),
    ],
)
def test_triple_equivalence(name, variant, answer, expected) -> None:
    assert check_tree(parse_math_input(answer), replay_problem(record(name, variant))) == expected


def test_ambiguous_mistakes_are_not_diagnosed() -> None:
    item = record("solid_of_revolution")
    problem = replay_value(item)
    both = replace(problem, mistakes=(("missing_jacobian", 4 * PI), ("z_bounds", 4 * PI)))
    assert check_and_diagnose(parse_math_input("4pi"), both, item) == ("incorrect", None)


def test_every_canonical_check_fits_half_the_worker_cpu_limit() -> None:
    """ADR-005 check budget: at most 1 s of CPU per canonical answer (the limit is 2 s)."""
    for (name, index), (_level, value, *_mistakes) in CASES.items():
        item = record(name, index, -3)
        tree = parse_math_input(source(-3 * value))
        start = time.process_time()
        outcome = check_and_diagnose(tree, replay_problem(item), item)
        assert outcome == ("correct", None)
        assert time.process_time() - start < 1.0, (name, index)


linux_only = pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux worker")


@linux_only
@pytest.mark.parametrize(
    "item,answer,expected",
    [
        (record("solid_of_revolution", 0, 2), "16pi/3", AnswerCheck("correct")),
        (
            record("solid_of_revolution", 0, 2),
            "8pi",
            AnswerCheck("incorrect", feedback_code="missing_jacobian"),
        ),
        (
            record("solid_of_revolution", 1, 1),
            "16pi",
            AnswerCheck("incorrect", feedback_code="z_bounds"),
        ),
        (
            record("box_sum", 0, 1),
            "-2",
            AnswerCheck("incorrect", feedback_code="bounds_reversed"),
        ),
        (record("cylindrical_conversion", 0, 1), "pi*(e - 1)/2", AnswerCheck("correct")),
        (record("tetrahedron", 0, -3), "-2", AnswerCheck("correct")),
    ],
)
def test_triple_check_fits_the_worker_limits(item, answer, expected) -> None:
    assert check_answer(answer, item) == expected
