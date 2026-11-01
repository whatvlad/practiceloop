"""Native basic integral forms, preserving the ADR-003 structural levels."""

from dataclasses import dataclass
from typing import Any

import sympy as sp

from app.engine.answers._symbolic import X
from app.engine.blocks.integral_forms.models import MethodStep, MethodTemplate

TEMPLATES = {
    "constant": MethodTemplate(1, sp.S.Reals, "direct"),
    "power": MethodTemplate(1, sp.S.Reals, "direct"),
    "exponential": MethodTemplate(1, sp.S.Reals, "direct"),
    "sine": MethodTemplate(1, sp.S.Reals, "direct"),
    "cosine": MethodTemplate(1, sp.S.Reals, "direct"),
    "sum": MethodTemplate(2, sp.S.Reals, "termwise"),
    "negative_power": MethodTemplate(3, sp.S.Reals - sp.FiniteSet(0), "power"),
    "fractional_power": MethodTemplate(3, sp.Interval.open(0, sp.oo), "power"),
    "reciprocal": MethodTemplate(3, sp.S.Reals - sp.FiniteSet(0), "logarithm"),
    "expand_square": MethodTemplate(4, sp.S.Reals, "expand"),
    "expand_and_split": MethodTemplate(5, sp.S.Reals - sp.FiniteSet(0), "expand_and_split"),
}


@dataclass(frozen=True)
class BasicStep(MethodStep):
    @property
    def latex(self) -> str:
        if self.kind == "linearity":
            return str(
                sp.latex(
                    sp.Add(
                        *(sp.Integral(t, X) for t in sp.Add.make_args(self.expression)),
                        evaluate=False,
                    )
                )
            )
        if self.kind == "rewrite_power":
            coefficient, power = self.expression.as_coeff_exponent(X)
            return rf"\int {sp.latex(coefficient)}x^{{{sp.latex(power)}}}\,dx"
        return rf"\int \left({sp.latex(self.expression)}\right)\,dx"


def build(name: str, a: Any, b: Any, n: int) -> tuple[Any, Any, tuple[MethodStep, ...]]:
    if name == "constant":
        primitive = a * X
    elif name == "power":
        primitive = a * X**n / n
    elif name == "exponential":
        primitive = a * sp.exp(X)
    elif name == "sine":
        primitive = -a * sp.cos(X)
    elif name == "cosine":
        primitive = a * sp.sin(X)
    elif name == "sum":
        primitive = a * X**n / n + b * sp.exp(X)
    elif name == "negative_power":
        primitive = a * X ** (1 - n) / (1 - n)
    elif name == "fractional_power":
        primitive = 2 * a * sp.sqrt(X)
    elif name == "reciprocal":
        primitive = a * sp.log(sp.Abs(X))
    else:
        primitive = a * (X**3 / 3 + b * X**2 + b**2 * X)
        if name == "expand_and_split":
            primitive += b * X + b * sp.log(sp.Abs(X))

    integrand = sp.diff(primitive, X)
    steps: list[BasicStep] = []
    if name == "sum":
        steps.append(BasicStep("linearity", integrand))
    elif name in {"negative_power", "fractional_power"}:
        steps.append(BasicStep("rewrite_power", integrand))
    elif name == "reciprocal":
        # d(log|x|)/dx = 1/x on both components; never silently use log(x).
        integrand = a / X
    elif name in {"expand_square", "expand_and_split"}:
        square = a * (X + b) ** 2
        expanded = sp.expand(square)
        integrand = square
        if name == "expand_and_split":
            fraction = b * (X + 1) / X
            integrand = sp.Add(square, fraction, evaluate=False)
            steps.append(BasicStep("expand", sp.Add(expanded, fraction, evaluate=False)))
            steps.append(BasicStep("split_fraction", expanded + b + b / X))
        else:
            steps.append(BasicStep("expand", expanded))
    return integrand, primitive, tuple(steps)
