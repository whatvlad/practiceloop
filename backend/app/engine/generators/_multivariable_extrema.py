"""Complete local and constrained extrema from AM2A/8.3–8.4."""

import math
from dataclasses import replace
from typing import Any

import sympy as sp

from app.engine.answers.computational import CategoryAnswer, FormulaAnswer, OrderedAnswer
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import path, plot, point
from app.engine.generators._sequence_limits import finish

X, Y = sp.symbols("x y", real=True)
MINIMUM = ("Minimum x", "Minimum y", "Minimum value")
MAXIMUM = ("Maximum x", "Maximum y", "Maximum value")
EXTREMA = (*MINIMUM, *MAXIMUM)
STATIONARY = ("Stationary x", "Stationary y", "Stationary type")
TYPES = ("minimum", "maximum", "saddle")
PARABOLA_EXTREMA = (*MINIMUM, "Other minimum x", "Other minimum y", *MAXIMUM)

Coordinate = tuple[sp.Expr, sp.Expr]


def formulas(values: tuple[sp.Expr, ...], labels: tuple[str, ...]) -> OrderedAnswer:
    return OrderedAnswer(tuple(FormulaAnswer(value) for value in values), labels)


def value_at(expression: sp.Expr, coordinate: Coordinate) -> sp.Expr:
    return sp.simplify(expression.subs({X: coordinate[0], Y: coordinate[1]}, simultaneous=True))


def local_extrema(
    expression: sp.Expr,
    critical: tuple[Coordinate, ...],
    reduction: str,
    *,
    domain: str = r"\mathbb R^2",
    width: float = 0.2,
) -> Built:
    xx, xy, yy = sp.diff(expression, X, 2), sp.diff(expression, X, Y), sp.diff(expression, Y, 2)
    determinant = xx * yy - xy**2
    classified: dict[str, list[Coordinate]] = {kind: [] for kind in TYPES}
    details = []
    for coordinate in critical:
        d = value_at(determinant, coordinate)
        curvature = value_at(xx, coordinate)
        if d.is_negative:
            kind = "saddle"
        elif d.is_positive and curvature.is_positive:
            kind = "minimum"
        elif d.is_positive and curvature.is_negative:
            kind = "maximum"
        else:
            raise ValueError("The stationary point must be nondegenerate")
        classified[kind].append(coordinate)
        details.append(
            rf"({tex(coordinate[0])},{tex(coordinate[1])}):"
            rf"\quad \det H={tex(d)},\quad f_{{xx}}={tex(curvature)}\quad\text{{{kind}}}."
        )
    extrema = [(kind, p) for kind in TYPES[:2] for p in classified[kind]]
    if extrema:
        labels = tuple(
            label for kind, _ in extrema for label in (MINIMUM if kind == "minimum" else MAXIMUM)
        )
        values = tuple(value for _, p in extrema for value in (*p, value_at(expression, p)))
        answer = formulas(values, labels)
        request = (
            r"\text{Find all local extrema. For each, give }(x,y,f(x,y))"
            r"\text{, with a minimum first if both types occur.}"
        )
        result = answer.latex()
    else:
        (p,) = classified["saddle"]
        answer = OrderedAnswer(
            (FormulaAnswer(p[0]), FormulaAnswer(p[1]), CategoryAnswer("saddle", TYPES)),
            STATIONARY,
        )
        request = (
            r"\text{Find the unique stationary point and classify it as}"
            r"\text{ a minimum, maximum or saddle.}"
        )
        result = r"\text{The only stationary point is a saddle, so there are no local extrema.}"
    built = finish(
        rf"f(x,y)={tex(expression)},\quad (x,y)\in {domain}.\quad" + request,
        answer,
        reduction,
        r"\qquad ".join(details) + r"\qquad " + result,
    )
    focus = extrema or [("saddle", classified["saddle"][0])]
    visual = local_sections(expression, focus, width)
    return replace(built, visual=visual)


def local_sections(
    expression: sp.Expr, focus: list[tuple[str, Coordinate]], width: float
) -> dict[str, Any]:
    paths, markers = [], []
    for kind, (x, y) in focus:
        height = value_at(expression, (x, y))
        t = sp.Symbol("t", real=True)
        fx = sp.lambdify(t, expression.subs({X: x + t, Y: y}, simultaneous=True) - height, "math")
        fy = sp.lambdify(t, expression.subs({X: x, Y: y + t}, simultaneous=True) - height, "math")
        paths.extend(
            [
                path(f"{kind} at fixed y", -width, width, fx),
                path(f"{kind} at fixed x", -width, width, fy),
            ]
        )
        markers.append(point(kind.capitalize(), 0, 0, included=True))
    visual = plot(
        "Local coordinate sections",
        "Each section subtracts the stationary height. "
        "Zero displacement marks the stationary point.",
        paths,
        markers,
    )
    visual.update(xLabel="displacement", yLabel="height change")
    return visual


def symmetric_cubic_extrema(a: int, b: int, c: int) -> Built:
    u, v = X - b, Y - c
    stationary = tuple(
        (sp.Integer(i + b), sp.Integer(j + c)) for i, j in ((4, 1), (-4, -1), (1, 4), (-1, -4))
    )
    return local_extrema(
        a * (u**3 + 3 * u * v * v - 51 * u - 24 * v),
        stationary,
        rf"u=x-{b},\ v=y-{c}:\quad uv=4,\ u^2+v^2=17."
        r"\quad (u+v)^2=25,\ (u-v)^2=9\text{ give exactly four stationary points.}",
    )


def reciprocal_exponential_extremum(a: int, b: int, c: int) -> Built:
    u, v = X / b, Y - c
    return local_extrema(
        a * (u * sp.exp(-v) + 1 / u + sp.exp(v)),
        ((sp.Integer(b), sp.Integer(c)),),
        rf"u=x/{b},\ v=y-{c}:\quad e^{{-v}}=1/u^2,\ u=e^{{2v}}>0."
        r"\quad\text{Substitution gives }u=u^4\text{, hence }u=1,v=0.",
        domain=r"\{(x,y):x\ne0\}",
    )


def positive_cubic_product_extremum(a: int, b: int, c: int) -> Built:
    k = 4 * (b + c)
    return local_extrema(
        a * X * Y**2 * (k - X - Y),
        ((sp.Integer(k // 4), sp.Integer(k // 2)),),
        rf"f_x=0\Longrightarrow 2x+y={k},\quad f_y=0\Longrightarrow 2x+3y={2 * k}."
        r"\quad\text{The two linear equations have one solution in the quadrant.}",
        domain=r"(0,\infty)^2",
    )


def square_root_extremum(a: int, b: int, c: int) -> Built:
    scale = 3 * (b + c)
    return local_extrema(
        a * (Y * sp.sqrt(X) - Y**2 - X + scale * Y),
        ((sp.Integer((b + c) ** 2), sp.Integer(2 * (b + c))),),
        rf"f_x=0\Longrightarrow y=2\sqrt x,\quad f_y=0\Longrightarrow 2y=\sqrt x+{scale}."
        r"\quad\text{At }x=0\text{ the only boundary candidate is }y="
        rf"{tex(sp.Rational(scale, 2))}\text{{. Along "
        rf"the boundary it decreases away from this point,"
        r" and moving inward at fixed }y\text{ increases the value.}",
        domain=r"[0,\infty)\times\mathbb R",
    )


def coupled_cubic_extremum(a: int, b: int, c: int) -> Built:
    u, v = X - b, Y - c
    return local_extrema(
        a * (u**3 + v**3 - 3 * a * u * v),
        ((sp.Integer(b), sp.Integer(c)), (sp.Integer(a + b), sp.Integer(a + c))),
        rf"u=x-{b},\ v=y-{c}:\quad u^2={a}v,\ v^2={a}u."
        rf"\quad u\left(u^3-{a**3}\right)=0\quad\text{{gives two real solutions.}}",
    )


def positive_rational_extremum(a: int, b: int, c: int) -> Built:
    k = b + c
    return local_extrema(
        a * (k**3 / X + X / Y + Y),
        ((sp.Integer(k * k), sp.Integer(k)),),
        rf"f_x=0\Longrightarrow x^2={k**3}y,\quad f_y=0\Longrightarrow x=y^2."
        rf"\quad y^3={k**3}\text{{ has a unique positive solution.}}",
        domain=r"(0,\infty)^2",
    )


def logarithmic_saddle(a: int, b: int, c: int) -> Built:
    y = sp.sqrt(2 * a)
    return local_extrema(
        b * (X * Y + sp.log(Y) + a * X**2) + c,
        ((-1 / y, y),),
        rf"f_x=0\Longrightarrow y+{2 * a}x=0,\quad f_y=0\Longrightarrow x=-1/y."
        rf"\quad y=\sqrt{{{2 * a}}}\text{{ by positivity.}}",
        domain=r"\mathbb R\times(0,\infty)",
    )


def exponential_sum_extremum(a: int, b: int, c: int) -> Built:
    u, v = X - b, Y - c
    return local_extrema(
        sp.exp(u - 2 * v) + sp.exp(v - u) + sp.exp(a + v),
        ((sp.Integer(b - a), sp.Integer(c) - sp.Rational(2 * a, 3)),),
        r"\text{Call the three exponential terms }A,B,C.\quad f_x=A-B,\quad f_y=-2A+B+C."
        r"\quad A=B=C\text{ gives two independent linear equations in the exponents.}",
    )


def exponential_product_saddle(a: int, b: int, c: int) -> Built:
    k = b + c
    return local_extrema(
        a * sp.exp(X**2 - Y) * (k - X - Y),
        ((-sp.S.Half, sp.Rational(2 * k + 3, 2)),),
        rf"L={k}-x-y:\quad f_y=0\Longrightarrow L=-1,"
        r"\quad f_x=0\Longrightarrow 2xL-1=0.\quad x=-1/2.",
    )


def restricted(
    expression: sp.Expr,
    constraint: str,
    values: tuple[sp.Expr, ...],
    labels: tuple[str, ...],
    derivation: str,
    result: str,
    curve: Any,
    interval: tuple[float, float],
    markers: list[tuple[str, float, float]],
    axis: str,
) -> Built:
    built = finish(
        rf"\text{{Find the constrained extrema of }}f(x,y)={tex(expression)},\quad {constraint}."
        rf"\quad\text{{ Return in order {', '.join(labels)}.}}",
        formulas(values, labels),
        derivation,
        result,
    )
    visual = plot(
        "Objective on the constraint",
        "The profile follows the constraint. The marked "
        "extrema use the same parameters as the task.",
        [path("Restricted objective", *interval, curve)],
        [point(label, t, height, included=True) for label, t, height in markers],
    )
    visual.update(xLabel=axis, yLabel="f")
    return replace(built, visual=visual)


def linear_constraint_minimum(a: int, b: int, c: int) -> Built:
    length_squared = a * a + b * b
    x, y = sp.Rational(a * c, length_squared), sp.Rational(b * c, length_squared)
    height = sp.Rational(c * c, length_squared)
    return restricted(
        X**2 + Y**2,
        rf"{a}x+{b}y={c}",
        (x, y, height),
        MINIMUM,
        rf"y=({c}-{a}x)/{b}.\quad\text{{The restricted "
        rf"quadratic has a positive leading coefficient.}}",
        rf"\min f={tex(height)}\text{{ at }}({tex(x)},{tex(y)})."
        r"\quad\text{The quadratic is unbounded above.}",
        lambda t: t * t + ((c - a * t) / b) ** 2,
        (float(x) - 1, float(x) + 1),
        [("Minimum", float(x), float(height))],
        "x",
    )


def parabolic_constraint_extrema(a: int, b: int, c: int) -> Built:
    h = b + c
    expression = (X - (a + h * h + 1)) ** 2 + 2 * Y**2
    x = sp.Integer(a + h * h)
    minimum, maximum = sp.Integer(2 * h * h + 1), sp.Integer((h * h + 1) ** 2)
    return restricted(
        expression,
        rf"x=y^2+{a}",
        (x, sp.Integer(h), minimum, x, sp.Integer(-h), sp.Integer(a), sp.S.Zero, maximum),
        PARABOLA_EXTREMA,
        rf"\text{{Substitute }}x=y^2+{a}:\quad f=(y^2-{h * h})^2+{minimum}."
        rf"\quad f'=4y(y-{h})(y+{h}).",
        rf"\text{{Global minima at }}y=\pm{h},\quad"
        r"\text{local maximum at }y=0\text{. There is no global maximum.}",
        lambda t: (t * t - h * h) ** 2 + int(minimum),
        (-h - 0.5, h + 0.5),
        [
            ("Minimum", h, float(minimum)),
            ("Minimum", -h, float(minimum)),
            ("Local maximum", 0, float(maximum)),
        ],
        "y",
    )


def logarithmic_constraint_maximum(a: int, b: int, c: int) -> Built:
    k = sp.Rational(b, 3 * a**3)
    x, y = sp.Integer(a), -k * a
    height = b * sp.log(a) - sp.Rational(b, 3) + c
    return restricted(
        X**2 * Y + b * sp.log(X) + c,
        rf"y=-{tex(k)}x,\quad x>0",
        (x, y, height),
        MAXIMUM,
        rf"f(x,-{tex(k)}x)=-{tex(k)}x^3+{b}\ln x+{c}."
        rf"\quad f'(x)=\frac{{{b}-3({tex(k)})x^3}}{{x}}.",
        rf"\text{{The derivative changes from positive to negative at }}x={a}."
        r"\quad\text{The profile tends to }-\infty\text{ at both ends.}",
        lambda t: -float(k) * t**3 + b * math.log(t) + c,
        (a / 4, 2 * a),
        [("Maximum", a, float(height))],
        "x",
    )


def circular_constraint_extrema(a: int, b: int, c: int) -> Built:
    norm = sp.sqrt(a * a + b * b)
    x, y = a * c / norm, b * c / norm
    height = c * norm
    angle = math.atan2(b, a)
    return restricted(
        a * X + b * Y,
        rf"x^2+y^2={c * c}",
        (-x, -y, -height, x, y, height),
        EXTREMA,
        rf"|{a}x+{b}y|\le\sqrt{{{a * a + b * b}}}\sqrt{{x^2+y^2}}={tex(height)}.",
        r"\text{Equality occurs only at the two antipodal "
        r"points parallel to the coefficient vector.}",
        lambda t: c * (a * math.cos(t) + b * math.sin(t)),
        (0, 2 * math.pi),
        [("Minimum", angle + math.pi, -float(height)), ("Maximum", angle, float(height))],
        "angle in radians",
    )
