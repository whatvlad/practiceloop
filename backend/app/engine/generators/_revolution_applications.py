"""Volumes and lateral surfaces of revolution with their generating profiles (#270)."""

from dataclasses import replace
from typing import Any

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.blocks.analysis_one import X
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._integral_applications import Strip, exact_difference, strip_paths
from app.engine.generators._limit_visuals import path, plot
from app.engine.generators._sequence_limits import finish


def rotation_visual(
    paths: list[dict[str, Any]], axis: str, coordinate: sp.Expr | int = 0
) -> dict[str, Any]:
    points = [point for curve in paths for point in curve["points"]]
    xs, ys = zip(*points, strict=True)
    position = float(coordinate)
    axis_points = (
        [[min(xs), position], [max(xs), position]]
        if axis == "horizontal"
        else [[position, min(ys)], [position, max(ys)]]
    )
    return plot(
        "Generating profile and rotation axis",
        "The generating curve or region and its rotation "
        "axis use the same parameters as the integral.",
        [*paths, {"label": "Rotation axis", "points": axis_points}],
    )


def volume(
    statement: str,
    strips: tuple[Strip, ...],
    integrand: sp.Expr,
    primitive: sp.Expr,
    lo: sp.Expr | int,
    hi: sp.Expr | int,
    method: str,
    *,
    axis: str = "horizontal",
    coordinate: sp.Expr | int = 0,
) -> Built:
    value = exact_difference(primitive, X, lo, hi)
    visual = rotation_visual(strip_paths(strips), axis, coordinate)
    built = finish(
        r"\text{Find the volume of the solid obtained by rotating the region }" + statement,
        FormulaAnswer(value),
        method,
        rf"V=\int_{{{tex(lo)}}}^{{{tex(hi)}}}{tex(integrand)}\,dx"
        rf"=\left[{tex(primitive)}\right]_{{{tex(lo)}}}^{{{tex(hi)}}}={tex(value)}.",
    )
    return replace(built, visual=visual)


def parabolic_disc_volume(a: int, b: int, c: int) -> Built:
    f = a * X * (b - X)
    integrand = sp.pi * f**2
    primitive = sp.pi * a * a * (b * b * X**3 / 3 - b * X**4 / 2 + X**5 / 5)
    return volume(
        rf"0\le x\le{b},\quad 0\le y\le{tex(f)}\text{{ about the }}x\text{{-axis.}}",
        (Strip(0, b, sp.S.Zero, f, sp.S.Zero),),
        integrand,
        primitive,
        0,
        b,
        rf"R(x)={tex(f)}\ge0,\quad A(x)=\pi R(x)^2.\quad\text{{Use discs.}}",
    )


def reciprocal_root_shell_volume(a: int, b: int, c: int) -> Built:
    height = (a + 1) / sp.sqrt(X**2 + b * b)
    primitive = 2 * sp.pi * (a + 1) * sp.sqrt(X**2 + b * b)
    return volume(
        rf"0\le x\le{c},\quad 0\le y\le{tex(height)}\text{{ about the }}y\text{{-axis.}}",
        (Strip(0, c, sp.S.Zero, height, sp.S.Zero),),
        2 * sp.pi * X * height,
        primitive,
        0,
        c,
        rf"r=x,\quad h={tex(height)},\quad dV=2\pi rh\,dx.\quad u=x^2+{b * b}.",
        axis="vertical",
    )


def tangent_disc_volume(a: int, b: int, c: int) -> Built:
    theta = sp.pi / (b + 3)
    end = theta / c
    f = a * sp.tan(c * X)
    primitive = sp.pi * a * a * (sp.tan(c * X) / c - X)
    return volume(
        rf"0\le x\le{tex(end)},\quad 0\le y\le{tex(f)}\text{{ about the }}x\text{{-axis.}}",
        (Strip(0, end, sp.S.Zero, f, sp.S.Zero),),
        sp.pi * f**2,
        primitive,
        0,
        end,
        r"\text{Use discs and }\tan^2u=\sec^2u-1\text{. The interval ends before the pole.}",
    )


def power_root_shell_volume(a: int, b: int, c: int) -> Built:
    lower = a * X**2 / b**2
    upper = a * sp.sqrt(X / b)
    primitive = (
        2
        * sp.pi
        * a
        * (sp.Rational(2, 5) * X ** sp.Rational(5, 2) / sp.sqrt(b) - X**4 / (4 * b * b))
    )
    return volume(
        rf"0\le x\le{b},\quad {tex(lower)}\le y\le{tex(upper)}\text{{ about the }}y\text{{-axis.}}",
        (Strip(0, b, lower, upper, sp.S.Zero),),
        2 * sp.pi * X * (upper - lower),
        primitive,
        0,
        b,
        r"\text{The curves meet at the two endpoints. Use shells "
        r"of radius }x\text{ and the vertical height difference.}",
        axis="vertical",
    )


def cubic_shell_volume(a: int, b: int, c: int) -> Built:
    upper = a * X**3
    primitive = 2 * sp.pi * a * X**5 / 5
    return volume(
        rf"0\le x\le{b},\quad 0\le y\le{tex(upper)}\text{{ about the }}y\text{{-axis.}}",
        (Strip(0, b, sp.S.Zero, upper, sp.S.Zero),),
        2 * sp.pi * a * X**4,
        primitive,
        0,
        b,
        rf"r=x,\quad h={tex(upper)},\quad dV=2\pi rh\,dx.",
        axis="vertical",
    )


def reciprocal_shell_volume(a: int, b: int, c: int) -> Built:
    height = a / X
    primitive = 2 * sp.pi * a * X
    return volume(
        rf"{b}\le x\le{b + c},\quad 0\le y\le{tex(height)}\text{{ about the }}y\text{{-axis.}}",
        (Strip(b, b + c, sp.S.Zero, height, sp.S.Zero),),
        2 * sp.pi * a,
        primitive,
        b,
        b + c,
        rf"r=x,\quad h={tex(height)},\quad 2\pi rh={tex(2 * sp.pi * a)}.\quad\text{{Use shells.}}",
        axis="vertical",
    )


def line_reciprocal_washers(a: int, b: int, c: int) -> Built:
    lo = a
    hi = a + b
    product = lo * hi
    total = lo + hi
    lower = product / X
    upper = total - X
    primitive = sp.pi * ((X - total) ** 3 / 3 + product**2 / X)
    return volume(
        rf"{lo}\le x\le{hi},\quad {tex(lower)}\le y"
        rf"\le{tex(upper)}\text{{ about the }}x\text{{-axis.}}",
        (Strip(lo, hi, lower, upper, sp.S.Zero),),
        sp.pi * (upper**2 - lower**2),
        primitive,
        lo,
        hi,
        rf"R={tex(upper)},\quad r={tex(lower)},\quad A=\pi(R^2-r^2).\quad"
        rf"\text{{The intersections solve }}(x-{lo})(x-{hi})=0.",
    )


def sine_cosine_disc_volume(a: int, b: int, c: int) -> Built:
    f = a * sp.sin(b * X) * sp.cos(b * X)
    end = sp.pi / (2 * b)
    primitive = sp.pi * a * a * (X / 8 - sp.sin(4 * b * X) / (32 * b))
    return volume(
        rf"0\le x\le{tex(end)},\quad 0\le y\le{tex(f)}\text{{ about the }}x\text{{-axis.}}",
        (Strip(0, end, sp.S.Zero, f, sp.S.Zero),),
        sp.pi * f**2,
        primitive,
        0,
        end,
        r"\text{Use discs and }\sin^2u\cos^2u=(1-\cos4u)/8.",
    )


def sine_shifted_horizontal_volume(a: int, b: int, c: int) -> Built:
    axis = a + c
    f = a * sp.sin(b * X)
    end = sp.pi / b
    primitive = sp.pi * (
        -2 * axis * a * sp.cos(b * X) / b - a * a * (X / 2 - sp.sin(2 * b * X) / (4 * b))
    )
    return volume(
        rf"0\le x\le{tex(end)},\quad 0\le y\le{tex(f)}\text{{ about }}y={axis}.",
        (Strip(0, end, sp.S.Zero, f, sp.S.Zero),),
        sp.pi * (axis**2 - (axis - f) ** 2),
        primitive,
        0,
        end,
        rf"R={axis},\quad r={axis}-{tex(f)}\ge{c}>0.\quad A=\pi(R^2-r^2).",
        coordinate=axis,
    )


def parabola_shifted_vertical_volume(a: int, b: int, c: int) -> Built:
    coordinate = b + c
    f = a * X * (b - X)
    primitive = 2 * sp.pi * a * (coordinate * b * X**2 / 2 - (coordinate + b) * X**3 / 3 + X**4 / 4)
    return volume(
        rf"0\le x\le{b},\quad 0\le y\le{tex(f)}\text{{ about }}x={coordinate}.",
        (Strip(0, b, sp.S.Zero, f, sp.S.Zero),),
        2 * sp.pi * (coordinate - X) * f,
        primitive,
        0,
        b,
        rf"r={coordinate}-x\ge{c}>0,\quad h={tex(f)}.\quad\text{{Use cylindrical shells.}}",
        axis="vertical",
        coordinate=coordinate,
    )


def surface(
    curve: sp.Expr,
    derivative: sp.Expr,
    lo: sp.Expr | int,
    hi: sp.Expr | int,
    simplified_density: sp.Expr,
    primitive: sp.Expr,
    method: str,
    *,
    axis: str = "horizontal",
) -> Built:
    value = exact_difference(primitive, X, lo, hi)
    function = sp.lambdify(X, curve, "math")
    visual = rotation_visual([path("Generating curve", float(lo), float(hi), function)], axis)
    radius = curve if axis == "horizontal" else X
    axis_tex = "x" if axis == "horizontal" else "y"
    built = finish(
        rf"\text{{Find the lateral surface area obtained by rotating }}y={tex(curve)}"
        rf"\text{{ for }}{tex(lo)}\le x\le{tex(hi)}\text{{ about the }}{axis_tex}\text{{-axis.}}"
        r"\text{ Include the surface traced by the curve only.}",
        FormulaAnswer(value),
        method,
        rf"y'={tex(derivative)},\quad r={tex(radius)},\quad"
        rf"S=2\pi\int_{{{tex(lo)}}}^{{{tex(hi)}}}r\sqrt{{1+(y')^2}}\,dx"
        rf"=\int_{{{tex(lo)}}}^{{{tex(hi)}}}{tex(simplified_density)}\,dx"
        rf"=\left[{tex(primitive)}\right]_{{{tex(lo)}}}^{{{tex(hi)}}}={tex(value)}.",
    )
    return replace(built, visual=visual)


def cosine_surface(a: int, b: int, c: int) -> Built:
    curve = sp.Rational(a, b) * sp.cos(b * X)
    u = a * sp.sin(b * X)
    primitive = sp.pi * (u * sp.sqrt(1 + u * u) + sp.log(u + sp.sqrt(1 + u * u))) / b**2
    return surface(
        curve,
        -a * sp.sin(b * X),
        0,
        sp.pi / (2 * b),
        2 * sp.pi * curve * sp.sqrt(1 + a * a * sp.sin(b * X) ** 2),
        primitive,
        rf"t={tex(u)},\quad dt={a * b}\cos({b}x)\,dx.\quad"
        r"\int\sqrt{1+t^2}\,dt=\tfrac12(t\sqrt{1+t^2}+\ln(t+\sqrt{1+t^2})).",
    )


def square_root_surface(a: int, b: int, c: int) -> Built:
    q = X + a * a
    curve = sp.sqrt(q)
    primitive = sp.pi * (4 * q + 1) ** sp.Rational(3, 2) / 6
    return surface(
        curve,
        1 / (2 * curve),
        -a * a,
        b + c,
        sp.pi * sp.sqrt(4 * q + 1),
        primitive,
        r"\text{The radius cancels the denominator inside the arc-length "
        r"factor. Use the right-hand limit at the initial endpoint.}",
    )


def logarithm_vertical_surface(a: int, b: int, c: int) -> Built:
    speed = sp.sqrt(X**2 + a * a)
    primitive = sp.pi * (X * speed + a * a * sp.log(X + speed))
    return surface(
        a * sp.log(X),
        a / X,
        1,
        sp.sqrt(b + c),
        2 * sp.pi * speed,
        primitive,
        r"x>0\text{, so }x\sqrt{1+a^2/x^2}=\sqrt{x^2+a^2}.\quad"
        r"\text{Use the standard square-root primitive.}",
        axis="vertical",
    )


def corner_vertical_surface(a: int, b: int, c: int) -> Built:
    speed = sp.sqrt(1 + a * a)
    return surface(
        a * sp.Abs(X - b) + c,
        a * sp.sign(X - b),
        0,
        2 * b,
        2 * sp.pi * X * speed,
        sp.pi * speed * X**2,
        rf"y'=\pm{a}\text{{ on the two smooth segments. The single corner has zero arc length.}}",
        axis="vertical",
    )


def sphere_belt_surface(a: int, b: int, c: int) -> Built:
    radius = a + b
    curve = sp.sqrt(radius**2 - X**2)
    return surface(
        curve,
        -X / curve,
        -a,
        a,
        2 * sp.pi * radius,
        2 * sp.pi * radius * X,
        rf"r\sqrt{{1+(y')^2}}=\sqrt{{{radius**2}-x^2}}"
        rf"\sqrt{{1+\frac{{x^2}}{{{radius**2}-x^2}}}}={radius}.",
    )


def root_cubic_surface(a: int, b: int, c: int) -> Built:
    u = a * X
    lo = sp.Rational(b + 3, 4)
    curve = sp.sqrt(u) * (1 - u / 3) / a
    primitive = sp.pi * (-(u**3) / 9 + u * u / 3 + u) / a**2
    return surface(
        curve,
        (1 - u) / (2 * sp.sqrt(u)),
        lo / a,
        sp.Rational(3, a),
        sp.pi * (1 - u / 3) * (u + 1) / a,
        primitive,
        rf"u={a}x>0,\quad 1+(y')^2=\frac{{(u+1)^2}}{{4u}}.\quad"
        r"\text{The radius is nonnegative throughout the interval.}",
    )


def line_vertical_surface(a: int, b: int, c: int) -> Built:
    speed = sp.sqrt(1 + sp.Rational(1, a * a))
    return surface(
        (X - b) / a,
        sp.Rational(1, a),
        b,
        b + c,
        2 * sp.pi * X * speed,
        sp.pi * speed * X**2,
        r"\text{The slope is constant. Multiply its arc-length factor by the radius }x.",
        axis="vertical",
    )


def parabola_vertical_surface(a: int, b: int, c: int) -> Built:
    primitive = sp.Rational(2, 3 * a * a) * sp.pi * (1 + a * a * X**2) ** sp.Rational(3, 2)
    return surface(
        a * X**2 / 2,
        a * X,
        0,
        sp.sqrt(b + c),
        2 * sp.pi * X * sp.sqrt(1 + a * a * X**2),
        primitive,
        rf"t=1+{a * a}x^2,\quad dt={2 * a * a}x\,dx.\quad\text{{Integrate }}\sqrt t.",
        axis="vertical",
    )


def sine_line_volume_exam(a: int, b: int, c: int) -> Built:
    end = sp.pi / (2 * b)
    upper = a * sp.sin(b * X)
    lower = 2 * a * b * X / sp.pi
    primitive = (
        sp.pi * a * a * (X / 2 - sp.sin(2 * b * X) / (4 * b))
        - sp.Rational(4 * a * a * b * b, 3) * X**3 / sp.pi
    )
    return volume(
        rf"0\le x\le{tex(end)},\quad {tex(lower)}\le y\le{tex(upper)}"
        r"\text{ about the }x\text{-axis.}",
        (Strip(0, end, lower, upper, sp.S.Zero),),
        sp.pi * (upper**2 - lower**2),
        primitive,
        0,
        end,
        r"\text{The sine is concave on this interval and "
        r"lies above its endpoint chord. Use washers.}",
    )


def sine_volume_and_surface_exam(a: int, b: int, c: int) -> Built:
    curve = sp.Rational(a, b) * sp.sin(b * X)
    end = sp.pi / b
    volume_value = sp.pi**2 * a * a / (2 * b**3)
    surface_value = 2 * sp.pi * (a * sp.sqrt(1 + a * a) + sp.log(a + sp.sqrt(1 + a * a))) / b**2
    visual = rotation_visual(
        strip_paths((Strip(0, end, sp.S.Zero, curve, sp.S.Zero),)), "horizontal"
    )
    answer = OrderedAnswer(
        (FormulaAnswer(volume_value), FormulaAnswer(surface_value)),
        ("Volume", "Lateral surface area"),
    )
    built = finish(
        rf"\text{{Rotate }}0\le y\le{tex(curve)},\quad0\le x\le{tex(end)}"
        r"\text{ about the }x\text{-axis. Find (volume; lateral surface area).}",
        answer,
        rf"V=\pi\int_0^{{{tex(end)}}}{tex(curve**2)}\,dx.\quad"
        rf"S=2\pi\int_0^{{{tex(end)}}}{tex(curve)}\sqrt{{1+{a * a}\cos^2({b}x)}}\,dx.",
        rf"V={tex(volume_value)}.\quad t={a}\cos({b}x)\text{{ in the surface integral gives }}"
        rf"S=\frac{{2\pi}}{{{b * b}}}\int_{{-{a}}}^{{{a}}}\sqrt{{1+t^2}}\,dt"
        rf"={tex(surface_value)}.",
    )
    return replace(built, visual=visual)


def torus_shell_volume(a: int, b: int, c: int) -> Built:
    minor = a
    major = a + b + c
    height = sp.sqrt(minor**2 - (X - major) ** 2)
    paths = strip_paths((Strip(major - minor, major + minor, -height, height, sp.S.Zero),))
    visual = rotation_visual(paths, "vertical")
    built = finish(
        rf"\text{{A circle of radius }}{minor}\text{{ has centre }}({major},0)"
        r"\text{. Rotate its filled disc about the }y\text{-axis. Find the torus volume.}",
        FormulaAnswer(2 * sp.pi**2 * major * minor**2),
        rf"R={major}>{minor}=r.\quad dV=2\pi x\cdot2\sqrt{{r^2-(x-R)^2}}\,dx.",
        rf"u=x-R:\quad V=4\pi\int_{{-r}}^r(R+u)\sqrt{{r^2-u^2}}\,du."
        rf"\quad\text{{The odd term vanishes and the remaining integral is a semicircle area.}}"
        rf"\quad V=4\pi R\frac{{\pi r^2}}2=2\pi^2Rr^2={tex(2 * sp.pi**2 * major * minor**2)}.",
    )
    return replace(built, visual=visual)
