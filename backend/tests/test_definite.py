"""Acceptance corpus for #36 definite-v1: values, bounds, rejection and equivalence."""

import json
import sys
from dataclasses import replace
from itertools import product

import pytest
import sympy as sp

from app.generators.basic import X
from app.generators.core import catalogue
from app.generators.core import replay as replay_exercise
from app.generators.definite import (
    TEMPLATES,
    base_record,
    difficulty,
    is_clean_value,
    replay_definite,
    verify_definite,
)
from app.services.answer_check import check_tree, replay_problem
from app.services.math_parser import parse_math_input
from app.services.math_worker import AnswerCheck, check_answer

COEFFICIENTS = (-3, -2, -1, 1, 2, 3)
# Template, topic, level and the value in the coefficient `A`, fixed independently of the code.
A = sp.Symbol("a")
CASES = [
    ("power", "basic-integrals", 1, 2 * A),
    ("exponential", "basic-integrals", 1, A * (sp.E - 1)),
    ("sum", "basic-integrals", 2, A / 2 + sp.E - 1),
    ("reciprocal", "basic-integrals", 3, A),
    ("fractional_power", "basic-integrals", 3, 2 * A),
    ("expand_square", "basic-integrals", 4, sp.Rational(7, 3) * A),
    ("polynomial_inner", "substitution", 3, A * (sp.E - 1)),
    ("factor_square", "substitution", 4, sp.Rational(7, 6) * A),
    ("linear_exponential", "integration-by-parts", 1, A),
    ("quadratic_exponential", "integration-by-parts", 2, A * (sp.E - 2)),
    ("cyclic_sine", "integration-by-parts", 3, A * ((sp.exp(sp.pi) + 1) / 2)),
    ("linear_denominator", "rational-functions", 1, A * (sp.log(2))),
    ("denominator_derivative", "rational-functions", 2, A * (sp.log(2))),
    ("distinct_factors", "rational-functions", 3, A * (sp.log(sp.Rational(4, 3)))),
    (
        "repeated_factor",
        "rational-functions",
        4,
        A * (sp.log(sp.Rational(4, 3)) - sp.Rational(1, 6)),
    ),
    ("division_then_fractions", "rational-functions", 5, A * (sp.log(3) + sp.Rational(1, 2))),
    ("sine", "trigonometric-integrals", 1, 2 * A),
    ("double_argument", "trigonometric-integrals", 2, A),
    ("odd_power", "trigonometric-integrals", 3, sp.Rational(4, 3) * A),
    ("even_power", "trigonometric-integrals", 4, sp.pi / 2 * A),
    ("identity_substitution", "trigonometric-integrals", 5, sp.Rational(1, 3) * A),
]


def record(name: str, coefficient: int = 1) -> dict[str, object]:
    return {"generator_version": "definite-v1", "template": name, "coefficient": coefficient}


def source(value: sp.Expr) -> str:
    """The value written in the learner input grammar."""
    return str(value).replace("**", "^").replace("E", "e")


def test_cases_cover_every_template() -> None:
    assert {case[0] for case in CASES} == set(TEMPLATES)


@pytest.mark.parametrize("case,coefficient", tuple(product(CASES, COEFFICIENTS)))
def test_complete_definite_corpus(case, coefficient) -> None:
    name, topic, level, value = case
    problem = replay_definite(record(name, coefficient))
    assert (problem.topic, problem.difficulty, difficulty(TEMPLATES[name])) == (topic, level, level)
    assert problem.template.is_definite is True
    assert sp.simplify(problem.value - value.subs(A, coefficient)) == 0
    assert is_clean_value(problem.value)
    # The closed interval stays inside the base template's real domain.
    assert sp.Interval(problem.lower, problem.upper).is_subset(problem.base_domain) is True
    assert problem.statement.startswith(r"\int_")
    assert problem.solution_steps[-1].latex == problem.answer_latex
    assert all(" + C" not in step.latex for step in problem.solution_steps[-2:])
    assert replay_definite(json.loads(json.dumps(record(name, coefficient)))) == problem
    tree = parse_math_input(source(problem.value))
    assert check_tree(tree, replay_problem(record(name, coefficient))) == "correct"


@pytest.mark.parametrize("case", CASES)
def test_values_match_an_independent_integration(case) -> None:
    name, *_rest, value = case
    problem = replay_definite(record(name))
    exact = sp.integrate(problem.integrand, (X, problem.lower, problem.upper))
    assert sp.simplify(exact - value.subs(A, 1)) == 0


def test_catalogue_cells_mix_definite_and_indefinite_records() -> None:
    for name, topic, level, _value in CASES:
        exercises = catalogue(topic, level)
        definite = [item for item in exercises if item.record["generator_version"] == "definite-v1"]
        assert {item.record["template"] for item in definite} >= {name}
        assert any(item.value is None for item in exercises)
        for item in definite:
            assert item.answer == replay_definite(item.record).answer_latex
            assert not item.answer.endswith("+ C")
            assert replay_exercise(item.record) == item
    # Indefinite records come first: the guest demo's first exercise is unchanged.
    assert catalogue("basic-integrals", 1)[0].record["generator_version"] == "basic-v1"


@pytest.mark.parametrize(
    "bad",
    [
        {**record("sine"), "extra": 1},
        {"generator_version": "definite-v1", "template": "sine"},
        {**record("sine"), "generator_version": "definite-v2"},
        {**record("sine"), "coefficient": 0},
        {**record("sine"), "coefficient": 4},
        {**record("sine"), "coefficient": True},
        {**record("sine"), "coefficient": "1"},
        {**record("sine"), "lower": 0},
        record("unknown"),
        record("expand_and_split"),
    ],
)
def test_replay_rejects_bad_records(bad) -> None:
    with pytest.raises(ValueError):
        replay_definite(bad)


def test_base_records_are_complete_basic_or_family_records() -> None:
    for name, template in TEMPLATES.items():
        base = base_record(template, 2)
        assert base["coefficient"] == 2 and base["template"] == name


@pytest.mark.parametrize(
    "name,lower,upper",
    [
        ("reciprocal", -1, 1),  # crosses the pole at 0
        ("reciprocal", 0, 1),  # touches the pole
        ("fractional_power", 0, 4),  # 1/sqrt(x) is undefined at 0
        ("distinct_factors", -2, 1),  # crosses both poles
        ("repeated_factor", -1, 2),
    ],
)
def test_bounds_never_touch_a_singularity(name, lower, upper) -> None:
    problem = replay_definite(record(name))
    with pytest.raises(RuntimeError):
        verify_definite(replace(problem, lower=sp.Integer(lower), upper=sp.Integer(upper)))


def test_rejects_unclean_wrong_reversed_and_zero_values() -> None:
    problem = replay_definite(record("sine"))
    for value in (sp.Integer(3), sp.Rational(37, 24) + 2, sp.Float(2.0), sp.sqrt(2) + 2):
        with pytest.raises(RuntimeError):
            verify_definite(replace(problem, value=value))
    with pytest.raises(RuntimeError):
        verify_definite(replace(problem, lower=sp.pi, upper=sp.Integer(0)))
    # An odd integrand on a symmetric interval would make every answer zero.
    with pytest.raises(RuntimeError):
        verify_definite(replace(problem, lower=-sp.pi, upper=sp.pi, value=sp.Integer(0)))
    assert not is_clean_value(sp.Integer(0))
    assert not is_clean_value(sp.log(sp.Rational(64, 27)) + sp.Rational(37, 24))
    assert not is_clean_value(sp.Symbol("x"))


@pytest.mark.parametrize(
    "name,answer,expected",
    [
        ("exponential", "e - 1", "correct"),
        ("exponential", "-(1 - e)", "correct"),
        ("exponential", "e^1 - e^0", "correct"),
        ("distinct_factors", "2ln(2) - ln(3)", "correct"),
        ("distinct_factors", "ln|4/3|", "correct"),
        ("distinct_factors", "-ln(3/4)", "correct"),
        ("cyclic_sine", "(e^pi + 1)/2", "correct"),
        ("even_power", "pi/2", "correct"),
        ("even_power", "1.5708", "incorrect"),  # a decimal approximation is not exact
        ("even_power", "pi/2 + C", "incorrect"),  # definite answers have no constant
        ("exponential", "e^x", "incorrect"),  # an antiderivative, not its value
        ("exponential", "1 - e", "incorrect"),  # bounds reversed
        ("distinct_factors", "ln(-4/3)", "incorrect"),  # not real
        ("sine", "sqrt(-4)", "incorrect"),
        ("sine", "2 + ln(1 - 1)", "invalid"),  # an undefined part never cancels
        ("sine", "0*ln(0) + 2", "invalid"),
        ("sine", "x - x + 2", "correct"),
    ],
)
def test_definite_equivalence(name, answer, expected) -> None:
    assert check_tree(parse_math_input(answer), replay_problem(record(name))) == expected


linux_only = pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux worker")


@linux_only
@pytest.mark.parametrize(
    "name,answer,expected",
    [
        ("cyclic_sine", "e^pi/2 + 1/2", AnswerCheck("correct")),
        ("division_then_fractions", "ln(3) + 1/2", AnswerCheck("correct")),
        ("repeated_factor", "ln(4/3) - 1/6", AnswerCheck("correct")),
        ("repeated_factor", "ln(4/3) - 1/6 + C", AnswerCheck("incorrect")),
        ("quadratic_exponential", "x^2*e^x", AnswerCheck("incorrect")),
    ],
)
def test_definite_check_fits_the_worker_limits(name, answer, expected) -> None:
    assert check_answer(answer, record(name)) == expected
