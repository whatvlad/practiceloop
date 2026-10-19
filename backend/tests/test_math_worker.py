from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from contextlib import nullcontext
from subprocess import Popen
from tempfile import TemporaryFile
from typing import Any

import pytest

from app.services import math_worker
from app.services.math_parser import MathInputError
from app.services.math_worker import MathWorkerError, validate_math_input

pytestmark = pytest.mark.skipif(
    not sys.platform.startswith("linux"), reason="Linux resource limits"
)


@pytest.fixture
def workers(monkeypatch: pytest.MonkeyPatch) -> list[subprocess.Popen[bytes]]:
    """Observe the real processes so tests prove that failed children were reaped."""
    processes: list[subprocess.Popen[bytes]] = []
    popen = subprocess.Popen

    def record(*args: Any, **kwargs: Any) -> subprocess.Popen[bytes]:
        process = popen(*args, **kwargs)
        processes.append(process)
        return process

    monkeypatch.setattr(math_worker.subprocess, "Popen", record)
    return processes


def _replace_child_computation(monkeypatch: pytest.MonkeyPatch, body: str) -> None:
    # Trusted test-only code replaces computation in a fresh interpreter. The actual
    # production launcher, limits, parser, result protocol and cleanup still execute.
    script = (
        "from app.services import math_worker as worker\n"
        "def compute(node):\n"
        + "\n".join("    " + line for line in body.splitlines())
        + "\nworker._build_sympy = compute\nraise SystemExit(worker._child())\n"
    )
    monkeypatch.setattr(math_worker, "_WORKER_COMMAND", (sys.executable, "-B", "-c", script))


@pytest.mark.parametrize(
    "source",
    [
        "3π + sqrt(3) + e^2",
        "sin(x)+cos(x)+tan(x)+sec(x)+csc(x)+cot(x)",
        "asin(x)+acos(x)+atan(x)+exp(x)+ln(x)+log(x)+sqrt(x)+abs(x)",
        "e^(e^(e^(e^x)))",
        "(99999999^12)^12",
        "sin(" * 12 + "x" + ")" * 12,
    ],
)
def test_valid_and_pathological_expressions_are_bounded(source: str) -> None:
    validate_math_input(source)


def test_limits_are_active_only_in_child(monkeypatch: pytest.MonkeyPatch) -> None:
    import resource

    limits = [resource.RLIMIT_CPU, resource.RLIMIT_AS, resource.RLIMIT_FSIZE]
    before = [resource.getrlimit(limit) for limit in limits]
    _replace_child_computation(
        monkeypatch,
        "import resource\n"
        "assert resource.getrlimit(resource.RLIMIT_CPU) == (2, 2)\n"
        "assert resource.getrlimit(resource.RLIMIT_AS) == (268435456, 268435456)\n"
        "assert resource.getrlimit(resource.RLIMIT_FSIZE) == (65536, 65536)",
    )
    validate_math_input("x")
    assert [resource.getrlimit(limit) for limit in limits] == before


def test_wall_limit_kills_and_reaps_stuck_worker(
    monkeypatch: pytest.MonkeyPatch, workers: list[subprocess.Popen[bytes]]
) -> None:
    _replace_child_computation(monkeypatch, "import time\ntime.sleep(30)")
    started = time.monotonic()
    with pytest.raises(MathWorkerError, match="wall-clock"):
        validate_math_input("x")
    assert time.monotonic() - started < 6
    assert workers[0].returncode == -signal.SIGKILL
    with pytest.raises(ChildProcessError):
        os.waitpid(workers[0].pid, os.WNOHANG)


def test_cpu_limit_stops_pathological_work(
    monkeypatch: pytest.MonkeyPatch, workers: list[subprocess.Popen[bytes]]
) -> None:
    _replace_child_computation(monkeypatch, "while True:\n    pass")
    # Separate the OS CPU ceiling from the wall timeout so the latter cannot mask it.
    monkeypatch.setattr(math_worker, "WALL_SECONDS", 5)
    with pytest.raises(MathWorkerError, match="resource limits"):
        validate_math_input("e^(e^x)")
    assert workers[0].returncode in {-signal.SIGKILL, -signal.SIGXCPU}


def test_memory_limit_stops_pathological_allocation(
    monkeypatch: pytest.MonkeyPatch, workers: list[subprocess.Popen[bytes]]
) -> None:
    _replace_child_computation(monkeypatch, "bytearray(256 * 1024 * 1024)")
    with pytest.raises(MathWorkerError, match="resource limits"):
        validate_math_input("x")
    assert workers[0].returncode == 1


def test_combined_stdout_stderr_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    _replace_child_computation(
        monkeypatch,
        "import os\nos.write(1, b'x' * 32768)\nos.write(2, b'x' * 32768)\nos.write(1, b'x')",
    )
    with TemporaryFile() as output:
        monkeypatch.setattr(math_worker, "TemporaryFile", lambda: nullcontext(output))
        with pytest.raises(MathWorkerError, match="resource limits"):
            validate_math_input("x")
        assert os.fstat(output.fileno()).st_size == 65536


def test_symbolic_construction_never_runs_in_parent(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(_node: object) -> None:
        pytest.fail("symbolic construction ran in request process")

    monkeypatch.setattr(math_worker, "_build_sympy", fail)
    validate_math_input("x")


def test_invalid_input_does_not_start_a_worker(workers: list[subprocess.Popen[bytes]]) -> None:
    with pytest.raises(MathInputError):
        validate_math_input("__import__('os')")
    assert not workers


def test_start_failure_is_retryable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(math_worker, "_WORKER_COMMAND", ("/nonexistent/practiceloop-worker",))
    with pytest.raises(MathWorkerError, match="could not run"):
        validate_math_input("x")


def test_interrupted_parent_reaps_worker(
    monkeypatch: pytest.MonkeyPatch, workers: list[subprocess.Popen[bytes]]
) -> None:
    def interrupt(*_args: Any, **_kwargs: Any) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(Popen, "communicate", interrupt)
    with pytest.raises(KeyboardInterrupt):
        validate_math_input("x")
    assert workers[0].returncode is not None
