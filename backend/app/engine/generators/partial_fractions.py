"""Decompose a bounded rational function with two simple real poles."""

import sympy as sp

from app.engine.answers._symbolic import X
from app.engine.answers.expression import ExpressionAnswer
from app.engine.blocks.rational import PartialFractionRational
from app.engine.generators.common import Seed, code
from app.engine.models import Step, Task
from app.engine.prng import DeterministicRNG


class PartialFractions:
    version = "partial-fractions-v1"
    params = Seed
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()

    def draw(self, seed: int) -> Seed:
        return Seed(seed=seed)

    def build(self, params: Seed) -> Task:
        rng = DeterministicRNG(params.seed)
        pole = 2 + rng.randbelow(5)
        numerator = 1 + rng.randbelow(6)
        if rng.randbelow(2):
            numerator = -numerator
        block = PartialFractionRational(poles=(-pole, pole), numerators=(numerator, numerator))
        combined, decomposition = block.combined(X), block.decomposition(X)
        if sp.cancel(combined - decomposition) != 0:
            raise ValueError("Invalid partial fraction decomposition")
        return Task(
            statement=rf"Decompose into partial fractions: \({sp.latex(combined)}\).",
            steps=(Step("decompose", rf"{sp.latex(combined)} = {sp.latex(decomposition)}"),),
            answer=ExpressionAnswer(decomposition, {"x": "real"}),
            metadata={"pole": pole},
            code=code(self, "PFR", "partial-fractions", params.seed),
            generator_version=self.version,
        )
