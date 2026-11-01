"""#192: deploy builds complete private pools; requests only read rendered data."""

from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from types import FrameType
from typing import Any

import pytest

from app.api import practice, worksheets
from app.engine import catalogue
from app.engine import practice as engine
from app.engine.generators.catalogue import registry
from app.engine.topics.catalogue import topics
from app.services.worksheets import Picker


def test_every_declared_cell_is_full_and_every_code_replays_its_stored_fields() -> None:
    stored = catalogue.load()
    assert {(c.topic, c.level) for c in stored.cells} == {
        (slug, level) for slug, entry in topics().items() for level in entry.levels
    }
    for cell in stored.cells:
        assert len(cell.problems) == len({p.code for p in cell.problems}) == catalogue.POOL_SIZE
        for problem in cell.problems:
            issued = problem.issued()
            assert engine.public_replay(issued.record) == issued


def test_cold_symbolic_issuing_and_worksheet_preparation_call_no_sympy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Exercise the future served symbolic entries without migrating any public topic.
    monkeypatch.setattr(engine, "ENGINE_TOPICS", topics())
    monkeypatch.setattr(practice, "TOPICS", practice.listed_topics(engine.ENGINE_TOPICS))
    catalogue.load.cache_clear()
    calls: list[str] = []

    def profile(frame: FrameType, event: str, _arg: Any) -> None:
        if event == "call" and frame.f_globals.get("__name__", "").startswith("sympy"):
            calls.append(frame.f_code.co_name)

    previous = sys.getprofile()
    sys.setprofile(profile)
    try:
        pick = Picker(random.Random(192))  # noqa: S311 - repeatable test
        for slug, entry in engine.ENGINE_TOPICS.items():
            for level in entry.levels:
                issued = engine.issue(slug, level, seed=192)
                record = pick.pick(slug, level)
                assert record is not None
                statement, solution = worksheets._prepare(record)
                assert statement and solution.answer_latex and solution.solution_steps
                assert issued.record in [p.issued().record for p in engine.pool(slug, level)]
                assert practice.capacity(slug, level) == catalogue.POOL_SIZE
    finally:
        sys.setprofile(previous)
    assert calls == []


def test_missing_pool_fails_closed_instead_of_generating(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(catalogue, "CATALOGUE_PATH", tmp_path / "missing.json")
    catalogue.load.cache_clear()
    try:
        with pytest.raises(FileNotFoundError):
            engine.issue("combinations", 1)
    finally:
        catalogue.load.cache_clear()


@pytest.mark.parametrize("damage", ["missing", "duplicate", "short", "version", "code", "size"])
def test_incomplete_or_incompatible_catalogue_is_refused(
    damage: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = json.loads(catalogue.CATALOGUE_PATH.read_bytes())
    if damage == "missing":
        data["cells"].pop()
    elif damage == "duplicate":
        data["cells"].append(data["cells"][0])
    elif damage == "short":
        data["cells"][0]["problems"].pop()
    elif damage == "version":
        data["cells"][0]["problems"][0]["generator_version"] = "combinations-v1"
    elif damage == "code":
        data["cells"][0]["problems"][0]["code"] = "PFR-1-0000000000000000-00"
    else:
        data["pool_size"] = 1
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(catalogue, "CATALOGUE_PATH", path)
    catalogue.load.cache_clear()
    try:
        with pytest.raises(ValueError):
            catalogue.load()
    finally:
        catalogue.load.cache_clear()


@pytest.mark.parametrize("failure", ["reject", "duplicate"])
def test_unfillable_cell_aborts_with_a_bounded_candidate_count(
    failure: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = topics()["combinations"]
    task = entry.generate(1, 0, registry())
    calls = 0

    def generate(*_args: object) -> Any:
        nonlocal calls
        calls += 1
        if failure == "reject":
            raise ValueError("No candidate")
        return task

    monkeypatch.setattr(type(entry), "generate", generate)
    with pytest.raises(ValueError, match="Cannot fill catalogue pool: combinations level 1"):
        catalogue.build({entry.slug: entry}, pool_size=2)
    assert calls == 2 * catalogue.ATTEMPTS_PER_SLOT


def test_failed_build_leaves_the_previous_artifact_untouched(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "catalogue.json"
    path.write_text("previous", encoding="utf-8")

    def fail() -> Any:
        raise ValueError("Cannot fill catalogue pool")

    monkeypatch.setattr(catalogue, "build", fail)
    with pytest.raises(ValueError, match="Cannot fill"):
        catalogue.write(path)
    assert path.read_text(encoding="utf-8") == "previous"
    assert list(tmp_path.iterdir()) == [path]


def test_a_new_entry_is_built_without_a_second_registration() -> None:
    entry = replace(topics()["combinations"], slug="counting", title="Counting")
    result = catalogue.build({entry.slug: entry}, pool_size=2)
    assert [(c.topic, c.level, len(c.problems)) for c in result.cells] == [("counting", 1, 2)]


def test_picks_do_not_expose_mutable_cached_data() -> None:
    issued = engine.issue("combinations", 1, seed=0)
    issued.record["code"] = "changed"
    issued.steps[0]["say"] = "changed"
    again = engine.issue("combinations", 1, seed=0)
    assert again.record["code"] != "changed" and again.steps[0]["say"] != "changed"


def test_combinations_worksheet_picker_exhausts_the_pool_without_duplicate_codes() -> None:
    pick = Picker(random.Random(192))  # noqa: S311 - repeatable test
    records = [pick.pick("combinations", 1) for _ in range(catalogue.POOL_SIZE)]
    assert all(records)
    assert len({r["code"] for r in records if r}) == catalogue.POOL_SIZE
    assert pick.pick("combinations", 1) is None
    assert "combinations" in practice.mixed_topics("algebra", 1, worksheet=True)[0]


@pytest.mark.skipif(sys.platform != "linux", reason="Oracle release script targets Linux")
def test_catalogue_build_failure_stops_release_before_activation(tmp_path: Path) -> None:
    release = tmp_path / "releases" / "test192"
    (release / "backend").mkdir(parents=True)
    bins = release / ".venv" / "bin"
    bins.mkdir(parents=True)
    for name, body in {"python3.12": "exit 0", "pip": "exit 0", "python": "exit 23"}.items():
        path = bins / name
        path.write_text("#!/bin/sh\n" + body + "\n", encoding="utf-8")
        path.chmod(0o700)
    current = tmp_path / "current"
    current.write_text("previous release", encoding="utf-8")
    script = Path(__file__).resolve().parents[2] / "deploy" / "oracle" / "release.sh"
    bash = shutil.which("bash")
    assert bash is not None
    result = subprocess.run(  # noqa: S603 - fixed deploy script in a disposable directory
        [bash, str(script), "test192"],
        env={**os.environ, "APP_ROOT": str(tmp_path), "PATH": f"{bins}:{os.environ['PATH']}"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 23
    assert "Building verified engine catalogue" in result.stdout
    assert "Starting test192" not in result.stdout
    assert current.read_text(encoding="utf-8") == "previous release"
