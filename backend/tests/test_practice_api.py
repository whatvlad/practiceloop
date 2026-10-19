"""Persisted practice routes (#10) against real Postgres as the RLS-bypassing service role.

Needs the disposable database CI's "Database isolation" job prepares (auth
fixture plus every migration). Run with:
PRACTICELOOP_TEST_DATABASE_URL=postgresql://... python -m pytest -m db
Never point it at Supabase or shared data: the tests commit and then delete users.
"""

from __future__ import annotations

import os
import threading
from collections.abc import Iterator
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.api import practice
from app.core import database
from app.core.auth import VerifiedUser, current_user
from app.generators.core import catalogue
from app.main import app
from app.services import idempotency
from app.services import owned_records as records
from app.services.idempotency import Scope, StoredResponse
from app.services.math_worker import AnswerCheck, MathCheckInconclusive, MathWorkerError

pytestmark = pytest.mark.db


class Users:
    def __init__(self) -> None:
        self.alice = uuid4()
        self.bob = uuid4()
        self.current = self.alice


@pytest.fixture
def url() -> str:
    value = os.environ.get("PRACTICELOOP_TEST_DATABASE_URL")
    if not value:
        pytest.fail("PRACTICELOOP_TEST_DATABASE_URL is required for -m db")
    return value


@pytest.fixture
def users(url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[Users]:
    people = Users()
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute("insert into auth.users(id) values (%s), (%s)", (people.alice, people.bob))
    monkeypatch.setenv("DATABASE_URL", url)
    database.close_pool()
    for limiter in (practice.generation_limit, practice.attempt_limit, practice.reveal_limit):
        limiter.reset()
    app.dependency_overrides[current_user] = lambda: VerifiedUser(people.current, None)
    try:
        yield people
    finally:
        app.dependency_overrides.pop(current_user, None)
        database.close_pool()
        with psycopg.connect(url, autocommit=True) as conn:
            conn.execute("delete from auth.users where id in (%s, %s)", (people.alice, people.bob))


@pytest.fixture
def client(users: Users) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def key() -> dict[str, str]:
    return {"Idempotency-Key": str(uuid4())}


def generate(client: TestClient, topic: str = "basic-integrals", level: int = 1) -> dict[str, Any]:
    response = client.post("/problems", json={"topic": topic, "difficulty": level}, headers=key())
    assert response.status_code == 201, response.text
    return dict(response.json()["problem"])


def rows(url: str, sql: str, *args: Any) -> list[tuple[Any, ...]]:
    with psycopg.connect(url) as conn:
        return conn.execute(sql, args).fetchall()


def stub_check(monkeypatch: pytest.MonkeyPatch, outcome: Any) -> None:
    def fake(_answer: str, _record: object) -> AnswerCheck:
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(practice, "shared_check", fake)


# Generation


def test_generation_persists_public_problem_and_private_solution_atomically(
    client: TestClient, users: Users, url: str
) -> None:
    problem = generate(client)
    assert set(problem) == {
        "id",
        "topic",
        "difficulty",
        "problemLatex",
        "createdAt",
        "answerRevealed",
        "solutionRevealed",
        "lastAttempt",
    }
    assert problem["createdAt"].endswith("Z")
    saved = rows(
        url,
        "select p.user_id, p.problem_latex, s.generator_version, s.answer_latex"
        " from public.problems p join private.problem_solutions s on s.problem_id = p.id"
        " where p.id = %s",
        problem["id"],
    )
    assert saved and saved[0][0] == users.alice and saved[0][1] == problem["problemLatex"]
    assert saved[0][2] == "basic-v1" and saved[0][3].endswith("+ C")
    assert rows(url, "select 1 from public.profiles where id = %s", users.alice)


def test_generation_response_never_carries_private_data(client: TestClient, url: str) -> None:
    for topic, level in (("basic-integrals", 2), ("substitution", 1)):
        problem = generate(client, topic, level)
        answer, data = rows(
            url,
            "select answer_latex, generator_data from private.problem_solutions"
            " where problem_id = %s",
            problem["id"],
        )[0]
        text = str(problem)
        assert answer not in text and "generator" not in text and "coefficient" not in text
        assert str(data) not in text


def test_no_repeat_within_the_latest_half_of_a_cell(client: TestClient, url: str) -> None:
    window = len(catalogue("basic-integrals", 1)) // 2 + 1
    ids = [generate(client)["id"] for _ in range(window)]
    data = rows(
        url,
        "select generator_data::text from private.problem_solutions where problem_id = any(%s)",
        ids,
    )
    assert len({row[0] for row in data}) == window


@pytest.mark.parametrize(
    "body",
    [
        {"topic": "integration-by-parts", "difficulty": 1},
        {"topic": "basic-integrals", "difficulty": 3},
        {"topic": "basic-integrals", "difficulty": "1"},
        {"topic": "basic-integrals", "difficulty": 1, "userId": "x"},
        {"topic": "basic-integrals"},
    ],
)
def test_unsupported_or_malformed_generation_is_422_and_writes_nothing(
    client: TestClient, url: str, users: Users, body: dict[str, Any]
) -> None:
    response = client.post("/problems", json=body, headers=key())
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"
    assert not rows(url, "select 1 from public.problems where user_id = %s", users.alice)


@pytest.mark.parametrize(
    "headers",
    [{}, {"Idempotency-Key": "not-a-uuid"}, {"Idempotency-Key": str(UUID(int=7, version=1))}],
)
def test_generation_requires_a_uuid4_idempotency_key(
    client: TestClient, headers: dict[str, str]
) -> None:
    response = client.post(
        "/problems", json={"topic": "basic-integrals", "difficulty": 1}, headers=headers
    )
    assert response.status_code == 422


def test_generation_replay_returns_the_same_problem_once(
    client: TestClient, users: Users, url: str
) -> None:
    headers = key()
    body = {"topic": "substitution", "difficulty": 2}
    first = client.post("/problems", json=body, headers=headers)
    again = client.post("/problems", json=body, headers=headers)
    assert first.status_code == again.status_code == 201
    assert again.json() == first.json()
    assert again.headers["idempotency-replayed"] == "true"
    assert "idempotency-replayed" not in first.headers
    assert rows(url, "select count(*) from public.problems where user_id = %s", users.alice) == [
        (1,)
    ]


def test_same_key_with_different_body_is_a_conflict(client: TestClient) -> None:
    headers = key()
    client.post("/problems", json={"topic": "substitution", "difficulty": 1}, headers=headers)
    response = client.post(
        "/problems", json={"topic": "substitution", "difficulty": 2}, headers=headers
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "idempotency_conflict"


def test_keys_are_scoped_per_user(client: TestClient, users: Users, url: str) -> None:
    headers = key()
    body = {"topic": "basic-integrals", "difficulty": 1}
    alice = client.post("/problems", json=body, headers=headers).json()
    users.current = users.bob
    bob = client.post("/problems", json=body, headers=headers)
    assert bob.status_code == 201 and "idempotency-replayed" not in bob.headers
    assert bob.json()["problem"]["id"] != alice["problem"]["id"]


def test_concurrent_claims_of_one_key_produce_one_mutation(url: str, users: Users) -> None:
    scope = Scope(users.alice, "POST", "/problems", uuid4(), "a" * 64)
    outcome: list[StoredResponse | None] = []
    with psycopg.connect(url) as first, psycopg.connect(url) as second:
        assert idempotency.claim(first, scope) is None
        waiter = threading.Thread(target=lambda: outcome.append(idempotency.claim(second, scope)))
        waiter.start()
        waiter.join(0.5)
        assert waiter.is_alive(), "second claim must wait for the first transaction"
        idempotency.store(first, scope, StoredResponse(201, {"problem": {"id": "x"}}))
        first.commit()
        waiter.join(5)
        second.commit()
    assert outcome == [StoredResponse(201, {"problem": {"id": "x"}})]


def test_database_failure_mid_generation_commits_nothing_and_retry_succeeds(
    client: TestClient, users: Users, url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken(*_args: Any, **_kwargs: Any) -> None:
        raise psycopg.OperationalError("connection lost")

    headers = key()
    body = {"topic": "basic-integrals", "difficulty": 1}
    with monkeypatch.context() as patch:
        patch.setattr(records, "insert_problem", broken)
        response = client.post("/problems", json=body, headers=headers)
    assert response.status_code == 503
    assert response.headers["retry-after"] == "5"
    assert response.json()["error"] == {
        "code": "database_unavailable",
        "message": response.json()["error"]["message"],
        "retryable": True,
    }
    assert not rows(url, "select 1 from private.idempotency_keys where user_id = %s", users.alice)
    retry = client.post("/problems", json=body, headers=headers)
    assert retry.status_code == 201 and "idempotency-replayed" not in retry.headers


def test_unreachable_database_is_retryable_503(
    users: Users, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://nobody@127.0.0.1:1/none?connect_timeout=1")
    monkeypatch.setattr(database, "POOL_TIMEOUT_SECONDS", 1.0)
    database.close_pool()
    with TestClient(app) as test_client:
        response = test_client.post(
            "/problems", json={"topic": "basic-integrals", "difficulty": 1}, headers=key()
        )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "database_unavailable"


def test_generation_is_rate_limited(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(practice.generation_limit, "limit", 2)
    generate(client)
    generate(client)
    response = client.post(
        "/problems", json={"topic": "basic-integrals", "difficulty": 1}, headers=key()
    )
    assert response.status_code == 429
    assert int(response.headers["retry-after"]) >= 1
    assert response.json()["error"]["retryable"] is True


# Attempts


def attempt(client: TestClient, problem_id: str, answer: str, headers: Any = None) -> Any:
    return client.post(
        f"/problems/{problem_id}/attempts", json={"answer": answer}, headers=headers or key()
    )


def primitive_of(url: str, problem_id: str) -> str:
    """The stored answer as learner input (tests only; the API never returns it unrevealed)."""
    from app.generators.core import replay

    (data,) = rows(
        url,
        "select generator_data from private.problem_solutions where problem_id = %s",
        problem_id,
    )[0]
    return str(replay(data).primitive).replace("**", "^")


def test_attempts_are_checked_by_the_real_worker_and_persisted(
    client: TestClient, users: Users, url: str
) -> None:
    problem = generate(client, "substitution", 1)
    primitive = primitive_of(url, problem["id"])
    cases = [
        (primitive + " + C", "correct", None, True, False),
        (primitive, "incorrect", "missing_constant", False, True),
        (primitive + " + x + C", "incorrect", None, False, False),
        ("x +* 2", "invalid", None, None, False),
    ]
    for answer, result, feedback, is_correct, omitted in cases:
        response = attempt(client, problem["id"], answer)
        assert response.status_code == 201, response.text
        body = response.json()["attempt"]
        assert (body["answer"], body["result"], body["feedbackCode"]) == (answer, result, feedback)
        saved = rows(
            url,
            "select user_id, is_correct, constant_omitted from public.attempts where id = %s",
            body["id"],
        )
        assert saved == [(users.alice, is_correct, omitted)]


def test_attempt_replay_and_conflict(
    client: TestClient, url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    stub_check(monkeypatch, AnswerCheck("correct"))
    problem = generate(client)
    headers = key()
    first = attempt(client, problem["id"], "x + C", headers)
    again = attempt(client, problem["id"], "x + C", headers)
    assert again.json() == first.json() and again.headers["idempotency-replayed"] == "true"
    assert attempt(client, problem["id"], "2x + C", headers).status_code == 409
    count = rows(url, "select count(*) from public.attempts where problem_id = %s", problem["id"])
    assert count == [(1,)]


@pytest.mark.parametrize(
    ("failure", "code", "retryable"),
    [
        (MathWorkerError("crashed"), "math_worker_unavailable", True),
        (MathCheckInconclusive("undecided"), "math_check_inconclusive", False),
    ],
)
def test_worker_failure_creates_no_attempt(
    client: TestClient,
    url: str,
    monkeypatch: pytest.MonkeyPatch,
    failure: Exception,
    code: str,
    retryable: bool,
) -> None:
    problem = generate(client)
    headers = key()
    with monkeypatch.context() as patch:
        stub_check(patch, failure)
        response = attempt(client, problem["id"], "x + C", headers)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == code
    assert response.json()["error"]["retryable"] is retryable
    assert not rows(url, "select 1 from public.attempts where problem_id = %s", problem["id"])
    stub_check(monkeypatch, AnswerCheck("correct"))
    assert attempt(client, problem["id"], "x + C", headers).status_code == 201


def test_busy_worker_slot_is_retryable(client: TestClient) -> None:
    problem = generate(client)
    assert practice.CHECK_SLOTS.acquire(blocking=False)
    try:
        response = attempt(client, problem["id"], "x + C")
    finally:
        practice.CHECK_SLOTS.release()
    assert response.status_code == 503
    assert response.headers["retry-after"] == "3"


@pytest.mark.parametrize("answer", ["", "   ", "x+" * 200 + "C"])
def test_empty_or_oversized_answers_are_rejected_before_an_attempt(
    client: TestClient, url: str, answer: str
) -> None:
    problem = generate(client)
    response = attempt(client, problem["id"], answer)
    assert response.status_code == 422
    assert not rows(url, "select 1 from public.attempts where problem_id = %s", problem["id"])


def test_other_users_problem_is_indistinguishable_from_missing(
    client: TestClient, users: Users, url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    stub_check(monkeypatch, AnswerCheck("correct"))
    problem = generate(client)
    users.current = users.bob
    for path in ("attempts", "reveal-answer", "reveal-solution"):
        body = {"answer": "x + C"} if path == "attempts" else None
        foreign = client.post(f"/problems/{problem['id']}/{path}", json=body, headers=key())
        missing = client.post(f"/problems/{uuid4()}/{path}", json=body, headers=key())
        assert foreign.status_code == missing.status_code == 404
        assert foreign.json() == missing.json()
    revealed = "select answer_revealed from public.problems where id = %s"
    assert rows(url, revealed, problem["id"]) == [(False,)]
    assert not rows(url, "select 1 from public.attempts where problem_id = %s", problem["id"])


def test_constant_flag_only_on_incorrect_attempts(url: str, users: Users) -> None:
    with psycopg.connect(url) as conn:
        conn.execute("set local role service_role")
        problem = conn.execute(
            "insert into public.problems(user_id, topic_id, difficulty, problem_latex)"
            " select %s, id, 1, 'p' from public.topics limit 1 returning id",
            (users.alice,),
        ).fetchone()
        assert problem is not None
        for is_correct in (True, None):
            with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
                records.insert_attempt(conn, users.alice, problem[0], "x", is_correct, True)
        conn.rollback()


# Reveals


def test_reveals_set_flags_return_payload_and_are_idempotent(client: TestClient, url: str) -> None:
    problem = generate(client)
    answer = client.post(f"/problems/{problem['id']}/reveal-answer")
    assert answer.status_code == 200 and answer.json()["answerLatex"].endswith("+ C")
    assert client.post(f"/problems/{problem['id']}/reveal-answer").json() == answer.json()
    flags = "select answer_revealed, solution_revealed from public.problems where id = %s"
    assert rows(url, flags, problem["id"]) == [(True, False)]
    solution = client.post(f"/problems/{problem['id']}/reveal-solution")
    steps = solution.json()["steps"]
    assert steps and all(set(step) == {"say", "latex"} for step in steps)
    assert rows(url, flags, problem["id"]) == [(True, True)]


def test_topics_lists_only_generated_cells(client: TestClient) -> None:
    items = client.get("/topics").json()["items"]
    assert [(item["slug"], item["availableDifficulties"]) for item in items] == [
        ("basic-integrals", [1, 2]),
        ("substitution", [1, 2]),
    ]
