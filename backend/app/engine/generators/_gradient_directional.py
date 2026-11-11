"""Gradients and directional derivatives from AM2A/7.3–7.6 (#280)."""

import math
from dataclasses import replace
from typing import Any

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, LimitAnswer, OrderedAnswer
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import path, plot, point
from app.engine.generators._sequence_limits import finish

X, Y, Z = sp.symbols("x y z", real=True)
QUOTIENTS = ("Left quotient limit", "Right quotient limit", "Two-sided quotient limit")
GRADIENT_XY = ("Gradient x", "Gradient y")
GRADIENT_XYZ = (*GRADIENT_XY, "Gradient z")
ZERO_DIRECTION = ("Zero direction x", "Zero direction y")
EXTREME_DIRECTIONS = (
    "Maximum rate",
    "Maximizing direction x",
    "Maximizing direction y",
    *ZERO_DIRECTION,
)


def vector(values: tuple[sp.Expr, ...]) -> str:
    return r"\left(" + ",".join(map(tex, values)) + r"\right)"


def formulas(values: tuple[sp.Expr, ...], labels: tuple[str, ...]) -> OrderedAnswer:
    return OrderedAnswer(tuple(FormulaAnswer(value) for value in values), labels)


def unit_direction(n: int) -> tuple[sp.Expr, ...]:
    return sp.Rational(n * n - 1, n * n + 1), sp.Rational(2 * n, n * n + 1)


def nonsmooth(
    statement: str,
    base: tuple[sp.Expr, ...],
    unit: tuple[sp.Expr, ...],
    left: sp.Expr,
    right: sp.Expr,
    joint: sp.Expr | str,
    proof: str,
    visual: dict[str, Any],
) -> Built:
    built = finish(
        rf"\text{{For }} f(x,y)={statement},\quad P={vector(base)},\quad v={vector(unit)},"
        r"\quad\text{ give the left, right and two-sided limits of }"
        r"\frac{f(P+tv)-f(P)}{t}\text{ as }t\to0.\text{ "
        r"Use does\_not\_exist when the limits disagree.}",
        OrderedAnswer((LimitAnswer(left), LimitAnswer(right), LimitAnswer(joint)), QUOTIENTS),
        proof,
        rf"L_-={tex(left)},\quad L_+={tex(right)},\quad"
        + (
            r"\text{the two-sided limit does not exist.}"
            if isinstance(joint, str)
            else rf"L={tex(joint)}\text{{, so there is no finite directional derivative.}}"
        ),
    )
    return replace(built, visual=visual)


def norm_at_origin(a: int, b: int, c: int) -> Built:
    unit = unit_direction(c + 1)
    slope = sp.sqrt(a * unit[0] ** 2 + b * unit[1] ** 2)
    visual = plot(
        "Directional section through the origin",
        "The two rays meet at the origin with opposite signed slopes.",
        [
            path("Negative displacement", -1, 0, lambda t: -float(slope) * t),
            path("Positive displacement", 0, 1, lambda t: float(slope) * t),
        ],
        [point("Origin", 0, 0, included=True)],
    )
    visual.update(xLabel="t", yLabel="f")
    return nonsmooth(
        tex(sp.sqrt(a * X**2 + b * Y**2)),
        (sp.S.Zero, sp.S.Zero),
        unit,
        -slope,
        slope,
        "does_not_exist",
        rf"f(tv)=|t|\,{tex(slope)},\quad\frac{{f(tv)-f(0)}}{{t}}=\frac{{|t|}}{{t}}{tex(slope)}.",
        visual,
    )


def cube_root_at_boundary(a: int, b: int, c: int) -> Built:
    unit = unit_direction(b + 1)
    ux, uy = map(float, unit)
    visual = plot(
        "Directional section through a cube root",
        "The function passes through the marked point. "
        "The quotient grows without bound on both sides.",
        [path("Cube root section", -0.5, 0.5, lambda t: math.cbrt(a * (c + t * ux) * t * uy))],
        [point("Base point", 0, 0, included=True)],
    )
    visual.update(xLabel="t", yLabel="f")
    return nonsmooth(
        rf"\sqrt[3]{{{a}xy}}",
        (sp.Integer(c), sp.S.Zero),
        unit,
        sp.oo,
        sp.oo,
        sp.oo,
        rf"\frac{{f(P+tv)}}{{t}}=\frac{{\sqrt[3]{{{a}({c}+tv_x)v_y}}}}{{|t|^{{2/3}}}}"
        rf"\quad\text{{and the numerator tends to }}\sqrt[3]{{{a * c}v_y}}>0.",
        visual,
    )


def gradient_at(expression: sp.Expr, base: tuple[sp.Expr, ...]) -> tuple[sp.Expr, ...]:
    variables = (X, Y, Z)[: len(base)]
    values = dict(zip(variables, base, strict=True))
    return tuple(
        sp.simplify(sp.diff(expression, var).subs(values, simultaneous=True)) for var in variables
    )


def gradient_or_direction(
    expression: sp.Expr,
    base: tuple[sp.Expr, ...],
    direction: tuple[sp.Expr, ...] = (),
) -> Built:
    names = "x,y,z" if len(base) == 3 else "x,y"
    grad = gradient_at(expression, base)
    known = rf"f({names})={tex(expression)},\quad P={vector(base)}."
    derivation = (
        r"\text{Differentiate in each coordinate holding the others fixed. }"
        rf"\nabla f(P)={vector(grad)}."
    )
    if not direction:
        labels = GRADIENT_XYZ if len(base) == 3 else GRADIENT_XY
        return finish(
            r"\text{Find the full gradient at the given point for }" + known,
            formulas(grad, labels),
            derivation,
            rf"\nabla f(P)={vector(grad)}.",
        )
    value = sp.simplify(sum(part * unit for part, unit in zip(grad, direction, strict=True)))
    built = finish(
        r"\text{Find the directional derivative for }"
        + known
        + rf"\quad\text{{The unit direction is }}v={vector(direction)}.",
        FormulaAnswer(value),
        derivation,
        rf"D_vf(P)=\nabla f(P)\cdot v={tex(value)}.",
    )
    t = sp.Symbol("t", real=True)
    variables = (X, Y, Z)[: len(base)]
    profile = expression.subs(
        {var: p + t * u for var, p, u in zip(variables, base, direction, strict=True)},
        simultaneous=True,
    )
    at_zero = float(profile.subs(t, 0))
    rate = float(value)
    section = sp.lambdify(t, profile, "math")
    visual = plot(
        "Directional section and tangent",
        "The tangent slope is the directional derivative. "
        "The horizontal axis is signed displacement.",
        [
            path("Function along direction", -0.2, 0.2, section),
            path("Tangent", -0.2, 0.2, lambda t: at_zero + rate * t),
        ],
        [point("Base point", 0, at_zero, included=True)],
    )
    visual.update(xLabel="t", yLabel="f")
    return replace(built, visual=visual)


def cubic_polynomial_gradient(a: int, b: int, c: int) -> Built:
    return gradient_or_direction(a * X**3 + b * X * Y**2 + c, (sp.S.One, sp.Integer(-2)))


def nested_log_gradient(a: int, b: int, c: int) -> Built:
    return gradient_or_direction(a * sp.log(X + b * sp.log(Y)), (c * sp.E, sp.S.One))


def variable_power_gradient(a: int, b: int, c: int) -> Built:
    return gradient_or_direction((1 + a * X * Y) ** (b * Y + c), (sp.S.Zero, sp.S.Zero))


def radical_log_gradient(a: int, b: int, c: int) -> Built:
    return gradient_or_direction(
        a * X * sp.sqrt(Y) - b * sp.exp(c * Z) * sp.log(Y), (sp.S.Zero, sp.S.One, sp.S.Zero)
    )


def sinusoidal_quotient_gradient(a: int, b: int, c: int) -> Built:
    return gradient_or_direction(a * X / (b * Y + c * sp.sin(Z)), (sp.S.Zero, sp.S.One, sp.pi))


def nested_root_gradient(a: int, b: int, c: int) -> Built:
    return gradient_or_direction(sp.sqrt(a * Z + sp.sqrt(b * Y + sp.sqrt(c * X))), (sp.S.One,) * 3)


def quadratic_directional(a: int, b: int, c: int) -> Built:
    return gradient_or_direction(
        a * X**2 - b * Y**2,
        (sp.Integer(-c - 2), sp.Integer(4)),
        (sp.Rational(12, 13), sp.Rational(5, 13)),
    )


def rational_directional(a: int, b: int, c: int) -> Built:
    return gradient_or_direction(
        a * X - b * Y / X**2 + c * Y, (sp.S.One, sp.S.One), (sp.Rational(3, 5), -sp.Rational(4, 5))
    )


def exponential_directional(a: int, b: int, c: int) -> Built:
    return gradient_or_direction(
        sp.exp((1 + a % 3) * X**2 * Y - b * Z),
        (-sp.S.One, sp.Integer(1 + c % 2), -sp.S.One),
        (sp.Rational(2, 3), -sp.Rational(2, 3), sp.Rational(1, 3)),
    )


def extreme_or_zero(expression: sp.Expr, base: tuple[sp.Expr, ...], *, extreme: bool) -> Built:
    p, q = gradient_at(expression, base)
    magnitude = sp.sqrt(p * p + q * q)
    maximizing = (p / magnitude, q / magnitude)
    sign = sp.sign(q)
    zero = (sign * q / magnitude, -sign * p / magnitude)
    if extreme:
        request = (
            r"\text{Give the maximum directional derivative, the maximizing unit vector,"
            r" and the zero-rate unit vector with positive }x\text{ component.}"
        )
        answer = formulas((magnitude, *maximizing, *zero), EXTREME_DIRECTIONS)
        details = rf"\max D_v f(P)={tex(magnitude)},\quad v_{{\max}}={vector(maximizing)}.\quad"
    else:
        request = (
            r"\text{The two zero-rate directions are opposites. Give the unit vector with"
            r" positive }x\text{ component.}"
        )
        answer = formulas(zero, ZERO_DIRECTION)
        details = ""
    built = finish(
        rf"f(x,y)={tex(expression)},\quad P={vector(base)}.\quad" + request,
        answer,
        rf"\nabla f(P)={vector((p, q))},\quad D_v f(P)=({tex(p)})\cos\alpha+({tex(q)})\sin\alpha."
        r"\quad\text{The rate is zero for perpendicular unit "
        r"vectors and maximal in the gradient direction.}",
        details + rf"v_0=\pm{vector(zero)}.",
    )
    zero_angle = math.atan2(float(zero[1]), float(zero[0])) % (2 * math.pi)
    other_angle = (zero_angle + math.pi) % (2 * math.pi)
    max_angle = math.atan2(float(q), float(p)) % (2 * math.pi)
    markers = [point("Zero rate", angle, 0, included=True) for angle in (zero_angle, other_angle)]
    if extreme:
        markers.append(point("Maximum rate", max_angle, float(magnitude), included=True))
    visual = plot(
        "Directional rate as a function of angle",
        "The marked zeros are separated by half a turn. The angle is measured in radians.",
        [
            path(
                "Directional derivative",
                0,
                2 * math.pi,
                lambda angle: float(p) * math.cos(angle) + float(q) * math.sin(angle),
            )
        ],
        markers,
    )
    visual.update(xLabel="angle in radians", yLabel="rate")
    return replace(built, visual=visual)


def logarithmic_extreme_directions(a: int, b: int, c: int) -> Built:
    return extreme_or_zero(
        a * Y - b * X**2 + (a + c) * sp.log(X * Y), (-sp.S.Half, -sp.S.One), extreme=True
    )


def exponential_zero_directions(a: int, b: int, c: int) -> Built:
    return extreme_or_zero(
        sp.exp(a * X / 2) * (b * X + c * Y**2), (sp.S.Zero, sp.Integer(2)), extreme=False
    )
