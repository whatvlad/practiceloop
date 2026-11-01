"""Polynomial and rational indefinite integrals."""

import sympy as sp

from app.engine.answers._symbolic import X, is_primitive
from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.engine.answers.expression import ExpressionAnswer
from app.engine.blocks.polynomial import Polynomial
from app.engine.generators.common import Seed, code
from app.engine.generators.partial_fractions import PartialFractions
from app.engine.models import Step, Task
from app.engine.prng import DeterministicRNG


class IndefiniteIntegral:
    version = "indefinite-v1"
    params = Seed
    answer = AntiderivativeAnswer
    requires = ("partial-fractions-v1",)

    def draw(self, seed: int) -> Seed:
        return Seed(seed=seed)

    def build(self, params: Seed) -> Task:
        rng = DeterministicRNG(params.seed)
        if rng.randbelow(2):
            partial = PartialFractions()
            source = partial.build(partial.draw(params.seed))
            if not isinstance(source.answer, ExpressionAnswer):
                raise ValueError("Unexpected partial fraction answer")
            decomposition = source.answer.expected
            integrand = sp.cancel(sp.together(decomposition))
            pole = source.metadata["pole"]
            if type(pole) is not int:
                raise ValueError("Invalid pole")
            domain = sp.Union(
                sp.Interval.open(-sp.oo, -pole),
                sp.Interval.open(-pole, pole),
                sp.Interval.open(pole, sp.oo),
            )
            primitive = sp.Add(
                *(
                    term.as_numer_denom()[0] * sp.log(sp.Abs(term.as_numer_denom()[1]))
                    for term in sp.Add.make_args(decomposition)
                )
            )
            steps = source.steps
        else:
            integrand = Polynomial.draw(rng, 1 + rng.randbelow(4)).expression(X)
            primitive = sp.integrate(integrand, X)
            domain = sp.S.Reals
            steps = ()
        if is_primitive(primitive, integrand, domain) != "yes":
            raise ValueError("Invalid antiderivative")
        return Task(
            statement=rf"Find \(\int {sp.latex(integrand)}\,dx\).",
            steps=steps + (Step("integrate", rf"{sp.latex(primitive)} + C"),),
            answer=AntiderivativeAnswer(integrand, primitive, domain),
            metadata={},
            code=code(self, "INT", "indefinite", params.seed),
            generator_version=self.version,
        )
