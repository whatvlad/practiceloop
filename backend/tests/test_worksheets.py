"""ADR-007 worksheet picker and template (#116), without a database or TeX."""

from __future__ import annotations

import random
from datetime import date

import pytest

from app.api import practice
from app.api.worksheets import WorksheetBody, label
from app.generators.core import catalogue_records
from app.services.worksheet_pdf import (
    PrintedGroup,
    PrintedProblem,
    PrintedStep,
    escape_text,
    render_tex,
)
from app.services.worksheets import Picker, base_key, record_key


def picker(seed: int = 7) -> Picker:
    return Picker(random.Random(seed))  # noqa: S311 - deterministic tests


def test_a_cell_is_used_up_without_repeats_and_then_capped() -> None:
    pick = picker()
    cell = catalogue_records("basic-integrals", 5)
    taken = [pick.pick("basic-integrals", 5) for _ in range(len(cell))]
    assert all(record is not None for record in taken)
    assert len({record_key(r) for r in taken if r}) == len(cell)
    assert pick.pick("basic-integrals", 5) is None


@pytest.mark.parametrize(("topic", "level"), [("substitution", 3), ("substitution", 1)])
def test_distinct_base_problems_come_before_coefficient_variants(topic: str, level: int) -> None:
    pick = picker()
    cell = catalogue_records(topic, level)
    bases = {base_key(record) for record in cell}
    assert len(bases) < len(cell), "the cell has coefficient variants"
    first = [pick.pick(topic, level) for _ in range(len(bases))]
    assert {base_key(r) for r in first if r} == bases


def test_substitution_v1_variants_differ_only_in_a() -> None:
    record = dict(catalogue_records("substitution", 1)[0])
    other = {**record, "a": -int(str(record["a"]))}
    assert base_key(record) == base_key(other) and record_key(record) != record_key(other)


def test_groups_of_one_cell_share_it() -> None:
    pick = picker()
    size = len(catalogue_records("basic-integrals", 5))
    first = [pick.pick("basic-integrals", 5) for _ in range(size - 2)]
    second = [pick.pick("basic-integrals", 5) for _ in range(5)]
    assert all(first) and sum(r is not None for r in second) == 2


def test_mixed_draws_stay_in_the_area_and_skip_used_up_topics() -> None:
    pick = picker()
    topics, weights = practice.mixed_topics("derivatives", 5)
    size = sum(len(catalogue_records(t, 5)) for t in topics)
    drawn = [pick.pick_mixed(topics, weights, 5) for _ in range(size)]
    assert all(d is not None and d[0] in topics for d in drawn)
    assert len({record_key(d[1]) for d in drawn if d}) == size
    assert pick.pick_mixed(topics, weights, 5) is None


def test_capacity_is_the_cell_size() -> None:
    assert practice.capacity("basic-integrals", 5) == len(catalogue_records("basic-integrals", 5))


def test_labels_name_the_topic_or_the_mixed_area() -> None:
    assert label("substitution", 2) == "Substitution, level 2"
    assert label("mixed:integrals", 3) == "Mixed integrals, level 3"
    assert label("mixed:derivatives", 1) == "Mixed derivatives, level 1"


@pytest.mark.parametrize(
    "body",
    [
        {"source": "generate"},
        {"source": "generate", "groups": []},
        {"source": "generate", "groups": [{"topic": "substitution", "difficulty": 1, "count": 21}]},
        {"source": "generate", "groups": [{"topic": "substitution", "difficulty": 1, "count": 0}]},
        {"source": "generate", "groups": [{"topic": "substitution", "difficulty": 1}]},
        {
            "source": "generate",
            "groups": [{"topic": "substitution", "difficulty": 1, "count": 1}] * 9,
        },
        {
            "source": "generate",
            "groups": [{"topic": "substitution", "difficulty": 1, "count": 20}] * 3,
        },
        {"source": "history"},
        {"source": "history", "problemIds": []},
        {"source": "history", "problemIds": ["not-a-uuid"]},
        {"source": "history", "problemIds": ["0" * 8 + "-0000-4000-8000-" + "0" * 12] * 2},
        {
            "source": "history",
            "problemIds": [f"{n:08x}-0000-4000-8000-{n:012x}" for n in range(41)],
        },
        {
            "source": "history",
            "problemIds": ["00000000-0000-4000-8000-000000000001"],
            "groups": [{"topic": "substitution", "difficulty": 1, "count": 1}],
        },
        {
            "source": "history",
            "problemIds": ["00000000-0000-4000-8000-000000000001"],
            "paper": "a3",
        },
        {"source": "history", "problemIds": ["00000000-0000-4000-8000-000000000001"], "columns": 3},
        {"source": "history", "problemIds": ["00000000-0000-4000-8000-000000000001"], "title": "x"},
        {"source": "upload", "problemIds": ["00000000-0000-4000-8000-000000000001"]},
    ],
)
def test_invalid_shapes_and_limits_are_rejected(body: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        WorksheetBody.model_validate(body)


def test_defaults_match_the_adr() -> None:
    body = WorksheetBody.model_validate(
        {"source": "history", "problemIds": ["00000000-0000-4000-8000-000000000001"]}
    )
    assert (body.paper, body.columns, body.answerKey) == ("a4", 1, True)


def group(name: str, *answers: str, space: float = 3.0) -> PrintedGroup:
    return PrintedGroup(name, [PrintedProblem(f"\\int {a}\\,dx", a, space) for a in answers])


def tex(*groups: PrintedGroup, **options: object) -> str:
    settings: dict[str, object] = {"paper": "a4", "columns": 1, "answer_key": True}
    settings.update(options)
    return render_tex(groups, day=date(2026, 10, 22), **settings)  # type: ignore[arg-type]


def test_template_numbers_problems_through_the_whole_worksheet() -> None:
    source = tex(group("Substitution, level 2", "a", "b"), group("Basic integrals, level 1", "c"))
    assert "\\section*{Substitution, level 2}" in source
    assert "\\section*{Basic integrals, level 1}" in source
    assert [source.count(f"\\plnumber{{{n}}}") for n in (1, 2, 3, 4)] == [2, 2, 2, 0]
    assert source.index("Basic integrals") > source.index("\\plnumber{2}")


def test_answers_start_on_a_new_page_and_only_with_the_key() -> None:
    source = tex(group("Topic, level 1", "x^2 + C"))
    head, answers = source.split("\\clearpage\n\\section*{Answers}")
    assert "x^2 + C" in answers and "\\int x^2 + C" in head
    without = tex(group("Topic, level 1", "x^2 + C"), answer_key=False)
    assert "Answers" not in without and "\\clearpage" not in without
    assert "$x^2 + C$" not in without


def test_page_options_reach_the_preamble() -> None:
    assert "[a4paper,margin=2cm]{geometry}" in tex(group("T", "a"))
    assert "[letterpaper,margin=2cm]{geometry}" in tex(group("T", "a"), paper="letter")
    assert "multicols*" not in tex(group("T", "a"))
    assert "\\begin{multicols*}{2}" in tex(group("T", "a"), columns=2)
    with pytest.raises(ValueError):
        tex(group("T", "a"), paper="a3")
    with pytest.raises(ValueError):
        tex(group("T", "a"), columns=3)


def test_writing_space_follows_the_topic_and_level() -> None:
    from app.api.worksheets import _space_cm

    assert _space_cm("basic-integrals", 1) == 3
    assert _space_cm("triple-integrals", 5) == 14
    assert _space_cm("substitution", 3) == 6
    assert "\\rule{0pt}{6.00cm}" in tex(group("T", "a", space=_space_cm("substitution", 3)))


def test_every_topic_declares_a_writing_space() -> None:
    assert all(topic.space_cm > 0 for topic in practice.TOPICS.values())


def test_text_is_escaped() -> None:
    assert escape_text("50% & $x_1$ #{}") == r"50\% \& \$x\_1\$ \#\{\}"
    assert "\\section*{a\\textbackslash{}input}" in tex(group("a\\input", "x"))


# Worked solutions (#130)


def worked(answer: str, *steps: tuple[str, str], graph: str = "") -> PrintedGroup:
    printed = [PrintedStep(say, latex) for say, latex in steps]
    return PrintedGroup("T", [PrintedProblem(f"\\int {answer}", answer, 3, printed, graph)])


def test_solutions_are_off_by_default() -> None:
    one = {"topic": "substitution", "difficulty": 1, "count": 1}
    body = WorksheetBody.model_validate({"source": "generate", "groups": [one]})
    assert body.solutions is False
    assert "Solutions" not in tex(worked("a", ("Say.", "a = b")))


def test_solutions_follow_the_answers_on_a_new_page_with_steps_and_graph() -> None:
    source = tex(
        worked("v", ("Integrate 50% of θ.", "u = x"), ("Add C.", "x + C"), graph="PICTURE"),
        solutions=True,
    )
    answers, solutions = source.split("\\clearpage\n\\section*{Solutions}")
    assert "\\section*{Answers}" in answers
    assert "\\plnumber{1}" in solutions and "\\int v" in solutions
    assert "Integrate 50\\% of $\\theta$." in solutions
    assert solutions.index("u = x") < solutions.index("x + C") < solutions.index("PICTURE")


def test_solutions_print_without_the_answer_key() -> None:
    source = tex(worked("a", ("Say.", "a")), answer_key=False, solutions=True)
    assert "Answers" not in source and "\\section*{Solutions}" in source
