"""Exact boolean, finite real set and single real interval answer policies."""

from dataclasses import dataclass
from typing import Any, ClassVar

import sympy as sp

from app.engine.answers._symbolic import classify_expression, evaluated_tree
from app.engine.answers.real_function import ConstantExpressionAnswer
from app.engine.models import Outcome
from app.math_input import MathNode, build_expression


class _Invalid(ValueError):
    pass


class _Unknown(ValueError):
    pass


def _scalar(tree: MathNode) -> Any:
    stack = [tree]
    while stack:
        node = stack.pop()
        if node.kind not in {"number", "symbol", "unary", "binary", "function"}:
            raise _Invalid
        if node.kind == "symbol" and node.value not in {"pi", "e"}:
            raise _Invalid
        subexpression = build_expression(node, evaluate=True)
        if subexpression.is_real is False or subexpression.has(sp.nan, sp.zoo, sp.oo, -sp.oo):
            raise _Invalid
        if subexpression.is_real is not True or subexpression.is_finite is not True:
            raise _Unknown
        stack.extend(node.children)
    value = evaluated_tree(tree)
    if value is None or value.is_real is False or value.is_finite is False:
        raise _Invalid
    if value.is_real is not True or value.is_finite is not True:
        raise _Unknown
    return value


def _trusted(value: Any) -> Any:
    value = sp.sympify(value)  # trusted constructor data, never learner text
    if value.is_real is not True or value.is_finite is not True:
        raise ValueError("Expected a finite real scalar")
    return value


class RealScalarAnswer(ConstantExpressionAnswer):
    """New real-only scalar consumers reject nonreal intermediate expressions."""

    __slots__ = ()

    def check(self, tree: MathNode) -> Outcome:
        try:
            _scalar(tree)
        except _Invalid:
            return "invalid"
        except _Unknown:
            return "inconclusive"
        return super().check(tree)


@dataclass(frozen=True, slots=True)
class BooleanAnswer:
    expected: bool
    kind: ClassVar[str] = "boolean"

    def __post_init__(self) -> None:
        if type(self.expected) is not bool:
            raise ValueError("Expected a boolean")

    def latex(self) -> str:
        return r"\text{Yes}" if self.expected else r"\text{No}"

    def check(self, tree: MathNode) -> Outcome:
        if tree.kind != "boolean" or tree.value not in {"true", "false"} or tree.children:
            return "invalid"
        return "correct" if (tree.value == "true") == self.expected else "incorrect"


@dataclass(frozen=True, slots=True)
class FiniteSetAnswer:
    expected: tuple[Any, ...]
    kind: ClassVar[str] = "finite_set"

    def __post_init__(self) -> None:
        if len(self.expected) > 8:
            raise ValueError("Finite support exceeds eight values")
        for value in self.expected:
            _trusted(value)
        if len(sp.FiniteSet(*self.expected)) != len(self.expected):
            raise ValueError("Expected support must be distinct")

    def latex(self) -> str:
        return str(sp.latex(sp.FiniteSet(*self.expected)))

    def check(self, tree: MathNode) -> Outcome:
        if tree.kind != "finite_set" or len(tree.children) > 8:
            return "invalid"
        try:
            candidates: list[Any] = []
            for child in tree.children:
                value = _scalar(child)
                comparisons = [classify_expression(value, other, {}) for other in candidates]
                if "correct" in comparisons:
                    continue
                if "inconclusive" in comparisons:
                    raise _Unknown
                candidates.append(value)
        except _Invalid:
            return "invalid"
        except _Unknown:
            return "inconclusive"
        if len(candidates) != len(self.expected):
            return "incorrect"
        unknown = False
        for value in candidates:
            comparisons = [
                classify_expression(value, _trusted(other), {}) for other in self.expected
            ]
            if "correct" not in comparisons:
                if "inconclusive" not in comparisons:
                    return "incorrect"
                unknown = True
        return "inconclusive" if unknown else "correct"


@dataclass(frozen=True, slots=True)
class IntervalAnswer:
    lower: Any
    upper: Any
    left_open: bool = False
    right_open: bool = False
    kind: ClassVar[str] = "interval"

    def __post_init__(self) -> None:
        if type(self.left_open) is not bool or type(self.right_open) is not bool:
            raise ValueError("Closure flags must be booleans")
        if self.lower != -sp.oo:
            _trusted(self.lower)
        elif not self.left_open:
            raise ValueError("Infinity is open")
        if self.upper != sp.oo:
            _trusted(self.upper)
        elif not self.right_open:
            raise ValueError("Infinity is open")
        if not bool(self.lower < self.upper) and not (
            self.lower == self.upper and not self.left_open and not self.right_open
        ):
            raise ValueError("Expected a nonempty interval")

    def latex(self) -> str:
        if self.lower == self.upper:
            return rf"\left[{sp.latex(self.lower)},{sp.latex(self.upper)}\right]"
        return str(sp.latex(sp.Interval(self.lower, self.upper, self.left_open, self.right_open)))

    def check(self, tree: MathNode) -> Outcome:
        if (
            tree.kind != "interval"
            or tree.value not in {"[]", "[)", "(]", "()"}
            or len(tree.children) != 2
        ):
            return "invalid"
        try:
            values = [
                -sp.oo
                if node.value == "-inf"
                else sp.oo
                if node.kind == "endpoint"
                else _scalar(node)
                for node in tree.children
            ]
            lower, upper = values
            if lower == sp.oo or upper == -sp.oo:
                return "invalid"
            width = sp.simplify(upper - lower)
            singleton = width.is_zero is True and tree.value == "[]"
            if width.is_extended_positive is False and not singleton:
                return "invalid"
            if width.is_extended_positive is not True and not singleton:
                raise _Unknown
        except _Invalid:
            return "invalid"
        except _Unknown:
            return "inconclusive"
        closure = ("(" if self.left_open else "[") + (")" if self.right_open else "]")
        if tree.value != closure:
            return "incorrect"
        outcomes = []
        for candidate, expected in zip(values, (self.lower, self.upper), strict=True):
            if candidate in {-sp.oo, sp.oo} or expected in {-sp.oo, sp.oo}:
                outcomes.append("correct" if candidate == expected else "incorrect")
            else:
                outcomes.append(classify_expression(candidate, _trusted(expected), {}))
        return (
            "incorrect"
            if "incorrect" in outcomes
            else "inconclusive"
            if "inconclusive" in outcomes
            else "correct"
        )
