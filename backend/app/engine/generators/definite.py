"""Definite integrals wrapping the indefinite generator."""

from fractions import Fraction

import sympy as sp

from app.engine.answers._symbolic import X
from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.engine.answers.number import NumberAnswer
from app.engine.generators.common import Seed, code
from app.engine.generators.indefinite import IndefiniteIntegral
from app.engine.models import Step, Task


class DefiniteIntegral:
    version = "definite-v1"
    params = Seed
    answer = NumberAnswer
    requires = ("indefinite-v1",)

    def draw(self, seed: int) -> Seed:
        return Seed(seed=seed)

    def build(self, params: Seed) -> Task:
        generator = IndefiniteIntegral()
        inner = generator.build(generator.draw(params.seed))
        if not isinstance(inner.answer, AntiderivativeAnswer):
            raise ValueError("Unexpected indefinite integral answer")
        primitive = inner.answer.primitive
        if not sp.Interval(-1, 1).is_subset(inner.answer.domain):
            raise ValueError("Integration bounds cross the domain")
        value = sp.simplify(primitive.subs(X, 1) - primitive.subs(X, -1))
        if value.is_Rational is not True:
            raise ValueError("Definite integral is not rational")
        answer = NumberAnswer(Fraction(int(value.p), int(value.q)))
        return Task(
            statement=rf"Calculate \(\int_{{-1}}^1 {sp.latex(inner.answer.integrand)}\,dx\).",
            steps=inner.steps
            + (
                Step(
                    "evaluate_bounds",
                    rf"\left[{sp.latex(primitive)}\right]_{{-1}}^1 = {sp.latex(value)}",
                ),
            ),
            answer=answer,
            metadata={},
            code=code(self, "DEF", "definite", params.seed),
            generator_version=self.version,
        )
