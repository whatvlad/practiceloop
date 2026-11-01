"""ADR-007 worksheet picking and storage.

The picker works on raw catalogue records and replays only the records it
keeps. Storage functions never commit; the API owns the transaction, and every
statement filters on the verified user like app.services.owned_records.
"""

from __future__ import annotations

import json
import random
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.engine import practice as engine


def catalogue_records(topic: str, difficulty: int) -> tuple[dict[str, object], ...]:
    """Pick only verified code records from the private release pool."""
    return tuple(
        {"generator_version": p.generator_version, "code": p.code}
        for p in engine.pool(topic, difficulty)
    )


def record_key(record: dict[str, object]) -> str:
    return json.dumps(record, sort_keys=True, separators=(",", ":"))


class Picker:
    """ADR-007 decision 4 for one worksheet: no record twice, distinct bases first."""

    def __init__(self, rng: random.Random) -> None:
        self._rng = rng
        self._used: set[str] = set()

    def remaining(self, topic: str, difficulty: int) -> list[dict[str, object]]:
        return [r for r in catalogue_records(topic, difficulty) if record_key(r) not in self._used]

    def pick(self, topic: str, difficulty: int) -> dict[str, object] | None:
        pool = self.remaining(topic, difficulty)
        if not pool:
            return None
        record = self._rng.choice(pool)
        self._used.add(record_key(record))
        return record

    def pick_mixed(
        self, topics: Sequence[str], weights: Sequence[int], difficulty: int
    ) -> tuple[str, dict[str, object]] | None:
        """A topic by its published weight among those with records left, then a record."""
        open_topics = [
            (t, w) for t, w in zip(topics, weights, strict=True) if self.remaining(t, difficulty)
        ]
        if not open_topics:
            return None
        topic = self._rng.choices([t for t, _ in open_topics], [w for _, w in open_topics])[0]
        record = self.pick(topic, difficulty)
        return None if record is None else (topic, record)


@dataclass(frozen=True)
class Worksheet:
    id: UUID
    created_at: datetime
    source: str
    paper: str
    columns: int
    answer_key: bool
    groups: list[dict[str, Any]]
    solutions: bool = False


@dataclass(frozen=True)
class OwnedProblem:
    id: UUID
    topic: str
    difficulty: int
    created_at: datetime


@dataclass(frozen=True)
class PrintItem:
    group_index: int
    topic: str
    difficulty: int
    problem_latex: str
    answer_latex: str
    solution_steps: list[dict[str, str]]
    generator_data: dict[str, object]


def insert_worksheet(
    conn: Connection[Any],
    user_id: UUID,
    *,
    source: str,
    paper: str,
    columns: int,
    answer_key: bool,
    groups: list[dict[str, Any]],
    solutions: bool = False,
) -> Worksheet:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "insert into public.worksheets"
            "(user_id, source, paper, columns, answer_key, groups, solutions)"
            " values (%s, %s, %s, %s, %s, %s, %s)"
            " returning id, created_at, source, paper, columns, answer_key, groups, solutions",
            (user_id, source, paper, columns, answer_key, Jsonb(groups), solutions),
        )
        row = cur.fetchone()
    if row is None:
        raise RuntimeError("Worksheet insert returned no row")
    return Worksheet(**row)


def insert_items(
    conn: Connection[Any], worksheet_id: UUID, items: Sequence[tuple[UUID, int]]
) -> None:
    """(problem id, group index) in print order; positions are 1..N."""
    with conn.cursor() as cur:
        cur.executemany(
            "insert into public.worksheet_items(worksheet_id, problem_id, position, group_index)"
            " values (%s, %s, %s, %s)",
            [(worksheet_id, pid, n, group) for n, (pid, group) in enumerate(items, start=1)],
        )


def owned_problems(
    conn: Connection[Any], user_id: UUID, problem_ids: Sequence[UUID]
) -> list[OwnedProblem]:
    """The user's problems among these ids; a missing or foreign id is simply absent."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "select p.id, t.slug as topic, p.difficulty, p.created_at from public.problems p"
            " join public.topics t on t.id = p.topic_id"
            " where p.user_id = %s and p.id = any(%s)",
            (user_id, list(problem_ids)),
        )
        return [OwnedProblem(**row) for row in cur.fetchall()]


def reveal_solutions(conn: Connection[Any], user_id: UUID, problem_ids: Sequence[UUID]) -> None:
    """#130: printed worked solutions are a solution reveal, which includes the answer (ADR-004)."""
    conn.execute(
        "update public.problems set answer_revealed = true, solution_revealed = true"
        " where user_id = %s and id = any(%s)",
        (user_id, list(problem_ids)),
    )


def reveal_answers(conn: Connection[Any], user_id: UUID, problem_ids: Sequence[UUID]) -> None:
    """ADR-007 decision 2: a printed answer key is an answer reveal (ADR-004)."""
    conn.execute(
        "update public.problems set answer_revealed = true where user_id = %s and id = any(%s)",
        (user_id, list(problem_ids)),
    )


def get_worksheet(conn: Connection[Any], user_id: UUID, worksheet_id: UUID) -> Worksheet | None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "select id, created_at, source, paper, columns, answer_key, groups, solutions"
            " from public.worksheets where id = %s and user_id = %s",
            (worksheet_id, user_id),
        )
        row = cur.fetchone()
    return Worksheet(**row) if row else None


def print_items(conn: Connection[Any], user_id: UUID, worksheet_id: UUID) -> list[PrintItem]:
    """Statements, private answers and solutions in print order, for the owner's worksheet only."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "select i.group_index, t.slug as topic, p.difficulty, p.problem_latex,"
            " s.answer_latex, s.solution_steps, s.generator_data from public.worksheet_items i"
            " join public.worksheets w on w.id = i.worksheet_id"
            " join public.problems p on p.id = i.problem_id and p.user_id = w.user_id"
            " join public.topics t on t.id = p.topic_id"
            " join private.problem_solutions s on s.problem_id = p.id"
            " where i.worksheet_id = %s and w.user_id = %s order by i.position",
            (worksheet_id, user_id),
        )
        return [PrintItem(**row) for row in cur.fetchall()]
