"""Bounded univariate polynomials with integer coefficients."""

from typing import Any

import sympy as sp
from pydantic import Field, field_validator

from app.engine.blocks.integers import IntegerRange
from app.engine.models import Parameters
from app.engine.prng import DeterministicRNG

_MAX_DEGREE = 5
_MAX_COEFFICIENT = 100_000


class Polynomial(Parameters):
    # Constant term first; the last coefficient is the nonzero leading term.
    coefficients: tuple[int, ...] = Field(min_length=1, max_length=_MAX_DEGREE + 1)

    @field_validator("coefficients")
    @classmethod
    def validate_coefficients(cls, values: tuple[int, ...]) -> tuple[int, ...]:
        if values[-1] == 0:
            raise ValueError("Leading coefficient must be nonzero")
        if any(abs(value) > _MAX_COEFFICIENT for value in values):
            raise ValueError("Coefficient outside the supported range")
        return values

    @classmethod
    def from_roots(cls, roots: tuple[int, ...], leading: int = 1) -> "Polynomial":
        if not isinstance(roots, tuple) or len(roots) > _MAX_DEGREE:
            raise ValueError("Roots must be a tuple of at most five integers")
        if type(leading) is not int or not 1 <= abs(leading) <= 6:
            raise ValueError("Leading coefficient must be a nonzero integer from -6 to 6")
        if any(type(root) is not int or abs(root) > 6 for root in roots):
            raise ValueError("Roots must be integers from -6 to 6")
        coefficients = [leading]
        for root in roots:
            next_coefficients = [0] * (len(coefficients) + 1)
            for index, coefficient in enumerate(coefficients):
                next_coefficients[index] -= root * coefficient
                next_coefficients[index + 1] += coefficient
            coefficients = next_coefficients
        return cls(coefficients=tuple(coefficients))

    @classmethod
    def draw(cls, rng: DeterministicRNG, degree: int) -> "Polynomial":
        if type(degree) is not int or not 0 <= degree <= _MAX_DEGREE:
            raise ValueError("Degree must be an integer from 0 through 5")
        coefficient = IntegerRange(minimum=-6, maximum=6)
        leading = IntegerRange(minimum=-6, maximum=6, exclude=(0,))
        return cls(
            coefficients=tuple(coefficient.draw(rng) for _ in range(degree)) + (leading.draw(rng),)
        )

    def expression(self, variable: Any) -> Any:
        return sp.Add(
            *(coefficient * variable**power for power, coefficient in enumerate(self.coefficients))
        )
