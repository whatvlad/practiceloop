"""#78: parts-v1. ADR-003 deliberately has no level 1 or level 2 parts cell."""

from typing import Any

import sympy as sp

from app.generators.basic import X
from app.generators.families import FamilyStep, FamilyTemplate

TEMPLATES = {
    "linear_exponential": FamilyTemplate(3, sp.S.Reals, "integration_by_parts"),
    "quadratic_exponential": FamilyTemplate(4, sp.S.Reals, "integration_by_parts", ("repeat",)),
    "cyclic_sine": FamilyTemplate(5, sp.S.Reals, "integration_by_parts", ("solve_cycle",)),
}


def build(name: str, a: Any) -> tuple[Any, Any, tuple[FamilyStep, ...]]:
    steps: tuple[FamilyStep, ...]
    exponential = sp.exp(X)
    if name == "linear_exponential":
        primitive = a * exponential * (X - 1)
        steps = (FamilyStep("parts", a * X * exponential - sp.Integral(a * exponential, X)),)
        integrand = a * X * exponential
    elif name == "quadratic_exponential":
        primitive = a * exponential * (X**2 - 2 * X + 2)
        steps = (
            FamilyStep("parts", a * X**2 * exponential - sp.Integral(2 * a * X * exponential, X)),
            FamilyStep(
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
            FamilyStep(
                "parts", a * exponential * sp.sin(X) - sp.Integral(a * exponential * sp.cos(X), X)
            ),
            FamilyStep("repeat_parts", boundary - sp.Integral(integrand, X)),
            FamilyStep("solve_cycle", boundary / 2),
        )
    return integrand, primitive, steps
