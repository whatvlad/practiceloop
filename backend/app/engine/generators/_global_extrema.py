"""Global extrema, least squares and skew lines from AM2A/9.1, 9.2 and 9.4."""

import math
from dataclasses import replace
from typing import Any

import sympy as sp

from app.engine.answers.computational import FormulaAnswer
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import path, plot, point
from app.engine.generators._multivariable_extrema import EXTREMA, MAXIMUM, MINIMUM, formulas
from app.engine.generators._sequence_limits import finish

U, V = sp.symbols("u v", real=True)
TWO_MINIMA = (*MINIMUM, "Other minimum x", "Other minimum y", *MAXIMUM)
TWO_MAXIMA = (*MINIMUM, *MAXIMUM, "Other maximum x", "Other maximum y")
Coordinate = tuple[sp.Expr, sp.Expr]


def global_extrema(
    a: int,
    b: int,
    c: int,
    function: sp.Expr,
    domain: str,
    minima: tuple[Coordinate, ...],
    maxima: tuple[Coordinate, ...],
    derivation: str,
    boundaries: list[dict[str, Any]],
    *,
    representative: str = "",
) -> Built:
    min_value = c * function.subs(dict(zip((U, V), minima[0], strict=True)))
    max_value = c * function.subs(dict(zip((U, V), maxima[0], strict=True)))
    min_points = tuple((a * u, b * v) for u, v in minima)
    max_points = tuple((a * u, b * v) for u, v in maxima)
    if len(minima) == 2 and not representative:
        values: tuple[sp.Expr, ...] = (
            *min_points[0],
            min_value,
            *min_points[1],
            *max_points[0],
            max_value,
        )
        labels: tuple[str, ...] = TWO_MINIMA
        request = (
            r"\text{Give the minimum point with smaller }x\text{ and its value,"
            r" then the other minimum point, then the maximum point and its value.}"
        )
    elif len(maxima) == 2 and not representative:
        values = (*min_points[0], min_value, *max_points[0], max_value, *max_points[1])
        labels = TWO_MAXIMA
        request = (
            r"\text{Give the minimum point and value, then the maximum point with smaller }x"
            r"\text{ and its value, then the other maximum point.}"
        )
    else:
        values = (*min_points[0], min_value, *max_points[0], max_value)
        labels = EXTREMA
        request = (
            r"\text{Give the minimum point and value, then the maximum point and value.}"
            + representative
        )
    answer = formulas(values, labels)

    def locations(coordinates: tuple[Coordinate, ...]) -> str:
        return r",\ ".join(rf"({tex(x)},{tex(y)})" for x, y in coordinates)

    built = finish(
        rf"\text{{Find the global extrema of }}f(x,y)={tex(c * function)},"
        rf"\quad u=x/{a},\ v=y/{b},\quad {domain}.\quad " + request,
        answer,
        derivation,
        rf"\min f={tex(min_value)}\text{{ at }}{locations(min_points)};"
        rf"\qquad\max f={tex(max_value)}\text{{ at }}{locations(max_points)}.",
    )
    markers = [
        point(label, float(x), float(y), included=True)
        for label, locations_ in (("Minimum", min_points), ("Maximum", max_points))
        for x, y in locations_
    ]
    return replace(
        built,
        visual=plot(
            "Feasible region and extremal points",
            "The paths mark the feasible boundary. The "
            "markers identify every point attaining an extreme.",
            boundaries,
            markers,
        ),
    )


def parabolic_cap_extrema(a: int, b: int, c: int) -> Built:
    return global_extrema(
        a,
        b,
        c,
        2 * U**3 + 4 * U**2 + V**2 - 2 * U * V,
        r"u^2\le v\le4",
        ((sp.S.Zero, sp.S.Zero),),
        ((sp.Integer(-2), sp.Integer(4)), (sp.Integer(2), sp.Integer(4))),
        r"\text{At an interior critical point }v=u\text{ "
        r"and }u(u+1)=0\text{, giving no interior point.}"
        r"\quad v=u^2\Longrightarrow f/c=u^4+4u^2."
        r"\quad v=4\Longrightarrow (f/c)'=2(3u-2)(u+2)."
        r"\quad\text{Check the endpoints and }u=2/3\text{ on the top edge.}",
        [
            path("Parabolic edge", -2 * a, 2 * a, lambda x: b * (x / a) ** 2),
            path("Top edge", -2 * a, 2 * a, lambda x: 4 * b),
        ],
    )


def radical_lens_extrema(a: int, b: int, c: int) -> Built:
    return global_extrema(
        a,
        b,
        c,
        sp.sqrt(V - U**2) + sp.sqrt(U - V**2),
        r"u^2\le v,\ v^2\le u",
        ((sp.S.Zero, sp.S.Zero), (sp.S.One, sp.S.One)),
        ((sp.S.Half, sp.S.Half),),
        r"0\le u,v\le1.\quad (f/c)^2\le2[(u-u^2)+(v-v^2)]\le1."
        r"\quad\text{Both inequalities are equalities only at }u=v=1/2."
        r"\quad f=0\Longleftrightarrow v=u^2,\ u=v^2\Longleftrightarrow u=v\in\{0,1\}.",
        [
            path("Lower parabola", 0, a, lambda x: b * (x / a) ** 2),
            path("Upper parabola", 0, a, lambda x: b * math.sqrt(x / a)),
        ],
    )


def radical_strip_extrema(a: int, b: int, c: int) -> Built:
    root = sp.sqrt(3)
    boundaries = [
        path("Upper arc", -a, a, lambda x: b * math.sqrt(4 - (x / a) ** 2)),
        path("Lower arc", -a, a, lambda x: -b * math.sqrt(4 - (x / a) ** 2)),
    ]
    for x, label in ((-a, "Left edge"), (a, "Right edge")):
        boundaries.append(
            {"label": label, "points": [[x, -b * math.sqrt(3)], [x, b * math.sqrt(3)]]}
        )
    return global_extrema(
        a,
        b,
        c,
        sp.sqrt(1 - U**2) + sp.sqrt(4 - U**2 - V**2),
        r"|u|\le1,\ u^2+v^2\le4",
        ((sp.S.One, root), (sp.S.One, -root), (-sp.S.One, root), (-sp.S.One, -root)),
        ((sp.S.Zero, sp.S.Zero),),
        r"\text{Both square roots are nonnegative and "
        r"vanish exactly at the four edge intersections.}"
        r"\quad\text{Their upper bounds are }1,2\text{ and both are attained only at the origin.}",
        boundaries,
        representative=r"\quad\text{For the minimum use the point with }x,y>0.",
    )


def triangular_region_extrema(a: int, b: int, c: int) -> Built:
    return global_extrema(
        a,
        b,
        c,
        U**2 - V**2,
        r"0\le u\le1,\ 1+u\le v\le2",
        ((sp.S.Zero, sp.Integer(2)),),
        ((sp.S.Zero, sp.S.One),),
        r"-4\le u^2-v^2\le u^2-(1+u)^2=-1-2u\le-1."
        r"\quad\text{The equality conditions specify the two vertices.}",
        [{"label": "Triangle", "closed": True, "points": [[0, b], [0, 2 * b], [a, 2 * b], [0, b]]}],
    )


def quartic_disk_extrema(a: int, b: int, c: int) -> Built:
    circle = {
        "label": "Elliptical boundary",
        "closed": True,
        "points": [
            [a * math.cos(i * math.tau / 48), b * math.sin(i * math.tau / 48)] for i in range(49)
        ],
    }
    return global_extrema(
        a,
        b,
        c,
        U**4 + V**4,
        r"u^2+v^2\le1",
        ((sp.S.Zero, sp.S.Zero),),
        (
            (sp.S.One, sp.S.Zero),
            (-sp.S.One, sp.S.Zero),
            (sp.S.Zero, sp.S.One),
            (sp.S.Zero, -sp.S.One),
        ),
        r"0\le u^4+v^4=(u^2+v^2)^2-2u^2v^2\le1."
        r"\quad\text{The upper bound requires }uv=0,\ u^2+v^2=1.",
        [circle],
        representative=r"\quad\text{For the maximum use the point on the positive }x\text{ axis.}",
    )


def quadrant_decay_extrema(a: int, b: int, c: int) -> Built:
    return global_extrema(
        a,
        b,
        c,
        (U + V) * sp.exp(-U - 2 * V),
        r"u,v\ge0",
        ((sp.S.Zero, sp.S.Zero),),
        ((sp.S.One, sp.S.Zero),),
        r"s=u+v\ge0.\quad f/c=s e^{-s}e^{-v}\le s e^{-s}\le e^{-1}."
        r"\quad\text{Equality at the upper bound requires }v=0,s=1."
        r"\quad\text{The value is zero exactly at }s=0.",
        [
            {"label": "Positive x axis", "points": [[0, 0], [3 * a, 0]], "arrow": True},
            {"label": "Positive y axis", "points": [[0, 0], [0, 3 * b]], "arrow": True},
        ],
    )


def triangle_least_squares(a: int, b: int, c: int) -> Built:
    vertices = ((-a, b + c), (a, b), (2 * a, -c))
    x, y = (sp.Rational(sum(vertex[i] for vertex in vertices), 3) for i in range(2))
    value = sum((x - u) ** 2 + (y - v) ** 2 for u, v in vertices)
    vertex_text = r",\ ".join(rf"({u},{v})" for u, v in vertices)
    built = finish(
        rf"\text{{For the triangle with vertices }}{vertex_text},"
        r"\text{ find the point minimizing the sum of squared distances to the vertices.}"
        r"\quad\text{Give }(x,y,\text{minimum sum}).",
        formulas((x, y, value), MINIMUM),
        r"\text{Write each squared distance relative to the centroid }G."
        r"\quad \sum_i\|P-A_i\|^2=3\|P-G\|^2+\sum_i\|G-A_i\|^2."
        r"\quad\text{The cross terms cancel and }G\text{ belongs to the triangle.}",
        rf"G=({tex(x)},{tex(y)}),\quad \min\sum_i\|P-A_i\|^2={tex(value)}.",
    )
    visual = plot(
        "Triangle and least-squares point",
        "The centroid minimizes the sum of the squared distances to the vertices.",
        [
            {
                "label": "Triangle",
                "closed": True,
                "points": [list(p) for p in (*vertices, vertices[0])],
            }
        ],
        [point("Centroid", float(x), float(y), included=True)],
    )
    return replace(built, visual=visual)


def skew_line_distance(a: int, b: int, c: int) -> Built:
    y = sp.Rational(b - a, 1 + a * c)
    x = 1 + c * y
    distance = sp.Integer(a + b)
    built = finish(
        rf"\text{{Find the exact distance between }}L_1:"
        rf"\begin{{cases}}{a}x+y={b}\\z=-{a}\end{{cases}}"
        rf"\quad\text{{and }}L_2:\begin{{cases}}x-{c}y=1\\z={b}\end{{cases}}.",
        FormulaAnswer(distance),
        r"\text{Any connector has vertical component }a+b\text{ in magnitude for the shown levels.}"
        rf"\quad\text{{The two horizontal projections intersect at }}({tex(x)},{tex(y)}).",
        rf"\text{{The vertical connector at that intersection "
        rf"attains the lower bound }}d={distance}.",
    )
    x0, y0 = float(x), float(y)

    def project(x: float, y: float, z: float) -> list[float]:
        return [x - 0.4 * y, z + 0.3 * y]

    first = [project(x0 + t, y0 - a * t, -a) for t in (-1, 1)]
    second = [project(x0 + c * t, y0 + t, b) for t in (-1, 1)]
    lower, upper = project(x0, y0, -a), project(x0, y0, b)
    visual = plot(
        "Skew lines and shortest connector",
        "Oblique projection. The vertical connector joins the two marked feet.",
        [
            {"label": "First line", "points": first},
            {"label": "Second line", "points": second},
            {"label": "Shortest connector", "points": [lower, upper]},
        ],
        [point("First foot", *lower, included=True), point("Second foot", *upper, included=True)],
    )
    visual.update(xLabel="projected x", yLabel="projected z")
    return replace(built, visual=visual)
