"""Input instructions preserve public privacy and avoid request-time symbolic work."""

import sys
from contextlib import nullcontext
from datetime import UTC, datetime
from types import FrameType
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api import codes, practice
from app.core.auth import VerifiedUser, current_user
from app.engine import practice as engine
from app.engine.generators.probability import generators
from app.engine.opening import rebuild
from app.main import app
from app.services import math_worker
from app.services.owned_records import ProblemRecord


@pytest.mark.parametrize(
    "template",
    [
        "events-independence",
        "finite-support",
        "ci-lower",
        "ci-mean-z",
        "continuous-exponential-tail",
    ],
)
def test_public_and_saved_input_instructions_are_safe_without_building(template, monkeypatch):
    g = next(g for g in generators() if g.template == template)
    opened = rebuild(g.build(g.draw(200)).code)
    record = opened.problem.issued().record
    expected = engine.input_projection(record)
    calls = []

    def profile(frame: FrameType, event: str, _: object):
        if event == "call" and frame.f_globals.get("__name__", "").startswith("sympy"):
            calls.append(frame.f_code.co_name)

    monkeypatch.setattr(codes, "open_problem_code", lambda _: opened.model_dump_json().encode())
    codes._opened.cache_clear()
    codes.lookup_limit.reset()

    def forbidden(*args, **kwargs):
        pytest.fail("Input metadata tried to build a symbolic task")

    monkeypatch.setattr(type(g), "build", forbidden)
    previous = sys.getprofile()
    sys.setprofile(profile)
    try:
        public = codes.lookup(opened.problem.code)
        saved = practice._public_problem(
            ProblemRecord(
                uuid4(),
                opened.topic,
                opened.difficulty,
                opened.problem.statement,
                datetime.now(UTC),
                False,
                False,
                generator_data=record,
            ),
            None,
        )
    finally:
        sys.setprofile(previous)
    assert not calls
    assert public == {
        "problem": {
            "topic": opened.topic,
            "difficulty": opened.difficulty,
            "problemLatex": opened.problem.statement,
            **expected,
        }
    }
    assert saved.get("answerInput") == expected.get("answerInput")
    assert not ({"generator_data", "code", "answerLatex", "steps", "expected"} & saved.keys())
    if expected:
        assert set(expected["answerInput"]) <= {"kind", "maxBytes", "maxItems"}
    with TestClient(app) as client:
        response = client.get("/codes", params={"code": opened.problem.code})
        assert response.status_code == 200 and response.json() == public
    codes._opened.cache_clear()


@pytest.mark.parametrize("template", ["events-independence", "finite-support", "ci-lower"])
def test_wrong_kind_is_invalid_before_worker_admission(template, monkeypatch):
    g = next(g for g in generators() if g.template == template)
    task = g.build(g.draw(200))
    record = {"generator_version": g.version, "code": task.code}
    monkeypatch.setattr(
        math_worker, "_run_worker", lambda *args: pytest.fail("Invalid grammar admitted a worker")
    )
    assert math_worker.check_answer("999999", record).result == "invalid"


def test_attempt_request_cannot_select_its_answer_kind(monkeypatch):
    app.dependency_overrides[current_user] = lambda: VerifiedUser(uuid4(), None)
    monkeypatch.setattr(
        practice, "transaction", lambda *args: pytest.fail("Invalid request reached database")
    )
    try:
        with TestClient(app) as client:
            response = client.post(
                f"/problems/{uuid4()}/attempts",
                json={"answer": "true", "answerInput": {"kind": "boolean"}},
            )
            assert response.status_code == 422
    finally:
        app.dependency_overrides.pop(current_user)


def test_archived_records_have_no_new_input_projection():
    assert engine.input_projection({"family": "legacy", "coefficient": 2}) == {}
    assert engine.input_projection(None) == {}


@pytest.mark.parametrize(
    "template,descriptor",
    [
        ("events-independence", {"kind": "boolean", "maxBytes": 256}),
        ("finite-support", {"kind": "finite_set", "maxBytes": 256, "maxItems": 8}),
        ("ci-lower", {"kind": "interval", "maxBytes": 256}),
    ],
)
def test_first_generation_response_already_includes_safe_input_instructions(
    template, descriptor, monkeypatch
):
    g = next(g for g in generators() if g.template == template)
    opened = rebuild(g.build(g.draw(200)).code)
    issued = opened.problem.issued()
    saved = ProblemRecord(
        uuid4(),
        opened.topic,
        opened.difficulty,
        issued.statement,
        datetime.now(UTC),
        False,
        False,
        generator_data=issued.record,
    )
    monkeypatch.setattr(practice, "transaction", lambda _: nullcontext(object()))
    monkeypatch.setattr(practice.records, "ensure_profile", lambda *_: None)
    monkeypatch.setattr(practice.records, "recent_generator_data", lambda *_: [])
    monkeypatch.setattr(practice.records, "insert_problem", lambda *_: saved)
    monkeypatch.setattr(practice.idempotency, "claim", lambda *_: None)
    monkeypatch.setattr(practice.idempotency, "store", lambda *_: None)
    monkeypatch.setattr(engine, "issue", lambda *_args, **_kwargs: issued)
    practice.generation_limit.reset()
    app.dependency_overrides[current_user] = lambda: VerifiedUser(uuid4(), None)
    try:
        with TestClient(app) as client:
            response = client.post(
                "/problems",
                json={"topic": opened.topic, "difficulty": opened.difficulty},
                headers={"Idempotency-Key": str(uuid4())},
            )
        assert response.status_code == 201, response.text
        assert response.json()["problem"] == {
            "id": str(saved.id),
            "topic": opened.topic,
            "difficulty": opened.difficulty,
            "problemLatex": issued.statement,
            "answerInput": descriptor,
            "createdAt": practice._timestamp(saved.created_at),
            "answerRevealed": False,
            "solutionRevealed": False,
            "lastAttempt": None,
        }
    finally:
        app.dependency_overrides.pop(current_user)
