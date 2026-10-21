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
from app.services import idempotency, learning_stats
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
def client(users: Users, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    # Indefinite records unless a test pins definite-v1, so assertions stay deterministic.
    pin_version(monkeypatch, None)
    with TestClient(app) as test_client:
        yield test_client


def pin_version(monkeypatch: pytest.MonkeyPatch, version: str | None) -> None:
    """Cells mix definite and indefinite records (#36): pin one version, or None for indefinite."""

    def keep(record: dict[str, object]) -> bool:
        if version is None:
            return record["generator_version"] != "definite-v1"
        return record["generator_version"] == version

    def pinned(*cell: Any) -> tuple[Any, ...]:
        return tuple(item for item in catalogue(*cell) if keep(item.record))

    monkeypatch.setattr(practice, "catalogue", pinned)


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
    window = len(practice.catalogue("basic-integrals", 1)) // 2 + 1
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
        {"topic": "integration-by-parts", "difficulty": 4},
        {"topic": "integration-by-parts", "difficulty": 5},
        {"topic": "basic-integrals", "difficulty": 6},
        {"topic": "definite-integrals", "difficulty": 1},
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


def answer_of(url: str, problem_id: str) -> str:
    """A correct learner answer: the exact value, or the antiderivative plus C."""
    from app.generators.core import replay

    (data,) = rows(
        url,
        "select generator_data from private.problem_solutions where problem_id = %s",
        problem_id,
    )[0]
    exercise = replay(data)
    if exercise.value is not None:
        return str(exercise.value).replace("**", "^").replace("E", "e")
    return str(exercise.primitive).replace("**", "^").replace("Abs", "abs") + " + C"


def test_attempts_are_checked_by_the_real_worker_and_persisted(
    client: TestClient, users: Users, url: str
) -> None:
    problem = generate(client, "substitution", 1)
    primitive = primitive_of(url, problem["id"])
    ((data,),) = rows(
        url,
        "select generator_data from private.problem_solutions where problem_id = %s",
        problem["id"],
    )
    # #36: substitution-v1 sine and cosine records declare a lost trigonometric sign.
    sign = None if data["family"] == "exp" else "trig_sign"
    cases = [
        (primitive + " + C", "correct", None, True, False),
        (primitive, "incorrect", "missing_constant", False, True),
        (primitive + " + x + C", "incorrect", None, False, False),
        ("-(" + primitive + ") + C", "incorrect", sign, False, False),
        ("x +* 2", "invalid", None, None, False),
    ]
    for answer, result, feedback, is_correct, omitted in cases:
        response = attempt(client, problem["id"], answer)
        assert response.status_code == 201, response.text
        body = response.json()["attempt"]
        assert (body["answer"], body["result"], body["feedbackCode"]) == (answer, result, feedback)
        saved = rows(
            url,
            "select user_id, is_correct, constant_omitted, feedback_code"
            " from public.attempts where id = %s",
            body["id"],
        )
        code = None if omitted else feedback
        assert saved == [(users.alice, is_correct, omitted, code)]


@pytest.mark.parametrize(
    ("topic", "level", "version"),
    [
        ("basic-integrals", 3, "basic-v1"),
        ("substitution", 4, "substitution-v2"),
        ("integration-by-parts", 3, "parts-v1"),
        ("rational-functions", 5, "rational-v1"),
        ("trigonometric-integrals", 4, "trigonometric-v1"),
        ("integration-by-parts", 2, "definite-v1"),
        ("double-integrals", 3, "double-v1"),
        ("rational-functions", 3, "definite-v1"),
    ],
)
def test_higher_levels_persist_their_family_record_and_check_answers(
    client: TestClient,
    url: str,
    monkeypatch: pytest.MonkeyPatch,
    topic: str,
    level: int,
    version: str,
) -> None:
    pin_version(monkeypatch, version)
    problem = generate(client, topic, level)
    assert (problem["topic"], problem["difficulty"]) == (topic, level)
    assert rows(
        url,
        "select generator_version from private.problem_solutions where problem_id = %s",
        problem["id"],
    ) == [(version,)]
    response = attempt(client, problem["id"], answer_of(url, problem["id"]))
    assert response.status_code == 201, response.text
    assert response.json()["attempt"]["result"] == "correct"


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


# A NUL byte cannot be stored in PostgreSQL text: it must be a 422, not a 500 (#13).
@pytest.mark.parametrize("answer", ["", "   ", "x+" * 200 + "C", "x\x00+C"])
def test_empty_oversized_or_nul_answers_are_rejected_before_an_attempt(
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
        ("basic-integrals", [1, 2, 3, 4, 5]),
        ("substitution", [1, 2, 3, 4, 5]),
        ("integration-by-parts", [1, 2, 3]),
        ("rational-functions", [1, 2, 3, 4, 5]),
        ("trigonometric-integrals", [1, 2, 3, 4, 5]),
        ("double-integrals", [1, 2, 3, 4, 5]),
        ("derivatives", [1, 2, 3, 4, 5]),
    ]


def test_topics_publish_the_fixed_mixed_practice_weights(client: TestClient) -> None:
    areas = client.get("/topics").json()["areas"]
    assert areas[0] == {
        "slug": "integrals",
        "name": "Integrals",
        "mixed": {
            "availableDifficulties": [1, 2, 3, 4, 5],
            "weights": {
                "basic-integrals": 1,
                "substitution": 2,
                "integration-by-parts": 2,
                "rational-functions": 2,
                "trigonometric-integrals": 2,
                "double-integrals": 2,
            },
        },
    }


def test_topics_are_grouped_by_area(client: TestClient) -> None:
    body = client.get("/topics").json()
    areas = [area["slug"] for area in body["areas"]]
    assert set(areas) <= set(practice.AREAS) and "integrals" in areas
    # Every topic names an area the response lists, and an area appears only with topics.
    assert {item["area"] for item in body["items"]} == set(areas)
    for item in body["items"]:
        assert item["area"] == practice.TOPICS[item["slug"]].area


def test_an_area_with_one_topic_offers_no_mixed_practice(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    topics = dict(practice.TOPICS)
    topics["derivatives"] = practice.Topic("Derivatives", "derivatives", (1, 2), 1)
    monkeypatch.setattr(practice, "TOPICS", topics)
    areas = {area["slug"]: area for area in client.get("/topics").json()["areas"]}
    assert areas["derivatives"] == {"slug": "derivatives", "name": "Derivatives", "mixed": None}
    response = client.post(
        "/problems",
        json={"topic": "mixed", "area": "derivatives", "difficulty": 1},
        headers=key(),
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    ("level", "slugs", "weights"),
    [
        (
            level,
            [s for s, t in practice.TOPICS.items() if level in t.levels and t.area == "integrals"],
            [
                t.mixed_weight
                for t in practice.TOPICS.values()
                if level in t.levels and t.area == "integrals"
            ],
        )
        # Only the topics that offer a level take part in its draw.
        for level in (1, 4)
    ],
)
@pytest.mark.parametrize("area", [None, "integrals"])
def test_mixed_practice_draws_a_topic_with_the_published_weights(
    client: TestClient, url: str, monkeypatch: pytest.MonkeyPatch, level, slugs, weights, area
) -> None:
    calls = []

    def choices(population, weights):
        calls.append((population, weights))
        return [population[-1]]

    monkeypatch.setattr(practice._RANDOM, "choices", choices)
    body = {"topic": "mixed", "difficulty": level, **({"area": area} if area else {})}
    response = client.post("/problems", json=body, headers=key())
    assert response.status_code == 201, response.text
    problem = response.json()["problem"]
    assert calls == [(slugs, weights)]
    # The saved problem belongs to the drawn topic, so history and statistics stay per topic.
    assert (problem["topic"], problem["difficulty"]) == (slugs[-1], level)
    assert rows(
        url,
        "select t.slug from public.problems p join public.topics t on t.id = p.topic_id"
        " where p.id = %s",
        problem["id"],
    ) == [(slugs[-1],)]


def test_mixed_practice_stays_within_the_chosen_area(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = []

    def choices(population, weights):
        calls.append(population)
        return [population[0]]

    topics = dict(practice.TOPICS)
    topics["derivatives"] = practice.Topic("Derivatives", "derivatives", (3,), 1)
    topics["partial-derivatives"] = practice.Topic("Partial derivatives", "derivatives", (3,), 1)
    monkeypatch.setattr(practice, "TOPICS", topics)
    monkeypatch.setattr(practice._RANDOM, "choices", choices)
    generate(client, "mixed", 3)
    assert set(calls[0]) == set(practice.area_topics("integrals"))
    # The draw is all that is checked here; these topics have no catalogue in this test.
    monkeypatch.setattr(practice, "_pick", lambda *_: (_ for _ in ()).throw(LookupError))
    with pytest.raises(LookupError):
        client.post(
            "/problems",
            json={"topic": "mixed", "area": "derivatives", "difficulty": 3},
            headers=key(),
        )
    assert calls[1] == ["derivatives", "partial-derivatives"]


@pytest.mark.parametrize(
    "body",
    [
        {"topic": "mixed", "area": "geometry", "difficulty": 1},
        {"topic": "basic-integrals", "area": "integrals", "difficulty": 1},
        {"topic": "mixed", "area": "", "difficulty": 1},
    ],
)
def test_generation_rejects_unknown_or_misplaced_areas(client: TestClient, body) -> None:
    assert client.post("/problems", json=body, headers=key()).status_code == 422


def test_mixed_practice_reaches_every_offered_topic(client: TestClient) -> None:
    seen = {generate(client, "mixed", 3)["topic"] for _ in range(25)}
    assert seen <= set(practice.area_topics("integrals")) and len(seen) >= 3


@pytest.mark.parametrize("level", [0, 6])
def test_mixed_practice_rejects_unknown_levels(client: TestClient, level: int) -> None:
    response = client.post("/problems", json={"topic": "mixed", "difficulty": level}, headers=key())
    assert response.status_code == 422


# History, persisted reopen and profile (#12)


def test_empty_history_and_profile_need_no_existing_profile(client: TestClient) -> None:
    assert client.get("/problems").json() == {"items": [], "nextCursor": None}
    assert client.get("/profile").json()["counts"] == {"generated": 0, "attempted": 0, "correct": 0}


def test_history_reopen_and_profile_are_owner_scoped(
    client: TestClient, users: Users, monkeypatch: pytest.MonkeyPatch
) -> None:
    stub_check(monkeypatch, AnswerCheck("correct"))
    problem = generate(client)
    attempt(client, problem["id"], "x+C")
    client.post(f"/problems/{problem['id']}/reveal-solution")
    users.current = users.bob
    assert client.get("/problems").json() == {"items": [], "nextCursor": None}
    foreign = client.get(f"/problems/{problem['id']}")
    missing = client.get(f"/problems/{uuid4()}")
    assert foreign.status_code == missing.status_code == 404
    assert foreign.json() == missing.json()
    profile = client.get("/profile").json()
    assert profile["account"]["id"] == str(users.bob)
    assert profile["counts"] == {"generated": 0, "attempted": 0, "correct": 0}


def test_reopen_restores_latest_attempt_and_only_previously_revealed_content(
    client: TestClient, url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    problem = generate(client)
    path = f"/problems/{problem['id']}"
    unrevealed = client.get(path).json()
    assert set(unrevealed) == {"problem", "share"}
    assert unrevealed["share"] is None
    assert unrevealed["problem"]["lastAttempt"] is None
    assert unrevealed["problem"]["attemptCount"] == 0
    stub_check(monkeypatch, AnswerCheck("incorrect", missing_constant=True))
    attempt(client, problem["id"], "x")
    state = client.get(path).json()
    assert state["problem"]["lastAttempt"] == {
        "answer": "x",
        "result": "incorrect",
        "feedbackCode": "missing_constant",
    }
    assert state["problem"]["attemptCount"] == 1
    stub_check(monkeypatch, AnswerCheck("incorrect", feedback_code="power_rule"))
    attempt(client, problem["id"], "x^2")
    assert client.get(path).json()["problem"]["lastAttempt"]["feedbackCode"] == "power_rule"
    answer = client.post(path + "/reveal-answer").json()
    assert client.get(path).json()["answer"] == answer
    assert "solution" not in client.get(path).json()
    solution = client.post(path + "/reveal-solution").json()
    reopened = client.get(path).json()
    assert reopened["answer"] == answer and reopened["solution"] == solution
    history = client.get("/problems").json()["items"][0]
    assert history["answerRevealed"] and history["solutionRevealed"]
    assert "answer" not in history and "solution" not in history
    assert "generator" not in str(reopened)
    assert rows(
        url,
        "select answer_revealed, solution_revealed from public.problems where id=%s",
        problem["id"],
    ) == [(True, True)]


def test_profile_counts_distinct_problems_and_remembers_a_correct_attempt(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    one, two, _untouched = generate(client), generate(client), generate(client)
    stub_check(monkeypatch, AnswerCheck("invalid"))
    attempt(client, one["id"], "x+*")
    assert client.get("/profile").json()["counts"] == {"generated": 3, "attempted": 1, "correct": 0}
    stub_check(monkeypatch, AnswerCheck("correct"))
    headers = key()
    attempt(client, two["id"], "x+C", headers)
    attempt(client, two["id"], "x+C", headers)
    stub_check(monkeypatch, AnswerCheck("incorrect"))
    attempt(client, two["id"], "x+1")
    assert client.get("/profile").json()["counts"] == {"generated": 3, "attempted": 2, "correct": 1}
    history = client.get("/problems").json()["items"]
    assert next(p for p in history if p["id"] == two["id"])["attemptCount"] == 2


def test_history_cursor_orders_ties_and_excludes_newer_insertions(
    client: TestClient, users: Users, url: str
) -> None:
    ids = [generate(client)["id"] for _ in range(4)]
    with psycopg.connect(url) as conn:
        conn.execute(
            "update public.problems set created_at='2026-01-01T00:00:00Z' where user_id=%s",
            (users.alice,),
        )
    first = client.get("/problems?limit=2").json()
    assert len(first["items"]) == 2 and first["nextCursor"]
    fresh = generate(client)["id"]
    second = client.get("/problems", params={"limit": 2, "cursor": first["nextCursor"]}).json()
    assert second["nextCursor"] is None
    seen = [p["id"] for p in first["items"] + second["items"]]
    assert seen == sorted(ids, reverse=True)
    assert fresh not in seen
    assert client.get("/problems").json()["items"][0]["id"] == fresh


@pytest.mark.parametrize(
    "query", ["limit=0", "limit=51", "limit=x", "cursor=bad!", "cursor=", "cursor=" + "x" * 257]
)
def test_history_rejects_malformed_pagination(client: TestClient, query: str) -> None:
    assert client.get("/problems?" + query).status_code == 422


def test_history_maximum_page_uses_one_extra_row_to_detect_more(
    client: TestClient, users: Users, url: str
) -> None:
    rows(
        url,
        "insert into public.problems(user_id, topic_id, difficulty, problem_latex)"
        " select %s, t.id, 1, 'statement' from public.topics t cross join generate_series(1,51)"
        " where t.slug='basic-integrals' returning id",
        users.alice,
    )
    page = client.get("/problems?limit=50").json()
    assert len(page["items"]) == 50 and page["nextCursor"]
    last = client.get("/problems", params={"limit": 50, "cursor": page["nextCursor"]}).json()
    assert len(last["items"]) == 1 and last["nextCursor"] is None


def test_history_reads_require_authentication_before_database_access(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.core.auth import token_verifier

    def no_database() -> Any:
        raise AssertionError("Unauthenticated request reached the database")

    monkeypatch.setattr(practice, "transaction", no_database)
    app.dependency_overrides.pop(current_user)
    app.dependency_overrides[token_verifier] = lambda: object()
    try:
        for path in ("/problems", f"/problems/{uuid4()}", "/profile", "/statistics"):
            assert client.get(path).status_code == 401
    finally:
        app.dependency_overrides.pop(token_verifier)


# Account completion (#35)


def test_private_omission_metrics_exclude_invalid_and_keep_each_checked_attempt(
    client, users, url, monkeypatch
):
    problem = generate(client)
    for outcome in (
        AnswerCheck("incorrect", True),
        AnswerCheck("correct", False),
        AnswerCheck("invalid", False),
    ):
        stub_check(monkeypatch, outcome)
        assert (
            client.post(
                f"/problems/{problem['id']}/attempts",
                json={"answer": "x", "elapsedMs": 1234},
                headers=key(),
            ).status_code
            == 201
        )
    stats = client.get("/statistics").json()
    assert (stats["checkedAttempts"], stats["omitted"], stats["rate"]) == (2, 1, 0.5)
    assert stats["byTopicDifficulty"] == [
        {
            "topic": "basic-integrals",
            "difficulty": 1,
            "checkedAttempts": 2,
            "omitted": 1,
            "rate": 0.5,
        }
    ]
    assert len(stats["weekly"]) == 8
    assert sum(w["omitted"] for w in stats["weekly"]) == 1
    assert rows(
        url, "select distinct elapsed_ms from public.attempts where user_id = %s", users.alice
    ) == [(1234,)]
    users.current = users.bob
    other = client.get("/statistics").json()
    assert other["checkedAttempts"] == 0 and other["omitted"] == 0 and other["rate"] is None
    assert other["byTopicDifficulty"] == []
    assert all(w["rate"] is None for w in other["weekly"])


def test_statistics_all_time_and_eight_week_trend_have_distinct_windows(client, users, url):
    problem = generate(client)
    with psycopg.connect(url) as conn:
        conn.execute(
            "insert into public.attempts(problem_id,user_id,user_answer,is_correct,"
            "constant_omitted,created_at) values (%s,%s,'x',false,true,"
            "now()-interval '10 weeks')",
            (problem["id"], users.alice),
        )
    stats = client.get("/statistics").json()
    assert stats["omitted"] == 1
    assert sum(w["omitted"] for w in stats["weekly"]) == 0


def test_omission_metrics_exclude_definite_integrals(client, monkeypatch):
    # A definite answer never takes a constant, so it cannot count as checked for omission.
    pin_version(monkeypatch, "definite-v1")
    problem = generate(client)
    stub_check(monkeypatch, AnswerCheck("incorrect"))
    response = client.post(
        f"/problems/{problem['id']}/attempts", json={"answer": "2"}, headers=key()
    )
    assert response.status_code == 201
    stats = client.get("/statistics").json()
    assert (stats["checkedAttempts"], stats["byTopicDifficulty"]) == (0, [])
    assert sum(w["checkedAttempts"] for w in stats["weekly"]) == 0


@pytest.mark.parametrize("version", learning_stats.CONSTANT_FREE_VERSIONS)
def test_omission_metrics_exclude_every_constant_free_version(client, url, version):
    # ADR-005: derivatives and multiple integrals never take a constant either.
    problem = generate(client)
    with psycopg.connect(url) as conn:
        conn.execute(
            "update private.problem_solutions set generator_version = %s where problem_id = %s",
            (version, problem["id"]),
        )
        conn.execute(
            "insert into public.attempts(problem_id,user_id,user_answer,is_correct,"
            "constant_omitted) select id, user_id, 'x', false, true from public.problems"
            " where id = %s",
            (problem["id"],),
        )
    stats = client.get("/statistics").json()
    assert (stats["checkedAttempts"], stats["byTopicDifficulty"]) == (0, [])


def test_optional_name_is_owner_scoped_editable_and_removable(client, users):
    assert client.get("/profile").json()["account"]["name"] is None
    assert client.post("/profile", json={"name": "  Ada  "}).json() == {"name": "Ada"}
    assert client.get("/profile").json()["account"]["name"] == "Ada"
    users.current = users.bob
    assert client.get("/profile").json()["account"]["name"] is None
    assert (
        client.post("/profile", json={"name": "B", "userId": str(users.alice)}).status_code == 422
    )
    users.current = users.alice
    assert client.post("/profile", json={"name": None}).status_code == 200
    assert client.get("/profile").json()["account"]["name"] is None
    assert client.post("/profile", json={"name": "x" * 81}).status_code == 422
    assert client.post("/profile", json={"name": "A\x00da"}).status_code == 422


def test_hard_delete_cascades_all_learning_data_and_old_identity_is_denied(
    client, users, url, monkeypatch
):
    own = generate(client)
    users.current = users.bob
    other = generate(client)
    users.current = users.alice
    with psycopg.connect(url) as conn:
        conn.execute(
            "insert into public.attempts(problem_id,user_id,user_answer,is_correct)"
            " values (%s,%s,'private answer',false)",
            (own["id"], users.alice),
        )

    def remove(identity):
        assert identity == users.alice
        with psycopg.connect(url) as conn:
            conn.execute("delete from auth.users where id = %s", (identity,))

    monkeypatch.setattr(practice, "delete_user", remove)
    assert client.post("/account/delete", json={"confirmation": "DELETE"}).status_code == 200
    for table, column in (
        ("public.profiles", "id"),
        ("public.problems", "user_id"),
        ("public.attempts", "user_id"),
        ("private.idempotency_keys", "user_id"),
    ):
        assert not rows(url, f"select 1 from {table} where {column} = %s", users.alice)  # noqa: S608 -- fixed test constants
    assert not rows(url, "select 1 from private.problem_solutions where problem_id = %s", own["id"])
    for path in ("/profile", "/statistics", "/problems", f"/problems/{own['id']}"):
        assert client.get(path).status_code == 401
    assert (
        client.post(
            "/problems", json={"topic": "basic-integrals", "difficulty": 1}, headers=key()
        ).status_code
        == 401
    )
    assert client.post("/profile", json={"name": "recreate"}).status_code == 401
    users.current = users.bob
    assert client.get(f"/problems/{other['id']}").status_code == 200
