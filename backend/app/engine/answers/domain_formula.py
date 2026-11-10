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
                        if gap.is_empty is None and isinstance(self.domain, sp.Interval):
                            # Periodic poles (cot, 1/sin^2) leave an undecided complement
                            # over R; restricting to the stated interval decides it.
                            gap = self.domain - continuous_domain(expression, x, self.domain)
                        if gap.is_empty is False:
                            return "invalid"
                        if gap != sp.S.EmptySet:
                            return "inconclusive"
                stack.extend(node.children)
            candidate = build_expression(tree, evaluate=True)
            if _differs_at_a_sample(candidate - self.expected, x, self.domain):
                return "incorrect"
            if not candidate.free_symbols and self.domain.interior.is_empty is False:
                # Identity with a constant would force the target's derivative
                # to vanish throughout the domain's interior. Certify a point
                # where that trusted derivative exists and is nonzero instead
                # of solving e.g. log(x)/log(4)+1 = 999999 (a huge integer root).
                # Finite/empty domains and undecided derivative sets fall through.
                try:
                    derivative = sp.diff(self.expected, x)
                    defined = continuous_domain(derivative, x, self.domain.interior)
                    zeros = sp.solveset(derivative, x, domain=defined)
                    if (defined - zeros).is_empty is False:
                        return "incorrect"
                except (NotImplementedError, TypeError, ValueError):
                    pass
            # Even simplification can combine logarithms into a huge exponential
            # constant, so the trusted derivative certificate must precede it.
            difference = sp.simplify(candidate - self.expected)
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


def _sample_points(domain: sp.Set) -> list[sp.Rational]:
    """A few rational points inside each interval component of the domain."""
    if domain == sp.S.Reals:
        domain = sp.Interval(-sp.oo, sp.oo)
    parts = domain.args if isinstance(domain, sp.Union) else (domain,)

    def rational(value: sp.Expr) -> sp.Rational:
        return sp.Rational(str(sp.N(value, 15)))

    points: list[sp.Rational] = []
    for part in parts:
        if not isinstance(part, sp.Interval):
            continue
        low, high = part.start, part.end
        if low.is_finite and high.is_finite:
            points.extend(rational(low + (high - low) * sp.Rational(k, 6)) for k in (1, 3, 5))
        elif low.is_finite:
            points.extend(rational(low) + d for d in (sp.Rational(1, 3), 2))
        elif high.is_finite:
            points.extend(rational(high) - d for d in (sp.Rational(1, 3), 2))
        else:
            points.extend((sp.Rational(-7, 3), sp.Rational(2, 7), sp.Rational(13, 5)))
    return [p for p in points if domain.contains(p) is sp.true][:8]


def _differs_at_a_sample(difference: sp.Expr, x: sp.Symbol, domain: sp.Set) -> bool:
    """Certify a non-identity numerically at an interior point; equality is never sampled."""
    for point in _sample_points(domain):
        value = sp.N(difference.subs(x, point), 30)
        if value.is_real and value.is_finite and abs(value) > sp.Float("1e-12"):
            return True
    return False
