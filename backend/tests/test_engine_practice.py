"""#169: the combinations topic served through the practice API on the new engine."""

from dataclasses import replace
from uuid import uuid4

import pytest

from app.api import practice
from app.core.auth import VerifiedUser
from app.engine import practice as engine
from app.services.math_parser import parse_math_input
from app.services.math_worker import check_answer
from app.visuals.spec import solution_payload


def test_combinations_is_listed_from_its_engine_entry_and_joins_algebra_mixed() -> None:
    body = practice.topics(VerifiedUser(uuid4(), None))
    item = next(item for item in body["items"] if item["slug"] == "combinations")
    assert item == {
        "slug": "combinations",
        "name": "Combinations",
        "area": "algebra",
        "availableDifficulties": [1],
        "worksheetCapacity": {"1": 0},
    }
    algebra = next(area for area in body["areas"] if area["slug"] == "algebra")
    # #191 (review decision 13): a published weight; worksheets wait for #192.
    assert algebra["mixed"]["weights"]["combinations"] == 1
    assert algebra["mixed"]["worksheetCapacity"]["1"] == sum(
        practice.capacity(slug, 1)
        for slug in (
            "matrices",
            "complex-numbers",
            "fundamental-theorem-algebra",
            "partial-fractions",
        )
    )
    assert "combinations" in practice.mixed_topics("algebra", 1)[0]
    assert "combinations" not in practice.mixed_topics("algebra", 1, worksheet=True)[0]


def test_a_served_entry_alone_lists_a_topic(monkeypatch: pytest.MonkeyPatch) -> None:
    """Acceptance of #191: the engine entry is the only code a new engine topic needs."""
    entry = replace(
        engine.ENGINE_TOPICS["combinations"], slug="counting", title="Counting", mixed_weight=3
    )
    monkeypatch.setitem(engine.ENGINE_TOPICS, "counting", entry)
    monkeypatch.setattr(practice, "TOPICS", practice.listed_topics(engine.ENGINE_TOPICS))
    body = practice.topics(VerifiedUser(uuid4(), None))
    item = next(item for item in body["items"] if item["slug"] == "counting")
    assert item == {
        "slug": "counting",
        "name": "Counting",
        "area": "algebra",
        "availableDifficulties": [1],
        "worksheetCapacity": {"1": 0},
    }
    algebra = next(area for area in body["areas"] if area["slug"] == "algebra")
    assert algebra["mixed"]["weights"]["counting"] == 3
    assert practice.TOPICS["counting"].space_cm == entry.space_cm


def test_a_served_entry_replaces_an_old_topic_of_its_slug_in_place() -> None:
    entry = replace(engine.ENGINE_TOPICS["combinations"], slug="matrices", title="Matrices")
    listed = practice.listed_topics({"matrices": entry})
    assert list(listed) == list(practice.listed_topics({}))
    assert listed["matrices"].levels == (1,)


def test_issue_stores_only_the_code_and_the_code_replays_the_problem() -> None:
    issued = engine.issue("combinations", 1, seed=1234)
    assert set(issued.record) == {"generator_version", "code"}
    assert issued.record["generator_version"] == "combinations-v1"
    assert str(issued.record["code"]).startswith("CMB-1-")
    assert engine.public_replay(issued.record) == issued
    assert engine.issue("combinations", 1, seed=1234) == issued
    assert issued.statement.startswith(r"\text{Calculate }\binom{")
    assert issued.steps[0]["say"] == "Evaluate the binomial coefficient."


def test_a_served_step_without_learner_text_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    generator = engine._registry().get("combinations-v1")
    monkeypatch.setattr(generator, "step_text", {"other": "Some other step."})
    with pytest.raises(ValueError, match="No learner text for step combinations"):
        engine.issue("combinations", 1, seed=1234)


@pytest.mark.parametrize("seed", range(40))
def test_every_seed_gives_a_checkable_problem(seed: int) -> None:
    issued = engine.issue("combinations", 1, seed=seed)
    answer = issued.answer_latex
    assert engine.check(issued.record, parse_math_input(answer)) == "correct"
    assert engine.check(issued.record, parse_math_input(f"{answer} + 1")) == "incorrect"
    assert solution_payload(issued.steps, issued.record) == {"steps": list(issued.steps)}


@pytest.mark.parametrize(
    "record",
    [
        {"generator_version": "combinations-v1"},
        {"generator_version": "derivative-v1", "code": "placeholder"},
        {"generator_version": "combinations-v1", "code": "CMB-1-0000000000000000-00", "x": 1},
        {"generator_version": "combinations-v1", "code": 7},
    ],
)
def test_unusable_records_are_rejected(record: dict[str, object]) -> None:
    if record.get("code") == "placeholder":
        record = {**record, "code": engine.issue("combinations", 1, seed=5).record["code"]}
    with pytest.raises(ValueError):
        engine.replay(record)


def test_a_mistyped_code_is_rejected() -> None:
    code = str(engine.issue("combinations", 1, seed=99).record["code"])
    digit = "1" if code[-4] != "1" else "2"
    broken = code[:-4] + digit + code[-3:]
    with pytest.raises(ValueError):
        engine.replay({"generator_version": "combinations-v1", "code": broken})


def test_statement_text_must_be_plain() -> None:
    assert engine.statement_latex(r"Find \(x\).") == r"\text{Find }x\text{.}"
    with pytest.raises(ValueError):
        engine.statement_latex(r"Find {x}.")


def test_the_worker_checks_a_new_engine_record() -> None:
    issued = engine.issue("combinations", 1, seed=7)
    assert check_answer(issued.answer_latex, issued.record).result == "correct"
    assert check_answer("1/2", issued.record).result == "incorrect"
    with pytest.raises(ValueError):
        check_answer("1", {"generator_version": "combinations-v1", "code": "CMB-1-1-00"})
