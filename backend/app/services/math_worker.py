"""Construct symbolic expressions only inside a resource-limited Linux process."""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryFile
from typing import Any, Literal, cast

from app.schemas.feedback import MISTAKE_CODES
from app.services.math_parser import (
    MAX_INPUT_BYTES,
    MathInputError,
    MathInputTooLong,
    MathNode,
    VariableDomain,
    declared_variables,
    parse_math_input,
)

CPU_SECONDS = 2
ADDRESS_SPACE_BYTES = 256 * 1024 * 1024
WALL_SECONDS = 3.0
MAX_OUTPUT_BYTES = 64 * 1024
MAX_CHECK_REQUEST_BYTES = 4096
_WORKER_COMMAND = (sys.executable, "-B", "-m", "app.services.math_worker")


class MathWorkerError(RuntimeError):
    """A retryable service failure, never a mathematically incorrect answer."""


def _build_sympy(node: MathNode, evaluate: bool = False) -> Any:
    # Import after child resource limits are active; never parse learner strings in SymPy.
    import sympy as sp

    if node.kind == "number":
        numerator, denominator = cast(tuple[int, int], node.value)
        return sp.Rational(numerator, denominator)
    if node.kind == "symbol":
        if node.value == "pi":
            return sp.pi
        if node.value == "e":
            return sp.E
        return sp.Symbol(node.value, real=True)
    if node.kind == "unary":
        child = _build_sympy(node.children[0], evaluate)
        return child if node.value == "+" else sp.Mul(sp.Integer(-1), child, evaluate=evaluate)
    if node.kind == "function":
        functions = {
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "sec": sp.sec,
            "csc": sp.csc,
            "cot": sp.cot,
            "asin": sp.asin,
            "acos": sp.acos,
            "atan": sp.atan,
            "exp": sp.exp,
            "ln": sp.log,
            "log": sp.log,
            "sqrt": sp.sqrt,
            "abs": sp.Abs,
        }
        return functions[cast(str, node.value)](
            _build_sympy(node.children[0], evaluate), evaluate=evaluate
        )
    left = _build_sympy(node.children[0], evaluate)
    right = _build_sympy(node.children[1], evaluate)
    if node.value == "+":
        return sp.Add(left, right, evaluate=evaluate)
    if node.value == "-":
        return sp.Add(left, sp.Mul(sp.Integer(-1), right, evaluate=evaluate), evaluate=evaluate)
    if node.value == "*":
        return sp.Mul(left, right, evaluate=evaluate)
    if node.value == "/":
        return sp.Mul(left, sp.Pow(right, sp.Integer(-1), evaluate=evaluate), evaluate=evaluate)
    return sp.Pow(left, right, evaluate=evaluate)


def _apply_limits() -> None:
    import resource

    resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS))
    resource.setrlimit(resource.RLIMIT_AS, (ADDRESS_SPACE_BYTES, ADDRESS_SPACE_BYTES))
    # Both output streams share one regular file, so this bounds their combined output.
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT_BYTES, MAX_OUTPUT_BYTES))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def _child() -> int:
    try:
        _apply_limits()
        source = sys.stdin.buffer.read(MAX_INPUT_BYTES * 4 + 1).decode("utf-8")
        _build_sympy(parse_math_input(source))
        sys.stdout.buffer.write(b"ok")
        sys.stdout.buffer.flush()
        return 0
    except Exception:
        # Never expose learner text, tracebacks or serialized symbolic objects to the parent.
        return 1


def record_variables(record: Mapping[str, object]) -> dict[str, VariableDomain] | None:
    """ADR-005 variables a stored record declares; None for the integration grammar.

    The generator copies them from its template; replay checks they still match.
    """
    if "variables" not in record:
        return None
    return declared_variables(record["variables"])


def _check_child() -> int:
    try:
        _apply_limits()
        request = json.loads(sys.stdin.buffer.read(MAX_CHECK_REQUEST_BYTES + 1))
        # Imported only now, under the limits: both modules import SymPy.
        from app.engine import practice as engine
        from app.services.answer_check import check_and_diagnose, replay_problem

        if engine.is_engine_record(request["record"]):
            try:
                engine.replay(request["record"])
            except (KeyError, TypeError, ValueError):
                outcome = "bad_record"
            else:
                tree = parse_math_input(request["answer"])
                outcome = engine.check(request["record"], tree)
            sys.stdout.buffer.write(outcome.encode("ascii"))
            sys.stdout.buffer.flush()
            return 0
        try:
            problem = replay_problem(request["record"])
            variables = record_variables(request["record"])
            if variables is not None and getattr(problem, "variables", None) != variables:
                raise ValueError("Record variables differ from the template")
        except (KeyError, TypeError, ValueError):
            outcome = "bad_record"
        else:
            tree = parse_math_input(request["answer"], variables)
            outcome, code = check_and_diagnose(tree, problem, request["record"])
            if code is not None:
                outcome += ":" + code
        sys.stdout.buffer.write(outcome.encode("ascii"))
        sys.stdout.buffer.flush()
        return 0
    except Exception:
        return 1


def _run_worker(arguments: tuple[str, ...], request: bytes) -> bytes:
    """Run one fresh limited child; return its bounded output or raise MathWorkerError."""
    if not sys.platform.startswith("linux"):
        raise MathWorkerError("The resource-limited math worker requires Linux")
    try:
        with TemporaryFile() as output:
            # Fixed trusted argv, no shell; learner text goes only to bounded stdin.
            with subprocess.Popen(  # noqa: S603
                (*_WORKER_COMMAND, *arguments),
                cwd=Path(__file__).resolve().parents[2],
                stdin=subprocess.PIPE,
                stdout=output,
                stderr=subprocess.STDOUT,
            ) as process:
                try:
                    process.communicate(request, timeout=WALL_SECONDS)
                except subprocess.TimeoutExpired as exc:
                    raise MathWorkerError("Math worker exceeded its wall-clock limit") from exc
                finally:
                    # Also reap on interruption or communication failure, not just timeout.
                    if process.poll() is None:
                        process.kill()
                    process.wait()
                output.seek(0)
                payload = output.read(MAX_OUTPUT_BYTES + 1)
                if process.returncode != 0 or len(payload) > MAX_OUTPUT_BYTES:
                    raise MathWorkerError("Math worker failed within its resource limits")
                return payload
    except OSError as exc:
        raise MathWorkerError("Math worker could not run") from exc


def validate_math_input(source: str) -> None:
    """Check syntax before spawning; construct SymPy only under child resource limits.

    Raises MathInputError for invalid syntax (MathInputTooLong for request size),
    or MathWorkerError for a retryable execution failure. Does not check equivalence.
    """
    parse_math_input(source)
    if _run_worker((), source.encode("utf-8")) != b"ok":
        raise MathWorkerError("Math worker failed within its resource limits")


type CheckResult = Literal["correct", "incorrect", "invalid"]


class MathCheckInconclusive(RuntimeError):
    """Neither proof nor a certified difference: 503 math_check_inconclusive, no attempt."""


@dataclass(frozen=True)
class AnswerCheck:
    result: CheckResult
    missing_constant: bool = False
    # A declared mistake (#36) that an incorrect answer unambiguously matches.
    feedback_code: str | None = None


_CHECK_OUTCOMES = {
    b"correct": AnswerCheck("correct"),
    b"incorrect": AnswerCheck("incorrect"),
    b"missing_constant": AnswerCheck("incorrect", missing_constant=True),
    b"invalid": AnswerCheck("invalid"),
}


def check_answer(answer: str, record: Mapping[str, object]) -> AnswerCheck:
    """ADR-003 check of a learner answer against a stored private generator record.

    Raises MathInputTooLong (422, no attempt), MathWorkerError (retryable 503) or
    MathCheckInconclusive (503). Grammar rejections are an `invalid` result.
    ValueError means the stored record itself is unusable: a server fault.
    """
    variables = record_variables(record)
    try:
        parse_math_input(answer, variables)
    except MathInputTooLong:
        raise
    except MathInputError:
        return AnswerCheck("invalid")
    request = json.dumps({"record": dict(record), "answer": answer}).encode("utf-8")
    if len(request) > MAX_CHECK_REQUEST_BYTES:
        raise ValueError("Generator record is too large")
    outcome = _run_worker(("check",), request)
    if outcome == b"inconclusive":
        raise MathCheckInconclusive("Answer could not be decided within the worker limits")
    if outcome == b"bad_record":
        raise ValueError("Generator record cannot be replayed")
    if outcome.startswith(b"incorrect:"):
        code = outcome.removeprefix(b"incorrect:").decode("ascii", "replace")
        if code not in MISTAKE_CODES:
            raise MathWorkerError("Math worker failed within its resource limits")
        return AnswerCheck("incorrect", feedback_code=code)
    if outcome not in _CHECK_OUTCOMES:
        raise MathWorkerError("Math worker failed within its resource limits")
    return _CHECK_OUTCOMES[outcome]


if __name__ == "__main__":
    sys.exit(_check_child() if sys.argv[1:] == ["check"] else _child())
