"""Polar double integrals, areas and volumes from AM2A/11.1–11.3 (#285)."""

import math
from dataclasses import replace
from typing import Any

import sympy as sp

from app.engine.answers.computational import FormulaAnswer
from app.engine.generators._double_integrals import ONE, ZERO, X, Y, integral
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import plot
from app.engine.generators._sequence_limits import finish

R, THETA = sp.symbols("r theta", real=True)
C, S = sp.cos(THETA), sp.sin(THETA)
PI = sp.pi
PolarBounds = tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr]
Origin = tuple[sp.Expr, sp.Expr]
ORIGIN = (ZERO, ZERO)


def polar_boundary(bounds: PolarBounds, center: Origin = ORIGIN) -> dict[str, Any]:
    start, end, inner, outer = bounds
    cx, cy = map(float, center)
    t0, t1 = map(float, (start, end))
    angles = [t0 + (t1 - t0) * i / 40 for i in range(41)]
    arcs = []
    for radius in (inner, outer):
        r = sp.lambdify(THETA, radius, "math")
        arcs.append([[cx + r(t) * math.cos(t), cy + r(t) * math.sin(t)] for t in angles])
    if end - start == 2 * PI:
        paths = [{"label": "Outer boundary", "closed": True, "points": arcs[1]}]
        if inner != 0:
            paths.append({"label": "Inner boundary", "closed": True, "points": arcs[0]})
    else:
        paths = [
            {
                "label": "Polar region boundary",
                "closed": True,
                "points": [*arcs[0], *reversed(arcs[1]), arcs[0][0]],
            }
        ]
    return plot(
        "Projection of the integration region",
        "The boundary uses the stated polar limits and center.",
        paths,
    )


def polar(
    statement: str,
    bounds: PolarBounds,
    converted: sp.Expr,
    radial_primitive: sp.Expr,
    value: sp.Expr,
    detail: str,
    *,
    center: Origin = ORIGIN,
) -> Built:
    start, end, lower, upper = bounds
    substituted = radial_primitive.subs(R, upper) - radial_primitive.subs(R, lower)
    value = sp.factor_terms(value)
    cx, cy = center
    built = finish(
        statement,
        FormulaAnswer(value),
        rf"x={tex(cx + R * C)},\ y={tex(cy + R * S)},\ dA=r\,dr\,d\theta."
        rf"\quad\int_{{{tex(start)}}}^{{{tex(end)}}}\int_{{{tex(lower)}}}^{{{tex(upper)}}}"
        rf"{tex(converted)}\,dr\,d\theta.",
        rf"\text{{A radial primitive is }}{tex(radial_primitive)}."
        rf"\quad\int_{{{tex(start)}}}^{{{tex(end)}}}\left({tex(substituted)}\right)\,d\theta"
        rf"={tex(value)}.\quad" + detail,
    )
    return replace(built, visual=polar_boundary(bounds, center))


def polar_prompt(function: sp.Expr, region: str) -> str:
    return (
        rf"\text{{Use polar coordinates to evaluate }}\iint_D {tex(function)}\,dA,"
        rf"\quad D:\ {region}."
    )


def sector_xy(a: int, b: int, c: int) -> Built:
    radius = sp.Integer(b + c)
    coefficient = sp.Integer(a)
    return polar(
        polar_prompt(
            coefficient * X * Y, rf"x^2+y^2\le{radius**2},\quad x/\sqrt3\le y\le\sqrt3\,x"
        ),
        (PI / 6, PI / 3, ZERO, radius),
        coefficient * R**3 * C * S,
        coefficient * R**4 * C * S / 4,
        coefficient * radius**4 / 16,
        r"\text{Use }\sin^2\theta/2\text{ as an angular primitive of }\sin\theta\cos\theta.",
    )


def half_annulus_xy_squared(a: int, b: int, c: int) -> Built:
    lower, upper = sp.Integer(b), sp.Integer(b + c)
    return polar(
        polar_prompt(a * X * Y**2, rf"{b * b}\le x^2+y^2\le{upper**2},\quad x\ge0"),
        (-PI / 2, PI / 2, lower, upper),
        a * R**4 * C * S**2,
        a * R**5 * C * S**2 / 5,
        2 * a * (upper**5 - lower**5) / 15,
        r"\text{The angular primitive of }\cos\theta\sin^2\theta\text{ is }\sin^3\theta/3.",
    )


def quadrant_radial_exponential(a: int, b: int, c: int) -> Built:
    primitive = sp.exp(a * R**2) * (a * R**2 - 1) / (2 * a * a)
    upper = sp.sqrt(b)
    return polar(
        polar_prompt(c * Y**2 * sp.exp(a * (X**2 + Y**2)), rf"x,y\ge0,\quad x^2+y^2\le{b}"),
        (ZERO, PI / 2, ZERO, upper),
        c * R**3 * S**2 * sp.exp(a * R**2),
        c * S**2 * primitive,
        c * PI * (primitive.subs(R, upper) - primitive.subs(R, 0)) / 4,
        r"\text{Substitute }u=r^2\text{ radially. The "
        r"angular integral of }\sin^2\theta\text{ is }\pi/4.",
    )


def shifted_disk_x_squared(a: int, b: int, c: int) -> Built:
    radius = 2 * b * S
    return polar(
        polar_prompt(a * c * X**2, rf"x^2+y^2\le{2 * b}y"),
        (ZERO, PI, ZERO, radius),
        a * c * R**3 * C**2,
        a * c * R**4 * C**2 / 4,
        a * c * (2 * b) ** 4 * PI / 64,
        r"\int_0^\pi\sin^4\theta\cos^2\theta\,d\theta"
        r"=\int_0^\pi(\sin^4\theta-\sin^6\theta)\,d\theta=\pi/16.",
    )


def radial_between_disks(a: int, b: int, c: int) -> Built:
    return polar(
        polar_prompt(a * c * (X**2 + Y**2), rf"y\ge0,\quad {b}y\le x^2+y^2\le{b}x"),
        (ZERO, PI / 4, b * S, b * C),
        a * c * R**3,
        a * c * R**4 / 4,
        sp.Rational(a * c * b**4, 8),
        r"\cos^4\theta-\sin^4\theta=\cos(2\theta).",
    )


def lower_shifted_disk_y(a: int, b: int, c: int) -> Built:
    return polar(
        polar_prompt(a * c * Y, rf"x^2+y^2\le{2 * b}x,\quad y\le0"),
        (-PI / 2, ZERO, ZERO, 2 * b * C),
        a * c * R**2 * S,
        a * c * R**3 * S / 3,
        -sp.Rational(a * c * (2 * b) ** 3, 12),
        r"\text{Use }u=\cos\theta\text{ after the radial integration.}",
    )


def radial_sine_disk(a: int, b: int, c: int) -> Built:
    radius = PI * sp.sqrt(b)
    return polar(
        polar_prompt(c * sp.sin(a * (X**2 + Y**2)), rf"x^2+y^2\le{tex(b * PI**2)}"),
        (ZERO, 2 * PI, ZERO, radius),
        c * R * sp.sin(a * R**2),
        -c * sp.cos(a * R**2) / (2 * a),
        c * PI * (1 - sp.cos(a * b * PI**2)) / a,
        r"\text{The radial substitution is }u=ar^2\text{ and the angle spans a full turn.}",
    )


def radial_log_annulus(a: int, b: int, c: int) -> Built:
    lower, upper = sp.Integer(b), sp.Integer(b + c)
    u = 1 + a * R**2
    primitive = u * (sp.log(u) - 1) / (2 * a)
    return polar(
        polar_prompt(sp.log(1 + a * (X**2 + Y**2)), rf"{b * b}\le x^2+y^2\le{upper**2}"),
        (ZERO, 2 * PI, lower, upper),
        R * sp.log(u),
        primitive,
        2 * PI * (primitive.subs(R, upper) - primitive.subs(R, lower)),
        r"\text{After }u=1+ar^2\text{ use the primitive }u\ln u-u.",
    )


def parabola_triangle_area(a: int, b: int, c: int) -> Built:
    return integral(
        ONE,
        (ZERO, sp.Integer(2 * a), Y**2 / (4 * a), 3 * a - Y),
        X,
        outer=Y,
        boundary_text=rf"y^2={4 * a}x,\quad x+y={3 * a},\quad y=0,\quad y\ge0",
        method=(
            r"\text{Integrate the constant one to obtain the area.}"
            rf"\quad\text{{The positive intersection has }}y={2 * a}."
        ),
    )


def nested_tangent_circles_area(a: int, b: int, c: int) -> Built:
    inner, outer = sp.Integer(b), sp.Integer(b + c)
    return polar(
        rf"\text{{Find the area inside }}x^2+y^2={2 * outer}y"
        rf"\text{{ and outside }}x^2+y^2={2 * inner}y.",
        (ZERO, PI, 2 * inner * S, 2 * outer * S),
        R,
        R**2 / 2,
        PI * (outer**2 - inner**2),
        r"\text{The angular integral of }\sin^2\theta\text{ over }[0,\pi]\text{ is }\pi/2.",
    )


def affine_parallelogram_area(a: int, b: int, c: int) -> Built:
    value = sp.Rational(b * c, 4)
    corners = ((a, 0), (a + b, 0), (a + b, c), (a, c), (a, 0))
    xy = [[(3 * u + v) / 4, (u - v) / 4] for u, v in corners]
    built = finish(
        rf"\text{{Find the area of }}{a}\le x+y\le{a + b},\quad 0\le x-3y\le{c}.",
        FormulaAnswer(value),
        r"u=x+y,\ v=x-3y\quad\Longrightarrow\quad x=(3u+v)/4,\ y=(u-v)/4."
        r"\quad\text{The absolute inverse Jacobian determinant is }1/4.",
        rf"A=\int_{{{a}}}^{{{a + b}}}\int_0^{{{c}}}\frac14\,dv\,du={tex(value)}.",
    )
    visual = plot(
        "Parallelogram of integration",
        "The four corners come from the inverse affine coordinate map.",
        [{"label": "Parallelogram", "points": xy, "closed": True}],
    )
    return replace(built, visual=visual)


def disk_wedge_area(a: int, b: int, c: int) -> Built:
    scale = b + c
    return polar(
        rf"\text{{Find the area inside }}x^2+y^2={2 * scale}y"
        r"\text{ and above }y=\sqrt3|x|.",
        (PI / 3, 2 * PI / 3, ZERO, 2 * scale * S),
        R,
        R**2 / 2,
        scale**2 * (PI / 3 + sp.sqrt(3) / 2),
        r"\text{Use }\theta/2-\sin(2\theta)/4\text{ as a primitive of }\sin^2\theta.",
    )


def sphere_paraboloid_volume(a: int, b: int, c: int) -> Built:
    radius = 4 * a
    top = sp.sqrt(25 * a * a - R**2)
    bottom = R**2 / a - 13 * a
    primitive = -((25 * a * a - R**2) ** sp.Rational(3, 2)) / 3 - R**4 / (4 * a) + 13 * a * R**2 / 2
    return polar(
        rf"\text{{Find the volume below }}z=\sqrt{{{25 * a * a}-x^2-y^2}}"
        rf"\text{{ and above }}z=(x^2+y^2)/{a}-{13 * a}.",
        (ZERO, 2 * PI, ZERO, sp.Integer(radius)),
        R * (top - bottom),
        primitive,
        2 * PI * (primitive.subs(R, radius) - primitive.subs(R, 0)),
        rf"\text{{The surfaces meet at }}r={radius},\ z={3 * a}."
        r"\quad\text{The upper height decreases and the lower one increases.}",
    )


def spherical_cap_volume(a: int, b: int, c: int) -> Built:
    radius = a + b + c
    top = sp.sqrt(radius**2 - R**2)
    cutoff = sp.sqrt(radius**2 - a * a)
    primitive = -((radius**2 - R**2) ** sp.Rational(3, 2)) / 3 - a * R**2 / 2
    return polar(
        rf"\text{{Find the volume of the cap }}x^2+y^2+z^2\le{radius**2},\quad z\ge{a}.",
        (ZERO, 2 * PI, ZERO, cutoff),
        R * (top - a),
        primitive,
        2 * PI * (primitive.subs(R, cutoff) - primitive.subs(R, 0)),
        r"\text{The projected circle is where the sphere reaches the cutting plane.}",
    )


def shifted_disk_paraboloid_volume(a: int, b: int, c: int) -> Built:
    radius = 2 * b * S
    return polar(
        rf"\text{{Find the volume inside }}x^2+y^2\le{2 * b}y"
        rf"\text{{ between }}z=0\text{{ and }}z={a * c}(x^2+y^2).",
        (ZERO, PI, ZERO, radius),
        a * c * R**3,
        a * c * R**4 / 4,
        a * c * (2 * b) ** 4 * 3 * PI / 32,
        r"\text{After integrating }r^3\text{, use }\int_0^\pi\sin^4\theta\,d\theta=3\pi/8.",
    )


def paraboloid_slab_volume(a: int, b: int, c: int) -> Built:
    cap = a + b + c
    upper = a + b
    value = PI * sp.Rational(b * (b + 2 * c), 2)
    built = finish(
        rf"\text{{Find the volume below }}z={cap}-x^2-y^2"
        rf"\text{{ between }}z={a}\text{{ and }}z={upper}.",
        FormulaAnswer(value),
        rf"\text{{At height }}z\text{{ the circular section has radius }}\sqrt{{{cap}-z}}."
        r"\quad\text{Its area follows by integrating }r\,dr\,d\theta.",
        rf"V=\pi\int_{{{a}}}^{{{upper}}}({cap}-z)\,dz={tex(value)}.",
    )
    visual = polar_boundary((ZERO, 2 * PI, sp.sqrt(c), sp.sqrt(b + c)))
    visual["description"] = (
        "The circles are the horizontal sections at the upper and lower heights."
    )
    visual["paths"][0]["label"] = "Lower section"
    visual["paths"][1]["label"] = "Upper section"
    return replace(built, visual=visual)


def disk_product_volume(a: int, b: int, c: int) -> Built:
    x0, y0 = sp.Integer(a + b), sp.Integer(a + c)
    height = (x0 + R * C) * (y0 + R * S)
    primitive = x0 * y0 * R**2 / 2 + (x0 * S + y0 * C) * R**3 / 3 + C * S * R**4 / 4
    return polar(
        rf"\text{{Find the volume over }}(x-{x0})^2+(y-{y0})^2\le{a * a}"
        r"\text{ between }z=0\text{ and }z=xy.",
        (ZERO, 2 * PI, ZERO, sp.Integer(a)),
        R * height,
        primitive,
        PI * a * a * x0 * y0,
        r"\text{Only the constant angular term survives a full turn.}",
        center=(x0, y0),
    )


def plane_paraboloid_volume(a: int, b: int, c: int) -> Built:
    height = c + sp.Rational(a * b * b, 2)
    radius = sp.sqrt(2 * a * height)
    return polar(
        rf"\text{{Find the volume between }}z=(x^2+y^2)/{2 * a}\text{{ and }}z={c}-{b}y.",
        (ZERO, 2 * PI, ZERO, radius),
        R * (height - R**2 / (2 * a)),
        height * R**2 / 2 - R**4 / (8 * a),
        PI * a * height**2,
        r"\text{Complete the square in the height difference to obtain a translated radial disk.}",
        center=(ZERO, sp.Integer(-a * b)),
    )
