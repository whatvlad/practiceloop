"""Native triple-integral curriculum data and worked setups (ADR-005)."""

from dataclasses import dataclass
from typing import Any, Literal

import sympy as sp

from app.engine.answers._symbolic import X
from app.engine.blocks.multiple.setup import (
    THETA,
    R,
    Setup,
    Y,
    bounds_latex,
    integration_steps,
    iterated_latex,
)
from app.engine.blocks.multiple.values import value_latex

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
        steps.append({"key": "describe_solid", "latex": bounds_latex(solution)})
        if solution.system == "cylindrical":
            steps.append({"key": "cylindrical_change", "latex": iterated_latex(solution)})
        else:
            steps.append({"key": "write_triple", "latex": iterated_latex(solution)})
    says = ("integrate_inner", "integrate_middle", "integrate_outer")
    steps.extend(integration_steps(solution, says))
    others = variant.checks if variant.stated is None else (variant.stated, *variant.checks)
    other = next((s for s in others if s.bounds != variant.solution.bounds), None)
    if other is not None:
        shown = Setup(other.system, a * variant.problem_integrand(), other.bounds)
        steps.append(
            {
                "key": "check_other",
                "latex": rf"{iterated_latex(shown)} = {value_latex(value)}",
            }
        )
    steps.append({"key": "multiple_value", "latex": value_latex(value)})
    return tuple(steps)
