"""Bounded integer choices, including exclusions such as zero or known poles."""

from typing import Self

from pydantic import Field, model_validator

from app.engine.models import Parameters
from app.engine.prng import DeterministicRNG


class IntegerRange(Parameters):
    minimum: int = Field(ge=-12, le=12)
    maximum: int = Field(ge=-12, le=12)
    exclude: tuple[int, ...] = ()

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.minimum > self.maximum:
            raise ValueError("Minimum must not exceed maximum")
        if len(set(self.exclude)) != len(self.exclude):
            raise ValueError("Excluded values must be distinct")
        if any(value < self.minimum or value > self.maximum for value in self.exclude):
            raise ValueError("Excluded values must be within the range")
        if len(self.exclude) == self.maximum - self.minimum + 1:
            raise ValueError("At least one value must remain")
        return self

    def draw(self, rng: DeterministicRNG) -> int:
        allowed = [
            value for value in range(self.minimum, self.maximum + 1) if value not in self.exclude
        ]
        return allowed[rng.randbelow(len(allowed))]
