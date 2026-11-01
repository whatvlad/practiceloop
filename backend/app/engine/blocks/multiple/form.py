"""Strict multiple-integral forms with exact primary setup verification."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import Literal

import sympy as sp
from pydantic import Field, model_validator

from app.engine.answers._symbolic import X
from app.engine.blocks.multiple import double, triple
from app.engine.blocks.multiple.setup import THETA, R, Setup, Y, integrate_setup
from app.engine.blocks.multiple.values import is_clean_value
from app.engine.models import Parameters, Step
from app.engine.prng import DeterministicRNG


@dataclass(frozen=True)
class MultipleData:
    statement: str
    steps: tuple[Step, ...]
    setup: Setup
    value: object


class MultipleForm(Parameters):
    dimension: Literal[2, 3]
    template: str = Field(min_length=1, max_length=32)
    variant: int = Field(ge=0, le=9)
    coefficient: Literal[-3, -2, -1, 1, 2, 3]

    @model_validator(mode="after")
    def valid_variant(self) -> MultipleForm:
        templates = double.TEMPLATES if self.dimension == 2 else triple.TEMPLATES
        if self.template not in templates:
            raise ValueError("Unknown multiple-integral template")
        if self.variant >= len(templates[self.template].variants):
            raise ValueError("Unknown multiple-integral variant")
        return self

    @property
    def difficulty(self) -> int:
        templates = double.TEMPLATES if self.dimension == 2 else triple.TEMPLATES
        return templates[self.template].difficulty

    @classmethod
    def draw(cls, rng: DeterministicRNG, dimension: Literal[2, 3]) -> MultipleForm:
        templates = double.TEMPLATES if dimension == 2 else triple.TEMPLATES
        level = 1 + rng.randbelow(5)
        names = [name for name, template in templates.items() if template.difficulty == level]
        name = names[rng.randbelow(len(names))]
        coefficients = (-3, -2, -1, 1, 2, 3)
        return cls(
            dimension=dimension,
            template=name,
            variant=rng.randbelow(len(templates[name].variants)),
            coefficient=coefficients[rng.randbelow(len(coefficients))],  # type: ignore[arg-type]
        )

    def evaluate(self) -> MultipleData:
        return _evaluate(self)


@cache
def _verify(dimension: int, name: str, index: int) -> None:
    variant: double.DoubleVariant | triple.TripleVariant
    if dimension == 2:
        variant = double.TEMPLATES[name].variants[index]
    else:
        variant = triple.TEMPLATES[name].variants[index]
    setup = variant.solution
    expression = variant.problem_integrand()
    if setup.system in {"polar", "cylindrical"}:
        expression = expression.subs(
            {X: R * sp.cos(THETA), Y: R * sp.sin(THETA)}, simultaneous=True
        )
    if sp.simplify(expression - setup.integrand) != 0:
        raise ValueError("Coordinate change differs from the stated integrand")
    if sp.simplify(integrate_setup(setup) - variant.value) != 0:
        raise ValueError("Multiple-integral value failed exact verification")
    if not is_clean_value(variant.value):
        raise ValueError("Unclean multiple-integral value")


@cache
def _evaluate(form: MultipleForm) -> MultipleData:
    _verify(form.dimension, form.template, form.variant)
    a = sp.Integer(form.coefficient)
    if form.dimension == 2:
        template = double.TEMPLATES[form.template]
        variant = template.variants[form.variant]
        statement = double._statement(template, variant, a)
        value = a * variant.value
        steps = double._steps(variant, a, value)
        setup = variant.solution.scaled(a)
    else:
        triple_template = triple.TEMPLATES[form.template]
        triple_variant = triple_template.variants[form.variant]
        statement = triple._statement(triple_template, triple_variant, a)
        value = a * triple_variant.value
        steps = triple._steps(triple_variant, a, value)
        setup = triple_variant.solution.scaled(a)
    if not is_clean_value(value):
        raise ValueError("Scaled multiple-integral value is not clean")
    return MultipleData(
        statement,
        tuple(Step(step["key"], step["latex"]) for step in steps),
        setup,
        value,
    )
