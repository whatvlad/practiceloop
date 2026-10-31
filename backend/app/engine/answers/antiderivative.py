"""ADR-003 antiderivatives with an explicit arbitrary constant."""

from dataclasses import dataclass
from typing import Any, ClassVar

import sympy as sp

from app.engine.answers._symbolic import (
    X,
    check_domain,
    is_primitive,
    same_number_everywhere,
    trusted_expression,
)
from app.engine.models import Outcome
from app.services.math_parser import MathNode
from app.services.math_worker import _build_sympy


@dataclass(frozen=True, slots=True)
class AntiderivativeAnswer:
    integrand: Any
    primitive: Any
    domain: Any
    kind: ClassVar[str] = "antiderivative"

    def __post_init__(self) -> None:
        object.__setattr__(self, "integrand", trusted_expression(self.integrand))
        object.__setattr__(self, "primitive", trusted_expression(self.primitive))

    def latex(self) -> str:
        return f"{sp.latex(self.primitive)} + C"

    def check(self, tree: MathNode) -> Outcome:
        problem = check_domain(tree, self.domain)
        if problem is not None:
            return problem
        answer = _build_sympy(tree, evaluate=True)
        if answer.has(sp.nan, sp.zoo, sp.oo, -sp.oo):
            return "invalid"
        constants = answer.free_symbols - {X}
        if len(constants) > 1:
            return "invalid"
        primitive = answer
        if constants:
            (constant,) = constants
            slope = sp.simplify(sp.diff(answer, constant))
            if not slope.is_number or slope.is_real is not True or slope.is_zero is not False:
                return "incorrect"
            primitive = answer.subs(constant, 0)
        verdict = is_primitive(primitive, self.integrand, self.domain)
        if verdict == "unknown":
            return "inconclusive"
        if verdict == "no":
            return "incorrect"
        if not constants:
            return "missing_constant"
        offset = same_number_everywhere(primitive - self.primitive, self.domain)
        if offset == "unknown":
            return "inconclusive"
        return "correct" if offset == "yes" else "incorrect"
