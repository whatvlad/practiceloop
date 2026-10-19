"""Authenticated, persisted practice (#10): generate, attempt and reveal.

Browser paths are /api/...; the Pages proxy strips /api, so FastAPI serves them
at the root, like /preview. Every route takes the user only from the verified
Supabase token. Transactions follow ADR-004; the contract is docs/api/README.md.
"""

from __future__ import annotations

import math
import secrets
import time
from collections import deque
from datetime import UTC, datetime
from threading import Lock
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app.core.auth import VerifiedUser, current_user
from app.core.database import transaction
from app.core.errors import ApiError
from app.generators.core import Exercise, catalogue
from app.services import idempotency
from app.services import owned_records as records
from app.services.idempotency import Scope, StoredResponse
from app.services.math_parser import MathInputTooLong
from app.services.math_worker import MathCheckInconclusive, MathWorkerError
from app.services.math_worker import check_answer as shared_check
from app.services.preview_check import CHECK_SLOTS

router = APIRouter(tags=["practice"])

# Only cells with a verified generator are offered; others are 422, never easy copies.
TOPICS = {
    "basic-integrals": ("Basic integrals", (1, 2)),
    "substitution": ("Substitution", (1, 2)),
}
MAX_ANSWER_CHARS = 512  # the parser's 256-byte limit applies after normalization


class RateLimiter:
    """Per-user sliding window; this API runs as one process on one VM."""

    def __init__(self, limit: int, window: float = 60.0, max_users: int = 10_000) -> None:
        self.limit = limit
        self.window = window
        self.max_users = max_users
        self._hits: dict[UUID, deque[float]] = {}
        self._lock = Lock()

    def check(self, user_id: UUID) -> None:
        now = time.monotonic()
        with self._lock:
            hits = self._hits.get(user_id)
            if hits is None:
                if len(self._hits) >= self.max_users:
                    self._prune(now)
                hits = self._hits[user_id] = deque()
            while hits and hits[0] <= now - self.window:
                hits.popleft()
            if len(hits) >= self.limit:
                wait = math.ceil(hits[0] + self.window - now)
                raise ApiError(
                    429,
                    "rate_limited",
                    "You're going a bit fast. Wait a moment and try again.",
                    retryable=True,
                    headers={"Retry-After": str(max(wait, 1))},
                )
            hits.append(now)

    def _prune(self, now: float) -> None:
        for user_id in [u for u, h in self._hits.items() if not h or h[-1] <= now - self.window]:
            del self._hits[user_id]

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


generation_limit = RateLimiter(30)
attempt_limit = RateLimiter(30)
reveal_limit = RateLimiter(60)


class GenerateBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    topic: str = Field(min_length=1, max_length=64)
    difficulty: int


class AttemptBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    answer: str = Field(min_length=1, max_length=MAX_ANSWER_CHARS)


def _invalid() -> ApiError:
    return ApiError(422, "invalid_request", "Check your request and try again.")


def _not_found() -> ApiError:
    return ApiError(404, "problem_not_found", "Problem not found.")


def _idempotency_key(value: str | None) -> UUID:
    try:
        key = UUID(value or "")
    except ValueError:
        raise _invalid() from None
    if key.version != 4 or str(key) != (value or "").lower():
        raise _invalid()
    return key


IdempotencyKey = Annotated[str | None, Header(alias="Idempotency-Key")]
User = Annotated[VerifiedUser, Depends(current_user)]


def _timestamp(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _respond(stored: StoredResponse, replayed: bool = False) -> JSONResponse:
    headers = {"Idempotency-Replayed": "true"} if replayed else None
    return JSONResponse(stored.body, status_code=stored.status_code, headers=headers)


def _pick(conn: Any, user_id: UUID, topic: str, difficulty: int) -> Exercise:
    """Random record, avoiding the ones behind the user's latest half-pool in this cell."""
    pool = catalogue(topic, difficulty)
    recent = records.recent_generator_data(conn, user_id, topic, difficulty, len(pool) // 2)
    fresh = [exercise for exercise in pool if exercise.record not in recent]
    return secrets.choice(fresh or list(pool))


@router.get("/topics")
def topics(_user: User) -> dict[str, object]:
    return {
        "items": [
            {"slug": slug, "name": name, "availableDifficulties": list(levels)}
            for slug, (name, levels) in TOPICS.items()
        ]
    }


@router.post("/problems", status_code=201)
def generate(body: GenerateBody, user: User, key: IdempotencyKey = None) -> JSONResponse:
    scope = Scope(
        user.id,
        "POST",
        "/problems",
        _idempotency_key(key),
        idempotency.request_hash(body.model_dump()),
    )
    cell = TOPICS.get(body.topic)
    if cell is None or body.difficulty not in cell[1]:
        raise _invalid()
    generation_limit.check(user.id)
    with transaction() as conn:
        records.ensure_profile(conn, user.id)
        stored = idempotency.claim(conn, scope)
        if stored is not None:
            return _respond(stored, replayed=True)
        exercise = _pick(conn, user.id, body.topic, body.difficulty)
        problem = records.insert_problem(
            conn,
            user.id,
            body.topic,
            body.difficulty,
            exercise.statement,
            records.PrivateSolution(
                generator_version=str(exercise.record["generator_version"]),
                generator_data=exercise.record,
                answer_latex=exercise.answer,
                solution_steps=list(exercise.steps),
            ),
        )
        response = StoredResponse(
            201,
            {
                "problem": {
                    "id": str(problem.id),
                    "topic": problem.topic,
                    "difficulty": problem.difficulty,
                    "problemLatex": problem.problem_latex,
                    "createdAt": _timestamp(problem.created_at),
                    "answerRevealed": problem.answer_revealed,
                    "solutionRevealed": problem.solution_revealed,
                    "lastAttempt": None,
                }
            },
        )
        idempotency.store(conn, scope, response)
    return _respond(response)


def _check(answer: str, record: dict[str, object]) -> tuple[bool | None, bool]:
    """(is_correct, constant_omitted); raises ApiError when no trustworthy result exists."""
    if not CHECK_SLOTS.acquire(blocking=False):
        raise _worker_unavailable()
    try:
        result = shared_check(answer, record)
    except MathInputTooLong:
        raise _invalid() from None
    except MathCheckInconclusive:
        raise ApiError(
            503,
            "math_check_inconclusive",
            "This answer couldn't be checked automatically. Try writing it more simply.",
        ) from None
    except MathWorkerError:
        raise _worker_unavailable() from None
    finally:
        CHECK_SLOTS.release()
    if result.result == "invalid":
        return None, False
    return result.result == "correct", result.missing_constant


def _worker_unavailable() -> ApiError:
    return ApiError(
        503,
        "math_worker_unavailable",
        "Answers can't be checked right now. Try again in a moment.",
        retryable=True,
        headers={"Retry-After": "3"},
    )


@router.post("/problems/{problem_id}/attempts", status_code=201)
def attempt(
    problem_id: UUID, body: AttemptBody, user: User, key: IdempotencyKey = None
) -> JSONResponse:
    scope = Scope(
        user.id,
        "POST",
        f"/problems/{problem_id}/attempts",
        _idempotency_key(key),
        idempotency.request_hash(body.model_dump()),
    )
    if not body.answer.strip():
        raise _invalid()
    attempt_limit.check(user.id)
    # Read the private record, then check without holding a connection; the
    # attempt and its key commit together only once a result exists.
    with transaction() as conn:
        stored = idempotency.lookup(conn, scope)
        if stored is not None:
            return _respond(stored, replayed=True)
        solution = records.solution_for_check(conn, user.id, problem_id)
    if solution is None:
        raise _not_found()
    is_correct, constant_omitted = _check(body.answer, dict(solution.generator_data))
    with transaction() as conn:
        stored = idempotency.claim(conn, scope)
        if stored is not None:
            return _respond(stored, replayed=True)
        saved = records.insert_attempt(
            conn, user.id, problem_id, body.answer, is_correct, constant_omitted
        )
        if saved is None:
            raise _not_found()
        result = "invalid" if is_correct is None else "correct" if is_correct else "incorrect"
        response = StoredResponse(
            201,
            {
                "attempt": {
                    "id": str(saved.id),
                    "answer": saved.user_answer,
                    "result": result,
                    "feedbackCode": "missing_constant" if saved.constant_omitted else None,
                    "createdAt": _timestamp(saved.created_at),
                }
            },
        )
        idempotency.store(conn, scope, response)
    return _respond(response)


@router.post("/problems/{problem_id}/reveal-answer")
def reveal_answer(problem_id: UUID, user: User) -> dict[str, str]:
    reveal_limit.check(user.id)
    with transaction() as conn:
        answer = records.reveal_answer(conn, user.id, problem_id)
    if answer is None:
        raise _not_found()
    return {"answerLatex": answer}


@router.post("/problems/{problem_id}/reveal-solution")
def reveal_solution(problem_id: UUID, user: User) -> dict[str, list[Any]]:
    reveal_limit.check(user.id)
    with transaction() as conn:
        steps = records.reveal_solution(conn, user.id, problem_id)
    if steps is None:
        raise _not_found()
    return {"steps": steps}
