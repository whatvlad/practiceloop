"""Expression answers whose declared domain is the entire real x axis."""

import sympy as sp

from app.engine.answers._symbolic import check_domain
from app.engine.answers.expression import ExpressionAnswer
from app.engine.models import Outcome
from app.math_input import MathNode


class FullRealExpressionAnswer(ExpressionAnswer):
    """Keep the expression kind; reject holes before algebraic cancellation."""

    __slots__ = ()

    def __post_init__(self) -> None:
        if dict(self.variables) != {"x": "real"}:
            raise ValueError("This answer policy requires exactly real x")
        super().__post_init__()

    def check(self, tree: MathNode) -> Outcome:
        problem = check_domain(tree, sp.S.Reals)
        return problem if problem is not None else super().check(tree)


class ConstantExpressionAnswer(ExpressionAnswer):
    """A scalar answer cannot introduce a variable and cancel it afterwards."""

    __slots__ = ()

    def __post_init__(self) -> None:
        if self.variables:
            raise ValueError("A constant answer has no variables")
        super().__post_init__()

    def check(self, tree: MathNode) -> Outcome:
        stack = [tree]
        while stack:
            node = stack.pop()
            if node.kind == "symbol" and node.value not in {"pi", "e"}:
                return "invalid"
            stack.extend(node.children)
        return super().check(tree)
