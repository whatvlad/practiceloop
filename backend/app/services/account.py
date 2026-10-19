"""Server-only Supabase Auth hard deletion; no redirects, credentials or bodies in logs."""

import json
import os
from http.client import HTTPException, HTTPSConnection
from urllib.parse import urlsplit
from uuid import UUID

from app.core.errors import ApiError


def delete_user(user_id: UUID) -> None:
    base = urlsplit(os.environ.get("SUPABASE_URL", "").strip())
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if (
        base.scheme != "https"
        or not base.hostname
        or base.username
        or base.path not in ("", "/")
        or not key
    ):
        raise unavailable()
    conn = HTTPSConnection(base.hostname, port=base.port, timeout=10)
    try:
        conn.request(
            "DELETE",
            f"/auth/v1/admin/users/{user_id}",
            body=json.dumps({"should_soft_delete": False}),
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
        )
        response = conn.getresponse()
        # Do not follow redirects or display upstream bodies. A retry can find no user.
        if response.status not in (200, 404):
            raise unavailable()
    except (HTTPException, OSError):
        raise unavailable() from None
    finally:
        conn.close()


def unavailable() -> ApiError:
    return ApiError(
        503,
        "account_deletion_unavailable",
        "Your account could not be deleted. Try again shortly.",
        retryable=True,
    )
