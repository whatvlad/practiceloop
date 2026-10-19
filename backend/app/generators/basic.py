"""Versioned, bounded basic-integral templates; no learner expression parsing."""

from dataclasses import dataclass
from random import Random
from typing import Any, Literal

import sympy as sp
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.content.catalogue import TEXT
from app.schemas.problem import PublicProblem

X = sp.Symbol("x", real=True)
C = sp.Symbol("C", real=True)
_POSITIVE_X = sp.Symbol("t", positive=True)
GENERATOR_VERSION = "basic-v1"

type Domain = Literal["real", "nonzero", "positive"]
type StepKind = Literal[
    "linearity", "rewrite_power", "expand", "split_fraction", "integrate", "constant"
]

_DOMAIN_LATEX: dict[Domain, str] = {
    "real": r"x\in\mathbb{R}",
    "nonzero": r"x\ne0",
    "positive": "x>0",
}


@dataclass(frozen=True)
class BasicTemplate:
    name: str
    difficulty: int
    domain: Domain
    primary_method: str
    auxiliary_transformations: tuple[StepKind, ...] = ()
    is_definite: bool = False


BASIC_TEMPLATES = (
    BasicTemplate("constant", 1, "real", "direct"),
    BasicTemplate("power", 1, "real", "direct"),
    BasicTemplate("exponential", 1, "real", "direct"),
    BasicTemplate("sine", 1, "real", "direct"),
    BasicTemplate("cosine", 1, "real", "direct"),
    BasicTemplate("sum", 2, "real", "termwise", ("linearity",)),
    BasicTemplate("negative_power", 3, "nonzero", "power", ("rewrite_power",)),
    BasicTemplate("fractional_power", 3, "positive", "power", ("rewrite_power",)),
    BasicTemplate("reciprocal", 3, "nonzero", "logarithm"),
    BasicTemplate("expand_square", 4, "real", "termwise", ("expand",)),
    BasicTemplate("expand_and_split", 5, "nonzero", "termwise", ("expand", "split_fraction")),
)
_TEMPLATES = {template.name: template for template in BASIC_TEMPLATES}
_POWER_TEMPLATES = {"power", "sum", "negative_power"}
_SECONDARY_TEMPLATES = {"sum", "expand_square", "expand_and_split"}


class BasicParameters(BaseModel):
    """Private JSON-safe replay record. Never accept a serialized symbolic expression."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    generator_version: Literal["basic-v1"]
    template: str = Field(max_length=32)
    coefficient: int = Field(ge=-3, le=3)
    secondary: int = Field(default=1, ge=1, le=2)
    power: int = Field(default=2, ge=2, le=4)

    @field_validator("coefficient")
    @classmethod
    def nonzero_coefficient(cls, value: int) -> int:
        if value == 0:
            raise ValueError("Coefficient must be nonzero")
        return value


@dataclass(frozen=True)
class SolutionStep:
    kind: StepKind
    expression: Any

    @property
    def say(self) -> str:
        return TEXT[self.kind]

    @property
    def latex(self) -> str:
        if self.kind == "constant":
            return str(sp.latex(self.expression - C)) + " + C"
        if self.kind == "integrate":
            return str(sp.latex(self.expression))
        if self.kind == "linearity":
            terms = (sp.Integral(term, X) for term in sp.Add.make_args(self.expression))
            return str(sp.latex(sp.Add(*terms, evaluate=False)))
        if self.kind == "rewrite_power":
            coefficient, power = self.expression.as_coeff_exponent(X)
            return rf"\int {sp.latex(coefficient)}x^{{{sp.latex(power)}}}\,dx"
        return rf"\int \left({sp.latex(self.expression)}\right)\,dx"


@dataclass(frozen=True)
class InternalProblem:
    parameters: BasicParameters
    integrand: Any
    antiderivative: Any
    solution_steps: tuple[SolutionStep, ...]

    @property
    def template(self) -> BasicTemplate:
        return _TEMPLATES[self.parameters.template]

    @property
    def difficulty(self) -> int:
        return self.template.difficulty

    @property
    def domain(self) -> Any:
        if self.template.domain == "nonzero":
            return sp.S.Reals - sp.FiniteSet(0)
        if self.template.domain == "positive":
            return sp.Interval.open(0, sp.oo)
        return sp.S.Reals

    @property
    def answer_latex(self) -> str:
        return str(sp.latex(self.antiderivative)) + " + C"

    def public(self) -> PublicProblem:
        # Only the statement and its real-domain restriction cross this boundary.
        statement = rf"\int \left({sp.latex(self.integrand)}\right)\,dx"
        statement += rf"\quad ({_DOMAIN_LATEX[self.template.domain]})"
        return PublicProblem(topic="basic-integrals", problem_latex=statement)


def generate_basic(*, difficulty: int, seed: int) -> InternalProblem:
    """Choose a v1 template with a local PRNG; persist parameters, not the seed alone."""
    if type(difficulty) is not int or difficulty not in range(1, 6):
        raise ValueError("Difficulty must be an integer from 1 to 5")
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("Seed must be an unsigned 32-bit integer")
    rng = Random(seed)  # noqa: S311 -- reproducible exercise selection, not a security token
    template = rng.choice([item for item in BASIC_TEMPLATES if item.difficulty == difficulty])
    coefficients = (1, 2, 3) if difficulty == 5 else (-3, -2, -1, 1, 2, 3)
    return replay_basic(
        {
            "generator_version": GENERATOR_VERSION,
            "template": template.name,
            "coefficient": rng.choice(coefficients),
            "secondary": rng.choice((1, 2)) if template.name in _SECONDARY_TEMPLATES else 1,
            "power": rng.choice((2, 3, 4)) if template.name in _POWER_TEMPLATES else 2,
        }
    )


def replay_basic(record: dict[str, object]) -> InternalProblem:
    """Reconstruct only allowlisted v1 primitive parameters, then verify every step."""
    parameters = BasicParameters.model_validate(record)
    name = parameters.template
    if name not in _TEMPLATES:
        raise ValueError("Unknown basic-integral template")
    if name not in _POWER_TEMPLATES and parameters.power != 2:
        raise ValueError("Unused power must retain its canonical default")
    if name not in _SECONDARY_TEMPLATES and parameters.secondary != 1:
        raise ValueError("Unused secondary parameter must retain its canonical default")
    if name == "expand_and_split" and parameters.coefficient < 0:
        raise ValueError("Mixed template requires positive coefficients to prevent cancellation")

    a, b, n = sp.Integer(parameters.coefficient), sp.Integer(parameters.secondary), parameters.power
    if name == "constant":
        primitive = a * X
    elif name == "power":
        primitive = a * X**n / n
    elif name == "exponential":
        primitive = a * sp.exp(X)
    elif name == "sine":
        primitive = -a * sp.cos(X)
    elif name == "cosine":
        primitive = a * sp.sin(X)
    elif name == "sum":
        primitive = a * X**n / n + b * sp.exp(X)
    elif name == "negative_power":
        primitive = a * X ** (1 - n) / (1 - n)
    elif name == "fractional_power":
        primitive = 2 * a * sp.sqrt(X)
    elif name == "reciprocal":
        primitive = a * sp.log(sp.Abs(X))
    else:
        primitive = a * (X**3 / 3 + b * X**2 + b**2 * X)
        if name == "expand_and_split":
            primitive += b * X + b * sp.log(sp.Abs(X))

    integrand = sp.diff(primitive, X)
    steps: list[SolutionStep] = []
    if name == "sum":
        steps.append(SolutionStep("linearity", integrand))
    elif name in {"negative_power", "fractional_power"}:
        steps.append(SolutionStep("rewrite_power", integrand))
    elif name == "reciprocal":
        # d(log|x|)/dx = 1/x on both components; never silently use log(x).
        integrand = a / X
    elif name in {"expand_square", "expand_and_split"}:
        square = a * (X + b) ** 2
        expanded = sp.expand(square)
        integrand = square
        if name == "expand_and_split":
            fraction = b * (X + 1) / X
            integrand = sp.Add(square, fraction, evaluate=False)
            steps.append(SolutionStep("expand", sp.Add(expanded, fraction, evaluate=False)))
            steps.append(SolutionStep("split_fraction", expanded + b + b / X))
        else:
            steps.append(SolutionStep("expand", expanded))
    steps.extend((SolutionStep("integrate", primitive), SolutionStep("constant", primitive + C)))
    problem = InternalProblem(parameters, integrand, primitive, tuple(steps))
    _verify(problem)
    return problem


def _verify(problem: InternalProblem) -> None:
    """Symbolic invariants on the entire declared domain, not numerical sampling."""
    if not problem.solution_steps or problem.solution_steps[-1] != SolutionStep(
        "constant", problem.antiderivative + C
    ):
        raise RuntimeError("Final step must match the primitive with an arbitrary constant")
    domain = problem.template.domain
    # Positive t and -t separately cover both connected components of R\{0}.
    substitutions: tuple[Any, ...] = (X,) if domain == "real" else (_POSITIVE_X,)
    if domain == "nonzero":
        substitutions = (_POSITIVE_X, -_POSITIVE_X)
    for replacement in substitutions:
        variable = X if domain == "real" else _POSITIVE_X
        chain_factor = sp.diff(replacement, variable)
        integrand = problem.integrand.subs(X, replacement)
        for step in problem.solution_steps:
            expression = step.expression.subs(X, replacement)
            if expression.is_real is not True:
                raise RuntimeError("Generated step is not real throughout its domain")
            if step.kind in {"integrate", "constant"}:
                expression = sp.diff(expression, variable) / chain_factor
            if sp.simplify(expression - integrand) != 0:
                raise RuntimeError("Generated solution failed symbolic verification")
