"""Compatible extensions of the existing analytic-geometry exercise engine.

Each mode owns a frozen version and code prefix. Shared givens and ordered
constructions drive both the mathematical task and its progressive diagrams.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Self

import sympy as sp
from pydantic import Field, model_validator

from app.engine.answers.computational import CategoryAnswer, FormulaAnswer, OrderedAnswer
from app.engine.answers.geometry import (
    PlaneEquationAnswer,
    VectorSetAnswer,
    vector_answer,
)
from app.engine.codes import encode
from app.engine.generators.eigen_geometry import Vector, _vec, vector_expression_seed
from app.engine.models import Answer, Drawn, Step, Task
from app.engine.prng import DeterministicRNG, draw_valid
from app.math_input.contracts import InputContract

# Append only: the index permanently determines this mode's published prefix.
MODES = (
    "point-collinearity",
    "parallel-vector",
    "unit-perpendiculars",
    "constrained-vector",
    "plane-equation",
    "plane-parameterisation",
    "line-equation",
    "containing-plane",
    "perpendicular-line",
    "parallel-parameter",
    "normal-parameters",
    "planes-common-point",
    "planes-common-line",
    "planes-three-lines",
    "line-angle",
    "plane-angle",
    "point-line-distance",
    "point-plane-distance",
    "parallel-line-distance",
    "skew-line-distance",
    "parallel-plane-distance",
    "line-line-intersection",
    "line-plane-intersection",
    "equidistant-plane",
    "point-line-projection",
    "point-plane-projection",
    "line-plane-projection",
    "directed-point-line-projection",
    "directed-point-plane-projection",
    "directed-line-plane-projection",
    "same-side",
    "line-reflection",
    "plane-reflection",
    "line-position",
    "line-plane-position",
)

VECTOR_MODES = MODES[:4]
LINE_MODES = MODES[4:14]
ANGLE_MODES = MODES[14:16]
DISTANCE_MODES = MODES[16:24]
PROJECTION_MODES = MODES[24:33]
POSITION_MODES = MODES[33:]
GEOMETRY_TOPICS = {
    "vector-operations": VECTOR_MODES,
    "lines-and-planes": LINE_MODES,
    "lengths-and-angles": ANGLE_MODES,
    "distances-and-intersections": (*DISTANCE_MODES, *POSITION_MODES),
    "projections-and-reflections": PROJECTION_MODES,
}

geometry_seed = vector_expression_seed


class GeometryParameters(Drawn):
    level: int = Field(ge=1, le=3)
    p: Vector
    u: Vector
    v: Vector
    w: Vector
    k: int = Field(ge=1, le=2)

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.seed // 10**12 != self.level - 1:
            raise ValueError("Geometry seed and level differ")
        if any(abs(c) > 4 for vector in (self.p, self.u, self.v, self.w) for c in vector):
            raise ValueError("Geometry coordinates exceed the practice range")
        u, v, w = (sp.Matrix(vector) for vector in (self.u, self.v, self.w))
        if (
            u.cross(v).dot(w) == 0
            or u.dot(w) == 0
            or u.cross(v).cross(w) == sp.zeros(3, 1)
            or u.cross(v).cross(u + w) == sp.zeros(3, 1)
        ):
            raise ValueError("Geometry basis is degenerate for the declared constructions")
        return self


@dataclass(frozen=True, slots=True)
class GeometryObject:
    kind: str
    label: str
    point: Any
    vectors: tuple[Any, ...] = ()


@dataclass(frozen=True, slots=True)
class ConstructionStep:
    key: str
    latex: str
    rule: str
    explanation: str
    objects: tuple[GeometryObject, ...] = ()
    hide: tuple[str, ...] = ()
    caption: str | None = None


@dataclass(frozen=True, slots=True)
class GeometryWork:
    statement: str
    answer: Answer
    steps: tuple[ConstructionStep, ...]
    givens: tuple[GeometryObject, ...]
    title: str


STEP_TEXT = {
    "midpoint": "Calculate the midpoint coordinate by coordinate.",
    "directions": "Determine the required direction vectors.",
    "combine": "Form the required linear combination of the vectors.",
    "cross": "Calculate the cross product in the stated order.",
    "normal": "Find a nonzero normal vector to the plane.",
    "length": "Calculate the required squared lengths and lengths.",
    "scale": "Use the scalar condition to find the scale factor.",
    "constraints": "Write the independent equations imposed by the given conditions.",
    "volume": "Use the absolute scalar triple product to express the volume.",
    "solve": "Solve the equations, retaining every admissible solution.",
    "plane": "Substitute a known point to complete the plane equation.",
    "line": "Use the point and direction to write parametric equations.",
    "basis": "Choose two independent directions parallel to the plane.",
    "substitute": "Substitute the parametric coordinates into the given equation.",
    "parameter": "Find the parameter value that satisfies the condition.",
    "intersection": "Substitute back to find the complete intersection point.",
    "dot": "Calculate the dot product and the required lengths.",
    "angle": "Use the dot-product formula for the required angle.",
    "distance": "Use the perpendicular component to calculate the distance.",
    "project": "Find the foot of the projection using its defining equations.",
    "reflect": "Use the midpoint relation between the point, its projection and its image.",
    "rank": "Compare the ranks of the coefficient and augmented matrices.",
    "condition": "State the full condition, including exceptional parameter values.",
    "result": "Write the complete result in the requested form.",
    "check": "Substitute the result into the original geometric conditions.",
}


def obj(kind: str, label: str, point: Any, *vectors: Any) -> GeometryObject:
    return GeometryObject(kind, label, sp.Matrix(point), tuple(sp.Matrix(v) for v in vectors))


def _st(
    key: str,
    latex: str,
    rule: str,
    explanation: str,
    *objects: GeometryObject,
    hide: tuple[str, ...] = (),
    caption: str | None = None,
) -> ConstructionStep:
    return ConstructionStep(key, latex, rule, explanation, objects, hide, caption)


def preparation_labels(
    steps: tuple[ConstructionStep, ...], objects: tuple[GeometryObject, ...], keep: tuple[str, ...]
) -> tuple[str, ...]:
    """Auxiliary objects can leave later scenes once their construction is complete."""
    labels = {item.label for item in objects}
    labels.update(item.label for step in steps for item in step.objects)
    return tuple(sorted(labels - set(keep)))


def _point_givens(
    p: GeometryParameters,
    target: Any,
    name: str = "P",
    *,
    endpoints: tuple[str, str] = ("A", "B"),
) -> tuple[str, tuple[ConstructionStep, ...], tuple[GeometryObject, ...]]:
    """Level three reconstructs the working point from an explicitly given midpoint."""
    target = sp.Matrix(target)
    if p.level < 3:
        return rf"{name}={_vec(target)}", (), (obj("point", name, target),)
    a, b = target - sp.Matrix(p.v), target + sp.Matrix(p.v)
    left, right = endpoints
    return (
        rf"{left}={_vec(a)},\ {right}={_vec(b)},\ {name}=({left}+{right})/2",
        (
            _st(
                "midpoint",
                rf"{name}=\frac{{{left}+{right}}}{{2}}={_vec(target)}",
                rf"M=({left}+{right})/2",
                "Average the corresponding coordinates of the two endpoints.",
                obj("point", name, target),
            ),
        ),
        (obj("point", left, a), obj("point", right, b), obj("segment", left + right, a, b - a)),
    )


def _direction_givens(
    p: GeometryParameters, u: Any, name: str = "d"
) -> tuple[str, tuple[ConstructionStep, ...], tuple[GeometryObject, ...]]:
    origin, u = sp.Matrix(p.p), sp.Matrix(u)
    if p.level == 1:
        return rf"{name}={_vec(u)}", (), (obj("vector", name, (0, 0, 0), u),)
    end = origin + u
    if p.level == 2:
        return (
            rf"C={_vec(origin)},\ D={_vec(end)},\ {name}=\overrightarrow{{CD}}",
            (
                _st(
                    "directions",
                    rf"{name}=D-C={_vec(u)}",
                    r"\overrightarrow{CD}=D-C",
                    "Subtract corresponding coordinates in end-minus-start order.",
                    obj("vector", name, origin, u),
                ),
            ),
            (obj("point", "C", origin), obj("point", "D", end)),
        )
    v = sp.Matrix(p.v)
    far = origin + (u + v) / 2
    return (
        rf"C={_vec(origin)},\ D={_vec(far)},\ E={_vec(origin + v)},\ "
        rf"{name}=2\overrightarrow{{CD}}-\overrightarrow{{CE}}",
        (
            _st(
                "directions",
                rf"\overrightarrow{{CD}}={_vec(far - origin)},\quad\overrightarrow{{CE}}={_vec(v)}",
                r"\overrightarrow{CD}=D-C",
                "First find both directed displacements from C.",
                obj("vector", "CD", origin, far - origin),
                obj("vector", "CE", origin, v),
            ),
            _st(
                "combine",
                rf"{name}=2\overrightarrow{{CD}}-\overrightarrow{{CE}}={_vec(u)}",
                r"2a-b=(2a_1-b_1,2a_2-b_2,2a_3-b_3)",
                "Scale each coordinate before subtracting the second vector.",
                obj("vector", name, origin, u),
            ),
        ),
        (obj("point", "C", origin), obj("point", "D", far), obj("point", "E", origin + v)),
    )


def _simple_pair(p: GeometryParameters) -> tuple[Any, Any]:
    if p.level != 1:
        return sp.Matrix(p.u), sp.Matrix(p.v)
    axis = p.seed % 3
    u, v = sp.zeros(3, 1), sp.zeros(3, 1)
    u[axis], v[(axis + 1) % 3] = 1 + abs(sum(p.u)) % 3, 1 + abs(sum(p.v)) % 3
    return u, v


def _vector_work(mode: str, p: GeometryParameters) -> GeometryWork:
    origin, u, v, w = (sp.Matrix(value) for value in (p.p, p.u, p.v, p.w))
    if mode == "point-collinearity":
        q, r = origin + u, origin + 2 * u + (v if p.seed % 2 else sp.zeros(3, 1))
        given, prep, objects = _point_givens(p, origin)
        r_given = rf"R={_vec(r)}"
        r_objects: tuple[GeometryObject, ...] = (obj("point", "R", r),)
        if p.level >= 2:
            c, d = r - v, r + v
            r_given = rf"C={_vec(c)},\ D={_vec(d)},\ R=(C+D)/2"
            r_objects = (obj("point", "C", c), obj("point", "D", d), obj("segment", "CD", c, d - c))
            prep = (
                *prep,
                _st(
                    "midpoint",
                    rf"R=\frac{{C+D}}{{2}}={_vec(r)}",
                    r"M=(C+D)/2",
                    "Recover the third point by averaging each pair of endpoint coordinates.",
                    obj("point", "R", r),
                ),
            )
        pq, pr = q - origin, r - origin
        cross = pq.cross(pr)
        steps = (
            *prep,
            _st(
                "directions",
                rf"\overrightarrow{{PQ}}={_vec(pq)},\quad\overrightarrow{{PR}}={_vec(pr)}",
                r"\overrightarrow{PQ}=Q-P",
                "Use vectors starting at the same point.",
                obj("vector", "PQ", origin, pq),
                obj("vector", "PR", origin, pr),
            ),
            _st(
                "cross",
                rf"\overrightarrow{{PQ}}\times\overrightarrow{{PR}}={_vec(cross)}",
                r"a\times b=0\iff a,b\text{ are parallel}",
                "The nonzero displacement PQ fixes a line. PR lies on that line exactly when "
                "the cross product vanishes.",
            ),
            _st(
                "result",
                r"\text{Collinear}" if cross == sp.zeros(3, 1) else r"\text{Not collinear}",
                r"P,Q,R\text{ collinear}\iff (Q-P)\times(R-P)=0",
                "This criterion includes points on either side of P; the scale factor need not "
                "be positive.",
            ),
        )
        return GeometryWork(
            rf"Determine whether P, Q and R are collinear: \({given},\ Q={_vec(q)},\ "
            rf"{r_given}\).",
            CategoryAnswer(
                "collinear" if cross == sp.zeros(3, 1) else "not_collinear",
                ("collinear", "not_collinear"),
            ),
            steps,
            (*objects, obj("point", "Q", q), *r_objects),
            "Collinearity of three points",
        )
    if mode == "parallel-vector":
        given, prep, objects = _direction_givens(p, w, "v")
        factor = sp.Rational(p.k, w.dot(w))
        result = factor * w
        steps = (
            *prep,
            _st(
                "constraints",
                r"u=\lambda v,\quad v\cdot u=\lambda(v\cdot v)",
                r"u\parallel v\iff u=\lambda v",
                "The given nonzero vector fixes the direction; a real scale factor also allows "
                "the opposite orientation.",
            ),
            _st(
                "length",
                rf"v\cdot v={w.dot(w)}",
                r"v\cdot v=v_1^2+v_2^2+v_3^2",
                "Sum the squares of all three coordinates.",
            ),
            _st(
                "scale",
                rf"\lambda\cdot {w.dot(w)}={p.k},\quad\lambda={sp.latex(factor)}",
                r"\lambda=c/(v\cdot v)",
                "The denominator is positive because the given vector is nonzero.",
            ),
            _st(
                "result",
                rf"u=\lambda v={_vec(result)}",
                r"u_i=\lambda v_i",
                "Multiply every coordinate by the same scale factor.",
                obj("vector", "u", (0, 0, 0), result),
            ),
            _st(
                "check",
                rf"v\cdot u={sp.latex(w.dot(result))}={p.k}",
                r"v\times u=0,\quad v\cdot u=c",
                "The result is parallel to v and satisfies the prescribed scalar product.",
            ),
        )
        return GeometryWork(
            rf"Find the vector u parallel to v such that \(v\cdot u={p.k}\), where \({given}\).",
            vector_answer(result),
            steps,
            objects,
            "A parallel vector with a scalar constraint",
        )
    if mode == "unit-perpendiculars":
        u, v = _simple_pair(p)
        if p.level == 3:
            a, b, c = origin, origin + u, origin + v
            given = (
                rf"A={_vec(a)},\ B={_vec(b)},\ C={_vec(c)},\ u=\overrightarrow{{AB}},\ "
                rf"v=\overrightarrow{{AC}}"
            )
            prep = (
                _st(
                    "directions",
                    rf"u=B-A={_vec(u)}",
                    r"\overrightarrow{AB}=B-A",
                    "Recover the first directed displacement from the common starting point.",
                    obj("vector", "u", a, u),
                ),
                _st(
                    "directions",
                    rf"v=C-A={_vec(v)}",
                    r"\overrightarrow{AC}=C-A",
                    "Recover the second displacement before taking the cross product.",
                    obj("vector", "v", a, v),
                ),
            )
            objects = (obj("point", "A", a), obj("point", "B", b), obj("point", "C", c))
        elif p.level == 2:
            given, prep, objects = _direction_givens(p, u, "u")
            given += rf",\ v={_vec(v)}"
            objects = (*objects, obj("vector", "v", (0, 0, 0), v))
        else:
            given = rf"u={_vec(u)},\ v={_vec(v)}"
            prep = ()
            objects = (obj("vector", "u", (0, 0, 0), u), obj("vector", "v", (0, 0, 0), v))
        normal = u.cross(v)
        length = sp.sqrt(normal.dot(normal))
        result = normal / length
        steps = (
            *prep,
            _st(
                "cross",
                rf"n=u\times v={_vec(normal)}",
                r"u\cdot(u\times v)=v\cdot(u\times v)=0",
                "The nonparallel input vectors span a plane, so their common perpendiculars "
                "form one line.",
                obj("vector", "n", (0, 0, 0), normal),
            ),
            _st(
                "length",
                rf"|n|=\sqrt{{{normal.dot(normal)}}}={sp.latex(length)}",
                r"|n|=\sqrt{n_1^2+n_2^2+n_3^2}",
                "The cross product is nonzero, so normalisation is defined.",
            ),
            _st(
                "result",
                rf"e=\pm\frac{{n}}{{|n|}}\in\left\{{{_vec(result)},{_vec(-result)}\right\}}",
                r"|\lambda n|=1\iff\lambda=\pm1/|n|",
                "Both signs are necessary: these are all unit vectors on the common "
                "perpendicular line.",
                obj("vector", "e", (0, 0, 0), result),
                obj("vector", "minus e", (0, 0, 0), -result),
            ),
            _st(
                "check",
                r"u\cdot e=v\cdot e=0,\quad e\cdot e=1",
                r"u\cdot e=0,\ v\cdot e=0,\ |e|=1",
                "Check perpendicularity to both vectors and unit length for each sign.",
            ),
        )
        return GeometryWork(
            rf"Find all unit vectors perpendicular to both u and v: \({given}\). Enter both "
            rf"vectors in either order.",
            VectorSetAnswer((tuple(result), tuple(-result))),
            steps,
            objects,
            "All unit common perpendiculars",
        )
    if mode == "constrained-vector":
        normal = u.cross(v)
        particular = v - u * (u.dot(v) / u.dot(u))
        offset = sp.simplify(v.dot(particular))
        volume = sp.Rational(p.k, 6) * normal.dot(normal)
        first, second = particular + p.k * normal, particular - p.k * normal
        given, prep, objects = _direction_givens(p, u, "a")
        steps = (
            *prep,
            _st(
                "constraints",
                rf"a\cdot x=0,\quad b\cdot x={sp.latex(offset)}",
                r"\text{endpoint in a plane}\iff b\cdot x=c",
                "The unknown vector starts at the origin, so its endpoint coordinates are the "
                "vector coordinates.",
            ),
            _st(
                "solve",
                rf"x_0=b-\frac{{a\cdot b}}{{|a|^2}}a={_vec(particular)},\quad "
                rf"a\cdot x_0=0,\quad b\cdot x_0={sp.latex(offset)}",
                r"a\cdot\left(b-\frac{a\cdot b}{|a|^2}a\right)=0",
                "Remove the component of b along a to obtain a perpendicular vector. "
                "Direct substitution also verifies the given plane condition.",
                obj("point", "x zero", particular),
            ),
            _st(
                "cross",
                rf"n=a\times b={_vec(normal)}",
                r"a\times b=(a_2b_3-a_3b_2,a_3b_1-a_1b_3,a_1b_2-a_2b_1)",
                "A common perpendicular to the two independent normals gives the direction "
                "of the line on which all possible endpoints lie.",
                obj("vector", "n", particular, normal),
            ),
            _st(
                "solve",
                rf"x={_vec(particular)}+t{_vec(normal)}",
                r"x=x_0+t(a\times b)",
                "The two independent linear equations define a line. Substitution verifies the "
                "displayed particular point and direction.",
                obj("line", "possible endpoints", particular, normal),
            ),
            _st(
                "volume",
                rf"V=\frac{{|x\cdot(a\times b)|}}{{6}}="
                rf"\frac{{{normal.dot(normal)}|t|}}{{6}}={sp.latex(volume)}",
                r"V=|x\cdot(a\times b)|/6",
                "The absolute value preserves both possible orientations of the tetrahedron.",
            ),
            _st(
                "parameter",
                rf"|t|={p.k},\quad t\in\{{-{p.k},{p.k}\}}",
                r"|t|=k>0\iff t=\pm k",
                "Retain both signs rather than choosing only the positive volume branch.",
            ),
            _st(
                "result",
                rf"x\in\{{{_vec(first)},{_vec(second)}\}}",
                r"x=x_0\pm k(a\times b)",
                "Substitute both parameter values to obtain all admissible endpoint vectors.",
                obj("vector", "x one", (0, 0, 0), first),
                obj("vector", "x two", (0, 0, 0), second),
            ),
            _st(
                "check",
                rf"a\cdot x_1=a\cdot x_2=0,\quad b\cdot x_1=b\cdot x_2={sp.latex(offset)}",
                r"|x_i\cdot(a\times b)|=6V",
                "Both solutions satisfy the plane, perpendicularity and absolute-volume "
                "conditions.",
            ),
        )
        return GeometryWork(
            rf"Find all vectors x starting at the origin whose endpoint lies in \(b\cdot "
            rf"x={sp.latex(offset)}\), with \(a\cdot x=0\). The tetrahedron spanned by x, a "
            rf"and b has volume \(V={sp.latex(volume)}\). Given \({given},\ b={_vec(v)}\). "
            rf"Enter both vectors in either order.",
            VectorSetAnswer((tuple(first), tuple(second))),
            steps,
            (
                *objects,
                obj("vector", "b", (0, 0, 0), v),
                obj("plane", "endpoint plane", v * offset / v.dot(v), normal, v.cross(normal)),
            ),
            "A vector satisfying three geometric conditions",
        )
    raise ValueError("Unknown vector geometry mode")


def mode_contract(mode: str) -> InputContract:
    scalar = InputContract("formula")
    vector = InputContract(
        "tuple", components=(scalar,) * 3, labels=("x coordinate", "y coordinate", "z coordinate")
    )
    if mode == "point-collinearity":
        return InputContract("category", choices=("collinear", "not_collinear"))
    if mode == "same-side":
        return InputContract("category", choices=("same_side", "opposite_sides", "on_plane"))
    if mode == "line-position":
        return InputContract("category", choices=("intersecting", "parallel", "skew", "coincident"))
    if mode == "line-plane-position":
        return InputContract("category", choices=("crossing", "parallel", "contained"))
    if mode in {"unit-perpendiculars", "constrained-vector"}:
        return InputContract(
            "tuple", components=(vector, vector), labels=("Vector one", "Vector two")
        )
    if mode in {"plane-equation", "containing-plane", "equidistant-plane"}:
        return InputContract("formula", symbols=tuple((name, "real") for name in "xyz"))
    if mode in {
        "plane-parameterisation",
        "line-equation",
        "perpendicular-line",
        "line-plane-projection",
        "directed-line-plane-projection",
    }:
        names = ("s", "t") if mode == "plane-parameterisation" else ("t",)
        expression = InputContract("formula", symbols=tuple((name, "real") for name in names))
        return InputContract("tuple", components=(expression,) * 3, labels=vector.labels)
    if mode in {"parallel-parameter", *ANGLE_MODES, *DISTANCE_MODES[:5]}:
        return scalar
    if mode == "normal-parameters":
        return InputContract(
            "tuple", components=(scalar, scalar), labels=("Parameter b", "Parameter c")
        )
    if mode in {"planes-common-point", "planes-common-line", "planes-three-lines"}:
        return InputContract(
            "tuple", components=(scalar, scalar), labels=("Exceptional a", "Compatible b")
        )
    return vector


class GeometryPractice:
    code_version: ClassVar[int] = 1
    params = GeometryParameters
    requires: ClassVar[tuple[str, ...]] = ()
    step_text = STEP_TEXT

    def __init__(self, mode: str):
        if mode not in MODES:
            raise ValueError("Unknown geometry mode")
        self.mode = mode
        self.version = f"geometry-practice-{mode}-v1"
        self.family = f"geometry-practice-{mode}"
        index = MODES.index(mode)
        self.prefix = "J" + chr(65 + index // 26) + chr(65 + index % 26)
        self.answer = (
            CategoryAnswer
            if mode_contract(mode).kind == "category"
            else VectorSetAnswer
            if mode in {"unit-perpendiculars", "constrained-vector"}
            else PlaneEquationAnswer
            if mode in {"plane-equation", "containing-plane", "equidistant-plane"}
            else FormulaAnswer
            if mode_contract(mode).kind == "formula"
            else OrderedAnswer
        )

    def draw(self, seed: int) -> GeometryParameters:
        level = seed // 10**12 + 1
        if level not in (1, 2, 3) or not 0 <= seed < 3 * 10**12:
            raise ValueError("Invalid geometry seed")
        rng = DeterministicRNG(seed)

        def vector() -> Vector:
            return tuple(rng.randbelow(5) - 2 for _ in range(3))  # type: ignore[return-value]

        def candidate() -> tuple[Vector, Vector, Vector]:
            return vector(), vector(), vector()

        def valid(values: tuple[Vector, Vector, Vector]) -> bool:
            u, v, w = (sp.Matrix(a) for a in values)
            return bool(
                u.cross(v).dot(w) != 0
                and u.dot(w) != 0
                and u.cross(v).cross(w) != sp.zeros(3, 1)
                and u.cross(v).cross(u + w) != sp.zeros(3, 1)
            )

        u, v, w = draw_valid(candidate, valid)
        return GeometryParameters(
            seed=seed, level=level, p=vector(), u=u, v=v, w=w, k=1 + rng.randbelow(2)
        )

    def input_contract(self, params: GeometryParameters) -> InputContract:
        return mode_contract(self.mode)

    def work(self, params: GeometryParameters) -> GeometryWork:
        if self.mode in VECTOR_MODES:
            return _vector_work(self.mode, params)
        if self.mode in LINE_MODES:
            from app.engine.generators.geometry_constructions import construction_work

            return construction_work(self.mode, params)
        from app.engine.generators.geometry_relations import relation_work

        return relation_work(self.mode, params)

    def build(self, params: GeometryParameters) -> Task:
        work = self.work(params)
        return Task(
            statement=work.statement,
            steps=tuple(Step(s.key, s.latex) for s in work.steps),
            answer=work.answer,
            metadata={"difficulty": params.level, "template": self.mode},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


def generators() -> tuple[GeometryPractice, ...]:
    return tuple(GeometryPractice(mode) for mode in MODES)
