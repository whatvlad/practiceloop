"""Cartesian double integrals and exact changes of order from AM2A/10.1–10.4."""

from dataclasses import replace
from typing import Any

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.answers.domain_formula import DomainFormulaAnswer
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import plot
from app.engine.generators._sequence_limits import finish

X, Y = sp.symbols("x y", real=True)
ONE, ZERO = sp.S.One, sp.S.Zero
Bounds = tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr]
BOUND_LABELS = ("Outer lower", "Outer upper", "Inner lower", "Inner upper")
PIECES = ("First integral", "Second integral", "Third integral")


def integral_tex(bounds: Bounds, outer: sp.Symbol, integrand: str) -> str:
    inner = Y if outer == X else X
    a, b, lower, upper = map(tex, bounds)
    return rf"\int_{{{a}}}^{{{b}}}\int_{{{lower}}}^{{{upper}}}{integrand}\,d{inner}\,d{outer}"


def boundary_paths(bounds: Bounds, outer: sp.Symbol) -> list[dict[str, Any]]:
    start, end, lower, upper = bounds
    traces = []
    for boundary in (lower, upper):
        points = []
        for i in range(33):
            coordinate = start + (end - start) * sp.Rational(i, 32)
            value = float(boundary.subs(outer, coordinate))
            xy = [float(coordinate), value]
            points.append(xy if outer == X else xy[::-1])
        traces.append(points)
    points = [*traces[0], *reversed(traces[1]), traces[0][0]]
    return [{"label": "Region boundary", "closed": True, "points": points}]


def integral(
    integrand: sp.Expr,
    bounds: Bounds,
    inner_primitive: sp.Expr,
    outer_primitive: sp.Expr | None = None,
    *,
    outer: sp.Symbol = X,
    boundary_text: str = "",
    method: str = "",
    symmetric_inner: sp.Expr | None = None,
) -> Built:
    start, end, lower, upper = bounds
    inner = Y if outer == X else X
    reduced = inner_primitive.subs(inner, upper) - inner_primitive.subs(inner, lower)
    if outer_primitive is None:
        integrand_for_outer = reduced if symmetric_inner is None else symmetric_inner
        outer_primitive = sp.Poly(integrand_for_outer, outer).integrate().as_expr()
    value = sp.simplify(outer_primitive.subs(outer, end) - outer_primitive.subs(outer, start))
    if boundary_text:
        statement = (
            rf"\text{{Evaluate }}\iint_D {tex(integrand)}\,dx\,dy"
            rf"\text{{ over the bounded region enclosed by }}{boundary_text}."
        )
    else:
        statement = r"\text{Evaluate }" + integral_tex(bounds, outer, tex(integrand)) + "."
    reduced_tex = tex(reduced if symmetric_inner is None else symmetric_inner)
    built = finish(
        statement,
        FormulaAnswer(value),
        method + rf"\quad {integral_tex(bounds, outer, tex(integrand))}."
        rf"\quad\text{{The inner antiderivative is }}{tex(inner_primitive)}.",
        rf"\text{{The resulting outer integral is }}\int_{{{tex(start)}}}^{{{tex(end)}}}"
        rf"\left({reduced_tex}\right)\,d{outer}"
        rf"=\left[{tex(outer_primitive)}\right]_{{{tex(start)}}}^{{{tex(end)}}}={tex(value)}.",
    )
    return replace(
        built,
        visual=plot(
            "Region of integration",
            "The boundary follows the displayed limits of integration.",
            boundary_paths(bounds, outer),
        ),
    )


def polynomial_rectangle(a: int, b: int, c: int) -> Built:
    f = a * X + X * Y - b * X**2 - c * Y
    return integral(f, (ZERO, ONE, ZERO, ONE), (a * X - b * X**2) * Y + (X - c) * Y**2 / 2)


def reciprocal_rectangle(a: int, b: int, c: int) -> Built:
    bounds = (ONE, sp.Integer(a + 1), sp.Integer(b), sp.Integer(b + c))
    return integral(
        X / Y**2, bounds, -X / Y, (sp.Rational(1, b) - sp.Rational(1, b + c)) * X**2 / 2
    )


def cubic_denominator_rectangle(a: int, b: int, c: int) -> Built:
    f = 1 / (X + Y + c) ** 3
    return integral(
        f,
        (ZERO, sp.Integer(a), ZERO, sp.Integer(b)),
        -1 / (2 * (X + Y + c) ** 2),
        (1 / (X + b + c) - 1 / (X + c)) / 2,
    )


def sine_rectangle(a: int, b: int, c: int) -> Built:
    stop = (b + 1) * sp.pi
    return integral(
        c * X * sp.sin(X * Y),
        (ZERO, sp.Rational(1, a + 1), sp.pi, stop),
        -c * sp.cos(X * Y),
        c * (sp.sin(sp.pi * X) / sp.pi - sp.sin(stop * X) / stop),
    )


def separable_exponential_rectangle(a: int, b: int, c: int) -> Built:
    f = sp.exp(a * X - b * Y)
    return integral(
        f,
        (ZERO, ONE, sp.Integer(-c), ZERO),
        -f / b,
        sp.exp(a * X) * (sp.exp(b * c) - 1) / (a * b),
    )


def linear_exponential_rectangle(a: int, b: int, c: int) -> Built:
    exp = sp.exp(-a * X)
    return integral(
        (X + Y) * exp,
        (ZERO, sp.Integer(b), ZERO, sp.Integer(c)),
        (X * Y + Y**2 / 2) * exp,
        -(c * X / a + sp.Rational(c, a * a) + sp.Rational(c * c, 2 * a)) * exp,
    )


def power_strip_integral(a: int, b: int, c: int) -> Built:
    return integral(
        b * Y / X**2,
        (ONE, sp.Integer(a + 1), c * X, c * X**2),
        b * Y**2 / (2 * X**2),
    )


def radical_wedge_integral(a: int, b: int, c: int) -> Built:
    return integral(
        b * X**2 * sp.sqrt(Y - X),
        (ONE, sp.Integer(a + 1), X, (1 + c * c) * X),
        sp.Rational(2 * b, 3) * X**2 * (Y - X) ** sp.Rational(3, 2),
        sp.Rational(4 * b * c**3, 27) * X ** sp.Rational(9, 2),
    )


def semicircle_integral(a: int, b: int, c: int) -> Built:
    return integral(
        b * X**3 + c * Y**3,
        (sp.Integer(-a), sp.Integer(a), ZERO, sp.sqrt(a * a - X**2)),
        b * X**3 * Y + c * Y**4 / 4,
        symmetric_inner=c * (a * a - X**2) ** 2 / 4,
        method=(
            r"\text{After the inner integration the term containing }x^3"
            r"\text{ is odd and integrates to zero.}"
        ),
    )


def radical_triangle_integral(a: int, b: int, c: int) -> Built:
    root = sp.sqrt(Y**2 + c * c)
    return integral(
        root,
        (ZERO, sp.Integer(a), ZERO, b * Y),
        X * root,
        sp.Rational(b, 3) * (Y**2 + c * c) ** sp.Rational(3, 2),
        outer=Y,
    )


def parabola_line_integral(a: int, b: int, c: int) -> Built:
    d = a * (a + 1)
    return integral(
        b * c * X * Y**2,
        (sp.Integer(-a - 1), sp.Integer(a), X, d - X**2),
        b * c * X * Y**3 / 3,
        boundary_text=rf"y=x,\ y={d}-x^2",
        method=rf"x^2+x-{d}=0\quad\Longrightarrow\quad x=-{a + 1},\ {a}.",
    )


def negative_curves_integral(a: int, b: int, c: int) -> Built:
    stop = 2 + (b - 1) % 3
    return integral(
        a * c * X**2 * Y,
        (sp.Integer(-stop), -ONE, -(Y**2), 1 / Y),
        a * c * X**3 * Y / 3,
        sp.Rational(a * c, 3) * (-1 / Y + Y**8 / 8),
        outer=Y,
        boundary_text=rf"y=-{stop},\ y=1/x,\ y=-\sqrt{{-x}}",
        method=r"\text{On the negative branch the curves meet at }y=-1\text{. Solve both for }x.",
    )


def exponential_radical_integral(a: int, b: int, c: int) -> Built:
    f = sp.exp(a * X / Y)
    return integral(
        f,
        (sp.Rational(1, b + 1), sp.Integer(c), ZERO, Y**2),
        Y * f / a,
        sp.exp(a * Y) * (Y / a**2 - sp.Rational(1, a**3)) - Y**2 / (2 * a),
        outer=Y,
        boundary_text=rf"x=0,\ y=\sqrt x,\ y={tex(sp.Rational(1, b + 1))},\ y={c}",
        method=r"\text{A horizontal slice runs from }x=0\text{ to }x=y^2.",
    )


def shifted_parabola_integral(a: int, b: int, c: int) -> Built:
    return integral(
        a * X * Y + b * X**2,
        (sp.Integer(-2), ZERO, X**2 + 3 * X + c, X + c),
        a * X * Y**2 / 2 + b * X**2 * Y,
        boundary_text=rf"y=x+{c},\ y=x^2+3x+{c}",
        method=r"\text{The boundaries meet when }x(x+2)=0.",
    )


def exponential_triangle_integral(a: int, b: int, c: int) -> Built:
    return integral(
        a * c * X**2 * sp.exp(X * Y),
        (ZERO, sp.Integer(b), X, sp.Integer(b)),
        a * c * X * sp.exp(X * Y),
        a * c * ((X / b - sp.Rational(1, b * b)) * sp.exp(b * X) - sp.exp(X**2) / 2),
        boundary_text=rf"y=x,\ y={b},\ x=0",
        method=r"\text{Use vertical slices and integrate the exponential in }y\text{ first.}",
    )


def angular_strip_integral(a: int, b: int, c: int) -> Built:
    return integral(
        c * X / (X**2 + Y**2),
        (sp.Integer(a), sp.Integer(a + b), X, sp.sqrt(3) * X),
        c * sp.atan(Y / X),
        c * sp.pi * X / 12,
        boundary_text=rf"x={a},\ x={a + b},\ y=x,\ y=\sqrt 3\,x",
        method=r"\text{Substitute }t=y/x\text{ in the inner integral. The angles are }\pi/4,\pi/3.",
    )


def gaussian_wedge_integral(a: int, b: int, c: int) -> Built:
    stop = sp.sqrt(sp.log(a + 1))
    return integral(
        sp.exp(c * X**2),
        (ZERO, stop, ZERO, 2 * b * X),
        Y * sp.exp(c * X**2),
        sp.Rational(b, c) * sp.exp(c * X**2),
        boundary_text=rf"y=0,\ y={2 * b}x,\ x=\sqrt{{\ln({a + 1})}}",
        method=r"\text{Integrate first across the wedge width, then use }u=x^2.",
    )


def sinusoidal_strip_integral(a: int, b: int, c: int) -> Built:
    outer = (
        b * (Y / 2 - sp.sin(2 * Y) / 4 - a * a * Y)
        - 2 * sp.cos(Y)
        + 3 * c * (Y * sp.cos(Y) - sp.sin(Y))
        + a * (2 * Y - 3 * c * Y**2 / 2)
    )
    return integral(
        2 * b * X - 3 * c * Y + 2,
        (ZERO, sp.pi, sp.Integer(-a), sp.sin(Y)),
        b * X**2 + (2 - 3 * c * Y) * X,
        outer,
        outer=Y,
        boundary_text=rf"y=0,\ y=\pi,\ x=-{a},\ x=\sin y",
        method=(
            r"\text{Use horizontal slices, the double-angle identity and integration by parts.}"
        ),
    )


def reverse_order(
    bounds: Bounds,
    reversed_bounds: tuple[Bounds, ...],
    explanation: str,
    *,
    original_outer: sp.Symbol = X,
) -> Built:
    outer = Y if original_outer == X else X
    parts = []
    for lo, hi, lower, upper in reversed_bounds:
        domain = sp.Interval(lo, hi)
        parts.append(
            OrderedAnswer(
                (
                    FormulaAnswer(lo),
                    FormulaAnswer(hi),
                    DomainFormulaAnswer(lower, domain, str(outer)),
                    DomainFormulaAnswer(upper, domain, str(outer)),
                ),
                BOUND_LABELS,
            )
        )
    labels = PIECES[: len(parts)]
    answer = OrderedAnswer(tuple(parts), labels) if len(parts) > 1 else parts[0]
    f = r"f(x,y)"
    original = integral_tex(bounds, original_outer, f)
    reversed_tex = "+".join(integral_tex(limits, outer, f) for limits in reversed_bounds)
    built = finish(
        rf"\text{{Reverse the order in }}{original}."
        rf"\quad\text{{Supply {len(parts)} integral "
        rf"piece(s) in increasing outer lower bound order.}}"
        r"\quad\text{At a tie, list the piece with lower inner coordinates first.}"
        r"\quad\text{Each piece gives outer lower, outer upper, inner lower, inner upper.}",
        answer,
        explanation,
        rf"{original}={reversed_tex}.",
    )
    return replace(
        built,
        visual=plot(
            "Region for changing integration order",
            "The boundary describes the original integral. Reversed slices cover the same region.",
            boundary_paths(bounds, original_outer),
        ),
    )


def absolute_value_reversal(a: int, b: int, c: int) -> Built:
    left, right = sp.Integer(-a), sp.Integer(a)
    bottom = sp.Integer(-b)
    cap = c * right
    return reverse_order(
        (left, right, bottom, c * sp.Abs(X)),
        ((bottom, ZERO, left, right), (ZERO, cap, left, -Y / c), (ZERO, cap, Y / c, right)),
        rf"y\le0\text{{ allows the full width. For }}y>0,\ |x|\ge y/{c}"
        r"\text{ gives two intervals.}",
    )


def circular_strip_reversal(a: int, b: int, c: int) -> Built:
    radius_squared = a * a + b * b
    limit = sp.sqrt(radius_squared - Y**2)
    return reverse_order(
        (sp.Integer(-a), sp.Integer(a), -sp.sqrt(radius_squared - X**2), ZERO),
        (
            (-sp.sqrt(radius_squared), sp.Integer(-b), -limit, limit),
            (sp.Integer(-b), ZERO, sp.Integer(-a), sp.Integer(a)),
        ),
        rf"x^2+y^2\le{radius_squared},\quad |x|\le{a},\quad y\le0."
        rf"\quad\text{{The circular bounds reach the side edges at }}y=-{b}.",
    )


def semicircle_split_reversal(a: int, b: int, c: int) -> Built:
    center = 2 * a
    right = sp.Integer(4 * a)
    middle = sp.Integer(center)
    radial = sp.sqrt(center * center - Y**2)
    left = Y**2 / right
    return reverse_order(
        (ZERO, right, sp.sqrt(right * X - X**2), 2 * sp.sqrt(a * X)),
        (
            (ZERO, middle, left, middle - radial),
            (ZERO, middle, middle + radial, right),
            (middle, right, left, right),
        ),
        rf"y\le2\sqrt{{{a}x}}\Longleftrightarrow x\ge y^2/{right}."
        rf"\quad\text{{For }}0\le y\le{center}\text{{ the semicircle removes the middle interval.}}"
        rf"\quad\text{{For }}y>{center}\text{{ there is only the parabola and the right edge.}}",
    )


def two_parabola_reversal(a: int, b: int, c: int) -> Built:
    end = sp.Integer(a)
    bound = sp.sqrt(2 * a)
    radius = sp.sqrt(X + a)
    inner = sp.sqrt(2 * X)
    return reverse_order(
        (-bound, bound, Y**2 - a, Y**2 / 2),
        ((-end, ZERO, -radius, radius), (ZERO, end, -radius, -inner), (ZERO, end, inner, radius)),
        rf"y^2\le x+{a},\quad y^2\ge2x."
        r"\quad\text{The second inequality matters only "
        r"for positive }x\text{ and separates two lobes.}",
        original_outer=Y,
    )


def trigonometric_reversal(a: int, b: int, c: int) -> Built:
    half = sp.pi / 2
    return reverse_order(
        (half, sp.pi, sp.cos(X), sp.sin(X)),
        ((-ONE, ZERO, sp.acos(Y), sp.pi), (ZERO, ONE, half, sp.pi - sp.asin(Y))),
        r"\text{On the second quadrant cosine and sine decrease. Negative }y"
        r"\text{ is bounded by cosine, positive }y\text{ by sine.}",
    )


def logarithmic_reversal(a: int, b: int, c: int) -> Built:
    return reverse_order(
        (ONE, sp.exp(a), sp.log(X), sp.Integer(a)),
        ((ZERO, sp.Integer(a), ONE, sp.exp(Y)),),
        rf"\ln x\le y\Longleftrightarrow x\le e^y.\quad 0\le y\le{a}.",
    )
