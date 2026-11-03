"""Problem shares (#37): an opaque link token and a short code for one problem.

Both are fresh randomness from `secrets`, never a hash of the problem, so a
holder learns nothing they could not already see and cannot guess another
share. A lookup returns only the statement, topic and difficulty. Owner
functions filter on the verified user ID like app.services.owned_records;
functions never commit, the caller owns the transaction.
"""

from __future__ import annotations

import re
import secrets
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from psycopg import Connection, errors
from psycopg.rows import dict_row

from app.services import owned_records as records

LIFETIME_DAYS = 90
# Crockford base32: no I, L, O or U, so a code survives being read aloud or retyped.
CODE_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
CODE_LENGTH = 8
TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{43}$")
CODE_PATTERN = re.compile(rf"^[{CODE_ALPHABET}]{{{CODE_LENGTH}}}$")
_CONFUSABLE = str.maketrans({"O": "0", "I": "1", "L": "1"})
_ATTEMPTS = 5


@dataclass(frozen=True)
class Share:
    token: str
    code: str
    expires_at: datetime


@dataclass(frozen=True)
class SharedProblem:
    topic: str
    difficulty: int
    problem_latex: str
    generator_data: Any = None


class State(Enum):
    MISSING = "missing"
    EXPIRED = "expired"
    REVOKED = "revoked"


def new_token() -> str:
    return secrets.token_urlsafe(32)


def new_code() -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))


def normalize_code(value: str) -> str | None:
    """`k7m2-qx9p`, `K7M2 QX9P` and `K7M2QX9P` are one code; None when it cannot be one."""
    code = re.sub(r"[\s-]", "", value).upper().translate(_CONFUSABLE)
    return code if CODE_PATTERN.match(code) else None


def valid_token(value: str) -> bool:
    return TOKEN_PATTERN.match(value) is not None


def active_share(conn: Connection[Any], user_id: UUID, problem_id: UUID) -> Share | None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "select token, code, expires_at from private.problem_shares"
            " where problem_id = %s and user_id = %s"
            " and revoked_at is null and expires_at > now()"
            " order by created_at desc limit 1",
            (problem_id, user_id),
        )
        row = cur.fetchone()
    return Share(**row) if row else None


def create_share(
    conn: Connection[Any], user_id: UUID, problem_id: UUID
) -> tuple[Share, bool] | None:
    """The problem's active share, or a new one (True). None when the problem is not the user's."""
    owned = conn.execute(
        # Locks the problem row, so concurrent requests agree on one active share.
        "select 1 from public.problems where id = %s and user_id = %s for update",
        (problem_id, user_id),
    ).fetchone()
    if owned is None:
        return None
    existing = active_share(conn, user_id, problem_id)
    if existing is not None:
        return existing, False
    for _ in range(_ATTEMPTS):
        try:
            with conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "insert into private.problem_shares"
                    "(problem_id, user_id, token, code, expires_at)"
                    " values (%s, %s, %s, %s, now() + make_interval(days => %s))"
                    " returning token, code, expires_at",
                    (problem_id, user_id, new_token(), new_code(), LIFETIME_DAYS),
                )
                row = cur.fetchone()
        except errors.UniqueViolation:
            continue  # a code collision (1 in 2^40 per share); draw again
        if row is not None:
            return Share(**row), True
    raise RuntimeError("Could not draw a unique share code")


def revoke_shares(conn: Connection[Any], user_id: UUID, problem_id: UUID) -> bool | None:
    """Revokes every live share of the problem; None when the problem is not the user's."""
    owned = conn.execute(
        "select 1 from public.problems where id = %s and user_id = %s for update",
        (problem_id, user_id),
    ).fetchone()
    if owned is None:
        return None
    conn.execute(
        "update private.problem_shares set revoked_at = now()"
        " where problem_id = %s and user_id = %s and revoked_at is null",
        (problem_id, user_id),
    )
    return True


def lookup(
    conn: Connection[Any], *, token: str | None = None, code: str | None = None
) -> SharedProblem | State:
    """Only the public statement, topic and difficulty, or why the share is unavailable."""
    if (token is None) == (code is None):
        raise ValueError("Pass exactly one of token and code")
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "select t.slug as topic, p.difficulty, p.problem_latex,"
            " (select a.generator_data from private.problem_solutions a"
            " where a.problem_id = p.id) as generator_data,"
            " s.revoked_at is not null as revoked, s.expires_at <= now() as expired"
            " from private.problem_shares s"
            " join public.problems p on p.id = s.problem_id and p.user_id = s.user_id"
            " join public.topics t on t.id = p.topic_id"
            " where s.token = %(token)s or s.code = %(code)s",
            {"token": token, "code": code},
        )
        row = cur.fetchone()
    if row is None:
        return State.MISSING
    # Revocation is the owner's explicit choice, so it wins over a later expiry.
    if row.pop("revoked"):
        return State.REVOKED
    if row.pop("expired"):
        return State.EXPIRED
    return SharedProblem(**row)


def copy_for_practice(
    conn: Connection[Any], user_id: UUID, *, token: str | None, code: str | None
) -> records.ProblemRecord | State:
    """Copy trusted content, never the sender's attempts or reveal state.

    Lock the source problem and share until commit. Revocation locks/updates
    these rows too, so it cannot race an authorized copy. The caller owns the
    idempotency claim and transaction; no source ID leaves this function.
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "select t.slug as topic, p.difficulty, p.problem_latex,"
            " s.revoked_at is not null as revoked, s.expires_at <= now() as expired,"
            " a.generator_version, a.generator_data, a.answer_latex, a.solution_steps"
            " from private.problem_shares s"
            " join public.problems p on p.id = s.problem_id and p.user_id = s.user_id"
            " join public.topics t on t.id = p.topic_id"
            " join private.problem_solutions a on a.problem_id = p.id"
            " where s.token = %(token)s or s.code = %(code)s"
            " for share of p, s",
            {"token": token, "code": code},
        )
        row = cur.fetchone()
    if row is None:
        return State.MISSING
    if row["revoked"]:
        return State.REVOKED
    if row["expired"]:
        return State.EXPIRED
    return records.insert_problem(
        conn,
        user_id,
        row["topic"],
        row["difficulty"],
        row["problem_latex"],
        records.PrivateSolution(
            row["generator_version"],
            row["generator_data"],
            row["answer_latex"],
            row["solution_steps"],
        ),
    )
