"""Problem sharing (#37): owners share by link or short code; anyone may look one up.

Lookups need no account, so they return only the statement, topic and
difficulty, and every unavailable share is one of four fixed error codes with
no problem data. The contract is docs/api/README.md "Sharing".
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.practice import RateLimiter, User, _not_found, _public_share
from app.core.database import transaction
from app.core.errors import ApiError
from app.services import shares
from app.services.shares import SharedProblem, State

router = APIRouter(tags=["sharing"])

share_limit = RateLimiter(20)
# The Pages proxy does not pass the client address, so anonymous lookups share
# one window. Guessing stays hopeless: a code has 2^40 values, a token 2^256.
lookup_limit = RateLimiter(120)
_EVERYONE = UUID(int=0)

_UNAVAILABLE = {
    State.MISSING: (404, "share_not_found", "No shared problem matches this link or code."),
    State.EXPIRED: (410, "share_expired", "This shared problem has expired."),
    State.REVOKED: (410, "share_revoked", "The owner has stopped sharing this problem."),
}


@router.post("/problems/{problem_id}/share")
def create(problem_id: UUID, user: User) -> JSONResponse:
    """Returns the problem's live share (200) or a new one (201); a second click adds none."""
    share_limit.check(user.id)
    with transaction(user.id) as conn:
        created = shares.create_share(conn, user.id, problem_id)
    if created is None:
        raise _not_found()
    share, new = created
    return JSONResponse({"share": _public_share(share)}, status_code=201 if new else 200)


@router.post("/problems/{problem_id}/share/revoke")
def revoke(problem_id: UUID, user: User) -> dict[str, None]:
    """Ends every live share of the problem at once. Idempotent."""
    share_limit.check(user.id)
    with transaction(user.id) as conn:
        if shares.revoke_shares(conn, user.id, problem_id) is None:
            raise _not_found()
    return {"share": None}


def _invalid_share() -> ApiError:
    return ApiError(400, "share_invalid", "This share link or code is not valid.")


def _shared(found: SharedProblem | State) -> dict[str, Any]:
    if isinstance(found, State):
        status, code, message = _UNAVAILABLE[found]
        raise ApiError(status, code, message)
    # An explicit projection: nothing else about the problem or its owner leaves here.
    return {
        "problem": {
            "topic": found.topic,
            "difficulty": found.difficulty,
            "problemLatex": found.problem_latex,
        }
    }


@router.get("/shares/code/{code}")
def by_code(code: str) -> dict[str, Any]:
    lookup_limit.check(_EVERYONE)
    normalized = shares.normalize_code(code) if len(code) <= 32 else None
    if normalized is None:
        raise _invalid_share()
    with transaction(read_only=True) as conn:
        return _shared(shares.lookup(conn, code=normalized))


@router.get("/shares/{token}")
def by_token(token: str) -> dict[str, Any]:
    lookup_limit.check(_EVERYONE)
    if not shares.valid_token(token):
        raise _invalid_share()
    with transaction(read_only=True) as conn:
        return _shared(shares.lookup(conn, token=token))
