"""#77: substitution-v2; existing substitution-v1 preview records stay unchanged."""

from typing import Any

import sympy as sp

from app.generators.basic import X
from app.generators.families import FamilyStep, FamilyTemplate

TEMPLATES = {
    "visible_pair": FamilyTemplate(1, sp.S.Reals, "substitution"),
    "affine_factor": FamilyTemplate(2, sp.S.Reals, "substitution", ("constant_factor",)),
    "polynomial_inner": FamilyTemplate(3, sp.S.Reals, "substitution"),
    "factor_square": FamilyTemplate(4, sp.S.Reals, "substitution", ("factor",)),
    "identity_nested": FamilyTemplate(5, sp.S.Reals, "substitution", ("double_angle",)),
}


def build(name: str, a: Any) -> tuple[Any, Any, tuple[FamilyStep, ...]]:
    u, v = sp.symbols("u v", real=True)
    steps: list[FamilyStep] = []
    if name == "visible_pair":
        inner, outer = X**2, a * sp.sin(u)
    elif name == "affine_factor":
        inner, outer = 2 * X + 1, a * sp.sin(u) / 2
    elif name == "polynomial_inner":
        inner, outer = X**3, a * sp.exp(u)
    elif name == "factor_square":
        inner, outer = X**2 + 1, a * u**3 / 6
    else:
        inner, outer = X**2, a * sp.sin(u) ** 3 / 3
    primitive = outer.subs(u, inner)
    integrand = sp.diff(primitive, X)
    if name == "factor_square":
        integrand = a * X * (X**4 + 2 * X**2 + 1)
        steps.append(FamilyStep("factor", sp.Integral(a * X * (X**2 + 1) ** 2, X)))
    elif name == "identity_nested":
        integrand = a * X * sp.sin(X**2) * sp.sin(2 * X**2)
        steps.append(
            FamilyStep("identity", sp.Integral(2 * a * X * sp.sin(X**2) ** 2 * sp.cos(X**2), X))
        )
    steps.append(
        FamilyStep("substitution_integral", sp.Subs(sp.Integral(sp.diff(outer, u), u), u, inner))
    )
    if name == "identity_nested":
        steps.append(
            FamilyStep("nested_substitution", sp.Subs(sp.Integral(a * v**2, v), v, sp.sin(inner)))
        )
    steps.append(FamilyStep("substitute_back", sp.Subs(outer, u, inner)))
    return integrand, primitive, tuple(steps)
