"""Polynomial and rational derivatives."""

import sympy as sp

from app.engine.answers._symbolic import X
from app.engine.answers.derivative import DerivativeAnswer
from app.engine.blocks.polynomial import Polynomial
from app.engine.codes import encode
from app.engine.generators.partial_fractions import PartialFractionParams, PartialFractions
from app.engine.models import Drawn, Step, Task
from app.engine.prng import DeterministicRNG


class DerivativeParams(Drawn):
    # A rational function is a partial fraction problem drawn from the same seed.
    function: PartialFractionParams | Polynomial

    @property
    def rational(self) -> bool:
        return isinstance(self.function, PartialFractionParams)


class Derivative:
    version = "derivative-v1"
    prefix = "DRV"
    family = "derivative"
    code_version = 1
    params = DerivativeParams
    answer = DerivativeAnswer
    requires = ("partial-fractions-v1",)
    step_text = {"differentiate": "Differentiate the function."}

    def draw(self, seed: int) -> DerivativeParams:
        rng = DeterministicRNG(seed)
        if rng.randbelow(2):
            return DerivativeParams(seed=seed, function=PartialFractions().draw(seed))
        return DerivativeParams(seed=seed, function=Polynomial.draw(rng, 1 + rng.randbelow(4)))

    def build(self, params: DerivativeParams) -> Task:
        function = params.function
        if isinstance(function, PartialFractionParams):
            partial = PartialFractions().decompose(function)
            expression = sp.cancel(sp.together(partial.decomposition))
            domain = partial.domain
        else:
            expression = function.expression(X)
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
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )
