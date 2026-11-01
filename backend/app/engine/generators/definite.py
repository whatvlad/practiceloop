"""Definite integrals over an indefinite integral drawn from the same seed."""

from fractions import Fraction

import sympy as sp

from app.engine.answers._symbolic import X
from app.engine.answers.number import NumberAnswer
from app.engine.codes import encode
from app.engine.generators.indefinite import IndefiniteIntegral, IndefiniteParams
from app.engine.models import Drawn, Step, Task


class DefiniteParams(Drawn):
    integral: IndefiniteParams


class DefiniteIntegral:
    version = "definite-v1"
    prefix = "DEF"
    family = "definite"
    code_version = 1
    params = DefiniteParams
    answer = NumberAnswer
    requires = ("indefinite-v1",)
    step_text = {
        **IndefiniteIntegral.step_text,
        "evaluate_bounds": "Subtract the antiderivative's values at the bounds.",
    }

    def draw(self, seed: int) -> DefiniteParams:
        return DefiniteParams(seed=seed, integral=IndefiniteIntegral().draw(seed))

    def build(self, params: DefiniteParams) -> Task:
        inner = IndefiniteIntegral().integrate(params.integral)
        primitive = inner.primitive
        if not sp.Interval(-1, 1).is_subset(inner.domain):
            raise ValueError("Integration bounds cross the domain")
        value = sp.simplify(primitive.subs(X, 1) - primitive.subs(X, -1))
        if value.is_Rational is not True:
            raise ValueError("Definite integral is not rational")
        answer = NumberAnswer(Fraction(int(value.p), int(value.q)))
        return Task(
            statement=rf"Calculate \(\int_{{-1}}^1 {sp.latex(inner.integrand)}\,dx\).",
            steps=inner.steps
            + (
                Step(
                    "evaluate_bounds",
                    rf"\left[{sp.latex(primitive)}\right]_{{-1}}^1 = {sp.latex(value)}",
                ),
            ),
            answer=answer,
            metadata={},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )
