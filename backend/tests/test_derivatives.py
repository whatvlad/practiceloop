"""#97 acceptance corpus for derivatives-v1 (ADR-005): every record, its check and
its declared mistakes, independently of the generator's own verifier."""

import json
import random
from dataclasses import replace
from itertools import product

import pytest
import sympy as sp
from sympy.calculus.util import continuous_domain
from test_definite import linux_only

from app.generators.basic import X
from app.generators.core import catalogue
from app.generators.core import replay as replay_exercise
from app.generators.derivatives import (
    COEFFICIENTS,
    TEMPLATES,
    DerivativeStep,
    generate_derivative,
    records,
    replay_derivative,
    verify_derivative,
)
from app.services.answer_check import check_and_diagnose, replay_problem
from app.services.math_parser import parse_math_input
from app.services.math_worker import AnswerCheck, check_answer

_POSITIVE = sp.Interval.open(0, sp.oo)
_REALS = sp.S.Reals

# Template, level, domain, function and its derivative at coefficient = 1.
CASES = [
    ("power", 1, _REALS, X**4, 4 * X**3),
    ("exponential", 1, _REALS, sp.exp(X), sp.exp(X)),
    ("sine", 1, _REALS, sp.sin(X), sp.cos(X)),
    ("cosine", 1, _REALS, sp.cos(X), -sp.sin(X)),
    ("logarithm", 1, _POSITIVE, sp.log(X), 1 / X),
    ("root_and_reciprocal", 2, _POSITIVE, 2 * sp.sqrt(X) - 3 / X, 1 / sp.sqrt(X) + 3 / X**2),
    ("linear_sine", 2, _REALS, sp.sin(3 * X), 3 * sp.cos(3 * X)),
    ("linear_exponential", 2, _REALS, sp.exp(2 * X), 2 * sp.exp(2 * X)),
    ("chain_exponential", 3, _REALS, sp.exp(X**2), 2 * X * sp.exp(X**2)),
    ("chain_power", 3, _REALS, (X**2 + 1) ** 3, 6 * X * (X**2 + 1) ** 2),
    ("product", 3, _REALS, X * sp.sin(X), sp.sin(X) + X * sp.cos(X)),
    ("quotient", 3, _REALS - {-1}, X / (X + 1), 1 / (X + 1) ** 2),
    ("log_product", 4, _POSITIVE, sp.log(X**2 * (X + 1)), 2 / X + 1 / (X + 1)),
    ("log_quotient", 4, _POSITIVE, sp.log(X**2 / (X + 1)), 2 / X - 1 / (X + 1)),
    ("root_chain", 4, _REALS, sp.sqrt(X**2 + 1), X / sp.sqrt(X**2 + 1)),
    ("expand_quotient", 4, _REALS - {0}, (X + 1) ** 2 / X, 1 - 1 / X**2),
    ("product_chain", 5, _REALS, X**2 * sp.exp(3 * X), (3 * X**2 + 2 * X) * sp.exp(3 * X)),
    (
        "quotient_chain",
        5,
        _REALS - {0},
        sp.sin(X**2) / X,
        (2 * X**2 * sp.cos(X**2) - sp.sin(X**2)) / X**2,
    ),
    (
        "product_chain_trig",
        5,
        _REALS,
        X * sp.cos(2 * X),
        sp.cos(2 * X) - 2 * X * sp.sin(2 * X),
    ),
]


def record(name: str, coefficient: int = 1) -> dict[str, object]:
    return dict(generator_version="derivatives-v1", template=name, coefficient=coefficient)


def learner(expression: sp.Expr) -> str:
    """An expression written in the ADR-003 input grammar."""
    return str(expression).replace("**", "^").replace("E", "e").replace("exp(", "e^(")


def outcome(stored: dict[str, object], answer: str) -> tuple[str, str | None]:
    return check_and_diagnose(parse_math_input(answer), replay_problem(stored), stored)


@pytest.mark.parametrize("case,coefficient", tuple(product(CASES, COEFFICIENTS)))
def test_complete_derivative_corpus(case, coefficient):
    name, level, domain, function, derivative = case
    stored = record(name, coefficient)
    problem = replay_derivative(stored)
    assert problem.difficulty == level
    assert problem.domain == domain
    assert sp.simplify(problem.function - coefficient * function) == 0
    assert sp.simplify(problem.derivative - coefficient * derivative) == 0
    # Independent of the generator: SymPy's derivative of the stated function.
    assert sp.simplify(sp.diff(problem.function, X) - problem.derivative) == 0
    assert domain.is_subset(continuous_domain(problem.function, X, sp.S.Reals))
    assert domain.is_subset(continuous_domain(problem.derivative, X, sp.S.Reals))
    assert problem.derivative.free_symbols == {X}
    assert not problem.derivative.has(sp.Derivative, sp.Subs)
    # All primitive values (not expression strings) survive actual JSON round trips.
    stored_json = json.loads(json.dumps(problem.parameters.model_dump(mode="json")))
    assert stored_json == stored
    assert replay_derivative(stored_json) == problem
    final = DerivativeStep("derivative_result", "derivative", problem.derivative)
    assert problem.solution_steps[-1] == final
    assert final.latex == "f'(x) = " + problem.answer_latex
    assert all(step.say and step.latex for step in problem.solution_steps)
    assert "C" not in problem.answer_latex
    # Visible values stay small: the function at most 9, its derivative at most 18.
    for expression, bound in ((problem.function, 9), (problem.derivative, 18)):
        assert not expression.atoms(sp.Float)
        for number in expression.atoms(sp.Rational):
            assert abs(number.p) <= bound
            assert number.q <= 2
    public = problem.public().model_dump()
    assert set(public) == {"topic", "problem_latex"}
    assert public["topic"] == "derivatives"
    # The canonical answer, written by a learner, is correct and has no `+ C`.
    assert outcome(stored, learner(problem.derivative)) == ("correct", None)


def test_exact_matrix_and_structural_levels():
    assert {(name, t.difficulty) for name, t in TEMPLATES.items()} == {
        (name, level) for name, level, *_ in CASES
    }
    rules = {
        level: [t.rules for t in TEMPLATES.values() if t.difficulty == level]
        for level in range(1, 6)
    }
    single = {"power_rule", "standard_derivative"}
    # 1: one standard term; 2: one preparation; 3: one rule; 4: rule plus rewrite;
    # 5: two compatible rules. Higher levels add structure, not bigger numbers.
    assert all(len(r) == 1 and r[0] in single for r in rules[1])
    assert all(r[-1] in single | {"linear_inner"} and len(r) <= 2 for r in rules[2])
    assert all(r in {("chain_rule",), ("product_rule",), ("quotient_rule",)} for r in rules[3])
    rewrites = {"log_laws", "rewrite_as_powers", "split_fraction"}
    assert all(len(r) == 2 and r[0] in rewrites for r in rules[4])
    assert all(
        len(r) == 2 and r[0] in {"product_rule", "quotient_rule"} and r[1] == "chain_rule"
        for r in rules[5]
    )
    for level in range(1, 6):
        assert len(records(level)) == len(rules[level]) * len(COEFFICIENTS)


def test_seeded_selection_is_deterministic_and_local():
    before = random.getstate()
    for level in range(1, 6):
        problem = generate_derivative(difficulty=level, seed=17)
        assert problem == generate_derivative(difficulty=level, seed=17)
        assert problem.difficulty == level
    assert random.getstate() == before


@pytest.mark.parametrize(
    "change",
    [{"difficulty": 0}, {"difficulty": 6}, {"difficulty": True}, {"seed": -1}, {"seed": 2**32}],
)
def test_unsupported_levels_and_invalid_seeds_are_rejected(change):
    with pytest.raises(ValueError):
        generate_derivative(**{"difficulty": 1, "seed": 0, **change})


@pytest.mark.parametrize(
    "change",
    [
        {"generator_version": "derivatives-v2"},
        {"generator_version": "parts-v1"},
        {"generator_version": None},
        {"template": "__import__('os')"},
        {"template": "visible_pair"},
        {"template": 1},
        {"template": "x" * 33},
        {"coefficient": 0},
        {"coefficient": 4},
        {"coefficient": -4},
        {"coefficient": True},
        {"coefficient": "1"},
        {"coefficient": 1.0},
        {"coefficient": 10**100},
        {"answer": "x"},
        {"difficulty": 1},
    ],
)
def test_bad_records_fail_before_symbolic_construction(change, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Invalid record reached symbolic construction")

    monkeypatch.setattr(sp, "Integer", forbidden)
    with pytest.raises(ValueError):
        replay_derivative({**record("quotient_chain"), **change})


@pytest.mark.parametrize("missing", ["generator_version", "template", "coefficient"])
def test_all_replay_fields_are_required(missing):
    stored = record("product")
    del stored[missing]
    with pytest.raises(ValueError):
        replay_derivative(stored)


def test_verifier_rejects_wrong_derivatives_steps_and_domains():
    problem = replay_derivative(record("product_chain", 2))
    wrong = problem.derivative + 1
    with pytest.raises(RuntimeError):
        verify_derivative(
            replace(
                problem,
                derivative=wrong,
                solution_steps=(DerivativeStep("derivative_result", "derivative", wrong),),
            )
        )
    bad_step = DerivativeStep("derivative_chain_rule", "derivative", problem.function)
    with pytest.raises(RuntimeError):
        verify_derivative(replace(problem, solution_steps=(bad_step, *problem.solution_steps)))
    with pytest.raises(RuntimeError):
        verify_derivative(replace(problem, solution_steps=problem.solution_steps[:-1]))
    logarithm = replay_derivative(record("logarithm"))
    reals = replace(logarithm.template, domain=sp.S.Reals)
    with pytest.raises(RuntimeError):
        verify_derivative(replace(logarithm, template=reals))


def test_catalogue_offers_every_level_without_a_constant():
    for level in range(1, 6):
        exercises = catalogue("derivatives", level)
        assert len(exercises) == len(records(level))
        for exercise in exercises:
            assert exercise.topic == "derivatives"
            assert exercise.difficulty == level
            assert not exercise.answer.endswith("+ C")
            assert exercise.steps[-1]["latex"] == "f'(x) = " + exercise.answer
            assert exercise.value is None
    assert replay_exercise(record("power")).statement.startswith(r"\frac{d}{dx}")


@pytest.mark.parametrize(
    ("name", "answer"),
    [
        ("power", "4x^3"),
        ("power", "2*2*x^(4-1)"),
        ("logarithm", "1/x"),
        ("logarithm", "1/abs(x)"),
        ("root_and_reciprocal", "x^(-1/2) + 3x^(-2)"),
        ("root_and_reciprocal", "1/sqrt(x) + 3/x^2"),
        ("linear_sine", "3cos(3x)"),
        ("chain_power", "6x*(x^2+1)^2"),
        ("chain_power", "6x^5 + 12x^3 + 6x"),
        ("product", "x*cos(x) + sin(x)"),
        ("quotient", "(x+1)^(-2)"),
        ("quotient", "1/(x^2 + 2x + 1)"),
        ("log_product", "(3x + 2)/(x^2 + x)"),
        ("log_product", "2/x + 1/(x+1)"),
        ("root_chain", "x*(x^2+1)^(-1/2)"),
        ("expand_quotient", "(x^2 - 1)/x^2"),
        ("product_chain", "x*e^(3x)*(3x + 2)"),
        ("quotient_chain", "2cos(x^2) - sin(x^2)/x^2"),
        ("product_chain_trig", "cos(2x) - 2x*sin(2x)"),
    ],
)
def test_equivalent_forms_are_accepted(name, answer):
    assert outcome(record(name), answer) == ("correct", None)


@pytest.mark.parametrize(
    ("name", "answer", "expected"),
    [
        ("power", "4x^3 + C", ("incorrect", "derivative_constant")),
        ("power", "4x^3 + K", ("incorrect", "derivative_constant")),
        ("product_chain", "(3x^2 + 2x)*e^(3x) + C", ("incorrect", "derivative_constant")),
        ("power", "4x^3 + 1", ("incorrect", None)),
        ("power", "x^4", ("incorrect", None)),
        ("sine", "C*cos(x)", ("incorrect", None)),
        # sqrt(x) is undefined for x < 0, inside the declared domain (ADR-003).
        ("power", "4*sqrt(x)^6", ("invalid", None)),
        ("logarithm", "1/x + 0*ln(-x)", ("incorrect", None)),
    ],
)
def test_a_constant_or_other_change_is_not_a_derivative(name, answer, expected):
    assert outcome(record(name), answer) == expected


def _mistake_cases() -> list[tuple[dict[str, object], str, str]]:
    cases = []
    for name, coefficient in product(TEMPLATES, (1, -2)):
        problem = replay_derivative(record(name, coefficient))
        for code, wrong in problem.mistakes():
            cases.append((record(name, coefficient), learner(wrong), code))
    return cases


MISTAKES = _mistake_cases()


@pytest.mark.parametrize(("stored", "answer", "code"), MISTAKES)
def test_each_declared_mistake_is_named(stored, answer, code):
    assert outcome(stored, answer) == ("incorrect", code)


def test_mistakes_are_wrong_distinct_and_cover_the_adr_list():
    for name in TEMPLATES:
        problem = replay_derivative(record(name, 2))
        wrong = [expression for _, expression in problem.mistakes()]
        for index, expression in enumerate(wrong):
            assert sp.simplify(expression - problem.derivative) != 0
            assert all(sp.simplify(expression - other) != 0 for other in wrong[:index])
    codes = {code for _, _, code in MISTAKES}
    # ADR-005 asks at least for a missing inner derivative and a quotient-rule sign error.
    assert {"derivative_chain", "quotient_sign"} <= codes
    assert codes == {
        "derivative_power",
        "derivative_trig_sign",
        "derivative_chain",
        "derivative_factors",
        "quotient_sign",
    }
    levels = {TEMPLATES[str(stored["template"])].difficulty for stored, _, _ in MISTAKES}
    assert levels == {1, 2, 3, 4, 5}


@linux_only
@pytest.mark.parametrize(
    ("name", "answer", "expected"),
    [
        ("quotient_chain", "(2x^2*cos(x^2) - sin(x^2))/x^2", AnswerCheck("correct")),
        ("quotient_chain", "2cos(x^2) - sin(x^2)/x^2", AnswerCheck("correct")),
        (
            "quotient_chain",
            "(sin(x^2) - 2x^2*cos(x^2))/x^2",
            AnswerCheck("incorrect", feedback_code="quotient_sign"),
        ),
        ("log_quotient", "(x + 2)/(x^2 + x)", AnswerCheck("correct")),
        ("product_chain", "x*e^(3x)*(3x + 2)", AnswerCheck("correct")),
        (
            "product_chain",
            "(x^2 + 2x)*e^(3x)",
            AnswerCheck("incorrect", feedback_code="derivative_chain"),
        ),
        ("product_chain_trig", "cos(2x) - 2x*sin(2x)", AnswerCheck("correct")),
        ("root_chain", "x/sqrt(x^2 + 1)", AnswerCheck("correct")),
        (
            "root_chain",
            "x/sqrt(x^2 + 1) + C",
            AnswerCheck("incorrect", feedback_code="derivative_constant"),
        ),
    ],
)
def test_derivative_check_fits_the_worker_limits(name, answer, expected):
    assert check_answer(answer, record(name)) == expected
