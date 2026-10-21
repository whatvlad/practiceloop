"""Acceptance corpus for #99 double-v1: values, statements, rejection and checking."""

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
from app.generators.double import (
    COEFFICIENTS,
    TEMPLATES,
    TOPIC,
    records,
    replay_double,
    replay_value,
    verify_variant,
)
from app.generators.multiple import THETA, R, Setup, Y, integrate_setup, verify_value
from app.services.answer_check import check_and_diagnose, check_tree, replay_problem
from app.services.math_parser import parse_math_input
from app.services.math_worker import AnswerCheck, check_answer

PI, E = sp.pi, sp.E
X = sp.Symbol("x", real=True)
# (template, variant) -> (level, value at coefficient 1, missing-r value), fixed by hand.
CASES = {
    ("rectangle_product", 0): (1, sp.Integer(3), None),
    ("rectangle_product", 1): (1, sp.Rational(9, 2), None),
    ("rectangle_product", 2): (1, sp.Integer(1), None),
    ("rectangle_product", 3): (1, 2 * E - 2, None),
    ("rectangle_sum", 0): (2, sp.Integer(3), None),
    ("rectangle_sum", 1): (2, sp.Rational(14, 3), None),
    ("rectangle_sum", 2): (2, E - 2, None),
    ("rectangle_sum", 3): (2, sp.Rational(5, 2), None),
    ("type_one", 0): (3, sp.Rational(1, 6), None),
    ("type_one", 1): (3, sp.Rational(1, 2), None),
    ("type_one", 2): (3, sp.Integer(2), None),
    ("type_two", 0): (3, sp.Rational(1, 3), None),
    ("type_two", 1): (3, sp.Integer(4), None),
    ("polar_disk", 0): (3, 8 * PI, 16 * PI / 3),
    ("polar_disk", 1): (3, 9 * PI, 6 * PI),
    ("polar_disk", 2): (3, 2 * PI / 3, PI),
    ("polar_annulus", 0): (3, 3 * PI, 2 * PI),
    ("polar_annulus", 1): (3, 2 * PI, 2 * PI - 2 * PI / E),
    ("polar_sector", 0): (3, sp.Rational(8, 3), sp.Integer(2)),
    ("polar_sector", 1): (3, 4 * PI, 8 * PI / 3),
    ("reverse_order", 0): (4, (E - 1) / 2, None),
    ("reverse_order", 1): (4, (E - 1) / 3, None),
    ("reverse_order", 2): (4, sp.Integer(2), None),
    ("region_choice", 0): (4, sp.Integer(2), sp.Integer(3)),
    ("region_choice", 1): (4, sp.Rational(1, 12), None),
    ("region_choice", 2): (4, 2 * PI, PI * sp.log(3)),
    ("polar_conversion", 0): (5, PI * (E - 1) / 2, None),
    ("polar_conversion", 1): (5, PI * sp.log(2) / 4, PI**2 / 8),
    ("polar_conversion", 2): (5, PI, None),
}


def record(name: str, variant: int = 0, coefficient: int = 1) -> dict[str, object]:
    return {
        "generator_version": "double-v1",
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
    # ADR-005: level 3 offers Cartesian variable bounds and polar disks, annuli and sectors.
    assert {n for (n, _), (level, *_) in CASES.items() if level == 3} == {
        "type_one",
        "type_two",
        "polar_disk",
        "polar_annulus",
        "polar_sector",
    }


@pytest.mark.parametrize("case", sorted(CASES))
def test_declared_values_are_recomputed_and_cross_checked(case) -> None:
    name, index = case
    level, value, missing_r = CASES[case]
    verify_variant(name, index)
    variant = TEMPLATES[name].variants[index]
    assert TEMPLATES[name].difficulty == level
    assert sp.simplify(variant.value - value) == 0
    assert (
        variant.missing_r is None
        if missing_r is None
        else (sp.simplify(variant.missing_r - missing_r) == 0)
    )
    assert sp.simplify(integrate_setup(variant.solution) - value) == 0


@pytest.mark.parametrize("case,coefficient", tuple(product(sorted(CASES), COEFFICIENTS)))
def test_complete_double_corpus(case, coefficient) -> None:
    name, index = case
    level, value, missing_r = CASES[case]
    item = record(name, index, coefficient)
    problem = replay_double(item)
    assert (problem.problem.topic, problem.problem.difficulty) == (TOPIC, level)
    assert sp.simplify(problem.problem.value - coefficient * value) == 0
    assert is_clean_value(problem.problem.value)
    assert problem.solution_steps[-1]["latex"] == problem.answer_latex
    assert replay_double(json.loads(json.dumps(item))) == problem
    tree = parse_math_input(source(problem.problem.value))
    worker = replay_problem(item)
    assert check_tree(tree, worker) == "correct"
    if missing_r is not None:
        wrong = parse_math_input(source(coefficient * missing_r))
        assert check_and_diagnose(wrong, worker, item) == ("incorrect", "missing_jacobian")
    reversed_bounds = parse_math_input(source(-coefficient * value))
    assert check_and_diagnose(reversed_bounds, worker, item) == ("incorrect", "bounds_reversed")


def test_statements_name_the_system_only_at_levels_one_to_three() -> None:
    for name, template in TEMPLATES.items():
        for index, variant in enumerate(template.variants):
            statement = replay_double(record(name, index)).statement
            named = r"\text{(" in statement
            if variant.stated is None:
                assert statement.startswith(r"\iint_D") and "D = " in statement
                assert named == (template.difficulty <= 3)
            else:
                # An iterated dy dx integral is Cartesian by its own notation.
                assert statement.startswith(r"\int_") and not named
                assert statement.count(r"\int_") == 2 and r"\,d" in statement
            if template.named == "polar":
                assert r"\text{(polar coordinates)}" in statement


def test_solution_steps_show_region_jacobian_and_each_integration() -> None:
    for name, template in TEMPLATES.items():
        for index, variant in enumerate(template.variants):
            steps = replay_double(record(name, index)).solution_steps
            text = " ".join(step["latex"] for step in steps)
            integrations = [s for s in steps if s["say"].startswith("Integrate the")]
            assert len(integrations) == 2
            if variant.solution.system == "polar":
                assert r"\,r\,dr\,d\theta" in text
                assert r"\le r \le" in steps[0]["latex"] and r"\theta" in steps[0]["latex"]
            if variant.stated is None or variant.stated.bounds != variant.solution.bounds:
                assert steps[0]["say"].startswith("Describe the region")
            if variant.checks or (
                variant.stated is not None and variant.stated.bounds != variant.solution.bounds
            ):
                assert any(s["say"].startswith("Check the value") for s in steps)


def test_catalogue_offers_every_level() -> None:
    for level in range(1, 6):
        exercises = catalogue(TOPIC, level)
        assert len(exercises) == len(records(level)) > 0
        for item in exercises:
            assert item.topic == TOPIC and item.difficulty == level
            assert item.answer == replay_double(item.record).answer_latex
            assert not item.answer.endswith("+ C")
            assert replay_exercise(item.record) == item


@pytest.mark.parametrize(
    "bad",
    [
        {**record("polar_disk"), "extra": 1},
        {"generator_version": "double-v1", "template": "polar_disk", "coefficient": 1},
        {**record("polar_disk"), "generator_version": "triple-v1"},
        {**record("polar_disk"), "generator_version": "double-v2"},
        {**record("polar_disk"), "coefficient": 0},
        {**record("polar_disk"), "coefficient": 4},
        {**record("polar_disk"), "coefficient": True},
        {**record("polar_disk"), "variant": "0"},
        {**record("polar_disk"), "variant": -1},
        record("polar_disk", 3),
        record("polar_disk", 10),
        record("unknown"),
        {**record("polar_disk"), "template": "x" * 33},
    ],
)
def test_replay_rejects_bad_records(bad) -> None:
    with pytest.raises(ValueError):
        replay_value(bad)
    with pytest.raises(ValueError):
        replay_double(bad)


def test_verification_rejects_wrong_unclean_and_inconsistent_values() -> None:
    disk = TEMPLATES["polar_disk"].variants[0]
    for value in (9 * PI, sp.Rational(37, 24), sp.Float(25.13), sp.Integer(0)):
        with pytest.raises(RuntimeError):
            verify_value(value, disk.solution, ())
    # A Cartesian set-up of a different region disagrees with the polar value.
    other = Setup("cartesian", X**2 + Y**2, ((Y, 0, 1), (X, 0, 1)))
    with pytest.raises(RuntimeError):
        verify_value(disk.value, disk.solution, (other,))
    # The Jacobian is part of the set-up: without r the disk value is wrong.
    no_jacobian = Setup("cartesian", R**2, ((R, 0, 2), (THETA, 0, 2 * PI)))
    with pytest.raises(RuntimeError):
        verify_value(disk.value, no_jacobian, ())


def test_a_mistake_equal_to_the_value_or_to_another_code_is_not_diagnosed() -> None:
    item = record("polar_disk")
    problem = replay_value(item)
    same = replace(problem, mistakes=(("missing_jacobian", problem.value),))
    tree = parse_math_input("8pi")
    assert check_and_diagnose(tree, same, item) == ("correct", None)
    ambiguous = replace(problem, mistakes=(("missing_jacobian", -problem.value),))
    assert check_and_diagnose(parse_math_input("-8pi"), ambiguous, item) == ("incorrect", None)


@pytest.mark.parametrize(
    "name,variant,answer,expected",
    [
        ("polar_disk", 0, "8pi", "correct"),
        ("polar_disk", 0, "8*pi", "correct"),
        ("polar_disk", 0, "16pi/2", "correct"),
        ("polar_disk", 0, "25.1327", "incorrect"),  # a decimal is not exact
        ("polar_disk", 0, "8pi + C", "incorrect"),
        ("polar_disk", 0, "x", "incorrect"),
        ("polar_disk", 0, "8pi + ln(0)", "invalid"),
        ("reverse_order", 0, "e/2 - 1/2", "correct"),
        ("reverse_order", 0, "(e^1 - 1)/2", "correct"),
        ("polar_conversion", 1, "ln(2)*pi/4", "correct"),
        ("polar_conversion", 1, "pi*ln(sqrt(2))/2", "correct"),
        ("polar_conversion", 1, "pi*ln(4)/8", "correct"),
        ("polar_annulus", 1, "2pi", "correct"),
        ("rectangle_sum", 2, "e - 2", "correct"),
    ],
)
def test_double_equivalence(name, variant, answer, expected) -> None:
    assert check_tree(parse_math_input(answer), replay_problem(record(name, variant))) == expected


def test_every_canonical_check_fits_half_the_worker_cpu_limit() -> None:
    """ADR-005 check budget: at most 1 s of CPU per canonical answer (the limit is 2 s)."""
    for (name, index), (_level, value, _missing) in CASES.items():
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
        (record("polar_disk", 0, 2), "16pi", AnswerCheck("correct")),
        (
            record("polar_disk", 0, 2),
            "32pi/3",
            AnswerCheck("incorrect", feedback_code="missing_jacobian"),
        ),
        (
            record("type_one", 0, 1),
            "-1/6",
            AnswerCheck("incorrect", feedback_code="bounds_reversed"),
        ),
        (record("polar_conversion", 0, 1), "pi*(e - 1)/2", AnswerCheck("correct")),
        (record("region_choice", 2, -2), "-4pi", AnswerCheck("correct")),
    ],
)
def test_double_check_fits_the_worker_limits(item, answer, expected) -> None:
    assert check_answer(answer, item) == expected
