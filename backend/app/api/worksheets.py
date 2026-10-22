"""ADR-007 printable worksheets (#116): create one, then download it as a PDF.

POST picks or loads the problems, saves the worksheet and sets reveal flags in
one transaction; GET only reads and renders, so it can be retried and repeated.
The contract is docs/api/README.md "Worksheets".
"""

from __future__ import annotations

import logging
import secrets
from datetime import UTC
from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.api.practice import (
    AREAS,
    MIXED,
    TOPICS,
    IdempotencyKey,
    RateLimiter,
    User,
    _idempotency_key,
    _invalid,
    _mixed,
    _not_found,
    _respond,
    _timestamp,
    mixed_topics,
)
from app.core.database import transaction
from app.core.errors import ApiError
from app.generators.core import replay
from app.services import idempotency
from app.services import owned_records as records
from app.services import worksheets as store
from app.services.idempotency import Scope, StoredResponse
from app.services.worksheet_pdf import (
    PrintedGroup,
    PrintedProblem,
    TexBusy,
    TexRenderError,
    compile_pdf,
    filename,
    render_tex,
)

logger = logging.getLogger("practiceloop.worksheets")
router = APIRouter(tags=["worksheets"])

MAX_GROUPS = 8
MAX_PER_GROUP = 20
MAX_PROBLEMS = 40
UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

create_minute_limit = RateLimiter(5)
create_hour_limit = RateLimiter(30, window=3600.0)
render_limit = RateLimiter(20)
_RANDOM = secrets.SystemRandom()


class GroupBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    # A topic slug, or "mixed:<area>" for mixed practice within one area.
    topic: str = Field(min_length=1, max_length=64)
    difficulty: int
    count: int = Field(ge=1, le=MAX_PER_GROUP)


class WorksheetBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    source: Literal["generate", "history"]
    groups: list[GroupBody] | None = Field(default=None, min_length=1, max_length=MAX_GROUPS)
    problemIds: (  # noqa: N815 - the JSON field name
        list[Annotated[str, Field(pattern=UUID_PATTERN)]] | None
    ) = Field(default=None, min_length=1, max_length=MAX_PROBLEMS)
    paper: Literal["a4", "letter"] = "a4"
    columns: Literal[1, 2] = 1
    answerKey: bool = True  # noqa: N815 - the JSON field name

    @model_validator(mode="after")
    def _one_source(self) -> WorksheetBody:
        if self.source == "generate":
            if self.groups is None or self.problemIds is not None:
                raise ValueError("generate takes groups")
            if sum(group.count for group in self.groups) > MAX_PROBLEMS:
                raise ValueError("too many problems")
        elif self.problemIds is None or self.groups is not None:
            raise ValueError("history takes problemIds")
        elif len(set(self.problemIds)) != len(self.problemIds):
            raise ValueError("repeated problem")
        return self


def label(topic: str, difficulty: int) -> str:
    """'Substitution, level 2' or 'Mixed integrals, level 3' (catalogue text only)."""
    if topic.startswith(MIXED + ":"):
        name = "Mixed " + AREAS[topic.removeprefix(MIXED + ":")].lower()
    else:
        name = TOPICS[topic].name
    return f"{name}, level {difficulty}"


def _space_cm(topic: str, difficulty: int) -> float:
    return TOPICS[topic].space_cm * (1 + 0.25 * (difficulty - 1))


def _check_group(group: GroupBody) -> None:
    if group.topic.startswith(MIXED + ":"):
        area = group.topic.removeprefix(MIXED + ":")
        if area not in AREAS or _mixed(area) is None or not mixed_topics(area, group.difficulty)[0]:
            raise _invalid()
        return
    cell = TOPICS.get(group.topic)
    if cell is None or group.difficulty not in cell.levels:
        raise _invalid()


def _limit(user_id: UUID) -> None:
    create_minute_limit.check(user_id)
    create_hour_limit.check(user_id)


def _response(worksheet: store.Worksheet, problem_ids: list[UUID]) -> StoredResponse:
    return StoredResponse(
        201,
        {
            "worksheet": {
                "id": str(worksheet.id),
                "source": worksheet.source,
                "createdAt": _timestamp(worksheet.created_at),
                "paper": worksheet.paper,
                "columns": worksheet.columns,
                "answerKey": worksheet.answer_key,
                "groups": [
                    {
                        "label": label(group["topic"], group["difficulty"]),
                        "topic": group["topic"],
                        "difficulty": group["difficulty"],
                        "requested": group["requested"],
                        "count": group["count"],
                    }
                    for group in worksheet.groups
                ],
                "problemIds": [str(problem_id) for problem_id in problem_ids],
            }
        },
    )


@router.post("/worksheets", status_code=201)
def create_worksheet(body: WorksheetBody, user: User, key: IdempotencyKey = None) -> JSONResponse:
    scope = Scope(
        user.id,
        "POST",
        "/worksheets",
        _idempotency_key(key),
        idempotency.request_hash(body.model_dump(exclude_none=True, mode="json")),
    )
    if body.groups is not None:
        for group in body.groups:
            _check_group(group)
    with transaction(user.id) as conn:
        stored = idempotency.lookup(conn, scope)
    if stored is not None:
        return _respond(stored, replayed=True)
    _limit(user.id)
    if body.source == "generate":
        return _generate(body, user.id, scope)
    return _from_history(body, user.id, scope)


def _generate(body: WorksheetBody, user_id: UUID, scope: Scope) -> JSONResponse:
    assert body.groups is not None  # noqa: S101 - checked by the model
    # Pick and replay before the transaction: replay is CPU work and needs no connection.
    picker = store.Picker(_RANDOM)
    picked: list[tuple[int, str, dict[str, object]]] = []
    groups: list[dict[str, Any]] = []
    for index, group in enumerate(body.groups):
        count = 0
        for _ in range(group.count):
            if group.topic.startswith(MIXED + ":"):
                area = group.topic.removeprefix(MIXED + ":")
                topics, weights = mixed_topics(area, group.difficulty)
                drawn = picker.pick_mixed(topics, weights, group.difficulty)
            else:
                record = picker.pick(group.topic, group.difficulty)
                drawn = None if record is None else (group.topic, record)
            if drawn is None:
                break
            picked.append((index, *drawn))
            count += 1
        groups.append(
            {
                "topic": group.topic,
                "difficulty": group.difficulty,
                "requested": group.count,
                "count": count,
            }
        )
    exercises = [(index, topic, replay(record)) for index, topic, record in picked]
    with transaction(user_id) as conn:
        records.ensure_profile(conn, user_id)
        stored = idempotency.claim(conn, scope)
        if stored is not None:
            return _respond(stored, replayed=True)
        worksheet = store.insert_worksheet(
            conn,
            user_id,
            source="generate",
            paper=body.paper,
            columns=body.columns,
            answer_key=body.answerKey,
            groups=groups,
        )
        items: list[tuple[UUID, int]] = []
        for index, topic, exercise in exercises:
            problem = records.insert_problem(
                conn,
                user_id,
                topic,
                exercise.difficulty,
                exercise.statement,
                records.PrivateSolution(
                    generator_version=str(exercise.record["generator_version"]),
                    generator_data=exercise.record,
                    answer_latex=exercise.answer,
                    solution_steps=list(exercise.steps),
                ),
                worksheet_id=worksheet.id,
            )
            items.append((problem.id, index))
        store.insert_items(conn, worksheet.id, items)
        if body.answerKey:
            store.reveal_answers(conn, user_id, [problem_id for problem_id, _ in items])
        response = _response(worksheet, [problem_id for problem_id, _ in items])
        idempotency.store(conn, scope, response)
    return _respond(response)


_TOPIC_ORDER = {slug: n for n, slug in enumerate(TOPICS)}
_AREA_ORDER = {area: n for n, area in enumerate(AREAS)}


def _print_order(problem: store.OwnedProblem) -> tuple[Any, ...]:
    """ADR-007: catalogue area and topic order, then level, then oldest first."""
    topic = TOPICS.get(problem.topic)
    area = _AREA_ORDER.get(topic.area, len(AREAS)) if topic else len(AREAS)
    position = _TOPIC_ORDER.get(problem.topic, len(TOPICS))
    return (area, position, problem.difficulty, problem.created_at, problem.id)


def _from_history(body: WorksheetBody, user_id: UUID, scope: Scope) -> JSONResponse:
    assert body.problemIds is not None  # noqa: S101 - checked by the model
    wanted = [UUID(value) for value in body.problemIds]
    with transaction(user_id) as conn:
        records.ensure_profile(conn, user_id)
        stored = idempotency.claim(conn, scope)
        if stored is not None:
            return _respond(stored, replayed=True)
        owned = store.owned_problems(conn, user_id, wanted)
        if len(owned) != len(wanted):
            # Rolls back the key too: no partial worksheet, and a fixed retry may run.
            raise _not_found()
        owned.sort(key=_print_order)
        groups: list[dict[str, Any]] = []
        items: list[tuple[UUID, int]] = []
        for problem in owned:
            last = groups[-1] if groups else None
            if last is None or (last["topic"], last["difficulty"]) != (
                problem.topic,
                problem.difficulty,
            ):
                last = {"topic": problem.topic, "difficulty": problem.difficulty, "count": 0}
                groups.append(last)
            last["count"] += 1
            items.append((problem.id, len(groups) - 1))
        for group in groups:
            group["requested"] = group["count"]
        worksheet = store.insert_worksheet(
            conn,
            user_id,
            source="history",
            paper=body.paper,
            columns=body.columns,
            answer_key=body.answerKey,
            groups=groups,
        )
        store.insert_items(conn, worksheet.id, items)
        if body.answerKey:
            store.reveal_answers(conn, user_id, [problem_id for problem_id, _ in items])
        response = _response(worksheet, [problem_id for problem_id, _ in items])
        idempotency.store(conn, scope, response)
    return _respond(response)


@router.get("/worksheets/{worksheet_id}/pdf")
def download_pdf(worksheet_id: UUID, user: User) -> Response:
    render_limit.check(user.id)
    with transaction(user.id, read_only=True) as conn:
        worksheet = store.get_worksheet(conn, user.id, worksheet_id)
        if worksheet is None:
            raise _not_found()
        items = store.print_items(conn, user.id, worksheet_id)
    groups = [
        PrintedGroup(
            label(group["topic"], group["difficulty"]),
            [
                PrintedProblem(
                    item.problem_latex,
                    item.answer_latex,
                    _space_cm(item.topic, item.difficulty),
                )
                for item in items
                if item.group_index == index
            ],
        )
        for index, group in enumerate(worksheet.groups)
    ]
    day = worksheet.created_at.astimezone(UTC).date()
    tex = render_tex(
        [group for group in groups if group.problems],
        paper=worksheet.paper,
        columns=worksheet.columns,
        answer_key=worksheet.answer_key,
        day=day,
    )
    try:
        pdf = compile_pdf(tex)
    except TexBusy:
        raise ApiError(
            503,
            "worksheet_busy",
            "Another worksheet is being prepared. Try again in a moment.",
            retryable=True,
            headers={"Retry-After": "5"},
        ) from None
    except TexRenderError as exc:
        logger.error("Worksheet %s failed to render: %s", worksheet.id, exc)
        raise ApiError(
            503,
            "worksheet_render_failed",
            "The worksheet couldn't be prepared. Try again.",
            retryable=True,
        ) from None
    return Response(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename(day)}"'},
    )
