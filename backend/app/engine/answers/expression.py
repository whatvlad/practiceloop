"""ADR-005 expression answers over declared variables."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, ClassVar

import sympy as sp

from app.engine.answers._symbolic import classify_expression, evaluated_tree, trusted_expression
from app.engine.models import Outcome
from app.services.math_parser import MathNode, VariableDomain, declared_variables


@dataclass(frozen=True, slots=True)
class ExpressionAnswer:
    expected: Any
    variables: Mapping[str, VariableDomain]
    kind: ClassVar[str] = "expression"

    def __post_init__(self) -> None:
        if self.variables:
            declared_variables(dict(self.variables))
        object.__setattr__(self, "expected", trusted_expression(self.expected))

    def latex(self) -> str:
        return str(sp.latex(self.expected))

    def check(self, tree: MathNode) -> Outcome:
        answer = evaluated_tree(tree)
        if answer is None:
            return "invalid"
        return classify_expression(answer, self.expected, self.variables)
