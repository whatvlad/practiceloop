"""Expandable explanations for the existing parameter-derived vector exercises."""

from typing import Any

import sympy as sp

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
    _vec,
)
from app.visuals.geometry import _params

Rule = dict[str, str]


def _rule(title: str, latex: str, explanation: str) -> Rule:
    return {"title": title, "latex": latex, "explanation": explanation}


def _edge_rule(a: Any, b: Any, c: Any, d: Any | None = None) -> Rule:
    ab, ac = b - a, c - a
    latex = rf"\vec{{AB}}=B-A={_vec(ab)},\qquad\vec{{AC}}=C-A={_vec(ac)}"
    if d is not None:
        latex += rf",\qquad\vec{{AD}}=D-A={_vec(d - a)}"
    return _rule(
        "Vectors from points",
        latex,
        "Subtract the starting point from the end point, coordinate by coordinate.",
    )


def _cross_rule(first: Any, second: Any, first_name: str, second_name: str) -> Rule:
    cross = first.cross(second)
    return _rule(
        "Cross product",
        rf"{first_name}\times {second_name}=(a_2b_3-a_3b_2,\ a_3b_1-a_1b_3,\ "
        rf"a_1b_2-a_2b_1)={_vec(cross)}",
        "The formula uses the coordinates of the first vector as a and those of the second as b. "
        "The result is perpendicular to both vectors.",
    )


def _volume_rule(a: Any, b: Any, c: Any, d: Any) -> Rule:
    ab, ac, ad = b - a, c - a, d - a
    normal = ab.cross(ac)
    triple = normal.dot(ad)
    volume = sp.Rational(abs(triple), 6)
    return _rule(
        "Volume from a scalar triple product",
        rf"\vec{{AB}}\times\vec{{AC}}={_vec(normal)},\quad"
        rf"(\vec{{AB}}\times\vec{{AC}})\cdot\vec{{AD}}={sp.latex(triple)},\quad"
        rf"V=\frac{{|{sp.latex(triple)}|}}{{6}}={sp.latex(volume)}",
        "The absolute scalar triple product is the volume of a parallelepiped. "
        "A tetrahedron with the same three edges has one sixth of that volume.",
    )


def _area_rule(a: Any, b: Any, c: Any) -> Rule:
    normal = (b - a).cross(c - a)
    norm = normal.norm()
    return _rule(
        "Area from a cross product",
        rf"\vec{{AB}}\times\vec{{AC}}={_vec(normal)},\quad"
        rf"|\vec{{AB}}\times\vec{{AC}}|={sp.latex(norm)},\quad"
        rf"S_{{ABC}}=\frac{{{sp.latex(norm)}}}{{2}}={sp.latex(norm / 2)}",
        "The cross product length is the area of the parallelogram. "
        "The triangle occupies half of it.",
    )


def step_rules(record: dict[str, object]) -> tuple[tuple[Rule, ...], ...]:
    params = _params(record)
    if params is None:
        return ()
    version = record["generator_version"]
    if version == PerpendicularParameter.version:
        if not isinstance(params, PerpendicularParameters):
            raise ValueError("Invalid perpendicular-parameter data")
        u2, v2 = PerpendicularParameter().squared_lengths(params)
        factor = 2 if params.level == 3 else 1
        root = sp.radsimp(sp.sqrt(u2 / (factor * v2)))
        parameter_leading: tuple[tuple[Rule, ...], ...] = ()
        if params.level == 2:
            squares_u = "+".join(rf"({value})^2" for value in params.u)
            squares_v = "+".join(rf"({value})^2" for value in params.v)
            parameter_leading = (
                (
                    _rule(
                        "Squared lengths",
                        rf"|u|^2={squares_u}={u2},\quad |v|^2={squares_v}={v2}",
                        "Square and add the coordinates of each vector.",
                    ),
                ),
            )
        elif params.level == 3:
            parameter_leading = (
                (
                    _rule(
                        "Perpendicular vectors",
                        r"u\cdot v=0",
                        "This dot product is zero because the given vectors are perpendicular.",
                    ),
                ),
            )
        if factor == 1:
            expansion = r"(u+\alpha v)\cdot(u-\alpha v)=|u|^2-\alpha^2|v|^2"
            why = (
                "The two mixed dot-product terms are equal and have opposite signs, so they cancel."
            )
        else:
            expansion = r"(u+\alpha v)\cdot(u-2\alpha v)=|u|^2-\alpha(u\cdot v)-2\alpha^2|v|^2"
            why = (
                "Distribute the dot product, then use the given perpendicularity "
                "to remove the mixed term."
            )
        return parameter_leading + (
            (_rule("Expand the dot product", expansion + rf"={u2}-{factor * v2}\alpha^2=0", why),),
            (
                _rule(
                    "Isolate the square",
                    rf"\alpha^2=\frac{{{u2}}}{{{factor * v2}}}",
                    "The given vectors are nonzero, so division by the squared length is valid.",
                ),
            ),
            (
                _rule(
                    "Both real roots",
                    rf"\alpha=\pm {sp.latex(root)}",
                    "A positive square has both a negative and a positive real square root.",
                ),
            ),
        )
    if version == VectorLengthPractice.version:
        if not isinstance(params, VectorLengthParameters):
            raise ValueError("Invalid vector-length parameters")
        a, b = sp.Integer(params.a), sp.Integer(params.b)
        cosine = sp.cos(sp.pi * params.angle / 180)
        dot = a * b * cosine
        squared = a**2 + b**2 - 2 * dot
        if params.level == 3:
            sum_squared = a**2 + b**2 + 2 * dot
            first = _rule(
                "Parallelogram identity",
                r"|u+v|^2+|u-v|^2=2|u|^2+2|v|^2",
                "Expand both squared lengths using dot products. The mixed terms cancel.",
            )
            calculation = rf"2({a})^2+2({b})^2-({sp.latex(sum_squared)})={sp.latex(squared)}"
        else:
            first = _rule(
                "Dot product and angle",
                rf"u\cdot v=|u||v|\cos({params.angle}^\circ)="
                rf"{a}\cdot{b}\cdot {sp.latex(cosine)}={sp.latex(dot)}",
                "For perpendicular vectors the cosine is zero. Otherwise use the given angle.",
            )
            calculation = rf"({a})^2+({b})^2-2({sp.latex(dot)})={sp.latex(squared)}"
        return (
            (first,),
            (
                _rule(
                    "Squared difference",
                    rf"|u-v|^2={calculation}",
                    "Substitute the given lengths into the appropriate identity.",
                ),
            ),
            (
                _rule(
                    "Length",
                    rf"|u-v|=\sqrt{{{sp.latex(squared)}}}={sp.latex(sp.sqrt(squared))}",
                    "A length is nonnegative, so use the nonnegative square root.",
                ),
            ),
        )
    if version == ScalarVectorExpression.version:
        if not isinstance(params, VectorExpressionParameters):
            raise ValueError("Invalid scalar-expression parameters")
        u, v, w = (sp.Matrix(vector) for vector in (params.u, params.v, params.w))
        if params.level == 1 and params.seed % 2:
            terms = "+".join(rf"({u[i]})({w[i]})" for i in range(3))
            return (
                (
                    _rule(
                        "Dot product",
                        rf"u\cdot w={terms}={sp.latex(u.dot(w))}",
                        "Multiply corresponding coordinates and add the products.",
                    ),
                ),
            )
        if params.level == 1:
            squares = "+".join(rf"({v[i]})^2" for i in range(3))
            return (
                (
                    _rule(
                        "Vector length",
                        rf"|v|=\sqrt{{{squares}}}={sp.latex(v.norm())}",
                        "Square all three coordinates, add them, then take the nonnegative "
                        "square root.",
                    ),
                ),
            )
        if params.level == 2 and params.seed % 2:
            squares = "+".join(rf"({w[i]})^2" for i in range(3))
            terms = "+".join(rf"({v[i]})({w[i]})" for i in range(3))
            length, dot = w.norm(), v.dot(w)
            return (
                (
                    _rule(
                        "Vector length",
                        rf"|w|=\sqrt{{{squares}}}={sp.latex(length)}",
                        "Square and add the coordinates, then take the nonnegative square root.",
                    ),
                ),
                (
                    _rule(
                        "Dot product",
                        rf"v\cdot w={terms}={sp.latex(dot)}",
                        "Multiply corresponding coordinates and add the products.",
                    ),
                ),
                (
                    _rule(
                        "Scalar subtraction",
                        rf"|w|-v\cdot w={sp.latex(length)}-({sp.latex(dot)})"
                        rf"={sp.latex(length - dot)}",
                        "Subtract the dot product, preserving its sign.",
                    ),
                ),
            )
        first = w - v if params.level == 2 else u.cross(v)
        if params.level == 2:
            subtraction = ",\\ ".join(rf"({w[i]})-({v[i]})" for i in range(3))
            first_rule = _rule(
                "Coordinate subtraction",
                rf"w-v=({subtraction})={_vec(first)}",
                "Subtract the corresponding coordinates in order.",
            )
            lhs, dot_with = r"u\cdot(w-v)", u
        else:
            first_rule = _cross_rule(u, v, r"\vec u", r"\vec v")
            lhs, dot_with = r"(u\times v)\cdot w", w
        terms = "+".join(rf"({first[i]})({dot_with[i]})" for i in range(3))
        dot = first.dot(dot_with)
        return (
            (first_rule,),
            (
                _rule(
                    "Dot product",
                    rf"{lhs}={terms}={sp.latex(dot)}",
                    "Multiply corresponding coordinates and add the products. "
                    "The result is a scalar.",
                ),
            ),
        )
    if version == SolidPractice.version:
        if not isinstance(params, SolidParameters):
            raise ValueError("Invalid solid parameters")
        a, b, c, d = (sp.Matrix(point) for point in params.points)
        target = (c + d) / 2 if params.level == 3 else d
        u, v, w = b - a, c - a, target - a
        third = "N" if params.level == 3 else "D"
        names: tuple[str, ...] = (r"\vec{AB}", r"\vec{AC}", rf"\vec{{A{third}}}")
        solid_leading: tuple[tuple[Rule, ...], ...] = ()
        if params.level == 3:
            solid_leading += (
                (
                    _rule(
                        "Midpoint",
                        rf"N=\frac{{C+D}}{{2}}={_vec(target)}",
                        "Average the corresponding coordinates of C and D.",
                    ),
                ),
            )
        if params.level > 1:
            solid_leading += (
                (
                    _rule(
                        "Vectors from points",
                        rf"{names[0]}={_vec(u)},\quad {names[1]}={_vec(v)},\quad "
                        rf"{names[2]}={_vec(w)}",
                        "Subtract A from each endpoint, coordinate by coordinate.",
                    ),
                ),
            )
        normal = u.cross(v)
        triple = normal.dot(w)
        volume = abs(triple) / 6
        if params.mode == "parallelepiped-area":
            pairs = (
                (u, v, names[0], names[1]),
                (u, w, names[0], names[2]),
                (v, w, names[1], names[2]),
            )
            face_rules: tuple[tuple[Rule, ...], ...] = tuple(
                (
                    _cross_rule(first, second, first_name, second_name),
                    _rule(
                        "Face area",
                        rf"|{first_name}\times {second_name}|="
                        rf"{sp.latex(first.cross(second).norm())}",
                        "The cross product length equals the area of the spanned face.",
                    ),
                )
                for first, second, first_name, second_name in pairs
            )
            areas = tuple(first.cross(second).norm() for first, second, _, _ in pairs)
            return (
                solid_leading
                + face_rules
                + (
                    (
                        _rule(
                            "Opposite faces",
                            rf"S=2\left({'+'.join(sp.latex(area) for area in areas)}\right)"
                            rf"={sp.latex(2 * sum(areas))}",
                            "Opposite faces of a parallelepiped are congruent, so each of "
                            "the three face areas occurs twice.",
                        ),
                    ),
                )
            )
        normal_rule = (_cross_rule(u, v, names[0], names[1]),)
        base_rules = ((_area_rule(a, b, c),),) if params.mode == "tetrahedron-height" else ()
        dot_terms = "+".join(rf"({normal[i]})({w[i]})" for i in range(3))
        triple_rule = (
            _rule(
                "Scalar triple product",
                rf"({names[0]}\times {names[1]})\cdot {names[2]}={dot_terms}={sp.latex(triple)}",
                "Multiply corresponding coordinates and add the products.",
            ),
        )
        volume_rule = (
            _rule(
                "Tetrahedron volume",
                rf"V=\frac{{|{sp.latex(triple)}|}}{{6}}={sp.latex(volume)}",
                "The absolute scalar triple product is the volume of the parallelepiped. "
                "The tetrahedron occupies one sixth of it.",
            ),
        )
        result = solid_leading + (normal_rule,) + base_rules + (triple_rule, volume_rule)
        if params.mode == "tetrahedron-height":
            area = normal.norm() / 2
            height = sp.radsimp(3 * volume / area)
            foot = target - normal * (normal.dot(target - a) / normal.dot(normal))
            result += (
                (
                    _rule(
                        "Height from volume",
                        rf"V=\frac{{1}}{{3}}S_{{ABC}}h,\quad "
                        rf"h=\frac{{3V}}{{S_{{ABC}}}}={sp.latex(height)}",
                        "Rearrange the volume formula using the nonzero base area.",
                    ),
                    _rule(
                        "Foot of the perpendicular",
                        rf"n={_vec(normal)},\quad "
                        rf"H={third}-\frac{{({third}-A)\cdot n}}{{n\cdot n}}n={_vec(foot)}",
                        "The normal is perpendicular to the base plane, and this "
                        "displacement reaches the plane at H.",
                    ),
                ),
            )
        return result
    if version == AreaPractice.version:
        if not isinstance(params, AreaParameters):
            raise ValueError("Invalid area parameters")
        a, b, c = (sp.Matrix(point) for point in params.points)
        area_leading: tuple[tuple[Rule, ...], ...] = ()
        if params.level == 1:
            u, v = a - b, c - b
            names = (r"\vec u", r"\vec v")
        elif params.level == 2:
            u, v = b - a, c - a
            names = (r"\vec{AB}", r"\vec{AC}")
        else:
            midpoint = (b + c) / 2
            u, v = b - a, midpoint - a
            names = (r"\vec{AB}", r"\vec{AM}")
            area_leading = (
                (
                    _rule(
                        "Midpoint",
                        rf"M=\frac{{B+C}}{{2}}={_vec(midpoint)}",
                        "Average the corresponding coordinates of B and C.",
                    ),
                ),
            )
        if params.level > 1:
            area_leading += (
                (
                    _rule(
                        "Vectors from points",
                        rf"{names[0]}={_vec(u)},\quad {names[1]}={_vec(v)}",
                        "Subtract the starting point from the endpoint for each coordinate.",
                    ),
                ),
            )
        normal = u.cross(v)
        norm = normal.norm()
        triangle = params.mode == "triangle-area"
        area = norm / 2 if triangle else norm
        terms = "+".join(rf"({normal[i]})^2" for i in range(3))
        divisor = r"\frac{1}{2}" if triangle else ""
        explanation = "The cross product length is the area of the spanned parallelogram."
        if triangle:
            explanation += " The triangle occupies half of that area."
        return area_leading + (
            (_cross_rule(u, v, names[0], names[1]),),
            (
                _rule(
                    "Area from a cross product",
                    rf"u={names[0]},\ v={names[1]},\quad "
                    rf"|u\times v|=\sqrt{{{terms}}}={sp.latex(norm)},\quad "
                    rf"S={divisor}|u\times v|={sp.latex(area)}",
                    explanation,
                ),
            ),
        )
    if version == VectorExpression.version:
        if not isinstance(params, VectorExpressionParameters):
            raise ValueError("Invalid vector-expression parameters")
        u, v, w = (sp.Matrix(vector) for vector in (params.u, params.v, params.w))

        def subtract(first: Any, second: Any, label: str) -> Rule:
            calculations = ",\\ ".join(rf"({first[i]})-({second[i]})" for i in range(3))
            return _rule(
                "Coordinate subtraction",
                rf"{label}=({calculations})={_vec(first - second)}",
                "Subtract the corresponding coordinates in their original order.",
            )

        if params.level == 1:
            return ((subtract(u, v, "u-v"),),)
        if params.level == 2 and params.seed % 2:
            length = u.norm()
            squares = "+".join(rf"({u[i]})^2" for i in range(3))
            return (
                (
                    _rule(
                        "Vector length",
                        rf"|u|=\sqrt{{{squares}}}={sp.latex(length)}",
                        "Square and add the coordinates, then take the nonnegative square root.",
                    ),
                ),
                (
                    _rule(
                        "Scalar multiplication",
                        rf"|u|v={sp.latex(length)}{_vec(v)}={_vec(length * v)}",
                        "Multiply every coordinate of v by the same scalar.",
                    ),
                ),
                (subtract(length * v, w, r"|u|v-w"),),
            )
        if params.level == 2:
            cross = u.cross(w)
            return (
                (_cross_rule(u, w, r"\vec u", r"\vec w"),),
                (subtract(cross, v, r"u\times w-v"),),
            )
        combined = 2 * u - v
        terms = ",\\ ".join(rf"2({u[i]})-({v[i]})" for i in range(3))
        return (
            (
                _rule(
                    "Linear combination",
                    rf"2u-v=({terms})={_vec(combined)}",
                    "Multiply each coordinate of u by two, then subtract the matching "
                    "coordinate of v.",
                ),
            ),
            (_cross_rule(combined, w, r"(2\vec u-\vec v)", r"\vec w"),),
        )
    if not isinstance(params, PointsParams):
        raise ValueError("Invalid point parameters")
    if version == TriangleAngleDegrees.version:
        if not isinstance(params, AngleParameters):
            raise ValueError("Invalid angle parameters")
        a, b, c = (sp.Matrix(point) for point in params.points)
        leading: tuple[tuple[Rule, ...], ...] = ()
        if params.level == 3:
            midpoint = (b + c) / 2
            u, v = b - a, midpoint - a
            names = (r"\vec{AB}", r"\vec{AM}")
            leading = (
                (
                    _rule(
                        "Midpoint",
                        rf"M=\frac{{B+C}}{{2}}={_vec(midpoint)}",
                        "Average the corresponding coordinates of B and C.",
                    ),
                ),
            )
        else:
            u, v = a - b, c - b
            names = (r"\vec u", r"\vec v") if params.level == 1 else (r"\vec{BA}", r"\vec{BC}")
        if params.level > 1:
            leading += (
                (
                    _rule(
                        "Vectors from points",
                        rf"{names[0]}={_vec(u)},\quad {names[1]}={_vec(v)}",
                        "Subtract the starting point from the endpoint for each coordinate.",
                    ),
                ),
            )
        dot, lu, lv = u.dot(v), u.norm(), v.norm()
        cosine = sp.radsimp(dot / (lu * lv))
        angle = sp.simplify(180 * sp.acos(cosine) / sp.pi)
        dot_terms = "+".join(rf"({u[i]})({v[i]})" for i in range(3))
        square_u = "+".join(rf"({u[i]})^2" for i in range(3))
        square_v = "+".join(rf"({v[i]})^2" for i in range(3))
        return leading + (
            (
                _rule(
                    "Dot product and length",
                    rf"u={names[0]},\ v={names[1]},\quad "
                    rf"u\cdot v={dot_terms}={dot},\quad "
                    rf"|u|=\sqrt{{{square_u}}}={sp.latex(lu)},\quad "
                    rf"|v|=\sqrt{{{square_v}}}={sp.latex(lv)}",
                    "Multiply corresponding coordinates and add. A vector length is the "
                    "square root of the sum of its squared coordinates.",
                ),
            ),
            (
                _rule(
                    "Angle formula",
                    rf"\cos\theta=\frac{{u\cdot v}}{{|u||v|}}={sp.latex(cosine)}",
                    "Both vectors are nonzero, so their lengths may be used as a denominator.",
                ),
            ),
            (
                _rule(
                    "Angle in degrees",
                    rf"\theta=\arccos({sp.latex(cosine)})={sp.latex(angle)}^\circ",
                    "The angle between nonzero vectors is chosen from 0 to 180 degrees.",
                ),
            ),
        )
    if version == TripleProduct.version:
        u, v, w = (sp.Matrix(point) for point in params.points[1:])
        cross = u.cross(v)
        dot = cross.dot(w)
        return (
            (_cross_rule(u, v, r"\vec u", r"\vec v"),),
            (
                _rule(
                    "Dot product",
                    rf"(\vec u\times\vec v)\cdot\vec w={_vec(cross)}\cdot{_vec(w)}={sp.latex(dot)}",
                    "Multiply corresponding coordinates and add the products. "
                    "The scalar triple product is a number.",
                ),
            ),
        )
    a, b, c = (sp.Matrix(point) for point in params.points[:3])
    if version == TriangleAngle.version:
        ba, bc = a - b, c - b
        numerator = ba.dot(bc)
        denominator = ba.norm() * bc.norm()
        return (
            (
                _rule(
                    "Vectors from B",
                    rf"\vec{{BA}}=A-B={_vec(ba)},\quad\vec{{BC}}=C-B={_vec(bc)}",
                    "Subtract B from each endpoint, coordinate by coordinate.",
                ),
            ),
            (
                _rule(
                    "Angle and dot product",
                    rf"\cos\angle B=\frac{{\vec{{BA}}\cdot\vec{{BC}}}}{{|\vec{{BA}}||\vec{{BC}}|}}"
                    rf"=\frac{{{sp.latex(numerator)}}}{{{sp.latex(denominator)}}}"
                    rf"={sp.latex(sp.radsimp(numerator / denominator))}",
                    "Divide the dot product by the product of the two nonzero vector lengths.",
                ),
            ),
        )
    if version == TriangleArea.version:
        return (
            (_edge_rule(a, b, c), _cross_rule(b - a, c - a, r"\vec{AB}", r"\vec{AC}")),
            (_area_rule(a, b, c),),
        )
    d = sp.Matrix(params.points[3])
    if version == TetrahedronVolume.version:
        return ((_edge_rule(a, b, c, d),), (_volume_rule(a, b, c, d),))
    if version == TetrahedronHeight.version:
        normal = (b - a).cross(c - a)
        volume = sp.Rational(abs(normal.dot(d - a)), 6)
        area = normal.norm() / 2
        height = sp.radsimp(3 * volume / area)
        foot = d - normal * (normal.dot(d - a) / normal.dot(normal))
        return (
            (_edge_rule(a, b, c, d), _volume_rule(a, b, c, d)),
            (_area_rule(a, b, c),),
            (
                _rule(
                    "Height from volume",
                    rf"V=\frac{{1}}{{3}}S_{{ABC}}h,\quad h=\frac{{3V}}{{S_{{ABC}}}}"
                    rf"=\frac{{3\cdot {sp.latex(volume)}}}{{{sp.latex(area)}}}={sp.latex(height)}",
                    "Rearrange the tetrahedron volume formula using the nonzero base area.",
                ),
                _rule(
                    "Foot of the perpendicular",
                    rf"n=\vec{{AB}}\times\vec{{AC}}={_vec(normal)},\quad "
                    rf"H=D-\frac{{(D-A)\cdot n}}{{n\cdot n}}n={_vec(foot)}",
                    "The vector n is perpendicular to the base plane. Moving from D along n "
                    "by this amount reaches H in the plane, so DH is perpendicular to the plane.",
                ),
            ),
        )
    return ()
