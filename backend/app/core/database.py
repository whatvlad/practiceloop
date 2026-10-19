"""The API's one database pool and its transaction boundary.

The backend connects through the Supabase pooler with DATABASE_URL (the
`postgres` user) and runs every transaction as `service_role`, which can use
only the learning tables and bypasses RLS. Ownership therefore lives in the SQL
of app.services.owned_records. Any connection failure becomes a retryable 503
in which nothing was committed.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from typing import Any
from uuid import UUID

import psycopg
from psycopg_pool import ConnectionPool, PoolTimeout

from app.core.errors import ApiError

POOL_MAX_SIZE = 4
POOL_TIMEOUT_SECONDS = 5.0
CONNECT_TIMEOUT_SECONDS = 5


class DatabaseNotConfigured(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_pool() -> ConnectionPool[Any]:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise DatabaseNotConfigured("DATABASE_URL is not set")
    pool: ConnectionPool[Any] = ConnectionPool(
        url,
        min_size=1,
        max_size=POOL_MAX_SIZE,
        timeout=POOL_TIMEOUT_SECONDS,
        open=False,
        # prepare_threshold=None keeps it valid behind the transaction pooler too.
        kwargs={
            "prepare_threshold": None,
            "connect_timeout": CONNECT_TIMEOUT_SECONDS,
            "application_name": "practiceloop-api",
        },
    )
    pool.open(wait=False)
    return pool


def close_pool() -> None:
    if get_pool.cache_info().currsize:
        get_pool().close()
        get_pool.cache_clear()


def database_unavailable() -> ApiError:
    return ApiError(
        503,
        "database_unavailable",
        "Your practice can't be saved right now. Try again shortly.",
        retryable=True,
        headers={"Retry-After": "5"},
    )


@contextmanager
def transaction(
    user_id: UUID | None = None, *, read_only: bool = False
) -> Iterator[psycopg.Connection[Any]]:
    """Commits on normal exit; any exception rolls everything back."""
    try:
        pool = get_pool()
    except DatabaseNotConfigured:
        raise database_unavailable() from None
    try:
        with pool.connection() as conn, conn.transaction():
            conn.execute("set local role service_role")
            if read_only:
                conn.execute("set transaction isolation level repeatable read, read only")
            if user_id is not None:
                exists = conn.execute("select private.account_exists(%s)", (user_id,)).fetchone()
                if not exists or not exists[0]:
                    raise ApiError(401, "invalid_token", "Your account is no longer available.")
            yield conn
    except (PoolTimeout, psycopg.OperationalError, psycopg.InterfaceError) as exc:
        raise database_unavailable() from exc
