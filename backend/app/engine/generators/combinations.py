"""Combination counts using integer arithmetic."""

from math import comb
from typing import Self

from pydantic import Field, model_validator

from app.engine.answers.number import NumberAnswer
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task
from app.engine.prng import DeterministicRNG


class CombinationParams(Drawn):
    n: int = Field(ge=2, le=20)
    k: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_k(self) -> Self:
        if self.k > self.n:
            raise ValueError("k must not exceed n")
        return self


class Combinations:
    version = "combinations-v1"
    prefix = "CMB"
    family = "combinations"
    code_version = 1
    params = CombinationParams
    answer = NumberAnswer
    requires: tuple[str, ...] = ()
    step_text = {"combinations": "Evaluate the binomial coefficient."}

    def draw(self, seed: int) -> CombinationParams:
        rng = DeterministicRNG(seed)
        n = 2 + rng.randbelow(19)
        return CombinationParams(seed=seed, n=n, k=rng.randbelow(n + 1))

    def build(self, params: CombinationParams) -> Task:
        n, k = params.n, params.k
        value = comb(n, k)
        return Task(
            statement=rf"Calculate \(\binom{{{n}}}{{{k}}}\).",
            steps=(Step("combinations", rf"\binom{{{n}}}{{{k}}} = {value}"),),
            answer=NumberAnswer(value),
            metadata={"n": n, "k": k},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )
