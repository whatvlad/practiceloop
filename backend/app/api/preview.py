"""Untracked, bounded preview sessions; no account, database or persistent outcomes."""

import secrets
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.generators.core import Exercise, catalogue
from app.services.math_parser import MathInputTooLong
from app.services.math_worker import MathWorkerError
from app.services.preview_check import check_answer

router = APIRouter(prefix="/preview", tags=["untracked preview"])
TTL = 3600
MAX_SESSIONS = 256
MAX_PROBLEMS = 200
_lock = Lock()
_requests: deque[float] = deque()


@dataclass
class Session:
    expires: float
    problems: dict[str, Exercise] = field(default_factory=dict)
    bags: dict[tuple[str, int], list[int]] = field(default_factory=dict)
    previous: dict[tuple[str, int], int] = field(default_factory=dict)


_sessions: dict[str, Session] = {}
# ponytail: one-process, one-hour preview only; persistent authenticated practice is #10.


class Generate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    topic: Literal["basic-integrals", "substitution"]
    difficulty: int = Field(ge=1, le=2)


class Attempt(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    answer: str = Field(min_length=1, max_length=256)


def _session(authorization: str) -> Session:
    # Caller holds _lock. Fixed global admission limit also bounds token churn.
    now = time.monotonic()
    while _requests and _requests[0] <= now - 60:
        _requests.popleft()
    if len(_requests) >= 120:
        raise HTTPException(429, "rate_limited", headers={"Retry-After": "60"})
    _requests.append(now)
    for token in tuple(_sessions):
        if _sessions[token].expires <= now:
            del _sessions[token]
    token = authorization.removeprefix("Bearer ") if authorization.startswith("Bearer ") else ""
    session = _sessions.get(token)
    if session is None:
        raise HTTPException(401, "preview_session_expired")
    return session


@router.post("/sessions", status_code=201)
def start_session() -> dict[str, str]:
    with _lock:
        # Apply the same admission/pruning path even before a token exists.
        try:
            _session("")
        except HTTPException as exc:
            if exc.status_code != 401:
                raise
        if len(_sessions) >= MAX_SESSIONS:
            raise HTTPException(503, "preview_capacity", headers={"Retry-After": "60"})
        token = secrets.token_urlsafe(32)
        _sessions[token] = Session(time.monotonic() + TTL)
        return {"token": token}


@router.get("/topics")
def topics() -> dict[str, object]:
    return {
        "items": [
            {"slug": topic, "availableDifficulties": [1, 2]}
            for topic in ("basic-integrals", "substitution")
        ]
    }


@router.post("/problems", status_code=201)
def generate(body: Generate, authorization: Annotated[str, Header()] = "") -> dict[str, object]:
    with _lock:
        session = _session(authorization)
        if len(session.problems) >= MAX_PROBLEMS:
            raise HTTPException(409, "preview_session_full")
        cell = (body.topic, body.difficulty)
        exercises = catalogue(*cell)
        bag = session.bags.setdefault(cell, [])
        if not bag:
            bag.extend(range(len(exercises)))
            secrets.SystemRandom().shuffle(bag)
            if bag[-1] == session.previous.get(cell):
                bag[0], bag[-1] = bag[-1], bag[0]
        index = bag.pop()
        session.previous[cell] = index
        exercise = exercises[index]
        identifier = str(uuid4())
        session.problems[identifier] = exercise
        return {
            "id": identifier,
            "topic": body.topic,
            "difficulty": body.difficulty,
            "problemLatex": exercise.statement,
            "createdAt": datetime.now(UTC).isoformat(),
            "answerRevealed": False,
            "solutionRevealed": False,
            "lastResult": None,
            "lastAnswer": None,
        }


def _problem(identifier: str, authorization: str) -> Exercise:
    with _lock:
        problem = _session(authorization).problems.get(identifier)
        if problem is None:
            raise HTTPException(404, "problem_not_found")
        return problem


@router.post("/problems/{identifier}/attempts")
def attempt(
    identifier: str, body: Attempt, authorization: Annotated[str, Header()] = ""
) -> dict[str, str | None]:
    problem = _problem(identifier, authorization)
    try:
        result = check_answer(body.answer, problem.record)
    except MathInputTooLong as exc:
        raise HTTPException(422, "invalid_request") from exc
    except MathWorkerError as exc:
        raise HTTPException(503, "math_check_unavailable", headers={"Retry-After": "3"}) from exc
    return {
        "result": "incorrect" if result == "missing_constant" else result,
        "feedbackCode": "missing_constant" if result == "missing_constant" else None,
    }


@router.post("/problems/{identifier}/reveal-answer")
def answer(identifier: str, authorization: Annotated[str, Header()] = "") -> dict[str, str]:
    return {"answerLatex": _problem(identifier, authorization).answer}


@router.post("/problems/{identifier}/reveal-solution")
def solution(identifier: str, authorization: Annotated[str, Header()] = "") -> dict[str, object]:
    return {"steps": _problem(identifier, authorization).steps}
