"""#79: rational-v1 with exact pole exclusions and logarithms of absolute values."""

from typing import Any

import sympy as sp

from app.generators.basic import X
from app.generators.families import FamilyStep, FamilyTemplate

_POLES = sp.S.Reals - sp.FiniteSet(-1, 0)
TEMPLATES = {
    "linear_denominator": FamilyTemplate(1, sp.S.Reals - sp.FiniteSet(0), "logarithm"),
    "denominator_derivative": FamilyTemplate(2, sp.S.Reals, "substitution"),
    "distinct_factors": FamilyTemplate(3, _POLES, "partial_fractions"),
    "repeated_factor": FamilyTemplate(4, _POLES, "partial_fractions", ("repeated_factor",)),
    "division_then_fractions": FamilyTemplate(
        5, _POLES, "partial_fractions", ("polynomial_division",)
    ),
}


def build(name: str, a: Any) -> tuple[Any, Any, tuple[FamilyStep, ...]]:
    log_x, log_next = sp.log(sp.Abs(X)), sp.log(sp.Abs(X + 1))
    steps: list[FamilyStep] = []
    if name == "linear_denominator":
        integrand, primitive = a / X, a * log_x
    elif name == "denominator_derivative":
        u = sp.Symbol("u", positive=True)
        integrand, primitive = 2 * a * X / (X**2 + 1), a * sp.log(X**2 + 1)
        steps.append(
            FamilyStep("substitution_integral", sp.Subs(sp.Integral(a / u, u), u, X**2 + 1))
        )
    elif name == "distinct_factors":
        integrand = a / (X * (X + 1))
        primitive = a * (log_x - log_next)
        steps.append(FamilyStep("partial_fractions", sp.Integral(a / X - a / (X + 1), X)))
    elif name == "repeated_factor":
        integrand = a / (X * (X + 1) ** 2)
        primitive = a * (log_x - log_next + 1 / (X + 1))
        steps.append(
            FamilyStep("partial_fractions", sp.Integral(a / X - a / (X + 1) - a / (X + 1) ** 2, X))
        )
    else:
        integrand = a * (X**3 + X + 1) / (X * (X + 1))
        primitive = a * (X**2 / 2 - X + log_x + log_next)
        steps.extend(
            (
                FamilyStep(
                    "polynomial_division", sp.Integral(a * (X - 1 + (2 * X + 1) / (X * (X + 1))), X)
                ),
                FamilyStep("partial_fractions", sp.Integral(a * (X - 1 + 1 / X + 1 / (X + 1)), X)),
            )
        )
    return integrand, primitive, tuple(steps)
