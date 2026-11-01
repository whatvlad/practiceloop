"""Native double-integral curriculum data and worked setups (ADR-005)."""

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
_PI, _E = sp.pi, sp.E


def _cartesian(integrand: Any, *bounds: tuple[Any, Any, Any]) -> Setup:
    return Setup("cartesian", integrand, bounds)


def _polar(integrand: Any, r: tuple[Any, Any], theta: tuple[Any, Any]) -> Setup:
    return Setup("polar", integrand, ((R, *r), (THETA, *theta)))


def _disk(radius: Any) -> Setup:
    """The Cartesian set-up of a whole disk, for numerical cross-checks."""
    edge = sp.sqrt(radius**2 - X**2)
    return _cartesian(sp.Integer(0), (Y, -edge, edge), (X, -radius, radius))


@dataclass(frozen=True)
class DoubleVariant:
    solution: Setup
    value: Any
    # Iterated form: the integral the statement shows. None means region form.
    stated: Setup | None = None
    # Region form: the integrand in x, y and the region D as LaTeX.
    integrand: Any = None
    region: str = ""
    # Other set-ups of the same region; the first one is shown as a check.
    checks: tuple[Setup, ...] = ()
    # Value without the factor r; None when it is not clean or the set-up is Cartesian.
    missing_r: Any = None
    exact_checks: bool = False

    def problem_integrand(self) -> Any:
        """The integrand in x and y, as the learner sees it."""
        return self.integrand if self.stated is None else self.stated.integrand


@dataclass(frozen=True)
class DoubleTemplate:
    difficulty: int
    # The system the statement names, or None when the learner chooses (levels 4-5).
    named: Literal["cartesian", "polar"] | None
    variants: tuple[DoubleVariant, ...]


def _same_region(variant: DoubleVariant, integrand: Any) -> tuple[Setup, ...]:
    """Cross-check set-ups carry the problem integrand, not a placeholder."""
    return tuple(Setup(c.system, integrand, c.bounds) for c in variant.checks)


_QUARTER_EDGE = sp.sqrt(4 - X**2)
_HALF_EDGE = sp.sqrt(1 - X**2)

TEMPLATES: dict[str, DoubleTemplate] = {
    # Level 1: rectangle, separable product integrand.
    "rectangle_product": DoubleTemplate(
        1,
        "cartesian",
        (
            DoubleVariant(
                _cartesian(3 * X * Y, (Y, 0, 1), (X, 0, 2)),
                sp.Integer(3),
                integrand=3 * X * Y,
                region=r"[0,2]\times[0,1]",
                checks=(_cartesian(0, (X, 0, 2), (Y, 0, 1)),),
                exact_checks=True,
            ),
            DoubleVariant(
                _cartesian(X**2 * Y, (Y, 0, 1), (X, 0, 3)),
                sp.Rational(9, 2),
                integrand=X**2 * Y,
                region=r"[0,3]\times[0,1]",
                checks=(_cartesian(0, (X, 0, 3), (Y, 0, 1)),),
                exact_checks=True,
            ),
            DoubleVariant(
                _cartesian(6 * X * Y**2, (Y, 0, 1), (X, 0, 1)),
                sp.Integer(1),
                integrand=6 * X * Y**2,
                region=r"[0,1]\times[0,1]",
                checks=(_cartesian(0, (X, 0, 1), (Y, 0, 1)),),
                exact_checks=True,
            ),
            DoubleVariant(
                _cartesian(X * sp.exp(Y), (Y, 0, 1), (X, 0, 2)),
                2 * (_E - 1),
                integrand=X * sp.exp(Y),
                region=r"[0,2]\times[0,1]",
                checks=(_cartesian(0, (X, 0, 2), (Y, 0, 1)),),
                exact_checks=True,
            ),
        ),
    ),
    # Level 2: rectangle, the inner result depends on the outer variable.
    "rectangle_sum": DoubleTemplate(
        2,
        "cartesian",
        (
            DoubleVariant(
                _cartesian(X + Y, (Y, 0, 2), (X, 0, 1)),
                sp.Integer(3),
                stated=_cartesian(X + Y, (Y, 0, 2), (X, 0, 1)),
                checks=(_cartesian(0, (X, 0, 1), (Y, 0, 2)),),
                exact_checks=True,
            ),
            DoubleVariant(
                _cartesian(X**2 + 2 * X * Y, (Y, 0, 1), (X, 0, 2)),
                sp.Rational(14, 3),
                stated=_cartesian(X**2 + 2 * X * Y, (Y, 0, 1), (X, 0, 2)),
                checks=(_cartesian(0, (X, 0, 2), (Y, 0, 1)),),
                exact_checks=True,
            ),
            DoubleVariant(
                _cartesian(X * sp.exp(X * Y), (Y, 0, 1), (X, 0, 1)),
                _E - 2,
                stated=_cartesian(X * sp.exp(X * Y), (Y, 0, 1), (X, 0, 1)),
                checks=(_cartesian(0, (X, 0, 1), (Y, 0, 1)),),
            ),
            DoubleVariant(
                _cartesian(2 * X * Y + 1, (Y, 0, 1), (X, 1, 2)),
                sp.Rational(5, 2),
                stated=_cartesian(2 * X * Y + 1, (Y, 0, 1), (X, 1, 2)),
                checks=(_cartesian(0, (X, 1, 2), (Y, 0, 1)),),
                exact_checks=True,
            ),
        ),
    ),
    # Level 3: one stated method. Type I and type II regions with a variable bound.
    "type_one": DoubleTemplate(
        3,
        "cartesian",
        (
            DoubleVariant(
                _cartesian(Y, (Y, 0, X), (X, 0, 1)),
                sp.Rational(1, 6),
                stated=_cartesian(Y, (Y, 0, X), (X, 0, 1)),
                checks=(_cartesian(0, (X, Y, 1), (Y, 0, 1)),),
                exact_checks=True,
            ),
            DoubleVariant(
                _cartesian(6 * X, (Y, X**2, X), (X, 0, 1)),
                sp.Rational(1, 2),
                stated=_cartesian(6 * X, (Y, X**2, X), (X, 0, 1)),
                checks=(_cartesian(0, (X, Y, sp.sqrt(Y)), (Y, 0, 1)),),
                exact_checks=True,
            ),
            DoubleVariant(
                _cartesian(X * Y, (Y, 0, X), (X, 0, 2)),
                sp.Integer(2),
                stated=_cartesian(X * Y, (Y, 0, X), (X, 0, 2)),
                checks=(_cartesian(0, (X, Y, 2), (Y, 0, 2)),),
                exact_checks=True,
            ),
        ),
    ),
    "type_two": DoubleTemplate(
        3,
        "cartesian",
        (
            DoubleVariant(
                _cartesian(2 * X, (X, 0, Y), (Y, 0, 1)),
                sp.Rational(1, 3),
                stated=_cartesian(2 * X, (X, 0, Y), (Y, 0, 1)),
                checks=(_cartesian(0, (Y, X, 1), (X, 0, 1)),),
                exact_checks=True,
            ),
            DoubleVariant(
                _cartesian(X + Y, (X, 0, Y), (Y, 0, 2)),
                sp.Integer(4),
                stated=_cartesian(X + Y, (X, 0, Y), (Y, 0, 2)),
                checks=(_cartesian(0, (Y, X, 2), (X, 0, 2)),),
                exact_checks=True,
            ),
        ),
    ),
    # Level 3: polar over a disk, an annulus or a sector, with the system named.
    "polar_disk": DoubleTemplate(
        3,
        "polar",
        (
            DoubleVariant(
                _polar(R**2, (0, 2), (0, 2 * _PI)),
                8 * _PI,
                integrand=X**2 + Y**2,
                region=r"\left\{(x,y) : x^{2}+y^{2} \le 4\right\}",
                checks=(_disk(2),),
                missing_r=16 * _PI / 3,
            ),
            DoubleVariant(
                _polar(sp.Integer(1), (0, 3), (0, 2 * _PI)),
                9 * _PI,
                integrand=sp.Integer(1),
                region=r"\left\{(x,y) : x^{2}+y^{2} \le 9\right\}",
                checks=(_disk(3),),
                missing_r=6 * _PI,
            ),
            DoubleVariant(
                _polar(R, (0, 1), (0, 2 * _PI)),
                2 * _PI / 3,
                integrand=sp.sqrt(X**2 + Y**2),
                region=r"\left\{(x,y) : x^{2}+y^{2} \le 1\right\}",
                # The Cartesian set-up has a kink at the origin: no clean check.
                missing_r=_PI,
            ),
        ),
    ),
    "polar_annulus": DoubleTemplate(
        3,
        "polar",
        (
            DoubleVariant(
                _polar(sp.Integer(1), (1, 2), (0, 2 * _PI)),
                3 * _PI,
                integrand=sp.Integer(1),
                region=r"\left\{(x,y) : 1 \le x^{2}+y^{2} \le 4\right\}",
                missing_r=2 * _PI,
            ),
            DoubleVariant(
                _polar(1 / R**2, (1, _E), (0, 2 * _PI)),
                2 * _PI,
                integrand=1 / (X**2 + Y**2),
                region=r"\left\{(x,y) : 1 \le x^{2}+y^{2} \le e^{2}\right\}",
                missing_r=2 * _PI * (1 - 1 / _E),
            ),
        ),
    ),
    "polar_sector": DoubleTemplate(
        3,
        "polar",
        (
            DoubleVariant(
                _polar(R * sp.cos(THETA), (0, 2), (0, _PI / 2)),
                sp.Rational(8, 3),
                integrand=X,
                region=r"\left\{(x,y) : x^{2}+y^{2} \le 4,\ x \ge 0,\ y \ge 0\right\}",
                checks=(_cartesian(0, (Y, 0, _QUARTER_EDGE), (X, 0, 2)),),
                missing_r=sp.Integer(2),
                exact_checks=True,
            ),
            DoubleVariant(
                _polar(R**2, (0, 2), (0, _PI)),
                4 * _PI,
                integrand=X**2 + Y**2,
                region=r"\left\{(x,y) : x^{2}+y^{2} \le 4,\ y \ge 0\right\}",
                checks=(_cartesian(0, (Y, 0, _QUARTER_EDGE), (X, -2, 2)),),
                missing_r=8 * _PI / 3,
            ),
        ),
    ),
    # Level 4: reverse the order of integration; the given order has no elementary
    # inner antiderivative.
    "reverse_order": DoubleTemplate(
        4,
        None,
        (
            DoubleVariant(
                _cartesian(sp.exp(X**2), (Y, 0, X), (X, 0, 1)),
                (_E - 1) / 2,
                stated=_cartesian(sp.exp(X**2), (X, Y, 1), (Y, 0, 1)),
            ),
            DoubleVariant(
                _cartesian(sp.exp(X**3), (Y, 0, X**2), (X, 0, 1)),
                (_E - 1) / 3,
                stated=_cartesian(sp.exp(X**3), (X, sp.sqrt(Y), 1), (Y, 0, 1)),
            ),
            DoubleVariant(
                _cartesian(sp.sin(Y) / Y, (X, 0, Y), (Y, 0, _PI)),
                sp.Integer(2),
                stated=_cartesian(sp.sin(Y) / Y, (Y, X, _PI), (X, 0, _PI)),
            ),
        ),
    ),
    # Level 4: bounds from a set description; the learner chooses the system.
    "region_choice": DoubleTemplate(
        4,
        None,
        (
            DoubleVariant(
                _polar(3 * R * sp.sin(THETA), (0, 1), (0, _PI)),
                sp.Integer(2),
                integrand=3 * Y,
                region=r"\left\{(x,y) : x^{2}+y^{2} \le 1,\ y \ge 0\right\}",
                checks=(_cartesian(0, (Y, 0, _HALF_EDGE), (X, -1, 1)),),
                missing_r=sp.Integer(3),
                exact_checks=True,
            ),
            DoubleVariant(
                _cartesian(X, (Y, X**2, X), (X, 0, 1)),
                sp.Rational(1, 12),
                integrand=X,
                region=r"\left\{(x,y) : x^{2} \le y \le x\right\}",
                checks=(_cartesian(0, (X, Y, sp.sqrt(Y)), (Y, 0, 1)),),
                exact_checks=True,
            ),
            DoubleVariant(
                _polar(1 / R, (1, 3), (0, _PI)),
                2 * _PI,
                integrand=1 / sp.sqrt(X**2 + Y**2),
                region=r"\left\{(x,y) : 1 \le x^{2}+y^{2} \le 9,\ y \ge 0\right\}",
                missing_r=_PI * sp.log(3),
            ),
        ),
    ),
    # Level 5: a Cartesian integral that is only clean in polar, plus an inner
    # substitution.
    "polar_conversion": DoubleTemplate(
        5,
        None,
        (
            DoubleVariant(
                _polar(sp.exp(R**2), (0, 1), (0, _PI)),
                _PI * (_E - 1) / 2,
                stated=_cartesian(sp.exp(X**2 + Y**2), (Y, 0, _HALF_EDGE), (X, -1, 1)),
            ),
            DoubleVariant(
                _polar(1 / (1 + R**2), (0, 1), (0, _PI / 2)),
                _PI * sp.log(2) / 4,
                stated=_cartesian(1 / (1 + X**2 + Y**2), (Y, 0, _HALF_EDGE), (X, 0, 1)),
                missing_r=_PI**2 / 8,
            ),
            DoubleVariant(
                _polar(R**2 * sp.exp(R**2), (0, 1), (0, 2 * _PI)),
                _PI,
                stated=_cartesian(
                    (X**2 + Y**2) * sp.exp(X**2 + Y**2), (Y, -_HALF_EDGE, _HALF_EDGE), (X, -1, 1)
                ),
            ),
        ),
    ),
}


def _statement(template: DoubleTemplate, variant: DoubleVariant, a: Any) -> str:
    if variant.stated is not None:
        return iterated_latex(variant.stated.scaled(a))
    integrand = sp.latex(a * variant.integrand)
    statement = rf"\iint_D \left({integrand}\right)\,dA,\quad D = {variant.region}"
    if template.named == "polar":
        statement += r"\quad\text{(polar coordinates)}"
    elif template.named == "cartesian":
        statement += r"\quad\text{(Cartesian coordinates)}"
    return statement


def _steps(variant: DoubleVariant, a: Any, value: Any) -> tuple[dict[str, str], ...]:
    solution = variant.solution.scaled(a)
    steps: list[dict[str, str]] = []
    if variant.stated is None or variant.stated.bounds != variant.solution.bounds:
        if solution.system == "polar":
            steps.append({"key": "describe_polar", "latex": bounds_latex(solution)})
            steps.append({"key": "polar_change", "latex": iterated_latex(solution)})
        else:
            steps.append({"key": "describe_region", "latex": bounds_latex(solution)})
            key: str = "write_iterated" if variant.stated is None else "reverse_order"
            steps.append({"key": key, "latex": iterated_latex(solution)})
    steps.extend(integration_steps(solution, ("integrate_inner", "integrate_outer")))
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
