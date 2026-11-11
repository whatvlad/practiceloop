"""Full natural regions and multivariable limits from AM2A/5.1 and 5.4 (#277)."""

import math
from dataclasses import replace
from typing import Any

import sympy as sp

from app.engine.answers.computational import LimitAnswer
from app.engine.answers.region import RegionLogicAnswer
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import path, plot, point
from app.engine.generators._sequence_limits import finish
from app.math_input.logic import parse_logic

X, Y, Z = sp.symbols("x y z", real=True)
ATOMS = ("p", "q", "r")
SIGN_ROWS = ((True, True, False), (False, True, False), (False, False, True))


def region(
    function: str,
    dimension: int,
    predicates: tuple[str, str, str],
    formula: str,
    rows: tuple[tuple[bool, ...], ...],
    expanded: str,
    proof: str,
    visual: dict[str, Any],
) -> Built:
    answer = RegionLogicAnswer(parse_logic(formula, ATOMS), ATOMS, rows)
    names = "x,y" if dimension == 2 else "x,y,z"
    legend = r",\quad ".join(
        rf"{atom}\equiv({condition})" for atom, condition in zip(ATOMS, predicates, strict=True)
    )
    built = finish(
        rf"\text{{Find the complete natural real domain of }}f({names})={function}.\quad{legend}."
        r"\text{ Give a Boolean formula in p, q and r using !, \&, "
        r"|. The predicates retain their stated mathematical meaning.}",
        answer,
        proof,
        rf"D=\{{({names})\in\mathbb R^{{{dimension}}}\mid {expanded}\}}"
        rf"\quad\Longleftrightarrow\quad {answer.latex()}.",
    )
    return replace(built, visual=visual)


def circles(
    inner: float, outer: float, center: float, *, included: bool, spherical: bool = False
) -> dict[str, Any]:
    paths = []
    for label, radius in (("Inner boundary", inner), ("Outer boundary", outer)):
        paths.append(
            {
                "label": label,
                "closed": True,
                "points": [
                    [
                        center + radius * math.cos(2 * math.pi * k / 48),
                        radius * math.sin(2 * math.pi * k / 48),
                    ]
                    for k in range(49)
                ],
            }
        )
    description = (
        "Meridian section of the spherical shell. Both circular boundaries are included."
        if spherical
        else "The domain is the annulus between the two excluded circles."
    )
    visual = plot(
        "Spherical shell section" if spherical else "Annular natural domain",
        description,
        paths,
        [
            point("Inner boundary point", center + inner, 0, included=included),
            point("Outer boundary point", center + outer, 0, included=included),
            point("Interior point", center + (inner + outer) / 2, 0, included=True),
        ],
    )
    if spherical:
        visual["yLabel"] = "z"
    return visual


def logarithmic_sine_region(a: int, b: int, c: int) -> Built:
    boundary = a * sp.sin(b * X) + c
    condition = rf"y>{tex(boundary)}"
    visual = plot(
        "Domain above a sine boundary",
        "The domain lies strictly above the excluded sine boundary. The plotting window is finite.",
        [path("Excluded boundary", -2, 2, lambda x: a * math.sin(b * x) + c)],
        [
            point("Boundary excluded", 0, c, included=False),
            point("Inside domain", 0, c + 1, included=True),
            point("Outside domain", 0, c - 1, included=False),
        ],
    )
    return region(
        rf"\ln\left(y-({tex(boundary)})\right)",
        2,
        (condition, rf"y\ge{tex(boundary)}", rf"y<{tex(boundary)}"),
        "p",
        SIGN_ROWS,
        condition,
        r"\text{A real logarithm requires a strictly positive "
        r"argument. Equality on the boundary is excluded.}",
        visual,
    )


def quotient_square_root_region(a: int, b: int, c: int) -> Built:
    center = -b
    extent = a + 2
    polygons = [
        {
            "label": "Upper-right region clipped",
            "closed": True,
            "points": [
                [center, c],
                [center + extent, c],
                [center + extent, c + extent],
                [center, c + extent],
            ],
        },
        {
            "label": "Lower-left region clipped",
            "closed": True,
            "points": [
                [center, c],
                [center - extent, c],
                [center - extent, c - extent],
                [center, c - extent],
            ],
        },
    ]
    visual = plot(
        "Square-root quotient domain",
        "Two clipped regions. The horizontal boundary is "
        "included away from the excluded vertical pole.",
        polygons,
        [
            point("Pole excluded", center, c, included=False),
            point("Horizontal boundary right", center + extent / 2, c, included=True),
            point("Horizontal boundary left", center - extent / 2, c, included=True),
        ],
    )
    rows = ((True, False, False), (True, True, True), (True, True, False), (False, True, False))
    return region(
        rf"\sqrt{{\frac{{y-{c}}}{{x+{b}}}}}",
        2,
        (rf"(x+{b})(y-{c})\ge0", rf"x\ne-{b}", rf"(x+{b})(y-{c})>0"),
        "p&q",
        rows,
        rf"x\ne-{b}\ \land\ (x+{b})(y-{c})\ge0",
        r"\text{The denominator must be nonzero. Multiplying the radicand inequality "
        r"by its positive squared denominator gives the product condition.}",
        visual,
    )


def denominator_root_region(a: int, b: int, c: int) -> Built:
    boundary = a * X**2 + b
    visual = plot(
        "Domain below a parabola",
        "The natural domain lies strictly below the excluded parabolic boundary.",
        [path("Excluded parabola", -2, 2, lambda x: a * x * x + b)],
        [
            point("Boundary excluded", 0, b, included=False),
            point("Inside domain", 0, b - 1, included=True),
        ],
    )
    condition = rf"y<{tex(boundary)}"
    return region(
        rf"\frac{{x^2y}}{{\sqrt{{{tex(boundary)}-y}}}}",
        2,
        (condition, rf"y\le{tex(boundary)}", rf"y>{tex(boundary)}"),
        "p",
        SIGN_ROWS,
        condition,
        r"\text{A square root in the denominator requires its radicand "
        r"to be strictly positive, even when the numerator vanishes.}",
        visual,
    )


def logarithmic_annulus_region(a: int, b: int, c: int) -> Built:
    inner = a
    outer = a + b
    radial = (X - c) ** 2 + Y**2
    rows = ((False, True, False), (False, True, True), (True, True, True), (True, False, True))
    return region(
        rf"\ln\frac{{{tex(radial)}-{inner**2}}}{{{outer**2}-({tex(radial)})}}",
        2,
        (
            rf"{tex(radial)}>{inner**2}",
            rf"{tex(radial)}<{outer**2}",
            rf"{tex(radial)}\ge{inner**2}",
        ),
        "p&q",
        rows,
        rf"{inner**2}<{tex(radial)}<{outer**2}",
        r"\text{The numerator and denominator of the logarithm argument must have the "
        r"same nonzero sign. Their ordered radial zeros leave exactly the open annulus.}",
        circles(inner, outer, c, included=False),
    )


def independent_root_region(a: int, b: int, c: int) -> Built:
    visual = plot(
        "Projection of the three-dimensional domain",
        "The domain extends right and down from the "
        "included corner. The y coordinate is unrestricted.",
        [
            {"label": "Included horizontal ray", "points": [[a, b], [a + 4, b]], "arrow": True},
            {"label": "Included vertical ray", "points": [[a, b], [a, b - 4]], "arrow": True},
        ],
        [
            point("Included corner", a, b, included=True),
            point("Inside domain", a + 1, b - 1, included=True),
            point("Outside domain", a - 1, b + 1, included=False),
        ],
    )
    visual["yLabel"] = "z"
    rows = tuple(
        (p, q, r) for p, r in ((False, False), (True, False), (True, True)) for q in (False, True)
    )
    return region(
        rf"\sqrt{{x-{a}}}+{c}\sqrt{{{b}-z}}",
        3,
        (rf"x\ge{a}", rf"z\le{b}", rf"x>{a}"),
        "p&q",
        rows,
        rf"x\ge{a}\ \land\ z\le{b},\quad y\in\mathbb R",
        r"\text{Both square-root radicands are nonnegative. "
        r"There is no restriction on the absent coordinate.}",
        visual,
    )


def arccosine_shell_region(a: int, b: int, c: int) -> Built:
    center = a * a + b + c
    lower = center - 1
    upper = center + 1
    radial = X**2 + Y**2 + Z**2
    rows = ((False, True, False), (True, True, False), (True, True, True), (True, False, True))
    return region(
        rf"\arccos({tex(radial)}-{center})",
        3,
        (rf"{tex(radial)}\ge{lower}", rf"{tex(radial)}\le{upper}", rf"{tex(radial)}>{lower}"),
        "p&q",
        rows,
        rf"{lower}\le{tex(radial)}\le{upper}",
        r"\text{The arccosine argument must lie in the closed interval "
        r"}[-1,1]\text{. Both spherical boundaries are included.}",
        circles(math.sqrt(lower), math.sqrt(upper), 0, included=True, spherical=True),
    )


def multivariable_limit(shown: str, value: sp.Expr | str, method: str, proof: str) -> Built:
    return finish(
        rf"\text{{Evaluate }}\lim_{{(x,y)\to(0,0)}}{shown}"
        rf"\text{{. Enter does\_not\_exist if the limit does not exist.}}",
        LimitAnswer(value),
        method,
        proof,
    )


def quartic_sine_limit(a: int, b: int, c: int) -> Built:
    return multivariable_limit(
        rf"\frac{{\sin({a}x^4-{b}y^4)}}{{{c}(x^2+y^2)}}",
        sp.S.Zero,
        r"|\sin u|\le|u|.\quad r=\sqrt{x^2+y^2}.",
        rf"|f(x,y)|\le\frac{{{a}x^4+{b}y^4}}{{{c}r^2}}"
        rf"\le\frac{{{max(a, b)}}}{{{c}}}r^2\to0\text{{ independently of the approach direction.}}",
    )


def quadratic_cosine_limit(a: int, b: int, c: int) -> Built:
    first = sp.Rational(a * a, 2 * c)
    second = sp.Rational(b * b, 2 * c)
    value = first if a == b else "does_not_exist"
    proof = rf"y=0\Longrightarrow L_x={tex(first)},\quad x=0\Longrightarrow L_y={tex(second)}."
    if a == b:
        proof += rf"\quad u=x^2+y^2\to0:\quad\frac{{1-\cos({a}u)}}{{{c}u^2}}\to{tex(first)}."
    else:
        proof += r"\quad\text{The axis limits differ, so the joint limit does not exist.}"
    built = multivariable_limit(
        rf"\frac{{1-\cos({a}x^2+{b}y^2)}}{{{c}(x^2+y^2)^2}}",
        value,
        r"\text{Check the two coordinate-axis approaches, "
        r"then prove the joint limit if they agree.}",
        proof,
    )
    visual = plot(
        "Coordinate-axis approaches to the limit",
        "Open markers give the two axis limits at the "
        "origin. The plotted paths stop before the origin.",
        [
            path(
                "Along the x axis",
                0.03,
                0.4,
                lambda t: 2 * math.sin(a * t * t / 2) ** 2 / (c * t**4),
            ),
            path(
                "Along the y axis",
                0.03,
                0.4,
                lambda t: 2 * math.sin(b * t * t / 2) ** 2 / (c * t**4),
            ),
        ],
        [
            point("x-axis limit", 0, float(first), included=False),
            point("y-axis limit", 0, float(second), included=False),
        ],
    )
    return replace(built, visual=visual)


def cubic_over_quadratic_limit(a: int, b: int, c: int) -> Built:
    return multivariable_limit(
        rf"\frac{{{a}xy^2}}{{{b}x^2+{c}y^2}}",
        sp.S.Zero,
        r"\text{Use a bound valid on the whole punctured plane.}",
        rf"|f(x,y)|\le\frac{{{a}}}{{{c}}}|x|\le\frac{{{a}}}{{{c}}}\sqrt{{x^2+y^2}}\to0.",
    )


def bounded_oscillation_limit(a: int, b: int, c: int) -> Built:
    return multivariable_limit(
        rf"{a}x^2\cos\!\left(\frac{{{b}}}{{x^4+{c}y^4}}\right)",
        sp.S.Zero,
        r"|\cos u|\le1\text{ controls the rapidly oscillating factor.}",
        rf"|f(x,y)|\le{a}x^2\le{a}(x^2+y^2)\to0."
        r"\quad\text{The denominator inside the cosine vanishes only at the excluded origin.}",
    )
