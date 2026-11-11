"""Permanent engine codes (#198); public statement only, recipient-owned practice."""

from functools import lru_cache
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app.api.practice import (
    IdempotencyKey,
    RateLimiter,
    User,
    _idempotency_key,
    _public_problem,
    _respond,
    _worker_unavailable,
    generation_limit,
)
from app.core.database import transaction
from app.core.errors import ApiError
from app.engine import practice as engine
from app.engine.codes import format_code, parse_code
from app.engine.opening import OpenedCode
from app.services import idempotency
from app.services import owned_records as records
from app.services.idempotency import Scope, StoredResponse
from app.services.math_worker import MathWorkerError, open_problem_code
from app.services.preview_check import CHECK_SLOTS

router = APIRouter(tags=["problem codes"])
lookup_limit = RateLimiter(120)
_EVERYONE = UUID(int=0)


def invalid_code() -> ApiError:
    return ApiError(400, "problem_code_invalid", "This problem code is not valid or is unknown.")


def canonical(text: str) -> str:
    try:
        return format_code(parse_code(text, engine._registry()), engine._registry())
    except ValueError:
        raise invalid_code() from None


@lru_cache(maxsize=128)
def _opened(code: str) -> OpenedCode:
    if not CHECK_SLOTS.acquire(blocking=False):
        raise _worker_unavailable()
    try:
        payload = open_problem_code(code)
    except MathWorkerError:
        raise _worker_unavailable() from None
    finally:
        CHECK_SLOTS.release()
    if payload == b"invalid_code":
        raise invalid_code()
    try:
        result = OpenedCode.model_validate_json(payload)
        if result.problem.code != code or result.topic not in engine.ENGINE_TOPICS:
            raise ValueError("Unusable worker response")
        return result
    except ValueError:
        raise _worker_unavailable() from None


@router.get("/codes")
def lookup(code: Annotated[str, Query(max_length=128)]) -> dict[str, Any]:
    lookup_limit.check(_EVERYONE)
    opened = _opened(canonical(code))
    return {
        "problem": {
            "topic": opened.topic,
            "difficulty": opened.difficulty,
            "problemLatex": opened.problem.statement,
            **engine.input_projection(opened.problem.issued().record),
            **(
                {"statementVisual": opened.problem.statement_visual}
                if opened.problem.statement_visual is not None
                else {}
            ),
        }
    }


class PracticeCodeBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    code: str = Field(max_length=128)


@router.post("/codes/practice", status_code=201)
def practice_code(body: PracticeCodeBody, user: User, key: IdempotencyKey = None) -> JSONResponse:
    code = canonical(body.code)
    scope = Scope(
        user.id,
        "POST",
        "/codes/practice",
        _idempotency_key(key),
        idempotency.request_hash({"code": code}),
    )
    generation_limit.check(user.id)
    with transaction(user.id) as conn:
        records.ensure_profile(conn, user.id)
        stored = idempotency.claim(conn, scope)
        if stored is not None:
            return _respond(stored, replayed=True)
        opened = _opened(code)
        issued = opened.problem.issued()
        problem = records.insert_problem(
            conn,
            user.id,
            opened.topic,
            opened.difficulty,
            issued.statement,
            records.PrivateSolution(
                str(issued.record["generator_version"]),
                issued.record,
                issued.answer_latex,
                list(issued.steps),
            ),
        )
        response = StoredResponse(201, {"problem": _public_problem(problem, None)})
        idempotency.store(conn, scope, response)
    return _respond(response)
