"""Exact geometric objects over the existing bounded formula/tuple grammars."""

from dataclasses import dataclass
from itertools import permutations
from typing import Any, ClassVar

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer, _expression, combine
from app.engine.models import Outcome
from app.math_input import MathNode
from app.math_input.contracts import InputContract

_LABELS = ("x coordinate", "y coordinate", "z coordinate")


def _vector(value: Any) -> tuple[Any, Any, Any]:
    result = tuple(sp.sympify(x) for x in value)
    if len(result) != 3 or any(x.is_real is not True or x.is_finite is not True for x in result):
        raise ValueError("Expected three finite real coordinates")
    return result


def _tex_vector(value: Any) -> str:
    return r"\left(" + ",".join(sp.latex(x) for x in value) + r"\right)"


def vector_answer(value: Any) -> OrderedAnswer:
    return OrderedAnswer(tuple(FormulaAnswer(x) for x in _vector(value)), _LABELS)


def _affine(tree: MathNode, names: tuple[str, ...]) -> tuple[Any, ...]:
    """Validate before simplification, so cancelled denominators cannot hide holes."""
    symbols = {name: sp.Symbol(name, real=True) for name in names}
    stack = [tree]
    while stack:
        node = stack.pop()
        if node.kind not in {"number", "symbol", "unary", "binary", "function"}:
            raise ValueError("Expected an affine expression")
        if node.kind == "symbol" and node.value not in {*names, "pi", "e"}:
            raise ValueError("Undeclared coordinate")
        value = _expression(node, symbols)
        if node.kind == "binary" and node.value == "/":
            denominator = _expression(node.children[1], symbols)
            if denominator.free_symbols or denominator.is_zero is not False:
                raise ValueError("Only nonzero constant denominators are allowed")
        if node.kind == "function" and value.free_symbols:
            raise ValueError("Coordinate functions must be affine")
        if value.is_real is not True or value.is_finite is not True:
            raise ValueError("Expression is not defined over the entire real parameter space")
        if value.free_symbols and (
            not value.is_polynomial(*symbols.values())
            or sp.Poly(value, *symbols.values()).total_degree() > 1
        ):
            raise ValueError("Expected an affine expression")
        stack.extend(node.children)
    expression = sp.expand(_expression(tree, symbols))
    return (
        *[expression.coeff(symbols[name]) for name in names],
        expression.subs(dict.fromkeys(symbols.values(), 0)),
    )


def _zero_status(values: Any) -> Outcome:
    simplified = [sp.simplify(x) for x in values]
    if all(x == 0 for x in simplified):
        return "correct"
    return "incorrect" if any(x.is_zero is False for x in simplified) else "inconclusive"


@dataclass(frozen=True, slots=True)
class PlaneEquationAnswer:
    normal: Any
    offset: Any
    kind: ClassVar[str] = "formula"

    def __post_init__(self) -> None:
        normal = _vector(self.normal)
        offset = sp.sympify(self.offset)
        if normal == (0, 0, 0) or offset.is_real is not True or offset.is_finite is not True:
            raise ValueError("A plane needs a nonzero finite normal")
        object.__setattr__(self, "normal", normal)
        object.__setattr__(self, "offset", offset)

    @property
    def contract(self) -> InputContract:
        return InputContract("formula", symbols=tuple((name, "real") for name in "xyz"))

    def latex(self) -> str:
        return (
            str(
                sp.latex(
                    sum(c * sp.Symbol(n) for c, n in zip(self.normal, "xyz", strict=True))
                    + self.offset
                )
            )
            + "=0"
        )

    def check(self, tree: MathNode) -> Outcome:
        try:
            candidate = _affine(tree, ("x", "y", "z"))
            if candidate[:3] == (0, 0, 0):
                return "invalid"
            expected = (*self.normal, self.offset)
            pivot = next(i for i, value in enumerate(self.normal) if value != 0)
            factor = candidate[pivot] / expected[pivot]
            return _zero_status(a - factor * b for a, b in zip(candidate, expected, strict=True))
        except (ValueError, TypeError, NotImplementedError):
            return "invalid"


@dataclass(frozen=True, slots=True)
class ParametricGeometryAnswer:
    point: Any
    directions: Any
    kind: ClassVar[str] = "tuple"

    def __post_init__(self) -> None:
        point = _vector(self.point)
        directions = tuple(_vector(v) for v in self.directions)
        if not 1 <= len(directions) <= 2 or sp.Matrix.hstack(
            *(sp.Matrix(v) for v in directions)
        ).rank() != len(directions):
            raise ValueError("An affine line or plane needs an independent basis")
        object.__setattr__(self, "point", point)
        object.__setattr__(self, "directions", directions)

    @property
    def parameters(self) -> tuple[str, ...]:
        return ("t",) if len(self.directions) == 1 else ("s", "t")

    @property
    def contract(self) -> InputContract:
        expression = InputContract(
            "formula", symbols=tuple((name, "real") for name in self.parameters)
        )
        return InputContract("tuple", components=(expression,) * 3, labels=_LABELS)

    def latex(self) -> str:
        return (
            "(x,y,z)="
            + _tex_vector(self.point)
            + "".join(
                "+" + name + _tex_vector(v)
                for name, v in zip(self.parameters, self.directions, strict=True)
            )
        )

    def check(self, tree: MathNode) -> Outcome:
        if tree.kind != "tuple" or len(tree.children) != 3:
            return "invalid"
        try:
            rows = [_affine(child, self.parameters) for child in tree.children]
            candidate = sp.Matrix([row[:-1] for row in rows])
            expected = sp.Matrix.hstack(*(sp.Matrix(v) for v in self.directions))
            dimension = len(self.directions)
            if candidate.rank() != dimension or expected.row_join(candidate).rank() != dimension:
                return "incorrect"
            difference = sp.Matrix([row[-1] for row in rows]) - sp.Matrix(self.point)
            return "correct" if expected.row_join(difference).rank() == dimension else "incorrect"
        except (ValueError, TypeError, NotImplementedError):
            return "invalid"


@dataclass(frozen=True, slots=True)
class VectorSetAnswer:
    vectors: Any
    kind: ClassVar[str] = "tuple"

    def __post_init__(self) -> None:
        vectors = tuple(_vector(v) for v in self.vectors)
        if not 1 <= len(vectors) <= 2 or len(set(vectors)) != len(vectors):
            raise ValueError("Expected one or two distinct complete solutions")
        object.__setattr__(self, "vectors", vectors)

    @property
    def contract(self) -> InputContract:
        return InputContract(
            "tuple",
            components=tuple(vector_answer(v).contract for v in self.vectors),
            labels=("Vector one", "Vector two")[: len(self.vectors)],
        )

    def latex(self) -> str:
        return r"\left\{" + ",".join(_tex_vector(v) for v in self.vectors) + r"\right\}"

    def check(self, tree: MathNode) -> Outcome:
        if tree.kind != "tuple" or len(tree.children) != len(self.vectors):
            return "invalid"
        outcomes = [
            combine(
                tuple(
                    vector_answer(v).check(child)
                    for v, child in zip(order, tree.children, strict=True)
                )
            )
            for order in permutations(self.vectors)
        ]
        return "correct" if "correct" in outcomes else combine(tuple(outcomes))
