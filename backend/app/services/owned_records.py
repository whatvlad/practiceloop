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
from psycopg.types.json import Jsonb

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
    constant_omitted: bool
    created_at: datetime
    feedback_code: str | None = None


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


def insert_problem(
    conn: Connection[Any],
    user_id: UUID,
    topic: str,
    difficulty: int,
    problem_latex: str,
    solution: PrivateSolution,
) -> ProblemRecord:
    """The public problem and its private solution; the caller's transaction makes it atomic."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "insert into public.problems(user_id, topic_id, difficulty, problem_latex)"
            " select %s, t.id, %s, %s from public.topics t where t.slug = %s"
            " returning id, difficulty, problem_latex, created_at,"
            " answer_revealed, solution_revealed",
            (user_id, difficulty, problem_latex, topic),
        )
        row = cur.fetchone()
    if row is None:
        raise LookupError(f"Unknown topic {topic!r}")
    conn.execute(
        "insert into private.problem_solutions"
        "(problem_id, generator_version, generator_data, answer_latex, solution_steps)"
        " values (%s, %s, %s, %s, %s)",
        (
            row["id"],
            solution.generator_version,
            Jsonb(solution.generator_data),
            solution.answer_latex,
            Jsonb(solution.solution_steps),
        ),
    )
    return ProblemRecord(topic=topic, **row)


def recent_generator_data(
    conn: Connection[Any], user_id: UUID, topic: str, difficulty: int, limit: int
) -> list[Any]:
    """Records behind the user's latest problems in one topic and level, newest first."""
    rows = conn.execute(
        "select s.generator_data from public.problems p"
        " join public.topics t on t.id = p.topic_id"
        " join private.problem_solutions s on s.problem_id = p.id"
        " where p.user_id = %s and t.slug = %s and p.difficulty = %s"
        " order by p.created_at desc, p.id desc limit %s",
        (user_id, topic, difficulty, limit),
    ).fetchall()
    return [row[0] for row in rows]


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
    *,
    include_next: bool = False,
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
            {
                "user": user_id,
                "created": created_before,
                "id": id_before,
                "limit": limit + int(include_next),
            },
        )
        return [ProblemRecord(**row) for row in cur.fetchall()]


def attempt_summaries(
    conn: Connection[Any], user_id: UUID, problem_ids: list[UUID]
) -> dict[UUID, tuple[AttemptRecord, int]]:
    """Latest attempt and total count, in one bounded query for the owner's page."""
    if not problem_ids:
        return {}
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "select distinct on (problem_id) id, problem_id, user_answer, is_correct,"
            " constant_omitted, created_at, feedback_code,"
            " count(*) over (partition by problem_id) as total"
            " from public.attempts where user_id = %s and problem_id = any(%s)"
            " order by problem_id, created_at desc, id desc",
            (user_id, problem_ids),
        )
        result = {}
        for row in cur.fetchall():
            count = int(row.pop("total"))
            attempt = AttemptRecord(**row)
            result[attempt.problem_id] = (attempt, count)
        return result


def profile_counts(conn: Connection[Any], user_id: UUID) -> dict[str, int]:
    """All three ADR-004 counts from one statement/snapshot, including invalid attempts."""
    row = conn.execute(
        "select count(*), count(*) filter (where exists ("
        " select 1 from public.attempts a where a.problem_id = p.id and a.user_id = p.user_id"
        ")), count(*) filter (where exists ("
        " select 1 from public.attempts a where a.problem_id = p.id and a.user_id = p.user_id"
        " and a.is_correct is true)) from public.problems p where p.user_id = %s",
        (user_id,),
    ).fetchone()
    if row is None:
        raise RuntimeError("Aggregate query returned no row")
    return dict(zip(("generated", "attempted", "correct"), map(int, row), strict=True))


def previously_revealed(conn: Connection[Any], user_id: UUID, problem_id: UUID) -> dict[str, Any]:
    """Read only previously authorized content; GET never changes reveal flags."""
    row = conn.execute(
        "select case when p.answer_revealed then s.answer_latex end,"
        " case when p.solution_revealed then s.solution_steps end"
        " from public.problems p join private.problem_solutions s on s.problem_id = p.id"
        " where p.id = %s and p.user_id = %s"
        " and (p.answer_revealed or p.solution_revealed)",
        (problem_id, user_id),
    ).fetchone()
    if row is None:
        return {}
    result: dict[str, Any] = {}
    if row[0] is not None:
        result["answer"] = {"answerLatex": str(row[0])}
    if row[1] is not None:
        result["solution"] = {"steps": list(row[1])}
    return result


def last_attempt(conn: Connection[Any], user_id: UUID, problem_id: UUID) -> AttemptRecord | None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "select id, problem_id, user_answer, is_correct, constant_omitted, created_at"
            " from public.attempts"
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
    constant_omitted: bool = False,
    feedback_code: str | None = None,
) -> AttemptRecord | None:
    """None when the problem is missing or belongs to someone else; nothing is written."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "insert into public.attempts"
            "(problem_id, user_id, user_answer, is_correct, constant_omitted, feedback_code)"
            " select p.id, p.user_id, %s, %s, %s, %s from public.problems p"
            " where p.id = %s and p.user_id = %s"
            " returning id, problem_id, user_answer, is_correct, constant_omitted, created_at,"
            " feedback_code",
            (user_answer, is_correct, constant_omitted, feedback_code, problem_id, user_id),
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
