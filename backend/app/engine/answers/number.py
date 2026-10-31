"""Exact rational answer checking without symbolic simplification."""

from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
from typing import ClassVar, cast

from app.engine.models import Outcome
from app.services.math_parser import MathNode

_MAX_BITS = 4096


class _Unsupported(ValueError):
    pass


class _Invalid(ValueError):
    pass


class _NonReal(ValueError):
    pass


def _bounded(value: Fraction) -> Fraction:
    if value.numerator.bit_length() > _MAX_BITS or value.denominator.bit_length() > _MAX_BITS:
        raise _Unsupported
    return value


def _fraction(node: MathNode) -> Fraction:
    if node.kind == "number":
        numerator, denominator = cast(tuple[int, int], node.value)
        return Fraction(numerator, denominator)
    if node.kind == "symbol":
        raise _Unsupported
    if node.kind == "unary":
        child = _fraction(node.children[0])
        return child if node.value == "+" else -child
    if node.kind == "function":
        child = _fraction(node.children[0])
        if node.value == "abs":
            return abs(child)
        if node.value == "sqrt":
            if child < 0:
                raise _NonReal
            numerator, denominator = isqrt(child.numerator), isqrt(child.denominator)
            if numerator**2 == child.numerator and denominator**2 == child.denominator:
                return Fraction(numerator, denominator)
        if node.value in {"ln", "log"}:
            if child == 0:
                raise _Invalid
            if child < 0:
                raise _NonReal
        raise _Unsupported
    values: list[Fraction] = []
    unsupported = False
    nonreal = False
    for child_node in node.children:
        try:
            values.append(_fraction(child_node))
        except _Unsupported:
            unsupported = True
        except _NonReal:
            nonreal = True
    if unsupported:
        raise _Unsupported
    if nonreal:
        raise _NonReal
    left, right = values
    if node.value == "+":
        return _bounded(left + right)
    if node.value == "-":
        return _bounded(left - right)
    if node.value == "*":
        return _bounded(left * right)
    if node.value == "/":
        if right == 0:
            raise _Invalid
        return _bounded(left / right)
    if right.denominator != 1:
        raise _Unsupported
    exponent = right.numerator
    if left == 0 and exponent < 0:
        raise _Invalid
    if abs(exponent) * max(left.numerator.bit_length(), left.denominator.bit_length()) > _MAX_BITS:
        raise _Unsupported
    return _bounded(left**exponent)


@dataclass(frozen=True, slots=True)
class NumberAnswer:
    expected: Fraction | int
    kind: ClassVar[str] = "number"

    def __post_init__(self) -> None:
        if not isinstance(self.expected, (int, Fraction)) or isinstance(self.expected, bool):
            raise ValueError("Expected value must be an exact integer or fraction")

    def latex(self) -> str:
        value = Fraction(self.expected)
        if value.denominator == 1:
            return str(value.numerator)
        sign = "-" if value < 0 else ""
        return rf"{sign}\frac{{{abs(value.numerator)}}}{{{value.denominator}}}"

    def check(self, tree: MathNode) -> Outcome:
        try:
            candidate = _fraction(tree)
        except _Invalid:
            return "invalid"
        except _NonReal:
            return "incorrect"
        except _Unsupported:
            return "inconclusive"
        return "correct" if candidate == self.expected else "incorrect"
