"""Problem sharing routes (#37) against real Postgres as the RLS-bypassing service role.

Same disposable database as test_practice_api.py; never point it at Supabase.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.api import practice, shares
from app.core import database
from app.core.auth import VerifiedUser, current_user, token_verifier
from app.generators.basic import replay_basic
from app.generators.core import catalogue
from app.main import app
from app.services import shares as share_service
from app.services.math_worker import AnswerCheck
from app.visuals.spec import build_visual

pytestmark = pytest.mark.db


class Users:
    def __init__(self) -> None:
        self.alice = uuid4()
        self.bob = uuid4()
        self.current: UUID | None = self.alice


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
    for limiter in (
        practice.generation_limit,
        practice.attempt_limit,
        practice.reveal_limit,
        shares.share_limit,
        shares.lookup_limit,
    ):
        limiter.reset()

    def signed_in() -> VerifiedUser:
        if people.current is None:
            raise AssertionError("a lookup asked for an account")
        return VerifiedUser(people.current, None)

    app.dependency_overrides[current_user] = signed_in
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


def generate(client: TestClient) -> dict[str, Any]:
    response = client.post(
        "/problems",
        json={"topic": "basic-integrals", "difficulty": 1},
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert response.status_code == 201, response.text
    return dict(response.json()["problem"])


def share(client: TestClient, problem_id: str, status: int = 201) -> dict[str, Any]:
    response = client.post(f"/problems/{problem_id}/share")
    assert response.status_code == status, response.text
    return dict(response.json()["share"])


def execute(url: str, sql: str, *args: Any) -> None:
    with psycopg.connect(url) as conn:
        conn.execute(sql, args)


def assert_unavailable(response: Any, status: int, code: str) -> None:
    assert response.status_code == status
    assert response.json() == {
        "error": {"code": code, "message": response.json()["error"]["message"], "retryable": False}
    }


def test_owner_shares_once_and_anyone_opens_it_by_link_or_code(
    client: TestClient, users: Users
) -> None:
    problem = generate(client)
    created = share(client, problem["id"])
    assert share_service.valid_token(created["token"])
    assert share_service.normalize_code(created["code"]) == created["code"]
    expires = datetime.fromisoformat(created["expiresAt"])
    assert abs(expires - datetime.now(UTC) - timedelta(days=90)) < timedelta(minutes=5)
    # A second click returns the same live share instead of a new link.
    assert share(client, problem["id"], status=200) == created
    assert client.get(f"/problems/{problem['id']}").json()["share"] == created

    users.current = None  # anonymous: a lookup never touches the account dependency
    expected = {
        "problem": {
            "topic": problem["topic"],
            "difficulty": problem["difficulty"],
            "problemLatex": problem["problemLatex"],
        }
    }
    code = created["code"]
    for path in (
        f"/shares/{created['token']}",
        f"/shares/code/{code}",
        f"/shares/code/{code[:4].lower()}-{code[4:].lower()}",
    ):
        response = client.get(path)
        assert response.status_code == 200, response.text
        assert response.json() == expected
        assert response.headers["Cache-Control"] == "no-store"


def test_shared_response_never_carries_answers_results_or_identities(
    client: TestClient, users: Users, url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # An indefinite record: a definite answer such as "2" also appears in its bounds.
    monkeypatch.setattr(
        practice,
        "catalogue",
        lambda *cell: tuple(
            item for item in catalogue(*cell) if item.record["generator_version"] != "definite-v1"
        ),
    )
    problem = generate(client)
    monkeypatch.setattr(
        practice, "shared_check", lambda *_: AnswerCheck("incorrect", False, "power_rule")
    )
    attempt = client.post(
        f"/problems/{problem['id']}/attempts",
        json={"answer": "x^7/7 + 13579"},
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert attempt.status_code == 201, attempt.text
    answer = client.post(f"/problems/{problem['id']}/reveal-answer").json()["answerLatex"]
    steps = client.post(f"/problems/{problem['id']}/reveal-solution").json()["steps"]
    created = share(client, problem["id"])

    users.current = None
    for path in (f"/shares/{created['token']}", f"/shares/code/{created['code']}"):
        body = client.get(path).text
        assert json.loads(body)["problem"].keys() == {"topic", "difficulty", "problemLatex"}
        for private in (
            "13579",
            answer,
            json.dumps(steps[-1]["latex"])[1:-1],
            problem["id"],
            str(users.alice),
            "incorrect",
            "power_rule",
            "createdAt",
            "attempt",
            "Revealed",
            "expiresAt",
        ):
            assert private not in body


def test_only_the_owner_can_share_or_revoke(client: TestClient, users: Users) -> None:
    problem = generate(client)
    created = share(client, problem["id"])
    users.current = users.bob
    assert client.post(f"/problems/{problem['id']}/share").status_code == 404
    assert client.post(f"/problems/{problem['id']}/share/revoke").status_code == 404
    assert client.post(f"/problems/{uuid4()}/share").status_code == 404
    # Bob holds the link, so he can read the statement, and nothing more.
    assert client.get(f"/shares/{created['token']}").status_code == 200


def test_revoking_ends_link_and_code_and_a_new_share_is_unrelated(
    client: TestClient, users: Users
) -> None:
    problem = generate(client)
    first = share(client, problem["id"])
    response = client.post(f"/problems/{problem['id']}/share/revoke")
    assert response.status_code == 200
    assert response.json() == {"share": None}
    assert client.post(f"/problems/{problem['id']}/share/revoke").status_code == 200
    assert client.get(f"/problems/{problem['id']}").json()["share"] is None

    users.current = None
    assert_unavailable(client.get(f"/shares/{first['token']}"), 410, "share_revoked")
    assert_unavailable(client.get(f"/shares/code/{first['code']}"), 410, "share_revoked")

    users.current = users.alice
    second = share(client, problem["id"])
    assert second["token"] != first["token"]
    assert second["code"] != first["code"]
    users.current = None
    assert client.get(f"/shares/{second['token']}").status_code == 200
    assert_unavailable(client.get(f"/shares/{first['token']}"), 410, "share_revoked")


def test_shares_expire_after_90_days(client: TestClient, users: Users, url: str) -> None:
    problem = generate(client)
    old = share(client, problem["id"])
    execute(
        url,
        "update private.problem_shares set created_at = now() - interval '91 days',"
        " expires_at = now() - interval '1 day' where token = %s",
        old["token"],
    )
    assert client.get(f"/problems/{problem['id']}").json()["share"] is None
    users.current = None
    assert_unavailable(client.get(f"/shares/{old['token']}"), 410, "share_expired")
    assert_unavailable(client.get(f"/shares/code/{old['code']}"), 410, "share_expired")
    users.current = users.alice
    fresh = share(client, problem["id"])
    assert fresh["token"] != old["token"]


def test_the_database_refuses_shares_longer_than_90_days(
    client: TestClient, users: Users, url: str
) -> None:
    problem = generate(client)
    created = share(client, problem["id"])
    with pytest.raises(psycopg.errors.CheckViolation):
        execute(
            url,
            "update private.problem_shares set expires_at = created_at + interval '91 days'"
            " where token = %s",
            created["token"],
        )


def test_invalid_and_missing_shares_are_distinct_and_empty(
    client: TestClient, users: Users
) -> None:
    users.current = None
    malformed = ["/shares/short", "/shares/" + "a" * 44]
    malformed += ["/shares/code/K7M2", "/shares/code/" + "A" * 99]
    for path in malformed:
        assert_unavailable(client.get(path), 400, "share_invalid")
    assert_unavailable(client.get("/shares/" + "a" * 43), 404, "share_not_found")
    assert_unavailable(client.get("/shares/code/K7M2-QX9P"), 404, "share_not_found")


def test_deleting_the_account_removes_its_shares(
    client: TestClient, users: Users, url: str
) -> None:
    problem = generate(client)
    created = share(client, problem["id"])
    execute(url, "delete from auth.users where id = %s", users.alice)
    users.current = None
    assert_unavailable(client.get(f"/shares/{created['token']}"), 404, "share_not_found")


def test_creating_and_revoking_shares_is_rate_limited(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    problem = generate(client)
    monkeypatch.setattr(shares.share_limit, "limit", 2)
    share(client, problem["id"])
    assert client.post(f"/problems/{problem['id']}/share/revoke").status_code == 200
    response = client.post(f"/problems/{problem['id']}/share")
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "rate_limited"
    assert int(response.headers["Retry-After"]) >= 1


def test_lookups_are_rate_limited_before_touching_the_database(
    client: TestClient, users: Users, monkeypatch: pytest.MonkeyPatch
) -> None:
    created = share(client, generate(client)["id"])
    users.current = None
    monkeypatch.setattr(shares.lookup_limit, "limit", 3)
    assert client.get(f"/shares/{created['token']}").status_code == 200
    assert client.get("/shares/code/bad").status_code == 400
    assert client.get(f"/shares/code/{created['code']}").status_code == 200
    for path in (f"/shares/{created['token']}", "/shares/code/bad"):
        response = client.get(path)
        assert response.status_code == 429
        assert int(response.headers["Retry-After"]) >= 1


def start_copy(client: TestClient, ref: dict[str, str], key: str | None = None) -> Any:
    return client.post(
        "/shares/practice", json=ref, headers={"Idempotency-Key": key or str(uuid4())}
    )


@pytest.mark.parametrize("topic", tuple(practice.TOPICS))
def test_copy_preserves_exact_trusted_content_for_every_topic(
    client: TestClient, users: Users, url: str, topic: str
) -> None:
    source = client.post(
        "/problems",
        json={"topic": topic, "difficulty": 3 if 3 in practice.TOPICS[topic].levels else 1},
        headers={"Idempotency-Key": str(uuid4())},
    ).json()["problem"]
    created = share(client, source["id"])
    users.current = users.bob
    response = start_copy(client, {"token": created["token"]})
    assert response.status_code == 201, response.text
    copied = response.json()["problem"]
    assert copied["id"] != source["id"]
    assert copied["answerRevealed"] is copied["solutionRevealed"] is False
    assert copied["lastAttempt"] is None
    assert copied["attemptCount"] == 0
    assert set(copied) == {
        "id",
        "topic",
        "difficulty",
        "problemLatex",
        "createdAt",
        "answerRevealed",
        "solutionRevealed",
        "lastAttempt",
        "attemptCount",
        "worksheetId",
    }
    for field in ("topic", "difficulty", "problemLatex"):
        assert copied[field] == source[field]
    with psycopg.connect(url) as conn:
        solutions = conn.execute(
            "select generator_version, generator_data, answer_latex, solution_steps"
            " from private.problem_solutions where problem_id in (%s, %s)",
            (source["id"], copied["id"]),
        ).fetchall()
        assert len(solutions) == 2 and solutions[0] == solutions[1]
        assert conn.execute(
            "select user_id from public.problems where id = %s", (copied["id"],)
        ).fetchone() == (users.bob,)
    assert client.get(f"/problems/{source['id']}").status_code == 404
    assert client.get(f"/problems/{copied['id']}").status_code == 200


def test_recipient_solves_reveals_and_reopens_without_changing_sender(
    client: TestClient, users: Users, monkeypatch: pytest.MonkeyPatch
) -> None:
    exercise = catalogue("basic-integrals", 4)[0]
    monkeypatch.setattr(practice, "_pick", lambda *_: exercise)
    source = client.post(
        "/problems",
        json={"topic": "basic-integrals", "difficulty": 4},
        headers={"Idempotency-Key": str(uuid4())},
    ).json()["problem"]
    created = share(client, source["id"])
    sender_before = client.get(f"/problems/{source['id']}").json()
    users.current = users.bob
    response = start_copy(client, {"code": created["code"].lower()})
    assert response.status_code == 201, response.text
    copied = response.json()["problem"]
    answer = str(replay_basic(dict(exercise.record)).antiderivative).replace("**", "^") + "+C"
    checked = client.post(
        f"/problems/{copied['id']}/attempts",
        json={"answer": answer},
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert checked.status_code == 201, checked.text
    assert checked.json()["attempt"]["result"] == "correct"
    assert client.post(f"/problems/{copied['id']}/reveal-answer").json() == {
        "answerLatex": exercise.answer
    }
    assert client.post(f"/problems/{copied['id']}/reveal-solution").json() == {
        "steps": list(exercise.steps),
        "visual": build_visual(exercise.record),
    }
    reopened = client.get(f"/problems/{copied['id']}").json()
    assert reopened["problem"]["lastAttempt"]["answer"] == answer
    assert reopened["problem"]["answerRevealed"] is True
    assert reopened["problem"]["solutionRevealed"] is True
    assert reopened["answer"]["answerLatex"] == exercise.answer
    assert reopened["share"] is None
    history = client.get("/problems").json()["items"]
    assert [item["id"] for item in history] == [copied["id"]]
    users.current = users.alice
    assert client.get(f"/problems/{source['id']}").json() == sender_before
    assert client.get(f"/problems/{copied['id']}").status_code == 404
    client.post(f"/problems/{source['id']}/share/revoke")
    users.current = users.bob
    assert client.get(f"/problems/{copied['id']}").json() == reopened


def test_copy_does_not_inherit_sender_attempts_or_reveals(
    client: TestClient, users: Users, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = generate(client)
    monkeypatch.setattr(practice, "shared_check", lambda *_: AnswerCheck("incorrect", False))
    client.post(
        f"/problems/{source['id']}/attempts",
        json={"answer": "13579"},
        headers={"Idempotency-Key": str(uuid4())},
    )
    client.post(f"/problems/{source['id']}/reveal-solution")
    created = share(client, source["id"])
    users.current = users.bob
    copied = start_copy(client, {"token": created["token"]}).json()["problem"]
    opened = client.get(f"/problems/{copied['id']}").json()
    assert opened == {"problem": copied, "share": None}
    assert "13579" not in str(opened)
    assert copied["lastAttempt"] is None and copied["attemptCount"] == 0
    assert not copied["answerRevealed"] and not copied["solutionRevealed"]


def test_concurrent_copy_retries_create_once_and_replay_after_revocation(
    client: TestClient, users: Users, url: str
) -> None:
    source = generate(client)
    created = share(client, source["id"])
    users.current = users.bob
    key = str(uuid4())
    ref = {"token": created["token"]}
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: start_copy(client, ref, key), range(2)))
    assert all(response.status_code == 201 for response in responses)
    assert responses[0].json() == responses[1].json()
    assert sum(r.headers.get("Idempotency-Replayed") == "true" for r in responses) == 1
    with psycopg.connect(url) as conn:
        assert conn.execute(
            "select count(*) from public.problems where user_id = %s", (users.bob,)
        ).fetchone() == (1,)
    users.current = users.alice
    client.post(f"/problems/{source['id']}/share/revoke")
    users.current = users.bob
    assert start_copy(client, ref, key).json() == responses[0].json()
    assert_unavailable(start_copy(client, ref), 410, "share_revoked")
    assert_unavailable(start_copy(client, {"code": created["code"]}), 410, "share_revoked")


def test_expired_missing_invalid_copies_and_untrusted_fields_write_nothing(
    client: TestClient, users: Users, url: str
) -> None:
    created = share(client, generate(client)["id"])
    execute(
        url,
        "update private.problem_shares set expires_at = now() where token = %s",
        created["token"],
    )
    users.current = users.bob
    for ref in ({"token": created["token"]}, {"code": created["code"]}):
        assert_unavailable(start_copy(client, ref), 410, "share_expired")
    assert_unavailable(start_copy(client, {"token": "a" * 43}), 404, "share_not_found")
    for ref in ({}, {"token": "short"}, {"code": "bad"}, {"token": "a" * 43, "code": "K7M2QX9P"}):
        assert_unavailable(start_copy(client, ref), 400, "share_invalid")
    assert start_copy(client, {"token": created["token"], "answerLatex": "x"}).status_code == 422
    with psycopg.connect(url) as conn:
        assert conn.execute(
            "select count(*) from public.problems where user_id = %s", (users.bob,)
        ).fetchone() == (0,)


def test_copy_requires_verified_authentication_and_idempotency_key(
    client: TestClient, users: Users, monkeypatch: pytest.MonkeyPatch
) -> None:
    created = share(client, generate(client)["id"])
    assert client.post("/shares/practice", json={"token": created["token"]}).status_code == 422
    app.dependency_overrides.pop(current_user)
    # Exercise the real missing-credentials dependency without requiring JWKS configuration.
    monkeypatch.setitem(app.dependency_overrides, token_verifier, lambda: None)
    assert start_copy(client, {"token": created["token"]}).status_code == 401
