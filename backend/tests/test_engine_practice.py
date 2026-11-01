"""The new-engine practice adapter keeps private code and exact answers server-side."""

import importlib
import json
import subprocess
import sys
from uuid import uuid4

import pytest

from app.api import practice
from app.core.auth import VerifiedUser


def adapter():
    return importlib.import_module("app.services.engine_practice")


def test_combinations_topic_is_published_without_worksheet_support() -> None:
    body = practice.topics(VerifiedUser(uuid4(), None))
    topic = next(item for item in body["items"] if item["slug"] == "combinations")
    assert topic["area"] == "combinatorics"
    assert topic["availableDifficulties"] == [1]
    assert topic["worksheetCapacity"] == {"1": 0}


def test_combination_record_replays_exactly_and_checks_numeric_answers() -> None:
    module = adapter()
    statement, private = module.issue_combination(123)
    task = module.replay_combination(private.generator_data)
    assert private.generator_version == "combinations-v1"
    assert set(private.generator_data) == {"generator_version", "code"}
    assert task.code == private.generator_data["code"]
    assert statement.startswith(r"\binom{")
    assert private.answer_latex == task.answer.latex()
    assert private.solution_steps and all(
        set(step) == {"say", "latex"} for step in private.solution_steps
    )
    assert module.check_combination(private.answer_latex, private.generator_data) == "correct"
    assert (
        module.check_combination(str(int(private.answer_latex) + 1), private.generator_data)
        == "incorrect"
    )
    assert module.check_combination("x", private.generator_data) == "invalid"
    assert module.check_combination("1/0", private.generator_data) == "invalid"


@pytest.mark.parametrize(
    "record",
    [
        {},
        {"generator_version": "combinations-v1", "code": "bad"},
        {"generator_version": "combinations-v1", "code": "CMB-1-0000000000000123-17", "extra": 1},
        {"generator_version": "other-v1", "code": "CMB-1-0000000000000123-17"},
        {"generator_version": "combinations-v1", "code": "PFR-1-0000000000000000-29"},
    ],
)
def test_combination_replay_rejects_invalid_private_records(record: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        adapter().replay_combination(record)


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux resource limits")
def test_combinations_are_checked_in_the_real_limited_worker() -> None:
    from app.services.math_worker import check_answer

    _, private = adapter().issue_combination(123)
    assert check_answer(private.answer_latex, private.generator_data).result == "correct"
    assert (
        check_answer(str(int(private.answer_latex) + 1), private.generator_data).result
        == "incorrect"
    )
    assert check_answer("x", private.generator_data).result == "invalid"


def test_worker_dispatch_replays_the_private_code_before_checking() -> None:
    _, private = adapter().issue_combination(123)
    command = (
        "from app.services import math_worker as worker; "
        "worker._apply_limits = lambda: None; raise SystemExit(worker._check_child())"
    )
    for answer, record, expected in (
        (private.answer_latex, private.generator_data, b"correct"),
        ("x", private.generator_data, b"invalid"),
        ("1", {"generator_version": "combinations-v1", "code": "invalid"}, b"bad_record"),
    ):
        request = json.dumps({"answer": answer, "record": record}).encode()
        result = subprocess.run(  # noqa: S603 - fixed command, learner text passed on stdin
            (sys.executable, "-c", command),
            input=request,
            capture_output=True,
            timeout=10,
            check=False,
        )
        assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
        assert result.stdout == expected
