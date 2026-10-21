"""#36 mistake diagnosis: every declared mistake of every offered record is named,
and nothing else is: correct answers, unrelated errors and ambiguous matches get none."""

from pathlib import Path

import pytest
import sympy as sp
from test_definite import linux_only

from app.api.practice import TOPICS
from app.content.catalogue import TEXT
from app.generators.core import catalogue
from app.generators.definite import TEMPLATES, base_record, replay_definite
from app.generators.mistakes import declared
from app.schemas.feedback import MISTAKE_CODES
from app.services.answer_check import check_and_diagnose, replay_problem
from app.services.math_parser import parse_math_input
from app.services.math_worker import AnswerCheck, check_answer

# Every offered cell, from the same table `GET /topics` publishes.
CELLS = [(topic, level) for topic, cell in TOPICS.items() for level in cell.levels]


def learner(expression: sp.Expr) -> str:
    """An expression written in the ADR-003 input grammar."""
    return (
        str(expression)
        .replace("**", "^")
        .replace("Abs", "abs")
        .replace("E", "e")
        .replace("exp(", "e^(")
    )


def outcome(record: dict[str, object], answer: str) -> tuple[str, str | None]:
    return check_and_diagnose(parse_math_input(answer), replay_problem(record), record)


def test_every_code_has_feedback_text_and_is_declared_somewhere() -> None:
    assert MISTAKE_CODES == {
        "power_rule",
        "trig_sign",
        "chain_factor",
        "log_absolute",
        "split_product",
        "parts_sign",
        "cycle_factor",
        "partial_fraction_sign",
        "definite_not_evaluated",
        "bounds_reversed",
        "definite_constant",
        "missing_jacobian",
        "derivative_power",
        "derivative_trig_sign",
        "derivative_chain",
        "derivative_factors",
        "quotient_sign",
        "derivative_constant",
        "partial_held_constant",
        "partial_chain_term",
        "jacobian_missing_r",
        "jacobian_sign",
        "z_bounds",
    }
    for code in MISTAKE_CODES:
        assert TEXT[f"feedback_{code}"]  # type: ignore[literal-required]
    frontend = Path(__file__).resolve().parents[2] / "frontend/src/data/types.ts"
    for code in MISTAKE_CODES:
        assert f"'{code}'" in frontend.read_text()


def _indefinite_cases() -> list[tuple[dict[str, object], str, str]]:
    cases = []
    for topic, level in CELLS:
        for exercise in catalogue(topic, level):
            if exercise.value is not None or exercise.record.get("coefficient", 1) not in (1, -2):
                continue
            mistakes = declared(dict(exercise.record), exercise.primitive)
            for code, wrong in mistakes:
                cases.append((exercise.record, learner(wrong) + " + C", code))
    return cases


INDEFINITE = _indefinite_cases()


@pytest.mark.parametrize(("record", "answer", "code"), INDEFINITE)
def test_each_declared_indefinite_mistake_is_named(record, answer, code) -> None:
    assert outcome(record, answer) == ("incorrect", code)
    # Without its constant the same mistake is still named, not reported as missing C.
    assert outcome(record, answer.removesuffix(" + C")) == ("incorrect", code)


def test_every_family_declares_mistakes() -> None:
    templates = {
        (r["generator_version"], r.get("template", r.get("family"))) for r, *_ in INDEFINITE
    }
    assert ("parts-v1", "cyclic_sine") in templates
    assert ("rational-v1", "repeated_factor") in templates
    assert ("trigonometric-v1", "even_power") in templates
    assert ("substitution-v2", "factor_square") in templates
    assert ("substitution-v1", "cos") in templates
    assert ("basic-v1", "reciprocal") in templates


def _definite_cases() -> list[tuple[dict[str, object], str, str | None]]:
    cases: list[tuple[dict[str, object], str, str | None]] = []
    for name, template in TEMPLATES.items():
        record = {"generator_version": "definite-v1", "template": name, "coefficient": 2}
        problem = replay_definite(record)
        cases.append((record, learner(problem.antiderivative), "definite_not_evaluated"))
        cases.append((record, learner(problem.value) + " + C", "definite_constant"))
        for code, wrong in declared(base_record(template, 2), problem.antiderivative):
            value = sp.simplify(wrong.subs(sp.Symbol("x", real=True), problem.upper))
            value -= sp.simplify(wrong.subs(sp.Symbol("x", real=True), problem.lower))
            if sp.simplify(value - problem.value) != 0 and value.is_finite:
                cases.append((record, learner(sp.nsimplify(value)), code))
    return cases


@pytest.mark.parametrize(("record", "answer", "code"), _definite_cases())
def test_each_declared_definite_mistake_is_named_or_left_ambiguous(record, answer, code) -> None:
    result, named = outcome(record, answer)
    assert result == "incorrect"
    # Two mistakes may give the same number on these bounds; then none is named.
    assert named in (code, None)


@pytest.mark.parametrize(
    ("record", "answer", "expected"),
    [
        # Bounds reversed is unambiguous here; on [0, π] for sin x it also equals the
        # lost-sign mistake, so no diagnosis is given.
        (
            {
                "generator_version": "definite-v1",
                "template": "quadratic_exponential",
                "coefficient": 1,
            },
            "2 - e",
            "bounds_reversed",
        ),
        ({"generator_version": "definite-v1", "template": "sine", "coefficient": 1}, "-2", None),
        (
            {"generator_version": "definite-v1", "template": "reciprocal", "coefficient": 1},
            "7",
            None,
        ),
        (
            {
                "generator_version": "basic-v1",
                "template": "power",
                "coefficient": 2,
                "secondary": 1,
                "power": 3,
            },
            "x^3 + 5x + C",
            None,
        ),
        (
            {
                "generator_version": "rational-v1",
                "template": "division_then_fractions",
                "coefficient": 1,
            },
            "x^2/2 + x + C",
            None,
        ),
        # Right derivative but a different constant on each side of the poles: the
        # ln(x) mistake has the same derivative, yet this answer is not that mistake.
        (
            {"generator_version": "rational-v1", "template": "distinct_factors", "coefficient": 1},
            "ln|x| - ln|x+1| + abs(x)/x + C",
            None,
        ),
    ],
)
def test_unmatched_or_ambiguous_errors_get_a_general_hint(record, answer, expected) -> None:
    assert outcome(record, answer) == ("incorrect", expected)


@pytest.mark.parametrize(
    ("record", "answer"),
    [
        (
            {
                "generator_version": "basic-v1",
                "template": "reciprocal",
                "coefficient": 1,
                "secondary": 1,
                "power": 2,
            },
            "ln|x| + C",
        ),
        (
            {
                "generator_version": "basic-v1",
                "template": "reciprocal",
                "coefficient": 1,
                "secondary": 1,
                "power": 2,
            },
            "ln|x|",
        ),
        ({"generator_version": "definite-v1", "template": "reciprocal", "coefficient": 1}, "1"),
        (
            {"generator_version": "trigonometric-v1", "template": "sine", "coefficient": 1},
            "1/(x - x)",
        ),
    ],
)
def test_correct_missing_constant_and_invalid_answers_get_no_diagnosis(record, answer) -> None:
    assert outcome(record, answer)[1] is None


@linux_only
@pytest.mark.parametrize(
    ("record", "answer", "expected"),
    [
        (
            {"generator_version": "rational-v1", "template": "repeated_factor", "coefficient": 3},
            "3ln|x| - 3ln|x+1| - 3/(x+1) + C",
            AnswerCheck("incorrect", feedback_code="partial_fraction_sign"),
        ),
        (
            {
                "generator_version": "rational-v1",
                "template": "division_then_fractions",
                "coefficient": 1,
            },
            "x^2/2 - x + ln(x) + ln(x+1) + C",
            AnswerCheck("incorrect", feedback_code="log_absolute"),
        ),
        (
            {"generator_version": "parts-v1", "template": "cyclic_sine", "coefficient": 1},
            "e^x*(sin(x) - cos(x)) + C",
            AnswerCheck("incorrect", feedback_code="cycle_factor"),
        ),
        (
            {
                "generator_version": "definite-v1",
                "template": "quadratic_exponential",
                "coefficient": 1,
            },
            "e^x*(x^2 - 2x + 2)",
            AnswerCheck("incorrect", feedback_code="definite_not_evaluated"),
        ),
    ],
)
def test_diagnosis_fits_the_worker_limits(record, answer, expected) -> None:
    assert check_answer(answer, record) == expected
