"""Monotonicity intervals, local and global extrema and optimization (#262)."""

from typing import Any

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer, RealSetAnswer
from app.engine.blocks.analysis_one import X
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._sequence_limits import finish

MONOTONIC = ("Increasing on", "Decreasing on")
EXTREMA = ("Minimum points", "Minimum values", "Maximum points", "Maximum values")
GLOBAL = ("Least value", "Greatest value")
DIMENSIONS = ("Width", "Height")
BOX = ("Base side", "Height")
ANGLE_RADIUS = ("Apex angle", "Largest radius")
EMPTY = sp.S.EmptySet


def scaled(k: int) -> str:
    return "" if k == 1 else str(k)


def iv(low: object, high: object) -> sp.Set:
    return sp.Interval.open(low, high)


def union(*parts: sp.Set) -> sp.Set:
    return sp.Union(*parts)


# AM1/46 and exam forms: intervals of monotonicity.


def monotonic(
    shown: str, increasing: sp.Set, decreasing: sp.Set, method: str, derivation: str
) -> Built:
    return finish(
        r"\text{Give the union of the open intervals on which }f\text{ is strictly increasing,}"
        r"\text{ and the same for strictly decreasing (use }\{\}\text{ for none):}"
        rf"\quad f(x)={shown}.",
        OrderedAnswer((RealSetAnswer(increasing), RealSetAnswer(decreasing)), MONOTONIC),
        method,
        derivation,
    )


def monotone_cubic(a: int, b: int, c: int) -> Built:
    p, q = a, a + 2 * b
    f = X**3 - sp.Rational(3 * (p + q), 2) * X**2 + 3 * p * q * X
    return monotonic(
        tex(f),
        union(iv(-sp.oo, p), iv(q, sp.oo)),
        iv(p, q),
        r"\text{Factor the derivative and read its sign.}",
        rf"f'(x)=3(x-{p})(x-{q}).",
    )


def monotone_trig_difference(a: int, b: int, c: int) -> Built:
    end = 2 * sp.pi / b
    return monotonic(
        rf"{scaled(a)}(\sin {scaled(b)}x-\cos {scaled(b)}x),\ 0\le x\le{tex(end)}",
        union(iv(0, 3 * sp.pi / (4 * b)), iv(7 * sp.pi / (4 * b), end)),
        iv(3 * sp.pi / (4 * b), 7 * sp.pi / (4 * b)),
        r"\cos u+\sin u=\sqrt2\sin(u+\pi/4).",
        rf"f'(x)={a * b}\sqrt2\sin({scaled(b)}x+\pi/4).",
    )


def monotone_linear_reciprocal(a: int, b: int, c: int) -> Built:
    r = sp.sqrt(sp.Rational(b, a))
    return monotonic(
        rf"{scaled(a)}x+\frac{{{b}}}{{x}}",
        union(iv(-sp.oo, -r), iv(r, sp.oo)),
        union(iv(-r, 0), iv(0, r)),
        r"\text{The domain excludes }0.",
        rf"f'(x)={a}-\frac{{{b}}}{{x^2}}=\frac{{{a}x^2-{b}}}{{x^2}},\quad x^2={tex(r**2)}.",
    )


def monotone_cubic_over_quadratic(a: int, b: int, c: int) -> Built:
    s, t = sp.sqrt(c), sp.sqrt(3 * c)
    return monotonic(
        rf"\frac{{x^3}}{{{c}-x^2}}",
        union(iv(-t, -s), iv(-s, s), iv(s, t)),
        union(iv(-sp.oo, -t), iv(t, sp.oo)),
        rf"\text{{The domain excludes }}x=\pm{tex(s)}.",
        rf"f'(x)=\frac{{x^2({3 * c}-x^2)}}{{({c}-x^2)^2}}\ge0\iff x^2\le{3 * c}.",
    )


def monotone_root_quotient(a: int, b: int, c: int) -> Built:
    return monotonic(
        rf"\frac{{\sqrt{{x^2-{c * c}}}}}{{{scaled(a)}x}}",
        union(iv(-sp.oo, -c), iv(c, sp.oo)),
        EMPTY,
        rf"\text{{The domain is }}|x|\ge{c}.",
        rf"f'(x)=\frac{{{c * c}}}{{{a}x^2\sqrt{{x^2-{c * c}}}}}>0.",
    )


def monotone_exponential_product(a: int, b: int, c: int) -> Built:
    turn = b + sp.Rational(1, a)
    return monotonic(
        tex((X - b) * sp.exp(-a * X)),
        iv(-sp.oo, turn),
        iv(turn, sp.oo),
        r"\text{Product rule.}",
        rf"f'(x)=e^{{-{a}x}}\left(1-{a}(x-{b})\right).",
    )


def monotone_log_square(a: int, b: int, c: int) -> Built:
    low = b * sp.exp(-2)
    return monotonic(
        rf"x\ln^2\frac{{x}}{{{b}}}" if b > 1 else r"x\ln^2x",
        union(iv(0, low), iv(b, sp.oo)),
        iv(low, b),
        r"\text{The domain is }x>0.",
        r"f'(x)=\ln u\,(\ln u+2),\quad u=x/" + str(b) + ".",
    )


def monotone_log_quotient(a: int, b: int, c: int) -> Built:
    turn = b * sp.E
    inner = rf"\frac{{x}}{{{b}}}" if b > 1 else "x"
    return monotonic(
        rf"\frac{{{scaled(a)}x}}{{\ln {inner}}}",
        iv(turn, sp.oo),
        union(iv(0, b), iv(b, turn)),
        rf"\text{{The domain is }}x>0,\ x\ne{b}.",
        rf"f'(x)=\frac{{{a}(\ln u-1)}}{{\ln^2u}},\quad u=x/{b}.",
    )


def monotone_exponential_difference(a: int, b: int, c: int) -> Built:
    base = a + 1
    turn = sp.log(sp.Rational(c * base, 2)) / sp.log(base)
    return monotonic(
        rf"{scaled(c)}\cdot{base}^{{x+1}}-{base * base}^{{x}}",
        iv(-sp.oo, turn),
        iv(turn, sp.oo),
        rf"\text{{Write }}{base * base}^x=({base}^x)^2.",
        rf"f'(x)={base}^x\ln{base}\left({c * base}-2\cdot{base}^x\right),\quad x_0={tex(turn)}.",
    )


def monotone_reciprocal_log(a: int, b: int, c: int) -> Built:
    turn = sp.Rational(a, b)
    return monotonic(
        rf"\frac{{{a}}}{{x}}+{scaled(b)}\ln x",
        iv(turn, sp.oo),
        iv(0, turn),
        r"\text{The domain is }x>0.",
        rf"f'(x)=\frac{{{b}x-{a}}}{{x^2}}.",
    )


def monotone_power_log(a: int, b: int, c: int) -> Built:
    k = b + 1
    turn = sp.exp(-sp.Rational(1, k))
    return monotonic(
        rf"{scaled(a)}x^{{{k}}}\ln x",
        iv(turn, sp.oo),
        iv(0, turn),
        r"\text{The domain is }x>0.",
        rf"f'(x)={a}x^{{{k - 1}}}({k}\ln x+1).",
    )


# AM1/47 and exam forms: local extrema.


def extrema(
    shown: str, minima: dict[Any, Any], maxima: dict[Any, Any], method: str, derivation: str
) -> Built:
    def sets(points: dict[Any, Any]) -> tuple[RealSetAnswer, RealSetAnswer]:
        return (
            RealSetAnswer(sp.FiniteSet(*points)),
            RealSetAnswer(sp.FiniteSet(*points.values())),
        )

    return finish(
        r"\text{Give the local minimum points and their values, then the local maximum}"
        r"\text{ points and their values, as sets (}\{\}\text{ for none):}"
        rf"\quad f(x)={shown}.",
        OrderedAnswer((*sets(minima), *sets(maxima)), EXTREMA),
        method,
        derivation,
    )


def extrema_cubic(a: int, b: int, c: int) -> Built:
    f = X**3 - a * X**2 + c
    turn = sp.Rational(2 * a, 3)
    return extrema(
        tex(f),
        {turn: f.subs(X, turn)},
        {sp.Integer(0): f.subs(X, 0)},
        r"\text{Critical points from }f'=0\text{; the sign of }f'\text{ changes there.}",
        rf"f'(x)=x(3x-{2 * a}).",
    )


def extrema_linear_reciprocal(a: int, b: int, c: int) -> Built:
    r = sp.sqrt(sp.Rational(b, a))
    value = 2 * sp.sqrt(a * b)
    return extrema(
        rf"{scaled(a)}x+\frac{{{b}}}{{x}}",
        {r: value},
        {-r: -value},
        r"\text{The domain excludes }0.",
        rf"f'(x)=\frac{{{a}x^2-{b}}}{{x^2}}.",
    )


def extrema_exponential_quotient(a: int, b: int, c: int) -> Built:
    base = a + 1
    point = 1 / sp.log(base)
    value = sp.E * sp.log(base) / b
    return extrema(
        rf"\frac{{{base}^x}}{{{scaled(b)}x}}",
        {point: value},
        {},
        r"\text{For }x<0\text{ the function is negative and decreasing.}",
        rf"f'(x)=\frac{{{base}^x(x\ln{base}-1)}}{{{b}x^2}}.",
    )


def extrema_shifted_exponential(a: int, b: int, c: int) -> Built:
    point = sp.Rational(1, a) - b
    return extrema(
        tex((X + b) * sp.exp(-a * X)),
        {},
        {point: sp.exp(a * b - 1) / a},
        r"\text{Product rule.}",
        rf"f'(x)=e^{{-{a}x}}(1-{a}(x+{b})).",
    )


def extrema_rational(a: int, b: int, c: int) -> Built:
    f = (X + b) / (X**2 + 1)
    root = sp.sqrt(b * b + 1)
    low, high = -b - root, -b + root
    return extrema(
        tex(f),
        {low: sp.radsimp(f.subs(X, low))},
        {high: sp.radsimp(f.subs(X, high))},
        r"\text{Quotient rule.}",
        rf"f'(x)=\frac{{1-{2 * b}x-x^2}}{{(x^2+1)^2}},\quad x=-{b}\pm{tex(root)}.",
    )


def extrema_absolute_quadratic(a: int, b: int, c: int) -> Built:
    p, q = -a, b + c
    middle = sp.Rational(p + q, 2)
    inner = sp.expand((X - p) * (X - q))
    return extrema(
        rf"\left|{tex(inner)}\right|",
        {sp.Integer(p): 0, sp.Integer(q): 0},
        {middle: sp.Rational(q - p, 2) ** 2},
        r"\text{The zeros of the quadratic are corners where }|\cdot|\text{ attains }0.",
        rf"|{tex(inner)}|=|(x-{tex(sp.Integer(p))})(x-{q})|,\ \text{{vertex at }}{tex(middle)}.",
    )


def extrema_x_log(a: int, b: int, c: int) -> Built:
    point = b / sp.E
    inner = rf"\frac{{x}}{{{b}}}" if b > 1 else "x"
    return extrema(
        rf"{scaled(a)}x\ln {inner}",
        {point: -a * b / sp.E},
        {},
        r"\text{The domain is }x>0.",
        rf"f'(x)={a}(\ln(x/{b})+1)=0\iff x={tex(point)}.",
    )


def extrema_root_cubic(a: int, b: int, c: int) -> Built:
    edge = c * sp.sqrt(3)
    return extrema(
        rf"{scaled(a)}\sqrt{{{3 * c * c}x-x^3}}",
        {-edge: 0, sp.Integer(0): 0, edge: 0},
        {sp.Integer(c): a * sp.sqrt(2 * c**3)},
        r"\text{The domain is }x\le-"
        + tex(edge)
        + r"\text{ or }0\le x\le"
        + tex(edge)
        + r"\text{; the function vanishes at the three boundary points.}",
        rf"f'(x)=\frac{{{a}({3 * c * c}-3x^2)}}{{2\sqrt{{{3 * c * c}x-x^3}}}}"
        rf"\ \Rightarrow\ x={c}.",
    )


def extrema_arctan_log(a: int, b: int, c: int) -> Built:
    point = sp.Rational(a, 2 * b)
    value = a * sp.atan(point) - b * sp.log(1 + point**2)
    return extrema(
        rf"{scaled(a)}\arctan x-{scaled(b)}\ln(1+x^2)",
        {},
        {point: value},
        r"\text{Differentiate both terms over the common denominator }1+x^2.",
        rf"f'(x)=\frac{{{a}-{2 * b}x}}{{1+x^2}}.",
    )


def extrema_none(a: int, b: int, c: int) -> Built:
    return extrema(
        rf"{scaled(a)}(\arctan x-x)-{scaled(b)}x^3",
        {},
        {},
        r"\text{Show that the derivative never changes sign.}",
        rf"f'(x)=-\frac{{{a}x^2}}{{1+x^2}}-{3 * b}x^2\le0,\ =0\text{{ only at }}0"
        r"\text{: strictly decreasing, no extrema.}",
    )


def extrema_exponential_shift(a: int, b: int, c: int) -> Built:
    point = b - sp.Rational(1, a)
    return extrema(
        tex((X - b) * sp.exp(a * X)),
        {point: -sp.exp(a * b - 1) / a},
        {},
        r"\text{Product rule.}",
        rf"f'(x)=e^{{{a}x}}(1+{a}(x-{b})).",
    )


# AM1/48 and exam forms: least and greatest values.


def global_values(shown: str, low: sp.Expr, high: sp.Expr, method: str, derivation: str) -> Built:
    return finish(
        rf"\text{{Give the least and the greatest value:}}\quad {shown}.",
        OrderedAnswer((FormulaAnswer(low), FormulaAnswer(high)), GLOBAL),
        method,
        derivation,
    )


def compare(f: sp.Expr, points: list[sp.Expr]) -> tuple[sp.Expr, sp.Expr]:
    values = [sp.nsimplify(sp.simplify(f.subs(X, p))) for p in points]
    return min(values, key=lambda v: float(v)), max(values, key=lambda v: float(v))


def global_cubic(a: int, b: int, c: int) -> Built:
    p, q = a, a + 1
    f = 2 * X**3 - 3 * (p + q) * X**2 + 6 * p * q * X
    left, right = p - 1, q + 1 + b % 2
    low, high = compare(f, [left, p, q, right])
    return global_values(
        rf"f(x)={tex(f)},\ x\in[{left},{right}]",
        low,
        high,
        r"\text{Compare the values at the critical points and the endpoints.}",
        rf"f'(x)=6(x-{p})(x-{q}).",
    )


def global_reciprocal_quadratic(a: int, b: int, c: int) -> Built:
    f = 1 / ((X - b) ** 2 + c)
    left, right = b - 3, b + 1
    return global_values(
        rf"f(x)={tex(f)},\ x\in[{left},{right}]",
        sp.Rational(1, 9 + c),
        sp.Rational(1, c),
        r"\text{The denominator is smallest at }x="
        + str(b)
        + r"\text{ and largest at the far end.}",
        rf"f(x)\le f({b})=\tfrac1{{{c}}},\qquad f({left})=\tfrac1{{{9 + c}}}.",
    )


def global_root_difference(a: int, b: int, c: int) -> Built:
    value = sp.sqrt(a + b)
    return global_values(
        rf"f(x)=\sqrt{{{a}+x}}-\sqrt{{{b}-x}}\ \text{{on its natural domain}}",
        -value,
        value,
        rf"\text{{The domain is }}[-{a},{b}]\text{{ and }}f\text{{ is increasing.}}",
        rf"f(-{a})=-{tex(value)},\qquad f({b})={tex(value)}.",
    )


def global_absolute_exponential(a: int, b: int, c: int) -> Built:
    k = b + 1
    # x<0: f'=e^{-x}(x-k)(k+2-x)<0. x>=0: f'=e^x(x-k)(x-k+2), local maximum at k-2.
    candidates = [(1 + k) ** 2 * sp.E, sp.Integer(k * k), sp.exp(k + 1)]
    if k >= 2:
        candidates.append(4 * sp.exp(k - 2))
    high = max(candidates, key=lambda v: float(v))
    return global_values(
        rf"f(x)=(x-{k})^2e^{{|x|}},\ x\in[-1,{k + 1}]",
        sp.Integer(0),
        high,
        r"\text{Treat }x<0\text{ and }x\ge0\text{ separately; }f"
        r"\text{ is not differentiable at }0.",
        rf"x<0:\ f'=e^{{-x}}(x-{k})({k + 2}-x)<0;\quad x\ge0:\ f'=e^x(x-{k})(x-{k - 2})."
        rf"\quad\text{{Compare }}f(-1),f(0),f({k - 2}),f({k}),f({k + 1}).",
    )


def global_absolute_parabola(a: int, b: int, c: int) -> Built:
    k = c + 1
    f = 1 - sp.Abs(k * k - X**2)
    left = -(k + 2)
    low, high = compare(f, [left, -k, 0, 1])
    return global_values(
        rf"f(x)=1-\left|{k * k}-x^2\right|,\ x\in[{left},1]",
        low,
        high,
        rf"\text{{Corners at }}x=\pm{k}\text{{; the inner parabola has its vertex at }}0.",
        rf"f({left})={tex(f.subs(X, left))},\ f(-{k})=1,\ f(0)={1 - k * k},\ f(1)={2 - k * k}.",
    )


def global_sine_cubic(a: int, b: int, c: int) -> Built:
    m = a + 3
    return global_values(
        rf"f(x)=\sin^3x-{m}\sin x,\ x\in\left[-\tfrac{{\pi}}{{2}},\tfrac{{\pi}}{{2}}\right]",
        sp.Integer(1 - m),
        sp.Integer(m - 1),
        r"\text{Put }u=\sin x\in[-1,1];\ g(u)=u^3-" + str(m) + r"u\text{ is decreasing.}",
        rf"g'(u)=3u^2-{m}<0,\qquad g(1)={1 - m},\ g(-1)={m - 1}.",
    )


def global_semicircle_root(a: int, b: int, c: int) -> Built:
    return global_values(
        rf"f(x)={scaled(a)}\sqrt{{{c * c}-(x-{b})^2}}\ \text{{on its natural domain}}",
        sp.Integer(0),
        sp.Integer(a * c),
        rf"\text{{The domain is }}[{b - c},{b + c}].",
        rf"f({b})={a * c},\qquad f({b - c})=f({b + c})=0.",
    )


def global_cosine_quotient(a: int, b: int, c: int) -> Built:
    p, q = ((5, 4), (5, 3), (13, 5), (13, 12), (17, 8))[a - 1]
    value = sp.Rational(1, sp.sqrt(p * p - q * q))
    return global_values(
        rf"f(x)=\frac{{\cos x}}{{{p}+{q}\sin x}}\ \text{{on }}\mathbb R",
        -value,
        value,
        r"\text{The function is }2\pi\text{-periodic; critical points from }f'=0.",
        rf"f'(x)=-\frac{{{p}\sin x+{q}}}{{({p}+{q}\sin x)^2}}=0\iff\sin x=-\tfrac{{{q}}}{{{p}}}.",
    )


def global_rational_interval(a: int, b: int, c: int) -> Built:
    return global_values(
        rf"f(x)=\frac{{{scaled(a)}x}}{{x^2-{scaled(c)}x+{c * c}}},\ x\in[0,{2 * c}]",
        sp.Integer(0),
        sp.Rational(a, c),
        r"\text{Quotient rule; the denominator is positive.}",
        rf"f'(x)=\frac{{{a}({c * c}-x^2)}}{{(x^2-{c}x+{c * c})^2}},"
        rf"\quad f({c})={tex(sp.Rational(a, c))},"
        rf"\ f(0)=0,\ f({2 * c})={tex(sp.Rational(2 * a, 3 * c))}.",
    )


def global_root_product(a: int, b: int, c: int) -> Built:
    r = 5 * a
    return global_values(
        rf"f(x)=x\sqrt{{{r * r}-x^2}},\ x\in[{-3 * a},{4 * a}]",
        sp.Integer(-12 * a * a),
        sp.Rational(r * r, 2),
        r"\text{Critical points }x=\pm r/\sqrt2\text{; only the positive one lies inside.}",
        rf"f'(x)=\frac{{{r * r}-2x^2}}{{\sqrt{{{r * r}-x^2}}}},\ f\left(\tfrac{{{r}}}{{\sqrt2}}"
        r"\right)"
        rf"={tex(sp.Rational(r * r, 2))},\ f({-3 * a})={-12 * a * a},\ f({4 * a})={12 * a * a}.",
    )


# AM1/49 and exam forms: optimization.


def pair(
    statement: str,
    first: sp.Expr,
    second: sp.Expr,
    labels: tuple[str, str],
    method: str,
    derivation: str,
) -> Built:
    return finish(
        statement,
        OrderedAnswer((FormulaAnswer(first), FormulaAnswer(second)), labels),
        method,
        derivation,
    )


def fenced_plots(a: int, b: int, c: int) -> Built:
    left, top, bottom = 100 * (a + 1), 100 * b, 100 * c
    total = left + top + bottom
    height = sp.sqrt(sp.Rational(2 * total + top + bottom, 3))
    width = total / height
    return pair(
        rf"\text{{A rectangle is split by a full-height fence into a left plot of }}{left}"
        rf"\text{{ m}}^2\text{{ and a right strip, which a horizontal fence splits into }}{top}"
        rf"\text{{ m}}^2\text{{ and }}{bottom}\text{{ m}}^2."
        r"\text{ Find the width and height (m) that}"
        r"\text{ minimise the total fence length.}",
        sp.radsimp(width),
        sp.radsimp(height),
        DIMENSIONS,
        r"\text{With height }y\text{ the width is }T/y\text{; the right strip has width }(B+C)/y.",
        rf"L(y)=2\cdot\frac{{{total}}}{{y}}+3y+\frac{{{top + bottom}}}{{y}},\quad L'(y)=0\iff "
        rf"y^2={tex(height**2)}.",
    )


def pipeline(a: int, b: int, c: int) -> Built:
    depth = 4 + 2 * a
    ratio = 2 + c % 2
    shore = depth + 4 * b
    point = sp.radsimp(depth / sp.sqrt(ratio * ratio - 1))
    return finish(
        rf"\text{{A platform lies }}{depth}\text{{ km from a straight coast; a refinery is on the}}"
        rf"\text{{ coast }}{shore}"
        rf"\text{{ km from the nearest coastal point. A km of pipe costs }}{ratio}"
        r"\text{ times more under sea than on land. How far from the nearest point should}"
        r"\text{ the pipe reach the coast (km)?}",
        FormulaAnswer(point),
        r"\text{Minimise }k\sqrt{d^2+x^2}+(s-x)\text{ for }0\le x\le s.",
        rf"\frac{{{ratio}x}}{{\sqrt{{{depth * depth}+x^2}}}}=1\iff x={tex(point)}<{shore}.",
    )


def container(a: int, b: int, c: int) -> Built:
    side = sp.Rational(a + 1, 2)
    floor, wall = 10 * (b + 1), 10 * (c + 1)
    volume = floor * side**3 / wall
    height = volume / side**2
    return pair(
        rf"\text{{A box with a square base holds }}{tex(volume)}\text{{ m}}^3."
        r"\text{ Base and lid cost }"
        rf"{floor}\text{{ per m}}^2\text{{, the four walls }}{wall}\text{{ per m}}^2."
        r"\text{ Find the base side and height (m) of least cost.}",
        side,
        height,
        BOX,
        r"\text{Express the cost with the base side }s\text{ alone.}",
        rf"K(s)={2 * floor}s^2+\frac{{{4 * wall}\cdot{tex(volume)}}}{{s}},\quad K'(s)=0\iff "
        rf"s^3={tex(side**3)}.",
    )


def incircle_triangle(a: int, b: int, c: int) -> Built:
    area = 3 * a * sp.sqrt(3)
    radius = sp.sqrt(sp.Rational(a, 1))
    return pair(
        rf"\text{{Among isosceles triangles of area }}{tex(area)}"
        r"\text{, find the apex angle that}"
        r"\text{ maximises the inscribed circle, and its radius.}",
        sp.pi / 3,
        radius,
        ANGLE_RADIUS,
        r"r=P/p\text{ with fixed area }P\text{; minimise the half-perimeter }p(\alpha).",
        r"p(\alpha)\text{ is least at }\alpha=\pi/3\text{ (equilateral)},\quad r=\sqrt{\frac{P}{3"
        r"\sqrt3}}" + rf"={tex(radius)}.",
    )


def parabola_rectangle(a: int, b: int, c: int) -> Built:
    k = c + 1
    half = k / sp.sqrt(3)
    return pair(
        rf"\text{{A rectangle has its base on the }}x\text{{-axis and its top corners on }}"
        rf"y={tex(a * (k * k - X**2))}.\text{{ Find the width and height of greatest area.}}",
        sp.radsimp(2 * half),
        sp.Rational(2 * a * k * k, 3),
        DIMENSIONS,
        r"\text{Area }2x\,y(x)\text{ for }0<x<" + str(k) + ".",
        rf"A(x)={2 * a}x({k * k}-x^2),\quad A'(x)=0\iff x={tex(half)}.",
    )


def semicircle_rectangle(a: int, b: int, c: int) -> Built:
    r = a + 1
    return pair(
        rf"\text{{Find the width and height of the largest rectangle inscribed in a half-disc of}}"
        rf"\text{{ radius }}{r}\text{{ with one side on the diameter.}}",
        r * sp.sqrt(2),
        r / sp.sqrt(2),
        DIMENSIONS,
        r"\text{With half-width }x\text{ the height is }\sqrt{R^2-x^2}.",
        rf"A(x)=2x\sqrt{{{r * r}-x^2}},\quad A'(x)=0\iff x=\tfrac{{{r}}}{{\sqrt2}}.",
    )


def semicircle_waste(a: int, b: int, c: int) -> Built:
    r = a + 1
    value = r * r * (sp.pi / 2 - 1)
    return finish(
        rf"\text{{The largest rectangle is cut from a half-disc of radius }}{r}"
        r"\text{ with one side on the diameter. How much material is lost?}",
        FormulaAnswer(value),
        r"\text{The largest rectangle has area }R^2.",
        rf"\tfrac{{\pi}}{{2}}\cdot{r * r}-{r * r}={tex(value)}.",
    )


def circle_square(a: int, b: int, c: int) -> Built:
    r = a + 1
    return pair(
        rf"\text{{A rectangle is cut from a disc of radius }}{r}\text{{ with the least waste.}}"
        r"\text{ Find its width and height.}",
        r * sp.sqrt(2),
        r * sp.sqrt(2),
        DIMENSIONS,
        r"\text{The diagonal is the diameter: maximise }xy\text{ with }x^2+y^2=4R^2.",
        rf"xy\le\tfrac{{x^2+y^2}}{{2}}={2 * r * r},\ "
        rf"\text{{equality for }}x=y={tex(r * sp.sqrt(2))}.",
    )
