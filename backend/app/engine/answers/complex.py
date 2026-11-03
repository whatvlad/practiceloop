"""#221: exact complex-number answers in algebraic form a + bi."""

from dataclasses import dataclass
from typing import Any, ClassVar

import sympy as sp

from app.engine.answers._symbolic import evaluated_tree, trusted_expression
from app.engine.models import Outcome
from app.math_input import MathNode, build_expression

_PRECISION = 50
_TOLERANCE = sp.Float("1e-30", _PRECISION)
# The complex grammar declares only `i`, so `x` stands in for it while the form is checked.
_UNIT = sp.Symbol("x", real=True)


def _unit_as_x(node: MathNode) -> MathNode:
    if node.kind == "symbol" and node.value == "i":
        return MathNode("symbol", "x")
    return MathNode(node.kind, node.value, tuple(_unit_as_x(child) for child in node.children))


def algebraic_form(tree: MathNode) -> bool:
    """True when the answer is a + b*i with i neither multiplied by itself nor divided by."""
    expression = sp.expand(build_expression(_unit_as_x(tree), evaluate=True))
    return bool(expression.is_polynomial(_UNIT)) and sp.degree(expression, _UNIT) <= 1


@dataclass(frozen=True, slots=True)
class ComplexAnswer:
    expected: Any
    kind: ClassVar[str] = "complex"

    def __post_init__(self) -> None:
        expected = sp.expand(trusted_expression(self.expected))
        if expected.free_symbols or not expected.is_number:
            raise ValueError("A complex answer is a constant")
        object.__setattr__(self, "expected", expected)

    def latex(self) -> str:
        return str(sp.latex(self.expected))

    def check(self, tree: MathNode) -> Outcome:
        answer = evaluated_tree(tree)
        if answer is None or answer.free_symbols:
            return "invalid"
        difference = answer - self.expected
        value = sp.N(difference, _PRECISION)
        if value.has(sp.nan, sp.zoo, sp.oo, -sp.oo) or not value.is_number:
            return "invalid"
        if abs(value) > _TOLERANCE:
            return "incorrect"
        if sp.simplify(sp.expand_complex(difference)) != 0:
            return "inconclusive"
        # A power or quotient of the question is equal but is not yet a + bi.
        return "correct" if algebraic_form(tree) else "incorrect"
