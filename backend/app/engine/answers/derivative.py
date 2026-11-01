"""ADR-005 derivatives, equal on every declared domain component."""

from dataclasses import dataclass
from typing import Any, ClassVar

import sympy as sp

from app.engine.answers._symbolic import X, check_domain, components, differs, trusted_expression
from app.engine.models import Outcome
from app.services.math_parser import MathNode
from app.services.math_worker import _build_sympy


@dataclass(frozen=True, slots=True)
class DerivativeAnswer:
    expected: Any
    domain: Any
    kind: ClassVar[str] = "derivative"

    def __post_init__(self) -> None:
        object.__setattr__(self, "expected", trusted_expression(self.expected))

    def latex(self) -> str:
        return str(sp.latex(self.expected))

    def check(self, tree: MathNode) -> Outcome:
        problem = check_domain(tree, self.domain)
        if problem is not None:
            return problem
        answer = _build_sympy(tree, evaluate=True)
        if answer.has(sp.nan, sp.zoo, sp.oo, -sp.oo):
            return "invalid"
        if answer.free_symbols - {X}:
            return "incorrect"
        undecided = False
        for replacement, variable, samples in components(self.domain):
            difference = answer.subs(X, replacement) - self.expected.subs(X, replacement)
            if sp.simplify(difference) == 0:
                continue
            if differs(difference, variable, samples):
                return "incorrect"
            undecided = True
        return "inconclusive" if undecided else "correct"
