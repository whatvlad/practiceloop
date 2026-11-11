"""Trigonometric powers and rational trigonometric antiderivatives (#267)."""

import sympy as sp

from app.engine.blocks.analysis_one import X
from app.engine.generators._antiderivatives import REALS, antiderivative
from app.engine.generators._elementary_common import Built, tex

U = sp.Symbol("u", real=True)
S = sp.sin(U)
C = sp.cos(U)
T = sp.tan(U)
FIRST_QUADRANT = sp.Interval.open(0, sp.pi / 2)
COS_POSITIVE = sp.Interval.open(-sp.pi / 2, sp.pi / 2)


def scaled_trig(
    amplitude: int,
    frequency: int,
    integrand: sp.Expr,
    primitive: sp.Expr,
    method: str,
    *,
    interval: sp.Set = REALS,
    phase: int = 0,
    work: str = "",
    checked: sp.Expr | None = None,
) -> Built:
    angle = frequency * X + phase
    domain = interval
    if isinstance(interval, sp.Interval):
        domain = sp.Interval.open(
            (interval.start - phase) / frequency, (interval.end - phase) / frequency
        )
    return antiderivative(
        amplitude * integrand.subs(U, angle),
        domain,
        rf"u={tex(angle)},\quad du={frequency}\,dx.\quad {method}",
        primitive=sp.Rational(amplitude, frequency) * primitive.subs(U, angle),
        checked=None if checked is None else amplitude * checked.subs(U, angle),
        derivation=rf"{work},\quad " if work else "",
    )


def odd_sine_cube(a: int, b: int, c: int) -> Built:
    return scaled_trig(
        a,
        b,
        S**3,
        -C + C**3 / 3,
        r"\sin^3u=(1-\cos^2u)\sin u,\quad t=\cos u,\quad dt=-\sin u\,du.",
        work=r"\int\sin^3u\,du=-\int(1-t^2)\,dt",
    )


def even_sine_odd_cosine(a: int, b: int, c: int) -> Built:
    return scaled_trig(
        a,
        b,
        S**4 * C**3,
        S**5 / 5 - S**7 / 7,
        r"\cos^3u=(1-\sin^2u)\cos u,\quad t=\sin u,\quad dt=\cos u\,du.",
        work=r"\int\sin^4u\cos^3u\,du=\int(t^4-t^6)\,dt",
    )


def shifted_cosine_fourth(a: int, b: int, c: int) -> Built:
    reduced = sp.Rational(3, 8) + sp.cos(2 * U) / 2 + sp.cos(4 * U) / 8
    return scaled_trig(
        a,
        b,
        C**4,
        3 * U / 8 + sp.sin(2 * U) / 4 + sp.sin(4 * U) / 32,
        r"\cos^4u=\tfrac14(1+\cos 2u)^2.",
        phase=c,
        work=r"\cos^4u=\tfrac38+\tfrac12\cos 2u+\tfrac18\cos 4u",
        checked=reduced,
    )


def odd_sine_even_cosine(a: int, b: int, c: int) -> Built:
    return scaled_trig(
        a,
        b,
        S**3 * C**6,
        -(C**7) / 7 + C**9 / 9,
        r"\sin^3u=(1-\cos^2u)\sin u,\quad t=\cos u,\quad dt=-\sin u\,du.",
        work=r"\int\sin^3u\cos^6u\,du=\int(t^8-t^6)\,dt",
    )


def cosine_square_double_angle(a: int, b: int, c: int) -> Built:
    reduced = sp.Rational(1, 4) + sp.cos(2 * U) / 2 + sp.cos(4 * U) / 4
    return scaled_trig(
        a,
        b,
        C**2 * sp.cos(2 * U),
        U / 4 + sp.sin(2 * U) / 4 + sp.sin(4 * U) / 16,
        r"\text{Use }\cos^2u=(1+\cos2u)/2\text{ and reduce the remaining square.}",
        work=rf"\cos^2u\cos2u={tex(reduced)}",
        checked=reduced,
    )


def product_of_sine_squares(a: int, b: int, c: int) -> Built:
    reduced = sp.Rational(1, 4) - sp.cos(2 * U) / 8 - sp.cos(4 * U) / 4 + sp.cos(6 * U) / 8
    result = U / 4 - sp.sin(2 * U) / 16 - sp.sin(4 * U) / 16 + sp.sin(6 * U) / 48
    return scaled_trig(
        a,
        b,
        sp.sin(2 * U) ** 2 * S**2,
        result,
        r"\text{Use the half-angle identities, then expand }\cos2u\cos4u.",
        work=rf"\sin^2(2u)\sin^2u={tex(reduced)}",
        checked=reduced,
    )


def reciprocal_sine(a: int, b: int, c: int) -> Built:
    return scaled_trig(
        a,
        b,
        1 / S,
        sp.log(sp.tan(U / 2)),
        r"t=\tan(u/2)>0,\quad \sin u=\frac{2t}{1+t^2},\quad du=\frac{2\,dt}{1+t^2}.",
        interval=FIRST_QUADRANT,
        work=r"\int\frac{du}{\sin u}=\int\frac{dt}{t}",
    )


def secant_plus_secant_tangent(a: int, b: int, c: int) -> Built:
    return scaled_trig(
        a,
        b,
        (1 + T) / C,
        1 / C + sp.log(1 + S) - sp.log(C),
        r"\text{Split into }\sec u+\sec u\tan u\text{ and integrate each term.}",
        interval=FIRST_QUADRANT,
        work=r"\int\sec u\,du=\ln(\sec u+\tan u)+C,\quad (\sec u)'=\sec u\tan u",
        checked=S / C**2 + C / (1 + S) + T,
    )


def cancel_sine_square(a: int, b: int, c: int) -> Built:
    return scaled_trig(
        a,
        b,
        S**2 / (1 + C),
        U - S,
        r"\sin^2u=(1-\cos u)(1+\cos u),\quad 1+\cos u>0\text{ on the given interval.}",
        interval=sp.Interval.open(-sp.pi, sp.pi),
        work=r"\frac{\sin^2u}{1+\cos u}=1-\cos u",
        checked=1 - C,
    )


def reciprocal_cosine_quadratic(a: int, b: int, c: int) -> Built:
    width = c + 1
    scale = width**2 - 1
    return scaled_trig(
        a,
        b,
        1 / (1 + scale * C**2),
        sp.atan(T / width) / width,
        r"t=\tan u,\quad \cos^2u=\frac1{1+t^2},\quad du=\frac{dt}{1+t^2}.",
        interval=COS_POSITIVE,
        work=rf"\int\frac{{du}}{{1+{scale}\cos^2u}}=\int\frac{{dt}}{{t^2+{width**2}}}",
        checked=(1 + T**2) / (width**2 + T**2),
    )


def reciprocal_one_minus_tangent(a: int, b: int, c: int) -> Built:
    return scaled_trig(
        a,
        b,
        1 / (1 - T),
        (U - sp.log(C - S)) / 2,
        r"\text{Multiply by }\cos u\text{ and split the numerator.}",
        interval=sp.Interval.open(0, sp.pi / 4),
        work=r"\frac{\cos u}{\cos u-\sin u}=\frac12+\frac{\cos u+\sin u}{2(\cos u-\sin u)}",
        checked=C / (C - S),
    )


def odd_sine_over_cosine_cube(a: int, b: int, c: int) -> Built:
    return scaled_trig(
        a,
        b,
        S**5 / C**3,
        1 / (2 * C**2) + 2 * sp.log(C) - C**2 / 2,
        r"t=\cos u>0,\quad dt=-\sin u\,du,\quad \sin^4u=(1-t^2)^2.",
        interval=FIRST_QUADRANT,
        work=r"\int\frac{\sin^5u}{\cos^3u}\,du=-\int(t^{-3}-2t^{-1}+t)\,dt",
        checked=S * (1 / C**3 - 2 / C + C),
    )


def reciprocal_sine_plus_tangent(a: int, b: int, c: int) -> Built:
    primitive = (sp.log(1 - C) - sp.log(1 + C)) / 4 - 1 / (2 * (1 + C))
    return scaled_trig(
        a,
        b,
        1 / (S + T),
        primitive,
        r"\frac1{\sin u+\tan u}=\frac{\cos u}{\sin u(1+\cos u)}.\quad t=\cos u.",
        interval=FIRST_QUADRANT,
        work=r"\int\frac{-t\,dt}{(1-t)(1+t)^2}"
        r"=\int\left(-\frac1{4(1-t)}-\frac1{4(1+t)}+\frac1{2(1+t)^2}\right)dt",
        checked=C / (S * (1 + C)),
    )


def reciprocal_sine_plus_cosine(a: int, b: int, c: int) -> Built:
    root = sp.sqrt(2)
    t = sp.tan(U / 2 + sp.pi / 8)
    return scaled_trig(
        a,
        b,
        1 / (S + C),
        sp.log(t) / root,
        r"\sin u+\cos u=\sqrt2\sin(u+\pi/4),\quad t=\tan(u/2+\pi/8).",
        interval=FIRST_QUADRANT,
        work=r"\int\frac{du}{\sin u+\cos u}=\frac1{\sqrt2}\int\frac{dt}{t}",
        checked=(1 + t**2) / (2 * root * t),
    )


def pythagorean_trig_denominator(a: int, b: int, c: int) -> Built:
    p = c + 1
    t = sp.tan(U / 2)
    sine_scale = 2 * p
    cosine_scale = p**2 - 1
    constant = p**2 + 1
    return scaled_trig(
        a,
        b,
        1 / (sine_scale * S + cosine_scale * C + constant),
        -1 / (p + t),
        r"t=\tan(u/2),\quad \sin u=\frac{2t}{1+t^2},\quad \cos u=\frac{1-t^2}{1+t^2}.",
        interval=FIRST_QUADRANT,
        work=rf"\int\frac{{du}}{{{sine_scale}\sin u+{cosine_scale}\cos u+{constant}}}"
        rf"=\int\frac{{dt}}{{(t+{p})^2}}",
        checked=(1 + t**2) / (2 * (p + t) ** 2),
    )


def sine_fourth_exam(a: int, b: int, c: int) -> Built:
    reduced = sp.Rational(3, 8) - sp.cos(2 * U) / 2 + sp.cos(4 * U) / 8
    return scaled_trig(
        a,
        b,
        S**4,
        3 * U / 8 - sp.sin(2 * U) / 4 + sp.sin(4 * U) / 32,
        r"\sin^4u=\tfrac14(1-\cos 2u)^2.",
        work=r"\sin^4u=\tfrac38-\tfrac12\cos 2u+\tfrac18\cos 4u",
        checked=reduced,
    )
