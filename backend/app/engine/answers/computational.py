"""Exact opt-in answer policies; original shipped policies remain unchanged."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, ClassVar, Protocol

import sympy as sp
from sympy.calculus.util import continuous_domain

from app.engine.answers.structured import _Invalid, _scalar, _Unknown
from app.engine.models import Outcome
from app.math_input import MathNode, build_expression
from app.math_input.contracts import Domain, InputContract


class ComputationalAnswer(Protocol):
    @property
    def contract(self) -> InputContract: ...

    def latex(self) -> str: ...

    def check(self, tree: MathNode) -> Outcome: ...


def combine(outcomes: tuple[Outcome, ...]) -> Outcome:
    # A malformed component is invalid even when another component is wrong.
    for outcome in ("invalid", "inconclusive", "missing_constant", "incorrect"):
        if outcome in outcomes:
            return outcome
    return "correct"


@dataclass(frozen=True, slots=True)
class CategoryAnswer:
    expected: str
    choices: tuple[str, ...]
    kind: ClassVar[str] = "category"

    def __post_init__(self) -> None:
        _ = self.contract
        if self.expected not in self.choices:
            raise ValueError("Expected category is not a choice")

    @property
    def contract(self) -> InputContract:
        return InputContract(self.kind, choices=self.choices)

    def latex(self) -> str:
        return r"\text{" + self.expected.replace("_", " ") + "}"

    def check(self, tree: MathNode) -> Outcome:
        if tree.kind != "category" or tree.children or tree.value not in self.choices:
            return "invalid"
        return "correct" if tree.value == self.expected else "incorrect"


@dataclass(frozen=True, slots=True)
class LimitAnswer:
    expected: Any
    kind: ClassVar[str] = "limit_result"
    contract: ClassVar[InputContract] = InputContract("limit_result")

    def __post_init__(self) -> None:
        if self.expected not in {sp.oo, -sp.oo, "does_not_exist"}:
            from app.engine.answers.structured import _trusted

            _trusted(self.expected)

    def latex(self) -> str:
        return (
            r"\text{does not exist}"
            if self.expected == "does_not_exist"
            else str(sp.latex(self.expected))
        )

    def check(self, tree: MathNode) -> Outcome:
        states = {sp.oo: "inf", -sp.oo: "-inf", "does_not_exist": "does_not_exist"}
        if tree.kind == "category":
            if tree.children or tree.value not in states.values():
                return "invalid"
            return "correct" if states.get(self.expected) == tree.value else "incorrect"
        try:
            candidate = _scalar(tree)
        except _Invalid:
            return "invalid"
        except _Unknown:
            return "inconclusive"
        if self.expected in states:
            return "incorrect"
        difference = sp.simplify(candidate - self.expected)
        if difference == 0:
            return "correct"
        return "incorrect" if difference.is_zero is False else "inconclusive"


@dataclass(frozen=True, slots=True)
class PeriodicSetAnswer:
    """Canonical base-cell real set and a fixed declared positive period.

    New families explicitly require this canonical period in their prompt.
    Arbitrary equivalent-period rescaling and free-form set builders are not
    guessed; mathematical delivery owns normalization to this representation.
    """

    period: Any
    base: Any
    kind: ClassVar[str] = "tuple"

    def __post_init__(self) -> None:
        period = sp.sympify(self.period)
        if period.is_positive is not True or period.free_symbols:
            raise ValueError("Period must be a positive exact constant")
        _validate_set(self.base)
        if self.base - sp.Interval.Ropen(0, period) != sp.S.EmptySet:
            raise ValueError("Base set must lie in the canonical half-open period cell")
        object.__setattr__(self, "period", period)

    @property
    def contract(self) -> InputContract:
        return InputContract(
            "tuple",
            components=(InputContract("formula"), InputContract("real_set")),
            labels=("Period", "Base set"),
        )

    def latex(self) -> str:
        return (
            str(sp.latex(self.base)) + r"+" + str(sp.latex(self.period)) + r"k,\quad k\in\mathbb{Z}"
        )

    def check(self, tree: MathNode) -> Outcome:
        if tree.kind != "tuple" or len(tree.children) != 2:
            return "invalid"
        return combine(
            (
                FormulaAnswer(self.period).check(tree.children[0]),
                RealSetAnswer(self.base).check(tree.children[1]),
            )
        )


@dataclass(frozen=True, slots=True)
class RealSetAnswer:
    expected: Any
    kind: ClassVar[str] = "real_set"
    contract: ClassVar[InputContract] = InputContract("real_set")

    def __post_init__(self) -> None:
        _validate_set(self.expected)

    def latex(self) -> str:
        return str(sp.latex(self.expected))

    def check(self, tree: MathNode) -> Outcome:
        try:
            candidate = _set(tree)
            difference = sp.SymmetricDifference(candidate, self.expected)
            if difference == sp.S.EmptySet:
                return "correct"
            if difference.is_empty is False:
                return "incorrect"
            return "inconclusive"
        except _Invalid:
            return "invalid"
        except (_Unknown, NotImplementedError, TypeError, ValueError):
            return "inconclusive"


def _validate_set(value: Any) -> None:
    if value in (sp.S.Reals, sp.S.EmptySet):
        return
    pieces = value.args if isinstance(value, sp.Union) else (value,)
    if len(pieces) > 8:
        raise ValueError("Too many trusted set pieces")
    for part in pieces:
        if isinstance(part, sp.Interval):
            values = (part.start, part.end)
        elif isinstance(part, sp.FiniteSet) and len(part) <= 8:
            values = tuple(part)
        else:
            raise ValueError("Expected a finite union of real intervals and points")
        if any(
            v.free_symbols
            or (v.is_real is not True and v not in {-sp.oo, sp.oo})
            or (v in {-sp.oo, sp.oo} and not isinstance(part, sp.Interval))
            for v in values
        ):
            raise ValueError("Set endpoints must be real constants")


def _set(tree: MathNode) -> Any:
    if tree.kind != "real_set":
        raise _Invalid
    if tree.value == "real" and not tree.children:
        return sp.S.Reals
    if tree.value == "excluded" and len(tree.children) == 1:
        return sp.S.Reals - _piece(tree.children[0])
    if tree.value == "union" and 1 <= len(tree.children) <= 8:
        return sp.Union(*(_piece(child) for child in tree.children))
    raise _Invalid


def _piece(tree: MathNode) -> Any:
    if tree.kind == "finite_set" and len(tree.children) <= 8:
        return sp.FiniteSet(*(_scalar(child) for child in tree.children))
    if (
        tree.kind != "interval"
        or len(tree.children) != 2
        or tree.value not in {"[]", "[)", "(]", "()"}
    ):
        raise _Invalid
    lo, hi = (
        -sp.oo
        if child.kind == "endpoint" and child.value == "-inf"
        else sp.oo
        if child.kind == "endpoint" and child.value == "inf"
        else _scalar(child)
        for child in tree.children
    )
    closure = str(tree.value)
    if (
        lo == sp.oo
        or hi == -sp.oo
        or (lo == -sp.oo and closure[0] != "(")
        or (hi == sp.oo and closure[1] != ")")
    ):
        raise _Invalid
    width = hi - lo
    if width.is_extended_positive is not True:
        if width.is_zero is True and closure == "[]":
            return sp.FiniteSet(lo)
        if width.is_extended_positive is False:
            raise _Invalid
        raise _Unknown
    return sp.Interval(lo, hi, closure[0] == "(", closure[1] == ")")


@dataclass(frozen=True, slots=True)
class OrderedAnswer:
    components: tuple[ComputationalAnswer, ...]
    labels: tuple[str, ...]
    kind: ClassVar[str] = "tuple"

    def __post_init__(self) -> None:
        _ = self.contract

    @property
    def contract(self) -> InputContract:
        return InputContract(
            self.kind, components=tuple(c.contract for c in self.components), labels=self.labels
        )

    def latex(self) -> str:
        return r"\left(" + r",\;".join(c.latex() for c in self.components) + r"\right)"

    def check(self, tree: MathNode) -> Outcome:
        if tree.kind != "tuple" or len(tree.children) != len(self.components):
            return "invalid"
        return combine(
            tuple(
                answer.check(child)
                for answer, child in zip(self.components, tree.children, strict=True)
            )
        )


@dataclass(frozen=True, slots=True)
class FormulaAnswer:
    """Exact identity over a declared Cartesian product of real symbol domains.

    Family-specific nonrectangular domains/ODE completeness need their own
    answer policy, composing this grammar rather than weakening this check.
    """

    expected: Any
    symbols: tuple[tuple[str, Domain], ...] = ()
    kind: ClassVar[str] = "formula"

    def __post_init__(self) -> None:
        _ = self.contract
        value = sp.sympify(self.expected)  # trusted construction only
        if any(s.name not in dict(self.symbols) for s in value.free_symbols):
            raise ValueError("Expected expression contains an undeclared symbol")
        object.__setattr__(self, "expected", value)

    @property
    def contract(self) -> InputContract:
        return InputContract(self.kind, symbols=self.symbols)

    def latex(self) -> str:
        return str(sp.latex(self.expected))

    def check(self, tree: MathNode) -> Outcome:
        symbols = {
            name: sp.Symbol(
                name,
                **{"integer": True}
                if domain == "integer"
                else {"positive": True}
                if domain == "positive"
                else {"real": True},
            )
            for name, domain in self.symbols
        }
        try:
            stack = [tree]
            while stack:
                node = stack.pop()
                if node.kind not in {"number", "symbol", "unary", "binary", "function"}:
                    return "invalid"
                if node.kind == "symbol" and node.value not in {*symbols, "pi", "e"}:
                    return "invalid"
                value = _expression(node, symbols)
                if node.kind == "binary" and node.value == "/":
                    denominator = _expression(node.children[1], symbols)
                    if denominator.is_zero is True:
                        return "invalid"
                    if denominator.is_nonzero is not True:
                        outcome = _domain(sp.Pow(denominator, -1, evaluate=False), symbols)
                        if outcome is not None:
                            return outcome
                if value.has(sp.nan, sp.zoo, sp.oo, -sp.oo) or value.is_real is False:
                    return "invalid"
                if value.is_real is not True or value.is_finite is not True:
                    outcome = _domain(value, symbols)
                    if outcome is not None:
                        return outcome
                stack.extend(node.children)
            candidate = _expression(tree, symbols)
            expected = self.expected.xreplace(
                {s: symbols[s.name] for s in self.expected.free_symbols}
            )
            difference = sp.simplify(candidate - expected)
            if difference == 0:
                return "correct"
            # Exact nonzero constants/polynomials certify difference. Sampling
            # never certifies equality; undecided identities stay inconclusive.
            if difference.is_zero is False or (
                difference.is_polynomial(*symbols.values())
                and sp.Poly(difference, *symbols.values()).is_zero is False
            ):
                return "incorrect"
            for index in range(3):
                point = {
                    symbol: sp.Integer(index + 1 if symbol.is_positive else index)
                    for symbol in symbols.values()
                }
                witness = difference.subs(point)
                if witness.is_finite is True and witness.is_zero is False:
                    return "incorrect"
            return "inconclusive"
        except (NotImplementedError, TypeError, ValueError):
            return "inconclusive"


def _expression(tree: MathNode, symbols: Mapping[str, Any]) -> Any:
    value = build_expression(tree, evaluate=True)
    return value.xreplace({s: symbols[s.name] for s in value.free_symbols if s.name in symbols})


def _domain(value: Any, symbols: Mapping[str, Any]) -> Outcome | None:
    if not value.free_symbols:
        return "inconclusive"
    for symbol in value.free_symbols:
        domain = (
            sp.S.Integers
            if symbol.is_integer
            else (sp.Interval.open(0, sp.oo) if symbol.is_positive else sp.S.Reals)
        )
        defined = continuous_domain(value, symbol, sp.S.Reals)
        gap = domain - defined
        if gap.is_empty is False:
            return "invalid"
        if gap != sp.S.EmptySet:
            return "inconclusive"
    return None
