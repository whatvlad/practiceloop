"""Problem reports (#38): an owner flags a faulty saved problem.

A report stores only the problem, one fixed category and an optional comment;
the account comes from the verified token and is kept only so a report goes
when the account or problem is deleted. The contract is docs/api/README.md
"Reports".
"""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app.api.practice import NO_NUL, RateLimiter, User, _not_found, _timestamp
from app.core.database import transaction

router = APIRouter(tags=["reports"])

# Reports are rare and read by people: a few a minute, a few dozen an hour.
burst_limit = RateLimiter(5)
hourly_limit = RateLimiter(30, window=3600.0)

Category = Literal["answer_check", "solution", "statement", "display", "other"]


class ReportBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    category: Category
    comment: str | None = Field(default=None, max_length=500, pattern=NO_NUL)


@router.post("/problems/{problem_id}/report", status_code=201)
def report(problem_id: UUID, body: ReportBody, user: User) -> JSONResponse:
    burst_limit.check(user.id)
    hourly_limit.check(user.id)
    comment = body.comment.strip() if body.comment else None
    with transaction(user.id) as conn:
        row = conn.execute(
            # Inserts only for the caller's own problem; nothing else is read or returned.
            "insert into private.problem_reports(problem_id, user_id, category, comment)"
            " select p.id, p.user_id, %s, %s from public.problems p"
            " where p.id = %s and p.user_id = %s"
            " returning id, created_at",
            (body.category, comment or None, problem_id, user.id),
        ).fetchone()
    if row is None:
        raise _not_found()
    report_id, created_at = row
    return JSONResponse(
        {
            "report": {
                "id": str(report_id),
                "category": body.category,
                "createdAt": _timestamp(created_at),
            }
        },
        status_code=201,
    )
