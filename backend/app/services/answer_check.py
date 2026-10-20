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
from app.generators.core import FAMILY_VERSIONS, Exercise, replay
from app.generators.families import FamilyProblem, replay_family
from app.services.math_parser import MathNode

type Problem = InternalProblem | Exercise | FamilyProblem

type Outcome = Literal["correct", "incorrect", "missing_constant", "invalid", "inconclusive"]
type Verdict = Literal["yes", "no", "unknown"]

_T = sp.Symbol("t", positive=True)
# Sample points avoid 0 and the values templates use; positive t covers x > 0 or x < 0.
_REAL_SAMPLES = (-2.75, -1.3, -0.45, 0.35, 1.15, 2.6)
_POSITIVE_SAMPLES = (0.35, 1.15, 2.6, 4.2)
_PRECISION = 50
_TOLERANCE = sp.Float("1e-12", _PRECISION)


def replay_problem(record: Mapping[str, object]) -> Problem:
    """Rebuild the trusted problem from its private JSON record (no expression strings)."""
    if record.get("generator_version") == "basic-v1":
        return replay_basic(dict(record))
    if record.get("generator_version") == "substitution-v1":
        return replay(dict(record))
    if record.get("generator_version") in FAMILY_VERSIONS:
        return replay_family(dict(record))
    raise ValueError("Unsupported generator version")


def _domain(problem: Problem) -> Any:
    """The template's declared real domain as a SymPy set."""
    domain = problem.template.domain
    if not isinstance(domain, str):
        return domain
    if domain == "real":
        return sp.S.Reals
    if domain == "positive":
        return sp.Interval.open(0, sp.oo)
    return sp.Union(sp.Interval.open(-sp.oo, 0), sp.Interval.open(0, sp.oo))


def _components(problem: Problem) -> tuple[tuple[Any, Any, tuple[float, ...]], ...]:
    """(replacement for x, variable it is written in, samples) per connected component.

    A positive `t` covers each open interval, as the generators' own proofs do:
    `a + t` and `b - t` for unbounded ones and `a + (b - a)t/(1 + t)` for (a, b).
    """
    domain = _domain(problem)
    if domain == sp.S.Reals:
        return ((X, X, _REAL_SAMPLES),)
    parts = domain.args if isinstance(domain, sp.Union) else (domain,)
    components = []
    for part in parts:
        if not isinstance(part, sp.Interval) or not (part.left_open and part.right_open):
            raise ValueError("Unsupported problem domain")
        if part.start == -sp.oo:
            replacement = part.end - _T
        elif part.end == sp.oo:
            replacement = part.start + _T
        else:
            replacement = part.start + (part.end - part.start) * _T / (1 + _T)
        components.append((replacement, _T, _POSITIVE_SAMPLES))
    return tuple(components)


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


def _is_primitive(candidate: Any, problem: Problem) -> Verdict:
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
        if realness is None and not _defined_throughout(candidate, problem):
            # e.g. log(x^2) on all reals: undefined at 0, which no sample point hits.
            if _not_real(expression, variable, samples):
                return "no"
            undecided = True
    return "unknown" if undecided else "yes"


def _defined_throughout(expression: Any, problem: Problem) -> bool:
    """A symbolic proof that `expression` is real and continuous on the whole domain.

    It settles `ln|x^2 + x|` on (-1, 0), whose sign SymPy cannot infer from `t`.
    """
    from sympy.calculus.util import continuous_domain

    try:
        gap = _domain(problem) - continuous_domain(expression, X, sp.S.Reals)
    except (NotImplementedError, ValueError, TypeError):
        return False
    return bool(gap == sp.S.EmptySet)


def _same_number_everywhere(offset: Any, problem: Problem) -> Verdict:
    """ADR-003: after removing the known primitive, `b` must be one numeric constant.

    Only called once both primitives are proven, so `offset` has a zero derivative
    and is constant on each component. If SymPy cannot reduce it in `t`, its exact
    value at the rational point t = 1 is that constant.
    """
    values = []
    for replacement, variable, _samples in _components(problem):
        value = sp.simplify(offset.subs(X, replacement))
        if not value.is_number and variable == _T:
            value = sp.simplify(value.subs(_T, sp.Integer(1)))
        if not value.is_number:
            return "unknown"
        values.append(value)
    if all(sp.simplify(value - values[0]) == 0 for value in values[1:]):
        return "yes"
    return "no"


def classify(answer: Any, problem: Problem) -> Outcome:
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


def check_tree(tree: MathNode, problem: Problem) -> Outcome:
    """Check every subexpression before evaluation can cancel a domain hole.

    On all-real domains a hole is `invalid`, as for the preview cells. On other
    domains a part that is undefined somewhere in the domain makes the answer
    `incorrect`, matching how `ln(x)` is treated where `x < 0` is allowed.
    """
    from sympy.calculus.util import continuous_domain

    from app.services.math_worker import _build_sympy

    domain = _domain(problem)
    all_reals = domain == sp.S.Reals
    stack = [tree]
    while stack:
        item = stack.pop()
        value = _build_sympy(item)
        if value.has(sp.zoo, sp.oo, -sp.oo, sp.nan):
            return "invalid"
        try:
            defined = continuous_domain(value, X, sp.S.Reals)
            if defined == sp.S.EmptySet or (all_reals and defined != sp.S.Reals):
                return "invalid"
            if not all_reals:
                # `is_subset` is undecided for unions; an evaluated gap is a set of points.
                gap = domain - defined
                if gap != sp.S.EmptySet and not isinstance(gap, sp.Complement):
                    return "incorrect"
            for constant in value.free_symbols - {X}:
                if continuous_domain(value, constant, sp.S.Reals) != sp.S.Reals:
                    return "invalid"
        except (NotImplementedError, ValueError, TypeError):
            # e.g. `ln|x| + C` in C needs the sign of |x|; its parts are still checked.
            if all_reals:
                return "inconclusive"
        stack.extend(item.children)
    return classify(_build_sympy(tree, evaluate=True), problem)
