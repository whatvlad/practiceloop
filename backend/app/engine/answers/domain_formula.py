"""Univariate formula identity on a family's explicitly stated real domain."""

from dataclasses import dataclass
from typing import Any, ClassVar

import sympy as sp
from sympy.calculus.util import continuous_domain

from app.engine.models import Outcome
from app.math_input import MathNode, build_expression
from app.math_input.contracts import InputContract


@dataclass(frozen=True, slots=True)
class DomainFormulaAnswer:
    expected: Any
    domain: Any
    kind: ClassVar[str] = "formula"
    contract: ClassVar[InputContract] = InputContract("formula", symbols=(("x", "real"),))

    def latex(self) -> str:
        return str(sp.latex(self.expected))

    def check(self, tree: MathNode) -> Outcome:
        x = sp.Symbol("x", real=True)
        try:
            stack = [tree]
            while stack:
                node = stack.pop()
                if node.kind not in {"number", "symbol", "unary", "binary", "function"}:
                    return "invalid"
                if node.kind == "symbol" and node.value not in {"x", "pi", "e"}:
                    return "invalid"
                value = build_expression(node, evaluate=True)
                if value.has(sp.nan, sp.zoo, sp.oo, -sp.oo) or value.is_real is False:
                    return "invalid"
                expressions = [value]
                if node.kind == "binary" and node.value == "/":
                    denominator = build_expression(node.children[1], evaluate=True)
                    if denominator.is_zero is True:
                        return "invalid"
                    expressions.append(sp.Pow(denominator, -1, evaluate=False))
                for expression in expressions:
                    if expression.free_symbols:
                        gap = self.domain - continuous_domain(expression, x, sp.S.Reals)
                        if gap.is_empty is False:
                            return "invalid"
                        if gap != sp.S.EmptySet:
                            return "inconclusive"
                stack.extend(node.children)
            difference = sp.simplify(build_expression(tree, evaluate=True) - self.expected)
            if difference == 0:
                return "correct"
            # A complete exact zero set may prove identity on a restricted branch.
            zeros = sp.solveset(difference, x, domain=self.domain)
            if zeros == self.domain:
                return "correct"
            gap = self.domain - zeros
            if gap.is_empty is False:
                return "incorrect"
            return "inconclusive"
        except (NotImplementedError, TypeError, ValueError):
            return "inconclusive"
