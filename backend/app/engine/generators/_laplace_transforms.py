"""Direct, graph-based and table-based Laplace transforms from AM2A/14.1–14.2."""

from collections.abc import Callable
from dataclasses import replace
from typing import Any

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer, RealSetAnswer
from app.engine.answers.domain_formula import DomainFormulaAnswer
from app.engine.generators._elementary_common import Built, tex
from app.engine.generators._limit_visuals import plot, point
from app.engine.generators._sequence_limits import finish

T, S = sp.symbols("t s", real=True)
R = sp.S.Reals
NONZERO = R - sp.FiniteSet(0)
TRANSFORM = ("Transform", "Convergence set")
COMPACT = ("Transform away from zero", "Value at zero", "Convergence set")


def transform(
    function: str,
    value: sp.Expr,
    domain: sp.Set,
    derivation: str,
    *,
    by_definition: bool = False,
    at_zero: sp.Expr | None = None,
    visual: dict[str, Any] | None = None,
) -> Built:
    method = (
        "Use the definition to find"
        if by_definition
        else "Use the Laplace table and linearity to find"
    )
    request = r"\text{Give the exact transform in }s\text{ and its real convergence set.}"
    if at_zero is None:
        parts = (DomainFormulaAnswer(value, domain, "s"), RealSetAnswer(domain))
        answer = OrderedAnswer(parts, TRANSFORM)
        result = rf"F(s)={tex(value)},\quad s\in{tex(domain)}."
    else:
        answer = OrderedAnswer(
            (
                DomainFormulaAnswer(value, NONZERO, "s"),
                FormulaAnswer(at_zero),
                RealSetAnswer(domain),
            ),
            COMPACT,
        )
        request = (
            r"\text{Give the exact formula for }s\ne0,\text{ the value at }s=0"
            r"\text{ and the full real convergence set.}"
        )
        result = rf"F(s)={tex(value)}\ (s\ne0),\quad F(0)={tex(at_zero)},\quad s\in\mathbb R."
    built = finish(
        rf"\text{{{method} the Laplace transform of }}{function}.\quad" + request,
        answer,
        r"F(s)=\int_0^\infty e^{-st}f(t)\,dt.\quad" + derivation,
        result,
    )
    return replace(built, visual=visual)


def right_of(value: int) -> sp.Set:
    return sp.Interval.open(value, sp.oo)


def affine_definition(a: int, b: int, c: int) -> Built:
    return transform(
        tex(a * T - b * c),
        a / S**2 - b * c / S,
        right_of(0),
        r"\text{For }s>0,\ \int_0^\infty e^{-st}\,dt=1/s."
        r"\quad\text{Integration by parts gives }\int_0^\infty t e^{-st}\,dt=1/s^2."
        r"\quad\text{The affine growth precludes convergence for }s\le0.",
        by_definition=True,
    )


def sine_definition(a: int, b: int, c: int) -> Built:
    frequency = b + c
    return transform(
        tex(a * sp.sin(frequency * T)),
        a * frequency / (S**2 + frequency**2),
        right_of(0),
        rf"\int e^{{-st}}\sin({frequency}t)\,dt="
        rf"-\frac{{e^{{-st}}(s\sin({frequency}t)+{frequency}\cos({frequency}t))}}"
        rf"{{s^2+{frequency**2}}}."
        r"\quad\text{The upper endpoint vanishes only for }s>0.",
        by_definition=True,
    )


def power_definition(a: int, b: int, c: int) -> Built:
    n = b + 1
    return transform(
        tex(a * c * T**n),
        a * c * sp.factorial(n) / S ** (n + 1),
        right_of(0),
        r"I_0=1/s,\quad I_n=\int_0^\infty t^ne^{-st}\,dt=(n/s)I_{n-1}\quad(s>0)."
        r"\quad\text{This follows by integration by parts and gives }I_n=n!/s^{n+1}.",
        by_definition=True,
    )


def decaying_linear_definition(a: int, b: int, c: int) -> Built:
    shift = b + c
    return transform(
        tex(a * T * sp.exp(-shift * T)),
        a / (S + shift) ** 2,
        right_of(-shift),
        rf"e^{{-st}}f(t)={a}t e^{{-(s+{shift})t}}."
        rf"\quad\text{{Integrate by parts with decay rate }}s+{shift}>0.",
        by_definition=True,
    )


def growing_cosine_definition(a: int, b: int, c: int) -> Built:
    p = S - b
    return transform(
        tex(a * sp.exp(b * T) * sp.cos(c * T)),
        a * p / (p * p + c * c),
        right_of(b),
        rf"q=s-{b}.\quad \int e^{{-qt}}\cos({c}t)\,dt="
        rf"\frac{{e^{{-qt}}(-q\cos({c}t)+{c}\sin({c}t))}}{{q^2+{c * c}}}."
        r"\quad\text{Only positive }q\text{ gives an upper endpoint limit.}",
        by_definition=True,
    )


def hyperbolic_sine_definition(a: int, b: int, c: int) -> Built:
    return transform(
        rf"{a * c}\sinh({b}t)",
        a * b * c / (S**2 - b * b),
        right_of(b),
        rf"\sinh({b}t)=(e^{{{b}t}}-e^{{-{b}t}})/2."
        rf"\quad\text{{The two exponential integrals both converge when }}s>{b}.",
        by_definition=True,
    )


def graph_description(a: int, b: int, c: int, shape: str) -> dict[str, Any]:
    height = b + c
    paths: list[dict[str, Any]]
    if shape == "rectangle":
        paths = [
            {"label": "Constant segment", "points": [[0, height], [a, height]]},
            {"label": "Zero tail", "points": [[a, 0], [3 * a, 0]], "arrow": True},
        ]
        markers = [
            point("Start", 0, height, included=True),
            point("Open end", a, height, included=False),
            point("Zero begins", a, 0, included=True),
        ]
        description = f"The graph equals {height} from t=0 up to t={a}, then equals zero."
    elif shape == "triangle":
        paths = [
            {"label": "Triangle", "points": [[0, 0], [a, height], [2 * a, 0]]},
            {"label": "Zero tail", "points": [[2 * a, 0], [3 * a, 0]], "arrow": True},
        ]
        markers = [
            point("Peak", a, height, included=True),
            point("Zero begins", 2 * a, 0, included=True),
        ]
        description = (
            f"Join (0,0), ({a},{height}) and ({2 * a},0) by straight lines, then stay at zero."
        )
    else:
        paths = [
            {"label": "Ramp", "points": [[0, 0], [a, height]]},
            {"label": "Constant tail", "points": [[a, height], [3 * a, height]], "arrow": True},
        ]
        markers = [point("Join", a, height, included=True)]
        description = (
            f"A straight ramp joins (0,0) to ({a},{height}), then the graph stays at {height}."
        )
    diagram = plot("Given function", description, paths, markers)
    diagram.update(xLabel="t", yLabel="f(t)")
    return diagram


def rectangle_graph(a: int, b: int, c: int) -> dict[str, Any]:
    return graph_description(a, b, c, "rectangle")


def triangle_graph(a: int, b: int, c: int) -> dict[str, Any]:
    return graph_description(a, b, c, "triangle")


def ramp_graph(a: int, b: int, c: int) -> dict[str, Any]:
    return graph_description(a, b, c, "ramp")


def rectangular_pulse_transform(a: int, b: int, c: int) -> Built:
    height = b + c
    return transform(
        r"\text{the function in the graph}",
        height * (1 - sp.exp(-a * S)) / S,
        R,
        rf"f(t)={height}\text{{ on }}[0,{a})\text{{ and zero afterwards.}}"
        rf"\quad F(s)={height}\int_0^{{{a}}}e^{{-st}}\,dt."
        r"\quad\text{Compact support gives convergence for every real }s.",
        by_definition=True,
        at_zero=sp.Integer(height * a),
        visual=rectangle_graph(a, b, c),
    )


def triangular_pulse_transform(a: int, b: int, c: int) -> Built:
    height = b + c
    slope = sp.Rational(height, a)
    return transform(
        r"\text{the function in the graph}",
        slope * (1 - sp.exp(-a * S)) ** 2 / S**2,
        R,
        rf"\text{{The slopes are }}{tex(slope)}\text{{ and }}{tex(-slope)}"
        rf"\text{{ on }}[0,{a}]\text{{ and }}[{a},{2 * a}]\text{{. Integration by parts gives }}"
        rf"F(s)=\frac{{{tex(slope)}}}s\left(\int_0^{{{a}}}e^{{-st}}\,dt"
        rf"-\int_{{{a}}}^{{{2 * a}}}e^{{-st}}\,dt\right)."
        r"\quad\text{At zero use the triangle area.}",
        by_definition=True,
        at_zero=sp.Integer(a * height),
        visual=triangle_graph(a, b, c),
    )


def ramp_to_constant_transform(a: int, b: int, c: int) -> Built:
    height = b + c
    slope = sp.Rational(height, a)
    return transform(
        r"\text{the function in the graph}",
        slope * (1 - sp.exp(-a * S)) / S**2,
        right_of(0),
        rf"\text{{The slope is }}{tex(slope)}\text{{ up to }}t={a}\text{{ and zero thereafter.}}"
        rf"\quad F(s)=\frac{{{tex(slope)}}}s\int_0^{{{a}}}e^{{-st}}\,dt"
        r"\text{ by integration by parts when }s>0."
        r"\quad\text{The nonzero constant tail forces }s>0.",
        by_definition=True,
        visual=ramp_graph(a, b, c),
    )


PROMPT_GRAPHS: dict[Callable[[int, int, int], Built], Callable[[int, int, int], dict[str, Any]]] = {
    rectangular_pulse_transform: rectangle_graph,
    triangular_pulse_transform: triangle_graph,
    ramp_to_constant_transform: ramp_graph,
}


def linear_cosine_table(a: int, b: int, c: int) -> Built:
    return transform(
        tex(a * T - b * sp.cos(c * T)),
        a / S**2 - b * S / (S * S + c * c),
        right_of(0),
        rf"\mathcal L\{{t\}}=s^{{-2}},\quad \mathcal L\{{\cos({c}t)\}}=s/(s^2+{c * c})."
        r"\quad\text{Take the stated linear combination on }s>0.",
    )


def polynomial_table(a: int, b: int, c: int) -> Built:
    n = c + 1
    return transform(
        tex(a + b * T**n),
        a / S + b * sp.factorial(n) / S ** (n + 1),
        right_of(0),
        rf"\mathcal L\{{1\}}=1/s,\quad \mathcal L\{{t^{{{n}}}\}}={n}!/s^{{{n + 1}}}."
        r"\quad\text{Both terms need positive }s.",
    )


def shifted_affine_table(a: int, b: int, c: int) -> Built:
    return transform(
        tex((a * T + b) * sp.exp(c * T)),
        a / (S - c) ** 2 + b / (S - c),
        right_of(c),
        rf"\mathcal L\{{{a}t+{b}\}}={a}/s^2+{b}/s."
        rf"\quad\text{{The exponential factor replaces }}s\text{{ by }}s-{c}.",
    )


def sine_cosine_table(a: int, b: int, c: int) -> Built:
    return transform(
        tex(a * sp.sin(b * T) + b * sp.cos(c * T)),
        a * b / (S * S + b * b) + b * S / (S * S + c * c),
        right_of(0),
        rf"\mathcal L\{{\sin({b}t)\}}={b}/(s^2+{b * b}),"
        rf"\quad \mathcal L\{{\cos({c}t)\}}=s/(s^2+{c * c})."
        r"\quad\text{The nonzero trigonometric sum has no convergent integral at }s=0.",
    )


def shifted_sine_constant_table(a: int, b: int, c: int) -> Built:
    q = S + b
    return transform(
        tex(a * sp.exp(-b * T) * (1 + sp.sin(c * T))),
        a * (1 / q + c / (q * q + c * c)),
        right_of(-b),
        rf"\mathcal L\{{1+\sin({c}t)\}}=1/s+{c}/(s^2+{c * c})."
        rf"\quad\text{{Now shift }}s\text{{ to }}s+{b}.",
    )


def shifted_trigonometric_table(a: int, b: int, c: int) -> Built:
    q = S - a
    return transform(
        tex(sp.exp(a * T) * (b * sp.cos(c * T) - a * sp.sin(c * T))),
        (b * q - a * c) / (q * q + c * c),
        right_of(a),
        rf"\mathcal L\{{{b}\cos({c}t)-{a}\sin({c}t)\}}=({b}s-{a * c})/(s^2+{c * c})."
        rf"\quad\text{{Now shift }}s\text{{ to }}s-{a}.",
    )
