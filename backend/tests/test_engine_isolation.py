"""#170: the new engine stays apart from the old generators and old saved problems.

Old saved problems keep opening from `problems.problem_latex` and replay through
the old generators exactly as they were saved. New-engine topics never import
or fall back to `app/generators`.
"""

import ast
import json
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest

from app.api import practice
from app.core.auth import VerifiedUser
from app.engine import practice as engine
from app.generators.core import replay
from app.services import archive
from app.services import owned_records as records

APP = Path(__file__).resolve().parents[1] / "app"
LEGACY = json.loads(
    (Path(__file__).parent / "fixtures" / "legacy_saved_problems.json").read_text(encoding="utf-8")
)


def imported_modules(path: Path) -> Iterator[str]:
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module
            yield from (f"{node.module}.{alias.name}" for alias in node.names)


def test_new_engine_never_imports_the_old_generators() -> None:
    sources = sorted((APP / "engine").rglob("*.py"))
    assert sources
    for path in sources:
        for module in imported_modules(path):
            assert module != "app.generators" and not module.startswith("app.generators."), (
                f"{path.relative_to(APP)} imports {module}"
            )


def test_loading_new_engine_topics_does_not_load_the_old_generators() -> None:
    script = (
        "import sys\n"
        "import app.engine.practice, app.engine.topics.catalogue\n"
        "assert not [m for m in sys.modules if m.split('.')[:2] == ['app', 'generators']]\n"
    )
    subprocess.run([sys.executable, "-c", script], check=True, cwd=APP.parent)  # noqa: S603


@pytest.mark.parametrize("slug", sorted(engine.ENGINE_TOPICS))
def test_new_engine_topics_are_served_only_by_the_new_engine(slug: str) -> None:
    for level in engine.levels(slug):
        issued = engine.issue(slug, level, seed=170)
        assert engine.is_engine_record(issued.record)
        assert engine.replay(issued.record).code == issued.record["code"]


def test_all_public_topics_use_the_engine_and_old_records_are_archives() -> None:
    assert set(practice.TOPICS) == set(engine.ENGINE_TOPICS)
    for item in LEGACY:
        # Even when a legacy version string overlaps, the missing code makes
        # the saved record an archive rather than a new-engine problem.
        assert not engine.is_engine_record(item["generator_data"])
        assert archive.is_archived(item["topic"], item["generator_data"])


@pytest.mark.parametrize("item", LEGACY, ids=lambda item: item["topic"])
def test_old_saved_problem_still_replays_as_saved(item: dict[str, Any]) -> None:
    exercise = replay(item["generator_data"])
    assert exercise.statement == item["problem_latex"]
    assert exercise.answer == item["answer_latex"]
    assert list(exercise.steps) == item["solution_steps"]


@pytest.mark.parametrize("item", LEGACY, ids=lambda item: item["topic"])
def test_old_saved_problem_opens_with_its_stored_statement(
    item: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    user, problem_id = uuid4(), uuid4()
    saved = records.ProblemRecord(
        problem_id,
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
        assert owner == user and read_only
        yield None

    def owned(found: Any) -> Any:
        return lambda _conn, owner, pid, *_: found if (owner, pid) == (user, problem_id) else None

    monkeypatch.setattr(practice, "transaction", transaction)
    monkeypatch.setattr(records, "get_problem", owned(saved))
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
    monkeypatch.setattr(records, "solution_for_check", owned(solution))
    monkeypatch.setattr(practice.shares, "active_share", lambda *_: None)

    body = practice.reopen(problem_id, VerifiedUser(user, None))
    assert body["problem"]["problemLatex"] == item["problem_latex"]
    assert body["problem"]["topic"] == item["topic"]
    assert body["answer"] == {"answerLatex": item["answer_latex"]}
    assert body["solution"]["steps"] == item["solution_steps"]
    assert "generator" not in json.dumps(body)
