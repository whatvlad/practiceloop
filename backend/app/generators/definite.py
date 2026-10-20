"""#36: definite-v1, clean bounds on already verified indefinite templates.

A definite template names one basic-v1 or family template and a closed interval
inside its real domain. The base template supplies the integrand, the
antiderivative and the method steps; this module only adds the bounds, the
evaluation step and the exact value F(b) - F(a).
"""

from dataclasses import dataclass
from typing import Any, Literal

import sympy as sp
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sympy.calculus.util import continuous_domain

from app.content.catalogue import TEXT
from app.generators.basic import BASIC_TEMPLATES, InternalProblem, X, replay_basic
from app.generators.families import FamilyProblem, FamilyTemplate, _families, replay_family

VERSION = "definite-v1"
# Visible rational parts of a value stay small: 14/3 or 3/2, never 37/24.
_MAX_NUMERATOR, _MAX_DENOMINATOR = 30, 12
_MAX_VALUE_OPS = 8
_CLEAN_ATOMS = (sp.Rational, sp.log, sp.exp, sp.NumberSymbol)


@dataclass(frozen=True)
class DefiniteTemplate:
    topic: str
    base: tuple[tuple[str, object], ...]
    lower: Any
    upper: Any


def _base(version: str, template: str, **extra: object) -> tuple[tuple[str, object], ...]:
    return (("generator_version", version), ("template", template), *extra.items())


def _basic(template: str, power: int = 2) -> tuple[tuple[str, object], ...]:
    return _base("basic-v1", template, secondary=1, power=power)


_PI = sp.pi
TEMPLATES = {
    "power": DefiniteTemplate("basic-integrals", _basic("power"), 0, 2),
    "exponential": DefiniteTemplate("basic-integrals", _basic("exponential"), 0, 1),
    "sum": DefiniteTemplate("basic-integrals", _basic("sum"), 0, 1),
    "reciprocal": DefiniteTemplate("basic-integrals", _basic("reciprocal"), 1, sp.E),
    "fractional_power": DefiniteTemplate("basic-integrals", _basic("fractional_power"), 1, 4),
    "expand_square": DefiniteTemplate("basic-integrals", _basic("expand_square"), 0, 1),
    "polynomial_inner": DefiniteTemplate(
        "substitution", _base("substitution-v2", "polynomial_inner"), 0, 1
    ),
    "factor_square": DefiniteTemplate(
        "substitution", _base("substitution-v2", "factor_square"), 0, 1
    ),
    "linear_exponential": DefiniteTemplate(
        "integration-by-parts", _base("parts-v1", "linear_exponential"), 0, 1
    ),
    "quadratic_exponential": DefiniteTemplate(
        "integration-by-parts", _base("parts-v1", "quadratic_exponential"), 0, 1
    ),
    "cyclic_sine": DefiniteTemplate(
        "integration-by-parts", _base("parts-v1", "cyclic_sine"), 0, _PI
    ),
    "linear_denominator": DefiniteTemplate(
        "rational-functions", _base("rational-v1", "linear_denominator"), 1, 2
    ),
    "denominator_derivative": DefiniteTemplate(
        "rational-functions", _base("rational-v1", "denominator_derivative"), 0, 1
    ),
    "distinct_factors": DefiniteTemplate(
        "rational-functions", _base("rational-v1", "distinct_factors"), 1, 2
    ),
    "repeated_factor": DefiniteTemplate(
        "rational-functions", _base("rational-v1", "repeated_factor"), 1, 2
    ),
    "division_then_fractions": DefiniteTemplate(
        "rational-functions", _base("rational-v1", "division_then_fractions"), 1, 2
    ),
    "sine": DefiniteTemplate("trigonometric-integrals", _base("trigonometric-v1", "sine"), 0, _PI),
    "double_argument": DefiniteTemplate(
        "trigonometric-integrals", _base("trigonometric-v1", "double_argument"), 0, _PI / 2
    ),
    "odd_power": DefiniteTemplate(
        "trigonometric-integrals", _base("trigonometric-v1", "odd_power"), 0, _PI
    ),
    "even_power": DefiniteTemplate(
        "trigonometric-integrals", _base("trigonometric-v1", "even_power"), 0, _PI
    ),
    "identity_substitution": DefiniteTemplate(
        "trigonometric-integrals", _base("trigonometric-v1", "identity_substitution"), 0, _PI / 2
    ),
}


class DefiniteParameters(BaseModel):
    """Private replay record; the bounds belong to the template, never to the record."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    generator_version: Literal["definite-v1"]
    template: str = Field(max_length=32)
    coefficient: int = Field(ge=-3, le=3)

    @field_validator("coefficient")
    @classmethod
    def nonzero_coefficient(cls, value: int) -> int:
        if value == 0:
            raise ValueError("Coefficient must be nonzero")
        return value


@dataclass(frozen=True)
class DefiniteStep:
    say: str
    latex: str


@dataclass(frozen=True)
class DefiniteProblem:
    parameters: DefiniteParameters
    topic: str
    template: FamilyTemplate
    integrand: Any
    antiderivative: Any
    lower: Any
    upper: Any
    value: Any
    solution_steps: tuple[DefiniteStep, ...]
    base_domain: Any

    @property
    def difficulty(self) -> int:
        return self.template.difficulty

    @property
    def answer_latex(self) -> str:
        return value_latex(self.value)

    @property
    def statement(self) -> str:
        return (
            rf"\int_{{{sp.latex(self.lower)}}}^{{{sp.latex(self.upper)}}}"
            rf" \left({sp.latex(self.integrand)}\right)\,dx"
        )


def difficulty(template: DefiniteTemplate) -> int:
    """The base template's level: bounds add evaluation, not a structural level."""
    base = dict(template.base)
    if base["generator_version"] == "basic-v1":
        return next(item.difficulty for item in BASIC_TEMPLATES if item.name == base["template"])
    templates = next(
        t for version, (_, t, _) in _families().items() if version == base["generator_version"]
    )
    return templates[str(base["template"])].difficulty


def value_latex(value: Any) -> str:
    """Leading symbolic term first: `e - 1`, not `-1 + e`."""
    return str(sp.latex(value, order="rev-lex"))


def base_record(template: DefiniteTemplate, coefficient: int) -> dict[str, object]:
    return {**dict(template.base), "coefficient": coefficient}


def replay_definite(record: dict[str, object], *, verify: bool = True) -> DefiniteProblem:
    """Validate the whole record, rebuild the base template, then add the bounds.

    `verify=False` is only for the answer worker, as for `replay_family`.
    """
    parameters = DefiniteParameters.model_validate(record)
    if parameters.template not in TEMPLATES:
        raise ValueError("Unknown definite template")
    template = TEMPLATES[parameters.template]
    source = base_record(template, parameters.coefficient)
    base: InternalProblem | FamilyProblem = (
        replay_basic(source)
        if source["generator_version"] == "basic-v1"
        else replay_family(source, verify=verify)
    )
    base_template, steps = base.template, base.solution_steps
    integrand, primitive = base.integrand, base.antiderivative
    lower, upper = sp.sympify(template.lower), sp.sympify(template.upper)
    at_upper, at_lower = primitive.subs(X, upper), primitive.subs(X, lower)
    # Simplify per unit coefficient, so 3 ln(4/3) is not merged into ln(64/27).
    coefficient = sp.Integer(parameters.coefficient)
    value = coefficient * sp.simplify((at_upper - at_lower) / coefficient)
    evaluation = (
        rf"\left[{sp.latex(primitive)}\right]_{{{sp.latex(lower)}}}^{{{sp.latex(upper)}}}"
        rf" = {sp.latex(sp.simplify(at_upper))} - \left({sp.latex(sp.simplify(at_lower))}\right)"
    )
    problem = DefiniteProblem(
        parameters,
        template.topic,
        FamilyTemplate(
            base_template.difficulty,
            sp.Interval(lower, upper),
            base_template.primary_method,
            tuple(base_template.auxiliary_transformations),
            is_definite=True,
        ),
        integrand,
        primitive,
        lower,
        upper,
        value,
        (
            # The base method steps without their final arbitrary-constant step.
            *(DefiniteStep(step.say, step.latex) for step in steps[:-1]),
            DefiniteStep(TEXT["evaluate_bounds"], evaluation),
            DefiniteStep(TEXT["definite_value"], value_latex(value)),
        ),
        base.domain,
    )
    if verify:
        verify_definite(problem)
    return problem


def is_clean_value(value: Any) -> bool:
    """Small exact rationals, π, e, and logarithms or powers of them; never zero."""
    if not value.is_number or value.is_real is not True or value.is_zero is not False:
        return False
    if value.atoms(sp.Float) or sp.count_ops(value) > _MAX_VALUE_OPS:
        return False
    for node in sp.preorder_traversal(value):
        if isinstance(node, sp.Rational) and (
            abs(node.p) > _MAX_NUMERATOR or node.q > _MAX_DENOMINATOR
        ):
            return False
        if node.is_Atom and not isinstance(node, _CLEAN_ATOMS):
            return False
        if node.is_Function and not isinstance(node, (sp.log, sp.exp)):
            return False
    return True


def verify_definite(problem: DefiniteProblem) -> None:
    """Reject bounds that touch an excluded point, and values that are not clean.

    The base replay has already proven the antiderivative on its whole domain.
    """
    interval = sp.Interval(problem.lower, problem.upper)
    if (
        problem.lower.is_number is not True
        or (problem.upper - problem.lower).is_positive is not True
    ):
        raise RuntimeError("Bounds must be numbers with lower < upper")
    if interval.is_subset(problem.base_domain) is not True:
        raise RuntimeError("Bounds cross a point outside the integrand's domain")
    if interval.is_subset(continuous_domain(problem.integrand, X, sp.S.Reals)) is not True:
        raise RuntimeError("Integrand is not continuous on the closed interval")
    if interval.is_subset(continuous_domain(problem.antiderivative, X, sp.S.Reals)) is not True:
        raise RuntimeError("Antiderivative is not continuous on the closed interval")
    exact = problem.antiderivative.subs(X, problem.upper) - problem.antiderivative.subs(
        X, problem.lower
    )
    if sp.simplify(exact - problem.value) != 0:
        raise RuntimeError("Value differs from F(b) - F(a)")
    if not is_clean_value(problem.value):
        raise RuntimeError("Definite value is not pedagogically clean")
