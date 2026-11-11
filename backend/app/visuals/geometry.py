"""Bounded, parameter-derived geometry for a problem and its solution steps."""

import json
from typing import Any, Literal

import sympy as sp
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.engine import practice as engine
from app.engine.codes import parse_code
from app.engine.generators.eigen_geometry import (
    AngleParameters,
    AreaParameters,
    AreaPractice,
    PerpendicularParameter,
    PerpendicularParameters,
    PointsParams,
    ScalarVectorExpression,
    SolidParameters,
    SolidPractice,
    TetrahedronHeight,
    TetrahedronVolume,
    TriangleAngle,
    TriangleAngleDegrees,
    TriangleArea,
    TripleProduct,
    VectorExpression,
    VectorExpressionParameters,
    VectorLengthParameters,
    VectorLengthPractice,
)
from app.visuals.plot2d import Finite, Label


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


Point3 = tuple[Finite, Finite, Finite]
Tone = Literal["given", "active", "previous"]


class Point(_Model):
    label: Label
    at: Point3
    tone: Tone = "given"


class Line(_Model):
    label: Label
    start: Point3
    end: Point3
    tone: Tone = "given"
    arrow: bool = False
    dashed: bool = False


class Face(_Model):
    label: Label
    vertices: tuple[Point3, Point3, Point3]
    tone: Tone = "given"


class Geometry3D(_Model):
    kind: Literal["geometry3d"] = "geometry3d"
    version: Literal[1] = 1
    title: Label
    description: Label
    points: list[Point] = Field(max_length=16)
    lines: list[Line] = Field(max_length=32)
    faces: list[Face] = Field(max_length=8)

    @model_validator(mode="after")
    def bounded(self) -> "Geometry3D":
        if not (self.points or self.lines or self.faces):
            raise ValueError("Diagram must contain geometry")
        if len(self.model_dump_json().encode("utf-8")) > 8192:
            raise ValueError("Diagram exceeds the visual budget")
        return self


def validate_geometry(value: object) -> dict[str, Any]:
    return Geometry3D.model_validate_json(json.dumps(value, allow_nan=False)).model_dump(
        mode="json"
    )


_VERSIONS = {
    TripleProduct.version,
    TriangleAngle.version,
    TriangleAngleDegrees.version,
    VectorExpression.version,
    ScalarVectorExpression.version,
    VectorLengthPractice.version,
    PerpendicularParameter.version,
    AreaPractice.version,
    SolidPractice.version,
    TriangleArea.version,
    TetrahedronVolume.version,
    TetrahedronHeight.version,
}


def _params(
    record: dict[str, object],
) -> (
    PointsParams
    | VectorExpressionParameters
    | VectorLengthParameters
    | PerpendicularParameters
    | None
):
    version = record.get("generator_version")
    if version not in _VERSIONS:
        return None
    if set(record) != {"generator_version", "code"} or not isinstance(record["code"], str):
        raise ValueError("Invalid geometry record")
    registry = engine._registry()
    code = parse_code(record["code"], registry)
    generator = registry.get_code(code.prefix, code.version)
    if generator.version != version:
        raise ValueError("Geometry record version differs from its code")
    params = generator.draw(code.seed)
    if not isinstance(
        params,
        PointsParams
        | VectorExpressionParameters
        | VectorLengthParameters
        | PerpendicularParameters,
    ):
        raise ValueError("Invalid geometry parameters")
    return params


def _point(at: Any) -> tuple[float, float, float]:
    return (float(at[0]), float(at[1]), float(at[2]))


def _parameter_practice(params: PerpendicularParameters, final: bool) -> dict[str, Any]:
    if params.level == 1:
        u = sp.Matrix((params.a, 0, 0))
        v = sp.Matrix((sp.Rational(params.b, 2), params.b * sp.sqrt(3) / 2, 0))
    else:
        u, v = (sp.Matrix(vector) for vector in (params.u, params.v))
    origin = (0.0, 0.0, 0.0)
    lines = [
        Line(
            label=name,
            start=origin,
            end=_point(vector),
            arrow=True,
            tone="previous" if final else "given",
        )
        for name, vector in (("u", u), ("v", v))
    ]
    description = (
        "Schematic vectors. The angle is not given."
        if params.level == 1
        else "The given vectors start at a common origin."
    )
    if final:
        factor = 2 if params.level == 3 else 1
        alpha = sp.sqrt(u.dot(u) / (factor * v.dot(v)))
        for label, vector in (
            ("u+alpha v", u + alpha * v),
            ("u-alpha v" if factor == 1 else "u-2alpha v", u - factor * alpha * v),
        ):
            largest = max(abs(float(component)) for component in vector)
            scale = min(1.0, 4 / largest) if largest else 1.0
            lines.append(
                Line(
                    label=label + (" scaled" if scale < 1 else ""),
                    start=origin,
                    end=_point(vector * scale),
                    tone="active",
                    arrow=True,
                )
            )
        description = (
            "One positive solution is shown. The other value also works. "
            "Scaled arrows are labelled."
        )
    return Geometry3D(
        title="Perpendicular vectors", description=description, points=[], lines=lines, faces=[]
    ).model_dump(mode="json")


def _length_practice(params: VectorLengthParameters, stage: int) -> dict[str, Any]:
    angle = sp.pi * params.angle / 180
    u = sp.Matrix((params.a, 0, 0))
    v = sp.Matrix((params.b * sp.cos(angle), params.b * sp.sin(angle), 0))
    origin = (0.0, 0.0, 0.0)
    lines = [
        Line(
            label=name,
            start=origin,
            end=_point(vector),
            arrow=True,
            tone="active" if stage == 1 and params.level < 3 else "given",
        )
        for name, vector in (("u", u), ("v", v))
    ]
    if params.level == 3:
        lines.append(Line(label="u+v", start=origin, end=_point(u + v), arrow=True))
    if stage >= 2:
        lines.append(Line(label="u-v", start=origin, end=_point(u - v), tone="active", arrow=True))
    description = (
        "Illustration of the given lengths. The angle is not given."
        if params.level == 3
        else f"The given angle between the vectors is {params.angle} degrees."
    )
    return Geometry3D(
        title="Vector lengths", description=description, points=[], lines=lines, faces=[]
    ).model_dump(mode="json")


def _scalar_expression(params: VectorExpressionParameters, stage: int) -> dict[str, Any]:
    origin = (0.0, 0.0, 0.0)
    u, v, w = (sp.Matrix(vector) for vector in (params.u, params.v, params.w))
    length_difference = params.level == 2 and params.seed % 2 == 1
    given = (
        (("u", u), ("w", w))
        if params.level == 1 and params.seed % 2
        else (("v", v),)
        if params.level == 1
        else (("v", v), ("w", w))
        if length_difference
        else (("u", u), ("v", v), ("w", w))
    )

    def active(name: str) -> bool:
        if not stage:
            return False
        if params.level == 1:
            return True
        if length_difference:
            return name == "w" or stage > 1
        return stage == 2 and name == ("u" if params.level == 2 else "w")

    lines = [
        Line(
            label=name,
            start=origin,
            end=_point(value),
            arrow=True,
            tone="active" if active(name) else "given",
        )
        for name, value in given
    ]
    description = "The given vectors start at a common origin."
    if stage and params.level > 1 and not length_difference:
        vector = w - v if params.level == 2 else u.cross(v)
        name = "w-v" if params.level == 2 else "u cross v"
        largest = max(abs(float(component)) for component in vector)
        scale = min(1.0, 4.0 / largest) if largest else 1.0
        lines.append(
            Line(
                label=name + (" scaled" if scale < 1 else ""),
                start=origin,
                end=_point(vector * scale),
                arrow=True,
                tone="active" if stage == 1 else "previous",
            )
        )
        description = "The constructed arrow is labelled if scaled."
        if vector == sp.zeros(3, 1):
            description += " The constructed vector is zero."
    return Geometry3D(
        title="Vectors", description=description, points=[], lines=lines, faces=[]
    ).model_dump(mode="json")


def _vector_expression(params: VectorExpressionParameters, stage: int) -> dict[str, Any]:
    origin = (0.0, 0.0, 0.0)
    u, v, w = (sp.Matrix(vector) for vector in (params.u, params.v, params.w))
    given = (("u", u), ("v", v)) + ((("w", w),) if params.level > 1 else ())
    scaled_form = params.level == 2 and params.seed % 2 == 1
    lines = [
        Line(
            label=name,
            start=origin,
            end=_point(value),
            arrow=True,
            tone="active" if scaled_form and stage == 1 and name == "u" else "given",
        )
        for name, value in given
    ]
    constructions: tuple[tuple[str, Any], ...]
    if params.level == 1:
        constructions = (("u-v", u - v),)
    elif scaled_form:
        constructions = (
            ("length u times v", u.norm() * v),
            ("length u times v - w", u.norm() * v - w),
        )
    elif params.level == 2:
        constructions = (("u cross w", u.cross(w)), ("u cross w - v", u.cross(w) - v))
    else:
        constructions = (("2u-v", 2 * u - v), ("(2u-v) cross w", (2 * u - v).cross(w)))
    construction_stage = max(0, stage - 1) if scaled_form else stage
    for index, (name, value) in enumerate(constructions[:construction_stage]):
        largest = max(abs(float(component)) for component in value)
        scale = min(1.0, 4.0 / largest) if largest else 1.0
        lines.append(
            Line(
                label=name + (" scaled" if scale < 1 else ""),
                start=origin,
                end=_point(value * scale),
                tone="active" if index == construction_stage - 1 else "previous",
                arrow=True,
            )
        )
    description = (
        "Given vectors and the construction at this step. Scaled arrows are labelled."
        if stage
        else "The given vectors start at a common origin."
    )
    if construction_stage and constructions[construction_stage - 1][1] == sp.zeros(3, 1):
        description += " The constructed vector is zero."
    return Geometry3D(
        title="Vectors", description=description, points=[], lines=lines, faces=[]
    ).model_dump(mode="json")


def _plane_patch(a: Any, b: Any, c: Any, foot: Any) -> list[Face]:
    """The convex planar patch includes an altitude foot outside the base triangle."""
    ab, ac = b - a, c - a
    gram = sp.Matrix([[ab.dot(ab), ab.dot(ac)], [ab.dot(ac), ac.dot(ac)]])
    x, y = gram.inv() * sp.Matrix([ab.dot(foot - a), ac.dot(foot - a)])
    planar = {
        sp.Point(0, 0): _point(a),
        sp.Point(1, 0): _point(b),
        sp.Point(0, 1): _point(c),
        sp.Point(x, y): _point(foot),
    }
    hull = sp.convex_hull(*planar).vertices
    return [
        Face(
            label="Plane ABC",
            vertices=(planar[hull[0]], planar[hull[index]], planar[hull[index + 1]]),
            tone="previous",
        )
        for index in range(1, len(hull) - 1)
    ]


def _solid_practice(params: SolidParameters, stage: str) -> dict[str, Any]:
    a, b, c, d = (sp.Matrix(point) for point in params.points)
    target = (c + d) / 2 if params.level == 3 else d
    third = "N" if params.level == 3 else "D"
    vertices = {name: _point(point) for name, point in zip("ABCD", (a, b, c, d), strict=True)}
    points = [Point(label=name, at=point) for name, point in vertices.items()]
    surface = params.mode == "parallelepiped-area"
    edge_names = ("AB", "AC", "AD") if surface else ("AB", "AC", "AD", "BC", "BD", "CD")
    lines = [
        Line(label=name, start=vertices[name[0]], end=vertices[name[1]]) for name in edge_names
    ]
    if surface and params.level == 3:
        lines.append(Line(label="CD", start=vertices["C"], end=vertices["D"]))
    if params.level == 3 and stage != "given":
        points.append(
            Point(
                label="N", at=_point(target), tone="active" if stage == "midpoint" else "previous"
            )
        )
        if stage != "midpoint":
            lines.append(
                Line(
                    label="AN",
                    start=_point(a),
                    end=_point(target),
                    tone="active" if stage == "edges" else "previous",
                    arrow=True,
                )
            )
            if not surface:
                lines.extend(
                    Line(
                        label=name + "N", start=vertices[name], end=_point(target), tone="previous"
                    )
                    for name in ("B", "C")
                )
    u, v, w = b - a, c - a, target - a
    if stage == "edges":
        for index, name in enumerate(edge_names):
            if name in {"AB", "AC", "AD"} and not (params.level == 3 and name == "AD"):
                lines[index] = Line(
                    label=name,
                    start=vertices[name[0]],
                    end=vertices[name[1]],
                    tone="active",
                    arrow=True,
                )
    faces: list[Face] = []
    if stage in {"cross", "triple"}:
        normal = u.cross(v)
        largest = max(abs(float(value)) for value in normal)
        scale = min(1.0, 4 / largest) if largest else 1.0
        lines.append(
            Line(
                label="base normal" + (" scaled" if scale < 1 else ""),
                start=_point(a),
                end=_point(a + normal * scale),
                tone="active",
                arrow=True,
            )
        )
    if stage == "base":
        faces.append(Face(label="ABC", vertices=(_point(a), _point(b), _point(c)), tone="active"))
    if stage == "volume":
        points_for_faces = (a, b, c, target)
        faces.extend(
            Face(
                label="Tetrahedron",
                vertices=(
                    _point(points_for_faces[i]),
                    _point(points_for_faces[j]),
                    _point(points_for_faces[k]),
                ),
                tone="active",
            )
            for i, j, k in ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3))
        )
    if stage == "height":
        normal = u.cross(v)
        foot = target - normal * (normal.dot(target - a) / normal.dot(normal))
        points.append(Point(label="H", at=_point(foot), tone="active"))
        lines.append(
            Line(
                label=third + "H",
                start=_point(target),
                end=_point(foot),
                tone="active",
                dashed=True,
            )
        )
        faces.extend(_plane_patch(a, b, c, foot))
    if stage in {"face_uv", "face_uw", "face_vw", "surface"}:
        pairs = {"face_uv": (u, v), "face_uw": (u, w), "face_vw": (v, w)}
        chosen = tuple(pairs.values()) if stage == "surface" else (pairs[stage],)
        for first, second in chosen:
            corners = (a, a + first, a + first + second, a + second)
            faces.extend(
                Face(
                    label="Face",
                    vertices=(_point(corners[i]), _point(corners[j]), _point(corners[k])),
                    tone="active",
                )
                for i, j, k in ((0, 1, 2), (0, 2, 3))
            )
        if stage == "surface":
            wire_corners = [
                a + i * u + j * v + k * w for i in (0, 1) for j in (0, 1) for k in (0, 1)
            ]
            lines.extend(
                Line(
                    label="edge",
                    start=_point(wire_corners[i]),
                    end=_point(wire_corners[j]),
                    tone="previous",
                )
                for i in range(8)
                for j in range(i + 1, 8)
                if (i ^ j) in (1, 2, 4)
            )
    description = (
        f"Perpendicular {third}H to the extended plane ABC."
        if stage == "height"
        else "Three adjacent faces are shown. Opposite faces have equal areas."
        if stage == "surface"
        else "Given vertices and the constructions in this step. Scaled arrows are labelled."
    )
    return Geometry3D(
        title="Parallelepiped" if surface else "Tetrahedron",
        description=description,
        points=points,
        lines=lines,
        faces=faces,
    ).model_dump(mode="json")


def _tetrahedron(params: PointsParams, stage: str) -> dict[str, Any]:
    a, b, c, d = (sp.Matrix(point) for point in params.points)
    vertices = {name: _point(point) for name, point in zip("ABCD", (a, b, c, d), strict=True)}
    points = [Point(label=name, at=point) for name, point in vertices.items()]
    lines = [
        Line(
            label=names,
            start=vertices[names[0]],
            end=vertices[names[1]],
            tone="active" if stage == "edges" and names in {"AB", "AC", "AD"} else "given",
            arrow=stage == "edges" and names in {"AB", "AC", "AD"},
        )
        for names in ("AB", "AC", "AD", "BC", "BD", "CD")
    ]
    faces: list[Face] = []
    if stage == "volume":
        faces.extend(
            Face(
                label=names,
                vertices=(vertices[names[0]], vertices[names[1]], vertices[names[2]]),
                tone="active",
            )
            for names in ("ABC", "ABD", "ACD", "BCD")
        )
    if stage == "base":
        faces.append(
            Face(label="ABC", vertices=(vertices["A"], vertices["B"], vertices["C"]), tone="active")
        )
    if stage == "height":
        normal = (b - a).cross(c - a)
        foot = d - normal * (normal.dot(d - a) / normal.dot(normal))
        h = _point(foot)
        points.append(Point(label="H", at=h, tone="active"))
        lines.append(Line(label="DH", start=vertices["D"], end=h, tone="active", dashed=True))
        faces.extend(_plane_patch(a, b, c, foot))
    description = (
        "Tetrahedron ABCD and perpendicular DH to the extended plane ABC."
        if stage == "height"
        else "Tetrahedron ABCD with the given vertices."
    )
    return Geometry3D(
        title="Tetrahedron ABCD", description=description, points=points, lines=lines, faces=faces
    ).model_dump(mode="json")


def _triangle(params: PointsParams, stage: str) -> dict[str, Any]:
    vertices = {name: _point(point) for name, point in zip("ABC", params.points, strict=True)}
    points = [Point(label=name, at=point) for name, point in vertices.items()]
    if stage in {"angle-edges", "cosine"}:
        names = ("BA", "BC", "AC")
        active = {"BA", "BC"}
    else:
        names = ("AB", "AC", "BC")
        active = {"AB", "AC"} if stage == "cross" else set()
    lines = [
        Line(
            label=name,
            start=vertices[name[0]],
            end=vertices[name[1]],
            tone="active" if name in active else "given",
            arrow=name in active,
        )
        for name in names
    ]
    faces = (
        [Face(label="ABC", vertices=(vertices["A"], vertices["B"], vertices["C"]), tone="active")]
        if stage == "area"
        else []
    )
    return Geometry3D(
        title="Triangle ABC",
        description="The given triangle ABC and the vectors used in this step.",
        points=points,
        lines=lines,
        faces=faces,
    ).model_dump(mode="json")


def _angle(params: AngleParameters, stage: str) -> dict[str, Any]:
    a, b, c = (sp.Matrix(point) for point in params.points)
    if params.level == 1:
        origin = (0.0, 0.0, 0.0)
        lines = [
            Line(
                label=name,
                start=origin,
                end=_point(vector),
                arrow=True,
                tone="given" if stage == "given" else "active",
            )
            for name, vector in (("u", a - b), ("v", c - b))
        ]
        return Geometry3D(
            title="Vectors u and v",
            description="The given vectors start at a common origin.",
            points=[],
            lines=lines,
            faces=[],
        ).model_dump(mode="json")
    if params.level == 2:
        return _triangle(params, "given" if stage == "given" else "angle-edges")
    vertices = {name: _point(point) for name, point in zip("ABC", (a, b, c), strict=True)}
    points = [Point(label=name, at=point) for name, point in vertices.items()]
    lines = [
        Line(label=name, start=vertices[name[0]], end=vertices[name[1]])
        for name in ("AB", "AC", "BC")
    ]
    if stage != "given":
        midpoint = _point((b + c) / 2)
        points.append(
            Point(label="M", at=midpoint, tone="active" if stage == "midpoint" else "previous")
        )
        if stage != "midpoint":
            lines[0] = Line(
                label="AB", start=vertices["A"], end=vertices["B"], tone="active", arrow=True
            )
            lines.append(
                Line(label="AM", start=vertices["A"], end=midpoint, tone="active", arrow=True)
            )
    return Geometry3D(
        title="Triangle ABC",
        description="Triangle ABC and the constructions in this step.",
        points=points,
        lines=lines,
        faces=[],
    ).model_dump(mode="json")


def _area_practice(params: AreaParameters, stage: str) -> dict[str, Any]:
    a, b, c = (sp.Matrix(point) for point in params.points)
    if params.level == 1:
        anchor = sp.zeros(3, 1)
        u, v = a - b, c - b
        points: list[Point] = []
        lines = [
            Line(label=name, start=_point(anchor), end=_point(vector), arrow=True)
            for name, vector in (("u", u), ("v", v))
        ]
    else:
        anchor = a
        u, v = b - a, (b + c) / 2 - a if params.level == 3 else c - a
        vertices = {name: _point(point) for name, point in zip("ABC", (a, b, c), strict=True)}
        points = [Point(label=name, at=point) for name, point in vertices.items()]
        lines = [
            Line(label=name, start=vertices[name[0]], end=vertices[name[1]])
            for name in ("AB", "AC", "BC")
        ]
        if params.level == 3 and stage != "given":
            points.append(
                Point(
                    label="M",
                    at=_point((b + c) / 2),
                    tone="active" if stage == "midpoint" else "previous",
                )
            )
        if stage not in {"given", "midpoint"}:
            lines[0] = Line(
                label="AB", start=_point(a), end=_point(a + u), arrow=True, tone="active"
            )
            second = "AM" if params.level == 3 else "AC"
            if params.level == 2:
                lines.pop(1)
            lines.append(
                Line(label=second, start=_point(a), end=_point(a + v), arrow=True, tone="active")
            )
    faces: list[Face] = []
    if stage in {"cross", "area"}:
        normal = u.cross(v)
        largest = max(abs(float(component)) for component in normal)
        scale = min(1.0, 4 / largest) if largest else 1.0
        lines.append(
            Line(
                label="cross product" + (" scaled" if scale < 1 else ""),
                start=_point(anchor),
                end=_point(anchor + normal * scale),
                arrow=True,
                tone="active" if stage == "cross" else "previous",
            )
        )
    if stage == "area":
        if params.mode == "triangle-area":
            faces.append(
                Face(
                    label="Triangle",
                    vertices=(_point(anchor), _point(anchor + u), _point(anchor + v)),
                    tone="active",
                )
            )
        else:
            corners = (anchor, anchor + u, anchor + u + v, anchor + v)
            lines.extend(
                Line(label="side", start=_point(first), end=_point(second), tone="previous")
                for first, second in ((corners[1], corners[2]), (corners[2], corners[3]))
            )
            faces.extend(
                Face(
                    label="Parallelogram",
                    vertices=(
                        _point(corners[indices[0]]),
                        _point(corners[indices[1]]),
                        _point(corners[indices[2]]),
                    ),
                    tone="active",
                )
                for indices in ((0, 1, 2), (0, 2, 3))
            )
    return Geometry3D(
        title="Triangle" if params.mode == "triangle-area" else "Parallelogram",
        description="Given edges and the constructions in this step. Scaled arrows are labelled.",
        points=points,
        lines=lines,
        faces=faces,
    ).model_dump(mode="json")


def _triple(params: PointsParams, stage: str) -> dict[str, Any]:
    u, v, w = (sp.Matrix(point) for point in params.points[1:])
    origin = (0.0, 0.0, 0.0)
    lines = [
        Line(label=name, start=origin, end=_point(vector), arrow=True)
        for name, vector in zip(("u", "v", "w"), (u, v, w), strict=True)
    ]
    description = "The given vectors u, v and w start at a common origin."
    normal = u.cross(v)
    if stage != "given" and normal != sp.zeros(3, 1):
        largest = max(abs(float(value)) for value in normal)
        scale = min(1.0, 5.0 / largest)
        lines.append(
            Line(
                label="u cross v scaled",
                start=origin,
                end=_point(normal * scale),
                tone="active",
                arrow=True,
            )
        )
        description = "The cross product arrow is scaled for visibility."
        if stage == "dot":
            projection = normal * (w.dot(normal) / normal.dot(normal))
            lines.append(
                Line(
                    label="w projection",
                    start=origin,
                    end=_point(projection),
                    tone="previous",
                    arrow=True,
                )
            )
    elif stage != "given":
        description = "The cross product is zero."
    return Geometry3D(
        title="Vectors u, v and w", description=description, points=[], lines=lines, faces=[]
    ).model_dump(mode="json")


def statement_visual(record: dict[str, object]) -> dict[str, Any] | None:
    params = _params(record)
    if params is None:
        return None
    version = record["generator_version"]
    if version == PerpendicularParameter.version:
        if not isinstance(params, PerpendicularParameters):
            raise ValueError("Invalid perpendicular-parameter data")
        return _parameter_practice(params, False)
    if version == VectorLengthPractice.version:
        if not isinstance(params, VectorLengthParameters):
            raise ValueError("Invalid vector-length parameters")
        return _length_practice(params, 0)
    if version == ScalarVectorExpression.version:
        if not isinstance(params, VectorExpressionParameters):
            raise ValueError("Invalid scalar-expression parameters")
        return _scalar_expression(params, 0)
    if version == SolidPractice.version:
        if not isinstance(params, SolidParameters):
            raise ValueError("Invalid solid parameters")
        return _solid_practice(params, "given")
    if version == AreaPractice.version:
        if not isinstance(params, AreaParameters):
            raise ValueError("Invalid area parameters")
        return _area_practice(params, "given")
    if version == VectorExpression.version:
        if not isinstance(params, VectorExpressionParameters):
            raise ValueError("Invalid vector-expression parameters")
        return _vector_expression(params, 0)
    if not isinstance(params, PointsParams):
        raise ValueError("Invalid point parameters")
    if version == TriangleAngleDegrees.version:
        if not isinstance(params, AngleParameters):
            raise ValueError("Invalid angle parameters")
        return _angle(params, "given")
    if version == TripleProduct.version:
        return _triple(params, "given")
    if version in {TriangleAngle.version, TriangleArea.version}:
        return _triangle(params, "given")
    return _tetrahedron(params, "given")


def step_visuals(record: dict[str, object]) -> tuple[dict[str, Any], ...]:
    params = _params(record)
    if params is None:
        return ()
    version = record["generator_version"]
    if version == PerpendicularParameter.version:
        if not isinstance(params, PerpendicularParameters):
            raise ValueError("Invalid perpendicular-parameter data")
        count = 4 if params.level > 1 else 3
        return tuple(_parameter_practice(params, index == count - 1) for index in range(count))
    if version == VectorLengthPractice.version:
        if not isinstance(params, VectorLengthParameters):
            raise ValueError("Invalid vector-length parameters")
        return tuple(_length_practice(params, stage) for stage in (1, 2, 3))
    if version == ScalarVectorExpression.version:
        if not isinstance(params, VectorExpressionParameters):
            raise ValueError("Invalid scalar-expression parameters")
        count = 1 if params.level == 1 else 3 if params.level == 2 and params.seed % 2 else 2
        return tuple(_scalar_expression(params, stage) for stage in range(1, count + 1))
    if version == SolidPractice.version:
        if not isinstance(params, SolidParameters):
            raise ValueError("Invalid solid parameters")
        stages = (("midpoint",) if params.level == 3 else ()) + (
            ("edges",) if params.level > 1 else ()
        )
        if params.mode == "parallelepiped-area":
            stages += ("face_uv", "face_uw", "face_vw", "surface")
        else:
            stages += (
                ("cross",)
                + (("base",) if params.mode == "tetrahedron-height" else ())
                + ("triple", "volume")
            )
            if params.mode == "tetrahedron-height":
                stages += ("height",)
        return tuple(_solid_practice(params, stage) for stage in stages)
    if version == AreaPractice.version:
        if not isinstance(params, AreaParameters):
            raise ValueError("Invalid area parameters")
        stages = (
            (("midpoint",) if params.level == 3 else ())
            + (("edges",) if params.level > 1 else ())
            + ("cross", "area")
        )
        return tuple(_area_practice(params, stage) for stage in stages)
    if version == VectorExpression.version:
        if not isinstance(params, VectorExpressionParameters):
            raise ValueError("Invalid vector-expression parameters")
        count = 1 if params.level == 1 else 3 if params.level == 2 and params.seed % 2 else 2
        return tuple(_vector_expression(params, stage) for stage in range(1, count + 1))
    if not isinstance(params, PointsParams):
        raise ValueError("Invalid point parameters")
    if version == TriangleAngleDegrees.version:
        if not isinstance(params, AngleParameters):
            raise ValueError("Invalid angle parameters")
        stages = (
            (("midpoint",) if params.level == 3 else ())
            + (("edges",) if params.level > 1 else ())
            + ("products", "cosine", "angle")
        )
        return tuple(_angle(params, stage) for stage in stages)
    if version == TripleProduct.version:
        return tuple(_triple(params, stage) for stage in ("cross", "dot"))
    if version == TriangleAngle.version:
        return tuple(_triangle(params, stage) for stage in ("angle-edges", "cosine"))
    if version == TriangleArea.version:
        return tuple(_triangle(params, stage) for stage in ("cross", "area"))
    stages = (
        ("volume", "base", "height")
        if version == TetrahedronHeight.version
        else ("edges", "volume")
    )
    return tuple(_tetrahedron(params, stage) for stage in stages)
