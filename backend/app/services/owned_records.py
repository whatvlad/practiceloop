"""Owner-scoped reads and writes of learning records.

The backend connects with a role that bypasses RLS, so these queries are the
ownership boundary: every statement filters on the verified user ID in SQL.
Another user's problem behaves exactly like a missing one (None), which the API
turns into the same 404. Functions never commit; the caller owns the transaction.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from psycopg import Connection
from psycopg.rows import dict_row

MAX_PAGE_SIZE = 50


@dataclass(frozen=True)
class ProblemRecord:
    id: UUID
    topic: str
    difficulty: int
    problem_latex: str
    created_at: datetime
    answer_revealed: bool
    solution_revealed: bool


@dataclass(frozen=True)
class AttemptRecord:
    id: UUID
    problem_id: UUID
    user_answer: str
    is_correct: bool | None
    created_at: datetime


@dataclass(frozen=True)
class PrivateSolution:
    """Backend-only; only the reveal functions below may hand parts of it out."""

    generator_version: str
    generator_data: Any
    answer_latex: str
    solution_steps: list[Any]


_PROBLEM_COLUMNS = """
    p.id, t.slug as topic, p.difficulty, p.problem_latex, p.created_at,
    p.answer_revealed, p.solution_revealed
"""


def ensure_profile(conn: Connection[Any], user_id: UUID) -> None:
    conn.execute(
        "insert into public.profiles(id) values (%s) on conflict (id) do nothing", (user_id,)
    )


def get_problem(conn: Connection[Any], user_id: UUID, problem_id: UUID) -> ProblemRecord | None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            f"select {_PROBLEM_COLUMNS} from public.problems p"  # noqa: S608 - constant columns
            " join public.topics t on t.id = p.topic_id"
            " where p.id = %s and p.user_id = %s",
            (problem_id, user_id),
        )
        row = cur.fetchone()
    return ProblemRecord(**row) if row else None


def list_problems(
    conn: Connection[Any],
    user_id: UUID,
    limit: int,
    before: tuple[datetime, UUID] | None = None,
) -> list[ProblemRecord]:
    """Newest first by (created_at, id); `before` is the last row of the previous page."""
    if not 1 <= limit <= MAX_PAGE_SIZE:
        raise ValueError("limit out of range")
    created_before, id_before = before if before else (None, None)
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            f"select {_PROBLEM_COLUMNS} from public.problems p"  # noqa: S608 - constant columns
            " join public.topics t on t.id = p.topic_id"
            " where p.user_id = %(user)s"
            " and (%(created)s::timestamptz is null"
            "      or (p.created_at, p.id) < (%(created)s::timestamptz, %(id)s::uuid))"
            " order by p.created_at desc, p.id desc limit %(limit)s",
            {"user": user_id, "created": created_before, "id": id_before, "limit": limit},
        )
        return [ProblemRecord(**row) for row in cur.fetchall()]


def last_attempt(conn: Connection[Any], user_id: UUID, problem_id: UUID) -> AttemptRecord | None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "select id, problem_id, user_answer, is_correct, created_at from public.attempts"
            " where problem_id = %s and user_id = %s"
            " order by created_at desc, id desc limit 1",
            (problem_id, user_id),
        )
        row = cur.fetchone()
    return AttemptRecord(**row) if row else None


def solution_for_check(
    conn: Connection[Any], user_id: UUID, problem_id: UUID
) -> PrivateSolution | None:
    """For checking an answer server-side; never returned to the browser."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "select s.generator_version, s.generator_data, s.answer_latex, s.solution_steps"
            " from private.problem_solutions s"
            " join public.problems p on p.id = s.problem_id"
            " where p.id = %s and p.user_id = %s",
            (problem_id, user_id),
        )
        row = cur.fetchone()
    return PrivateSolution(**row) if row else None


def insert_attempt(
    conn: Connection[Any],
    user_id: UUID,
    problem_id: UUID,
    user_answer: str,
    is_correct: bool | None,
) -> AttemptRecord | None:
    """None when the problem is missing or belongs to someone else; nothing is written."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "insert into public.attempts(problem_id, user_id, user_answer, is_correct)"
            " select p.id, p.user_id, %s, %s from public.problems p"
            " where p.id = %s and p.user_id = %s"
            " returning id, problem_id, user_answer, is_correct, created_at",
            (user_answer, is_correct, problem_id, user_id),
        )
        row = cur.fetchone()
    return AttemptRecord(**row) if row else None


def reveal_answer(conn: Connection[Any], user_id: UUID, problem_id: UUID) -> str | None:
    """Sets answer_revealed and reads the answer in one statement. Idempotent."""
    row = conn.execute(
        "with p as ("
        "  update public.problems set answer_revealed = true"
        "  where id = %s and user_id = %s returning id"
        ") select s.answer_latex from p join private.problem_solutions s on s.problem_id = p.id",
        (problem_id, user_id),
    ).fetchone()
    return str(row[0]) if row else None


def reveal_solution(conn: Connection[Any], user_id: UUID, problem_id: UUID) -> list[Any] | None:
    """The solution contains the answer, so both flags are set (ADR-004). Idempotent."""
    row = conn.execute(
        "with p as ("
        "  update public.problems set answer_revealed = true, solution_revealed = true"
        "  where id = %s and user_id = %s returning id"
        ") select s.solution_steps from p join private.problem_solutions s"
        " on s.problem_id = p.id",
        (problem_id, user_id),
    ).fetchone()
    return list(row[0]) if row else None
