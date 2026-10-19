"""ADR-003 equivalence of a learner antiderivative. Runs only inside the limited worker.

Symbolic proof decides `correct`. Numerical evaluation is used only to certify
that two expressions differ (or that an answer is not real) at a point of the
declared domain; it never proves equality. Anything undecided is `inconclusive`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

import sympy as sp

from app.generators.basic import InternalProblem, X, replay_basic

type Outcome = Literal["correct", "incorrect", "missing_constant", "invalid", "inconclusive"]
type Verdict = Literal["yes", "no", "unknown"]

_T = sp.Symbol("t", positive=True)
# Sample points avoid 0 and the values templates use; positive t covers x > 0 or x < 0.
_REAL_SAMPLES = (-2.75, -1.3, -0.45, 0.35, 1.15, 2.6)
_POSITIVE_SAMPLES = (0.35, 1.15, 2.6, 4.2)
_PRECISION = 50
_TOLERANCE = sp.Float("1e-12", _PRECISION)


def replay_problem(record: Mapping[str, object]) -> InternalProblem:
    """Rebuild the trusted problem from its private JSON record (no expression strings)."""
    if record.get("generator_version") == "basic-v1":
        return replay_basic(dict(record))
    raise ValueError("Unsupported generator version")


def _components(problem: InternalProblem) -> tuple[tuple[Any, Any, tuple[float, ...]], ...]:
    """(replacement for x, variable it is written in, samples) per connected component."""
    domain = problem.template.domain
    if domain == "real":
        return ((X, X, _REAL_SAMPLES),)
    if domain == "positive":
        return ((_T, _T, _POSITIVE_SAMPLES),)
    return ((_T, _T, _POSITIVE_SAMPLES), (-_T, _T, _POSITIVE_SAMPLES))


def _value(expression: Any, variable: Any, point: float) -> Any:
    # evalf with `subs` raises working precision on cancellation; exact rational points.
    return expression.evalf(_PRECISION, subs={variable: sp.Rational(str(point))})


def _differs(expression: Any, variable: Any, samples: tuple[float, ...]) -> bool:
    """A certified nonzero (or undefined) value at some sample point."""
    for point in samples:
        value = _value(expression, variable, point)
        if value.has(sp.nan, sp.zoo, sp.oo, -sp.oo) or not value.is_number:
            return True
        if abs(value) > _TOLERANCE:
            return True
    return False


def _not_real(expression: Any, variable: Any, samples: tuple[float, ...]) -> bool:
    for point in samples:
        value = _value(expression, variable, point)
        if value.has(sp.nan, sp.zoo, sp.oo, -sp.oo) or abs(sp.im(value)) > _TOLERANCE:
            return True
    return False


def _is_primitive(candidate: Any, problem: InternalProblem) -> Verdict:
    """Does `candidate` differentiate to the integrand and stay real on every component?"""
    undecided = False
    for replacement, variable, samples in _components(problem):
        expression = candidate.subs(X, replacement)
        integrand = problem.integrand.subs(X, replacement)
        chain = sp.diff(replacement, variable)
        difference = sp.diff(expression, variable) / chain - integrand
        if sp.simplify(difference) != 0:
            if _differs(difference, variable, samples):
                return "no"
            undecided = True
        realness = expression.is_real
        if realness is False:
            return "no"
        if realness is None:
            # e.g. log(x^2) on all reals: undefined at 0, which no sample point hits.
            if _not_real(expression, variable, samples):
                return "no"
            undecided = True
    return "unknown" if undecided else "yes"


def _same_number_everywhere(offset: Any, problem: InternalProblem) -> Verdict:
    """ADR-003: after removing the known primitive, `b` must be one numeric constant."""
    values = []
    for replacement, _variable, _samples in _components(problem):
        value = sp.simplify(offset.subs(X, replacement))
        if not value.is_number:
            return "unknown"
        values.append(value)
    if all(sp.simplify(value - values[0]) == 0 for value in values[1:]):
        return "yes"
    return "no"


def classify(answer: Any, problem: InternalProblem) -> Outcome:
    """`answer` is the evaluated SymPy form of a parsed learner expression."""
    if problem.template.is_definite:
        raise ValueError("Definite templates are not supported yet")
    if answer.has(sp.nan, sp.zoo, sp.oo, -sp.oo):
        return "invalid"
    constants = answer.free_symbols - {X}
    if len(constants) > 1:
        return "invalid"
    primitive = answer
    if constants:
        (constant,) = constants
        slope = sp.simplify(sp.diff(answer, constant))
        # The constant must enter as aK + b with a nonzero real number a.
        if not slope.is_number or slope.is_real is not True or slope.is_zero is not False:
            return "incorrect"
        primitive = answer.subs(constant, 0)
    verdict = _is_primitive(primitive, problem)
    if verdict == "unknown":
        return "inconclusive"
    if verdict == "no":
        return "incorrect"
    if not constants:
        return "missing_constant"
    offset = _same_number_everywhere(primitive - problem.antiderivative, problem)
    if offset == "unknown":
        return "inconclusive"
    return "correct" if offset == "yes" else "incorrect"
