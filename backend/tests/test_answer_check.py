from __future__ import annotations

import subprocess
import sys
import time
from typing import Any

import pytest
import sympy as sp
from engine_fixtures import CURRICULUM, answer_for, check, native_record

from app.math_input import MathInputTooLong, parse_math_input
from app.services import math_worker
from app.services.math_worker import (
    AnswerCheck,
    MathCheckInconclusive,
    MathWorkerError,
    check_answer,
)

linux_only = pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux worker")


def test_domain_check_avoids_repeating_sum_domains_and_preserves_holes(monkeypatch) -> None:
    from app.engine.answers import _symbolic

    original = _symbolic.continuous_domain
    calls = []

    def track(value, variable, domain):
        if value.has(sp.log):
            calls.append(value)
        return original(value, variable, domain)

    monkeypatch.setattr(_symbolic, "continuous_domain", track)
    domain = sp.Union(
        sp.Interval.open(-sp.oo, -1), sp.Interval.open(-1, 0), sp.Interval.open(0, sp.oo)
    )
    assert _symbolic.check_domain(parse_math_input("x^2/2-x+ln|x^2+x|+C"), domain) is None
    assert len(calls) == 1
    assert _symbolic.check_domain(parse_math_input("x+1/x"), sp.S.Reals) == "invalid"
    assert _symbolic.check_domain(parse_math_input("0*(1/x)"), sp.S.Reals) == "invalid"


def test_rational_log_primitive_has_an_exact_domain_checked_fast_proof(monkeypatch) -> None:
    from app.engine.answers import _symbolic

    x = _symbolic.X
    domain = sp.S.Reals - sp.FiniteSet(-1, 0)
    candidate = x**2 / 2 - x + sp.log(sp.Abs(x**2 + x))
    integrand = (x**3 + x + 1) / (x * (x + 1))
    certify = _symbolic.certifies_rational_primitive
    assert certify(candidate, integrand, x, domain)
    # The same polynomial has zeros on R: the proof cannot erase those holes.
    assert not certify(candidate, integrand, x, sp.S.Reals)
    assert not certify(candidate + x, integrand, x, domain)
    assert not certify(candidate + sp.I, integrand, x, domain)
    assert not certify(sp.sin(x), sp.cos(x), x, sp.S.Reals)
    monkeypatch.setattr(_symbolic, "certifies_rational_primitive", lambda *_: False)
    assert _symbolic.is_primitive(candidate, integrand, domain) == "yes"
    monkeypatch.setattr(_symbolic, "certifies_rational_primitive", certify)
    assert _symbolic.is_primitive(candidate, integrand, domain) == "yes"


def record(
    template: str, coefficient: int = 1, secondary: int = 1, power: int = 2
) -> dict[str, Any]:
    return native_record("basic", template, coefficient, secondary, power)


POWER = record("power", 2, power=3)  # 2x^2, primitive 2x^3/3, all reals
RECIPROCAL = record("reciprocal")  # 1/x on x != 0
FRACTIONAL = record("fractional_power", 2)  # 2/sqrt(x) on x > 0
NEGATIVE = record("negative_power")  # x^-2 on x != 0
SINE = record("sine", 3)  # 3 sin x
COSINE = record("cosine")
SQUARE = record("expand_square")  # (x+1)^2
MIXED = record("expand_and_split", 2, 2)  # 2(x+2)^2 + (2x+2)/x on x != 0
SUM = record("sum", 2, 2, 3)  # 2x^2 + 2e^x


def outcome(answer: str, problem_record: dict[str, Any]) -> str:
    """In-process classification for fast table tests; production runs it in the worker."""
    return answer_for(problem_record).check(parse_math_input(answer))


RECORDS = [
    native_record(**row["form"])
    for row in CURRICULUM["integrals"]
    if row["form"]["family"] == "basic"
]


@pytest.mark.parametrize(
    ("problem", "answer", "expected"),
    [
        # Notation and equivalent fractions.
        (POWER, "2x^3/3 + C", "correct"),
        (POWER, "2/3 x^3 + C", "correct"),
        (POWER, "0.666666 x^3 + C", "incorrect"),
        (POWER, "(2x^3 + 7)/3 + k", "correct"),
        (POWER, "x^3 * 4/6 + c", "correct"),
        # Constant policy: aK + b with a nonzero real number a.
        (POWER, "2x^3/3 + 2C + 7", "correct"),
        (POWER, "2x^3/3 - pi*C", "correct"),
        (POWER, "2x^3/3 + C^2", "incorrect"),
        (POWER, "2x^3/3 + C*x", "incorrect"),
        (POWER, "2x^3/3 + e^C", "incorrect"),
        (POWER, "C", "incorrect"),
        (POWER, "2x^3/3", "missing_constant"),
        (POWER, "2x^3/3 + 7", "missing_constant"),
        (POWER, "2x^3/3 + C - C", "missing_constant"),
        (POWER, "x^3 + C", "incorrect"),
        (POWER, "x^3", "incorrect"),
        (POWER, "2x^3/3 + sqrt(x^2) - abs(x) + C", "correct"),
        (POWER, "tan(x) + C", "invalid"),
        (POWER, "1/(x-x) + C", "invalid"),
        # Logs, absolute values and the real domain.
        (RECIPROCAL, "ln|x| + C", "correct"),
        (RECIPROCAL, "log(abs(x)) + C", "correct"),
        (RECIPROCAL, "ln|2x| + C", "correct"),
        (RECIPROCAL, "ln(x^2)/2 + C", "correct"),
        (RECIPROCAL, "ln(x) + C", "incorrect"),
        (RECIPROCAL, "ln(2x) + C", "incorrect"),
        (RECIPROCAL, "ln|x|", "missing_constant"),
        # Different constants on the two components are not one numeric b.
        (RECIPROCAL, "ln|x| + |x|/x + C", "incorrect"),
        (FRACTIONAL, "4sqrt(x) + C", "correct"),
        (FRACTIONAL, "4x^(1/2) + C", "correct"),
        (FRACTIONAL, "4sqrt(abs(x)) + C", "correct"),
        (FRACTIONAL, "2sqrt(x) + C", "incorrect"),
        (NEGATIVE, "-1/x + C", "correct"),
        (NEGATIVE, "-x^(-1) + C", "correct"),
        (NEGATIVE, "(-1-x)/x + C", "correct"),
        (NEGATIVE, "(1-x)/x + C", "incorrect"),
        # Trigonometric identities.
        (SINE, "-3cos(x) + C", "correct"),
        (SINE, "3 - 3cos(x) + C", "correct"),
        (SINE, "6sin^2(x/2) + C", "correct"),
        (SINE, "3cos(x) + C", "incorrect"),
        (COSINE, "sin(x) + C", "correct"),
        (COSINE, "2sin(x/2)cos(x/2) + C", "correct"),
        (COSINE, "sin(x)", "missing_constant"),
        # Multi-step templates.
        (SQUARE, "(x+1)^3/3 + C", "correct"),
        (SQUARE, "x^3/3 + x^2 + x + C", "correct"),
        (MIXED, "2x^3/3 + 4x^2 + 10x + 2ln|x| + C", "correct"),
        (MIXED, "2/3(x+2)^3 + 2x + 2ln|x| + C", "correct"),
        (MIXED, "2x^3/3 + 4x^2 + 10x + 2ln(x) + C", "incorrect"),
        (SUM, "2x^3/3 + 2*e^x + C", "correct"),
        (SUM, "2x^3/3 + 2*exp(x) + C", "correct"),
        (SUM, "2x^4/3 + 2*e^x + C", "incorrect"),
    ],
)
def test_classification(problem: dict[str, Any], answer: str, expected: str) -> None:
    assert outcome(answer, problem) == expected


def test_undecidable_definedness_is_inconclusive_not_a_guess() -> None:
    # log(x^2) is undefined at x = 0, which is inside the problem's domain.
    assert outcome("2x^3/3 + log(x^2) - 2log|x| + C", POWER) == "invalid"


def _learner_text(expression: Any) -> str:
    return sp.sstr(expression).replace("**", "^").replace("Abs", "abs")


@pytest.mark.parametrize("problem_record", RECORDS)
def test_every_generated_answer_is_accepted(problem_record: dict[str, Any]) -> None:
    problem = answer_for(problem_record)
    primitive = _learner_text(problem.primitive)
    assert outcome(f"{primitive} + C", problem_record) == "correct"
    assert outcome(f"3K - ({primitive}) * (-1) + 5", problem_record) == "correct"
    assert outcome(primitive, problem_record) == "missing_constant"
    assert outcome(f"{primitive} + x + C", problem_record) == "incorrect"


def family(version: str, template: str, coefficient: int = 1) -> dict[str, Any]:
    names = {
        "rational-v1": "rational",
        "parts-v1": "parts",
        "trigonometric-v1": "trigonometric",
        "substitution-v2": "substitution",
    }
    return native_record(names[version], template, coefficient)


FAMILY_RECORDS = [
    native_record(**row["form"])
    for row in CURRICULUM["integrals"]
    if row["form"]["family"] != "basic"
]

POLES = family("rational-v1", "distinct_factors")  # 1/(x(x+1)) on x not in {-1, 0}
REPEATED = family("rational-v1", "repeated_factor")  # 1/(x(x+1)^2)
DIVISION = family("rational-v1", "division_then_fractions")  # (x^3+x+1)/(x(x+1))
LOG_ONLY = family("rational-v1", "linear_denominator")  # 1/x on x != 0
PARTS = family("parts-v1", "linear_exponential")  # x e^x
CYCLIC = family("parts-v1", "cyclic_sine")  # e^x sin x
ODD = family("trigonometric-v1", "odd_power")  # sin^3 x
EVEN = family("trigonometric-v1", "even_power")  # sin^2 x
NESTED = family("substitution-v2", "identity_nested")  # x sin(x^2) sin(2x^2)


@pytest.mark.parametrize("problem_record", FAMILY_RECORDS)
def test_every_family_answer_is_accepted(problem_record: dict[str, Any]) -> None:
    test_every_generated_answer_is_accepted(problem_record)


@pytest.mark.parametrize(
    ("problem", "answer", "expected"),
    [
        # Every connected component of a multi-pole domain, including (-1, 0).
        (POLES, "ln|x| - ln|x+1| + C", "correct"),
        (POLES, "ln|x/(x+1)| + C", "correct"),
        (POLES, "ln|x| - ln|x+1|", "missing_constant"),
        (POLES, "ln(x) - ln(x+1) + C", "incorrect"),
        (POLES, "ln|x| - ln(x+1) + C", "incorrect"),
        (POLES, "ln|x| + ln|x+1| + C", "incorrect"),
        # The derivative is right, but the offset differs between components.
        (POLES, "ln|x| - ln|x+1| + abs(x+1)/(x+1) + C", "incorrect"),
        (POLES, "ln|x| - ln|x+1| + abs(x)/x + C", "incorrect"),
        # A part undefined inside the domain cannot be cancelled away.
        (POLES, "ln|x| - ln|x+1| + (x-2)/(x-2) + C", "incorrect"),
        (POLES, "ln|x| - ln|x+1| + 1/(x-x) + C", "invalid"),
        (REPEATED, "ln|x| - ln|x+1| + 1/(x+1) + C", "correct"),
        (REPEATED, "ln|x/(x+1)| + 1/(x+1) + C", "correct"),
        (REPEATED, "ln|x/(x+1)| - 1/(x+1) + C", "incorrect"),
        (DIVISION, "x^2/2 - x + ln|x| + ln|x+1| + C", "correct"),
        (DIVISION, "x^2/2 - x + ln|x^2 + x| + C", "correct"),
        (DIVISION, "(x-1)^2/2 + ln|x*(x+1)| + C", "correct"),
        (DIVISION, "x^2/2 - x + ln|x| - ln|x+1| + C", "incorrect"),
        (LOG_ONLY, "ln|x| + C", "correct"),
        (LOG_ONLY, "ln(x) + C", "incorrect"),
        # All-real families keep the preview's hole rule and accept alternative methods.
        (PARTS, "x e^x - e^x + C", "correct"),
        (PARTS, "(x-1)e^x + C", "correct"),
        (PARTS, "x e^x + C", "incorrect"),
        (PARTS, "(x-1)e^x + (x-2)/(x-2) + C", "invalid"),
        (CYCLIC, "e^x * (sin(x) - cos(x))/2 + C", "correct"),
        (CYCLIC, "e^x sin(x)/2 - e^x cos(x)/2 + C", "correct"),
        (CYCLIC, "e^x * (sin(x) + cos(x))/2 + C", "incorrect"),
        (ODD, "cos^3(x)/3 - cos(x) + C", "correct"),
        (ODD, "-cos(x) + cos(x)^3/3 + C", "correct"),
        (ODD, "-cos(x) + C", "incorrect"),
        (EVEN, "x/2 - sin(2x)/4 + C", "correct"),
        (EVEN, "x/2 - sin(x)cos(x)/2 + C", "correct"),
        (EVEN, "(x - sin(x)cos(x))/2", "missing_constant"),
        (NESTED, "sin^3(x^2)/3 + C", "correct"),
        (NESTED, "-cos^3(x^2)/3 + C", "incorrect"),
    ],
)
def test_family_classification(problem: dict[str, Any], answer: str, expected: str) -> None:
    assert check(parse_math_input(answer), answer_for(problem)) == expected


def test_unknown_record_version_is_rejected() -> None:
    with pytest.raises(ValueError, match="record"):
        answer_for({"generator_version": "basic-v9"})


# Through the real limited worker.


@linux_only
@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("2/3(x+2)^3 + 2x + 2ln|x| + C", AnswerCheck("correct")),
        ("2x^3/3 + 4x^2 + 10x + 2ln|x|", AnswerCheck("incorrect", missing_constant=True)),
        (
            "2x^3/3 + 4x^2 + 10x + 2ln(x) + C",
            AnswerCheck("incorrect", feedback_code=None),
        ),
        ("x +* 2", AnswerCheck("invalid")),
        ("__import__('os').system('id')", AnswerCheck("invalid")),
    ],
)
def test_check_answer_end_to_end(answer: str, expected: AnswerCheck) -> None:
    assert check_answer(answer, MIXED) == expected


@linux_only
@pytest.mark.parametrize(
    ("problem", "answer", "expected"),
    [
        (DIVISION, "x^2/2 - x + ln|x^2 + x| + C", AnswerCheck("correct")),
        (DIVISION, "x^2/2 - x + ln|x| + ln|x+1|", AnswerCheck("incorrect", missing_constant=True)),
        (POLES, "ln|x| - ln|x+1| + abs(x)/x + C", AnswerCheck("incorrect")),
        (CYCLIC, "e^x * (sin(x) - cos(x))/2 + C", AnswerCheck("correct")),
        (NESTED, "sin^3(x^2)/3 + C", AnswerCheck("correct")),
    ],
)
def test_family_check_fits_the_worker_limits(
    problem: dict[str, Any], answer: str, expected: AnswerCheck
) -> None:
    assert check_answer(answer, problem) == expected


@linux_only
def test_original_domain_hole_is_invalid_before_simplification() -> None:
    assert check_answer("2x^3/3 + log(x^2) - 2log|x| + C", POWER) == AnswerCheck("invalid")


def test_inconclusive_is_a_service_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(math_worker, "_run_worker", lambda *_args: b"inconclusive")
    with pytest.raises(MathCheckInconclusive):
        check_answer("2x^3/3+C", POWER)


@linux_only
def test_unreplayable_record_is_a_server_fault() -> None:
    with pytest.raises(ValueError, match="record"):
        check_answer("x + C", {**POWER, "coefficient": 0})


def test_oversized_answer_is_request_validation() -> None:
    with pytest.raises(MathInputTooLong):
        check_answer("x+" * 200 + "C", POWER)


def test_invalid_syntax_never_starts_a_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_args: Any, **_kwargs: Any) -> None:
        pytest.fail("worker started for invalid syntax")

    monkeypatch.setattr(math_worker.subprocess, "Popen", forbidden)
    assert check_answer("sin x", POWER) == AnswerCheck("invalid")


@linux_only
def test_worker_output_outside_the_protocol_is_a_service_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    script = "import sys\nsys.stdout.write('correct!')"
    monkeypatch.setattr(math_worker, "_WORKER_COMMAND", (sys.executable, "-B", "-c", script))
    with pytest.raises(MathWorkerError, match="resource limits"):
        check_answer("x + C", POWER)


# Adversarial corpus: grammar-valid answers that stress SymPy. Each must end in a
# decided result or a retryable service error within the wall limit, never a crash,
# a hang or a result reported as `incorrect` because the worker gave up.
ADVERSARIAL = [
    "e^(e^(e^(e^x))) + C",
    "(99999999^12)^12 * x + C",
    "sin(" * 12 + "x" + ")" * 12 + " + C",
    "(x+1)^12 * (x+2)^12 * (x+3)^12 * (x+4)^12 + C",
    "((x+1)^12 + 1)^12 + C",
    "e^(x^12) * sin(x^12) * cos(x^12) * tan(x^12) + C",
    "abs(abs(abs(abs(x - 1) - 2) - 3) - 4) + C",
    "asin(x) + acos(x) + atan(x) + sec(x) + csc(x) + cot(x) + C",
    "sqrt(sqrt(sqrt(sqrt(sqrt(sqrt(x^12 + 1)))))) + C",
    "ln(abs(ln(abs(ln(abs(x)))))) + C",
    "(x^(1/12))^12 - x + 2x^3/3 + C",
    "(12345678/9999999)^12 * x^12 / (x^12 + 1)^12 + C",
]


@linux_only
@pytest.mark.parametrize("answer", ADVERSARIAL)
def test_adversarial_answers_terminate_within_limits(
    monkeypatch: pytest.MonkeyPatch, answer: str
) -> None:
    processes: list[subprocess.Popen[bytes]] = []
    popen = subprocess.Popen

    def observe(*args: Any, **kwargs: Any) -> subprocess.Popen[bytes]:
        process = popen(*args, **kwargs)
        processes.append(process)
        return process

    monkeypatch.setattr(math_worker.subprocess, "Popen", observe)
    started = time.monotonic()
    try:
        result = check_answer(answer, POWER)
    except (MathWorkerError, MathCheckInconclusive):
        pass
    else:
        assert result.result in {"correct", "incorrect", "invalid"}
    assert time.monotonic() - started < math_worker.WALL_SECONDS + 3
    assert processes and all(process.returncode is not None for process in processes)
