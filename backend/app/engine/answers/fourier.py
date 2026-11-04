"""Exact bounded cosine linearization; the requested representation is checked too."""

from dataclasses import dataclass
from typing import Any

import sympy as sp

from app.engine.answers.computational import FormulaAnswer
from app.engine.models import Outcome
from app.math_input import MathNode, build_expression


@dataclass(frozen=True, slots=True)
class FourierAnswer(FormulaAnswer):
    frequencies: tuple[int, ...] = ()

    def check(self, tree: MathNode) -> Outcome:
        x = sp.Symbol("x", real=True)
        harmonics = {sp.cos(k * x): sp.Dummy(f"h{k}", real=True) for k in self.frequencies}
        try:
            value: Any = sp.expand(build_expression(tree, evaluate=True)).xreplace(harmonics)
            variables = tuple(harmonics.values())
            if value.free_symbols - set(variables):
                return "invalid"
            if not value.is_polynomial(*variables):
                return "invalid"
            if sp.Poly(value, *variables).total_degree() > 1:
                return "invalid"
        except (ValueError, TypeError, NotImplementedError):
            return "invalid"
        return super(FourierAnswer, self).check(tree)
