"""Applied optimization from AM2A/9.3 and 9.5–9.7 (#283)."""

from dataclasses import replace

import sympy as sp

from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import path, plot, point
from app.engine.generators._multivariable_extrema import X, Y, formulas, local_sections
from app.engine.generators._sequence_limits import finish

DIMENSIONS = ("Length", "Width", "Height", "Minimum objective")
PROFIT = ("Internal doors", "External doors", "Maximum profit")
CLOSEST = ("Closest x", "Closest y", "Distance")


def container(
    side: int,
    height: int,
    walls: int,
    floor: int,
    ceiling: int,
    *,
    open_top: bool,
) -> Built:
    volume = side * side * height
    horizontal = floor + ceiling
    objective = horizontal * side**2 + 4 * walls * side * height
    if open_top:
        prompt = (
            rf"\text{{An open rectangular tank must hold }}{volume}\text{{ cubic meters.}}"
            r"\quad\text{Give its length, width, height and minimum sheet area in square meters.}"
        )
    else:
        prompt = (
            rf"\text{{A rectangular warehouse must hold }}{volume}\text{{ cubic meters.}}"
            rf"\quad\text{{Costs per square meter are }}{walls}\text{{ for walls, }}"
            rf"{floor}\text{{ for the floor and }}{ceiling}\text{{ for the ceiling.}}"
            r"\quad\text{Give length, width, height in meters and minimum total cost.}"
        )
    built = finish(
        prompt,
        formulas(tuple(map(sp.Integer, (side, side, height, objective))), DIMENSIONS),
        rf"C={horizontal}xy+2({walls})h(x+y),\quad xyh={volume}."
        r"\quad\text{For fixed base area }s^2=xy,\ x+y\ge2s"
        r"\text{ with equality only for }x=y=s.",
        rf"C(s)={horizontal}s^2+\frac{{{4 * walls * volume}}}s,\quad"
        rf"C'(s)=2({horizontal})s-\frac{{{4 * walls * volume}}}{{s^2}}."
        rf"\quad C'\text{{ changes from negative to positive at }}s={side},\quad"
        rf"h={volume}/s^2={height},\quad C_{{\min}}={objective}.",
    )
    visual = plot(
        "Objective for a square base",
        "After minimizing over base shape, the marked side "
        "length minimizes the objective at fixed volume.",
        [
            path(
                "Objective at fixed volume",
                side / 2,
                2 * side,
                lambda s: horizontal * s * s + 4 * walls * volume / s,
            )
        ],
        [point("Minimum", side, objective, included=True)],
    )
    visual.update(xLabel="base side in meters", yLabel="area" if open_top else "cost")
    return replace(built, visual=visual)


def open_tank(a: int, b: int, c: int) -> Built:
    height = a + b + c
    return container(2 * height, height, 1, 1, 0, open_top=True)


def weighted_warehouse(a: int, b: int, c: int) -> Built:
    walls = a + b
    return container(
        walls * (b + 1), (walls + c) * (b + 1), walls, walls + 2 * c, walls, open_top=False
    )


def discrete_profit(a: int, b: int, c: int) -> Built:
    u = a + b + c + 2
    v = u + c
    factor = 10
    p, q = factor * (2 * u - v), factor * (2 * v - u)
    cost = factor * (X**2 - X * Y + Y**2)
    profit = p * X + q * Y - cost
    maximum = profit.subs({X: u, Y: v})
    built = finish(
        rf"\text{{Internal doors sell for }}{p}\text{{ "
        rf"each and external doors for }}{q}\text{{ each.}}"
        rf"\quad\text{{The cost of }}x\text{{ internal "
        rf"and }}y\text{{ external doors is }}{tex(cost)}."
        r"\quad\text{Give the nonnegative integer production counts and maximum profit.}",
        formulas((sp.Integer(u), sp.Integer(v), maximum), PROFIT),
        rf"P={tex(profit)}.\quad P_x=0,\ P_y=0\Longrightarrow (x,y)=({u},{v}).",
        rf"P(x,y)=P({u},{v})-{factor}\big[(x-{u})^2-(x-{u})(y-{v})+(y-{v})^2\big]."
        r"\quad\text{The bracket is positive away from the "
        r"stated integer point, so the maximizer is unique.}"
        rf"\quad P_{{\max}}={maximum}.",
    )
    return replace(
        built, visual=local_sections(profit, [("maximum", (sp.Integer(u), sp.Integer(v)))], 2)
    )


def closest_parabola(a: int, b: int, c: int) -> Built:
    x = sp.Integer(1 + (a - 1) % 3)
    factor = 1 + (c - 1) % 2
    curve = sp.Rational(factor, 2) * X**2
    y = curve.subs(X, x)
    u = sp.Rational(factor**2, 2) * x**3 + b * x
    v = sp.Rational(1 - b, factor)
    distance = sp.sqrt((x - u) ** 2 + (y - v) ** 2)
    built = finish(
        rf"\text{{Find the point on }}y={tex(curve)}\text{{ closest to }}P=({tex(u)},{tex(v)})."
        r"\quad\text{Give its coordinates and the exact distance.}",
        formulas((x, y, distance), CLOSEST),
        rf"D^2=(x-({tex(u)}))^2+({tex(curve)}-({tex(v)}))^2."
        rf"\quad (D^2)'={factor**2}x^3+{2 * b}x-{tex(2 * u)}.",
        rf"\text{{The derivative is strictly increasing and vanishes at }}x={x}."
        rf"\quad\text{{The unique closest point is }}({tex(x)},{tex(y)}),\quad D={tex(distance)}.",
    )
    x0, y0, u0, v0 = map(float, (x, y, u, v))
    visual = plot(
        "Closest point on the parabola",
        "The marked connector is perpendicular to the parabola tangent at the closest point.",
        [
            path("Parabola", x0 - 3, x0 + 3, lambda t: factor * t * t / 2),
            {"label": "Shortest connector", "points": [[u0, v0], [x0, y0]]},
        ],
        [
            point("Given point", u0, v0, included=True),
            point("Closest point", x0, y0, included=True),
        ],
    )
    return replace(built, visual=visual)
