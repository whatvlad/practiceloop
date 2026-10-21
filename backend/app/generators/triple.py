"""#100: triple-v1, triple integrals in Cartesian and cylindrical coordinates (ADR-005).

Each template has a few fixed variants: a solid, its integrand and the set-up the
worked solution uses, with the value and the declared mistake values written down
at coefficient 1. A record picks a variant and scales the integrand by a nonzero
coefficient. Levels 1-3 name the coordinate system (or state the iterated
integral); levels 4-5 leave the choice to the learner, and the solution shows the
set-up that is clean. The shared machinery is in `multiple.py`, as for double-v1.
"""

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Literal

import sympy as sp

from app.content.catalogue import TEXT
from app.generators.basic import X
from app.generators.definite import is_clean_value, value_latex
from app.generators.multiple import (
    THETA,
    MultipleParameters,
    R,
    Setup,
    ValueProblem,
    Y,
    bounds_latex,
    integrate_setup,
    integration_steps,
    iterated_latex,
    verify_missing_jacobian,
    verify_value,
)

VERSION = "triple-v1"
TOPIC = "triple-integrals"
COEFFICIENTS = (-3, -2, -1, 1, 2, 3)
Z = sp.Symbol("z", real=True)
_PI, _E = sp.pi, sp.E
_TURN = (THETA, 0, 2 * _PI)


def _cartesian(integrand: Any, *bounds: tuple[Any, Any, Any]) -> Setup:
    return Setup("cartesian", sp.sympify(integrand), bounds)


def _cylindrical(integrand: Any, *bounds: tuple[Any, Any, Any]) -> Setup:
    return Setup("cylindrical", sp.sympify(integrand), bounds)


def _over_disk(radius: Any, low: Any, high: Any) -> Setup:
    """The Cartesian set-up of a solid over the disk x^2 + y^2 <= radius^2."""
    edge = sp.sqrt(radius**2 - X**2)
    return _cartesian(0, (Z, low, high), (Y, -edge, edge), (X, -radius, radius))


@dataclass(frozen=True)
class TripleVariant:
    solution: Setup
    value: Any
    # Iterated form: the integral the statement shows. None means solid form.
    stated: Setup | None = None
    # Solid form: the integrand in x, y, z and the solid E as LaTeX.
    integrand: Any = None
    solid: str = ""
    # Other set-ups of the same solid; the first one is shown as a check.
    checks: tuple[Setup, ...] = ()
    # Value without the factor r; None when it is not clean or the set-up is Cartesian.
    missing_r: Any = None
    # z bounds a learner might use instead, and the value they give at coefficient 1.
    wrong_z: tuple[tuple[Any, Any], Any] | None = None
    exact_checks: bool = False

    def problem_integrand(self) -> Any:
        """The integrand in x, y and z, as the learner sees it."""
        return self.integrand if self.stated is None else self.stated.integrand


@dataclass(frozen=True)
class TripleTemplate:
    difficulty: int
    # The system the statement names, or None when the learner chooses (levels 4-5)
    # or the statement is an iterated Cartesian integral.
    named: Literal["cartesian", "cylindrical"] | None
    variants: tuple[TripleVariant, ...]


def _box(integrand: Any, x: Any, y: Any, z: Any, value: Any) -> TripleVariant:
    """A box [0,x]×[0,y]×[0,z]; the check integrates in the opposite order."""
    return TripleVariant(
        _cartesian(integrand, (Z, 0, z), (Y, 0, y), (X, 0, x)),
        value,
        integrand=integrand,
        solid=rf"[0,{x}]\times[0,{y}]\times[0,{z}]",
        checks=(_cartesian(0, (X, 0, x), (Y, 0, y), (Z, 0, z)),),
        exact_checks=True,
    )


def _wrong_z(variant: TripleVariant) -> Setup:
    if variant.wrong_z is None:
        raise ValueError("The variant declares no wrong z bounds")
    (low, high), _ = variant.wrong_z
    _, *outer = variant.solution.bounds
    return Setup(variant.solution.system, variant.solution.integrand, ((Z, low, high), *outer))


_HALF_EDGE = sp.sqrt(1 - X**2)

TEMPLATES: dict[str, TripleTemplate] = {
    # Level 1: a box and a product of one-variable factors.
    "box_product": TripleTemplate(
        1,
        "cartesian",
        (
            _box(X * Y * Z, 1, 2, 1, sp.Rational(1, 2)),
            _box(X * Y**2 * Z, 2, 1, 3, sp.Integer(3)),
            _box(X * Y * Z**2, 2, 1, 3, sp.Integer(9)),
        ),
    ),
    # Level 2: a box whose inner results depend on the outer variables.
    "box_sum": TripleTemplate(
        2,
        "cartesian",
        (
            _box(X + Y * Z, 1, 1, 2, sp.Integer(2)),
            _box(X + Y + Z, 2, 1, 1, sp.Integer(4)),
        ),
    ),
    # Level 3: one stated method, a simplex in Cartesian coordinates ...
    "simplex": TripleTemplate(
        3,
        None,
        (
            TripleVariant(
                _cartesian(X, (Z, 0, 2 - X - Y), (Y, 0, 2 - X), (X, 0, 2)),
                sp.Rational(2, 3),
                stated=_cartesian(X, (Z, 0, 2 - X - Y), (Y, 0, 2 - X), (X, 0, 2)),
                checks=(_cartesian(0, (X, 0, 2 - Y - Z), (Y, 0, 2 - Z), (Z, 0, 2)),),
                wrong_z=((0, 2), sp.Rational(8, 3)),
                exact_checks=True,
            ),
            TripleVariant(
                _cartesian(1, (Z, 0, 1 - X - Y), (Y, 0, 1 - X), (X, 0, 1)),
                sp.Rational(1, 6),
                stated=_cartesian(1, (Z, 0, 1 - X - Y), (Y, 0, 1 - X), (X, 0, 1)),
                checks=(_cartesian(0, (X, 0, 1 - Y - Z), (Y, 0, 1 - Z), (Z, 0, 1)),),
                wrong_z=((0, 1), sp.Rational(1, 2)),
                exact_checks=True,
            ),
        ),
    ),
    # ... or a cylinder in cylindrical coordinates.
    "cylinder": TripleTemplate(
        3,
        "cylindrical",
        (
            TripleVariant(
                _cylindrical(R**2, (Z, 0, 3), (R, 0, 1), _TURN),
                3 * _PI / 2,
                integrand=X**2 + Y**2,
                solid=r"\left\{x^{2}+y^{2} \le 1,\ 0 \le z \le 3\right\}",
                checks=(_over_disk(1, 0, 3),),
                missing_r=2 * _PI,
            ),
            TripleVariant(
                _cylindrical(Z, (Z, 0, 2), (R, 0, 1), _TURN),
                2 * _PI,
                integrand=Z,
                solid=r"\left\{x^{2}+y^{2} \le 1,\ 0 \le z \le 2\right\}",
                checks=(_over_disk(1, 0, 2),),
                missing_r=4 * _PI,
            ),
        ),
    ),
    # Level 4: bounds from a described solid; the learner chooses the system.
    "solid_of_revolution": TripleTemplate(
        4,
        None,
        (
            TripleVariant(
                _cylindrical(1, (Z, R, 2), (R, 0, 2), _TURN),
                8 * _PI / 3,
                integrand=sp.Integer(1),
                solid=r"\left\{\sqrt{x^{2}+y^{2}} \le z \le 2\right\}",
                checks=(_over_disk(2, sp.sqrt(X**2 + Y**2), 2),),
                missing_r=4 * _PI,
                wrong_z=((0, 2), 8 * _PI),
            ),
            TripleVariant(
                _cylindrical(1, (Z, 0, 4 - R**2), (R, 0, 2), _TURN),
                8 * _PI,
                integrand=sp.Integer(1),
                solid=r"\left\{0 \le z \le 4 - x^{2} - y^{2}\right\}",
                checks=(_over_disk(2, 0, 4 - X**2 - Y**2),),
                missing_r=32 * _PI / 3,
                wrong_z=((0, 4), 16 * _PI),
            ),
        ),
    ),
    "tetrahedron": TripleTemplate(
        4,
        None,
        (
            TripleVariant(
                _cartesian(1, (Z, 0, 2 - 2 * X - Y), (Y, 0, 2 - 2 * X), (X, 0, 1)),
                sp.Rational(2, 3),
                integrand=sp.Integer(1),
                solid=r"\left\{x \ge 0,\ y \ge 0,\ z \ge 0,\ 2x + y + z \le 2\right\}",
                checks=(_cartesian(0, (X, 0, (2 - Y - Z) / 2), (Y, 0, 2 - Z), (Z, 0, 2)),),
                wrong_z=((0, 2), sp.Integer(2)),
                exact_checks=True,
            ),
            TripleVariant(
                _cartesian(1, (Z, 0, 6 - 3 * X - 2 * Y), (Y, 0, 3 - 3 * X / 2), (X, 0, 2)),
                sp.Integer(6),
                integrand=sp.Integer(1),
                solid=r"\left\{x \ge 0,\ y \ge 0,\ z \ge 0,\ 3x + 2y + z \le 6\right\}",
                checks=(_cartesian(0, (X, 0, (6 - 2 * Y - Z) / 3), (Y, 0, 3 - Z / 2), (Z, 0, 6)),),
                wrong_z=((0, 6), sp.Integer(18)),
                exact_checks=True,
            ),
        ),
    ),
    # Level 5: a Cartesian integral that is only clean in cylindrical coordinates,
    # plus the inner substitution u = r^2.
    "cylindrical_conversion": TripleTemplate(
        5,
        None,
        (
            TripleVariant(
                _cylindrical(Z * sp.exp(R**2), (Z, 0, 2), (R, 0, 1), (THETA, 0, _PI / 2)),
                _PI * (_E - 1) / 2,
                stated=_cartesian(
                    Z * sp.exp(X**2 + Y**2), (Z, 0, 2), (Y, 0, _HALF_EDGE), (X, 0, 1)
                ),
            ),
            TripleVariant(
                _cylindrical(2 * Z / (1 + R**2), (Z, 0, 1), (R, 0, 1), (THETA, 0, _PI)),
                _PI * sp.log(2) / 2,
                stated=_cartesian(
                    2 * Z / (1 + X**2 + Y**2), (Z, 0, 1), (Y, 0, _HALF_EDGE), (X, -1, 1)
                ),
                missing_r=_PI**2 / 4,
            ),
        ),
    ),
}


def records(difficulty: int) -> list[dict[str, object]]:
    return [
        {"generator_version": VERSION, "template": name, "variant": index, "coefficient": a}
        for name, template in TEMPLATES.items()
        if template.difficulty == difficulty
        for index in range(len(template.variants))
        for a in COEFFICIENTS
    ]


def _lookup(record: dict[str, object]) -> tuple[MultipleParameters, TripleTemplate, TripleVariant]:
    """Validate the whole record before any symbolic construction."""
    parameters = MultipleParameters.model_validate(record)
    if parameters.generator_version != VERSION or parameters.template not in TEMPLATES:
        raise ValueError("Unknown triple-integral template")
    template = TEMPLATES[parameters.template]
    if parameters.variant >= len(template.variants):
        raise ValueError("Unknown triple-integral variant")
    return parameters, template, template.variants[parameters.variant]


def replay_value(record: dict[str, object]) -> ValueProblem:
    """The answer worker's view: declared values only, no integration."""
    parameters, template, variant = _lookup(record)
    a = sp.Integer(parameters.coefficient)
    mistakes: tuple[tuple[str, Any], ...] = ()
    if variant.missing_r is not None:
        mistakes += (("missing_jacobian", a * variant.missing_r),)
    if variant.wrong_z is not None:
        mistakes += (("z_bounds", a * variant.wrong_z[1]),)
    return ValueProblem(parameters, TOPIC, template.difficulty, a * variant.value, mistakes)


@dataclass(frozen=True)
class TripleProblem:
    problem: ValueProblem
    statement: str
    solution_steps: tuple[dict[str, str], ...]

    @property
    def answer_latex(self) -> str:
        return value_latex(self.problem.value)


def _statement(template: TripleTemplate, variant: TripleVariant, a: Any) -> str:
    if variant.stated is not None:
        return iterated_latex(variant.stated.scaled(a))
    scaled = a * variant.integrand
    integrand = sp.latex(scaled) if scaled.is_number else rf"\left({sp.latex(scaled)}\right)"
    statement = rf"\iiint_E {integrand}\,dV,\quad E = {variant.solid}"
    if template.named == "cylindrical":
        statement += r"\quad\text{(cylindrical coordinates)}"
    elif template.named == "cartesian":
        statement += r"\quad\text{(Cartesian coordinates)}"
    return statement


def _steps(variant: TripleVariant, a: Any, value: Any) -> tuple[dict[str, str], ...]:
    solution = variant.solution.scaled(a)
    steps: list[dict[str, str]] = []
    if variant.stated is None or variant.stated.bounds != variant.solution.bounds:
        steps.append({"say": TEXT["describe_solid"], "latex": bounds_latex(solution)})
        if solution.system == "cylindrical":
            steps.append({"say": TEXT["cylindrical_change"], "latex": iterated_latex(solution)})
        else:
            steps.append({"say": TEXT["write_triple"], "latex": iterated_latex(solution)})
    says = (TEXT["integrate_inner"], TEXT["integrate_middle"], TEXT["integrate_outer"])
    steps.extend(integration_steps(solution, says))
    others = variant.checks if variant.stated is None else (variant.stated, *variant.checks)
    other = next((s for s in others if s.bounds != variant.solution.bounds), None)
    if other is not None:
        shown = Setup(other.system, a * variant.problem_integrand(), other.bounds)
        steps.append(
            {
                "say": TEXT["check_other"],
                "latex": rf"{iterated_latex(shown)} = {value_latex(value)}",
            }
        )
    steps.append({"say": TEXT["multiple_value"], "latex": value_latex(value)})
    return tuple(steps)


def replay_triple(record: dict[str, object], *, verify: bool = True) -> TripleProblem:
    problem = replay_value(record)
    parameters, template, variant = _lookup(record)
    if verify:
        verify_variant(parameters.template, parameters.variant)
        if not is_clean_value(problem.value):
            raise RuntimeError("Triple-integral value is not pedagogically clean")
    a = sp.Integer(parameters.coefficient)
    return TripleProblem(
        problem, _statement(template, variant, a), _steps(variant, a, problem.value)
    )


def _to_cylindrical(expression: Any) -> Any:
    return expression.subs({X: R * sp.cos(THETA), Y: R * sp.sin(THETA)}, simultaneous=True)


@lru_cache(maxsize=64)
def verify_variant(name: str, index: int) -> None:
    """Recompute a variant's declared values once per process (coefficients scale them)."""
    template = TEMPLATES[name]
    variant = template.variants[index]
    integrand = variant.problem_integrand()
    if (variant.integrand is None) == (variant.stated is None):
        raise RuntimeError("A variant has exactly one statement form")
    if template.named is not None and variant.solution.system != template.named:
        raise RuntimeError("The solution must use the coordinate system the statement names")
    if variant.solution.bounds[0][0] != Z:
        raise RuntimeError("The innermost integration is in z")
    cylindrical = variant.solution.system == "cylindrical"
    expected = _to_cylindrical(integrand) if cylindrical else integrand
    if sp.simplify(expected - variant.solution.integrand) != 0:
        raise RuntimeError("Solution integrand differs from the problem integrand")
    checks = tuple(Setup(c.system, integrand, c.bounds) for c in variant.checks)
    if variant.stated is not None and variant.stated.bounds != variant.solution.bounds:
        checks = (variant.stated, *checks)
    if cylindrical and not checks:
        raise RuntimeError("A cylindrical solid is cross-checked in Cartesian coordinates")
    verify_value(
        variant.value,
        variant.solution,
        checks,
        lambda setup: variant.exact_checks and setup is not variant.stated,
    )
    verify_missing_jacobian(variant.missing_r, variant.solution)
    if variant.wrong_z is not None:
        wrong = variant.wrong_z[1]
        if sp.simplify(integrate_setup(_wrong_z(variant)) - wrong) != 0:
            raise RuntimeError("Declared wrong-z value is wrong")
        if sp.simplify(wrong - variant.value) == 0 or sp.simplify(wrong + variant.value) == 0:
            raise RuntimeError("A wrong-z value must differ from the value and its negative")
    for a in COEFFICIENTS:
        if not is_clean_value(a * variant.value):
            raise RuntimeError("Scaled value is not pedagogically clean")
