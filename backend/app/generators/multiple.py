"""ADR-005: shared pieces of the multiple-integral generators (double-v1, triple-v1).

A set-up is one iterated integral in one coordinate system: the integrand in that
system's variables without the Jacobian factor, and its bounds innermost first.
The answer to a multiple integral is its exact value, so the answer worker never
integrates: templates declare their values, and `verify=True` replays recompute
them with SymPy and cross-check them by numerical quadrature.
"""

from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any, Literal

import mpmath
import sympy as sp
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.generators.definite import is_clean_value, value_latex

Y = sp.Symbol("y", real=True)
R = sp.Symbol("r", positive=True)
THETA = sp.Symbol("theta", real=True)

type System = Literal["cartesian", "polar", "cylindrical"]
type Bound = tuple[Any, Any, Any]

# Numerical cross-checks: a disagreement beyond this is a template error.
_QUAD_DIGITS = 25
_QUAD_TOLERANCE = mpmath.mpf("1e-15")


@dataclass(frozen=True)
class Setup:
    system: System
    integrand: Any
    # (variable, lower, upper), innermost first; a bound uses only outer variables.
    bounds: tuple[Bound, ...]

    def scaled(self, coefficient: Any) -> "Setup":
        return replace(self, integrand=coefficient * self.integrand)


def jacobian(system: System) -> Any:
    return sp.Integer(1) if system == "cartesian" else R


def integrand_with_jacobian(setup: Setup) -> Any:
    return setup.integrand * jacobian(setup.system)


def integrate_setup(setup: Setup, *, with_jacobian: bool = True) -> Any:
    """The exact value by iterated SymPy integration, innermost first."""
    expression = integrand_with_jacobian(setup) if with_jacobian else setup.integrand
    for variable, lower, upper in setup.bounds:
        expression = sp.integrate(expression, (variable, lower, upper))
    return sp.simplify(expression)


def quadrature(setup: Setup) -> Any:
    """An independent numerical value of the set-up, for cross-checks only.

    Nested quadrature at this precision is too slow beyond two levels, so SymPy
    integrates the innermost levels of a triple set-up exactly (in z, a polynomial
    or a simple rational step) and mpmath the outer two.
    """
    expression = integrand_with_jacobian(setup)
    *inner, outer, last = setup.bounds
    for variable, lower, upper in inner:
        expression = sp.integrate(expression, (variable, lower, upper))
    setup = Setup(setup.system, expression, (outer, last))
    variables = [variable for variable, _, _ in setup.bounds]
    integrand = sp.lambdify(variables, setup.integrand, "mpmath")
    bounds = [
        (
            sp.lambdify(variables, lower, "mpmath"),
            sp.lambdify(variables, upper, "mpmath"),
        )
        for _, lower, upper in setup.bounds
    ]

    def level(index: int, values: list[Any]) -> Any:
        if index < 0:
            return integrand(*values)
        lower, upper = bounds[index]

        def inner(point: Any) -> Any:
            values[index] = point
            return level(index - 1, values)

        # Bounds of level `index` use only the outer variables, already set in `values`.
        low, high = lower(*values), upper(*values)
        # Solids such as a cone have a kink on the axis; quadrature needs it as a node.
        return mpmath.quad(inner, [low, 0, high] if low < 0 < high else [low, high])

    with mpmath.workdps(_QUAD_DIGITS):
        return level(len(variables) - 1, [mpmath.mpf(0)] * len(variables))


def agrees(setup: Setup, value: Any) -> bool:
    with mpmath.workdps(_QUAD_DIGITS):
        return bool(
            abs(quadrature(setup) - mpmath.mpf(sp.N(value, _QUAD_DIGITS))) < _QUAD_TOLERANCE
        )


def differential(setup: Setup) -> str:
    names = "".join(rf"\,d{sp.latex(variable)}" for variable, _, _ in setup.bounds)
    return names if setup.system == "cartesian" else names.replace(r"\,dr", r"\,r\,dr", 1)


def iterated_latex(setup: Setup) -> str:
    """`∫∫ f dy dx` with outer bounds first; polar and cylindrical show `r dr`."""
    integrals = "".join(
        rf"\int_{{{sp.latex(lower)}}}^{{{sp.latex(upper)}}}"
        for _, lower, upper in reversed(setup.bounds)
    )
    return rf"{integrals} \left({sp.latex(setup.integrand)}\right){differential(setup)}"


def bounds_latex(setup: Setup) -> str:
    """The region as inequalities, outer variable first: `0 \\le x \\le 1,\\ 0 \\le y \\le x`."""
    return r",\quad ".join(
        rf"{sp.latex(lower)} \le {sp.latex(variable)} \le {sp.latex(upper)}"
        for variable, lower, upper in reversed(setup.bounds)
    )


def integration_steps(setup: Setup, says: tuple[str, ...]) -> tuple[dict[str, str], ...]:
    """One step per integration, innermost first; `says` has one instruction per level."""
    steps = []
    expression = integrand_with_jacobian(setup)
    for (variable, lower, upper), say in zip(setup.bounds, says, strict=True):
        result = sp.simplify(sp.integrate(expression, (variable, lower, upper)))
        steps.append(
            {
                "say": say,
                "latex": (
                    rf"\int_{{{sp.latex(lower)}}}^{{{sp.latex(upper)}}}"
                    rf" \left({sp.latex(expression)}\right)\,d{sp.latex(variable)}"
                    rf" = {value_latex(result) if result.is_number else sp.latex(result)}"
                ),
            }
        )
        expression = result
    return tuple(steps)


class MultipleParameters(BaseModel):
    """Private replay record of a multiple integral; no expression strings."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    generator_version: Literal["double-v1", "triple-v1"]
    template: str = Field(max_length=32)
    variant: int = Field(ge=0, le=9)
    coefficient: int = Field(ge=-3, le=3)

    @field_validator("coefficient")
    @classmethod
    def nonzero_coefficient(cls, value: int) -> int:
        if value == 0:
            raise ValueError("Coefficient must be nonzero")
        return value


@dataclass(frozen=True)
class ValueProblem:
    """What the answer worker needs: an exact value and the declared wrong values."""

    parameters: MultipleParameters
    topic: str
    difficulty: int
    value: Any
    # (code, wrong value at this record's coefficient); `bounds_reversed` is implied.
    mistakes: tuple[tuple[str, Any], ...]


def verify_value(
    value: Any,
    solution: Setup,
    checks: tuple[Setup, ...],
    exact_checks: Callable[[Setup], bool] = lambda _setup: False,
) -> None:
    """The declared value is the exact SymPy value of the solution set-up, it is clean,
    and every other set-up of the same region agrees numerically (exactly if asked)."""
    if not is_clean_value(value):
        raise RuntimeError("Multiple-integral value is not pedagogically clean")
    if sp.simplify(integrate_setup(solution) - value) != 0:
        raise RuntimeError("Declared value differs from the solution set-up")
    for setup in (solution, *checks):
        if not agrees(setup, value):
            raise RuntimeError("Set-ups of one region disagree numerically")
        if setup is not solution and exact_checks(setup):
            if sp.simplify(integrate_setup(setup) - value) != 0:
                raise RuntimeError("Set-ups of one region disagree exactly")


def verify_missing_jacobian(declared: Any, solution: Setup) -> None:
    """A declared missing-`r` value is the value without the factor; None if it is not clean."""
    if solution.system == "cartesian":
        if declared is not None:
            raise RuntimeError("A Cartesian set-up has no Jacobian factor to miss")
        return
    computed = integrate_setup(solution, with_jacobian=False)
    if declared is None:
        if computed.is_number and is_clean_value(computed):
            raise RuntimeError("A clean missing-r value must be declared")
        return
    if sp.simplify(computed - declared) != 0:
        raise RuntimeError("Declared missing-r value is wrong")
