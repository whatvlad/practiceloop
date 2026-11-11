"""Tangent planes and first-order estimates from AM2A/6.4–7.2 (#279)."""

from dataclasses import replace

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import path, plot, point
from app.engine.generators._sequence_limits import finish

X, Y, Z = sp.symbols("x y z", real=True)
PLANE = ("Slope in x", "Slope in y", "Constant term")
CONTACT = ("Contact x", "Contact y", "Contact z")
LINEAR = ("Linear change", "Linear estimate")


def ordered(values: tuple[sp.Expr, ...], labels: tuple[str, ...]) -> OrderedAnswer:
    return OrderedAnswer(tuple(FormulaAnswer(value) for value in values), labels)


def tangent_visual(
    expression: sp.Expr,
    x: sp.Expr,
    y: sp.Expr,
    height: sp.Expr,
    p: sp.Expr,
    q: sp.Expr,
    width: float,
) -> dict[str, object]:
    fx = sp.lambdify(X, expression.subs(Y, y), "math")
    fy = sp.lambdify(Y, expression.subs(X, x), "math")
    x0, y0, z0 = float(x), float(y), float(height)
    visual = plot(
        "Coordinate sections at contact",
        "Each curve and its tangent share the same contact "
        "height. The horizontal coordinate is displacement.",
        [
            path("Surface at fixed y", -width, width, lambda t: fx(x0 + t)),
            path("Plane at fixed y", -width, width, lambda t: z0 + float(p) * t),
            path("Surface at fixed x", -width, width, lambda t: fy(y0 + t)),
            path("Plane at fixed x", -width, width, lambda t: z0 + float(q) * t),
        ],
        [point("Point of tangency", 0, z0, included=True)],
    )
    visual.update(xLabel="displacement", yLabel="z")
    return visual


def tangent(
    expression: sp.Expr,
    x: sp.Expr,
    y: sp.Expr,
    condition: str,
    *,
    derivation: str = "",
    contact_answer: bool = False,
    width: float = 0.25,
) -> Built:
    coordinates = {X: x, Y: y}
    height = expression.subs(coordinates, simultaneous=True)
    p, q = (sp.diff(expression, symbol).subs(coordinates, simultaneous=True) for symbol in (X, Y))
    offset = sp.simplify(height - p * x - q * y)
    plane = tex(p * X + q * Y + offset)
    at = rf"(x_0,y_0,z_0)=({tex(x)},{tex(y)},{tex(height)})"
    if contact_answer:
        prompt = r"\text{Give the contact point as an ordered triple.}"
        answer = ordered((x, y, height), CONTACT)
    else:
        prompt = r"\text{Give }(p,q,r)\text{ in the plane }z=px+qy+r."
        answer = ordered((p, q, offset), PLANE)
    built = finish(
        rf"\text{{For }}z={tex(expression)}\text{{, find the tangent plane }}{condition}.\quad"
        + prompt,
        answer,
        derivation + rf"\quad {at},\quad f_x(x_0,y_0)={tex(p)},\quad f_y(x_0,y_0)={tex(q)}.",
        rf"z-z_0=f_x(x_0,y_0)(x-x_0)+f_y(x_0,y_0)(y-y_0)\quad\Longrightarrow\quad z={plane}.",
    )
    return replace(built, visual=tangent_visual(expression, x, y, height, p, q, width))


def radical_plane(a: int, b: int, c: int) -> Built:
    y = sp.Integer((b + 1) ** 2 - 1)
    return tangent(a * X**2 * sp.sqrt(Y + 1), sp.Integer(c), y, rf"\text{{above }}({c},{y})")


def exponential_plane(a: int, b: int, c: int) -> Built:
    x = sp.Integer(1 + c % 3)
    return tangent(sp.exp(a * X + b * Y), x, sp.Integer(-1), rf"\text{{above }}({x},-1)")


def inverse_trig_plane(a: int, b: int, c: int) -> Built:
    expression = sp.Rational(a, b + c) * sp.asin(X) / sp.acos(Y)
    return tangent(
        expression, -sp.S.Half, sp.sqrt(3) / 2, r"\text{above }(-1/2,\sqrt{3}/2)", width=0.075
    )


def vertical_axis_plane(a: int, b: int, c: int) -> Built:
    return tangent(
        (a + X - b * Y) ** (c + 2),
        sp.S.Zero,
        sp.S.Zero,
        r"\text{at the intersection with the }z\text{ axis}",
        derivation=r"\text{On the vertical axis }x_0=y_0=0.",
    )


def horizontal_axis_plane(a: int, b: int, c: int) -> Built:
    return tangent(
        sp.exp(a * X + b * Y) - sp.exp(c - b * Y),
        sp.Rational(c, a),
        sp.S.Zero,
        r"\text{at the intersection with the }x\text{ axis}",
        derivation=(
            rf"\text{{On the axis }}y=z=0,\quad e^{{{a}x_0}}=e^{{{c}}}"
            rf"\Longrightarrow x_0={tex(sp.Rational(c, a))}."
        ),
    )


def parallel_plane_contact(a: int, b: int, c: int) -> Built:
    y = sp.Rational(a * b, b * b + (a * c) ** 2)
    x = -sp.Rational(c, b) * y
    return tangent(
        sp.atan(a * X / Y),
        x,
        y,
        rf"\text{{parallel to }}{b}x+{c}y-z=5",
        derivation=(
            rf"f_x={b},\ f_y={c}\ \Longrightarrow\ "
            rf"\frac{{{a}y}}{{y^2+{a * a}x^2}}={b},\quad -\frac{{{a}x}}{{y^2+{a * a}x^2}}={c}."
            rf"\quad x=-\frac{{{c}}}{{{b}}}y\text{{, then solve for nonzero }}y."
        ),
        contact_answer=True,
        width=float(y) / 3,
    )


def perpendicular_line_plane(a: int, b: int, c: int) -> Built:
    return tangent(
        a * X**2 + b * Y**2,
        -sp.Rational(1, 2 * a * c),
        -sp.Rational(1, 2 * b * c),
        rf"\text{{perpendicular to the line }}(x,y,z)=(t,t,{c}t)",
        derivation=(
            rf"(-f_x,-f_y,1)=\frac{{1}}{{{c}}}(1,1,{c})"
            rf"\quad\Longrightarrow\quad 2{a}x_0=2{b}y_0=-\frac{{1}}{{{c}}}."
        ),
    )


def first_order(
    expression: sp.Expr,
    base: tuple[sp.Expr, ...],
    increments: tuple[sp.Expr, ...],
    *,
    quantity: str = "",
    mode: str = "estimate",
) -> Built:
    variables = (X, Y, Z)[: len(base)]
    coordinates = dict(zip(variables, base, strict=True))
    baseline = expression.subs(coordinates, simultaneous=True)
    derivatives = tuple(
        sp.diff(expression, var).subs(coordinates, simultaneous=True) for var in variables
    )
    change = sp.simplify(
        sum(part * delta for part, delta in zip(derivatives, increments, strict=True))
    )
    estimate = sp.simplify(baseline + change)
    target = tuple(x + delta for x, delta in zip(base, increments, strict=True))
    base_tex = ",".join(map(tex, base))
    inc_tex = ",".join(map(tex, increments))
    if mode == "estimate":
        answer: FormulaAnswer | OrderedAnswer = ordered((change, estimate), LINEAR)
        request = r"\text{Give the signed linear change and the linear estimate of the value.}"
        result = rf"df={tex(change)},\quad f(P+\Delta)\approx {tex(estimate)}."
    else:
        value = sp.simplify(change / baseline) if mode == "relative" else change
        answer = FormulaAnswer(value)
        request, name = {
            "absolute": (
                r"\text{Give the first-order bound on absolute measurement error.}",
                r"|df|_{\max}",
            ),
            "relative": (
                r"\text{Give the first-order relative error bound as a fraction.}",
                r"|df|_{\max}/|f(P)|",
            ),
            "change": (r"\text{Give the approximate increase.}", r"df"),
        }[mode]
        result = rf"{name}={tex(value)}."
    names = ",".join(map(str, variables))
    if mode in ("absolute", "relative"):
        perturbation = rf"\text{{The coordinate error bounds are }}({inc_tex})."
        detail = (
            r"\quad\text{Each partial is positive, so all positive errors attain the linear bound.}"
        )
    else:
        perturbation = rf"\Delta=({inc_tex})."
        detail = ""
    built = finish(
        rf"\text{{{quantity} }}f({names})={tex(expression)},\quad P=({base_tex}).\quad "
        + perturbation
        + r"\quad\text{Use the total differential. }"
        + request,
        answer,
        rf"\nabla f(P)=({','.join(map(tex, derivatives))}),\quad f(P)={tex(baseline)}."
        rf"\quad df=\nabla f(P)\cdot\Delta={tex(change)}." + detail,
        result,
    )
    t = sp.Symbol("t", real=True)
    profile = expression.subs(
        {var: x + t * delta for var, x, delta in zip(variables, base, increments, strict=True)},
        simultaneous=True,
    )
    exact = sp.lambdify(t, profile, "math")
    visual = plot(
        "Linear estimate along the perturbation",
        "The two paths compare the function and its "
        "first-order model along the stated perturbation.",
        [
            path("Original function", 0, 1, exact),
            path("First-order model", 0, 1, lambda t: float(baseline) + t * float(change)),
        ],
        [
            point("Linear estimate", 1, float(estimate), included=True),
            point(
                "Original value",
                1,
                float(expression.subs(dict(zip(variables, target, strict=True)))),
                included=True,
            ),
        ],
    )
    visual.update(xLabel="fraction of perturbation", yLabel="f")
    return replace(built, visual=visual)


def power_product_approximation(a: int, b: int, c: int) -> Built:
    return first_order(
        X ** (a + 2) * Y ** (b + 1),
        (sp.S.One, sp.S.One),
        (sp.Rational(c, 100), -sp.Rational(b, 1000)),
    )


def cube_norm_approximation(a: int, b: int, c: int) -> Built:
    return first_order(
        (X**3 + Y**3 + Z**3) ** sp.Rational(1, 3),
        (sp.Integer(3), sp.Integer(4), sp.Integer(5)),
        tuple(sp.Rational(i, 100) for i in (a, b, c)),
    )


def exponential_product_approximation(a: int, b: int, c: int) -> Built:
    return first_order(
        X * sp.exp(Y), (sp.Integer(a + 2), sp.S.Zero), (-sp.Rational(b, 100), sp.Rational(c, 100))
    )


def cosine_quotient_approximation(a: int, b: int, c: int) -> Built:
    return first_order(
        sp.cos(X) / Y, (sp.S.Zero, sp.Integer(a + 1)), (sp.Rational(b, 100), -sp.Rational(c, 100))
    )


def cylinder_measurement_error(a: int, b: int, c: int) -> Built:
    return first_order(
        sp.pi * X**2 * Y,
        (sp.Integer(100 + 10 * a), sp.Integer(300 + 10 * b)),
        (sp.Integer(c), sp.Integer(c)),
        quantity="For a cylinder, x is the radius and y the height in mm. Use cubic mm.",
        mode="absolute",
    )


def diagonal_measurement_change(a: int, b: int, c: int) -> Built:
    return first_order(
        sp.sqrt(X**2 + Y**2 + Z**2),
        (sp.Integer(a + 2), sp.Integer(b + 3), sp.Integer(c + 10)),
        (sp.Rational(1, 50),) * 3,
        quantity="The rectangular box edges and its diagonal are measured in meters.",
        mode="change",
    )


def box_relative_error(a: int, b: int, c: int) -> Built:
    return first_order(
        X * Y * Z,
        (sp.Integer(a + 3), sp.Integer(b + 4), sp.Integer(c + 5)),
        (sp.Rational(a, 100), sp.Rational(b, 100), sp.Rational(c, 100)),
        quantity="A rectangular box has volume",
        mode="relative",
    )
