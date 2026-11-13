"""Distances, relative positions, projections and reflections from shared data."""

from dataclasses import replace
from typing import Any

import sympy as sp

from app.engine.answers.computational import CategoryAnswer, FormulaAnswer
from app.engine.answers.geometry import ParametricGeometryAnswer, PlaneEquationAnswer, vector_answer
from app.engine.generators.eigen_geometry import _plane, _vec
from app.engine.generators.geometry_constructions import (
    cross_step,
    line_givens,
    linear_rule,
    plane_basis,
    plane_givens,
)
from app.engine.generators.geometry_practice import (
    ConstructionStep,
    GeometryParameters,
    GeometryWork,
    _point_givens,
    _st,
    obj,
    preparation_labels,
)


def _plane_context(p: GeometryParameters) -> tuple[Any, ...]:
    point, u, v = (sp.Matrix(a) for a in (p.p, p.u, p.v))
    n = u.cross(v)
    if p.level == 1:
        return _plane(n, -n.dot(point)), (), (obj("plane", "pi", point, u, v),), n, -n.dot(point)
    given, prep, objects, _, n, _ = plane_givens(p)
    qualifier = "through P parallel to u and v" if p.level == 2 else "through P, C and D"
    return (
        rf"\text{{{qualifier}: }}{given}",
        prep,
        (*objects, obj("plane", "pi", point, u, v)),
        n,
        -n.dot(point),
    )


def _point_line_steps(point: Any, direction: Any, source: Any) -> tuple[Any, tuple[Any, ...]]:
    parameter = sp.simplify(direction.dot(source - point) / direction.dot(direction))
    foot = point + parameter * direction
    return foot, (
        _st(
            "constraints",
            rf"H={_vec(point)}+t{_vec(direction)},\quad {_vec(direction)}\cdot(S-H)=0",
            r"H\in l,\quad SH\perp l",
            "The perpendicular foot must lie on the line. Here P is the displayed base "
            "point and d is its direction. The displacement to S is perpendicular to d.",
        ),
        _st(
            "parameter",
            rf"t=\frac{{d\cdot(S-P)}}{{d\cdot d}}="
            rf"\frac{{{sp.latex(direction.dot(source - point))}}}"
            rf"{{{sp.latex(direction.dot(direction))}}}={sp.latex(parameter)}",
            r"d\cdot(S-P)-t(d\cdot d)=0",
            "Expand the dot product and solve the resulting linear equation. Its denominator "
            "is positive.",
        ),
        _st(
            "project",
            rf"H={_vec(point)}+({sp.latex(parameter)}){_vec(direction)}={_vec(foot)}",
            r"H=P+\frac{d\cdot(S-P)}{|d|^2}d",
            "Substitute the parameter to locate the perpendicular foot.",
            obj("point", "H", foot),
            obj("segment", "SH", source, foot - source),
        ),
    )


def _point_plane_steps(normal: Any, offset: Any, source: Any) -> tuple[Any, tuple[Any, ...]]:
    signed = normal.dot(source) + offset
    factor = sp.simplify(signed / normal.dot(normal))
    foot = source - factor * normal
    return foot, (
        _st(
            "normal",
            rf"n={_vec(normal)},\quad n\cdot S+c={sp.latex(signed)},\quad "
            rf"|n|^2={normal.dot(normal)}",
            r"\pi:n\cdot X+c=0",
            "Read a normal vector from the equation and calculate the signed substitution value.",
            obj("normal", "n", source, normal),
        ),
        _st(
            "constraints",
            r"H=S-\lambda n,\quad n\cdot H+c=0",
            r"SH\parallel n,\quad H\in\pi",
            "A perpendicular to a plane follows its normal. Impose the plane equation on its foot.",
        ),
        _st(
            "parameter",
            rf"\lambda=\frac{{n\cdot S+c}}{{|n|^2}}={sp.latex(factor)}",
            r"n\cdot S-\lambda|n|^2+c=0",
            "Solve for the amount to move along the normal, preserving its sign.",
        ),
        _st(
            "project",
            rf"H=S-\lambda n={_vec(foot)}",
            r"H=S-\frac{n\cdot S+c}{|n|^2}n",
            "Substitute back. A negative parameter moves in the opposite normal direction.",
            obj("point", "H", foot),
            obj("segment", "SH", source, foot - source),
        ),
    )


def _distance_finish(source: Any, foot: Any) -> tuple[Any, tuple[Any, ...]]:
    squared = sp.simplify((source - foot).dot(source - foot))
    distance = sp.sqrt(squared)
    return distance, (
        _st(
            "distance",
            rf"d=|S-H|=\sqrt{{{sp.latex(squared)}}}={sp.latex(distance)}",
            r"|S-H|=\sqrt{(s_1-h_1)^2+(s_2-h_2)^2+(s_3-h_3)^2}",
            "Distance is a nonnegative length. A source already on the target has distance zero.",
        ),
        _st(
            "check",
            rf"d\ge0,\quad |S-H|^2={sp.latex(squared)}",
            r"d^2=(S-H)\cdot(S-H)",
            "The constructed segment is perpendicular to the target, so its length is the "
            "shortest distance.",
        ),
    )


def _angle_work(mode: str, p: GeometryParameters) -> GeometryWork:
    point = sp.Matrix(p.p)
    axis = p.seed % 3
    d = sp.zeros(3, 1)
    e = sp.zeros(3, 1)
    d[axis] = 1 + abs(sum(p.u)) % 3
    case = (p.seed % 10**12) % 3
    if case == 0:
        e[axis] = e[(axis + 1) % 3] = 1 + abs(sum(p.v)) % 3
    elif case == 1:
        e[(axis + 1) % 3] = 1 + abs(sum(p.v)) % 3
    else:
        e[axis] = 1 + abs(sum(p.v)) % 3
    cosine = sp.simplify(abs(d.dot(e)) / sp.sqrt(d.dot(d) * e.dot(e)))
    degrees = sp.simplify(180 * sp.acos(cosine) / sp.pi)
    other = point + sp.Matrix(p.w)
    if mode == "line-angle":
        first, a_steps, a_objects = line_givens(p, point, d, "l")
        second, b_steps, b_objects = line_givens(p, other, e, "m")
        given = rf"{first},\quad {second}"
        prep = tuple(step for step in (*a_steps, *b_steps) if step.key != "solve")
        objects = (*a_objects, *b_objects)
        what = "lines"
    else:
        a, b = plane_basis(d)
        c, f = plane_basis(e)
        objects = (obj("plane", "pi one", point, a, b), obj("plane", "pi two", other, c, f))
        if p.level == 1:
            given = rf"\pi_1:{_plane(d, -d.dot(point))},\quad\pi_2:{_plane(e, -e.dot(other))}"
            prep = (
                _st(
                    "normal",
                    rf"n_1={_vec(d)},\quad n_2={_vec(e)}",
                    r"n=(A,B,C)\text{ for }Ax+By+Cz+D=0",
                    "Read the three coordinate coefficients; the constant is not part of the "
                    "normal.",
                ),
            )
        elif p.level == 2:
            given = (
                rf"\pi_1:X={_vec(point)}+s{_vec(a)}+t{_vec(b)},\quad"
                rf"\pi_2:X={_vec(other)}+s{_vec(c)}+t{_vec(f)}"
            )
            prep = (cross_step(a, b, "n_1", point), cross_step(c, f, "n_2", other))
            objects = (
                *objects,
                obj("vector", "u1", point, a),
                obj("vector", "v1", point, b),
                obj("vector", "u2", other, c),
                obj("vector", "v2", other, f),
            )
        else:
            given = (
                rf"\pi_1\text{{ through }}A={_vec(point)},"
                rf"B={_vec(point + a)},C={_vec(point + b)};\quad"
                rf"\pi_2\text{{ through }}D={_vec(other)},"
                rf"E={_vec(other + c)},F={_vec(other + f)}"
            )
            objects = (
                *objects,
                *(
                    obj("point", label, at)
                    for label, at in (
                        ("A", point),
                        ("B", point + a),
                        ("C", point + b),
                        ("D", other),
                        ("E", other + c),
                        ("F", other + f),
                    )
                ),
            )
            prep = (
                _st(
                    "directions",
                    rf"AB={_vec(a)},\ AC={_vec(b)},\ DE={_vec(c)},\ DF={_vec(f)}",
                    r"AB=B-A,\quad AC=C-A",
                    "Form two independent in-plane directions for each plane.",
                ),
                cross_step(a, b, "n_1", point),
                cross_step(c, f, "n_2", other),
            )
        what = "planes"
    if mode == "plane-angle" and p.level > 1:
        raw_first, raw_second = a.cross(b), c.cross(f)
        first_scale = next(raw_first[i] / d[i] for i in range(3) if d[i] != 0)
        second_scale = next(raw_second[i] / e[i] for i in range(3) if e[i] != 0)
        prep = (
            *prep,
            _st(
                "scale",
                rf"a=\frac{{n_1}}{{{sp.latex(first_scale)}}}={_vec(d)},\quad "
                rf"b=\frac{{n_2}}{{{sp.latex(second_scale)}}}={_vec(e)}",
                r"\frac{|(\alpha a)\cdot(\beta b)|}{|\alpha a||\beta b|}="
                r"\frac{|a\cdot b|}{|a||b|},\quad\alpha\beta\ne0",
                "Rescale each normal by the displayed nonzero constant. This preserves "
                "the unoriented angle and simplifies the following arithmetic.",
            ),
        )
    steps = (
        *prep,
        _st(
            "dot",
            rf"a={_vec(d)},\quad b={_vec(e)},\quad "
            rf"|a\cdot b|={sp.latex(abs(d.dot(e)))},\quad |a|={sp.latex(d.norm())},\quad "
            rf"|b|={sp.latex(e.norm())}",
            r"a\cdot b=a_1b_1+a_2b_2+a_3b_3",
            "Use line directions or plane normals. Any nonzero rescaling leaves the acute "
            "angle unchanged.",
            hide=preparation_labels(prep, objects, ("l", "m", "pi one", "pi two", "n_1", "n_2")),
        ),
        _st(
            "angle",
            rf"\cos\theta=\frac{{|a\cdot b|}}{{|a||b|}}={sp.latex(cosine)},\quad"
            rf"\theta={sp.latex(degrees)}^\circ",
            r"\theta=\arccos\frac{|a\cdot b|}{|a||b|},\quad0\le\theta\le90^\circ",
            "The absolute value selects the smaller unoriented angle. Convert the "
            "inverse-cosine value from radians to degrees.",
        ),
        _st(
            "check",
            rf"0\le {sp.latex(degrees)}\le90,\quad\cos\theta={sp.latex(cosine)}",
            r"\cos0^\circ=1,\ \cos45^\circ=\sqrt2/2,\ \cos90^\circ=0",
            "Parallel and perpendicular cases are included; the answer is the angle itself, "
            "not just its cosine.",
        ),
    )
    return GeometryWork(
        rf"Find the smaller angle between the {what} in degrees: \({given}\).",
        FormulaAnswer(degrees),
        steps,
        objects,
        "The smaller angle between " + what,
    )


def relation_work(mode: str, p: GeometryParameters) -> GeometryWork:
    if mode in {"line-angle", "plane-angle"}:
        return _angle_work(mode, p)
    point, u, v, w = (sp.Matrix(a) for a in (p.p, p.u, p.v, p.w))
    normal = u.cross(v)
    source = point + (u if p.seed % 5 == 4 else w)
    if mode in {
        "point-line-distance",
        "point-line-projection",
        "line-reflection",
        "parallel-line-distance",
    }:
        given, prep, objects = line_givens(p, point, u)
        extra: tuple[ConstructionStep, ...] = ()
        source_text = rf"S={_vec(source)}"
        if p.level == 3:
            source_text, extra, source_objects = _point_givens(p, source, "S")
        else:
            source_objects = (obj("point", "S", source),)
        if mode == "parallel-line-distance":
            source_text = rf"m:X={_vec(source)}+s{_vec(u)}"
            source_objects = (obj("line", "m", source, u), obj("point", "S", source))
            extra = (
                _st(
                    "substitute",
                    rf"S={_vec(source)},\quad d_m={_vec(u)}",
                    r"m:X=S+s\,d_m",
                    "Read a point on the second line and its direction from its parameterisation.",
                ),
            )
        foot, construction = _point_line_steps(point, u, source)
        objects = (*objects, *source_objects)
        construction = (
            replace(
                construction[0], hide=preparation_labels((*prep, *extra), objects, ("l", "m", "S"))
            ),
            *construction[1:],
        )
        steps = (*prep, *extra, *construction)
        if mode in {"point-line-distance", "parallel-line-distance"}:
            value, finish = _distance_finish(source, foot)
            intro = (
                "Find the distance from S to line l"
                if mode == "point-line-distance"
                else "Find the distance between lines l and m (coincident lines have distance zero)"
            )
            return GeometryWork(
                rf"{intro}: \({given},\ {source_text}\).",
                FormulaAnswer(value),
                (*steps, *finish),
                objects,
                "Perpendicular distance to a line",
            )
        if mode == "point-line-projection":
            result = foot
            intro = "Find the orthogonal projection of S onto line l"
            end: tuple[ConstructionStep, ...] = ()
        else:
            result = 2 * foot - source
            intro = "Find the reflection of S in line l"
            end = (
                _st(
                    "reflect",
                    rf"R=2H-S={_vec(result)}",
                    r"H=(S+R)/2\iff R=2H-S",
                    "The line is the rotation axis of a half-turn. Its perpendicular foot is "
                    "the midpoint of the point and its image.",
                    obj("point", "R", result),
                    obj("segment", "HR", foot, result - foot),
                ),
            )
        check_step = _st(
            "check",
            rf"u\cdot(S-H)={sp.latex(u.dot(source - foot))},\quad H\in l",
            r"SH\perp l,\quad H\in l",
            "Check the foot on the line and its perpendicular displacement; for reflection "
            "also check the midpoint relation.",
        )
        return GeometryWork(
            rf"{intro}: \({given},\ {source_text}\).",
            vector_answer(result),
            (*steps, *end, check_step),
            objects,
            "Orthogonal line projection"
            if mode == "point-line-projection"
            else "Reflection in a line",
        )
    if mode in {
        "point-plane-distance",
        "point-plane-projection",
        "plane-reflection",
        "equidistant-plane",
        "parallel-plane-distance",
    }:
        given, prep, objects, normal, offset = _plane_context(p)
        if mode == "equidistant-plane":
            source = point + w
            other_offset = sp.simplify(-2 * normal.dot(source) - offset)
            signed = normal.dot(source) + offset
            steps = (
                *prep,
                _st(
                    "normal",
                    rf"n={_vec(normal)},\quad \pi':n\cdot X+d=0",
                    r"\pi'\parallel\pi\Longrightarrow n'=\lambda n,\ \lambda\ne0",
                    "Use the same normal after rescaling the equation.",
                    hide=preparation_labels(prep, objects, ("pi", "S")),
                ),
                _st(
                    "constraints",
                    rf"|n\cdot S+d|=|n\cdot S+({sp.latex(offset)})|",
                    r"d(S,\pi)=|n\cdot S+c|/|n|",
                    "The common positive denominator cancels in the equality of the two distances.",
                ),
                _st(
                    "solve",
                    rf"d={sp.latex(offset)}\quad\text{{or}}\quad d=-2n\cdot "
                    rf"S-c={sp.latex(other_offset)}",
                    r"|a|=|b|\iff a=b\ \text{or}\ a=-b",
                    "The first choice reproduces the original plane; retain the second because "
                    "a distinct plane was requested.",
                ),
                _st(
                    "plane",
                    _plane(normal, other_offset),
                    r"\pi':n\cdot X+d=0",
                    "Insert the remaining constant into the plane equation.",
                    obj(
                        "plane",
                        "new plane",
                        source - normal * (normal.dot(source) + other_offset) / normal.dot(normal),
                        *plane_basis(normal),
                    ),
                ),
                _st(
                    "check",
                    rf"n\cdot S+c={sp.latex(signed)},\quad n\cdot S+d={sp.latex(-signed)}",
                    r"|a|=|-a|",
                    "The signed substitution values are opposite and nonzero. The planes are "
                    "distinct and the distances are equal.",
                ),
            )
            return GeometryWork(
                rf"Find a plane distinct from and parallel to pi such that S is equally "
                rf"distant from both: \(\pi:{given},\ S={_vec(source)}\). Enter the affine "
                rf"left-hand side equal to zero.",
                PlaneEquationAnswer(tuple(normal), other_offset),
                steps,
                (*objects, obj("point", "S", source)),
                "A distinct equidistant parallel plane",
            )
        if mode == "parallel-plane-distance":
            second_offset = -normal.dot(source)
            multiplier = 1 if p.level == 1 else 2 + p.seed % 2
            if p.level < 3:
                given = (
                    rf"\pi_1:{_plane(normal, offset)},\quad\pi_2:"
                    rf"{_plane(multiplier * normal, multiplier * second_offset)}"
                )
                prep = (
                    ()
                    if p.level == 1
                    else (
                        _st(
                            "scale",
                            rf"\pi_2:{_plane(normal, second_offset)}",
                            r"F(X)=0\iff\lambda F(X)=0,\quad\lambda\ne0",
                            "Divide the entire second equation by its common nonzero factor "
                            "before comparing constants.",
                        ),
                    )
                )
                objects = (obj("plane", "pi one", point, *plane_basis(normal)),)
                prep = (
                    *prep,
                    _st(
                        "substitute",
                        rf"S={_vec(source)},\quad n\cdot S+c_2=0",
                        r"n_1s_1+n_2s_2+n_3s_3+c_2=0",
                        "Choose the displayed values for two coordinates and solve for a "
                        "coordinate with a nonzero coefficient. This gives one point S on "
                        "the second plane; the distance is independent of that choice.",
                        obj("point", "S", source),
                    ),
                )
            else:
                given = (
                    rf"\pi_1:{given},\quad\pi_2\text{{ parallel to }}"
                    rf"\pi_1\text{{ through }}S={_vec(source)}"
                )
                prep = (
                    *prep,
                    _st(
                        "plane",
                        rf"\pi_1:{_plane(normal, offset)},\quad"
                        rf"\pi_2:{_plane(normal, second_offset)}",
                        r"c_i=-n\cdot P_i",
                        "Use the same normal and a known point of each plane to calculate the "
                        "two constant terms.",
                    ),
                )
            distance = sp.simplify(abs(second_offset - offset) / normal.norm())
            foot = source - normal * (normal.dot(source) + offset) / normal.dot(normal)
            steps = (
                *prep,
                _st(
                    "normal",
                    rf"n={_vec(normal)},\quad |n|={sp.latex(normal.norm())}",
                    r"n=(A,B,C)",
                    "The normals agree after rescaling, so the planes are parallel or coincident.",
                    obj("normal", "n", source, normal),
                    hide=preparation_labels(prep, objects, ("pi", "pi one", "pi two", "S")),
                ),
                _st(
                    "project",
                    rf"H={_vec(foot)}",
                    r"H=S-\frac{n\cdot S+c_1}{|n|^2}n",
                    "Project a point of the second plane onto the first to construct a common "
                    "perpendicular.",
                    obj("point", "H", foot),
                    obj("segment", "SH", source, foot - source),
                ),
                _st(
                    "distance",
                    rf"d=\frac{{|c_2-c_1|}}{{|n|}}={sp.latex(distance)}",
                    r"d(\pi_1,\pi_2)=|c_2-c_1|/|n|",
                    "Subtract constants only after making the normal coefficients identical.",
                ),
                _st(
                    "check",
                    r"d\ge0,\quad n\cdot H+c_1=0",
                    r"d=|S-H|",
                    "The perpendicular segment verifies the distance, including the "
                    "coincident-plane case.",
                ),
            )
            return GeometryWork(
                rf"Find the distance between the planes: \({given}\).",
                FormulaAnswer(distance),
                steps,
                (*objects, obj("plane", "pi two", source, *plane_basis(normal))),
                "Distance between parallel planes",
            )
        foot, construction = _point_plane_steps(normal, offset, source)
        construction = (
            replace(construction[0], hide=preparation_labels(prep, objects, ("pi", "S"))),
            *construction[1:],
        )
        steps = (*prep, *construction)
        objects = (*objects, obj("point", "S", source))
        if mode == "point-plane-distance":
            value, finish = _distance_finish(source, foot)
            return GeometryWork(
                rf"Find the distance from S to the plane pi: \(S={_vec(source)},\ \pi:{given}\).",
                FormulaAnswer(value),
                (*steps, *finish),
                objects,
                "Perpendicular distance to a plane",
            )
        result = foot if mode == "point-plane-projection" else 2 * foot - source
        if mode == "plane-reflection":
            steps = (
                *steps,
                _st(
                    "reflect",
                    rf"R=2H-S={_vec(result)}",
                    r"H=(S+R)/2\iff R=2H-S",
                    "The perpendicular foot is the midpoint of the point and its reflected image.",
                    obj("point", "R", result),
                    obj("segment", "HR", foot, result - foot),
                ),
            )
        check_step = _st(
            "check",
            r"n\cdot H+c=0,\quad S-H\parallel n",
            r"H\in\pi,\quad SH\perp\pi",
            "The foot lies in the plane and its connecting segment is normal to it. The "
            "midpoint relation additionally verifies reflection.",
        )
        intro = (
            "Find the orthogonal projection of S onto plane pi"
            if mode == "point-plane-projection"
            else "Find the reflection of S in plane pi"
        )
        return GeometryWork(
            rf"{intro}: \(S={_vec(source)},\ \pi:{given}\).",
            vector_answer(result),
            (*steps, check_step),
            objects,
            "Orthogonal plane projection"
            if mode == "point-plane-projection"
            else "Reflection in a plane",
        )
    if mode == "skew-line-distance":
        given, prep, objects = line_givens(p, point, u, "l")
        second, b_steps, b_objects = line_givens(p, source, v, "m")
        delta = source - point
        gram = sp.Matrix(((u.dot(u), -u.dot(v)), (u.dot(v), -v.dot(v))))
        s, t = gram.inv() * sp.Matrix((delta.dot(u), delta.dot(v)))
        a, b = point + s * u, source + t * v
        distance = sp.simplify(abs(delta.dot(normal)) / normal.norm())
        steps = (
            *prep,
            *b_steps,
            cross_step(
                u,
                v,
                "n",
                point,
                hide=preparation_labels((*prep, *b_steps), (*objects, *b_objects), ("l", "m")),
            ),
            _st(
                "constraints",
                r"(Q+t v-P-s u)\cdot u=0,\quad(Q+t v-P-s u)\cdot v=0",
                r"AB\perp u,\quad AB\perp v",
                "A shortest connector between nonparallel lines must be perpendicular to both "
                "directions.",
            ),
            _st(
                "solve",
                rf"s={sp.latex(s)},\quad t={sp.latex(t)},\quad A={_vec(a)},\quad B={_vec(b)}",
                linear_rule(gram.row_join(sp.Matrix((delta.dot(u), delta.dot(v))))),
                "Solve the two linear perpendicularity equations, then substitute to find the "
                "endpoints.",
                obj("point", "foot l", a),
                obj("point", "foot m", b),
                obj("segment", "shortest connector", a, b - a),
            ),
            _st(
                "distance",
                rf"d=\frac{{|(Q-P)\cdot(u\times v)|}}{{|u\times v|}}={sp.latex(distance)}",
                r"d=|AB|=|(Q-P)\cdot n|/|n|",
                "The scalar triple product measures the perpendicular displacement between the "
                "two lines.",
            ),
            _st(
                "check",
                rf"(B-A)\cdot u={sp.latex((b - a).dot(u))},\quad(B-A)\cdot "
                rf"v={sp.latex((b - a).dot(v))}",
                r"A\in l,\quad B\in m",
                "Check both incidences and perpendicularities. When the lines intersect, the "
                "connector has zero length.",
            ),
        )
        return GeometryWork(
            rf"Find the distance between the two nonparallel lines: \({given},\quad {second}\).",
            FormulaAnswer(distance),
            steps,
            (*objects, *b_objects),
            "Distance between nonparallel lines",
        )
    if mode in {"line-line-intersection", "line-plane-intersection"}:
        if mode == "line-line-intersection":
            first, a_steps, a_objects = line_givens(p, point, u, "l")
            q = point + p.k * u - (1 + p.seed % 3) * v
            second, b_steps, b_objects = line_givens(p, q, v, "m")
            result = point + p.k * u
            equation = rf"{_vec(point)}+t{_vec(u)}={_vec(q)}+s{_vec(v)}"
            parameter = rf"t={p.k},\quad s={1 + p.seed % 3}"
            given = rf"{first},\quad {second}"
            prep = (*a_steps, *b_steps)
            objects = (*a_objects, *b_objects)
            explanation = (
                "Equate the three coordinates of the two parameterisations. Solve for both "
                "parameters and verify the third coordinate."
            )
            parameter_rule = linear_rule(sp.Matrix.hstack(u, -v, q - point))
        else:
            plane, b_steps, b_objects, normal, offset = _plane_context(p)
            q, direction = point + w, u + p.k * w
            first, a_steps, a_objects = line_givens(p, q, direction, "l")
            parameter_value = sp.simplify(-(normal.dot(q) + offset) / normal.dot(direction))
            result = q + parameter_value * direction
            equation = (
                sp.latex(sp.expand(normal.dot(q + sp.Symbol("t") * direction) + offset)) + "=0"
            )
            parameter = rf"t={sp.latex(parameter_value)}"
            given = rf"{first},\quad\pi:{plane}"
            prep = (*a_steps, *b_steps)
            objects = (*a_objects, *b_objects)
            explanation = (
                "Substitute all three coordinates of the line into the plane equation. The "
                "nonzero direction-normal dot product ensures one intersection."
            )
            parameter_rule = r"\alpha t+\beta=0\iff t=-\beta/\alpha,\quad\alpha\ne0"
        steps = (
            *prep,
            _st(
                "substitute",
                equation,
                r"X_l(t)=X_m(s)\quad\text{or}\quad n\cdot X_l(t)+c=0",
                explanation,
                hide=preparation_labels(prep, objects, ("l", "m", "pi")),
            ),
            _st(
                "parameter",
                parameter,
                parameter_rule,
                "Retain the parameter values satisfying every coordinate equation.",
            ),
            _st(
                "intersection",
                rf"H={_vec(result)}",
                r"H=P+t\,d",
                "Substitute into the line to obtain all three coordinates.",
                obj("point", "H", result),
            ),
            _st(
                "check",
                rf"H={_vec(result)}\text{{ satisfies both defining objects}}",
                r"H\in l\cap m\quad\text{or}\quad H\in l\cap\pi",
                "Substitute the point into both original definitions, including every coordinate.",
            ),
        )
        return GeometryWork(
            rf"Find the intersection point: \({given}\).",
            vector_answer(result),
            steps,
            objects,
            "The complete intersection point",
        )
    if mode in {"point-line-projection", "point-plane-projection"}:
        raise AssertionError("Projection should be handled with its orthogonal construction")
    if mode in {
        "directed-point-line-projection",
        "directed-point-plane-projection",
        "line-plane-projection",
        "directed-line-plane-projection",
    }:
        return _directed_work(mode, p)
    if mode == "same-side":
        given, prep, objects, normal, offset = _plane_context(p)
        source = point + w
        other = point + (2 * w if p.seed % 3 == 0 else -w if p.seed % 3 == 1 else u)
        left, right = normal.dot(source) + offset, normal.dot(other) + offset
        category = (
            "on_plane"
            if left * right == 0
            else "same_side"
            if left * right > 0
            else "opposite_sides"
        )
        steps = (
            *prep,
            _st(
                "substitute",
                rf"f(S)={sp.latex(left)},\quad f(T)={sp.latex(right)}",
                r"f(X)=n\cdot X+c",
                "Substitute both points into the same plane equation.",
            ),
            _st(
                "condition",
                rf"f(S)f(T)={sp.latex(left * right)},\quad\text{{{category.replace('_', ' ')}}}",
                r"f(S)f(T)>0:\text{ same side};\quad<0:\text{ opposite sides}",
                "A zero product means at least one point is on the plane, rather than in "
                "either open half-space.",
            ),
        )
        return GeometryWork(
            rf"Determine the positions of S and T relative to plane pi: \(S={_vec(source)},\ "
            rf"T={_vec(other)},\ \pi:{given}\).",
            CategoryAnswer(category, ("same_side", "opposite_sides", "on_plane")),
            steps,
            (*objects, obj("point", "S", source), obj("point", "T", other)),
            "Which side of a plane?",
        )
    if mode in {"line-position", "line-plane-position"}:
        return _position_work(mode, p)
    raise ValueError("Unknown geometric relation")


def _directed_work(mode: str, p: GeometryParameters) -> GeometryWork:
    point, u, v, w = (sp.Matrix(a) for a in (p.p, p.u, p.v, p.w))
    source = point + w
    if mode == "directed-point-line-projection":
        source = point + p.k * u + p.k * v
        given, prep, objects = line_givens(p, point, u)
        parameters = sp.Matrix.hstack(u, -v).gauss_jordan_solve(source - point)[0]
        s, t = parameters
        result = point + s * u
        steps = (
            *prep,
            _st(
                "constraints",
                rf"P+s u=S+t v,\quad {_vec(point)}+s{_vec(u)}={_vec(source)}+t{_vec(v)}",
                r"H\in l\cap\{S+t v:t\in\mathbb R\}",
                "Intersect the target line with the line through S in the specified projection "
                "direction.",
                obj("line", "projection ray", source, v),
                hide=preparation_labels(prep, objects, ("l", "S", "v")),
            ),
            _st(
                "solve",
                rf"s={sp.latex(s)},\quad t={sp.latex(t)}",
                linear_rule(sp.Matrix.hstack(u, -v, source - point)),
                "Solve the coordinate equations and verify all three; independence of the two "
                "directions gives uniqueness.",
            ),
            _st(
                "project",
                rf"H=P+s u={_vec(result)}",
                r"H=P+s u=S+t v",
                "Substitute either parameterisation to locate the same point.",
                obj("point", "H", result),
                obj("segment", "SH", source, result - source),
            ),
            _st(
                "check",
                r"H\in l,\quad H-S\parallel v",
                r"(H-S)\times v=0",
                "A directed projection follows the specified vector; its segment need not be "
                "perpendicular to the target.",
            ),
        )
        return GeometryWork(
            rf"Project S onto line l in direction v: \({given},\ S={_vec(source)},\ v={_vec(v)}\).",
            vector_answer(result),
            steps,
            (*objects, obj("point", "S", source), obj("vector", "v", source, v)),
            "Directed projection onto a line",
        )
    plane, prep, objects, normal, offset = _plane_context(p)
    directed = mode != "line-plane-projection"
    projection_direction = w + p.k * u if directed else normal
    denominator = normal.dot(projection_direction)
    if denominator == 0:
        raise ValueError("Projection direction is parallel to the plane")
    foot = sp.simplify(source - projection_direction * (normal.dot(source) + offset) / denominator)
    projection_parameter = -(normal.dot(source) + offset) / denominator
    setup = _st(
        "normal",
        rf"n={_vec(normal)},\quad c={sp.latex(offset)},\quad "
        rf"q={_vec(projection_direction)},\quad n\cdot q={sp.latex(denominator)}\ne0",
        r"q=n\text{ for an orthogonal projection};\quad n\cdot q\ne0",
        "Read the plane normal and constant. An orthogonal projection uses its normal "
        "as the projection direction. A directed projection uses the specified q.",
        obj("normal", "n", source, normal),
    )
    prep = (*prep, setup)
    rule = r"\operatorname{pr}(X)=X-\frac{n\cdot X+c}{n\cdot q}q"
    if mode == "directed-point-plane-projection":
        steps = (
            *prep,
            _st(
                "constraints",
                rf"H=S+t q,\quad n\cdot H+c=0,\quad n\cdot q={sp.latex(denominator)}\ne0",
                r"H\in\pi,\quad SH\parallel q",
                "Impose the plane equation on the line through S in the prescribed direction.",
                obj("line", "projection ray", source, projection_direction),
                hide=preparation_labels(prep, objects, ("pi", "n", "S", "q")),
            ),
            _st(
                "parameter",
                rf"t=-\frac{{n\cdot S+c}}{{n\cdot q}}={sp.latex(projection_parameter)}",
                r"n\cdot S+t(n\cdot q)+c=0",
                "The nonzero coefficient ensures the directed projection exists uniquely.",
            ),
            _st(
                "project",
                rf"H={_vec(foot)}",
                rule,
                "Substitute the parameter. Orthogonality is not assumed for a directed projection.",
                obj("point", "H", foot),
                obj("segment", "SH", source, foot - source),
            ),
            _st(
                "check",
                r"n\cdot H+c=0,\quad(H-S)\times q=0",
                r"H\in\pi,\quad H-S\parallel q",
                "Check both the target plane and the specified projection direction.",
            ),
        )
        return GeometryWork(
            rf"Project S onto plane pi in direction q: \(S={_vec(source)},\ "
            rf"q={_vec(projection_direction)},\ \pi:{plane}\).",
            vector_answer(foot),
            steps,
            (*objects, obj("point", "S", source), obj("vector", "q", source, projection_direction)),
            "Directed projection onto a plane",
        )
    direction = u + v + w if directed else u + w
    projected_direction = sp.simplify(
        direction - projection_direction * normal.dot(direction) / denominator
    )
    if projected_direction == sp.zeros(3, 1):
        raise ValueError("This line projects to a point, not to the advertised line")
    line, line_steps, line_objects = line_givens(p, source, direction)
    answer = ParametricGeometryAnswer(tuple(foot), (tuple(projected_direction),))
    steps = (
        *line_steps,
        *prep,
        _st(
            "project",
            rf"S={_vec(source)},\quad H=\operatorname{{pr}}(S)={_vec(foot)}",
            rule,
            "Choose the displayed point S on the source line, using its parameterisation, "
            "and project it onto the plane. The original givens remain in earlier drawings.",
            obj("point", "S", source),
            obj("point", "H", foot),
            obj("segment", "SH", source, foot - source),
            hide=preparation_labels(
                (*line_steps, *prep), (*objects, *line_objects), ("pi", "l", "n", "q")
            ),
        ),
        _st(
            "directions",
            rf"d={_vec(direction)},\quad "
            rf"d'=d-\frac{{n\cdot d}}{{n\cdot q}}q={_vec(projected_direction)}",
            r"\operatorname{pr}(S+t "
            r"d)=\operatorname{pr}(S)+t\left(d-\frac{n\cdot d}{n\cdot q}q\right)",
            "Separate the constant and parameter terms of the projection formula. The constant "
            "plane offset does not appear in the direction term.",
            obj("vector", "projected direction", foot, projected_direction),
        ),
        _st(
            "line",
            answer.latex(),
            r"X'=H+t d'",
            "The projected direction is nonzero, so the image is the whole displayed line.",
            obj("line", "image line", foot, projected_direction),
            hide=("projected direction",),
        ),
        _st(
            "check",
            r"n\cdot H+c=0,\quad n\cdot d'=0,\quad d'\ne0",
            r"n\cdot(H+t d')+c=0\quad\forall t\in\mathbb R",
            "Every image point lies in the target plane. The projection formula verifies the "
            "direction of every connecting segment.",
        ),
    )
    extra = rf",\ q={_vec(projection_direction)}" if directed else ""
    kind = "in direction q" if directed else "orthogonally"
    return GeometryWork(
        rf"Project line l onto plane pi {kind}: \({line},\ \pi:{plane}{extra}\). Enter affine "
        rf"equations x(t), y(t), z(t) of the image.",
        answer,
        steps,
        (
            *objects,
            *line_objects,
            *((obj("vector", "q", source, projection_direction),) if directed else ()),
        ),
        "The projection of a whole line",
    )


def _position_work(mode: str, p: GeometryParameters) -> GeometryWork:
    point, u, v, w = (sp.Matrix(a) for a in (p.p, p.u, p.v, p.w))
    if mode == "line-position":
        first, prep, objects = line_givens(p, point, u, "l")
        case = p.seed % 4
        q = point + p.k * u - v if case == 0 else point + w if case in (1, 2) else point + p.k * u
        direction = v if case in (0, 2) else u if case == 1 else -2 * u
        second, other_steps, other_objects = line_givens(p, q, direction, "m")
        cross = u.cross(direction)
        triple = (q - point).dot(cross)
        category = (
            "coincident"
            if cross == sp.zeros(3, 1) and (q - point).cross(u) == sp.zeros(3, 1)
            else "parallel"
            if cross == sp.zeros(3, 1)
            else "intersecting"
            if triple == 0
            else "skew"
        )
        steps = (
            *prep,
            *other_steps,
            _st(
                "directions",
                rf"P={_vec(point)},\ Q={_vec(q)},\ d_1={_vec(u)},\ d_2={_vec(direction)}",
                r"l:X=P+t d_1,\quad m:X=Q+s d_2",
                "Use a known point and a nonzero direction from each line. The following "
                "tests use these consistently named P, Q, d1 and d2.",
                obj("point", "P", point),
                obj("point", "Q", q),
                hide=preparation_labels(
                    (*prep, *other_steps), (*objects, *other_objects), ("l", "m")
                ),
            ),
            _st(
                "cross",
                rf"d_1\times d_2={_vec(cross)},\quad(Q-P)\times d_1={_vec((q - point).cross(u))}",
                r"d_1\times d_2=0\iff d_1\parallel d_2",
                "For parallel directions, a parallel joining displacement distinguishes the "
                "same line from two distinct parallel lines.",
            ),
            _st(
                "condition",
                rf"(Q-P)\cdot(d_1\times d_2)={sp.latex(triple)},\quad\text{{{category}}}",
                r"d_1\times d_2\ne0:\quad\text{intersection}\iff(Q-P)\cdot(d_1\times d_2)=0",
                "For nonparallel directions, a zero scalar triple product means coplanarity "
                "and one intersection; otherwise the lines are skew.",
            ),
        )
        return GeometryWork(
            rf"Classify the relative positions of the lines: \({first},\quad{second}\).",
            CategoryAnswer(category, ("intersecting", "parallel", "skew", "coincident")),
            steps,
            (*objects, *other_objects),
            "The four relative positions of lines",
        )
    normal = u.cross(v)
    case = p.seed % 3
    q = point + w if case != 2 else point + v
    direction = w if case == 0 else u
    line, a_steps, a_objects = line_givens(p, q, direction)
    plane, b_steps, b_objects, normal, offset = _plane_context(p)
    coefficient = normal.dot(direction)
    value = normal.dot(q) + offset
    category = "crossing" if coefficient != 0 else "contained" if value == 0 else "parallel"
    steps = (
        *a_steps,
        *b_steps,
        _st(
            "substitute",
            rf"n\cdot(Q+t d)+c=({sp.latex(coefficient)})t+({sp.latex(value)})",
            r"\alpha t+\beta=0",
            "Substitute the line into the plane equation without cancelling the parameter "
            "coefficient.",
            hide=preparation_labels(
                (*a_steps, *b_steps), (*a_objects, *b_objects), ("l", "pi", "n")
            ),
        ),
        _st(
            "condition",
            rf"\alpha={sp.latex(coefficient)},\quad\beta={sp.latex(value)},\quad\text{{{category}}}",
            r"\alpha\ne0:\text{ one point};\ \alpha=0,\beta\ne0:\text{ none};\ "
            r"\alpha=\beta=0:\text{ whole line}",
            "Distinguish one solution, no solutions and every real parameter value.",
        ),
    )
    return GeometryWork(
        rf"Classify the relative positions of line l and plane pi: \({line},\ \pi:{plane}\).",
        CategoryAnswer(category, ("crossing", "parallel", "contained")),
        steps,
        (*a_objects, *b_objects),
        "A line relative to a plane",
    )
