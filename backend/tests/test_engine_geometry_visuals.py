"""The drawing must describe the same problem without revealing its solution."""

from copy import deepcopy
from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.api.practice import _public_problem
from app.api.shares import _shared
from app.engine import practice
from app.engine.generators.eigen_geometry import PointsParams, TetrahedronHeight
from app.engine.opening import rebuild
from app.services.owned_records import ProblemRecord
from app.services.shares import SharedProblem
from app.visuals import spec as visuals
from app.visuals.complex_plane import validate_visual

HEIGHT_CODE = "VTH-1-0000000000000000-07"


def height_record():
    opened = rebuild(HEIGHT_CODE)
    return opened.problem.issued().record


def test_rendered_problem_keeps_public_and_private_drawings_on_reopen() -> None:
    opened = rebuild(HEIGHT_CODE)
    issued = opened.problem.issued()

    public = getattr(issued, "statement_visual", None)
    assert public is not None
    assert {point["label"] for point in public["points"]} == {"A", "B", "C", "D"}
    assert all(step.get("visual") is not None for step in issued.steps)
    restored = type(opened).model_validate_json(opened.model_dump_json()).problem.issued()
    assert restored.statement_visual == public
    assert restored.steps == issued.steps


def test_drawing_cannot_be_attached_to_a_different_seeded_statement() -> None:
    generator = TetrahedronHeight()
    parameters = PointsParams(seed=0, points=((0, 0, 0), (1, 0, 0), (0, 1, 0), (2, 2, 1)))
    task = generator.build(parameters)
    assert generator.draw(0).points != parameters.points
    with pytest.raises(ValueError, match="does not match"):
        practice._public(task)


@pytest.mark.parametrize(
    "code",
    [
        "VTP-1-0000000000000000-26",
        "VTA-1-0000000000000000-21",
        "VTR-1-0000000000000000-14",
        "VTV-1-0000000000000000-89",
        HEIGHT_CODE,
    ],
)
def test_each_geometry_step_has_an_expandable_mathematical_explanation(code):
    issued = rebuild(code).problem.issued()
    for step in issued.steps:
        assert step.get("rules")
        assert all(
            rule["title"] and rule["latex"] and rule["explanation"] for rule in step["rules"]
        )


def test_history_and_share_return_only_the_given_geometry(monkeypatch) -> None:
    issued = rebuild(HEIGHT_CODE).problem.issued()
    monkeypatch.setattr(visuals.engine, "pooled", lambda _: issued)
    saved = ProblemRecord(
        id=UUID(int=1),
        topic="vectors",
        difficulty=5,
        problem_latex=issued.statement,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        answer_revealed=False,
        solution_revealed=False,
        generator_data=issued.record,
    )
    shared = SharedProblem("vectors", 5, issued.statement, issued.record)

    for problem in (_public_problem(saved, None), _shared(shared)["problem"]):
        visual = problem.get("statementVisual")
        assert visual is not None
        assert {point["label"] for point in visual["points"]} == {"A", "B", "C", "D"}
        assert "answer" not in problem and "solution" not in problem


@pytest.mark.parametrize(
    ("code", "point_labels", "line_labels"),
    [
        ("VTP-1-0000000000000000-26", set(), {"u", "v", "w"}),
        ("VTA-1-0000000000000000-21", {"A", "B", "C"}, {"AB", "AC", "BC"}),
        ("VTR-1-0000000000000000-14", {"A", "B", "C"}, {"AB", "AC", "BC"}),
        ("VTV-1-0000000000000000-89", {"A", "B", "C", "D"}, {"AB", "AC", "AD", "BC", "BD", "CD"}),
    ],
)
def test_existing_vector_problems_have_given_and_step_diagrams(code, point_labels, line_labels):
    issued = rebuild(code).problem.issued()
    visual = visuals.statement_visual(issued.record)
    assert visual is not None
    assert {point["label"] for point in visual["points"]} == point_labels
    assert {line["label"] for line in visual["lines"]} == line_labels
    assert validate_visual(visual) == visual
    solution = visuals.solution_payload(issued.steps, issued.record)
    assert all(step.get("visual") is not None for step in solution["steps"])


def test_triple_product_condition_uses_only_the_three_given_vectors():
    issued = rebuild("VTP-1-0000000000000000-26").problem.issued()
    visual = visuals.statement_visual(issued.record)
    assert visual is not None
    lines = {line["label"]: line for line in visual["lines"]}
    assert lines["u"]["end"] == [3, 1, -5]
    assert lines["v"]["end"] == [0, 5, 0]
    assert lines["w"]["end"] == [2, -3, 0]
    assert all(line["start"] == [0, 0, 0] and line["arrow"] for line in lines.values())


def test_height_statement_shows_only_given_vertices() -> None:
    visual = getattr(visuals, "statement_visual", lambda _: None)(height_record())

    assert visual is not None
    assert visual["kind"] == "geometry3d"
    points = {point["label"]: point["at"] for point in visual["points"]}
    assert points == {
        "A": [0, -5, -5],
        "B": [3, 1, -5],
        "C": [0, 5, 0],
        "D": [2, -3, 0],
    }
    assert "answer" not in visual
    assert "steps" not in visual
    assert validate_visual(visual) == visual

    malformed = deepcopy(visual)
    malformed["points"][0]["at"][0] = float("inf")
    with pytest.raises(ValueError):
        validate_visual(malformed)
    malformed = deepcopy(visual)
    malformed["answer"] = 4
    with pytest.raises(ValueError):
        validate_visual(malformed)


def test_height_foot_is_revealed_at_the_height_step() -> None:
    opened = rebuild(HEIGHT_CODE)
    issued = opened.problem.issued()
    result = visuals.solution_payload(issued.steps, issued.record)

    assert all(
        "H" not in {p["label"] for p in step.get("visual", {}).get("points", [])}
        for step in result["steps"][:-1]
    )
    visual = result["steps"][-1].get("visual")
    assert visual is not None
    points = {point["label"]: point["at"] for point in visual["points"]}
    assert points["H"] == pytest.approx([-2 / 3, -5 / 3, -8 / 3])
    assert any(line["label"] == "DH" for line in visual["lines"])
    # Here H is outside triangle ABC; the visible plane must extend to H.
    assert any(points["H"] in face["vertices"] for face in visual["faces"])
