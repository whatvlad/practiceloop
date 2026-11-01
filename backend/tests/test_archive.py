"""#190: old saved problems of a topic that moved to the new engine are a read-only archive.

Each legacy topic in tests/fixtures/legacy_saved_problems.json is moved to the new
engine for one test. Its saved problem must still open, reveal and print from the
stored rows alone, and a check must be `409 problem_archived`, never a 500.
"""

import json
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, NoReturn
from uuid import UUID, uuid4

import pytest

from app.api import practice, worksheets
from app.core.auth import VerifiedUser
from app.core.errors import ApiError
from app.engine import practice as engine
from app.services import archive, idempotency, shares
from app.services import owned_records as records
from app.services import worksheets as store

APP = Path(__file__).resolve().parents[1] / "app"
LEGACY = json.loads(
    (Path(__file__).parent / "fixtures" / "legacy_saved_problems.json").read_text(encoding="utf-8")
)


def legacy_code_is_never_run(*_: Any) -> NoReturn:
    raise AssertionError("an archived problem needs no old generator")


@pytest.fixture
def migrated(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """The legacy item's topic, as if its migration to the new engine had landed."""
    item: dict[str, Any] = request.param
    monkeypatch.setitem(engine.ENGINE_TOPICS, item["topic"], engine.ENGINE_TOPICS["combinations"])
    monkeypatch.setattr(practice, "solution_payload", legacy_code_is_never_run)
    monkeypatch.setattr(practice, "shared_check", legacy_code_is_never_run)
    monkeypatch.setattr(worksheets, "build_visual", legacy_code_is_never_run)
    return item


each_legacy_topic = pytest.mark.parametrize(
    "migrated", LEGACY, ids=lambda item: item["topic"], indirect=True
)


class Saved:
    """One user's saved legacy problem behind mocked owned-record queries."""

    def __init__(self, item: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
        self.user, self.problem_id = uuid4(), uuid4()
        problem = records.ProblemRecord(
            self.problem_id,
            item["topic"],
            item["difficulty"],
            item["problem_latex"],
            datetime(2026, 10, 1, tzinfo=UTC),
            answer_revealed=True,
            solution_revealed=True,
        )
        solution = records.PrivateSolution(
            item["generator_data"]["generator_version"],
            item["generator_data"],
            item["answer_latex"],
            item["solution_steps"],
        )

        @contextmanager
        def transaction(owner: UUID, read_only: bool = False) -> Iterator[None]:
            assert owner == self.user
            yield None

        def owned(found: Any) -> Any:
            return lambda _conn, owner, pid, *_: (
                found if (owner, pid) == (self.user, self.problem_id) else None
            )

        monkeypatch.setattr(practice, "transaction", transaction)
        monkeypatch.setattr(records, "get_problem", owned(problem))
        monkeypatch.setattr(records, "solution_for_check", owned(solution))
        monkeypatch.setattr(records, "attempt_summaries", lambda *_: {})
        monkeypatch.setattr(
            records,
            "previously_revealed",
            owned(
                {
                    "answer": {"answerLatex": item["answer_latex"]},
                    "solution": {"steps": item["solution_steps"]},
                }
            ),
        )
        monkeypatch.setattr(records, "reveal_solution", owned(item["solution_steps"]))
        monkeypatch.setattr(records, "insert_attempt", legacy_code_is_never_run)
        monkeypatch.setattr(idempotency, "lookup", lambda *_: None)
        monkeypatch.setattr(shares, "active_share", lambda *_: None)

    @property
    def owner(self) -> VerifiedUser:
        return VerifiedUser(self.user, None)


def test_the_archive_never_imports_the_old_generators() -> None:
    script = (
        "import sys\n"
        "import app.services.archive\n"
        "assert not [m for m in sys.modules if m.split('.')[:2] == ['app', 'generators']]\n"
    )
    subprocess.run([sys.executable, "-c", script], check=True, cwd=APP.parent)  # noqa: S603


def test_only_old_records_of_a_migrated_topic_are_archived() -> None:
    issued = engine.issue("combinations", engine.levels("combinations")[0], seed=190)
    assert not archive.is_archived("combinations", issued.record)
    for item in LEGACY:
        # Every legacy topic is still served by the old generators today.
        assert not archive.is_archived(item["topic"], item["generator_data"])


@each_legacy_topic
def test_an_archived_problem_opens_from_its_stored_rows(
    migrated: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    assert archive.is_archived(migrated["topic"], migrated["generator_data"])
    saved = Saved(migrated, monkeypatch)
    body = practice.reopen(saved.problem_id, saved.owner)
    assert body["problem"]["problemLatex"] == migrated["problem_latex"]
    assert body["problem"]["topic"] == migrated["topic"]
    assert body["answer"] == {"answerLatex": migrated["answer_latex"]}
    assert body["solution"] == {"steps": migrated["solution_steps"]}
    assert "generator" not in json.dumps(body)


@each_legacy_topic
def test_an_archived_problem_reveals_its_stored_solution(
    migrated: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    saved = Saved(migrated, monkeypatch)
    body = practice.reveal_solution(saved.problem_id, saved.owner)
    assert body == {"steps": migrated["solution_steps"]}


@each_legacy_topic
def test_checking_an_archived_problem_is_an_archived_error(
    migrated: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    practice.attempt_limit.reset()
    saved = Saved(migrated, monkeypatch)
    with pytest.raises(ApiError) as raised:
        practice.attempt(
            saved.problem_id, practice.AttemptBody(answer="1"), saved.owner, str(uuid4())
        )
    assert (raised.value.status_code, raised.value.code) == (409, "problem_archived")
    assert not raised.value.retryable


@each_legacy_topic
def test_an_archived_problem_prints_its_steps_without_a_graph(migrated: dict[str, Any]) -> None:
    item = store.PrintItem(
        0,
        migrated["topic"],
        migrated["difficulty"],
        migrated["problem_latex"],
        migrated["answer_latex"],
        migrated["solution_steps"],
        migrated["generator_data"],
    )
    steps, graph = worksheets._worked(item, deadline=float("inf"))
    assert [(step.say, step.latex) for step in steps] == [
        (step["say"], step["latex"]) for step in migrated["solution_steps"]
    ]
    assert graph == ""
