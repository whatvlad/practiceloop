"""Native parts integral forms; formulas retained from the verified curriculum."""

from typing import Any

import sympy as sp

from app.engine.answers._symbolic import X
from app.engine.blocks.integral_forms.models import MethodStep, MethodTemplate

TEMPLATES = {
    "linear_exponential": MethodTemplate(1, sp.S.Reals, "integration_by_parts"),
    "quadratic_exponential": MethodTemplate(2, sp.S.Reals, "integration_by_parts", ("repeat",)),
    "cyclic_sine": MethodTemplate(3, sp.S.Reals, "integration_by_parts", ("solve_cycle",)),
}


def build(name: str, a: Any) -> tuple[Any, Any, tuple[MethodStep, ...]]:
    steps: tuple[MethodStep, ...]
    exponential = sp.exp(X)
    if name == "linear_exponential":
        primitive = a * exponential * (X - 1)
        steps = (MethodStep("parts", a * X * exponential - sp.Integral(a * exponential, X)),)
        integrand = a * X * exponential
    elif name == "quadratic_exponential":
        primitive = a * exponential * (X**2 - 2 * X + 2)
        steps = (
            MethodStep("parts", a * X**2 * exponential - sp.Integral(2 * a * X * exponential, X)),
            MethodStep(
                "repeat_parts",
                a * X**2 * exponential - 2 * a * (X * exponential - sp.Integral(exponential, X)),
            ),
        )
        integrand = a * X**2 * exponential
    else:
        integrand = a * exponential * sp.sin(X)
        boundary = a * exponential * (sp.sin(X) - sp.cos(X))
        primitive = boundary / 2
        steps = (
            MethodStep(
                "parts", a * exponential * sp.sin(X) - sp.Integral(a * exponential * sp.cos(X), X)
            ),
            MethodStep("repeat_parts", boundary - sp.Integral(integrand, X)),
            MethodStep("solve_cycle", boundary / 2),
        )
    return integrand, primitive, steps
