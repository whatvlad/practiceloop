"""Bounded, immutable forms with verified primitives and explicit real domains."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import Any, Literal

import sympy as sp
from pydantic import Field, model_validator

from app.engine.answers._symbolic import X, components
from app.engine.blocks.integral_forms import basic, parts, rational, substitution, trigonometric
from app.engine.blocks.integral_forms.models import MethodStep
from app.engine.blocks.rational_proof import certifies_rational_primitive
from app.engine.models import Parameters
from app.engine.prng import DeterministicRNG

type Family = Literal["basic", "substitution", "parts", "rational", "trigonometric"]
METHODS = {
    "basic": basic,
    "substitution": substitution,
    "parts": parts,
    "rational": rational,
    "trigonometric": trigonometric,
}

# Bounds remain those of the approved curriculum; all lie inside the form's domain.
BOUNDS: dict[tuple[str, str], tuple[Any, Any]] = {
    ("basic", "power"): (0, 2),
    ("basic", "exponential"): (0, 1),
    ("basic", "sum"): (0, 1),
    ("basic", "reciprocal"): (1, sp.E),
    ("basic", "fractional_power"): (1, 4),
    ("basic", "expand_square"): (0, 1),
    ("substitution", "polynomial_inner"): (0, 1),
    ("substitution", "factor_square"): (0, 1),
    ("parts", "linear_exponential"): (0, 1),
    ("parts", "quadratic_exponential"): (0, 1),
    ("parts", "cyclic_sine"): (0, sp.pi),
    ("rational", "linear_denominator"): (1, 2),
    ("rational", "denominator_derivative"): (0, 1),
    ("rational", "distinct_factors"): (1, 2),
    ("rational", "repeated_factor"): (1, 2),
    ("rational", "division_then_fractions"): (1, 2),
    ("trigonometric", "sine"): (0, sp.pi),
    ("trigonometric", "double_argument"): (0, sp.pi / 2),
    ("trigonometric", "odd_power"): (0, sp.pi),
    ("trigonometric", "even_power"): (0, sp.pi),
    ("trigonometric", "identity_substitution"): (0, sp.pi / 2),
}


@dataclass(frozen=True)
class IntegralData:
    integrand: Any
    primitive: Any
    domain: Any
    steps: tuple[MethodStep, ...]
    lower: Any = None
    upper: Any = None
    value: Any = None


class IntegralForm(Parameters):
    family: Family
    template: str = Field(min_length=1, max_length=32)
    coefficient: Literal[-3, -2, -1, 1, 2, 3]
    secondary: int = Field(default=1, ge=1, le=2)
    power: int = Field(default=2, ge=2, le=4)

    @model_validator(mode="after")
    def canonical(self) -> IntegralForm:
        if self.template not in METHODS[self.family].TEMPLATES:
            raise ValueError("Unknown integral form")
        variable_substitution = self.family == "substitution" and self.template.startswith(
            ("quadratic_", "linear_")
        )
        if variable_substitution:
            if self.power not in ((2, 3) if self.template.startswith("linear_") else (2,)):
                raise ValueError("Invalid substitution scale")
        elif self.family != "basic":
            if self.secondary != 1 or self.power != 2:
                raise ValueError("Unused parameters must retain canonical defaults")
        else:
            if (
                self.template not in {"sum", "expand_square", "expand_and_split"}
                and self.secondary != 1
            ):
                raise ValueError("Unused secondary parameter")
            if self.template not in {"power", "sum", "negative_power"} and self.power != 2:
                raise ValueError("Unused power")
            if self.template == "expand_and_split" and self.coefficient < 0:
                raise ValueError("Positive coefficient prevents cancellation")
        return self

    @property
    def difficulty(self) -> int:
        return int(METHODS[self.family].TEMPLATES[self.template].difficulty)

    @classmethod
    def draw(cls, rng: DeterministicRNG, family: Family, bounded: bool) -> IntegralForm:
        names = [n for n in METHODS[family].TEMPLATES if not bounded or (family, n) in BOUNDS]
        levels = sorted({METHODS[family].TEMPLATES[n].difficulty for n in names})
        level = levels[rng.randbelow(len(levels))]
        names = [n for n in names if METHODS[family].TEMPLATES[n].difficulty == level]
        name = names[rng.randbelow(len(names))]
        coefficients = (1, 2, 3) if name == "expand_and_split" else (-3, -2, -1, 1, 2, 3)
        return cls(
            family=family,
            template=name,
            coefficient=coefficients[rng.randbelow(len(coefficients))],  # type: ignore[arg-type]
            secondary=1 + rng.randbelow(2)
            if not bounded
            and (
                (family == "basic" and name in {"sum", "expand_square", "expand_and_split"})
                or (family == "substitution" and name.startswith(("quadratic_", "linear_")))
            )
            else 1,
            power=(
                2 + rng.randbelow(2)
                if family == "substitution" and name.startswith("linear_")
                else 2 + rng.randbelow(3)
                if family == "basic" and not bounded and name in {"power", "sum", "negative_power"}
                else 2
            ),
        )

    def evaluate(self, bounded: bool = False) -> IntegralData:
        return _evaluate(self, bounded)


@cache
def _evaluate(form: IntegralForm, bounded: bool) -> IntegralData:
    a = sp.Integer(form.coefficient)
    if form.family == "basic":
        integrand, primitive, steps = basic.build(
            form.template, a, sp.Integer(form.secondary), form.power
        )
    elif form.family == "substitution":
        integrand, primitive, steps = substitution.build(
            form.template, a, form.secondary, form.power
        )
    else:
        method = {
            "substitution": substitution,
            "parts": parts,
            "rational": rational,
            "trigonometric": trigonometric,
        }[form.family]
        integrand, primitive, steps = method.build(form.template, a)
    domain = METHODS[form.family].TEMPLATES[form.template].domain
    # Exact rational certificates or component-wise proof of every displayed step.
    for expression, antiderivative in [
        (primitive, True),
        *((step.expression, not isinstance(step, basic.BasicStep)) for step in steps),
    ]:
        if antiderivative and certifies_rational_primitive(expression, integrand, X, domain):
            continue
        for replacement, variable, _ in components(domain):
            difference = expression.subs(X, replacement)
            if antiderivative:
                difference = sp.diff(difference, variable) / sp.diff(replacement, variable)
            if sp.simplify(sp.trigsimp(difference - integrand.subs(X, replacement))) != 0:
                raise ValueError("Integral form failed exact verification")
    if not bounded:
        return IntegralData(integrand, primitive, domain, steps)
    lower, upper = (sp.sympify(v) for v in BOUNDS[(form.family, form.template)])
    if sp.Interval(lower, upper).is_subset(domain) is not True:
        raise ValueError("Bounds cross the real domain")
    value = a * sp.simplify((primitive.subs(X, upper) - primitive.subs(X, lower)) / a)
    if value.is_real is not True or value.has(sp.nan, sp.zoo, sp.oo, -sp.oo):
        raise ValueError("Definite result must be finite and real")
    return IntegralData(integrand, primitive, domain, steps, lower, upper, value)
