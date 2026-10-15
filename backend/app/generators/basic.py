from dataclasses import dataclass
from typing import Any

from sympy import Integer, Rational, Symbol, latex

from app.schemas.problem import PublicProblem

X = Symbol("x", real=True)


@dataclass(frozen=True)
class InternalProblem:
    integrand: Any
    antiderivative: Any
    answer_latex: str
    solution_steps: tuple[str, ...]

    def public(self) -> PublicProblem:
        return PublicProblem(topic="basic-integrals", problem_latex=latex(self.integrand))


def generate_basic(coefficient: int, power: int) -> InternalProblem:
    """A bounded trusted-parameter fixture, not the five-level MVP generator.

    No string evaluation or user answer parsing. Degree >= 0 avoids logarithmic
    domain issues. The owner-approved integration-constant policy is still open.
    """
    if type(coefficient) is not int or type(power) is not int:
        raise ValueError("Parameters must be integers")
    if not -20 <= coefficient <= 20 or coefficient == 0 or not 0 <= power <= 8:
        raise ValueError("Parameters out of bounds")
    integrand = Integer(coefficient) * X**power
    primitive = Rational(coefficient, power + 1) * X ** (power + 1)
    return InternalProblem(
        integrand=integrand,
        antiderivative=primitive,
        answer_latex=latex(primitive) + " + C",
        solution_steps=(
            r"\int a x^n\,dx = \frac{a}{n+1}x^{n+1}+C\quad(n\ne-1)",
            latex(primitive) + " + C",
        ),
    )
