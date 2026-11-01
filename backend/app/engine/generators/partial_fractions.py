"""Decompose a bounded rational function with two simple real poles."""

from dataclasses import dataclass
from typing import Any, Self

import sympy as sp
from pydantic import Field, model_validator

from app.engine.answers._symbolic import X
from app.engine.answers.expression import ExpressionAnswer
from app.engine.blocks.rational import PartialFractionRational
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task
from app.engine.prng import DeterministicRNG


class PartialFractionParams(Drawn):
    # The fraction is numerator/(x + pole) + numerator/(x - pole).
    pole: int = Field(ge=2, le=6)
    numerator: int

    @model_validator(mode="after")
    def validate_numerator(self) -> Self:
        if not 1 <= abs(self.numerator) <= 6:
            raise ValueError("Numerator must be a nonzero integer from -6 to 6")
        return self


@dataclass(frozen=True, slots=True)
class Decomposition:
    """What a composing generator may use from a partial fraction problem."""

    combined: Any
    decomposition: Any
    domain: Any
    steps: tuple[Step, ...]


class PartialFractions:
    version = "partial-fractions-v1"
    prefix = "PFR"
    family = "partial-fractions"
    code_version = 1
    params = PartialFractionParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    step_text = {"decompose": "Split the fraction into partial fractions."}

    def draw(self, seed: int) -> PartialFractionParams:
        rng = DeterministicRNG(seed)
        pole = 2 + rng.randbelow(5)
        numerator = 1 + rng.randbelow(6)
        if rng.randbelow(2):
            numerator = -numerator
        return PartialFractionParams(seed=seed, pole=pole, numerator=numerator)

    def decompose(self, params: PartialFractionParams) -> Decomposition:
        pole = params.pole
        block = PartialFractionRational(
            poles=(-pole, pole), numerators=(params.numerator, params.numerator)
        )
        combined, decomposition = block.combined(X), block.decomposition(X)
        if sp.cancel(combined - decomposition) != 0:
            raise ValueError("Invalid partial fraction decomposition")
        return Decomposition(
            combined=combined,
            decomposition=decomposition,
            domain=sp.Union(
                sp.Interval.open(-sp.oo, -pole),
                sp.Interval.open(-pole, pole),
                sp.Interval.open(pole, sp.oo),
            ),
            steps=(Step("decompose", rf"{sp.latex(combined)} = {sp.latex(decomposition)}"),),
        )

    def build(self, params: PartialFractionParams) -> Task:
        result = self.decompose(params)
        return Task(
            statement=rf"Decompose into partial fractions: \({sp.latex(result.combined)}\).",
            steps=result.steps,
            answer=ExpressionAnswer(result.decomposition, {"x": "real"}),
            metadata={"pole": params.pole},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )
