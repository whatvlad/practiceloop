"""Line/plane constructions for the existing versioned geometry provider."""

from typing import Any

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.answers.geometry import ParametricGeometryAnswer, PlaneEquationAnswer
from app.engine.generators.eigen_geometry import _line, _plane, _vec
from app.engine.generators.geometry_practice import (
    GeometryParameters,
    GeometryWork,
    _direction_givens,
    _point_givens,
    _st,
    obj,
    preparation_labels,
)
from app.engine.models import Answer

X = sp.Matrix(sp.symbols("x y z"))


def plane_basis(normal: Any) -> tuple[Any, Any]:
    n = sp.Matrix(normal)
    pivot = next(i for i in range(3) if n[i] != 0)
    result = []
    for j in range(3):
        if j != pivot:
            v = sp.zeros(3, 1)
            v[j], v[pivot] = 1, -n[j] / n[pivot]
            result.append(v)
    return tuple(result)


def cross_step(
    a: Any, b: Any, name: str = "n", origin: Any = (0, 0, 0), *, hide: tuple[str, ...] = ()
) -> Any:
    cross = a.cross(b)
    return _st(
        "cross",
        rf"{name}={_vec(a)}\times{_vec(b)}={_vec(cross)}",
        r"a\times b=(a_2b_3-a_3b_2,\ a_3b_1-a_1b_3,\ a_1b_2-a_2b_1)",
        "Use the coordinates in order. The result is perpendicular to each of the two "
        "independent vectors.",
        obj("vector", name, origin, cross),
        hide=hide,
    )


def linear_rule(augmented: Any) -> str:
    return str(sp.latex(augmented) + r"\ \longrightarrow\ " + sp.latex(augmented.rref()[0]))


def plane_givens(p: GeometryParameters) -> tuple[Any, ...]:
    point, u, v = (sp.Matrix(a) for a in (p.p, p.u, p.v))
    n = u.cross(v)
    if p.level == 1:
        return (
            rf"P={_vec(point)},\ n={_vec(n)}",
            (),
            (obj("point", "P", point), obj("normal", "n", point, n)),
            point,
            n,
            (u, v),
        )
    if p.level == 2:
        return (
            rf"P={_vec(point)},\ u={_vec(u)},\ v={_vec(v)}",
            (cross_step(u, v, origin=point),),
            (obj("point", "P", point), obj("vector", "u", point, u), obj("vector", "v", point, v)),
            point,
            n,
            (u, v),
        )
    given, prep, objects = _point_givens(p, point)
    directions = _st(
        "directions",
        rf"u=C-P={_vec(u)},\quad v=D-P={_vec(v)}",
        r"u=C-P,\quad v=D-P",
        "After finding P, form two independent directions in the required plane.",
        obj("vector", "u", point, u),
        obj("vector", "v", point, v),
    )
    return (
        rf"{given},\ C={_vec(point + u)},\ D={_vec(point + v)}",
        (*prep, directions, cross_step(u, v, origin=point)),
        (*objects, obj("point", "C", point + u), obj("point", "D", point + v)),
        point,
        n,
        (u, v),
    )


def line_givens(
    p: GeometryParameters, point: Any, direction: Any, label: str = "l"
) -> tuple[Any, ...]:
    point, direction = sp.Matrix(point), sp.Matrix(direction)
    base_name, end_name, direction_name = f"P_{{{label}}}", f"Q_{{{label}}}", f"d_{{{label}}}"
    if p.level == 1:
        return (
            rf"{label}:{_line(tuple(point), tuple(direction))}",
            (),
            (obj("line", label, point, direction),),
        )
    if p.level == 2:
        end = point + direction
        return (
            rf"{label}:\ {base_name}={_vec(point)},\ {end_name}={_vec(end)}",
            (
                _st(
                    "directions",
                    rf"{direction_name}={end_name}-{base_name}={_vec(direction)}",
                    r"d=Q-P",
                    "The line is determined by two distinct points.",
                    obj("vector", "d " + label, point, direction),
                ),
            ),
            (
                obj("point", "P " + label, point),
                obj("point", "Q " + label, end),
                obj("line", label, point, direction),
            ),
        )
    a, b = plane_basis(direction)
    raw = a.cross(b)
    pivot = next(i for i in range(3) if direction[i] != 0)
    factor = sp.simplify(raw[pivot] / direction[pivot])
    other = [i for i in range(3) if i != pivot]
    system = sp.Matrix(
        [[n[i] for i in other] + [n.dot(point) - n[pivot] * point[pivot]] for n in (a, b)]
    )
    statement = (
        rf"{label}:\ "
        rf"\begin{{cases}}{_plane(a, -a.dot(point))}\\{_plane(b, -b.dot(point))}\end{{cases}}"
    )
    prep = (
        cross_step(a, b, f"d_{{{label}0}}", point),
        _st(
            "scale",
            rf"{direction_name}=\frac{{{_vec(raw)}}}{{{sp.latex(factor)}}}={_vec(direction)}",
            r"\lambda d\text{ is the same line direction for }\lambda\ne0",
            "Rescale a nonzero direction to keep the parameterisation concise.",
            obj("vector", "d " + label, point, direction),
        ),
        _st(
            "solve",
            rf"{str(X[pivot])}={sp.latex(point[pivot])}\quad\Longrightarrow\quad "
            rf"{base_name}={_vec(point)}",
            linear_rule(system),
            "Choose the displayed value of the free coordinate and solve the two linear "
            "equations for the other coordinates in their x, y, z order. The displayed "
            "augmented matrix reduces to the two solved coordinates. Any free value is valid.",
            obj("point", "P " + label, point),
        ),
    )
    return (
        statement,
        prep,
        (
            obj("plane", label + " plane one", point, *plane_basis(a)),
            obj("plane", label + " plane two", point, *plane_basis(b)),
            obj("line", label, point, direction),
        ),
    )


def construction_work(mode: str, p: GeometryParameters) -> GeometryWork:
    answer: Answer
    point, u, v, w = (sp.Matrix(a) for a in (p.p, p.u, p.v, p.w))
    n = u.cross(v)
    if mode in {"plane-equation", "plane-parameterisation"}:
        given, prep, objects, point, n, basis = plane_givens(p)
        origin_rule = r"n\cdot(X-P)=0"
        if mode == "plane-equation":
            qualifier = (
                "through P with normal n"
                if p.level == 1
                else "through P parallel to u and v"
                if p.level == 2
                else "through P, C and D"
            )
            statement = (
                rf"Find an equation of the plane {qualifier}: \({given}\). Enter "
                rf"the affine left-hand side of an equation equal to zero. Any equivalent "
                rf"equation is accepted."
            )
            steps = (
                *prep,
                _st(
                    "substitute",
                    sp.latex(n.dot(X - point)) + "=0",
                    origin_rule,
                    "The displacement from a point of the plane is perpendicular to its "
                    "nonzero normal.",
                ),
                _st(
                    "plane",
                    _plane(n, -n.dot(point)),
                    r"n\cdot X+c=0,\quad c=-n\cdot P",
                    "Expand the dot product and collect the constant term.",
                    obj("plane", "required plane", point, *basis),
                ),
                _st(
                    "check",
                    rf"n\cdot P+c={sp.latex(n.dot(point) - n.dot(point))},\quad n\ne0",
                    origin_rule,
                    "The given point satisfies the equation and the normal has the required "
                    "direction.",
                ),
            )
            return GeometryWork(
                statement,
                PlaneEquationAnswer(tuple(n), -n.dot(point)),
                steps,
                objects,
                "A plane from geometric data",
            )
        if p.level == 2:
            offset = -n.dot(point)
            pivot = next(i for i in range(3) if n[i] != 0)
            anchor = sp.zeros(3, 1)
            anchor[pivot] = -offset / n[pivot]
            basis = plane_basis(n)
            statement = (
                rf"Parameterise the plane \({_plane(n, offset)}\). Enter x(s,t), y(s,t), "
                rf"z(s,t); any affine parameterisation of the whole plane is accepted."
            )
            objects = (obj("plane", "given plane", point, *basis),)
            prep = (
                _st(
                    "solve",
                    rf"P_0={_vec(anchor)}",
                    r"n\cdot P_0+c=0",
                    "Set two coordinates to zero and solve for a coordinate with a nonzero "
                    "normal coefficient.",
                    obj("point", "P zero", anchor),
                ),
                _st(
                    "basis",
                    rf"a={_vec(basis[0])},\quad b={_vec(basis[1])}",
                    r"n\cdot a=n\cdot b=0,\quad a\times b\ne0",
                    "Set each free coordinate to one in turn in the homogeneous plane "
                    "equation. The two directions are independent.",
                    obj("vector", "a", anchor, basis[0]),
                    obj("vector", "b", anchor, basis[1]),
                ),
            )
            point = anchor
        else:
            qualifier = (
                "through P with directions u and v" if p.level == 1 else "through P, C and D"
            )
            if p.level == 1:
                given = given.replace("n=" + _vec(n), "u=" + _vec(u) + ", v=" + _vec(v))
            statement = (
                rf"Parameterise the plane "
                rf"{qualifier}: \({given}\). Enter x(s,t), y(s,t), z(s,t)."
            )
            if p.level == 1:
                objects = (
                    obj("point", "P", point),
                    obj("vector", "u", point, u),
                    obj("vector", "v", point, v),
                )
        answer = ParametricGeometryAnswer(tuple(point), tuple(tuple(a) for a in basis))
        steps = (
            *prep,
            _st(
                "result",
                answer.latex(),
                r"X=P+s\,a+t\,b,\quad s,t\in\mathbb R",
                "Two independent in-plane directions cover the whole plane.",
                obj("plane", "required plane", point, *basis),
            ),
            _st(
                "check",
                r"n\cdot a=n\cdot b=0,\quad n\cdot P+c=0",
                r"\operatorname{rank}[a\ b]=2",
                "Both directions are parallel to the plane, and their independence prevents "
                "the parameterisation from collapsing to a line.",
            ),
        )
        return GeometryWork(statement, answer, steps, objects, "Parametric equations of a plane")
    if mode == "line-equation":
        if p.level == 1:
            given, prep, objects = (
                rf"P={_vec(point)},\ d={_vec(w)}",
                (),
                (obj("point", "P", point), obj("vector", "d", point, w)),
            )
            direction = w
        elif p.level == 2:
            given, prep, objects = line_givens(p, point, w)
            direction = w
        else:
            p_text, p_steps, p_objects = _point_givens(p, point)
            given = (
                rf"{p_text},\ \pi_1:{_plane(u, -u.dot(point + w))},\ "
                rf"\pi_2:{_plane(v, -v.dot(point + w))}"
            )
            prep = (*p_steps, cross_step(u, v, "d", point))
            objects = (
                *p_objects,
                obj("plane", "pi one", point + w, *plane_basis(u)),
                obj("plane", "pi two", point + w, *plane_basis(v)),
            )
            direction = n
        answer = ParametricGeometryAnswer(tuple(point), (tuple(direction),))
        qualifier = (
            "through P with direction d"
            if p.level == 1
            else "through the two given points"
            if p.level == 2
            else "through P and parallel to the intersection of pi one and pi two"
        )
        statement = rf"Find parametric equations of the line {qualifier}: "
        statement += rf"\({given}\). Enter x(t), y(t), z(t)."
        steps = (
            *prep,
            _st(
                "line",
                answer.latex(),
                r"X=P+t\,d,\quad t\in\mathbb R",
                "Add the same real parameter times the direction to each coordinate.",
                obj("line", "required line", point, direction),
            ),
            _st(
                "check",
                rf"X(0)={_vec(point)},\quad d={_vec(direction)}\ne0",
                r"X(t)-X(0)=t\,d",
                "The parameterisation passes through the required point and has the required "
                "nonzero direction.",
            ),
        )
        return GeometryWork(statement, answer, steps, objects, "A line from geometric data")
    if mode == "containing-plane":
        if p.level == 1:
            given = rf"l:{_line(tuple(point), tuple(u))},\ Q={_vec(point + v)}"
            intro = "Find the plane containing line l and point Q"
            prep = (
                _st(
                    "directions",
                    rf"d={_vec(u)},\quad Q-P={_vec(v)}",
                    r"n=d\times(Q-P)",
                    "A direction of the line and the displacement to the extra point are "
                    "independent.",
                ),
            )
            objects = (obj("line", "l", point, u), obj("point", "Q", point + v))
        elif p.level == 2:
            given = rf"l:{_line(tuple(point), tuple(u))},\ m:{_line(tuple(point + v), tuple(u))}"
            intro = "Find the plane containing the two distinct parallel lines"
            prep = (
                _st(
                    "directions",
                    rf"d={_vec(u)},\quad Q-P={_vec(v)}",
                    r"n=d\times(Q-P)",
                    "Use a line direction and a displacement joining one point on each line.",
                ),
            )
            objects = (obj("line", "l", point, u), obj("line", "m", point + v, u))
        else:
            first, first_steps, first_objects = line_givens(p, point, u, "l")
            second, second_steps, second_objects = line_givens(p, point, v, "m")
            given = rf"{first},\quad {second}"
            intro = "Find the plane containing the two intersecting lines"
            prep = (*first_steps, *second_steps)
            objects = (*first_objects, *second_objects)
        steps = (
            *prep,
            cross_step(u, v, origin=point),
            _st(
                "plane",
                _plane(n, -n.dot(point)),
                r"n\cdot(X-P)=0",
                "Use a point on the first line to find the constant term.",
                obj("plane", "required plane", point, u, v),
            ),
            _st(
                "check",
                r"n\cdot u=n\cdot v=0,\quad n\cdot P+c=0",
                r"u\times v\ne0",
                "The candidate contains both independent directions and the required points, "
                "so it is the unique plane.",
            ),
        )
        return GeometryWork(
            rf"{intro}: \({given}\). Enter the affine left-hand side equal to zero.",
            PlaneEquationAnswer(tuple(n), -n.dot(point)),
            steps,
            objects,
            "A plane containing lines",
        )
    if mode == "perpendicular-line":
        if p.level < 3:
            if p.level == 1:
                given = rf"P={_vec(point)},\ u={_vec(u)},\ v={_vec(v)}"
                prep = ()
                objects = (
                    obj("point", "P", point),
                    obj("vector", "u", (0, 0, 0), u),
                    obj("vector", "v", (0, 0, 0), v),
                )
            else:
                given = (
                    rf"P={_vec(point)},\ l:{_line(tuple(point + w), tuple(u))},\ "
                    rf"m:{_line(tuple(point + v + w), tuple(v))}"
                )
                prep = (
                    _st(
                        "directions",
                        rf"u={_vec(u)},\quad v={_vec(v)}",
                        r"X=A+t\,d\Longrightarrow\text{direction }d",
                        "Read the direction multiplying the parameter in each line equation.",
                    ),
                )
                objects = (
                    obj("point", "P", point),
                    obj("line", "l", point + w, u),
                    obj("line", "m", point + v + w, v),
                )
            direction = n
            prep = (*prep, cross_step(u, v, "d", point))
            intro = (
                "Find a line through P whose direction is perpendicular to both given directions"
            )
        else:
            q = point + v
            parameter = -u.dot(v) / u.dot(w)
            meet = q + parameter * w
            direction = meet - point
            given = rf"P={_vec(point)},\ u={_vec(u)},\ l:{_line(tuple(q), tuple(w))}"
            intro = "Find the line through P perpendicular to u and intersecting l"
            objects = (
                obj("point", "P", point),
                obj("vector", "u", point, u),
                obj("line", "l", q, w),
            )
            prep = (
                _st(
                    "constraints",
                    rf"H={_vec(q)}+t{_vec(w)},\quad u\cdot(H-P)=0",
                    r"d\perp u\iff d\cdot u=0",
                    "Write a point on the given line and impose perpendicularity of the "
                    "connecting direction.",
                ),
                _st(
                    "parameter",
                    rf"t=-\frac{{u\cdot(Q-P)}}{{u\cdot w}}={sp.latex(parameter)}",
                    r"u\cdot(Q-P)+t(u\cdot w)=0",
                    "The nonzero coefficient ensures a unique intersection point.",
                ),
                _st(
                    "intersection",
                    rf"H={_vec(meet)},\quad d=H-P={_vec(direction)}",
                    r"d=H-P",
                    "The nonzero displacement from P to H gives the required line direction.",
                    obj("point", "H", meet),
                    obj("vector", "d", point, direction),
                ),
            )
        answer = ParametricGeometryAnswer(tuple(point), (tuple(direction),))
        steps = (
            *prep,
            _st(
                "line",
                answer.latex(),
                r"X=P+t\,d",
                "This answer parameter is independent of any parameter in a given line.",
                obj("line", "required line", point, direction),
            ),
            _st(
                "check",
                rf"u\cdot d={sp.latex(u.dot(direction))}",
                r"u\cdot d=0",
                "Check the perpendicularity condition; the construction also satisfies the "
                "required incidence.",
            ),
        )
        return GeometryWork(
            rf"{intro}: \({given}\). Enter x(t), y(t), z(t).",
            answer,
            steps,
            objects,
            "A perpendicular line",
        )
    if mode == "parallel-parameter":
        given, prep, objects = _direction_givens(p, w)
        target = u.cross(w)
        pivot = next(i for i in range(3) if w[i] != 0)
        a = sp.Symbol("a")
        unknown = target.copy()
        unknown[pivot] = a
        offset = 1 - target.dot(point)
        equation = sp.expand(unknown.dot(w))
        steps = (
            *prep,
            _st(
                "constraints",
                sp.latex(equation) + "=0",
                r"l\parallel\pi\Longrightarrow n(a)\cdot d=0",
                "A line parallel to a plane has direction perpendicular to its normal.",
            ),
            _st(
                "parameter",
                rf"a={sp.latex(target[pivot])}",
                r"\alpha a+\beta=0\iff a=-\beta/\alpha",
                "The coefficient is nonzero, so the parameter value is unique.",
                obj("normal", "n", point, target),
                obj("plane", "pi", point - target / target.dot(target), *plane_basis(target)),
            ),
            _st(
                "check",
                rf"n\cdot d=0,\quad n\cdot P+c={sp.latex(target.dot(point) + offset)}\ne0",
                r"l\text{ disjoint from }\pi\iff n\cdot d=0,\ n\cdot P+c\ne0",
                "The second condition excludes a line lying in the plane.",
            ),
        )
        statement = (
            rf"Find a for which the line is parallel to and disjoint from the plane: "
            rf"\(l:X={_vec(point)}+t d,\ {given},\ \pi:{sp.latex(unknown.dot(X) + offset)}=0\)."
        )
        return GeometryWork(
            statement,
            FormulaAnswer(target[pivot]),
            steps,
            (*objects, obj("line", "l", point, w)),
            "A parameter for strict line-plane parallelism",
        )
    if mode == "normal-parameters":
        a = 1 + u.dot(u)
        d2, d3 = 2 + abs(sum(v)), 1 + abs(sum(w))
        b, c = sp.symbols("b c")
        normal = sp.Matrix((-a, -b, 1))
        direction = sp.Matrix((c, d2, d3))
        b_value, c_value = -sp.Rational(d2, d3), -a * d3
        actual = normal.subs(b, b_value)
        prep = ()
        if p.level == 1:
            givens = (
                rf"\pi:{sp.latex(normal.dot(X - point))}=0,\quad "
                rf"l:X={_vec(point + w)}+t{_vec(direction)}"
            )
        else:
            first, second = sp.Matrix((1, 0, a)), sp.Matrix((0, 1, b))
            givens = (
                rf"\pi:X={_vec(point)}+s{_vec(first)}+r{_vec(second)},\quad "
                rf"l:X={_vec(point + w)}+t{_vec(direction)}"
            )
            prep = (
                _st(
                    "normal",
                    rf"n={_vec(first)}\times{_vec(second)}={_vec(normal)}",
                    r"n=u\times v",
                    "The spanning directions are independent for every b.",
                ),
            )
            if p.level == 3:
                givens = (
                    rf"\pi\text{{ through }}P={_vec(point)},\ Q={_vec(point + first)},\ "
                    rf"R={_vec(point + second)},\quad l:X={_vec(point + w)}+t{_vec(direction)}"
                )
                prep = (
                    _st(
                        "directions",
                        rf"Q-P={_vec(first)},\quad R-P={_vec(second)}",
                        r"u=Q-P,\quad v=R-P",
                        "Form both spanning directions, retaining the unknown parameter symbol.",
                    ),
                    *prep,
                )
        steps = (
            *prep,
            _st(
                "constraints",
                rf"(c,{d2},{d3})=\lambda(-{a},-b,1)",
                r"l\perp\pi\iff d\parallel n",
                "A perpendicular line is directed along a normal of the plane.",
            ),
            _st(
                "scale",
                rf"\lambda={d3},\quad {d2}=-{d3}b,\quad c=-{d3}\cdot {a}",
                r"d_i=\lambda n_i",
                "Use the fixed third coordinate to determine the scale, then compare the "
                "remaining coordinates.",
            ),
            _st(
                "result",
                rf"b={sp.latex(b_value)},\quad c={sp.latex(c_value)}",
                r"b=-d_2/d_3,\quad c=-a d_3",
                "These values satisfy all three proportionality equations.",
                obj("normal", "solved normal", point, actual),
                obj("plane", "pi", point, *plane_basis(actual)),
                obj("line", "l", point + w, (c_value, d2, d3)),
            ),
            _st(
                "check",
                rf"d={d3}n,\quad n\ne0",
                r"d\times n=0",
                "The third normal coordinate is one, so the plane and the line remain "
                "nondegenerate.",
            ),
        )
        answer = OrderedAnswer(
            (FormulaAnswer(b_value), FormulaAnswer(c_value)), ("Parameter b", "Parameter c")
        )
        return GeometryWork(
            rf"Find b and c so that line l is perpendicular to plane pi: \({givens}\). "
            rf"Directions depending on the unknown parameters are not drawn before they are "
            rf"found.",
            answer,
            steps,
            (obj("point", "P", point),),
            "Parameters for a perpendicular line and plane",
        )
    if mode in {"planes-common-point", "planes-common-line", "planes-three-lines"}:
        a, b = sp.symbols("a b")
        threshold = p.k + 1
        c1, c2 = u.dot(point), v.dot(point)
        compatible = p.k * c1 + c2
        third = p.k * u + v + (a - threshold) * w
        normal_matrix = sp.Matrix.vstack(u.T, v.T, third.T)
        determinant = sp.factor(normal_matrix.det())
        criterion = {
            "planes-common-point": r"a\ne A\ \text{or}\ b=B",
            "planes-common-line": r"a=A\ \text{and}\ b=B",
            "planes-three-lines": r"a=A\ \text{and}\ b\ne B",
        }[mode]
        wanted = {
            "planes-common-point": "have at least one common point",
            "planes-common-line": "have exactly one common line",
            "planes-three-lines": "intersect pairwise in three distinct lines",
        }[mode]
        p_text, p_steps, p_objects = _point_givens(p, point, endpoints=("E", "F"))
        if p.level == 1:
            prep = ()
            given = rf"\pi_1:{_plane(u, -c1)},\quad\pi_2:{_plane(v, -c2)}"
        else:
            given = (
                rf"\pi_1\text{{ through }}P\text{{ with normal }}{_vec(u)},\quad"
                rf"\pi_2\text{{ through }}P\text{{ with normal }}{_vec(v)},\quad {p_text}"
            )
            prep = (
                *p_steps,
                _st(
                    "plane",
                    rf"\pi_1:{_plane(u, -c1)},\quad\pi_2:{_plane(v, -c2)}",
                    r"n\cdot(X-P)=0",
                    "Convert both point-normal descriptions to equations before comparing ranks.",
                ),
            )
        exceptional_normal = p.k * u + v
        common_direction = u.cross(v)
        example = r"\text{Diagram: }a=A,\ b=B"
        example_a = threshold + (1 if mode == "planes-common-point" else 0)
        example_b = compatible + (1 if mode == "planes-three-lines" else 0)
        example_objects: tuple[Any, ...] = ()
        if mode == "planes-common-point":
            example_normal = exceptional_normal + w
            system = sp.Matrix.vstack(u.T, v.T, example_normal.T)
            meeting = system.inv() * sp.Matrix((c1, c2, compatible))
            example = rf"\text{{Diagram: }}a=A+1,\ b=B,\quad S={_vec(meeting)}"
            example_objects = (
                obj("plane", "pi three", meeting, *plane_basis(example_normal)),
                obj("normal", "n3", meeting, example_normal),
                obj("point", "S", meeting),
            )
        elif mode == "planes-three-lines":
            v_perp = v - u * u.dot(v) / u.dot(u)
            u_perp = u - v * u.dot(v) / v.dot(v)
            first = point + v_perp / v.dot(v_perp)
            second = point + u_perp / (p.k * u.dot(u_perp))
            example = r"\text{Diagram: }a=A,\ b=B+1,\quad l_{ij}=\pi_i\cap\pi_j"
            example_objects = (
                obj("plane", "pi three", first, *plane_basis(exceptional_normal)),
                obj("line", "l13", first, common_direction),
                obj("line", "l23", second, common_direction),
            )
        steps = (
            *prep,
            _st(
                "rank",
                rf"\det N={sp.latex(determinant)}",
                rf"\det {sp.latex(normal_matrix)}={sp.latex(determinant)},\quad "
                r"\det N=n_1\cdot(n_2\times n_3)",
                "Outside the exceptional parameter value, all three independent equations have "
                "a unique common point.",
                hide=preparation_labels(prep, p_objects, ("P",)),
            ),
            _st(
                "parameter",
                rf"a=A={threshold}\quad\Longrightarrow\quad n_3={p.k}n_1+n_2",
                r"\det N=0",
                "At the exceptional value, the third normal is a combination of the first two. "
                "Those first two normals remain independent.",
                obj("normal", "n3", point, exceptional_normal),
            ),
            _st(
                "constraints",
                rf"b=B={p.k}\cdot({sp.latex(c1)})+({sp.latex(c2)})={sp.latex(compatible)}"
                r",\quad\text{Diagram: }a=A,\ b=B",
                r"[n_3\mid b]=\alpha[n_1\mid c_1]+\beta[n_2\mid c_2]",
                "The same combination must also hold for the right-hand side. Otherwise the "
                "augmented matrix has larger rank. Rank counts independent equations. The "
                "diagram now shows the common-line boundary case, with both parameters fixed.",
                obj("plane", "pi three", point, *plane_basis(exceptional_normal)),
                obj("line", "l12", point, common_direction),
                caption=f"Example: a={threshold}, b={compatible}. Common-line case.",
            ),
            _st(
                "condition",
                rf"A={threshold},\quad B={sp.latex(compatible)},\quad {criterion}"
                rf",\quad {example}",
                r"\operatorname{rank}N=\operatorname{rank}[N\mid c]",
                "At a=A and b=B the common set is a line. At a=A and b different from B there "
                "is no common point, but each pair intersects in a distinct parallel line "
                "because both combination coefficients are nonzero. The diagram illustrates "
                "the explicitly labelled parameter pair; the criterion covers every pair.",
                *example_objects,
                caption=f"Example: a={example_a}, b={example_b}. Full criterion above.",
            ),
        )
        objects = (
            *(() if p.level == 1 else p_objects),
            obj("plane", "pi one", point, *plane_basis(u)),
            obj("plane", "pi two", point, *plane_basis(v)),
        )
        statement = (
            rf"Find constants A and B in the complete criterion \({criterion}\) for which the "
            rf"planes {wanted}: \({given},\quad\pi_3:{sp.latex(third.dot(X))}=b\). Enter A and "
            rf"B; the displayed criterion specifies the full set of parameter pairs."
        )
        answer = OrderedAnswer(
            (FormulaAnswer(threshold), FormulaAnswer(compatible)), ("Exceptional a", "Compatible b")
        )
        return GeometryWork(
            statement, answer, steps, objects, "All parameter cases for three planes"
        )
    raise ValueError("Unknown line or plane construction")
