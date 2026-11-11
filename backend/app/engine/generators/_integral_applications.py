"""Bounded regions and applications of the single integral (#269)."""

import math
from dataclasses import dataclass, replace
from typing import Any

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, LimitAnswer
from app.engine.blocks.analysis_one import X
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import path, plot, point
from app.engine.generators._sequence_limits import finish

Y = sp.Symbol("y", real=True)


@dataclass(frozen=True, slots=True)
class Strip:
    lo: sp.Expr | int
    hi: sp.Expr | int
    lower: sp.Expr
    upper: sp.Expr
    primitive: sp.Expr


def exact_difference(primitive: sp.Expr, variable: sp.Symbol, lo: Any, hi: Any) -> sp.Expr:
    return sp.expand(sp.expand_log(primitive.subs(variable, hi) - primitive.subs(variable, lo)))


def strip_paths(strips: tuple[Strip, ...], variable: sp.Symbol = X) -> list[dict[str, Any]]:
    outlines = []
    for index, strip in enumerate(strips, start=1):
        lower = sp.lambdify(variable, strip.lower, "math")
        upper = sp.lambdify(variable, strip.upper, "math")
        lo, hi = float(strip.lo), float(strip.hi)
        samples = [lo + (hi - lo) * k / 31 for k in range(32)]
        samples[0], samples[-1] = lo, hi
        coordinates = [[t, lower(t)] for t in samples] + [[t, upper(t)] for t in reversed(samples)]
        if variable == Y:
            coordinates = [[v, u] for u, v in coordinates]
        outlines.append(
            {"label": f"Region boundary {index}", "points": coordinates, "closed": True}
        )
    return outlines


def region(
    statement: str, strips: tuple[Strip, ...], method: str, *, variable: sp.Symbol = X
) -> Built:
    value = sum(exact_difference(s.primitive, variable, s.lo, s.hi) for s in strips)
    integrals = "+".join(
        rf"\int_{{{tex(s.lo)}}}^{{{tex(s.hi)}}}\left({tex(s.upper - s.lower)}\right)d{variable}"
        for s in strips
    )
    bounds = "+".join(
        rf"\left[{tex(s.primitive)}\right]_{{{tex(s.lo)}}}^{{{tex(s.hi)}}}" for s in strips
    )
    visual = plot(
        "Bounded integration region",
        "The plotted boundaries and strip endpoints use "
        "the computed intersections for this problem.",
        strip_paths(strips, variable),
    )
    built = finish(
        r"\text{Find the area of the specified bounded region: }" + statement,
        FormulaAnswer(value),
        method,
        rf"A={integrals}={bounds}={tex(value)}.",
    )
    return replace(built, visual=visual)


def parabola_and_line(a: int, b: int, c: int) -> Built:
    upper, lower = a * X - b * X**2, -c * X
    end = sp.Rational(a + c, b)
    primitive = (a + c) * X**2 / 2 - b * X**3 / 3
    return region(
        rf"y={tex(upper)},\quad y={tex(lower)},\quad 0\le x\le {tex(end)}.",
        (Strip(0, end, lower, upper, primitive),),
        rf"{tex(upper - lower)}=x({a + c}-{b}x)\ge0\text{{ between its two roots.}}",
    )


def two_parabolas_and_ray(a: int, b: int, c: int) -> Built:
    low = a * X**2
    high = (a + b) * X**2
    ray = c * X
    first, last = sp.Rational(c, a + b), sp.Rational(c, a)
    return region(
        rf"y={tex(low)},\quad y={tex(high)},\quad y={tex(ray)}.\quad"
        r"\text{Use the region bounded by both parabolas from the "
        r"origin and the ray between its positive intersections.}",
        (
            Strip(0, first, low, high, b * X**3 / 3),
            Strip(first, last, low, ray, c * X**2 / 2 - a * X**3 / 3),
        ),
        rf"x_1={tex(first)},\quad x_2={tex(last)}.\quad"
        r"\text{The upper boundary changes at the first intersection.}",
    )


def inverse_square_and_line(a: int, b: int, c: int) -> Built:
    top = a + b + 1
    left, right = a / sp.sqrt(Y), a * Y
    primitive = a * Y**2 / 2 - 2 * a * sp.sqrt(Y)
    return region(
        rf"y=\frac{{{a * a}}}{{x^2}},\quad y=\frac x{{{a}}},\quad y={top},\quad x>0.",
        (Strip(1, top, left, right, primitive),),
        rf"x={tex(left)}\text{{ on the left, }}x={tex(right)}"
        rf"\text{{ on the right. Their intersection has }}y=1.",
        variable=Y,
    )


def rational_cap_and_horizontal(a: int, b: int, c: int) -> Built:
    radius = a + b
    upper = c * radius**2 / (X**2 + a**2)
    lower = sp.Integer(c)
    end = sp.sqrt(radius**2 - a**2)
    primitive = sp.Rational(c * radius**2, a) * sp.atan(X / a) - c * X
    return region(
        rf"y={tex(upper)},\quad y={c}.",
        (Strip(-end, end, lower, upper, primitive),),
        rf"x=\pm{tex(end)}.\quad\text{{The rational curve "
        rf"is above the line between these intersections.}}",
    )


def exponential_and_horizontal(a: int, b: int, c: int) -> Built:
    base = b + 1
    ceiling = base**a
    exponential = base**X
    return region(
        rf"y={tex(exponential)},\quad y={ceiling},\quad x=0.",
        (Strip(0, a, exponential, sp.Integer(ceiling), ceiling * X - exponential / sp.log(base)),),
        rf"{base}^x={ceiling}\Longrightarrow x={a}.\quad"
        rf"\text{{Use the horizontal line as the upper boundary.}}",
    )


def sine_lobe_area(a: int, b: int, c: int) -> Built:
    theta = sp.pi / (c + 3)
    level = a * sp.sin(theta)
    upper = a * sp.sin(b * X)
    return region(
        rf"y={tex(upper)},\quad y={tex(level)}.\quad"
        rf"\text{{Use the central region where }}{tex(theta)}\le {b}x\le\pi-{tex(theta)}.",
        (
            Strip(
                theta / b,
                (sp.pi - theta) / b,
                level,
                upper,
                -sp.Rational(a, b) * sp.cos(b * X) - level * X,
            ),
        ),
        rf"\sin({b}x)=\sin({tex(theta)})\text{{ at both "
        rf"endpoints. The sine curve is above the line inside.}}",
    )


def meeting_root_arcs(a: int, b: int, c: int) -> Built:
    span = c + 1
    intersection = sp.Rational(b * b * span, a * a + b * b)
    first = a * sp.sqrt(X)
    second = b * sp.sqrt(span - X)
    return region(
        rf"y={tex(first)},\quad y={tex(second)},\quad y=0,\quad 0\le x\le{span}.",
        (
            Strip(0, intersection, sp.S.Zero, first, 2 * a * X ** sp.Rational(3, 2) / 3),
            Strip(
                intersection, span, sp.S.Zero, second, -2 * b * (span - X) ** sp.Rational(3, 2) / 3
            ),
        ),
        rf"{a * a}x={b * b}({span}-x)\Longrightarrow x={tex(intersection)}.\quad"
        r"\text{The two upper boundary arcs meet there.}",
    )


def inverse_fourth_between_levels(a: int, b: int, c: int) -> Built:
    upper_level = (b + 1) ** 4
    half_width = a * Y ** (-sp.Rational(1, 4))
    return region(
        rf"yx^4={a**4},\quad y=1,\quad y={upper_level}.\quad"
        r"\text{Use the central region between the negative and positive branches.}",
        (
            Strip(
                1,
                upper_level,
                -half_width,
                half_width,
                sp.Rational(8 * a, 3) * Y ** sp.Rational(3, 4),
            ),
        ),
        rf"x=\pm{tex(half_width)}.\quad\text{{A horizontal "
        rf"strip has width }}{tex(2 * half_width)}.",
        variable=Y,
    )


def logarithmic_arch(a: int, b: int, c: int) -> Built:
    span = a + b + 2
    center = sp.Rational(span, 2)
    first = c * sp.log(X)
    second = c * sp.log(span - X)
    return region(
        rf"y={tex(first)},\quad y={tex(second)},\quad y=0.\quad"
        r"\text{Use the region above the axis and below both curves.}",
        (
            Strip(1, center, sp.S.Zero, first, c * (X * sp.log(X) - X)),
            Strip(
                center,
                span - 1,
                sp.S.Zero,
                second,
                -c * ((span - X) * sp.log(span - X) - (span - X)),
            ),
        ),
        rf"x=1,\quad x={span - 1},\quad x={tex(center)}"
        rf"\text{{ are the intercepts and curve intersection.}}",
    )


def root_sum_with_axes(a: int, b: int, c: int) -> Built:
    upper = b * (c - sp.sqrt(X / a)) ** 2
    end = a * c * c
    primitive = b * (
        c * c * X - sp.Rational(4 * c, 3) * X ** sp.Rational(3, 2) / sp.sqrt(a) + X**2 / (2 * a)
    )
    return region(
        rf"\sqrt{{x/{a}}}+\sqrt{{y/{b}}}={c},\quad x\ge0,\quad y\ge0.",
        (Strip(0, end, sp.S.Zero, upper, primitive),),
        rf"y={tex(upper)},\quad 0\le x\le{end}.\quad\text{{The "
        rf"intercepts determine the bounded first-quadrant region.}}",
    )


def parabola_and_rational_cap(a: int, b: int, c: int) -> Built:
    divisor = a + 1
    height = sp.Rational(b * b * (b * b + c * c), divisor)
    lower = X**2 / divisor
    upper = height / (X**2 + c * c)
    primitive = height * sp.atan(X / c) / c - X**3 / (3 * divisor)
    return region(
        rf"y={tex(lower)},\quad y={tex(upper)}.",
        (Strip(-b, b, lower, upper, primitive),),
        rf"x^2(x^2+{c * c})={tex(height * divisor)}.\quad"
        rf"\text{{The real intersections are }}x=\pm{b}"
        rf"\text{{; the rational curve is higher between them.}}",
    )


def logarithm_and_two_lines(a: int, b: int, c: int) -> Built:
    lo, hi = sp.exp(-a), sp.exp(b)
    primitive = X * sp.log(X) + (a - 1) * X
    return region(
        rf"y=\ln x,\quad y=-{a},\quad x=e^{{{b}}}.",
        (Strip(lo, hi, sp.Integer(-a), sp.log(X), primitive),),
        rf"\ln x=-{a}\Longrightarrow x=e^{{-{a}}}.\quad\text{{The "
        rf"logarithm is above the horizontal boundary.}}",
    )


def circle_between_horizontal_lines(a: int, b: int, c: int) -> Built:
    radius = a + b + c
    half_width = sp.sqrt(radius**2 - Y**2)
    primitive = Y * half_width + radius**2 * sp.asin(Y / radius)
    return region(
        rf"y=\sqrt{{{radius**2}-x^2}},\quad y={a},\quad y={a + b}.\quad"
        r"\text{Include the full strip between the left and right circle arcs.}",
        (Strip(a, a + b, -half_width, half_width, primitive),),
        rf"x=\pm\sqrt{{{radius**2}-y^2}}.\quad\text{{Integrate the horizontal width.}}",
        variable=Y,
    )


def two_exponentials_and_level(a: int, b: int, c: int) -> Built:
    base = b + 1
    high = base ** (2 * (1 + a % 2))
    lower = sp.log(Y) / (2 * sp.log(base))
    upper = sp.log(Y) / sp.log(base)
    primitive = (Y * sp.log(Y) - Y) / (2 * sp.log(base))
    return region(
        rf"y={base}^x,\quad y={base**2}^x,\quad y={high}.\quad y\ge1.",
        (Strip(1, high, lower, upper, primitive),),
        rf"\text{{The curves meet at }}(0,1).\quad x_1={tex(lower)},\quad x_2={tex(upper)}.",
        variable=Y,
    )


def unbounded_tangent_cotangent(a: int, b: int, c: int) -> Built:
    end = sp.pi / (2 * b)
    crossing = sp.atan(sp.sqrt(sp.Rational(c, a))) / b
    visual = plot(
        "Unbounded area between tangent curves",
        "The branches continue toward vertical poles at "
        "both ends. The plotted window truncates them.",
        [
            path(
                "Scaled tangent",
                float(end) / 40,
                float(end) * 39 / 40,
                lambda x: a * math.tan(b * x),
            ),
            path(
                "Scaled cotangent",
                float(end) / 40,
                float(end) * 39 / 40,
                lambda x: c / math.tan(b * x),
            ),
        ],
        [point("Intersection", float(crossing), math.sqrt(a * c), included=True)],
    )
    built = finish(
        rf"\text{{Find the total area between }}y={a}\tan({b}x)\text{{ and }}"
        rf"y={c}\cot({b}x)\text{{ on }}0<x<{tex(end)}\text{{. Enter inf if the area diverges.}}",
        LimitAnswer(sp.oo),
        rf"x_0={tex(crossing)}\text{{ is the only intersection. "
        rf"The endpoint poles make the area improper.}}",
        rf"\int_0^{{x_0}}\left({c}\cot({b}x)-{a}\tan({b}x)\right)dx"
        rf"=\lim_{{\varepsilon\to0^+}}\left[\frac{{{c}}}{{{b}}}\ln\sin({b}x)"
        rf"+\frac{{{a}}}{{{b}}}\ln\cos({b}x)\right]_\varepsilon^{{x_0}}=\infty.",
    )
    return replace(built, visual=visual)


def arc(
    curve: sp.Expr,
    derivative: sp.Expr,
    speed: sp.Expr,
    primitive: sp.Expr,
    lo: sp.Expr | int,
    hi: sp.Expr | int,
    method: str,
) -> Built:
    value = exact_difference(primitive, X, lo, hi)
    function = sp.lambdify(X, curve, "math")
    visual = plot(
        "Arc-length integration interval",
        "The curve segment and endpoints use the same parameters as the length integral.",
        [path("Curve segment", float(lo), float(hi), function)],
        [
            point("Start", float(lo), float(function(float(lo))), included=True),
            point("End", float(hi), float(function(float(hi))), included=True),
        ],
    )
    built = finish(
        rf"\text{{Find the arc length of }}y={tex(curve)}\text{{ for }}{tex(lo)}\le x\le{tex(hi)}.",
        FormulaAnswer(value),
        method,
        rf"y'={tex(derivative)},\quad L=\int_{{{tex(lo)}}}^{{{tex(hi)}}}\sqrt{{1+(y')^2}}\,dx"
        rf"=\int_{{{tex(lo)}}}^{{{tex(hi)}}}{tex(speed)}\,dx"
        rf"=\left[{tex(primitive)}\right]_{{{tex(lo)}}}^{{{tex(hi)}}}={tex(value)}.",
    )
    return replace(built, visual=visual)


def logarithmic_exponential_arc(a: int, b: int, c: int) -> Built:
    exponential = sp.exp(a * X)
    curve = sp.log((exponential + 1) / (exponential - 1)) / a
    derivative = -2 * exponential / (exponential**2 - 1)
    speed = (exponential**2 + 1) / (exponential**2 - 1)
    primitive = (sp.log(exponential - sp.exp(-a * X))) / a
    return arc(
        curve,
        derivative,
        speed,
        primitive,
        b,
        b + c,
        r"\text{On the positive interval, the square root "
        r"simplifies to the positive hyperbolic cotangent.}",
    )


def parabola_arc(a: int, b: int, c: int) -> Built:
    speed = sp.sqrt(1 + 4 * a * a * X**2)
    primitive = X * speed / 2 + sp.log(2 * a * X + speed) / (4 * a)
    return arc(
        a * X**2 + c,
        2 * a * X,
        speed,
        primitive,
        0,
        b,
        rf"t={2 * a}x\text{{ reduces the length to the "
        rf"standard }}\sqrt{{1+t^2}}\text{{ integral.}}",
    )


def three_halves_power_arc(a: int, b: int, c: int) -> Built:
    speed = sp.sqrt(1 + sp.Rational(9 * a * a, 4) * X)
    primitive = sp.Rational(8, 27 * a * a) * (1 + sp.Rational(9 * a * a, 4) * X) ** sp.Rational(
        3, 2
    )
    return arc(
        a * X ** sp.Rational(3, 2),
        sp.Rational(3 * a, 2) * sp.sqrt(X),
        speed,
        primitive,
        0,
        b + c,
        rf"t=1+\frac{{{9 * a * a}}}4x\text{{ turns the "
        rf"arc-length integral into a power integral.}}",
    )


def exponential_arc(a: int, b: int, c: int) -> Built:
    exponential = sp.exp(c * X)
    speed = sp.sqrt(1 + exponential**2)
    primitive = (speed + sp.log(exponential / (1 + speed))) / c
    return arc(
        exponential / c,
        exponential,
        speed,
        primitive,
        sp.log(a) / c,
        sp.log(a + b) / c,
        r"t=e^{cx}\text{ gives }\int\sqrt{1+t^2}/t\,dt.\quad"
        r"\text{Use }t=\sinh u\text{ to obtain }\sqrt{1+t^2}+\ln\frac{t}{1+\sqrt{1+t^2}}.",
    )


def reciprocal_power_arc(a: int, b: int, c: int) -> Built:
    power = 2 + a % 3
    lo = 1 + b % 2
    hi = lo + 1 + c % 2
    curve = X ** (power + 1) / (2 * (power + 1)) + X ** (1 - power) / (2 * (power - 1))
    derivative = (X**power - X ** (-power)) / 2
    speed = (X**power + X ** (-power)) / 2
    primitive = X ** (power + 1) / (2 * (power + 1)) - X ** (1 - power) / (2 * (power - 1))
    return arc(
        curve,
        derivative,
        speed,
        primitive,
        lo,
        hi,
        r"\text{Use }1+\tfrac14(t-t^{-1})^2=\tfrac14(t+t^{-1})^2\text{ with }t=x^m>0.",
    )


def logarithm_cosine_arc(a: int, b: int, c: int) -> Built:
    theta = sp.pi / (b + 3)
    cosine = sp.cos(a * X)
    primitive = sp.log((1 + sp.sin(a * X)) / cosine) / a
    return arc(
        (c - sp.log(cosine)) / a,
        sp.tan(a * X),
        1 / cosine,
        primitive,
        0,
        theta / a,
        r"\sqrt{1+\tan^2u}=\sec u\text{ on this interval. Integrate using }\ln(\sec u+\tan u).",
    )


def spring_work(a: int, b: int, c: int) -> Built:
    stiffness = 10 * a
    extension = sp.Rational(c, 10)
    natural_length = sp.Rational(b, 10)
    value = stiffness * extension**2 / 2
    visual = plot(
        "Spring force and extension",
        "Work is the triangular area under the linear force curve up to the final extension.",
        [
            path("Force", 0, float(extension), lambda x: stiffness * x),
            {
                "label": "Final extension",
                "points": [[float(extension), 0], [float(extension), float(stiffness * extension)]],
            },
        ],
    )
    visual.update(xLabel="Extension (m)", yLabel="Force (N)")
    built = finish(
        rf"\text{{A spring has stiffness }}{stiffness}\,\mathrm{{N/m}}\text{{ and natural length }}"
        rf"{tex(natural_length)}\,\mathrm m\text{{. Find the work in joules to stretch it to }}"
        rf"{tex(natural_length + extension)}\,\mathrm m.",
        FormulaAnswer(value),
        rf"s=L-l={tex(extension)}\,\mathrm m,\quad F(s)={stiffness}s.",
        rf"W=\int_0^{{{tex(extension)}}}{stiffness}s\,ds"
        rf"=\left[\frac{{{stiffness}s^2}}2\right]_0^{{{tex(extension)}}}={tex(value)}\,\mathrm J.",
    )
    return replace(built, visual=visual)


def horizontal_tank_work(a: int, b: int, c: int) -> Built:
    radius = a
    length = b + c
    gravity = sp.Rational(981, 100)
    weight = 1000 * gravity
    value = weight * length * sp.pi * radius**3
    circumference = {
        "label": "Tank cross section",
        "points": [
            [radius * math.cos(2 * math.pi * k / 64), radius * math.sin(2 * math.pi * k / 64)]
            for k in range(65)
        ],
        "closed": True,
    }
    visual = plot(
        "Horizontal cylindrical tank",
        f"Radius {radius} m and length {length} m. A slice "
        f"at height y is lifted to the outlet at y = {radius}.",
        [
            circumference,
            {"label": "Lift from the centre", "points": [[0, 0], [0, radius]], "arrow": True},
            {"label": "Middle water slice", "points": [[-radius, 0], [radius, 0]]},
        ],
    )
    built = finish(
        rf"\text{{A full horizontal cylindrical water tank has radius }}{radius}\,\mathrm m"
        rf"\text{{ and length }}{length}\,\mathrm m\text{{. "
        rf"Pump all water to an outlet at its top.}}"
        rf"\text{{ Use density }}1000\,\mathrm{{kg/m^3}}"
        rf"\text{{ and }}g={tex(gravity)}\,\mathrm{{m/s^2}}"
        r"\text{. Find the work in joules.}",
        FormulaAnswer(value),
        rf"dV={2 * length}\sqrt{{{radius**2}-y^2}}\,dy,\quad\text{{lift distance }}={radius}-y.",
        rf"W={tex(weight)}\int_{{-{radius}}}^{{{radius}}}({radius}-y){2 * length}"
        rf"\sqrt{{{radius**2}-y^2}}\,dy."
        rf"\quad\text{{The odd term integrates to zero and "
        rf"the remaining integral is a semicircle area.}}"
        rf"\quad W={tex(weight)}\cdot{length}\cdot\pi\cdot{radius**3}={tex(value)}\,\mathrm J.",
    )
    return replace(built, visual=visual)


def two_phase_motion(a: int, b: int, c: int) -> Built:
    initial = a + b * c
    acceleration = a
    duration = b
    deceleration = b
    second_duration = c
    join_velocity = initial + acceleration * duration
    first = initial * duration + sp.Rational(acceleration * duration**2, 2)
    second = join_velocity * second_duration - sp.Rational(deceleration * second_duration**2, 2)
    value = first + second
    visual = plot(
        "Velocity during both motion phases",
        "The two linear velocity segments meet at the "
        "phase change. Their signed area gives displacement.",
        [
            path("Acceleration", 0, duration, lambda t: initial + acceleration * t),
            path(
                "Deceleration",
                duration,
                duration + second_duration,
                lambda t: join_velocity - deceleration * (t - duration),
            ),
        ],
        [point("Phase change", duration, join_velocity, included=True)],
    )
    visual.update(xLabel="Time (s)", yLabel="Velocity (m/s)")
    built = finish(
        rf"\text{{A particle starts at }}x=0\text{{ with velocity }}{initial}\,\mathrm{{m/s}}"
        rf"\text{{. It accelerates at }}{acceleration}\,"
        rf"\mathrm{{m/s^2}}\text{{ for }}{duration}\,\mathrm s"
        rf"\text{{, then at }}-{deceleration}\,\mathrm{{m/s^2}}"
        rf"\text{{ for }}{second_duration}\,\mathrm s"
        r"\text{. Find its final position in metres.}",
        FormulaAnswer(value),
        rf"v_1(t)={initial}+{acceleration}t,\quad v_2(s)={join_velocity}-{deceleration}s."
        rf"\quad v_2({second_duration})={join_velocity - deceleration * second_duration}>0.",
        rf"x=\int_0^{{{duration}}}({initial}+{acceleration}t)\,dt"
        rf"+\int_0^{{{second_duration}}}({join_velocity}-{deceleration}s)\,ds"
        rf"={tex(first)}+{tex(second)}={tex(value)}\,\mathrm m.",
    )
    return replace(built, visual=visual)


def approaching_particles(a: int, b: int, c: int) -> Built:
    time = a + 1
    distance = (a + b) * time**2 + c * time**4
    visual = plot(
        "Separation until the collision",
        "The separation decreases to zero. The relative speed is positive after time zero.",
        [path("Separation", 0, time, lambda t: distance - (a + b) * t * t - c * t**4)],
        [point("Collision", time, 0, included=True)],
    )
    visual.update(xLabel="Time (s)", yLabel="Separation (m)")
    built = finish(
        rf"\text{{Two particles initially }}{distance}\,"
        rf"\mathrm m\text{{ apart move toward each other}}"
        rf"\text{{ with speeds }}v_1(t)={2 * a}t+{4 * c}t^3\text{{ and }}v_2(t)={2 * b}t"
        r"\text{ in metres per second for }t\ge0\text{. Find their collision time in seconds.}",
        FormulaAnswer(sp.Integer(time)),
        rf"\int_0^t(v_1+v_2)\,ds={a + b}t^2+{c}t^4.\quad u=t^2\ge0.",
        rf"{c}u^2+{a + b}u-{distance}=0\Longrightarrow"
        rf"u=\frac{{-{a + b}+\sqrt{{{(a + b) ** 2 + 4 * c * distance}}}}}{{{2 * c}}}={time**2}."
        rf"\quad t={time}\,\mathrm s.\quad\text{{The travelled "
        rf"separation is strictly increasing for }}t>0.",
    )
    return replace(built, visual=visual)


def root_line_axis_exam(a: int, b: int, c: int) -> Built:
    intercept = a + b * a * a
    upper = intercept - b * X
    lower = sp.sqrt(X)
    return region(
        rf"y=\sqrt x,\quad y={tex(upper)},\quad x=0,\quad 0\le x\le{a * a}.",
        (
            Strip(
                0,
                a * a,
                lower,
                upper,
                intercept * X - b * X**2 / 2 - sp.Rational(2, 3) * X ** sp.Rational(3, 2),
            ),
        ),
        rf"t=\sqrt x\ge0:\quad {b}t^2+t-{intercept}=0\Longrightarrow t={a},\quad x={a * a}.",
    )


def sideways_parabola_line_exam(a: int, b: int, c: int) -> Built:
    intercept = a * (a + 1)
    upper = intercept - Y
    lower = Y**2
    return region(
        rf"x=y^2,\quad x+y={intercept}.",
        (Strip(-a - 1, a, lower, upper, intercept * Y - Y**2 / 2 - Y**3 / 3),),
        rf"y^2+y-{intercept}=(y-{a})(y+{a + 1})=0.\quad\text{{The line is the right boundary.}}",
        variable=Y,
    )


def two_parabolas_exam(a: int, b: int, c: int) -> Built:
    lower = b * X**2 - c * X
    height = b + c
    difference = height * (X + a) * (c - X)
    upper = sp.expand(lower + difference)
    primitive = height * (-(X**3) / 3 + (c - a) * X**2 / 2 + a * c * X)
    return region(
        rf"y={tex(lower)},\quad y={tex(upper)}.",
        (Strip(-a, c, lower, upper, primitive),),
        rf"y_{{upper}}-y_{{lower}}={tex(difference)}\ge0\quad\text{{for }}-{a}\le x\le{c}.",
    )


def parabola_tangent_axes_exam(a: int, b: int, c: int) -> Built:
    contact = a + c
    parabola = b * (X**2 + c * c)
    tangent = 2 * b * contact * X + b * (c * c - contact**2)
    intercept = sp.Rational(contact**2 - c * c, 2 * contact)
    parabola_primitive = b * (X**3 / 3 + c * c * X)
    tangent_primitive = b * contact * X**2 + b * (c * c - contact**2) * X
    return region(
        rf"y={tex(parabola)},\quad\text{{its tangent at }}x={contact},\quad x=0,\quad y=0."
        r"\quad\text{Use the first-quadrant region under "
        r"the parabola and above the axis or tangent.}",
        (
            Strip(0, intercept, sp.S.Zero, parabola, parabola_primitive),
            Strip(intercept, contact, tangent, parabola, parabola_primitive - tangent_primitive),
        ),
        rf"y_{{tan}}={tex(tangent)},\quad x_{{intercept}}={tex(intercept)}.\quad"
        r"\text{The lower boundary changes from the axis to the tangent there.}",
    )


def cubic_tangent_axis_exam(a: int, b: int, c: int) -> Built:
    curve = a * X**3
    tangent = 3 * a * b * b * X - 2 * a * b**3
    return region(
        rf"y={tex(curve)},\quad\text{{its tangent at }}x={b},\quad x=0,\quad 0\le x\le{b}.",
        (
            Strip(
                0,
                b,
                tangent,
                curve,
                a * X**4 / 4 - sp.Rational(3 * a * b * b, 2) * X**2 + 2 * a * b**3 * X,
            ),
        ),
        rf"y_{{tan}}={tex(tangent)},\quad y-y_{{tan}}={a}(x-{b})^2(x+{2 * b})"
        rf"\ge0\text{{ on the stated interval.}}",
    )


def logarithm_and_square_exam(a: int, b: int, c: int) -> Built:
    lower = b * sp.log(X) ** 2
    upper = a * sp.log(X)
    primitive = a * (X * sp.log(X) - X) - b * X * (sp.log(X) ** 2 - 2 * sp.log(X) + 2)
    return region(
        rf"y={tex(upper)},\quad y={tex(lower)}.",
        (Strip(1, sp.exp(sp.Rational(a, b)), lower, upper, primitive),),
        rf"\ln x=0\text{{ or }}\ln x={tex(sp.Rational(a, b))}.\quad"
        r"\text{Between these intersections the linear "
        r"logarithm is above its quadratic counterpart.}",
    )
