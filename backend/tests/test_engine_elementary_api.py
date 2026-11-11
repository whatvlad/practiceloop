"""Actual registered contracts across saved API, owner copies and private visuals."""

import sys
from contextlib import nullcontext
from dataclasses import replace
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from test_engine_analysis_limits import source as limit_source
from test_engine_elementary import source

from app.api import codes, practice, shares, worksheets
from app.core.auth import VerifiedUser, current_user
from app.engine import catalogue
from app.engine import practice as engine
from app.engine.answers.computational import (
    CategoryAnswer,
    OrderedAnswer,
    PeriodicSetAnswer,
    RealSetAnswer,
)
from app.engine.answers.logic import LogicAnswer
from app.engine.codes import parse_code
from app.engine.generators.analysis_limits import generators as limit_generators
from app.engine.generators.elementary import generators
from app.engine.opening import rebuild
from app.engine.topics.catalogue import Choice
from app.main import app
from app.math_input import parse_answer_input
from app.services import math_worker
from app.services.owned_records import AttemptRecord, ProblemRecord
from app.services.shares import SharedProblem
from app.services.worksheet_graphs import graph
from app.visuals.spec import _build, build_visual

REPRESENTATIVES = (
    "logic-negation-not",
    "logic-negation-equivalence",
    "domain-arcsin-square",
    "composition-reciprocal-square",
    "inverse-semicircle-branch",
    "inverse-exponential",
    "log-equation-quadratic",
    "trig-linearization-fourth",
    "trig-equation-cos-mixed",
    "trig-domain-tan-ratio",
    "trig-inequality-sine-cosine",
)


LIMIT_REPRESENTATIVES = {
    "SLAC",
    "FLAK",
    "FLBG",
    "INAA",
    "INAG",
    "INBM",
    "INBU",
    "INBX",
    "INCH",
    "INCL",
    "INCX",
    "INDF",
    "INDS",
    "INDT",
    "INDW",
    "INEK",
    "INES",
    "INET",
    "INFJ",
    "INFU",
    "INFV",
    "IPAE",
    "IPAF",
    "IPAT",
    "SRAA",
    "SRAC",
    "SRAD",
    "SRAY",
    "SRAZ",
    "SRBG",
    "SRBM",
    "SRBQ",
    "SRBS",
    "SRBV",
    "SRCD",
    "SRCH",
    "SRCL",
    "SRCP",
    "MVAB",
    "MVAF",
    "MVAH",
    "MVAL",
    "MVAQ",
    "MVAY",
    "MVBA",
    "MVBD",
    "MVBG",
    "MVBJ",
    "MVBN",
    "MVBP",
    "MVBQ",
    "MVBW",
    "MVCA",
    "MVCC",
    "MVCJ",
    "MVCN",
    "MVCX",
    "MVDA",
    "MVDC",
    "MVDH",
    "MVDJ",
    "MVDK",
    "MVDL",
    "DIAH",
    "DIAK",
    "DIAN",
    "DIAV",
    "DIAZ",
    "DIBF",
    "DIBK",
    "DIBP",
    "DIBR",
    "DIBY",
    "DICC",
    "DICF",
    "ODAB",
    "ODAE",
    "ODAK",
    "ODAO",
    "ODAT",
    "ODAX",
    "ODAZ",
    "LTAG",
    "LTAH",
    "LTAI",
    "LTAM",
    "LTAT",
    "LTAY",
    "LTBB",
    "LTBC",
}


@pytest.mark.parametrize(
    ("generator", "answer_source"),
    [
        *((g, source) for g in generators() if g.template in REPRESENTATIVES),
        *((g, limit_source) for g in limit_generators() if g.prefix in LIMIT_REPRESENTATIVES),
    ],
    ids=[g.template for g in generators() if g.template in REPRESENTATIVES]
    + [g.prefix for g in limit_generators() if g.prefix in LIMIT_REPRESENTATIVES],
)
def test_saved_generation_reopen_history_owner_copy_reveal_and_share_are_consistent(
    generator, answer_source, monkeypatch
):
    topic = next(
        t
        for t in engine.ENGINE_TOPICS.values()
        if any(c.generator == generator.version for group in t.levels.values() for c in group)
    )
    view = replace(topic, levels={generator.difficulty: (Choice(generator.version),)})
    stored = catalogue.build({topic.slug: view}, engine._registry(), pool_size=3)
    monkeypatch.setattr(catalogue, "load", lambda: stored)
    monkeypatch.setattr("app.main.load_engine_catalogue", lambda: stored)
    issued = stored.cells[0].problems[0].issued()
    opened = rebuild(str(issued.record["code"]))
    contract = generator.input_contract(generator.draw(int(issued.record["code"].split("-")[2])))
    descriptor = contract.public() if contract is not None else None
    expected_prompt = engine.prompt_visual(issued.record)
    monkeypatch.setattr(codes, "open_problem_code", lambda _: opened.model_dump_json().encode())
    codes._opened.cache_clear()
    _build.cache_clear()
    owners = (uuid4(), uuid4())
    acting = [owners[0]]
    problems, solutions, attempts = {}, {}, {}
    connection = SimpleNamespace(execute=lambda *_: None)

    def transaction(*args, **kwargs):
        return nullcontext(connection)

    def insert(_, owner, slug, level, statement, solution, *args):
        item = ProblemRecord(
            uuid4(),
            slug,
            level,
            statement,
            datetime.now(UTC),
            False,
            False,
            generator_data=solution.generator_data,
        )
        problems[owner, item.id] = item
        solutions[owner, item.id] = solution
        return item

    def reveal(_, owner, problem_id, kind):
        item = problems.get((owner, problem_id))
        if item is None:
            return None
        problems[owner, problem_id] = replace(item, **{kind + "_revealed": True})
        solution = solutions[owner, problem_id]
        return solution.answer_latex if kind == "answer" else solution.solution_steps

    def insert_attempt(_, owner, problem_id, text, correct, constant, feedback):
        if (owner, problem_id) not in problems:
            return None
        result = AttemptRecord(
            uuid4(), problem_id, text, correct, constant, datetime.now(UTC), feedback
        )
        attempts[owner, problem_id] = (result, 1)
        return result

    records = practice.records
    real_issue = engine.issue
    monkeypatch.setattr(
        engine, "issue", lambda slug, level, **kwargs: real_issue(slug, level, seed=0, **kwargs)
    )
    monkeypatch.setattr(practice, "transaction", transaction)
    monkeypatch.setattr(codes, "transaction", transaction)
    monkeypatch.setattr(records, "ensure_profile", lambda *_: None)
    monkeypatch.setattr(records, "recent_generator_data", lambda *_: [])
    monkeypatch.setattr(records, "insert_problem", insert)
    monkeypatch.setattr(records, "get_problem", lambda _, owner, key: problems.get((owner, key)))
    monkeypatch.setattr(
        records, "solution_for_check", lambda _, owner, key: solutions.get((owner, key))
    )
    monkeypatch.setattr(records, "insert_attempt", insert_attempt)
    monkeypatch.setattr(
        records,
        "list_problems",
        lambda _, owner, *args, **kwargs: [p for (who, _), p in problems.items() if who == owner],
    )
    monkeypatch.setattr(
        records,
        "attempt_summaries",
        lambda _, owner, ids: {
            key: attempts[owner, key] for key in ids if (owner, key) in attempts
        },
    )
    monkeypatch.setattr(records, "previously_revealed", lambda *_: {})
    monkeypatch.setattr(
        records, "reveal_answer", lambda conn, owner, key: reveal(conn, owner, key, "answer")
    )
    monkeypatch.setattr(
        records, "reveal_solution", lambda conn, owner, key: reveal(conn, owner, key, "solution")
    )
    monkeypatch.setattr(practice.shares, "active_share", lambda *_: None)
    monkeypatch.setattr(practice.idempotency, "claim", lambda *_: None)
    monkeypatch.setattr(practice.idempotency, "lookup", lambda *_: None)
    monkeypatch.setattr(practice.idempotency, "store", lambda *_: None)

    def checked(text, record):
        replayed = engine.replay(record)
        answer = replayed.answer
        tree = parse_answer_input(text, answer.kind, contract=getattr(answer, "contract", None))
        return math_worker.AnswerCheck(answer.check(tree))

    monkeypatch.setattr(practice, "shared_check", checked)
    for limiter in (
        practice.generation_limit,
        practice.attempt_limit,
        practice.reveal_limit,
        codes.lookup_limit,
    ):
        limiter.reset()
    app.dependency_overrides[current_user] = lambda: VerifiedUser(acting[0], None)
    try:
        with TestClient(app) as client:
            public = client.get("/codes", params={"code": issued.record["code"]}).json()
            public_fields = {"topic", "difficulty", "problemLatex"}
            if descriptor is not None:
                public_fields.add("answerInput")
            if expected_prompt is not None:
                public_fields.add("promptVisual")
            assert set(public["problem"]) == public_fields
            assert public["problem"].get("promptVisual") == expected_prompt
            assert public["problem"].get("answerInput") == descriptor
            response = client.post(
                "/problems",
                json={"topic": topic.slug, "difficulty": generator.difficulty},
                headers={"Idempotency-Key": str(uuid4())},
            )
            assert response.status_code == 201, response.text
            saved = response.json()["problem"]
            original_id = saved["id"]
            private = solutions[acting[0], UUID(original_id)]
            picked = engine.replay(private.generator_data)
            assert saved.get("answerInput") == descriptor
            assert saved.get("promptVisual") == engine.prompt_visual(private.generator_data)
            assert not {"visual", "answerLatex", "steps", "generator_data"}.intersection(saved)
            for restored in (
                client.get("/problems").json()["items"][0],
                client.get(f"/problems/{original_id}").json()["problem"],
            ):
                assert {key: restored[key] for key in saved} == saved
                assert set(restored) == set(saved) | {"attemptCount", "worksheetId"}
            attempt = client.post(
                f"/problems/{original_id}/attempts",
                json={"answer": answer_source(picked.answer)},
                headers={"Idempotency-Key": str(uuid4())},
            )
            assert (
                attempt.status_code == 201 and attempt.json()["attempt"]["result"] == "correct"
            ), attempt.text
            answer = client.post(f"/problems/{original_id}/reveal-answer")
            assert answer.json() == {"answerLatex": picked.answer.latex()}
            solution = client.post(f"/problems/{original_id}/reveal-solution")
            assert solution.status_code == 200, solution.text
            expected_visual = engine.pooled(private.generator_data).visual
            assert solution.json().get("visual") == expected_visual
            if expected_visual:
                assert "pdfliteral" in graph(expected_visual)
                detached = build_visual(private.generator_data)
                detached["title"] = "changed locally"
                assert build_visual(private.generator_data)["title"] != "changed locally"
            acting[0] = owners[1]
            assert client.get(f"/problems/{original_id}").status_code == 404
            assert client.post(f"/problems/{original_id}/reveal-solution").status_code == 404
            copied = client.post(
                "/codes/practice",
                json={"code": issued.record["code"]},
                headers={"Idempotency-Key": str(uuid4())},
            )
            assert copied.status_code == 201, copied.text
            copy = copied.json()["problem"]
            assert copy["id"] != original_id and copy.get("answerInput") == descriptor
            assert copy["problemLatex"] == issued.statement
            assert copy.get("promptVisual") == expected_prompt
            assert not copy["answerRevealed"] and not copy["solutionRevealed"]
            shared = shares._shared(
                SharedProblem(topic.slug, generator.difficulty, issued.statement, issued.record)
            )
            assert shared == public
            worksheet_statement, worksheet_solution = worksheets._prepare(issued.record)
            assert worksheet_statement == issued.statement
            assert worksheet_solution.generator_data == issued.record
            assert worksheet_solution.answer_latex == issued.answer_latex
            assert worksheet_solution.solution_steps == list(issued.steps)
    finally:
        app.dependency_overrides.pop(current_user, None)
        codes._opened.cache_clear()
        _build.cache_clear()


def wrong(answer):
    if isinstance(answer, CategoryAnswer):
        return next(choice for choice in answer.choices if choice != answer.expected)
    if isinstance(answer, LogicAnswer):
        return "!(" + source(answer) + ")"
    if isinstance(answer, RealSetAnswer):
        return "R" if source(answer) == "{}" else "{}"
    if isinstance(answer, PeriodicSetAnswer):
        return "(1;{})"
    if isinstance(answer, OrderedAnswer):
        return (
            "("
            + ";".join(
                [wrong(answer.components[0]), *(source(part) for part in answer.components[1:])]
            )
            + ")"
        )
    return "1" if answer.expected == 0 else "0"


@pytest.mark.parametrize(
    "template", ["logic-negation-not", "composition-reciprocal-square", "inverse-semicircle-branch"]
)
def test_public_descriptors_and_pooled_visuals_do_not_rebuild_symbolic_tasks(template, monkeypatch):
    generator = next(g for g in generators() if g.template == template)
    topic = next(
        t
        for t in engine.ENGINE_TOPICS.values()
        if any(c.generator == generator.version for choices in t.levels.values() for c in choices)
    )
    selected = replace(topic, levels={generator.difficulty: (Choice(generator.version),)})
    stored = catalogue.build({topic.slug: selected}, engine._registry(), pool_size=3)
    monkeypatch.setattr(catalogue, "load", lambda: stored)
    issued = stored.cells[0].problems[0].issued()
    parsed = parse_code(str(issued.record["code"]), engine._registry())
    descriptor = generator.input_contract(generator.draw(parsed.seed)).public()
    calls = []

    def profile(frame, event, arg):
        if event == "call" and frame.f_globals.get("__name__", "").startswith("sympy"):
            calls.append(frame.f_code.co_name)

    def forbidden(*args, **kwargs):
        pytest.fail("Symbolic task or visual regenerated in ordinary request")

    monkeypatch.setattr(type(generator), "build", forbidden)
    monkeypatch.setattr(type(generator), "solution_visual", forbidden)
    _build.cache_clear()
    previous = sys.getprofile()
    sys.setprofile(profile)
    try:
        assert engine.input_projection(issued.record) == {"answerInput": descriptor}
        assert engine.issue(topic.slug, generator.difficulty, seed=0) == issued
        assert build_visual(issued.record) == issued.visual
        assert (
            shares._shared(
                SharedProblem(topic.slug, generator.difficulty, issued.statement, issued.record)
            )["problem"]["answerInput"]
            == descriptor
        )
    finally:
        sys.setprofile(previous)
        _build.cache_clear()
    assert not calls


@pytest.mark.skipif(
    not sys.platform.startswith("linux"), reason="Actual Linux resource-limited child"
)
@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.template)
def test_actual_elementary_targets_and_wrong_results_fit_original_worker_limits(generator):
    task = generator.build(generator.draw(200))
    record = {"generator_version": generator.version, "code": task.code}
    assert math_worker.check_answer(source(task.answer), record).result == "correct"
    assert math_worker.check_answer(wrong(task.answer), record).result == "incorrect"
    assert math_worker.CPU_SECONDS == 2 and math_worker.ADDRESS_SPACE_BYTES == 256 * 1024 * 1024


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Actual Linux limited child")
@pytest.mark.parametrize("hash_seed", range(8))
def test_large_wrong_constant_never_constructs_an_exponential_root_in_the_worker(
    hash_seed, monkeypatch
):
    monkeypatch.setenv("PYTHONHASHSEED", str(hash_seed))
    generator = next(g for g in generators() if g.template == "inverse-exponential")
    task = generator.build(generator.draw(200))
    record = {"generator_version": generator.version, "code": task.code}
    answer = "(999999;" + ";".join(source(part) for part in task.answer.components[1:]) + ")"
    assert math_worker.check_answer(answer, record).result == "incorrect"
