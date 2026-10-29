"""ADR-003 equivalence of a learner antiderivative. Runs only inside the limited worker.

Symbolic proof decides `correct`. Numerical evaluation is used only to certify
that two expressions differ (or that an answer is not real) at a point of the
declared domain; it never proves equality. Anything undecided is `inconclusive`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

import sympy as sp

from app.generators.basic import InternalProblem, X, replay_basic
from app.generators.core import FAMILY_VERSIONS, Exercise, replay
from app.generators.definite import DefiniteProblem, replay_definite
from app.generators.derivatives import VERSION as DERIVATIVES_VERSION
from app.generators.derivatives import DerivativeProblem, replay_derivative
from app.generators.double import replay_value as replay_double_value
from app.generators.families import FamilyProblem, replay_family
from app.generators.mistakes import declared
from app.generators.multiple import ValueProblem
from app.generators.partial import PartialProblem, replay_partial
from app.generators.symbolic import replay_symbolic
from app.generators.triple import replay_value as replay_triple_value
from app.services import partial_check
from app.services.math_parser import MathNode, VariableDomain


@dataclass(frozen=True)
class ExpressionProblem:
    """ADR-005: the answer is an expression in the template's declared variables,
    such as a derivative. `expected` is written in `variable_symbol` symbols."""

    expected: Any
    variables: Mapping[str, VariableDomain]


type Problem = (
    InternalProblem
    | Exercise
    | FamilyProblem
    | DefiniteProblem
    | DerivativeProblem
    | ExpressionProblem
    | PartialProblem
    | ValueProblem
)

# The problems whose answer is an antiderivative, checked up to a constant.
type Integral = InternalProblem | Exercise | FamilyProblem | DefiniteProblem
# The problems whose answer is a function of x on a declared domain.
type Symbolic = Integral | DerivativeProblem
# Problems whose answer is one exact number: definite and multiple integrals.
_VALUE_PROBLEMS = (DefiniteProblem, ValueProblem)

type Outcome = Literal["correct", "incorrect", "missing_constant", "invalid", "inconclusive"]
type Verdict = Literal["yes", "no", "unknown"]

_T = sp.Symbol("t", positive=True)
# Sample points avoid 0 and the values templates use; positive t covers x > 0 or x < 0.
_REAL_SAMPLES = (-2.75, -1.3, -0.45, 0.35, 1.15, 2.6)
_POSITIVE_SAMPLES = (0.35, 1.15, 2.6, 4.2)
_PRECISION = 50
_TOLERANCE = sp.Float("1e-12", _PRECISION)


def variable_symbol(name: str, domain: VariableDomain) -> Any:
    """The SymPy symbol for a declared variable on its domain (`r > 0`, say)."""
    return sp.Symbol(name, positive=True) if domain == "positive" else sp.Symbol(name, real=True)


def replay_problem(record: Mapping[str, object]) -> Problem:
    """Rebuild the trusted problem from its private JSON record (no expression strings)."""
    if record.get("generator_version") == "basic-v1":
        return replay_basic(dict(record))
    if record.get("generator_version") == "substitution-v1":
        return replay(dict(record))
    if record.get("generator_version") in FAMILY_VERSIONS:
        return replay_family(dict(record), verify=False)
    if record.get("generator_version") == "definite-v1":
        return replay_definite(dict(record), verify=False)
    if record.get("generator_version") == "double-v1":
        return replay_double_value(dict(record))
    if record.get("generator_version") == DERIVATIVES_VERSION:
        return replay_derivative(dict(record), verify=False)
    if record.get("generator_version") == "partial-v1":
        return replay_partial(dict(record), verify=False)
    if record.get("generator_version") == "symbolic-v1":
        symbolic = replay_symbolic(dict(record))
        return ExpressionProblem(symbolic.expected, symbolic.variables)
    if record.get("generator_version") == "triple-v1":
        return replay_triple_value(dict(record))
    raise ValueError("Unsupported generator version")


def _domain(problem: Symbolic) -> Any:
    """The template's declared real domain as a SymPy set."""
    domain = problem.template.domain
    if not isinstance(domain, str):
        return domain
    if domain == "real":
        return sp.S.Reals
    if domain == "positive":
        return sp.Interval.open(0, sp.oo)
    return sp.Union(sp.Interval.open(-sp.oo, 0), sp.Interval.open(0, sp.oo))


def _components(problem: Symbolic) -> tuple[tuple[Any, Any, tuple[float, ...]], ...]:
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


def _is_primitive(candidate: Any, problem: Integral) -> Verdict:
    """Does `candidate` differentiate to the integrand and stay real on every component?"""
    undecided = False
    defined: bool | None = None  # computed once, only if some component needs it
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
        if realness is None and defined is None:
            defined = _defined_throughout(candidate, problem)
        if realness is None and not defined:
            # e.g. log(x^2) on all reals: undefined at 0, which no sample point hits.
            if _not_real(expression, variable, samples):
                return "no"
            undecided = True
    return "unknown" if undecided else "yes"


def _defined_throughout(expression: Any, problem: Symbolic) -> bool:
    """A symbolic proof that `expression` is real and continuous on the whole domain.

    It settles `ln|x^2 + x|` on (-1, 0), whose sign SymPy cannot infer from `t`.
    """
    from sympy.calculus.util import continuous_domain

    try:
        gap = _domain(problem) - continuous_domain(expression, X, sp.S.Reals)
    except (NotImplementedError, ValueError, TypeError):
        return False
    return bool(gap == sp.S.EmptySet)


def _same_number_everywhere(offset: Any, problem: Symbolic) -> Verdict:
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


def _classify_definite(answer: Any, problem: DefiniteProblem | ValueProblem) -> Outcome:
    """ADR-003: a definite answer is one real number, with no `x` and no constant.
    ADR-005 answers multiple integrals the same way."""
    if answer.free_symbols:
        return "incorrect"
    difference = answer - problem.value
    if sp.simplify(difference) == 0:
        return "correct"
    value = difference.evalf(_PRECISION)
    if value.has(sp.nan, sp.zoo, sp.oo, -sp.oo) or not value.is_number:
        return "incorrect"
    # A certified difference, or a non-real value such as ln(-2), is incorrect.
    return "incorrect" if abs(value) > _TOLERANCE else "inconclusive"


def _expression_points(problem: ExpressionProblem) -> tuple[dict[Any, Any], ...]:
    """Bounded sample points of the declared domain, one value per variable each.

    The variables take their samples at different offsets, so no point lies on a
    diagonal such as x = y where unequal answers can agree.
    """
    symbols = [variable_symbol(name, domain) for name, domain in problem.variables.items()]
    samples = [
        _POSITIVE_SAMPLES if domain == "positive" else _REAL_SAMPLES
        for domain in problem.variables.values()
    ]
    points = []
    for index in range(len(_REAL_SAMPLES)):
        points.append(
            {
                symbol: sp.Rational(str(values[(index + 2 * offset) % len(values)]))
                for offset, (symbol, values) in enumerate(zip(symbols, samples, strict=True))
            }
        )
    return tuple(points)


def _classify_expression(answer: Any, problem: ExpressionProblem) -> Outcome:
    """Symbolic proof on the declared domain; samples only certify a difference."""
    names = {name: variable_symbol(name, domain) for name, domain in problem.variables.items()}
    if any(symbol.name not in names for symbol in answer.free_symbols):
        return "invalid"
    # The parser builds real symbols; give each one its declared domain.
    answer = answer.xreplace({sp.Symbol(name, real=True): s for name, s in names.items()})
    difference = answer - problem.expected
    if sp.simplify(difference) == 0:
        return "correct"
    for point in _expression_points(problem):
        value = difference.evalf(_PRECISION, subs=point)
        if value.has(sp.nan, sp.zoo, sp.oo, -sp.oo) or not value.is_number:
            return "incorrect"
        # A certified difference, or a non-real value such as ln(-y), is incorrect.
        if abs(value) > _TOLERANCE:
            return "incorrect"
    return "inconclusive"


def _classify_derivative(answer: Any, problem: DerivativeProblem) -> Outcome:
    """ADR-005: f'(x) itself, equal on every component; an added constant is wrong."""
    if answer.free_symbols - {X}:
        return "incorrect"
    undecided = False
    for replacement, variable, samples in _components(problem):
        difference = answer.subs(X, replacement) - problem.derivative.subs(X, replacement)
        if sp.simplify(difference) == 0:
            continue
        if _differs(difference, variable, samples):
            return "incorrect"
        undecided = True
    return "inconclusive" if undecided else "correct"


def classify(answer: Any, problem: Problem) -> Outcome:
    """`answer` is the evaluated SymPy form of a parsed learner expression."""
    if answer.has(sp.nan, sp.zoo, sp.oo, -sp.oo):
        return "invalid"
    if isinstance(problem, _VALUE_PROBLEMS):
        return _classify_definite(answer, problem)
    if isinstance(problem, ExpressionProblem):
        return _classify_expression(answer, problem)
    if isinstance(problem, DerivativeProblem):
        return _classify_derivative(answer, problem)
    if isinstance(problem, PartialProblem):
        return partial_check.classify(answer, problem)
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

    if isinstance(problem, (*_VALUE_PROBLEMS, ExpressionProblem, PartialProblem)):
        # Every part must have a value: `0/(1 - 1) + 2` is invalid, not 2.
        stack = [tree]
        while stack:
            item = stack.pop()
            if _build_sympy(item, evaluate=True).has(sp.zoo, sp.oo, -sp.oo, sp.nan):
                return "invalid"
            stack.extend(item.children)
        if isinstance(problem, PartialProblem):
            return partial_check.classify(_build_sympy(tree, evaluate=True), problem)
        return classify(_build_sympy(tree, evaluate=True), problem)
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


def _differ_by_constant(left: Any, right: Any) -> bool:
    """A proof that `left - right` is one number. A per-component constant is not
    enough: `ln(x)` and `ln|x|` have the same derivative but are different answers."""
    return X not in sp.simplify(left - right).free_symbols


def _definite_value(expression: Any, problem: DefiniteProblem) -> Any:
    from sympy.calculus.util import continuous_domain

    interval = sp.Interval(problem.lower, problem.upper)
    if interval.is_subset(continuous_domain(expression, X, sp.S.Reals)) is not True:
        return None
    return expression.subs(X, problem.upper) - expression.subs(X, problem.lower)


def _base_record(problem: DefiniteProblem) -> dict[str, object]:
    from app.generators.definite import TEMPLATES, base_record

    return base_record(TEMPLATES[problem.parameters.template], problem.parameters.coefficient)


def _definite_mistakes(answer: Any, problem: DefiniteProblem) -> set[str]:
    constants = answer.free_symbols - {X}
    if len(constants) > 1:
        return set()
    plain = answer.subs(dict.fromkeys(constants, 0))
    if X in plain.free_symbols:
        # An antiderivative written as the answer, without evaluating it at the bounds.
        if _differ_by_constant(plain, problem.antiderivative):
            return {"definite_not_evaluated"}
        return set()
    if constants:
        return {"definite_constant"} if sp.simplify(plain - problem.value) == 0 else set()
    codes = {"bounds_reversed"} if sp.simplify(answer + problem.value) == 0 else set()
    for code, wrong in declared(_base_record(problem), problem.antiderivative):
        value = _definite_value(wrong, problem)
        # A mistake that still gives the right value on these bounds is not diagnosable.
        if value is None or sp.simplify(value - problem.value) == 0:
            continue
        if sp.simplify(answer - value) == 0:
            codes.add(code)
    return codes


def _multiple_mistakes(answer: Any, problem: ValueProblem) -> set[str]:
    """ADR-005: a sign error from reversed bounds, or a declared wrong value."""
    if answer.free_symbols:
        return set()
    codes = {"bounds_reversed"} if sp.simplify(answer + problem.value) == 0 else set()
    for code, wrong in problem.mistakes:
        # A mistake that still gives the right value is not diagnosable.
        if sp.simplify(wrong - problem.value) != 0 and sp.simplify(answer - wrong) == 0:
            codes.add(code)
    return codes


def _derivative_mistakes(answer: Any, problem: DerivativeProblem) -> set[str]:
    """A derivative is compared exactly: `f' + 1` is not `f'`, unlike antiderivatives."""
    constants = answer.free_symbols - {X}
    if len(constants) > 1:
        return set()
    if constants:
        plain = answer.subs(dict.fromkeys(constants, 0))
        same = sp.simplify(plain - problem.derivative) == 0
        return {"derivative_constant"} if same else set()
    return {code for code, wrong in problem.mistakes() if sp.simplify(answer - wrong) == 0}


def diagnose(answer: Any, problem: Problem, record: Mapping[str, object]) -> str | None:
    """The one declared mistake an incorrect answer matches, or None for a general hint.

    Only called after `classify` returned `incorrect`. Two matching codes, or a
    match that cannot be proven symbolically, give no diagnosis: never a guess.
    """
    if isinstance(problem, PartialProblem):
        return partial_check.diagnose(answer, problem)
    if isinstance(problem, ExpressionProblem):
        # Templates that use declared variables bring their own mistakes (#97, #101).
        return None
    if isinstance(problem, DefiniteProblem):
        codes = _definite_mistakes(answer, problem)
    elif isinstance(problem, ValueProblem):
        codes = _multiple_mistakes(answer, problem)
    elif isinstance(problem, DerivativeProblem):
        codes = _derivative_mistakes(answer, problem)
    else:
        constants = answer.free_symbols - {X}
        if len(constants) > 1:
            return None
        plain = answer.subs(dict.fromkeys(constants, 0))
        codes = {
            code
            for code, wrong in declared(dict(record), problem.antiderivative)
            if _differ_by_constant(plain, wrong)
        }
    return codes.pop() if len(codes) == 1 else None


def check_and_diagnose(
    tree: MathNode, problem: Problem, record: Mapping[str, object]
) -> tuple[Outcome, str | None]:
    from app.services.math_worker import _build_sympy

    outcome = check_tree(tree, problem)
    if outcome != "incorrect":
        return outcome, None
    return outcome, diagnose(_build_sympy(tree, evaluate=True), problem, record)
