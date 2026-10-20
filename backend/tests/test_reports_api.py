"""Problem reports (#38) against real Postgres as the RLS-bypassing service role.

Same disposable database as test_practice_api.py; never point it at Supabase.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.api import practice, reports
from app.core import database
from app.core.auth import VerifiedUser, current_user
from app.main import app

pytestmark = pytest.mark.db


class Users:
    def __init__(self) -> None:
        self.alice = uuid4()
        self.bob = uuid4()
        self.current: UUID = self.alice


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
    for limiter in (practice.generation_limit, reports.burst_limit, reports.hourly_limit):
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


def generate(client: TestClient) -> str:
    response = client.post(
        "/problems",
        json={"topic": "basic-integrals", "difficulty": 1},
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert response.status_code == 201, response.text
    return str(response.json()["problem"]["id"])


def stored(url: str, user: UUID) -> list[tuple[Any, ...]]:
    with psycopg.connect(url) as conn:
        return conn.execute(
            "select problem_id, category, comment from private.problem_reports"
            " where user_id = %s order by created_at",
            (user,),
        ).fetchall()


def test_owner_reports_a_problem_with_only_the_approved_fields(
    client: TestClient, users: Users, url: str
) -> None:
    problem = generate(client)
    response = client.post(
        f"/problems/{problem}/report", json={"category": "answer_check", "comment": "  1/2 = 2/4 "}
    )
    assert response.status_code == 201, response.text
    body = response.json()["report"]
    assert body.keys() == {"id", "category", "createdAt"}
    assert body["category"] == "answer_check"
    assert client.post(f"/problems/{problem}/report", json={"category": "other"}).status_code == 201
    assert (
        client.post(
            f"/problems/{problem}/report", json={"category": "display", "comment": "   "}
        ).json()["report"]["category"]
        == "display"
    )
    assert stored(url, users.alice) == [
        (UUID(problem), "answer_check", "1/2 = 2/4"),
        (UUID(problem), "other", None),
        (UUID(problem), "display", None),
    ]
    with psycopg.connect(url) as conn:
        columns = conn.execute(
            "select column_name from information_schema.columns"
            " where table_schema = 'private' and table_name = 'problem_reports' order by 1"
        ).fetchall()
    assert [c[0] for c in columns] == [
        "category",
        "comment",
        "created_at",
        "id",
        "problem_id",
        "user_id",
    ]


def test_nobody_reports_someone_elses_or_a_missing_problem(
    client: TestClient, users: Users, url: str
) -> None:
    problem = generate(client)
    users.current = users.bob
    assert client.post(f"/problems/{problem}/report", json={"category": "other"}).status_code == 404
    assert client.post(f"/problems/{uuid4()}/report", json={"category": "other"}).status_code == 404
    assert stored(url, users.bob) == []
    assert stored(url, users.alice) == []


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"category": "rude"},
        {"category": "other", "comment": "x" * 501},
        {"category": "other", "comment": "a\x00b"},
        {"category": "other", "email": "learner@example.invalid"},
        {"category": 3},
    ],
)
def test_invalid_reports_are_refused_without_echoing_them(
    client: TestClient, users: Users, url: str, body: dict[str, Any]
) -> None:
    problem = generate(client)
    response = client.post(f"/problems/{problem}/report", json=body)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"
    assert "example.invalid" not in response.text and "xxxx" not in response.text
    assert stored(url, users.alice) == []


def test_reports_are_rate_limited_per_user(client: TestClient, users: Users) -> None:
    problem = generate(client)
    for _ in range(reports.burst_limit.limit):
        assert (
            client.post(f"/problems/{problem}/report", json={"category": "other"}).status_code
            == 201
        )
    limited = client.post(f"/problems/{problem}/report", json={"category": "other"})
    assert limited.status_code == 429
    assert limited.json()["error"]["code"] == "rate_limited"
    assert int(limited.headers["Retry-After"]) >= 1
    users.current = users.bob
    assert client.post(f"/problems/{problem}/report", json={"category": "other"}).status_code == 404


def test_reports_go_with_the_account(client: TestClient, users: Users, url: str) -> None:
    problem = generate(client)
    assert client.post(f"/problems/{problem}/report", json={"category": "other"}).status_code == 201
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute("delete from auth.users where id = %s", (users.alice,))
    assert stored(url, users.alice) == []
