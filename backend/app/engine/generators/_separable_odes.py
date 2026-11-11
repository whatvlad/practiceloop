"""Decay models and complete separable solution families from AM2A/13.1–13.3."""

import math
from collections.abc import Callable
from dataclasses import replace
from typing import Any

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer, RealSetAnswer
from app.engine.answers.domain_formula import DomainFormulaAnswer
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import path, plot, point
from app.engine.generators._multivariable_extrema import formulas
from app.engine.generators._sequence_limits import finish

T, Y, W = sp.symbols("t y x", real=True)
ZERO = sp.S.Zero
R = sp.S.Reals
POSITIVE = sp.Interval.open(0, sp.oo)
NONZERO = R - sp.FiniteSet(0)
EMPTY = sp.S.EmptySet
DECAY_FIT = ("Initial mass", "Positive decay rate")
HALF_LIFE = ("Remaining mass", "Positive decay rate")
DECAY_PERCENT = ("First percentage", "Second percentage", "Third percentage")
GENERAL = ("Time formula", "Admissible constants", "Equilibrium values")
JUNCTION = (*GENERAL, "Joining times")
IVP = ("Solution formula", "Maximal time interval")
IMPLICIT_IVP = ("Dependent formula", "Time formula", "Initial constant", "Maximal time interval")
WAITING = ("Time formula", "Branch formula", "Departure constants", "Maximal time interval")
Curve = tuple[str, float, float, Callable[[float], float]]


def visual(
    curves: list[Curve], markers: list[tuple[str, float, float]], *, decay: bool = False
) -> dict[str, Any]:
    diagram = plot(
        "Decay model" if decay else "Solution curves",
        "Marked points are the sampled model data or initial "
        "values. Paths show finite portions of the curves.",
        [path(label, start, end, function) for label, start, end, function in curves],
        [point(label, x, y, included=True) for label, x, y in markers],
    )
    diagram.update(xLabel="t", yLabel="amount" if decay else "y")
    return diagram


def decay_plot(
    built: Built,
    amount: sp.Expr,
    rate: sp.Expr,
    time: sp.Expr,
    markers: list[tuple[str, float, float]],
) -> Built:
    return replace(
        built,
        visual=visual(
            [
                (
                    "Exponential decay",
                    0,
                    float(time),
                    lambda t: float(amount) * math.exp(-float(rate) * t),
                )
            ],
            markers,
            decay=True,
        ),
    )


def two_measurements_decay(a: int, b: int, c: int) -> Built:
    factor = b + 1
    initial = sp.Integer(c * factor**2)
    rate = sp.log(factor) / a
    built = finish(
        rf"\text{{A sample decays exponentially. At times }}{a}\text{{ and }}{2 * a}"
        rf"\text{{ its masses are }}{c * factor}\text{{ and }}{c}\text{{ grams.}}"
        r"\quad\text{Give initial mass and positive rate }k\text{ in }M(t)=M_0e^{-kt}.",
        formulas((initial, rate), DECAY_FIT),
        rf"M(2\cdot{a})/M({a})=1/{factor}=e^{{-{a}k}}.",
        rf"k={tex(rate)},\quad M_0=M({a})e^{{{a}k}}={initial}.",
    )
    return decay_plot(
        built,
        initial,
        rate,
        sp.Integer(2 * a),
        [("First measurement", a, c * factor), ("Second measurement", 2 * a, c)],
    )


def half_life_mass(a: int, b: int, c: int) -> Built:
    half = 20 * a * (c + 1)
    elapsed = 20 * a * b
    initial = sp.Integer(50 + 10 * c)
    rate = sp.log(2) / half
    remaining = initial * 2 ** (-sp.Rational(elapsed, half))
    built = finish(
        rf"\text{{A sample has half-life }}{half}\text{{ days and starts at }}{initial}"
        rf"\text{{ grams. Give its mass after }}{elapsed}\text{{ days and positive decay rate.}}",
        formulas((remaining, rate), HALF_LIFE),
        rf"e^{{-{half}k}}=1/2\quad\Longrightarrow\quad k={tex(rate)}.",
        rf"M({elapsed})={initial}\,2^{{-{tex(sp.Rational(elapsed, half))}}}={tex(remaining)}.",
    )
    return decay_plot(
        built,
        initial,
        rate,
        sp.Integer(max(half, elapsed)),
        [("Requested time", elapsed, float(remaining)), ("Half-life", half, float(initial) / 2)],
    )


def half_life_percentages(a: int, b: int, c: int) -> Built:
    half = 2 * (b + 2) * a
    times = (2 * a, half // 2, (c + 1) * half)
    values = tuple(100 * 2 ** (-sp.Rational(t, half)) for t in times)
    rate = sp.log(2) / half
    built = finish(
        rf"\text{{A substance has half-life }}{half}\text{{ "
        rf"years. Give the three percentages remaining at }}"
        rf"\quad {times[0]},\ {times[1]},\ {times[2]}\text{{ years, in that order.}}",
        formulas(values, DECAY_PERCENT),
        r"\text{The remaining percentage after time }t\text{ is }100\,2^{-t/H}."
        rf"\quad H={half}.",
        r"\left(" + ",".join(map(tex, values)) + r"\right)\ \text{percent}.",
    )
    markers = [
        ("Requested percentage", float(t), float(v)) for t, v in zip(times, values, strict=True)
    ]
    return decay_plot(built, sp.Integer(100), rate, sp.Integer(times[-1]), markers)


def general(
    equation: str,
    template: str,
    kernel: sp.Expr,
    domain: sp.Set,
    constants: sp.Set,
    equilibria: sp.Set,
    derivation: str,
    complete: str,
    curves: list[Curve],
    *,
    joining: sp.Set | None = None,
) -> Built:
    parts: tuple[DomainFormulaAnswer | RealSetAnswer, ...] = (
        DomainFormulaAnswer(kernel, domain, "t"),
        RealSetAnswer(constants),
        RealSetAnswer(equilibria),
    )
    labels: tuple[str, ...] = GENERAL
    request = (
        r"\text{Give the exact time formula }F(t)\text{, the set of admissible constants }C"
        r"\text{ for nonconstant solutions, and the set of equilibrium values.}"
    )
    if joining is not None:
        parts = (*parts, RealSetAnswer(joining))
        labels = JUNCTION
        request += (
            r"\quad\text{Also give the set of times where a nonconstant branch can join }y=0."
        )
    built = finish(
        rf"\text{{Find the general real solution of }}{equation}."
        rf"\quad\text{{Use the family form }}{template}.\quad" + request,
        OrderedAnswer(parts, labels),
        derivation,
        rf"F(t)={tex(kernel)},\quad C\in{tex(constants)},\quad y_{{\rm eq}}\in{tex(equilibria)}."
        r"\quad" + complete,
    )
    return replace(built, visual=visual(curves, []))


def circle_separable_family(a: int, b: int, c: int) -> Built:
    k = a + b
    return general(
        rf"y y'+{k}t=0",
        r"y=\pm\sqrt{F(t)+C},\quad F(0)=0,\quad F(t)+C>0",
        -k * T**2,
        R,
        POSITIVE,
        EMPTY,
        rf"(y^2)'=-{2 * k}t\quad\Longrightarrow\quad y^2=C-{k}t^2.",
        rf"\text{{Each sign is valid on }}(-\sqrt{{C/{k}}},\sqrt{{C/{k}}})."
        r"\quad\text{At its endpoints }y=0\text{ but the equation has a nonzero time term.}",
        [
            ("Positive branch", -0.99, 0.99, lambda t: math.sqrt(k * (1 - t * t))),
            ("Negative branch", -0.99, 0.99, lambda t: -math.sqrt(k * (1 - t * t))),
        ],
    )


def vanishing_factor_family(a: int, b: int, c: int) -> Built:
    k = a + b + c
    return general(
        rf"y y'={k}ty",
        r"y=F(t)+C\text{ on its moving parts},\quad F(0)=0",
        k * T**2 / 2,
        R,
        R,
        sp.FiniteSet(0),
        rf"y\ne0\Longrightarrow y'={k}t\Longrightarrow y={k}t^2/2+C."
        r"\quad\text{The undivided equation also admits }y=0.",
        r"\text{Nonzero constants give full quadratic "
        r"solutions, including any isolated zero crossings.}"
        r"\quad\text{A zero plateau can meet a moving part only at a zero with zero derivative,}"
        r"\text{ so only at }t=0,C=0.\quad\text{Each half-line "
        r"may then independently use zero or the quadratic.}",
        [
            ("Quadratic", -1, 1, lambda t: k * t * t / 2),
            ("Equilibrium", -1, 1, lambda t: 0),
            ("Joined solution", -1, 1, lambda t: k * max(t, 0) ** 2 / 2),
        ],
        joining=sp.FiniteSet(0),
    )


def product_invariant_family(a: int, b: int, c: int) -> Built:
    k = a * a
    d = b * b
    return general(
        rf"t(y^2-{d})+y(t^2-{k})y'=0",
        rf"y=\pm\sqrt{{{d}+C F(t)}},\quad t\ne\pm{a},\quad {d}+C F(t)>0",
        1 / (T**2 - k),
        R - sp.FiniteSet(-a, a),
        NONZERO,
        sp.FiniteSet(-b, b),
        rf"\big[(t^2-{k})(y^2-{d})\big]'=0.",
        rf"\text{{For }}C\ne0\text{{ each sign extends on a connected component of }}"
        rf"\{{t\ne\pm{a}:{d}+C/(t^2-{k})>0\}}."
        r"\quad\text{A finite zero at }t\ne0\text{ violates the undivided equation."
        r" A possible zero at }t=0\text{ has no real punctured neighborhood.}"
        r"\quad C=0\text{ gives the two equilibria on the whole line.}",
        [
            ("Positive branch", a + 0.2, a + 2, lambda t: math.sqrt(d + 1 / (t * t - k))),
            ("Negative branch", a + 0.2, a + 2, lambda t: -math.sqrt(d + 1 / (t * t - k))),
        ],
    )


def arcsine_plateau_family(a: int, b: int, c: int) -> Built:
    coefficient = sp.Rational(a, b + c)
    scale = float(coefficient)

    def joined(t: float) -> float:
        return math.sin(max(-math.pi / 2, min(math.pi / 2, scale * math.sqrt(t) - 1)))

    return general(
        rf"2\sqrt t\,y'={tex(coefficient)}\sqrt{{1-y^2}},\quad t>0",
        r"y=\sin(\operatorname{clip}(F(t)+C,-\pi/2,\pi/2)),"
        r"\quad\lim_{t\downarrow0}F(t)=0",
        coefficient * sp.sqrt(T),
        POSITIVE,
        sp.Interval.open(-sp.oo, sp.pi / 2),
        sp.FiniteSet(-1, 1),
        rf"(\arcsin y)'={tex(coefficient)}/(2\sqrt t)\quad\text{{for }}|y|<1.",
        r"\text{Clipping means holding the angle at the nearer endpoint outside the interval.}"
        r"\quad\text{The joins are differentiable since cosine vanishes at both endpoints.}"
        r"\quad\text{Every nonconstant solution increases "
        r"between possible plateaus on }(0,\infty).",
        [
            ("Joined solution", 0.01, ((math.pi / 2 + 1) / scale) ** 2 + 1, joined),
            ("Upper equilibrium", 0.01, ((math.pi / 2 + 1) / scale) ** 2 + 1, lambda t: 1),
            ("Lower equilibrium", 0.01, ((math.pi / 2 + 1) / scale) ** 2 + 1, lambda t: -1),
        ],
    )


def euler_separable_family(a: int, b: int, c: int) -> Built:
    exponent = a + b
    return general(
        rf"t y'+{exponent}y=0",
        rf"y=C F(t),\quad F(1)=1,\quad F(-1)=(-1)^{{{exponent}}}",
        T ** (-exponent),
        NONZERO,
        NONZERO,
        sp.FiniteSet(0),
        rf"y\ne0,\ t\ne0\Longrightarrow (\ln|y|)'=-{exponent}/t.",
        r"\text{Each nonzero solution is maximal on one open half-line.}"
        r"\quad\text{Only the zero equilibrium can extend across }t=0.",
        [
            ("Positive time", 0.6, 2, lambda t: t ** (-exponent)),
            ("Negative time", -2, -0.6, lambda t: t ** (-exponent)),
            ("Equilibrium", -2, 2, lambda t: 0),
        ],
    )


def exponential_separable_family(a: int, b: int, c: int) -> Built:
    coefficient = sp.Rational(a, b)
    kernel = sp.exp(coefficient * (sp.exp(b * T) - 1) + c * T)
    return general(
        rf"y'=({a}e^{{{b}t}}+{c})y",
        r"y=C F(t),\quad F(0)=1",
        kernel,
        R,
        NONZERO,
        sp.FiniteSet(0),
        rf"(\ln|y|)'={a}e^{{{b}t}}+{c}\quad\text{{when }}y\ne0.",
        r"\text{The exponential factor is defined and nonzero for every real }t."
        r"\quad\text{Both signs are supplied by }C\ne0\text{ and }y=0\text{ is the equilibrium.}",
        [
            (
                "Positive solution",
                -1,
                0.2,
                lambda t: math.exp(float(coefficient) * math.expm1(b * t) + c * t),
            ),
            (
                "Negative solution",
                -1,
                0.2,
                lambda t: -math.exp(float(coefficient) * math.expm1(b * t) + c * t),
            ),
        ],
    )


def explicit_ivp(
    equation: str,
    initial: str,
    value: sp.Expr,
    domain: sp.Set,
    derivation: str,
    conclusion: str,
    bounds: tuple[float, float],
    initial_point: tuple[float, float],
) -> Built:
    answer = OrderedAnswer((DomainFormulaAnswer(value, domain, "t"), RealSetAnswer(domain)), IVP)
    built = finish(
        rf"\text{{Solve }}{equation},\quad {initial}."
        r"\quad\text{Give the exact solution in }t\text{ and its maximal open time interval.}",
        answer,
        derivation,
        rf"y(t)={tex(value)},\quad t\in{tex(domain)}.\quad" + conclusion,
    )
    y = sp.lambdify(T, value, "math")
    return replace(
        built, visual=visual([("IVP solution", *bounds, y)], [("Initial point", *initial_point)])
    )


def logarithm_sine_ivp(a: int, b: int, c: int) -> Built:
    coefficient = a + b
    value = sp.exp(c * sp.tan(T / 2) ** coefficient)
    domain = sp.Interval.open(0, sp.pi)
    return explicit_ivp(
        rf"y'\sin t={coefficient}y\ln y,\quad \sin t\ne0,\ y>0",
        rf"y(\pi/2)=e^{{{c}}}",
        value,
        domain,
        rf"u=\ln y\Longrightarrow u'={coefficient}u/\sin t."
        rf"\quad u={c}\tan^{{{coefficient}}}(t/2)\text{{ by the initial value.}}",
        r"\text{The adjacent excluded zeros of sine are }0\text{ and }\pi.",
        (0.2, math.pi / 2 + 0.04),
        (math.pi / 2, math.exp(c)),
    )


def square_root_waiting_ivp(a: int, b: int, c: int) -> Built:
    coefficient = sp.Rational(a, a + b + c)
    domain = sp.Interval.open(-1, 1)
    constants = sp.Interval(0, coefficient)
    f = coefficient * sp.sqrt(1 - T**2)
    g = sp.sqrt(1 - W**2)
    answer = OrderedAnswer(
        (
            DomainFormulaAnswer(f, domain, "t"),
            DomainFormulaAnswer(g, constants, "x"),
            RealSetAnswer(constants),
            RealSetAnswer(domain),
        ),
        WAITING,
    )
    built = finish(
        rf"\text{{Solve }}{tex(coefficient)}t\sqrt{{1-y^2}}+y\sqrt{{1-t^2}}y'=0,"
        r"\quad y(0)=1,\quad 0<y\le1."
        r"\quad\text{Use }y=G(\max(0,C-F(t)))\text{ with "
        r"independent }C\text{ on each side of zero.}"
        r"\quad\text{Take }F\text{ even with limit zero at "
        r"}|t|=1\text{ and use }x=\sqrt{1-y^2}\text{ for }G(x)."
        r"\quad\text{Give }F(t),G(x),\text{ the admissible "
        r"constant set and maximal open interval.}",
        answer,
        rf"w=\sqrt{{1-y^2}}\Longrightarrow w'={tex(coefficient)}t/\sqrt{{1-t^2}}"
        r"\text{ wherever }y<1.\quad w=C-F(t)."
        r"\quad\text{Where }w=0\text{ the solution can remain at }y=1.",
        rf"F(t)={tex(f)},\quad G(x)={tex(g)},\quad C\in{tex(constants)},\quad t\in{tex(domain)}."
        r"\quad\text{The two constants choose when each branch departs from }y=1."
        r"\quad\text{At departure }w=0\text{, so the "
        r"derivative of }\sqrt{1-w^2}\text{ joins smoothly.}",
    )
    s = float(coefficient)

    def branch(t: float, delay: float) -> float:
        w = max(0, delay - s * math.sqrt(1 - t * t))
        return math.sqrt(1 - w * w)

    return replace(
        built,
        visual=visual(
            [
                ("Immediate departure", -0.99, 0.99, lambda t: branch(t, s)),
                ("Delayed departure", -0.99, 0.99, lambda t: branch(t, s / 2)),
                ("Equilibrium", -0.99, 0.99, lambda t: 1),
            ],
            [("Initial point", 0, 1)],
        ),
    )


def implicit_ivp(
    equation: str,
    initial: str,
    g: sp.Expr,
    f: sp.Expr,
    value: sp.Expr,
    time_domain: sp.Set,
    derivation: str,
    bounds: tuple[float, float],
    initial_point: tuple[float, float],
    left: Callable[[float], float],
) -> Built:
    answer = OrderedAnswer(
        (
            DomainFormulaAnswer(g, POSITIVE, "y"),
            DomainFormulaAnswer(f, time_domain, "t"),
            FormulaAnswer(value),
            RealSetAnswer(time_domain),
        ),
        IMPLICIT_IVP,
    )
    built = finish(
        rf"\text{{Solve }}{equation},\quad {initial},\quad y>0."
        r"\quad\text{Use the normalized implicit form }G(y)=F(t)+K."
        r"\quad\text{Use coefficient one on }\ln y\text{ and zero additive constants in }G,F."
        r"\quad\text{Give }G(y),F(t),K"
        r"\text{ and the maximal open time interval.}",
        answer,
        derivation,
        rf"{tex(g)}={tex(f)}+({tex(value)}),\quad t\in{tex(time_domain)}."
        r"\quad\text{The left side increases from }-\infty\text{ to }+\infty"
        r"\text{ for positive }y\text{, giving exactly one branch throughout this time interval.}",
    )
    target = sp.lambdify(T, f + value, "math")

    def solution(t: float) -> float:
        wanted = target(t)
        lo, hi = -40.0, 40.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if left(mid) < wanted:
                lo = mid
            else:
                hi = mid
        return math.exp((lo + hi) / 2)

    return replace(
        built,
        visual=visual(
            [("Positive implicit branch", *bounds, solution)], [("Initial point", *initial_point)]
        ),
    )


def logarithm_implicit_ivp(a: int, b: int, c: int) -> Built:
    initial = sp.exp(c)
    constant = b + sp.log(b) - a * c
    return implicit_ivp(
        rf"t(y+1)y'={a}y,\quad t>0",
        rf"y(e^{{{c}}})={b}",
        Y + sp.log(Y),
        a * sp.log(T),
        constant,
        POSITIVE,
        rf"(1+1/y)y'={a}/t\quad\Longrightarrow\quad y+\ln y={a}\ln t+K.",
        (float(initial) / 2, float(initial) * 1.5),
        (float(initial), b),
        lambda z: math.exp(z) + z,
    )


def cosine_implicit_ivp(a: int, b: int, c: int) -> Built:
    k = sp.Rational(a, c)
    constant = sp.log(b) + sp.Rational(b * b, 2)
    return implicit_ivp(
        rf"(1+y^2)y'={tex(k)}y\cos t",
        rf"y(0)={b}",
        sp.log(Y) + Y**2 / 2,
        k * sp.sin(T),
        constant,
        R,
        rf"(1/y+y)y'={tex(k)}\cos t\quad\Longrightarrow\quad\ln y+y^2/2={tex(k)}\sin t+K.",
        (-math.pi, math.pi),
        (0, b),
        lambda z: z + math.exp(2 * z) / 2,
    )


def reciprocal_pole_ivp(a: int, b: int, c: int) -> Built:
    p = c * (T + b * T**3 / 3 + a + sp.Rational(b * a**3, 3))
    initial = -1 / p.subs(T, 0)
    return explicit_ivp(
        rf"y'={c}y^2(1+{b}t^2)",
        rf"y(0)={tex(initial)}",
        -1 / p,
        sp.Interval.open(-a, sp.oo),
        rf"(-1/y)'={c}(1+{b}t^2)\quad\Longrightarrow\quad -1/y={tex(p)}.",
        rf"\text{{The cubic is strictly increasing and has its only zero at }}t=-{a}.",
        (-a + 0.1, a + 1),
        (0, float(initial)),
    )


def exponential_log_ivp(a: int, b: int, c: int) -> Built:
    w = (b + sp.Rational(a, c)) * sp.exp(c * T) - sp.Rational(a, c)
    left = sp.log(sp.Rational(a, a + b * c)) / c
    return explicit_ivp(
        rf"e^y(y'-{c})={a}",
        rf"y(0)=\ln {b}",
        sp.log(w),
        sp.Interval.open(left, sp.oo),
        rf"w=e^y\Longrightarrow w'={c}w+{a},\quad w(0)={b}."
        rf"\quad w={tex(w)}.",
        rf"\text{{The logarithm argument is positive exactly when }}t>{tex(left)}.",
        (float(left) + 0.01, 1.5),
        (0, math.log(b)),
    )
