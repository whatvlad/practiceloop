"""Versioned algebra exercises added after the initial curriculum migration."""

from typing import Any, Self

import sympy as sp
from pydantic import Field, model_validator

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


class QuadraticRemainderParams(Drawn):
    first: int = Field(ge=-2, le=2)
    second: int = Field(ge=-2, le=2)
    exponent: int = Field(ge=2, le=100)

    @model_validator(mode="after")
    def distinct_roots(self) -> Self:
        if self.first == self.second:
            raise ValueError("Divisor roots must be distinct")
        return self


class QuadraticRemainder:
    version = "algebra-quadratic-remainder-v1"
    prefix = "QRM"
    family = "algebra-quadratic-remainder"
    code_version = 1
    params = QuadraticRemainderParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    step_text = {
        "substitute": "Evaluate the polynomial at each root of the divisor.",
        "interpolate": "Find the linear remainder through these two values.",
    }

    def draw(self, seed: int) -> QuadraticRemainderParams:
        rng = DeterministicRNG(seed)
        first = rng.randbelow(5) - 2
        second = rng.randbelow(4) - 2
        if second >= first:
            second += 1
        return QuadraticRemainderParams(
            seed=seed, first=first, second=second, exponent=3 + rng.randbelow(8)
        )

    def input_variables(self, params: QuadraticRemainderParams) -> dict[str, VariableDomain]:
        return {"x": "real"}

    def build(self, params: QuadraticRemainderParams) -> Task:
        a, b, n = params.first, params.second, params.exponent
        y1, y2 = sp.Integer(a) ** n, sp.Integer(b) ** n
        remainder = sp.expand(y1 + (y2 - y1) * (X - a) / (b - a))
        if remainder.subs(X, a) != y1 or remainder.subs(X, b) != y2:
            raise ValueError("Quadratic remainder failed verification")
        divisor = rf"({sp.latex(X - a)})({sp.latex(X - b)})"
        return Task(
            statement=rf"Find the remainder when \(x^{{{n}}}\) is divided by \({divisor}\).",
            steps=(
                Step("substitute", rf"R({a})={y1},\quad R({b})={y2}"),
                Step("interpolate", rf"R(x)={sp.latex(remainder)}"),
            ),
            answer=ExpressionAnswer(remainder, {"x": "real"}),
            metadata={"difficulty": 2, "template": "quadratic-remainder"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


def generators() -> tuple[TaskGenerator[Any], ...]:
    return (RemainderTheorem(), PolynomialQuotient(), QuadraticRemainder())
