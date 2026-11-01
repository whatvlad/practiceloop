"""Polynomial and rational indefinite integrals."""

from dataclasses import dataclass
from typing import Any

import sympy as sp

from app.engine.answers._symbolic import X, is_primitive
from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.engine.blocks.polynomial import Polynomial
from app.engine.codes import encode
from app.engine.generators.partial_fractions import PartialFractionParams, PartialFractions
from app.engine.models import Drawn, Step, Task, TaskGenerator
from app.engine.prng import DeterministicRNG


class IndefiniteParams(Drawn):
    # A rational integrand is a partial fraction problem drawn from the same seed.
    function: PartialFractionParams | Polynomial

    @property
    def rational(self) -> bool:
        return isinstance(self.function, PartialFractionParams)


@dataclass(frozen=True, slots=True)
class Integral:
    """What a composing generator may use from an indefinite integral."""

    integrand: Any
    primitive: Any
    domain: Any
    steps: tuple[Step, ...]


class IndefiniteIntegral:
    version = "indefinite-v1"
    prefix = "INT"
    family = "indefinite"
    code_version = 1
    params = IndefiniteParams
    answer = AntiderivativeAnswer
    requires = ("partial-fractions-v1",)
    step_text = {**PartialFractions.step_text, "integrate": "Integrate term by term."}

    def draw(self, seed: int) -> IndefiniteParams:
        rng = DeterministicRNG(seed)
        if rng.randbelow(2):
            return IndefiniteParams(seed=seed, function=PartialFractions().draw(seed))
        return IndefiniteParams(seed=seed, function=Polynomial.draw(rng, 1 + rng.randbelow(4)))

    def integrate(self, params: IndefiniteParams) -> Integral:
        function = params.function
        if isinstance(function, PartialFractionParams):
            source = PartialFractions().decompose(function)
            decomposition = source.decomposition
            integrand = sp.cancel(sp.together(decomposition))
            domain = source.domain
            primitive = sp.Add(
                *(
                    term.as_numer_denom()[0] * sp.log(sp.Abs(term.as_numer_denom()[1]))
                    for term in sp.Add.make_args(decomposition)
                )
            )
            steps = source.steps
        else:
            integrand = function.expression(X)
            primitive = sp.integrate(integrand, X)
            domain = sp.S.Reals
            steps = ()
        if is_primitive(primitive, integrand, domain) != "yes":
            raise ValueError("Invalid antiderivative")
        return Integral(
            integrand=integrand,
            primitive=primitive,
            domain=domain,
            steps=steps + (Step("integrate", rf"{sp.latex(primitive)} + C"),),
        )

    def build(self, params: IndefiniteParams) -> Task:
        result = self.integrate(params)
        return Task(
            statement=rf"Find \(\int {sp.latex(result.integrand)}\,dx\).",
            steps=result.steps,
            answer=AntiderivativeAnswer(result.integrand, result.primitive, result.domain),
            metadata={},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


def generators() -> tuple[TaskGenerator[Any], ...]:
    """Contribute this module's frozen versions to registry discovery."""
    return (IndefiniteIntegral(),)
