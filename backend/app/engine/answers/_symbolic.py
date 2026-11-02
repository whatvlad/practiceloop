"""ADR-003/005 symbolic checks, called only inside the limited math worker.

These helpers mirror the existing checker while taking explicit trusted answer
data rather than importing legacy generator types.
"""

from collections.abc import Mapping
from fractions import Fraction
from typing import Any, Literal

import sympy as sp
from sympy.calculus.util import continuous_domain

from app.engine.models import Outcome
from app.math_input import MathNode, VariableDomain, build_expression

Verdict = Literal["yes", "no", "unknown"]
X = sp.Symbol("x", real=True)
_T = sp.Symbol("t", positive=True)
_REAL_SAMPLES = (-2.75, -1.3, -0.45, 0.35, 1.15, 2.6)
_POSITIVE_SAMPLES = (0.35, 1.15, 2.6, 4.2)
_PRECISION = 50
_TOLERANCE = sp.Float("1e-12", _PRECISION)


def trusted_expression(value: Any) -> Any:
    """Convert trusted integer and fraction constants without parsing text."""
    if type(value) is int:
        return sp.Integer(value)
    if isinstance(value, Fraction):
        return sp.Rational(value.numerator, value.denominator)
    return value


def variable_symbol(name: str, domain: VariableDomain) -> Any:
    if domain == "imaginary":
        raise ValueError("The imaginary unit is a constant, not a variable")
    return sp.Symbol(name, positive=True) if domain == "positive" else sp.Symbol(name, real=True)


def components(domain: Any) -> tuple[tuple[Any, Any, tuple[float, ...]], ...]:
    if domain == sp.S.Reals:
        return ((X, X, _REAL_SAMPLES),)
    parts = domain.args if isinstance(domain, sp.Union) else (domain,)
    result = []
    for part in parts:
        if not isinstance(part, sp.Interval) or not (part.left_open and part.right_open):
            raise ValueError("Unsupported problem domain")
        if part.start == -sp.oo:
            replacement = part.end - _T
        elif part.end == sp.oo:
            replacement = part.start + _T
        else:
            replacement = part.start + (part.end - part.start) * _T / (1 + _T)
        result.append((replacement, _T, _POSITIVE_SAMPLES))
    return tuple(result)


def _value(expression: Any, variable: Any, point: float) -> Any:
    return expression.evalf(_PRECISION, subs={variable: sp.Rational(str(point))})


def differs(expression: Any, variable: Any, samples: tuple[float, ...]) -> bool:
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


def _defined_throughout(expression: Any, domain: Any) -> bool:
    try:
        gap = domain - continuous_domain(expression, X, sp.S.Reals)
    except (NotImplementedError, ValueError, TypeError):
        return False
    return bool(gap == sp.S.EmptySet)


def is_primitive(candidate: Any, integrand: Any, domain: Any) -> Verdict:
    undecided = False
    defined: bool | None = None
    for replacement, variable, samples in components(domain):
        expression = candidate.subs(X, replacement)
        difference = sp.diff(expression, variable) / sp.diff(replacement, variable)
        difference -= integrand.subs(X, replacement)
        if sp.simplify(difference) != 0:
            if differs(difference, variable, samples):
                return "no"
            undecided = True
        realness = expression.is_real
        if realness is False:
            return "no"
        if realness is None and defined is None:
            defined = _defined_throughout(candidate, domain)
        if realness is None and not defined:
            if _not_real(expression, variable, samples):
                return "no"
            undecided = True
    return "unknown" if undecided else "yes"


def same_number_everywhere(offset: Any, domain: Any) -> Verdict:
    values = []
    for replacement, variable, _samples in components(domain):
        value = sp.simplify(offset.subs(X, replacement))
        if not value.is_number and variable == _T:
            value = sp.simplify(value.subs(_T, sp.Integer(1)))
        if not value.is_number:
            return "unknown"
        values.append(value)
    return "yes" if all(sp.simplify(v - values[0]) == 0 for v in values[1:]) else "no"


def check_domain(tree: MathNode, domain: Any) -> Outcome | None:
    """Check unevaluated subexpressions so cancellation cannot erase a hole."""
    all_reals = domain == sp.S.Reals
    stack = [tree]
    while stack:
        item = stack.pop()
        value = build_expression(item)
        if value.has(sp.zoo, sp.oo, -sp.oo, sp.nan):
            return "invalid"
        # Sums and products introduce no holes beyond those of their operands;
        # inspect those operands individually instead of solving their domains twice.
        if item.kind in {"number", "symbol", "unary"} or (
            item.kind == "binary" and item.value in {"+", "-", "*"}
        ):
            stack.extend(item.children)
            continue
        try:
            defined = continuous_domain(value, X, sp.S.Reals)
            if defined == sp.S.EmptySet or (all_reals and defined != sp.S.Reals):
                return "invalid"
            if not all_reals:
                gap = domain - defined
                if gap != sp.S.EmptySet and not isinstance(gap, sp.Complement):
                    return "incorrect"
            for constant in value.free_symbols - {X}:
                if continuous_domain(value, constant, sp.S.Reals) != sp.S.Reals:
                    return "invalid"
        except (NotImplementedError, ValueError, TypeError):
            if all_reals:
                return "inconclusive"
        stack.extend(item.children)
    return None


def evaluated_tree(tree: MathNode) -> Any | None:
    """Return None if any subexpression is undefined before cancellation."""
    stack = [tree]
    while stack:
        item = stack.pop()
        if build_expression(item, evaluate=True).has(sp.zoo, sp.oo, -sp.oo, sp.nan):
            return None
        stack.extend(item.children)
    return build_expression(tree, evaluate=True)


def classify_expression(
    answer: Any, expected: Any, variables: Mapping[str, VariableDomain]
) -> Outcome:
    names = {name: variable_symbol(name, domain) for name, domain in variables.items()}
    if any(symbol.name not in names for symbol in answer.free_symbols):
        return "invalid"
    answer = answer.xreplace({sp.Symbol(name, real=True): symbol for name, symbol in names.items()})
    difference = answer - expected
    if sp.simplify(difference) == 0:
        return "correct"
    samples = [
        _POSITIVE_SAMPLES if domain == "positive" else _REAL_SAMPLES
        for domain in variables.values()
    ]
    for index in range(len(_REAL_SAMPLES)):
        point = {
            symbol: sp.Rational(str(values[(index + 2 * offset) % len(values)]))
            for offset, (symbol, values) in enumerate(zip(names.values(), samples, strict=True))
        }
        value = difference.evalf(_PRECISION, subs=point)
        if value.has(sp.nan, sp.zoo, sp.oo, -sp.oo) or not value.is_number:
            return "incorrect"
        if abs(value) > _TOLERANCE:
            return "incorrect"
    return "inconclusive"
