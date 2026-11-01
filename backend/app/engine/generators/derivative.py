"""Polynomial and rational derivatives."""

import sympy as sp

from app.engine.answers._symbolic import X
from app.engine.answers.derivative import DerivativeAnswer
from app.engine.answers.expression import ExpressionAnswer
from app.engine.blocks.polynomial import Polynomial
from app.engine.generators.common import Seed, code
from app.engine.generators.partial_fractions import PartialFractions
from app.engine.models import Step, Task
from app.engine.prng import DeterministicRNG


class Derivative:
    version = "derivative-v1"
    params = Seed
    answer = DerivativeAnswer
    requires = ("partial-fractions-v1",)

    def draw(self, seed: int) -> Seed:
        return Seed(seed=seed)

    def build(self, params: Seed) -> Task:
        rng = DeterministicRNG(params.seed)
        if rng.randbelow(2):
            partial = PartialFractions().build(params)
            if not isinstance(partial.answer, ExpressionAnswer):
                raise ValueError("Unexpected partial fraction answer")
            expression = sp.cancel(sp.together(partial.answer.expected))
            pole = partial.metadata["pole"]
            if type(pole) is not int:
                raise ValueError("Invalid pole")
            domain = sp.Union(
                sp.Interval.open(-sp.oo, -pole),
                sp.Interval.open(-pole, pole),
                sp.Interval.open(pole, sp.oo),
            )
        else:
            expression = Polynomial.draw(rng, 1 + rng.randbelow(4)).expression(X)
            domain = sp.S.Reals
        result = sp.diff(expression, X)
        return Task(
            statement=rf"Differentiate \({sp.latex(expression)}\).",
            steps=(
                Step(
                    "differentiate",
                    rf"\frac{{d}}{{dx}}\left({sp.latex(expression)}\right) = {sp.latex(result)}",
                ),
            ),
            answer=DerivativeAnswer(result, domain),
            metadata={"function": str(expression).replace("**", "^")},
            code=code(self, "DRV", "derivative", params.seed),
            generator_version=self.version,
        )
