"""Surface patches, centroids and mass moments from AM2A/12.1–12.3 (#286)."""

import math
from dataclasses import replace
from typing import Any

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.generators._double_integrals import ZERO, X, boundary_paths
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import path, plot, point
from app.engine.generators._multivariable_extrema import formulas
from app.engine.generators._polar_integrals import PI, C, R, polar, polar_boundary
from app.engine.generators._sequence_limits import finish
from app.math_input.contracts import Domain

CENTROID = ("Centroid x", "Centroid y")
INERTIA = ("About the x axis", "About the y axis")
MASS: tuple[tuple[str, Domain], ...] = (("m", "positive"),)
M = sp.Symbol("m", positive=True)


def paraboloid_patch(a: int, b: int, c: int) -> Built:
    k = b + c
    q = 1 + 4 * k * k * R**2
    primitive = q ** sp.Rational(3, 2) / (12 * k * k)
    return polar(
        rf"\text{{Find the area of }}z={k}(x^2+y^2)\text{{ over }}x^2+y^2\le{a * a}.",
        (ZERO, 2 * PI, ZERO, sp.Integer(a)),
        R * sp.sqrt(q),
        primitive,
        2 * PI * (primitive.subs(R, a) - primitive.subs(R, 0)),
        r"dS=\sqrt{1+z_x^2+z_y^2}\,dA.\quad\text{Substitute "
        r"}u=1+4k^2r^2\text{ with the shown coefficient.}",
    )


def tangent_disk_spherical_patch(a: int, b: int, c: int) -> Built:
    radius = a + b + c
    radial = sp.sqrt(radius * radius - R**2)
    return polar(
        rf"\text{{Find the area of the upper sphere }}x^2+y^2+z^2={radius**2}"
        rf"\text{{ over }}x^2+y^2\le{radius}x.",
        (-PI / 2, PI / 2, ZERO, radius * C),
        radius * R / radial,
        -radius * radial,
        radius**2 * (PI - 2),
        r"\text{The upper graph has area factor }R_0/\sqrt{R_0^2-r^2}."
        r"\quad\text{The radial integral is }R_0^2(1-|\sin\theta|)"
        r"\text{. The endpoint on the equator is integrable.}",
    )


def conical_patch(a: int, b: int, c: int) -> Built:
    inner, outer = sp.Rational(a, c), sp.Rational(a + b, c)
    factor = sp.sqrt(1 + c * c)
    return polar(
        rf"\text{{Find the area of }}z={c}\sqrt{{x^2+y^2}}\text{{ for }}{a}\le z\le{a + b}.",
        (ZERO, 2 * PI, inner, outer),
        factor * R,
        factor * R**2 / 2,
        PI * factor * (outer**2 - inner**2),
        r"\text{The graph has constant gradient magnitude equal to the cone slope.}",
    )


def spherical_paraboloid_patch(a: int, b: int, c: int) -> Built:
    radius = sp.sqrt(3) * a
    radial = sp.sqrt(radius**2 - R**2)
    return polar(
        rf"\text{{Find the area of the part of }}x^2+y^2+z^2={3 * a * a}"
        rf"\text{{ with }}z\ge (x^2+y^2)/{2 * a}.",
        (ZERO, 2 * PI, ZERO, sp.sqrt(2) * a),
        radius * R / radial,
        -radius * radial,
        2 * PI * radius * (radius - a),
        rf"\text{{The paraboloid selects the upper cap. The intersection has }}z={a}"
        rf"\text{{ and }}r={tex(sp.sqrt(2) * a)}."
        r"\quad\text{The spherical graph factor is }R_0/\sqrt{R_0^2-r^2}.",
    )


def centroid(
    region: str,
    center: tuple[sp.Expr, sp.Expr],
    area: sp.Expr,
    moment_x: sp.Expr,
    moment_y: sp.Expr,
    derivation: str,
    boundaries: list[dict[str, Any]],
) -> Built:
    x, y = center
    built = finish(
        rf"\text{{Find the centroid }}(\bar x,\bar y)\text{{ of the uniform region }}{region}.",
        formulas(center, CENTROID),
        r"\bar x=M_y/A,\quad \bar y=M_x/A.\quad" + derivation,
        rf"A={tex(area)},\quad M_x={tex(moment_x)},\quad M_y={tex(moment_y)}."
        rf"\quad (\bar x,\bar y)=({tex(x)},{tex(y)}).",
    )
    visual = plot(
        "Uniform region and centroid",
        "The marked centroid uses the first moments of the pictured uniform region.",
        boundaries,
        [point("Centroid", float(x), float(y), included=True)],
    )
    return replace(built, visual=visual)


def parabolic_segment_centroid(a: int, b: int, c: int) -> Built:
    lower = b * (X - c) ** 2 / a**2
    area = sp.Rational(4 * a * b, 3)
    mx = sp.Rational(4 * a * b * b, 5)
    return centroid(
        rf"{tex(lower)}\le y\le{b}",
        (sp.Integer(c), sp.Rational(3 * b, 5)),
        area,
        mx,
        area * c,
        rf"\text{{Use symmetry about }}x={c}\text{{. Integrate the vertical widths for area"
        r" and the differences of squared heights divided by two for }M_x.",
        boundary_paths((sp.Integer(c - a), sp.Integer(c + a), lower, sp.Integer(b)), X),
    )


def sine_square_centroid(a: int, b: int, c: int) -> Built:
    k = b + c
    top = k * sp.sin(a * X) ** 2
    area = k * PI / (2 * a)
    mx = 3 * k * k * PI / (16 * a)
    return centroid(
        rf"0\le x\le\pi/{a},\quad 0\le y\le{tex(top)}",
        (PI / (2 * a), sp.Rational(3 * k, 8)),
        area,
        mx,
        area * PI / (2 * a),
        r"\text{Symmetry gives the horizontal coordinate. The first moment uses }"
        r"\int_0^\pi\sin^4 u\,du=3\pi/8.",
        boundary_paths((ZERO, PI / a, ZERO, top), X),
    )


def exponential_bound_centroid(a: int, b: int, c: int) -> Built:
    top = sp.exp(b)
    left = sp.Integer(c - 1)
    right = left + a
    x = (left + right) / 2
    area = 2 * a * top
    return centroid(
        rf"{left}\le x\le{right},\quad |y|\le e^{{{b}}}",
        (x, ZERO),
        area,
        ZERO,
        area * x,
        r"\text{The exponential bound is constant, so the "
        r"region is a rectangle with two symmetry axes.}",
        boundary_paths((left, right, -top, top), X),
    )


def isosceles_triangle_centroid(a: int, b: int, c: int) -> Built:
    h = b + c
    return centroid(
        rf"\text{{with vertices }}(-{a},0),({a},0),(0,{h})",
        (ZERO, sp.Rational(h, 3)),
        sp.Integer(a * h),
        sp.Rational(a * h * h, 3),
        ZERO,
        rf"\text{{The horizontal slice has width }}{2 * a}(1-y/{h})."
        r"\quad\text{Integrate its width and its width times height.}",
        [{"label": "Triangle", "closed": True, "points": [[-a, 0], [a, 0], [0, h], [-a, 0]]}],
    )


def semicircle_triangle_centroid(a: int, b: int, c: int) -> Built:
    h = sp.sqrt(3) * a
    area = a * a * (sp.sqrt(3) + PI / 2)
    mx = sp.Rational(a**3, 3)
    boundaries = [
        {"label": "Triangle sides", "points": [[-a, 0], [0, float(h)], [a, 0]]},
        path("Semicircle", -a, a, lambda x: -math.sqrt(max(0, a * a - x * x))),
    ]
    return centroid(
        rf"\text{{made from the equilateral triangle above the base }}[-{a},{a}]"
        rf"\text{{ on the }}x\text{{ axis and the semicircle of radius }}{a}\text{{ below it}}",
        (ZERO, mx / area),
        area,
        mx,
        ZERO,
        rf"\text{{Add triangle area }}{tex(a * h)}\text{{ "
        rf"and semicircle area }}{tex(PI * a * a / 2)}."
        rf"\quad\text{{Their centroid heights are "
        rf"}}{tex(h / 3)}\text{{ and }}{tex(-4 * a / (3 * PI))}.",
        boundaries,
    )


def semicircle_cutout_centroid(a: int, b: int, c: int) -> Built:
    area = a * a * (4 - PI / 2)
    mx = sp.Rational(10 * a**3, 3)
    return centroid(
        rf"[-{a},{a}]\times[0,{2 * a}]"
        rf"\text{{ after removing the upper semicircle "
        rf"of radius }}{a}\text{{ centered at the origin}}",
        (ZERO, mx / area),
        area,
        mx,
        ZERO,
        rf"\text{{Subtract the semicircle area }}{tex(PI * a * a / 2)}"
        rf"\text{{ and first moment }}{tex(sp.Rational(2 * a**3, 3))}\text{{ from the square.}}",
        boundary_paths(
            (sp.Integer(-a), sp.Integer(a), sp.sqrt(a * a - X**2), sp.Integer(2 * a)), X
        ),
    )


def inertia(
    region: str,
    axis: str,
    means: tuple[sp.Expr, ...],
    derivation: str,
    boundaries: list[dict[str, Any]],
    axes: list[dict[str, Any]],
) -> Built:
    parts = tuple(FormulaAnswer(M * mean, MASS) for mean in means)
    if len(parts) == 1:
        answer: FormulaAnswer | OrderedAnswer = parts[0]
        request = r"\text{Give the moment of inertia in terms of }m."
    else:
        answer = OrderedAnswer(parts, INERTIA)
        request = r"\text{Give the moments about the }x\text{ and }y\text{ axes in that order.}"
    built = finish(
        rf"\text{{For the uniform region }}{region}\text{{ with mass }}m>0,"
        rf"\quad\text{{use }}{axis}.\quad" + request,
        answer,
        r"\rho=m/A,\quad I=\rho\iint_D d^2\,dA."
        r"\quad\text{Here }d\text{ is the distance to the stated axis or point.}",
        derivation + rf"\quad I={answer.latex()}.",
    )
    visual = plot(
        "Region for the inertia calculation",
        "The boundary and indicated axis or center define the distance used in the moment.",
        boundaries + axes,
        [point("Center", 0, 0, included=True)] if not axes else None,
    )
    return replace(built, visual=visual)


def triangle_base_inertia(a: int, b: int, c: int) -> Built:
    h = sp.sqrt(3) * a
    return inertia(
        rf"\text{{equilateral triangle with base }}[-{a},{a}]"
        r"\text{ on the }x\text{ axis and apex above the base}",
        r"\text{the base as axis}",
        (h * h / 6,),
        rf"h={tex(h)}.\quad I=\frac{{m}}{{{a}h}}\int_0^h y^2\,{2 * a}(1-y/h)\,dy.",
        [
            {
                "label": "Triangle",
                "closed": True,
                "points": [[-a, 0], [a, 0], [0, float(h)], [-a, 0]],
            }
        ],
        [{"label": "Base axis", "points": [[-a, 0], [a, 0]]}],
    )


def parabolic_segment_inertia(a: int, b: int, c: int) -> Built:
    h = b + c
    return inertia(
        rf"-{a}\le x\le{a},\quad 0\le y\le {h}(1-x^2/{a * a})",
        r"\text{the }y\text{ axis}",
        (sp.Rational(a * a, 5),),
        rf"A=\frac43({a})({h}),\quad I=\frac mA\int_{{-{a}}}^{{{a}}}"
        rf"x^2\,{h}(1-x^2/{a * a})\,dx.",
        boundary_paths((sp.Integer(-a), sp.Integer(a), ZERO, h * (1 - X**2 / a**2)), X),
        [{"label": "Symmetry axis", "points": [[0, 0], [0, h]]}],
    )


def square_diagonal_inertia(a: int, b: int, c: int) -> Built:
    side = a + b + c
    return inertia(
        rf"[0,{side}]^2",
        r"\text{the diagonal }y=x",
        (sp.Rational(side * side, 12),),
        rf"d^2=(x-y)^2/2.\quad I=\frac{{m}}{{{side**2}}}\int_0^{{{side}}}"
        rf"\int_0^{{{side}}}\frac{{(x-y)^2}}2\,dy\,dx.",
        [
            {
                "label": "Square",
                "closed": True,
                "points": [[0, 0], [side, 0], [side, side], [0, side], [0, 0]],
            }
        ],
        [{"label": "Diagonal axis", "points": [[0, 0], [side, side]]}],
    )


def quadrant_symmetry_inertia(a: int, b: int, c: int) -> Built:
    radius = a + b
    return inertia(
        rf"x,y\ge0,\quad x^2+y^2\le{radius * radius}",
        r"\text{the symmetry axis }y=x",
        (radius**2 * (PI - 2) / (4 * PI),),
        rf"d^2=r^2(1-\sin2\theta)/2,\quad A={tex(PI * radius**2 / 4)}."
        rf"\quad I=\frac mA\int_0^{{\pi/2}}\int_0^{{{radius}}}"
        r"\frac{r^3(1-\sin2\theta)}2\,dr\,d\theta.",
        polar_boundary((ZERO, PI / 2, ZERO, sp.Integer(radius)))["paths"],
        [
            {
                "label": "Symmetry axis",
                "points": [[0, 0], [radius / math.sqrt(2), radius / math.sqrt(2)]],
            }
        ],
    )


def disk_center_inertia(a: int, b: int, c: int) -> Built:
    radius = a + b + c
    return inertia(
        rf"x^2+y^2\le{radius * radius}",
        r"\text{the origin as the reference point}",
        (sp.Rational(radius * radius, 2),),
        rf"d=r,\quad I=\frac{{m}}{{\pi({radius**2})}}"
        rf"\int_0^{{2\pi}}\int_0^{{{radius}}}r^3\,dr\,d\theta.",
        polar_boundary((ZERO, 2 * PI, ZERO, sp.Integer(radius)))["paths"],
        [],
    )


def ellipse_axes_inertia(a: int, b: int, c: int) -> Built:
    major, minor = a + c, b + c
    outline = [
        [major * math.cos(math.tau * i / 48), minor * math.sin(math.tau * i / 48)]
        for i in range(49)
    ]
    return inertia(
        rf"x^2/{major * major}+y^2/{minor * minor}\le1",
        r"\text{the two coordinate symmetry axes}",
        (sp.Rational(minor * minor, 4), sp.Rational(major * major, 4)),
        rf"x={major}u,\ y={minor}v\text{{ transform the ellipse to the unit disk.}}"
        r"\quad\text{On that disk the means of }u^2,v^2\text{ are each }1/4"
        r"\text{, by radial integration and symmetry.}",
        [{"label": "Ellipse", "closed": True, "points": outline}],
        [
            {"label": "Horizontal axis", "points": [[-major, 0], [major, 0]]},
            {"label": "Vertical axis", "points": [[0, -minor], [0, minor]]},
        ],
    )
