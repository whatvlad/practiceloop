"""Worksheet routes (#116, ADR-007) against real Postgres as the RLS-bypassing service role.

The PDF compile is stubbed here (the Database job has no TeX); tests/test_worksheet_tex.py
compiles for real. Run with PRACTICELOOP_TEST_DATABASE_URL=... python -m pytest -m db
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.api import practice, worksheets
from app.core import database
from app.core.auth import VerifiedUser, current_user
from app.generators.core import catalogue_records
from app.main import app
from app.services.worksheet_pdf import TexBusy, TexRenderError

pytestmark = pytest.mark.db


class Users:
    def __init__(self) -> None:
        self.alice = uuid4()
        self.bob = uuid4()
        self.current = self.alice


@pytest.fixture
def url() -> str:
    value = os.environ.get("PRACTICELOOP_TEST_DATABASE_URL")
    if not value:
        pytest.fail("PRACTICELOOP_TEST_DATABASE_URL is required for -m db")
    return value


@pytest.fixture
def users(url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[Users]:
    people = Users()
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute("insert into auth.users(id) values (%s), (%s)", (people.alice, people.bob))
    monkeypatch.setenv("DATABASE_URL", url)
    database.close_pool()
    for limiter in (
        practice.generation_limit,
        practice.attempt_limit,
        practice.reveal_limit,
        worksheets.create_minute_limit,
        worksheets.create_hour_limit,
        worksheets.render_limit,
    ):
        limiter.reset()
    app.dependency_overrides[current_user] = lambda: VerifiedUser(people.current, None)
    try:
        yield people
    finally:
        app.dependency_overrides.pop(current_user, None)
        database.close_pool()
        with psycopg.connect(url, autocommit=True) as conn:
            conn.execute("delete from auth.users where id in (%s, %s)", (people.alice, people.bob))


class Compiled:
    def __init__(self) -> None:
        self.sources: list[str] = []
        self.error: Exception | None = None


@pytest.fixture
def compiled(monkeypatch: pytest.MonkeyPatch) -> Compiled:
    seen = Compiled()

    def fake(tex: str) -> bytes:
        seen.sources.append(tex)
        if seen.error is not None:
            raise seen.error
        return b"%PDF-1.5 stub"

    monkeypatch.setattr(worksheets, "compile_pdf", fake)
    return seen


@pytest.fixture
def client(users: Users, compiled: Compiled) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def key() -> dict[str, str]:
    return {"Idempotency-Key": str(uuid4())}


def create(client: TestClient, body: dict[str, Any], status: int = 201) -> dict[str, Any]:
    response = client.post("/worksheets", json=body, headers=key())
    assert response.status_code == status, response.text
    return dict(response.json().get("worksheet") or response.json())


def generate(*groups: tuple[str, int, int], **options: Any) -> dict[str, Any]:
    return {
        "source": "generate",
        "groups": [{"topic": t, "difficulty": d, "count": c} for t, d, c in groups],
        **options,
    }


def rows(url: str, sql: str, *args: Any) -> list[tuple[Any, ...]]:
    with psycopg.connect(url) as conn:
        return conn.execute(sql, args).fetchall()


def make_problem(client: TestClient, topic: str = "basic-integrals", level: int = 1) -> str:
    response = client.post("/problems", json={"topic": topic, "difficulty": level}, headers=key())
    assert response.status_code == 201, response.text
    return str(response.json()["problem"]["id"])


# Generate


def test_generated_worksheet_saves_problems_items_and_reveals_with_the_key(
    client: TestClient, users: Users, url: str
) -> None:
    sheet = create(client, generate(("substitution", 3, 3), ("derivatives", 2, 2)))
    assert sheet["source"] == "generate" and sheet["answerKey"] is True
    assert (sheet["paper"], sheet["columns"]) == ("a4", 1)
    assert sheet["groups"] == [
        {"label": "Substitution, level 3", "topic": "substitution", "difficulty": 3,
         "requested": 3, "count": 3},
        {"label": "Derivatives, level 2", "topic": "derivatives", "difficulty": 2,
         "requested": 2, "count": 2},
    ]  # fmt: skip
    ids = sheet["problemIds"]
    assert len(ids) == len(set(ids)) == 5
    saved = rows(
        url,
        "select p.id::text, t.slug, p.difficulty, p.worksheet_id::text, p.answer_revealed,"
        " p.solution_revealed, i.position, i.group_index from public.problems p"
        " join public.topics t on t.id = p.topic_id"
        " join public.worksheet_items i on i.problem_id = p.id"
        " where p.user_id = %s order by i.position",
        users.alice,
    )
    assert [r[0] for r in saved] == ids
    assert [(r[1], r[2], r[7]) for r in saved] == [("substitution", 3, 0)] * 3 + [
        ("derivatives", 2, 1)
    ] * 2
    assert {r[3] for r in saved} == {sheet["id"]}
    assert all(r[4] and not r[5] for r in saved)
    assert [r[6] for r in saved] == [1, 2, 3, 4, 5]
    records = rows(
        url,
        "select s.generator_data from private.problem_solutions s"
        " join public.problems p on p.id = s.problem_id where p.user_id = %s",
        users.alice,
    )
    keys = [str(sorted(r[0].items())) for r in records]
    assert len(set(keys)) == 5


def test_without_the_key_no_reveal_flag_changes(client: TestClient, users: Users, url: str) -> None:
    create(client, generate(("basic-integrals", 1, 4), answerKey=False))
    assert rows(
        url, "select bool_or(answer_revealed) from public.problems where user_id = %s", users.alice
    ) == [(False,)]
    assert rows(
        url, "select answer_key from public.worksheets where user_id = %s", users.alice
    ) == [(False,)]


def test_groups_are_capped_at_their_cell_and_share_it(client: TestClient) -> None:
    size = len(catalogue_records("basic-integrals", 5))
    sheet = create(client, generate(("basic-integrals", 5, 20), ("basic-integrals", 5, 3)))
    assert [(g["requested"], g["count"]) for g in sheet["groups"]] == [(20, size), (3, 0)]
    assert len(sheet["problemIds"]) == size


def test_mixed_groups_draw_within_the_area(client: TestClient, url: str, users: Users) -> None:
    sheet = create(client, generate(("mixed:derivatives", 3, 10)))
    assert sheet["groups"][0]["label"] == "Mixed derivatives, level 3"
    assert sheet["groups"][0]["count"] == 10
    slugs = rows(
        url,
        "select distinct t.slug from public.problems p join public.topics t on t.id = p.topic_id"
        " where p.user_id = %s",
        users.alice,
    )
    assert {s[0] for s in slugs} <= {"derivatives", "partial-derivatives"}


def test_worksheet_problems_are_in_history_and_count_as_generated_once_attempted(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    plain = make_problem(client)
    sheet = create(client, generate(("basic-integrals", 2, 3)))
    items = client.get("/problems").json()["items"]
    assert {i["id"] for i in items} == {plain, *sheet["problemIds"]}
    assert {i["worksheetId"] for i in items if i["id"] != plain} == {sheet["id"]}
    assert next(i for i in items if i["id"] == plain)["worksheetId"] is None
    only = client.get("/problems", params={"worksheet": "true"}).json()["items"]
    assert {i["id"] for i in only} == set(sheet["problemIds"])
    assert client.get(f"/problems/{plain}").json()["problem"]["worksheetId"] is None
    assert client.get("/profile").json()["counts"]["generated"] == 1
    from app.services.math_worker import AnswerCheck

    monkeypatch.setattr(practice, "shared_check", lambda *_: AnswerCheck("incorrect"))
    attempt = client.post(
        f"/problems/{sheet['problemIds'][0]}/attempts", json={"answer": "x"}, headers=key()
    )
    assert attempt.status_code == 201, attempt.text
    assert client.get("/profile").json()["counts"] == {"generated": 2, "attempted": 1, "correct": 0}


@pytest.mark.parametrize(
    "body",
    [
        generate(("no-such-topic", 1, 1)),
        generate(("integration-by-parts", 4, 1)),
        generate(("substitution", 6, 1)),
        generate(("mixed", 1, 1)),
        generate(("mixed:geometry", 1, 1)),
        generate(("substitution", 1, 21)),
        generate(*[("substitution", 1, 5)] * 9),
        generate(*[("substitution", 1, 20)] * 3),
        generate(("substitution", 1, 1), paper="a3"),
        {"source": "history", "problemIds": [str(uuid4())] * 2},
    ],
)
def test_invalid_requests_are_422_and_write_nothing(
    client: TestClient, users: Users, url: str, body: dict[str, Any]
) -> None:
    response = client.post("/worksheets", json=body, headers=key())
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"
    assert rows(url, "select count(*) from public.worksheets where user_id = %s", users.alice) == [
        (0,)
    ]


def test_a_uuid4_idempotency_key_is_required(client: TestClient) -> None:
    body = generate(("substitution", 1, 1))
    assert client.post("/worksheets", json=body).status_code == 422
    assert (
        client.post("/worksheets", json=body, headers={"Idempotency-Key": "x"}).status_code == 422
    )


def test_an_exact_retry_returns_the_same_worksheet(
    client: TestClient, users: Users, url: str
) -> None:
    headers = key()
    body = generate(("substitution", 2, 3))
    first = client.post("/worksheets", json=body, headers=headers)
    again = client.post("/worksheets", json=body, headers=headers)
    assert first.status_code == again.status_code == 201
    assert again.headers["Idempotency-Replayed"] == "true"
    assert first.json() == again.json()
    assert rows(url, "select count(*) from public.problems where user_id = %s", users.alice) == [
        (3,)
    ]
    other = client.post("/worksheets", json=generate(("substitution", 2, 4)), headers=headers)
    assert other.status_code == 409
    assert other.json()["error"]["code"] == "idempotency_conflict"


def test_creation_is_rate_limited(client: TestClient) -> None:
    for _ in range(5):
        create(client, generate(("basic-integrals", 1, 1)))
    response = client.post("/worksheets", json=generate(("basic-integrals", 1, 1)), headers=key())
    assert response.status_code == 429 and response.headers["Retry-After"]


# History


def test_history_orders_by_catalogue_topic_then_level_then_oldest(
    client: TestClient, users: Users, url: str
) -> None:
    derivative = make_problem(client, "derivatives", 1)
    sub_new = make_problem(client, "substitution", 1)
    basic_two = make_problem(client, "basic-integrals", 2)
    sub_old = make_problem(client, "substitution", 1)
    basic_one = make_problem(client, "basic-integrals", 1)
    with psycopg.connect(url) as conn:
        conn.execute(
            "update public.problems set created_at = now() - interval '1 day' where id = %s",
            (sub_old,),
        )
    picked = [derivative, sub_new, basic_two, sub_old, basic_one]
    sheet = create(client, {"source": "history", "problemIds": picked, "answerKey": False})
    assert sheet["problemIds"] == [basic_one, basic_two, sub_old, sub_new, derivative]
    assert [(g["label"], g["count"], g["requested"]) for g in sheet["groups"]] == [
        ("Basic integrals, level 1", 1, 1),
        ("Basic integrals, level 2", 1, 1),
        ("Substitution, level 1", 2, 2),
        ("Derivatives, level 1", 1, 1),
    ]
    assert rows(
        url,
        "select count(*) from public.problems where user_id = %s"
        " and (answer_revealed or worksheet_id is not null)",
        users.alice,
    ) == [(0,)]


def test_history_with_the_key_reveals_answers_only_of_the_chosen_problems(
    client: TestClient, users: Users, url: str
) -> None:
    chosen, other = make_problem(client), make_problem(client)
    create(client, {"source": "history", "problemIds": [chosen]})
    revealed = rows(
        url, "select id::text, answer_revealed from public.problems where user_id = %s", users.alice
    )
    assert dict(revealed) == {chosen: True, other: False}


def test_a_foreign_or_missing_problem_fails_the_whole_request(
    client: TestClient, users: Users, url: str
) -> None:
    mine = make_problem(client)
    users.current = users.bob
    theirs = make_problem(client)
    users.current = users.alice
    for foreign in (theirs, str(uuid4())):
        response = client.post(
            "/worksheets", json={"source": "history", "problemIds": [mine, foreign]}, headers=key()
        )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "problem_not_found"
    assert rows(url, "select count(*) from public.worksheets") == [(0,)]
    assert rows(
        url, "select bool_or(answer_revealed) from public.problems where id = %s", mine
    ) == [(False,)]


# PDF


def test_pdf_download_renders_the_saved_worksheet_without_changing_flags(
    client: TestClient, compiled: Compiled, users: Users, url: str
) -> None:
    sheet = create(
        client,
        generate(("substitution", 3, 2), ("mixed:integrals", 1, 2), paper="letter", columns=2),
    )
    flags_before = rows(url, "select id, answer_revealed, solution_revealed from public.problems")
    response = client.get(f"/worksheets/{sheet['id']}/pdf")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    day = sheet["createdAt"][:10]
    assert response.headers["Content-Disposition"] == (
        f'attachment; filename="practiceloop-worksheet-{day}.pdf"'
    )
    assert response.content == b"%PDF-1.5 stub"
    tex = compiled.sources[-1]
    assert "letterpaper" in tex and "multicols*" in tex
    assert "\\section*{Substitution, level 3}" in tex
    assert "\\section*{Mixed integrals, level 1}" in tex
    assert "\\section*{Answers}" in tex and "\\plnumber{4}" in tex
    # Level 3 substitution: 4 cm base times 1.5.
    assert "\\rule{0pt}{6.00cm}" in tex
    assert rows(url, "select id, answer_revealed, solution_revealed from public.problems") == (
        flags_before
    )
    assert client.get(f"/worksheets/{sheet['id']}/pdf").status_code == 200


def test_pdf_without_the_key_has_no_answers(client: TestClient, compiled: Compiled) -> None:
    sheet = create(client, generate(("basic-integrals", 1, 2), answerKey=False))
    assert client.get(f"/worksheets/{sheet['id']}/pdf").status_code == 200
    assert "Answers" not in compiled.sources[-1]


def test_another_users_worksheet_is_not_found(client: TestClient, users: Users) -> None:
    sheet = create(client, generate(("basic-integrals", 1, 1)))
    users.current = users.bob
    for worksheet_id in (sheet["id"], str(uuid4())):
        response = client.get(f"/worksheets/{worksheet_id}/pdf")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "problem_not_found"


@pytest.mark.parametrize(
    ("error", "code"),
    [(TexBusy("busy"), "worksheet_busy"), (TexRenderError("bad"), "worksheet_render_failed")],
)
def test_render_failures_are_retryable_503s(
    client: TestClient, compiled: Compiled, error: Exception, code: str
) -> None:
    sheet = create(client, generate(("basic-integrals", 1, 1)))
    compiled.error = error
    response = client.get(f"/worksheets/{sheet['id']}/pdf")
    assert response.status_code == 503
    assert response.json()["error"] == {
        "code": code,
        "message": response.json()["error"]["message"],
        "retryable": True,
    }
    assert "bad" not in response.text


def test_a_deleted_problem_drops_out_of_its_worksheet(
    client: TestClient, compiled: Compiled, url: str
) -> None:
    sheet = create(client, generate(("basic-integrals", 1, 2)))
    with psycopg.connect(url) as conn:
        conn.execute("delete from public.problems where id = %s", (UUID(sheet["problemIds"][0]),))
    assert client.get(f"/worksheets/{sheet['id']}/pdf").status_code == 200
    assert "\\plnumber{2}" not in compiled.sources[-1]


# Worked solutions (#130)


def test_solutions_reveal_both_flags_and_print_steps_and_graphs(
    client: TestClient, compiled: Compiled, users: Users, url: str
) -> None:
    sheet = create(client, generate(("substitution", 1, 2), ("derivatives", 1, 1), solutions=True))
    assert sheet["solutions"] is True and sheet["answerKey"] is True
    assert rows(
        url,
        "select bool_and(answer_revealed and solution_revealed) from public.problems"
        " where user_id = %s",
        users.alice,
    ) == [(True,)]
    assert rows(url, "select solutions from public.worksheets where user_id = %s", users.alice) == [
        (True,)
    ]
    assert client.get(f"/worksheets/{sheet['id']}/pdf").status_code == 200
    tex = compiled.sources[-1]
    answers, solutions = tex.split("\\section*{Solutions}")
    assert "\\section*{Answers}" in answers
    assert [solutions.count(f"\\plnumber{{{n}}}") for n in (1, 2, 3)] == [1, 1, 1]
    assert "Set u equal to the inner expression." in solutions
    # Substitution has a visual; derivatives have none (ADR-006).
    assert solutions.count("\\pdfliteral") == 2


def test_history_solutions_without_the_key_still_reveal_both(
    client: TestClient, compiled: Compiled, users: Users, url: str
) -> None:
    chosen, other = make_problem(client), make_problem(client)
    sheet = create(
        client, {"source": "history", "problemIds": [chosen], "answerKey": False, "solutions": True}
    )
    flags = rows(
        url,
        "select id::text, answer_revealed, solution_revealed from public.problems"
        " where user_id = %s",
        users.alice,
    )
    assert {r[0]: (r[1], r[2]) for r in flags} == {chosen: (True, True), other: (False, False)}
    assert client.get(f"/worksheets/{sheet['id']}/pdf").status_code == 200
    assert "Answers" not in compiled.sources[-1]
    assert "\\section*{Solutions}" in compiled.sources[-1]


def test_without_solutions_nothing_extra_is_printed_or_revealed(
    client: TestClient, compiled: Compiled, users: Users, url: str
) -> None:
    sheet = create(client, generate(("substitution", 1, 1)))
    assert sheet["solutions"] is False
    revealed = "select bool_or(solution_revealed) from public.problems where user_id = %s"
    assert rows(url, revealed, users.alice) == [(False,)]
    assert client.get(f"/worksheets/{sheet['id']}/pdf").status_code == 200
    assert "Solutions" not in compiled.sources[-1] and "pdfliteral" not in compiled.sources[-1]


def test_graphs_stop_after_their_time_budget_but_steps_still_print(
    client: TestClient, compiled: Compiled, monkeypatch: pytest.MonkeyPatch
) -> None:
    sheet = create(client, generate(("substitution", 1, 2), solutions=True))
    monkeypatch.setattr(worksheets, "GRAPH_SECONDS", -1.0)
    assert client.get(f"/worksheets/{sheet['id']}/pdf").status_code == 200
    solutions = compiled.sources[-1].split("\\section*{Solutions}")[1]
    assert "pdfliteral" not in solutions and "Set u equal" in solutions
