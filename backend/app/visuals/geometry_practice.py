"""Progressive scenes from the same exact constructions as the revealed solution."""

import math
import re
from typing import Any

from app.engine.generators.geometry_practice import STEP_TEXT, GeometryObject, GeometryWork
from app.visuals.geometry import validate_geometry


def _label(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9 .,():/+=-]", " ", value).strip()[:120]


def _point(value: Any) -> tuple[float, float, float]:
    return tuple(float(x) for x in value)  # type: ignore[return-value]


def _add(a: Any, b: Any, factor: float = 1) -> tuple[float, float, float]:
    return tuple(x + factor * y for x, y in zip(a, b, strict=True))


def _unit(value: Any) -> tuple[float, float, float]:
    vector = _point(value)
    length = math.hypot(*vector)
    if length < 1e-12:
        raise ValueError("A line or plane needs a nonzero direction")
    return tuple(x / length for x in vector)  # type: ignore[return-value]


def _scene(
    work: GeometryWork,
    state: dict[Any, GeometryObject],
    given: set[Any],
    active: set[Any],
    omitted: bool = False,
    caption: str | None = None,
) -> dict[str, Any]:
    values = list(state.items())
    anchors = [_point(value.point) for _, value in values]
    span = max([1.0, *(abs(x) for point in anchors for x in point)])
    extent = max(3.0, min(10.0, span * 0.6))
    coverage = list(anchors)
    for _, value in values:
        point = _point(value.point)
        if value.kind in {"vector", "segment"}:
            coverage.append(_add(point, _point(value.vectors[0])))
        elif value.kind == "normal":
            coverage.append(_add(point, _unit(value.vectors[0]), min(3.0, extent)))
    planes = [key for key, value in values if value.kind == "plane"]
    # Once their intersection lines are established, old auxiliary patches can
    # obscure the new plane. Keep the four latest patches within the DTO budget.
    visible_planes = set(planes[-4:])
    points: dict[Any, dict[str, Any]] = {}
    lines = []
    faces = []

    def line(
        label: str, start: Any, end: Any, tone: str, arrow: bool = False, dashed: bool = False
    ) -> None:
        if math.dist(start, end) < 1e-10:
            return
        lines.append(
            dict(label=_label(label), start=start, end=end, tone=tone, arrow=arrow, dashed=dashed)
        )

    for key, value in values:
        tone = "active" if key in active else "given" if key in given else "previous"
        point = _point(value.point)
        label = _label(value.label)
        if value.kind == "point":
            at = tuple(round(x, 10) for x in point)
            if at in points:
                if label not in points[at]["label"].split(" = "):
                    points[at]["label"] += " = " + label
                if tone == "active":
                    points[at]["tone"] = tone
            else:
                points[at] = dict(label=label, at=point, tone=tone)
        elif value.kind in {"vector", "normal", "segment", "line"}:
            direction = _point(value.vectors[0])
            if value.kind == "line":
                direction = _unit(direction)
                along = []
                for anchor in coverage:
                    delta = tuple(b - a for a, b in zip(point, anchor, strict=True))
                    distance = sum(a * b for a, b in zip(delta, direction, strict=True))
                    if math.hypot(*_add(delta, direction, -distance)) < 1e-8:
                        along.append(distance)
                low = min([-extent * 1.4, *along]) - extent * 0.15
                high = max([extent * 1.4, *along]) + extent * 0.15
                line(
                    label,
                    _add(point, direction, low),
                    _add(point, direction, high),
                    tone,
                )
            elif value.kind == "normal":
                direction = _unit(direction)
                line(label, point, _add(point, direction, min(3.0, extent)), tone, arrow=True)
            else:
                line(
                    label,
                    point,
                    _add(point, direction),
                    tone,
                    arrow=value.kind == "vector",
                    dashed=value.kind == "segment",
                )
        elif value.kind == "plane" and key in visible_planes:
            a = _unit(value.vectors[0])
            b = _point(value.vectors[1])
            projection = sum(x * y for x, y in zip(a, b, strict=True))
            b = _unit(_add(b, a, -projection))
            normal = (
                a[1] * b[2] - a[2] * b[1],
                a[2] * b[0] - a[0] * b[2],
                a[0] * b[1] - a[1] * b[0],
            )
            in_plane = [
                tuple(y - x for x, y in zip(point, anchor, strict=True))
                for anchor in coverage
                if abs(sum((y - x) * n for x, y, n in zip(point, anchor, normal, strict=True)))
                < 1e-8
            ]
            extent_a = max(
                [
                    extent,
                    *(
                        abs(sum(x * y for x, y in zip(delta, a, strict=True))) + extent * 0.15
                        for delta in in_plane
                    ),
                ]
            )
            extent_b = max(
                [
                    extent,
                    *(
                        abs(sum(x * y for x, y in zip(delta, b, strict=True))) + extent * 0.15
                        for delta in in_plane
                    ),
                ]
            )
            vertices = [
                _add(_add(point, a, s * extent_a), b, t * extent_b)
                for s, t in ((-1, -1), (1, -1), (1, 1), (-1, 1))
            ]
            for indices in ((0, 1, 2), (0, 2, 3)):
                faces.append(dict(label=label, vertices=[vertices[i] for i in indices], tone=tone))
            for i in range(4):
                line(label, vertices[i], vertices[(i + 1) % 4], tone)
    description = "Givens only. " if not active else "Construction at this step. "
    description += "Patches and segments represent infinite objects. Normal arrows are scaled."
    if len(planes) > 4 or omitted:
        description = (
            "Earlier auxiliary constructions omitted for clarity. Normals are scaled. "
            "Planes and lines extend beyond their drawings."
        )
    if caption:
        description = caption + " Infinite planes and lines. Normals scaled."
        if omitted:
            description += " Auxiliaries omitted."
    return validate_geometry(
        dict(
            kind="geometry3d",
            version=1,
            title=_label(work.title),
            description=description,
            points=list(points.values()),
            lines=lines,
            faces=faces,
        )
    )


def render_work(work: GeometryWork) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    state = {(item.kind, item.label): item for item in work.givens}
    given = set(state)
    prompt = _scene(work, state, given, set())
    active: set[Any] = set()
    omitted = False
    caption = None
    steps = []
    for step in work.steps:
        if step.caption is not None:
            caption = step.caption
        if step.hide:
            removed = {key for key, value in state.items() if value.label in step.hide}
            state = {key: value for key, value in state.items() if key not in removed}
            active -= removed
            omitted = omitted or bool(removed)
        if step.objects:
            active = {(item.kind, item.label) for item in step.objects}
            state.update({(item.kind, item.label): item for item in step.objects})
        steps.append(
            dict(
                say=STEP_TEXT[step.key],
                latex=step.latex,
                visual=_scene(work, state, given, active, omitted, caption),
                rules=[
                    dict(
                        title=STEP_TEXT[step.key].removesuffix("."),
                        latex=step.rule,
                        explanation=step.explanation,
                    )
                ],
            )
        )
    return prompt, tuple(steps)
