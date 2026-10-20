"""ADR-003 topic families, offered by the practice API through `core.catalogue` (#36)."""

from collections.abc import Callable
from dataclasses import dataclass
from random import Random
from typing import Any, Literal

import sympy as sp
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sympy.calculus.util import continuous_domain

from app.content.catalogue import TEXT, TextKey
from app.generators.basic import C, X
from app.schemas.problem import PublicProblem

type Version = Literal["substitution-v2", "parts-v1", "rational-v1", "trigonometric-v1"]


class FamilyParameters(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    generator_version: Version
    template: str = Field(max_length=32)
    coefficient: int = Field(ge=-3, le=3)

    @field_validator("coefficient")
    @classmethod
    def nonzero_coefficient(cls, value: int) -> int:
        if value == 0:
            raise ValueError("Coefficient must be nonzero")
        return value


@dataclass(frozen=True)
class FamilyTemplate:
    difficulty: int
    domain: Any
    primary_method: str
    auxiliary_transformations: tuple[str, ...] = ()
    is_definite: bool = False


@dataclass(frozen=True)
class FamilyStep:
    kind: TextKey
    expression: Any

    @property
    def say(self) -> str:
        return TEXT[self.kind]

    @property
    def latex(self) -> str:
        if self.kind == "constant":
            return str(sp.latex(self.expression - C)) + " + C"
        return str(sp.latex(self.expression))


@dataclass(frozen=True)
class FamilyProblem:
    parameters: FamilyParameters
    topic: str
    template: FamilyTemplate
    integrand: Any
    antiderivative: Any
    solution_steps: tuple[FamilyStep, ...]

    @property
    def difficulty(self) -> int:
        return self.template.difficulty

    @property
    def domain(self) -> Any:
        return self.template.domain

    @property
    def answer_latex(self) -> str:
        return str(sp.latex(self.antiderivative)) + " + C"

    def public(self) -> PublicProblem:
        return PublicProblem(
            topic=self.topic,
            problem_latex=rf"\int \left({sp.latex(self.integrand)}\right)\,dx"
            rf"\quad (x\in {sp.latex(self.domain)})",
        )


type Builder = Callable[[str, Any], tuple[Any, Any, tuple[FamilyStep, ...]]]


def _families() -> dict[Version, tuple[str, dict[str, FamilyTemplate], Builder]]:
    from app.generators import by_parts, rational, substitution, trigonometric

    return {
        "substitution-v2": ("substitution", substitution.TEMPLATES, substitution.build),
        "parts-v1": ("integration-by-parts", by_parts.TEMPLATES, by_parts.build),
        "rational-v1": ("rational-functions", rational.TEMPLATES, rational.build),
        "trigonometric-v1": (
            "trigonometric-integrals",
            trigonometric.TEMPLATES,
            trigonometric.build,
        ),
    }


def replay_family(record: dict[str, object]) -> FamilyProblem:
    """Validate the entire primitive record before constructing symbolic expressions."""
    parameters = FamilyParameters.model_validate(record)
    topic, templates, build = _families()[parameters.generator_version]
    if parameters.template not in templates:
        raise ValueError("Unknown template for generator version")
    integrand, primitive, steps = build(parameters.template, sp.Integer(parameters.coefficient))
    problem = FamilyProblem(
        parameters,
        topic,
        templates[parameters.template],
        integrand,
        primitive,
        (*steps, FamilyStep("integrate", primitive), FamilyStep("constant", primitive + C)),
    )
    verify_family(problem)
    return problem


def generate_family(*, topic: str, difficulty: int, seed: int) -> FamilyProblem:
    """Use a local PRNG; save the returned parameters, not the seed alone."""
    if type(difficulty) is not int or difficulty not in range(1, 6):
        raise ValueError("Difficulty must be an integer from 1 to 5")
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("Seed must be an unsigned 32-bit integer")
    choices = [
        (version, name)
        for version, (slug, templates, _) in _families().items()
        if slug == topic
        for name, template in templates.items()
        if template.difficulty == difficulty
    ]
    if not choices:
        raise ValueError("Unsupported topic or difficulty")
    rng = Random(seed)  # noqa: S311 -- deterministic exercise choice, not a security token
    version, name = rng.choice(choices)
    return replay_family(
        dict(
            generator_version=version, template=name, coefficient=rng.choice((-3, -2, -1, 1, 2, 3))
        )
    )


def verify_family(problem: FamilyProblem) -> None:
    """Prove every displayed stage differentiates to the integrand on every component.

    Unevaluated integrals retain the method in the solution. Differentiation checks
    them without asking a general-purpose integrator to discover the solution.
    """
    if not problem.solution_steps or problem.solution_steps[-1] != FamilyStep(
        "constant", problem.antiderivative + C
    ):
        raise RuntimeError("Final step must contain the answer and arbitrary constant")
    if continuous_domain(problem.integrand, X, sp.S.Reals) != problem.domain:
        raise RuntimeError("Integrand domain differs from the declared domain")
    if (
        problem.domain.is_subset(continuous_domain(problem.antiderivative, X, sp.S.Reals))
        is not True
    ):
        raise RuntimeError("Answer is not defined throughout the domain")
    for step in problem.solution_steps:
        # Check the explicit boundary terms as well as derivatives. A complex
        # logarithm may have the right derivative and still be an invalid step.
        boundary = step.expression.xreplace(
            dict.fromkeys(step.expression.atoms(sp.Integral), sp.S.Zero)
        ).doit()
        if problem.domain.is_subset(continuous_domain(boundary, X, sp.S.Reals)) is not True:
            raise RuntimeError("Solution step is not real throughout the domain")
    components = problem.domain.args if isinstance(problem.domain, sp.Union) else (problem.domain,)
    t = sp.Symbol("t", positive=True)
    for component in components:
        if component == sp.S.Reals:
            replacement, variable = X, X
        elif component.start == -sp.oo:
            replacement, variable = component.end - t, t
        elif component.end == sp.oo:
            replacement, variable = component.start + t, t
        else:
            replacement = component.start + (component.end - component.start) * t / (1 + t)
            variable = t
        integrand = problem.integrand.subs(X, replacement)
        for step in problem.solution_steps:
            # Differentiate after substitution so signs in log|x-a| resolve per interval.
            expression = step.expression.subs(X, replacement)
            difference = sp.diff(expression, variable) / sp.diff(replacement, variable) - integrand
            if sp.simplify(sp.trigsimp(difference)) != 0:
                raise RuntimeError("Solution step failed symbolic verification")
