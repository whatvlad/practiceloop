"""Versioned algebra exercises added after the initial curriculum migration."""

from typing import Any

import sympy as sp
from pydantic import Field

from app.engine.answers.expression import ExpressionAnswer
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task, TaskGenerator
from app.engine.prng import DeterministicRNG
from app.math_input import VariableDomain

X = sp.Symbol("x", real=True)


class RemainderParams(Drawn):
    a: int = Field(ge=1, le=5)
    b: int = Field(ge=-5, le=5)
    c: int = Field(ge=-5, le=5)
    root: int = Field(ge=-3, le=3)


class RemainderTheorem:
    version = "algebra-remainder-v1"
    prefix = "BZT"
    family = "algebra-remainder"
    code_version = 1
    params = RemainderParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    step_text = {"substitute": "Evaluate the polynomial at the zero of the divisor."}

    def draw(self, seed: int) -> RemainderParams:
        rng = DeterministicRNG(seed)
        return RemainderParams(
            seed=seed,
            a=1 + rng.randbelow(5),
            b=rng.randbelow(11) - 5,
            c=rng.randbelow(11) - 5,
            root=rng.randbelow(7) - 3,
        )

    def build(self, params: RemainderParams) -> Task:
        polynomial = params.a * X**2 + params.b * X + params.c
        remainder = polynomial.subs(X, params.root)
        if sp.rem(polynomial, X - params.root, X) != remainder:
            raise ValueError("Polynomial remainder failed verification")
        return Task(
            statement=(
                rf"Find the remainder when \(P(x)={sp.latex(polynomial)}\) "
                rf"is divided by \({sp.latex(X - params.root)}\)."
            ),
            steps=(Step("substitute", rf"P({params.root})={sp.latex(remainder)}"),),
            answer=ExpressionAnswer(remainder, {}),
            metadata={"difficulty": 1, "template": "remainder-theorem"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class PolynomialQuotient(RemainderTheorem):
    version = "algebra-polynomial-quotient-v1"
    prefix = "PQT"
    family = "algebra-polynomial-quotient"
    step_text = {"divide": "Divide the polynomial and check the remainder."}

    def input_variables(self, params: RemainderParams) -> dict[str, VariableDomain]:
        return {"x": "real"}

    def build(self, params: RemainderParams) -> Task:
        polynomial = params.a * X**2 + params.b * X + params.c
        divisor = X - params.root
        quotient = params.a * X + params.b + params.a * params.root
        remainder = polynomial.subs(X, params.root)
        if sp.expand(divisor * quotient + remainder - polynomial) != 0:
            raise ValueError("Polynomial division failed verification")
        return Task(
            statement=(
                rf"Find the quotient when \({sp.latex(polynomial)}\) "
                rf"is divided by \({sp.latex(divisor)}\)."
            ),
            steps=(
                Step(
                    "divide",
                    rf"{sp.latex(polynomial)}=({sp.latex(divisor)})"
                    rf"({sp.latex(quotient)})+({sp.latex(remainder)})",
                ),
            ),
            answer=ExpressionAnswer(quotient, {"x": "real"}),
            metadata={"difficulty": 2, "template": "polynomial-quotient"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


def generators() -> tuple[TaskGenerator[Any], ...]:
    return (RemainderTheorem(), PolynomialQuotient())
