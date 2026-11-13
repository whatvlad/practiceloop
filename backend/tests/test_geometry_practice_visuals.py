"""Diagrams follow the reveal order and the existing finite visual budgets."""

import json
import math

import pytest

from app.engine.generators.geometry_practice import MODES, GeometryPractice, geometry_seed
from app.visuals.geometry_practice import render_work


def labels(diagram):
    return {item["label"] for name in ("points", "lines", "faces") for item in diagram[name]}


def assert_visible_incidences(visual, infinite_labels):
    def delta(a, b):
        return [y - x for x, y in zip(a, b, strict=True)]

    def dot(a, b):
        return sum(x * y for x, y in zip(a, b, strict=True))

    visible = [point["at"] for point in visual["points"]]
    visible.extend(
        end
        for line in visual["lines"]
        if line["arrow"] or line["dashed"]
        for end in (line["start"], line["end"])
    )
    for line in visual["lines"]:
        if line["label"] not in infinite_labels:
            continue
        d = delta(line["start"], line["end"])
        for point in visible:
            v = delta(line["start"], point)
            t = dot(v, d) / dot(d, d)
            if math.hypot(*(a - t * b for a, b in zip(v, d, strict=True))) < 1e-7:
                assert -1e-7 <= t <= 1 + 1e-7
    seen = set()
    for face in visual["faces"]:
        if face["label"] in seen:
            continue
        seen.add(face["label"])
        a, b, c = face["vertices"]
        u, v = delta(a, b), delta(b, c)
        n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        for point in visible:
            difference = delta(a, point)
            if abs(dot(difference, n)) / math.hypot(*n) < 1e-7:
                s, t = dot(difference, u) / dot(u, u), dot(difference, v) / dot(v, v)
                assert -1e-7 <= s <= 1 + 1e-7 and -1e-7 <= t <= 1 + 1e-7


@pytest.mark.parametrize("level", [1, 2, 3])
@pytest.mark.parametrize(
    ("mode", "variation", "line_label"),
    [
        ("line-plane-intersection", 0, "l"),
        ("line-line-intersection", 1, "m"),
        ("directed-point-plane-projection", 0, "projection ray"),
    ],
)
def test_visible_infinite_line_reaches_its_constructed_incident_point(
    mode, variation, line_label, level
):
    generator = GeometryPractice(mode)
    _, steps = render_work(generator.work(generator.draw(geometry_seed(level, variation))))
    visual = steps[-1]["visual"]
    foot = next(p["at"] for p in visual["points"] if "H" in p["label"].split(" = "))
    line = next(line for line in visual["lines"] if line["label"] == line_label)
    direction = [b - a for a, b in zip(line["start"], line["end"], strict=True)]
    delta = [b - a for a, b in zip(line["start"], foot, strict=True)]
    t = sum(x * y for x, y in zip(delta, direction, strict=True)) / sum(x * x for x in direction)
    assert math.sqrt(sum((a - t * b) ** 2 for a, b in zip(delta, direction, strict=True))) < 1e-7
    assert 0 <= t <= 1


@pytest.mark.parametrize("level", [1, 2, 3])
def test_visible_plane_reaches_the_endpoints_satisfying_its_constraint(level):
    generator = GeometryPractice("constrained-vector")
    _, steps = render_work(generator.work(generator.draw(geometry_seed(level, 1))))
    visual = steps[-1]["visual"]
    face = next(f for f in visual["faces"] if f["label"] == "endpoint plane")
    a, b, c = face["vertices"]
    first = [y - x for x, y in zip(a, b, strict=True)]
    second = [y - x for x, y in zip(b, c, strict=True)]
    for line in visual["lines"]:
        if line["label"] not in {"x one", "x two"}:
            continue
        delta = [y - x for x, y in zip(a, line["end"], strict=True)]
        s = sum(x * y for x, y in zip(delta, first, strict=True)) / sum(x * x for x in first)
        t = sum(x * y for x, y in zip(delta, second, strict=True)) / sum(x * x for x in second)
        assert 0 <= s <= 1 and 0 <= t <= 1


@pytest.mark.parametrize(
    "mode", ["planes-common-point", "planes-common-line", "planes-three-lines"]
)
def test_three_plane_parameter_cases_add_the_third_plane_only_after_its_parameters_are_known(mode):
    generator = GeometryPractice(mode)
    work = generator.work(generator.draw(geometry_seed(3, 1)))
    statement, steps = render_work(work)
    assert "pi three" not in labels(statement)
    index = next(i for i, step in enumerate(work.steps) if step.key == "constraints")
    assert all("pi three" not in labels(step["visual"]) for step in steps[:index])
    assert "pi three" in labels(steps[index]["visual"])
    assert "Diagram" in work.steps[-1].latex
    assert "Example: a=" in steps[-1]["visual"]["description"]
    assert not {"A", "B", "E", "F", "EF"} & labels(steps[-1]["visual"])
    assert r"E=" in work.statement and r"F=" in work.statement
    if mode == "planes-three-lines":
        assert {"l12", "l13", "l23"} <= labels(steps[-1]["visual"])
    elif mode == "planes-common-point":
        assert "S" in labels(steps[-1]["visual"])


@pytest.mark.parametrize("mode", ["parallel-parameter", "normal-parameters"])
def test_parameter_dependent_objects_are_drawn_after_their_parameters_are_solved(mode):
    generator = GeometryPractice(mode)
    work = generator.work(generator.draw(geometry_seed(3, 1)))
    statement, steps = render_work(work)
    assert not statement["faces"]
    index = next(
        i
        for i, step in enumerate(work.steps)
        if step.key == ("result" if mode == "normal-parameters" else "parameter")
    )
    assert not any(step["visual"]["faces"] for step in steps[:index])
    assert steps[index]["visual"]["faces"]
    if mode == "normal-parameters":
        assert "l" in labels(steps[index]["visual"])


def test_parallel_line_distance_does_not_use_unstated_midpoint_endpoints():
    generator = GeometryPractice("parallel-line-distance")
    work = generator.work(generator.draw(geometry_seed(3, 1)))
    assert not any(step.key == "midpoint" for step in work.steps)


def test_completed_line_projection_keeps_the_main_objects_without_preparation_clutter():
    generator = GeometryPractice("directed-line-plane-projection")
    work = generator.work(generator.draw(geometry_seed(3, 1)))
    statement, steps = render_work(work)
    assert "l plane one" in labels(statement)
    final = steps[-1]["visual"]
    assert {"l", "pi", "image line", "H", "S"} <= labels(final)
    assert not {
        "l plane one",
        "l plane two",
        "A",
        "B",
        "C",
        "D",
        "u",
        "v",
        "projected direction",
    } & labels(final)
    assert "omitted for clarity" in final["description"]


def test_reflection_foot_and_image_do_not_leak_into_the_statement_or_earlier_steps():
    generator = GeometryPractice("line-reflection")
    work = generator.work(generator.draw(geometry_seed(1, 0)))
    statement, steps = render_work(work)
    assert not any("H" == x or "R" == x for x in labels(statement))
    foot_index = next(i for i, s in enumerate(work.steps) if s.key == "project")
    image_index = next(i for i, s in enumerate(work.steps) if s.key == "reflect")
    assert all("H" not in labels(s["visual"]) for s in steps[:foot_index])
    assert all("R" not in labels(s["visual"]) for s in steps[:image_index])
    assert "H" in labels(steps[foot_index]["visual"])
    assert "R" in labels(steps[image_index]["visual"])
    assert any(
        p["label"] == "R" and p["tone"] == "active" for p in steps[image_index]["visual"]["points"]
    )


def test_sought_plane_is_not_drawn_as_given_geometry():
    generator = GeometryPractice("plane-equation")
    statement, steps = render_work(generator.work(generator.draw(geometry_seed(3, 0))))
    assert not statement["faces"]
    assert any(s["visual"]["faces"] for s in steps)


def test_engine_render_attaches_private_steps_and_a_givens_only_statement_diagram():
    from app.engine.generators.catalogue import registry
    from app.engine.rendering import render

    generator = GeometryPractice("plane-reflection")
    task = generator.build(generator.draw(geometry_seed(2, 0)))
    issued = render(task, registry())
    assert issued.statement_visual is not None
    assert not {"H", "R"} & labels(issued.statement_visual)
    assert len(issued.steps) == len(task.steps)
    assert all(step.get("rules") and step.get("visual") for step in issued.steps)
    assert issued.record == {"generator_version": task.generator_version, "code": task.code}


def test_reopening_projects_the_prepared_statement_without_symbolic_reconstruction(monkeypatch):
    from app.engine import practice
    from app.engine.generators.catalogue import registry
    from app.engine.rendering import render
    from app.visuals.spec import statement_projection, statement_visual

    generator = GeometryPractice("plane-reflection")
    issued = render(generator.build(generator.draw(geometry_seed(2, 0))), registry())
    monkeypatch.setattr(practice, "pooled", lambda record: issued)

    def forbidden(*args, **kwargs):
        raise AssertionError("Reopening a prepared problem must not rebuild its mathematics")

    monkeypatch.setattr(GeometryPractice, "draw", forbidden)
    assert statement_projection(issued.record) == {"statementVisual": issued.statement_visual}
    assert statement_visual(issued.record) == issued.statement_visual


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("level", [1, 2, 3])
def test_each_supported_visual_has_bounded_valid_data_and_explained_matching_steps(mode, level):
    generator = GeometryPractice(mode)
    work = generator.work(generator.draw(geometry_seed(level, 5)))
    named_points = {}
    for item in [*work.givens, *(o for s in work.steps for o in s.objects)]:
        if item.kind == "point":
            if item.label in named_points:
                assert named_points[item.label] == item.point
            named_points[item.label] = item.point
    statement, steps = render_work(work)
    assert len(steps) == len(work.steps)
    assert all(s["rules"] and s["say"] and s["latex"] for s in steps)
    infinite_labels = {
        item.label
        for item in (*work.givens, *(o for s in work.steps for o in s.objects))
        if item.kind == "line"
    }
    for visual in [statement, *(s["visual"] for s in steps)]:
        assert visual["kind"] == "geometry3d"
        assert visual["points"] or visual["lines"] or visual["faces"]
        assert (
            len(visual["points"]) <= 16 and len(visual["lines"]) <= 32 and len(visual["faces"]) <= 8
        )
        assert len(json.dumps(visual).encode()) <= 8192
        assert visual["title"] and visual["description"]
        assert_visible_incidences(visual, infinite_labels)
