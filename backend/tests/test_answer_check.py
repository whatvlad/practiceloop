from __future__ import annotations

import subprocess
import sys
import time
from typing import Any

import pytest
import sympy as sp
from test_basic import RECORDS

from app.services import math_worker
from app.services.answer_check import classify, replay_problem
from app.services.math_parser import MathInputTooLong, parse_math_input
from app.services.math_worker import (
    AnswerCheck,
    MathCheckInconclusive,
    MathWorkerError,
    _build_sympy,
    check_answer,
)

linux_only = pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux worker")


def record(
    template: str, coefficient: int = 1, secondary: int = 1, power: int = 2
) -> dict[str, Any]:
    return {
        "generator_version": "basic-v1",
        "template": template,
        "coefficient": coefficient,
        "secondary": secondary,
        "power": power,
    }


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
    return classify(
        _build_sympy(parse_math_input(answer), evaluate=True), replay_problem(problem_record)
    )


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
        (POWER, "tan(x) + C", "incorrect"),
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
    assert outcome("2x^3/3 + log(x^2) - 2log|x| + C", POWER) == "inconclusive"


def _learner_text(expression: Any) -> str:
    return sp.sstr(expression).replace("**", "^").replace("Abs", "abs")


@pytest.mark.parametrize("problem_record", RECORDS)
def test_every_generated_answer_is_accepted(problem_record: dict[str, Any]) -> None:
    problem = replay_problem(problem_record)
    primitive = _learner_text(problem.antiderivative)
    assert outcome(f"{primitive} + C", problem_record) == "correct"
    assert outcome(f"3K - ({primitive}) * (-1) + 5", problem_record) == "correct"
    assert outcome(primitive, problem_record) == "missing_constant"
    assert outcome(f"{primitive} + x + C", problem_record) == "incorrect"


def test_unknown_record_version_is_rejected() -> None:
    with pytest.raises(ValueError, match="version"):
        replay_problem({"generator_version": "basic-v9"})


# Through the real limited worker.


@linux_only
@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("2/3(x+2)^3 + 2x + 2ln|x| + C", AnswerCheck("correct")),
        ("2x^3/3 + 4x^2 + 10x + 2ln|x|", AnswerCheck("incorrect", missing_constant=True)),
        ("2x^3/3 + 4x^2 + 10x + 2ln(x) + C", AnswerCheck("incorrect")),
        ("x +* 2", AnswerCheck("invalid")),
        ("__import__('os').system('id')", AnswerCheck("invalid")),
    ],
)
def test_check_answer_end_to_end(answer: str, expected: AnswerCheck) -> None:
    assert check_answer(answer, MIXED) == expected


@linux_only
def test_inconclusive_is_a_service_error(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(MathCheckInconclusive):
        check_answer("2x^3/3 + log(x^2) - 2log|x| + C", POWER)


@linux_only
def test_unreplayable_record_is_a_server_fault() -> None:
    with pytest.raises(ValueError, match="replayed"):
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
