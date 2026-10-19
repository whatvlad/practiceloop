"""ADR-004 idempotency keys for generation and attempts.

A key is scoped to the verified user, the HTTP method and the concrete route.
`claim` inserts the key inside the caller's transaction, before the mutation.
A concurrent request with the same key waits on that row and, once the first
commits, gets its stored response instead of mutating again. If the first rolls
back (worker or database failure), the key was never stored and a retry runs.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from psycopg import Connection
from psycopg.types.json import Jsonb

from app.core.database import database_unavailable
from app.core.errors import ApiError


@dataclass(frozen=True)
class StoredResponse:
    status_code: int
    body: dict[str, Any]


@dataclass(frozen=True)
class Scope:
    user_id: UUID
    method: str
    route: str
    key: UUID
    request_hash: str


def request_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def _conflict() -> ApiError:
    return ApiError(
        409,
        "idempotency_conflict",
        "This request key was already used for a different request.",
    )


def _replay(row: tuple[Any, ...] | None, scope: Scope) -> StoredResponse:
    if row is None or row[1] is None:
        # Expired and deleted in between, or never completed: nothing to replay yet.
        raise database_unavailable()
    if row[0] != scope.request_hash:
        raise _conflict()
    return StoredResponse(int(row[1]), dict(row[2]))


_SELECT = (
    "select request_hash, status_code, response from private.idempotency_keys"
    " where user_id = %s and method = %s and route = %s and key = %s"
    " and created_at > now() - interval '24 hours'"
)


def lookup(conn: Connection[Any], scope: Scope) -> StoredResponse | None:
    """A committed outcome for this key, without claiming it."""
    row = conn.execute(_SELECT, (scope.user_id, scope.method, scope.route, scope.key)).fetchone()
    return None if row is None else _replay(row, scope)


def claim(conn: Connection[Any], scope: Scope) -> StoredResponse | None:
    """None when this transaction now owns the key; else the committed outcome."""
    conn.execute(
        "delete from private.idempotency_keys"
        " where user_id = %s and created_at <= now() - interval '24 hours'",
        (scope.user_id,),
    )
    claimed = conn.execute(
        "insert into private.idempotency_keys(user_id, method, route, key, request_hash)"
        " values (%s, %s, %s, %s, %s) on conflict do nothing returning 1",
        (scope.user_id, scope.method, scope.route, scope.key, scope.request_hash),
    ).fetchone()
    if claimed:
        return None
    row = conn.execute(_SELECT, (scope.user_id, scope.method, scope.route, scope.key)).fetchone()
    return _replay(row, scope)


def store(conn: Connection[Any], scope: Scope, response: StoredResponse) -> None:
    conn.execute(
        "update private.idempotency_keys set status_code = %s, response = %s"
        " where user_id = %s and method = %s and route = %s and key = %s",
        (
            response.status_code,
            Jsonb(response.body),
            scope.user_id,
            scope.method,
            scope.route,
            scope.key,
        ),
    )
