"""Ownership against real Postgres, connected as the RLS-bypassing service_role.

Needs the disposable database that CI's "Database isolation" job prepares
(supabase/tests/auth_fixture.sql + migrations). Run with:
PRACTICELOOP_TEST_DATABASE_URL=postgresql://... python -m pytest -m db
Never point it at Supabase or shared data.
"""

import os
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from psycopg.types.json import Jsonb

from app.services import owned_records as records

pytestmark = pytest.mark.db


@dataclass
class World:
    conn: psycopg.Connection[Any]
    alice: UUID
    bob: UUID
    alice_problem: UUID
    bob_problem: UUID


def add_problem(conn: psycopg.Connection[Any], user: UUID, answer: str) -> UUID:
    problem = conn.execute(
        "insert into public.problems(user_id, topic_id, difficulty, problem_latex)"
        " select %s, id, 1, %s from public.topics where slug = 'basic-integrals'"
        " returning id",
        (user, f"\\int {answer}"),
    ).fetchone()
    assert problem is not None
    conn.execute(
        "insert into private.problem_solutions"
        "(problem_id, generator_version, generator_data, answer_latex, solution_steps)"
        " values (%s, 'basic-v1', %s, %s, %s)",
        (problem[0], Jsonb({"seed": 1}), answer, Jsonb([{"say": "step", "latex": answer}])),
    )
    return UUID(str(problem[0]))


@pytest.fixture
def world() -> Iterator[World]:
    url = os.environ.get("PRACTICELOOP_TEST_DATABASE_URL")
    if not url:
        pytest.fail("PRACTICELOOP_TEST_DATABASE_URL is required for -m db")
    with psycopg.connect(url) as conn:
        alice, bob = uuid4(), uuid4()
        conn.execute("insert into auth.users(id) values (%s), (%s)", (alice, bob))
        # Same privileges as the backend: bypasses RLS, so only the SQL filters protect.
        conn.execute("set local role service_role")
        world = World(
            conn, alice, bob, add_problem(conn, alice, "x^2"), add_problem(conn, bob, "x^3")
        )
        conn.execute(
            "insert into public.attempts(problem_id, user_id, user_answer, is_correct)"
            " values (%s, %s, 'x^3 + C', true)",
            (world.bob_problem, bob),
        )
        try:
            yield world
        finally:
            conn.rollback()


def flags(w: World, problem: UUID) -> tuple[bool, bool]:
    row = w.conn.execute(
        "select answer_revealed, solution_revealed from public.problems where id = %s", (problem,)
    ).fetchone()
    assert row is not None
    return row[0], row[1]


def test_service_role_really_bypasses_rls(world: World) -> None:
    count = world.conn.execute("select count(*) from public.problems").fetchone()
    assert count is not None and count[0] >= 2


def test_owner_reads_own_problem(world: World) -> None:
    problem = records.get_problem(world.conn, world.alice, world.alice_problem)
    assert problem is not None
    assert (problem.topic, problem.difficulty) == ("basic-integrals", 1)


def test_other_users_problem_is_indistinguishable_from_missing(world: World) -> None:
    assert records.get_problem(world.conn, world.alice, world.bob_problem) is None
    assert records.get_problem(world.conn, world.alice, uuid4()) is None


def test_history_lists_only_own_problems_with_stable_cursor(world: World) -> None:
    second = add_problem(world.conn, world.alice, "x^4")
    page = records.list_problems(world.conn, world.alice, limit=1)
    assert len(page) == 1
    rest = records.list_problems(
        world.conn, world.alice, limit=50, before=(page[0].created_at, page[0].id)
    )
    seen = {page[0].id} | {p.id for p in rest}
    assert seen == {world.alice_problem, second}
    assert world.bob_problem not in seen
    with pytest.raises(ValueError, match="limit"):
        records.list_problems(world.conn, world.alice, limit=51)


def test_attempts_are_scoped_to_owner(world: World) -> None:
    assert records.last_attempt(world.conn, world.alice, world.bob_problem) is None
    attempt = records.last_attempt(world.conn, world.bob, world.bob_problem)
    assert attempt is not None and attempt.is_correct is True


def test_cannot_attempt_someone_elses_problem(world: World) -> None:
    assert records.insert_attempt(world.conn, world.alice, world.bob_problem, "x", False) is None
    count = world.conn.execute(
        "select count(*) from public.attempts where user_id = %s", (world.alice,)
    ).fetchone()
    assert count == (0,)
    own = records.insert_attempt(world.conn, world.alice, world.alice_problem, "y", None)
    assert own is not None and own.is_correct is None


def test_private_solution_only_for_owner(world: World) -> None:
    assert records.solution_for_check(world.conn, world.alice, world.bob_problem) is None
    solution = records.solution_for_check(world.conn, world.bob, world.bob_problem)
    assert solution is not None and solution.answer_latex == "x^3"


def test_reveals_deny_other_users_and_change_nothing(world: World) -> None:
    assert records.reveal_answer(world.conn, world.alice, world.bob_problem) is None
    assert records.reveal_solution(world.conn, world.alice, world.bob_problem) is None
    assert flags(world, world.bob_problem) == (False, False)


def test_reveal_answer_sets_only_answer_flag_idempotently(world: World) -> None:
    for _ in range(2):
        assert records.reveal_answer(world.conn, world.alice, world.alice_problem) == "x^2"
    assert flags(world, world.alice_problem) == (True, False)


def test_reveal_solution_sets_both_flags(world: World) -> None:
    steps = records.reveal_solution(world.conn, world.alice, world.alice_problem)
    assert steps == [{"say": "step", "latex": "x^2"}]
    assert flags(world, world.alice_problem) == (True, True)


def test_ensure_profile_is_idempotent(world: World) -> None:
    records.ensure_profile(world.conn, world.alice)
    records.ensure_profile(world.conn, world.alice)
    count = world.conn.execute(
        "select count(*) from public.profiles where id = %s", (world.alice,)
    ).fetchone()
    assert count == (1,)
