"""Construct symbolic expressions only inside a resource-limited Linux process."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryFile
from typing import Any, cast

from app.services.math_parser import MAX_INPUT_BYTES, MathNode, parse_math_input

CPU_SECONDS = 2
ADDRESS_SPACE_BYTES = 256 * 1024 * 1024
WALL_SECONDS = 3.0
MAX_OUTPUT_BYTES = 64 * 1024
_WORKER_COMMAND = (sys.executable, "-B", "-m", "app.services.math_worker")


class MathWorkerError(RuntimeError):
    """A retryable service failure, never a mathematically incorrect answer."""


def _build_sympy(node: MathNode) -> Any:
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
        child = _build_sympy(node.children[0])
        return child if node.value == "+" else sp.Mul(sp.Integer(-1), child, evaluate=False)
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
        return functions[cast(str, node.value)](_build_sympy(node.children[0]), evaluate=False)
    left = _build_sympy(node.children[0])
    right = _build_sympy(node.children[1])
    if node.value == "+":
        return sp.Add(left, right, evaluate=False)
    if node.value == "-":
        return sp.Add(left, sp.Mul(sp.Integer(-1), right, evaluate=False), evaluate=False)
    if node.value == "*":
        return sp.Mul(left, right, evaluate=False)
    if node.value == "/":
        return sp.Mul(left, sp.Pow(right, sp.Integer(-1), evaluate=False), evaluate=False)
    return sp.Pow(left, right, evaluate=False)


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


def validate_math_input(source: str) -> None:
    """Check syntax before spawning; construct SymPy only under child resource limits.

    Raises MathInputError for invalid syntax (MathInputTooLong for request size),
    or MathWorkerError for a retryable execution failure. Does not check equivalence.
    """
    parse_math_input(source)
    if not sys.platform.startswith("linux"):
        raise MathWorkerError("The resource-limited math worker requires Linux")
    try:
        with TemporaryFile() as output:
            # Fixed trusted argv, no shell; learner text goes only to bounded stdin.
            with subprocess.Popen(  # noqa: S603
                _WORKER_COMMAND,
                cwd=Path(__file__).resolve().parents[2],
                stdin=subprocess.PIPE,
                stdout=output,
                stderr=subprocess.STDOUT,
            ) as process:
                try:
                    process.communicate(source.encode("utf-8"), timeout=WALL_SECONDS)
                except subprocess.TimeoutExpired as exc:
                    raise MathWorkerError("Math worker exceeded its wall-clock limit") from exc
                finally:
                    # Also reap on interruption or communication failure, not just timeout.
                    if process.poll() is None:
                        process.kill()
                    process.wait()
                output.seek(0)
                payload = output.read(MAX_OUTPUT_BYTES + 1)
                if process.returncode != 0 or payload != b"ok":
                    raise MathWorkerError("Math worker failed within its resource limits")
    except OSError as exc:
        raise MathWorkerError("Math worker could not run") from exc


if __name__ == "__main__":
    sys.exit(_child())
