"""Authenticated, persisted practice (#10): generate, attempt and reveal.

Browser paths are /api/...; the Pages proxy strips /api, so FastAPI serves them
at the root, like /preview. Every route takes the user only from the verified
Supabase token. Transactions follow ADR-004; the contract is docs/api/README.md.
"""

from __future__ import annotations

import base64
import binascii
import json
import math
import secrets
import time
from collections import deque
from collections.abc import Mapping
from datetime import UTC, datetime
from threading import Lock
from typing import Annotated, Any, Literal, NamedTuple
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app.core.auth import VerifiedUser, current_user
from app.core.database import transaction
from app.core.errors import ApiError
from app.engine import practice as engine
from app.engine.topics.catalogue import Topic as EngineTopic
from app.math_input import MathInputTooLong
from app.services import archive, idempotency, shares
from app.services import owned_records as records
from app.services.account import delete_user
from app.services.idempotency import Scope, StoredResponse
from app.services.learning_stats import statistics
from app.services.math_worker import AnswerCheck, MathCheckInconclusive, MathWorkerError
from app.services.math_worker import check_answer as shared_check
from app.services.preview_check import CHECK_SLOTS
from app.visuals.spec import solution_payload

router = APIRouter(tags=["practice"])


class Topic(NamedTuple):
    name: str
    area: str
    # Only cells with a verified generator are offered; others are 422, never easy copies.
    levels: tuple[int, ...]
    # #36 mixed practice: a fixed, published weight, never adapted to a learner's history.
    # 0 keeps a topic out of mixed practice.
    mixed_weight: int
    # ADR-007: writing space after a level-1 problem on a printed worksheet, in cm.
    space_cm: float


# #144: Algebra and Mathematical Analysis are the top-level practice areas.
AREAS = {
    "algebra": "Algebra",
    "mathematical-analysis": "Mathematical Analysis",
    "probability-statistics": "Probability and Statistics",
}


def listed_topics(served: Mapping[str, EngineTopic]) -> dict[str, Topic]:
    """#191: a topic served by the new engine is listed from its engine entry alone.

    Entry order is kept within each public area; no legacy topic fallback remains.
    """
    merged = {
        slug: Topic(
            entry.title, entry.area, tuple(sorted(entry.levels)), entry.mixed_weight, entry.space_cm
        )
        for slug, entry in served.items()
    }
    order = list(AREAS)
    return dict(sorted(merged.items(), key=lambda item: order.index(item[1].area)))


TOPICS = listed_topics(engine.ENGINE_TOPICS)
MIXED = "mixed"
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


_RANDOM = secrets.SystemRandom()
generation_limit = RateLimiter(30)
attempt_limit = RateLimiter(30)
reveal_limit = RateLimiter(60)


# PostgreSQL text cannot hold NUL; reject it as a bad request instead of failing the insert.
NO_NUL = r"^[^\x00]*$"


class MatrixOptions(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation: Literal["add", "subtract", "multiply", "mixed"]
    size: Literal["2x2", "3x3", "rectangular"]


class RankDimensions(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    rows: int = Field(ge=2, le=5)
    columns: int = Field(ge=2, le=5)


class MatrixDimensions(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation: Literal["add", "subtract", "multiply", "divide"]
    rowsA: int = Field(ge=1, le=5)
    colsA: int = Field(ge=1, le=5)
    rowsB: int = Field(ge=1, le=5)
    colsB: int = Field(ge=1, le=5)


class GenerateBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    topic: str = Field(min_length=1, max_length=64)
    difficulty: int
    # Only with "mixed": Mathematical Analysis when omitted; legacy selectors remain valid.
    area: str | None = Field(default=None, min_length=1, max_length=64)
    matrixOptions: MatrixOptions | None = None
    modulusMode: Literal["expression", "properties", "geometry"] | None = None
    rankDimensions: RankDimensions | None = None
    matrixDimensions: MatrixDimensions | None = None
    squareSize: int | None = Field(default=None, ge=2, le=5)
    exerciseMode: (
        Literal[
            "multiply",
            "divide",
            "division",
            "remainder",
            "divisibility",
            "alg-trig",
            "alg-exp",
            "trig-alg",
            "exp-alg",
            "roots",
            "fractions",
            "argument",
            "power",
            "root",
        ]
        | None
    ) = None


class AttemptBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    answer: str = Field(min_length=1, max_length=MAX_ANSWER_CHARS, pattern=NO_NUL)
    elapsedMs: int | None = Field(default=None, ge=0, le=86400000)


class ProfileBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    name: str | None = Field(max_length=80, pattern=NO_NUL)


class DeleteBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    confirmation: str


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


def area_topics(area: str) -> list[str]:
    # Keep in-flight requests and saved worksheet groups from pre-#144 clients usable.
    if area in ("integrals", "derivatives"):
        derivatives = {"derivatives", "partial-derivatives"}
        return [
            slug
            for slug, topic in TOPICS.items()
            if topic.area == "mathematical-analysis"
            and (slug in derivatives) == (area == "derivatives")
        ]
    return [slug for slug, topic in TOPICS.items() if topic.area == area]


def mixed_topics(
    area: str, difficulty: int, worksheet: bool = False
) -> tuple[list[str], list[int]]:
    """The area's topics offered at this level and their weights; a missing cell has none.

    Engine worksheet records come from the release catalogue (#192).
    """
    slugs = [
        slug
        for slug in area_topics(area)
        if difficulty in TOPICS[slug].levels and TOPICS[slug].mixed_weight
    ]
    return slugs, [TOPICS[slug].mixed_weight for slug in slugs]


def _mixed(area: str) -> dict[str, object] | None:
    """Mixed practice needs a choice, so an area offers it only with two topics or more."""
    slugs = [slug for slug in area_topics(area) if TOPICS[slug].mixed_weight]
    if len(slugs) < 2:
        return None
    levels = sorted({level for slug in slugs for level in TOPICS[slug].levels})
    return {
        "availableDifficulties": levels,
        "weights": {slug: TOPICS[slug].mixed_weight for slug in slugs},
        "worksheetCapacity": {
            str(level): sum(
                capacity(slug, level) for slug in mixed_topics(area, level, worksheet=True)[0]
            )
            for level in levels
        },
    }


def capacity(topic: str, difficulty: int) -> int:
    """ADR-007 decision 4: a worksheet never repeats a record, so a cell holds this many.

    Engine topics use the private deploy-time pools (#192).
    """
    return len(engine.pool(topic, difficulty))


@router.get("/topics")
def topics(_user: User) -> dict[str, object]:
    return {
        "areas": [
            {"slug": area, "name": name, "mixed": _mixed(area)}
            for area, name in AREAS.items()
            if area_topics(area)
        ],
        "items": [
            {
                "slug": slug,
                "name": topic.name,
                "area": topic.area,
                "availableDifficulties": list(topic.levels),
                "worksheetCapacity": {str(level): capacity(slug, level) for level in topic.levels},
            }
            for slug, topic in TOPICS.items()
        ],
    }


def _public_problem(
    problem: records.ProblemRecord, summary: tuple[records.AttemptRecord, int] | None
) -> dict[str, Any]:
    last = summary[0] if summary else None
    return {
        "id": str(problem.id),
        "topic": problem.topic,
        "difficulty": problem.difficulty,
        "problemLatex": problem.problem_latex,
        **engine.input_projection(problem.generator_data),
        **engine.public_settings(problem.generator_data),
        "createdAt": _timestamp(problem.created_at),
        "answerRevealed": problem.answer_revealed,
        "solutionRevealed": problem.solution_revealed,
        "worksheetId": str(problem.worksheet_id) if problem.worksheet_id else None,
        "attemptCount": summary[1] if summary else 0,
        "lastAttempt": None
        if last is None
        else {
            "answer": last.user_answer,
            "result": "invalid"
            if last.is_correct is None
            else "correct"
            if last.is_correct
            else "incorrect",
            "feedbackCode": _feedback(last),
        },
    }


def _public_share(share: shares.Share | None) -> dict[str, str] | None:
    """The owner's live share link and code (#37), shown only to the owner."""
    if share is None:
        return None
    return {"token": share.token, "code": share.code, "expiresAt": _timestamp(share.expires_at)}


def _feedback(attempt: records.AttemptRecord) -> str | None:
    """`missing_constant`, a declared mistake code (#36), or None for a general hint."""
    return "missing_constant" if attempt.constant_omitted else attempt.feedback_code


def _encode_cursor(problem: records.ProblemRecord) -> str:
    data = json.dumps([_timestamp(problem.created_at), str(problem.id)], separators=(",", ":"))
    return base64.urlsafe_b64encode(data.encode()).decode().rstrip("=")


def _decode_cursor(value: str | None) -> tuple[datetime, UUID] | None:
    if value is None:
        return None
    try:
        data = json.loads(
            base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True)
        )
        if (
            not isinstance(data, list)
            or len(data) != 2
            or not all(isinstance(x, str) for x in data)
        ):
            raise ValueError
        timestamp = datetime.fromisoformat(data[0])
        if timestamp.tzinfo is None:
            raise ValueError
        return timestamp, UUID(data[1])
    except (ValueError, TypeError, binascii.Error, UnicodeDecodeError):
        raise _invalid() from None


@router.get("/problems")
def history(
    user: User,
    limit: Annotated[int, Query(ge=1, le=records.MAX_PAGE_SIZE)] = 20,
    cursor: Annotated[str | None, Query(max_length=256)] = None,
    worksheet: Annotated[bool, Query()] = False,
) -> dict[str, Any]:
    before = _decode_cursor(cursor)
    with transaction(user.id, read_only=True) as conn:
        page = records.list_problems(
            conn, user.id, limit, before, include_next=True, worksheet_only=worksheet
        )
        visible = page[:limit]
        summaries = records.attempt_summaries(conn, user.id, [p.id for p in visible])
    return {
        "items": [_public_problem(p, summaries.get(p.id)) for p in visible],
        "nextCursor": _encode_cursor(visible[-1]) if len(page) > limit else None,
    }


@router.get("/problems/{problem_id}")
def reopen(problem_id: UUID, user: User) -> dict[str, Any]:
    with transaction(user.id, read_only=True) as conn:
        problem = records.get_problem(conn, user.id, problem_id)
        if problem is None:
            raise _not_found()
        summary = records.attempt_summaries(conn, user.id, [problem.id]).get(problem.id)
        revealed = records.previously_revealed(conn, user.id, problem.id)
        solved = "solution" in revealed
        stored = records.solution_for_check(conn, user.id, problem.id) if solved else None
        share = shares.active_share(conn, user.id, problem.id)
    if stored is not None:
        # Built after the transaction: the visual is CPU work and needs no connection.
        revealed["solution"] = _solution(problem.topic, revealed["solution"]["steps"], stored)
    return {"problem": _public_problem(problem, summary), "share": _public_share(share), **revealed}


@router.get("/profile")
def profile(user: User) -> dict[str, Any]:
    with transaction(user.id) as conn:
        counts = records.profile_counts(conn, user.id)
        row = conn.execute(
            "select display_name from public.profiles where id = %s", (user.id,)
        ).fetchone()
    return {
        "account": {
            "id": str(user.id),
            "name": row[0] if row else None,
            "email": user.email or "",
            "provider": "Google",
        },
        "counts": counts,
    }


@router.get("/statistics")
def learning_statistics(user: User) -> dict[str, Any]:
    with transaction(user.id, read_only=True) as conn:
        return statistics(conn, user.id)


@router.post("/profile")
def update_profile(body: ProfileBody, user: User) -> dict[str, Any]:
    name = body.name.strip() if body.name else None
    with transaction(user.id) as conn:
        records.ensure_profile(conn, user.id)
        conn.execute(
            "update public.profiles set display_name = %s where id = %s", (name or None, user.id)
        )
    return {"name": name or None}


@router.post("/account/delete")
def delete_account(body: DeleteBody, user: User) -> dict[str, bool]:
    if body.confirmation != "DELETE":
        raise _invalid()
    # Hard deletion cascades profiles, problems, private solutions, attempts and keys
    # in the Auth transaction. No partial learning-data deletion before Auth succeeds.
    delete_user(user.id)
    return {"deleted": True}


@router.post("/problems", status_code=201)
def generate(body: GenerateBody, user: User, key: IdempotencyKey = None) -> JSONResponse:
    scope = Scope(
        user.id,
        "POST",
        "/problems",
        _idempotency_key(key),
        # exclude_none keeps the hash of a request without an area as it was before #98.
        idempotency.request_hash(body.model_dump(exclude_none=True)),
    )
    topic = body.topic
    if body.exerciseMode is not None and (
        body.difficulty not in (1, 2, 3)
        or body.exerciseMode
        not in {
            "complex-arithmetic": {"multiply", "divide"},
            "polynomial-division": {"division", "remainder", "divisibility"},
            "complex-conversion": {"alg-trig", "alg-exp", "trig-alg", "exp-alg"},
            "polynomial-roots": {"roots"},
            "partial-fractions": {"fractions"},
            "complex-polar-form": {"argument", "power", "root"},
        }.get(topic, set())
        or any(
            value is not None
            for value in (
                body.matrixOptions,
                body.matrixDimensions,
                body.rankDimensions,
                body.modulusMode,
                body.squareSize,
            )
        )
    ):
        raise _invalid()
    if body.squareSize is not None and (
        topic not in ("determinants", "inverse-matrices", "linear-systems")
        or body.difficulty not in (1, 2, 3)
        or any(
            value is not None
            for value in (
                body.matrixOptions,
                body.matrixDimensions,
                body.rankDimensions,
                body.modulusMode,
            )
        )
    ):
        raise _invalid()
    if body.matrixDimensions is not None and (
        topic != "matrix-operations"
        or body.difficulty not in (1, 2, 3)
        or body.matrixOptions is not None
        or body.rankDimensions is not None
        or body.modulusMode is not None
    ):
        raise _invalid()
    if body.rankDimensions is not None and (
        topic != "matrix-rank"
        or body.difficulty not in (1, 2, 3)
        or body.matrixOptions is not None
        or body.modulusMode is not None
    ):
        raise _invalid()
    if body.modulusMode is not None and (
        topic != "complex-numbers" or body.difficulty not in (1, 2, 3)
    ):
        raise _invalid()
    if body.matrixOptions is not None and (
        topic != "matrix-operations"
        or not engine.matrix_options_supported(body.difficulty, body.matrixOptions.model_dump())
    ):
        raise _invalid()
    if topic == MIXED:
        area = body.area or "mathematical-analysis"
        slugs, weights = mixed_topics(area, body.difficulty) if _mixed(area) else ([], [])
        if not slugs:
            raise _invalid()
        topic = _RANDOM.choices(slugs, weights)[0]
    elif body.area is not None:
        raise _invalid()
    cell = TOPICS.get(topic)
    if cell is None or body.difficulty not in cell.levels:
        raise _invalid()
    generation_limit.check(user.id)
    with transaction(user.id) as conn:
        records.ensure_profile(conn, user.id)
        stored = idempotency.claim(conn, scope)
        if stored is not None:
            return _respond(stored, replayed=True)
        recent = records.recent_generator_data(
            conn, user.id, topic, body.difficulty, len(engine.pool(topic, body.difficulty)) // 2
        )
        try:
            if body.exerciseMode is not None:
                issued = engine.issue(
                    topic, body.difficulty, recent=tuple(recent), exercise_mode=body.exerciseMode
                )
            elif body.squareSize is not None:
                issued = engine.issue(
                    topic, body.difficulty, recent=tuple(recent), square_size=body.squareSize
                )
            elif body.matrixDimensions:
                issued = engine.issue(
                    topic,
                    body.difficulty,
                    recent=tuple(recent),
                    matrix_dimensions=body.matrixDimensions.model_dump(),
                )
            elif body.rankDimensions:
                issued = engine.issue(
                    topic,
                    body.difficulty,
                    recent=tuple(recent),
                    rank_dimensions=body.rankDimensions.model_dump(),
                )
            elif body.matrixOptions:
                issued = engine.issue(
                    topic,
                    body.difficulty,
                    recent=tuple(recent),
                    matrix_options=body.matrixOptions.model_dump(),
                )
            elif body.modulusMode:
                issued = engine.issue(
                    topic, body.difficulty, recent=tuple(recent), modulus_mode=body.modulusMode
                )
            else:
                issued = engine.issue(topic, body.difficulty, recent=tuple(recent))
        except ValueError as exc:
            raise _invalid() from exc
        statement, solution = (
            issued.statement,
            records.PrivateSolution(
                generator_version=str(issued.record["generator_version"]),
                generator_data=issued.record,
                answer_latex=issued.answer_latex,
                solution_steps=list(issued.steps),
            ),
        )
        problem = records.insert_problem(conn, user.id, topic, body.difficulty, statement, solution)
        response = StoredResponse(
            201,
            {
                "problem": {
                    "id": str(problem.id),
                    "topic": problem.topic,
                    "difficulty": problem.difficulty,
                    "problemLatex": problem.problem_latex,
                    **engine.input_projection(problem.generator_data),
                    **engine.public_settings(problem.generator_data),
                    "createdAt": _timestamp(problem.created_at),
                    "answerRevealed": problem.answer_revealed,
                    "solutionRevealed": problem.solution_revealed,
                    "lastAttempt": None,
                }
            },
        )
        idempotency.store(conn, scope, response)
    return _respond(response)


def _check(answer: str, record: dict[str, object]) -> AnswerCheck:
    """A trustworthy check result; raises ApiError when none exists."""
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
    return result


def _solution(topic: str, steps: Any, stored: records.PrivateSolution) -> dict[str, Any]:
    if archive.is_archived(topic, stored.generator_data):
        return archive.stored_solution(steps)
    return solution_payload(steps, stored.generator_data)


def _archived() -> ApiError:
    return ApiError(
        409,
        "problem_archived",
        "This problem is archived, so answers can't be checked anymore. "
        "Its answer and solution are still available.",
    )


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
    with transaction(user.id) as conn:
        stored = idempotency.lookup(conn, scope)
        if stored is not None:
            return _respond(stored, replayed=True)
        problem = records.get_problem(conn, user.id, problem_id)
        solution = records.solution_for_check(conn, user.id, problem_id)
    if problem is None or solution is None:
        raise _not_found()
    if archive.is_archived(problem.topic, solution.generator_data):
        raise _archived()
    checked = _check(body.answer, dict(solution.generator_data))
    is_correct = None if checked.result == "invalid" else checked.result == "correct"
    with transaction(user.id) as conn:
        stored = idempotency.claim(conn, scope)
        if stored is not None:
            return _respond(stored, replayed=True)
        saved = records.insert_attempt(
            conn,
            user.id,
            problem_id,
            body.answer,
            is_correct,
            checked.missing_constant,
            checked.feedback_code,
        )
        if saved is None:
            raise _not_found()
        conn.execute(
            "update public.attempts set elapsed_ms = %s where id = %s and user_id = %s",
            (body.elapsedMs, saved.id, user.id),
        )
        result = "invalid" if is_correct is None else "correct" if is_correct else "incorrect"
        response = StoredResponse(
            201,
            {
                "attempt": {
                    "id": str(saved.id),
                    "answer": saved.user_answer,
                    "result": result,
                    "feedbackCode": _feedback(saved),
                    "createdAt": _timestamp(saved.created_at),
                }
            },
        )
        idempotency.store(conn, scope, response)
    return _respond(response)


@router.post("/problems/{problem_id}/reveal-answer")
def reveal_answer(problem_id: UUID, user: User) -> dict[str, str]:
    reveal_limit.check(user.id)
    with transaction(user.id) as conn:
        answer = records.reveal_answer(conn, user.id, problem_id)
    if answer is None:
        raise _not_found()
    return {"answerLatex": answer}


@router.post("/problems/{problem_id}/reveal-solution")
def reveal_solution(problem_id: UUID, user: User) -> dict[str, Any]:
    reveal_limit.check(user.id)
    with transaction(user.id) as conn:
        steps = records.reveal_solution(conn, user.id, problem_id)
        problem = records.get_problem(conn, user.id, problem_id) if steps else None
        stored = records.solution_for_check(conn, user.id, problem_id) if steps else None
    if steps is None or problem is None or stored is None:
        raise _not_found()
    return _solution(problem.topic, steps, stored)
