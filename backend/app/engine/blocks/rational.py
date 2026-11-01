"""Rational functions built from simple real partial fractions."""

from typing import Any, Self

import sympy as sp
from pydantic import Field, model_validator

from app.engine.blocks.integers import IntegerRange
from app.engine.models import Parameters
from app.engine.prng import DeterministicRNG


class PartialFractionRational(Parameters):
    poles: tuple[int, ...] = Field(min_length=1, max_length=4)
    numerators: tuple[int, ...] = Field(min_length=1, max_length=4)

    @model_validator(mode="after")
    def validate_terms(self) -> Self:
        if len(self.poles) != len(self.numerators):
            raise ValueError("Each pole must have one numerator")
        if len(set(self.poles)) != len(self.poles):
            raise ValueError("Poles must be distinct")
        if any(abs(pole) > 6 for pole in self.poles):
            raise ValueError("Poles must be integers from -6 to 6")
        if any(not 1 <= abs(value) <= 6 for value in self.numerators):
            raise ValueError("Numerators must be nonzero integers from -6 to 6")
        return self

    @classmethod
    def draw(cls, rng: DeterministicRNG, terms: int) -> "PartialFractionRational":
        if type(terms) is not int or not 1 <= terms <= 4:
            raise ValueError("Number of terms must be an integer from 1 through 4")
        available = list(range(-6, 7))
        numerator = IntegerRange(minimum=-6, maximum=6, exclude=(0,))
        poles = []
        numerators = []
        for _ in range(terms):
            poles.append(available.pop(rng.randbelow(len(available))))
            numerators.append(numerator.draw(rng))
        return cls(poles=tuple(poles), numerators=tuple(numerators))

    def decomposition(self, variable: Any) -> Any:
        return sp.Add(
            *(
                sp.Rational(numerator) / (variable - pole)
                for pole, numerator in zip(self.poles, self.numerators, strict=True)
            )
        )

    def combined(self, variable: Any) -> Any:
        return sp.cancel(sp.together(self.decomposition(variable)))
