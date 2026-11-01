"""Native substitution integral forms; formulas retained from the verified curriculum."""

from typing import Any

import sympy as sp

from app.engine.answers._symbolic import X
from app.engine.blocks.integral_forms.models import MethodStep, MethodTemplate

TEMPLATES = {
    **{
        f"quadratic_{kind}": MethodTemplate(1, sp.S.Reals, "substitution")
        for kind in ("sine", "cosine", "exp")
    },
    **{
        f"linear_{kind}": MethodTemplate(2, sp.S.Reals, "substitution")
        for kind in ("sine", "cosine", "exp")
    },
    "visible_pair": MethodTemplate(1, sp.S.Reals, "substitution"),
    "affine_factor": MethodTemplate(2, sp.S.Reals, "substitution", ("constant_factor",)),
    "polynomial_inner": MethodTemplate(3, sp.S.Reals, "substitution"),
    "factor_square": MethodTemplate(4, sp.S.Reals, "substitution", ("factor",)),
    "identity_nested": MethodTemplate(5, sp.S.Reals, "substitution", ("double_angle",)),
}


def build(
    name: str, a: Any, secondary: int = 1, scale: int = 2
) -> tuple[Any, Any, tuple[MethodStep, ...]]:
    u, v = sp.symbols("u v", real=True)
    steps: list[MethodStep] = []
    if name.startswith(("quadratic_", "linear_")):
        inner = X**2 + secondary if name.startswith("quadratic_") else scale * X + secondary
        function = {"sine": sp.sin, "cosine": sp.cos, "exp": sp.exp}[name.split("_")[1]]
        outer = a * function(u)
    elif name == "visible_pair":
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
        steps.append(MethodStep("factor", sp.Integral(a * X * (X**2 + 1) ** 2, X)))
    elif name == "identity_nested":
        integrand = a * X * sp.sin(X**2) * sp.sin(2 * X**2)
        steps.append(
            MethodStep("identity", sp.Integral(2 * a * X * sp.sin(X**2) ** 2 * sp.cos(X**2), X))
        )
    steps.append(
        MethodStep("substitution_integral", sp.Subs(sp.Integral(sp.diff(outer, u), u), u, inner))
    )
    if name == "identity_nested":
        steps.append(
            MethodStep("nested_substitution", sp.Subs(sp.Integral(a * v**2, v), v, sp.sin(inner)))
        )
    steps.append(MethodStep("substitute_back", sp.Subs(outer, u, inner)))
    return integrand, primitive, tuple(steps)
