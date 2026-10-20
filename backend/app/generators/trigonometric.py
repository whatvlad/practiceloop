"""#80: trigonometric-v1, structural difficulty with small exact coefficients."""

from typing import Any

import sympy as sp

from app.generators.basic import X
from app.generators.families import FamilyStep, FamilyTemplate

TEMPLATES = {
    "sine": FamilyTemplate(1, sp.S.Reals, "direct"),
    "double_argument": FamilyTemplate(2, sp.S.Reals, "constant_factor"),
    "odd_power": FamilyTemplate(3, sp.S.Reals, "substitution", ("split_odd_power",)),
    "even_power": FamilyTemplate(4, sp.S.Reals, "trigonometric_identity"),
    "identity_substitution": FamilyTemplate(5, sp.S.Reals, "substitution", ("double_angle",)),
}


def build(name: str, a: Any) -> tuple[Any, Any, tuple[FamilyStep, ...]]:
    u = sp.Symbol("u", real=True)
    steps: list[FamilyStep] = []
    if name == "sine":
        integrand, primitive = a * sp.sin(X), -a * sp.cos(X)
    elif name == "double_argument":
        integrand, primitive = a * sp.sin(2 * X), -a * sp.cos(2 * X) / 2
        steps.append(
            FamilyStep(
                "substitution_integral", sp.Subs(sp.Integral(a * sp.sin(u) / 2, u), u, 2 * X)
            )
        )
    elif name == "odd_power":
        integrand = a * sp.sin(X) ** 3
        primitive = a * (sp.cos(X) ** 3 / 3 - sp.cos(X))
        steps.extend(
            (
                FamilyStep("identity", sp.Integral(a * sp.sin(X) * (1 - sp.cos(X) ** 2), X)),
                FamilyStep(
                    "substitution_integral", sp.Subs(sp.Integral(a * (u**2 - 1), u), u, sp.cos(X))
                ),
            )
        )
    elif name == "even_power":
        integrand = a * sp.sin(X) ** 2
        primitive = a * (X / 2 - sp.sin(2 * X) / 4)
        steps.append(FamilyStep("identity", sp.Integral(a * (1 - sp.cos(2 * X)) / 2, X)))
    else:
        integrand = a * (1 - sp.cos(2 * X)) * sp.cos(X) / 2
        primitive = a * sp.sin(X) ** 3 / 3
        steps.extend(
            (
                FamilyStep("identity", sp.Integral(a * sp.sin(X) ** 2 * sp.cos(X), X)),
                FamilyStep(
                    "substitution_integral", sp.Subs(sp.Integral(a * u**2, u), u, sp.sin(X))
                ),
            )
        )
    return integrand, primitive, tuple(steps)
