"""ADR-006 expression trees: trusted SymPy in, plain JSON out, plus a float evaluator.

The browser evaluates the same tree with its own evaluator (frontend
src/visual/expression.ts). This module's `evaluate` is its Python twin: it samples
windows on the server and proves in tests that a tree means its SymPy source.
"""

import math
from collections.abc import Callable, Mapping
from typing import Any

import sympy as sp

Tree = float | int | str | list[Any]

NAMES = frozenset({"x", "y", "z", "r", "theta"})
CONSTANTS = {"pi": math.pi, "e": math.e}
# One-argument heads; `add` and `mul` take any number, `pow` exactly two.
_UNARY: dict[type, str] = {
    sp.exp: "exp",
    sp.log: "log",
    sp.sin: "sin",
    sp.cos: "cos",
    sp.tan: "tan",
    sp.Abs: "abs",
}
HEADS = frozenset({"add", "mul", "pow", "sqrt", *_UNARY.values()})


class UnsupportedExpression(ValueError):
    """The expression needs a head ADR-006 does not list; add it on both sides first."""


def to_tree(expr: Any) -> Tree:
    """A JSON tree for a trusted, real SymPy expression built by a generator."""
    expr = sp.sympify(expr)
    if expr is sp.pi:
        return "pi"
    if expr is sp.E:
        return "e"
    if expr.is_Symbol:
        name = str(expr)
        if name not in NAMES:
            raise UnsupportedExpression(f"Unknown name {name}")
        return name
    if expr.is_Number:
        if expr.is_real is not True or not expr.is_finite:
            raise UnsupportedExpression("Numbers must be real and finite")
        # Plotting needs floats; integers stay integers so the JSON stays short.
        return int(expr) if expr.is_Integer else float(expr)
    if expr.is_Add:
        return ["add", *(to_tree(arg) for arg in expr.args)]
    if expr.is_Mul:
        return ["mul", *(to_tree(arg) for arg in expr.args)]
    if expr.is_Pow:
        base, exponent = expr.args
        if exponent == sp.Rational(1, 2):
            return ["sqrt", to_tree(base)]
        if base is sp.E:
            return ["exp", to_tree(exponent)]
        return ["pow", to_tree(base), to_tree(exponent)]
    head = _UNARY.get(type(expr))
    if head is None or len(expr.args) != 1:
        raise UnsupportedExpression(f"Unsupported head {type(expr).__name__}")
    return [head, to_tree(expr.args[0])]


def _pow(base: float, exponent: float) -> float:
    return math.pow(base, exponent)


def _sqrt(value: float) -> float:
    return math.sqrt(value)


def _log(value: float) -> float:
    return math.log(value)


_APPLY: dict[str, Callable[..., float]] = {
    "exp": math.exp,
    "log": _log,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "abs": abs,
    "sqrt": _sqrt,
    "pow": _pow,
}


def evaluate(tree: Tree, env: Mapping[str, float]) -> float:
    """The tree's value; NaN where the browser would leave a gap (outside the domain)."""
    try:
        value = _evaluate(tree, env)
    except (ValueError, OverflowError, ZeroDivisionError):
        return math.nan
    return value if math.isfinite(value) else math.nan


def _evaluate(tree: Tree, env: Mapping[str, float]) -> float:
    if isinstance(tree, bool):
        raise TypeError("Booleans are not numbers")
    if isinstance(tree, int | float):
        return float(tree)
    if isinstance(tree, str):
        if tree in CONSTANTS:
            return CONSTANTS[tree]
        if tree in NAMES:
            return float(env[tree])
        raise TypeError(f"Unknown name {tree}")
    if not isinstance(tree, list) or not tree or tree[0] not in HEADS:
        raise TypeError("Unknown head")
    head, args = tree[0], [_evaluate(arg, env) for arg in tree[1:]]
    if head == "add":
        return math.fsum(args)
    if head == "mul":
        return math.prod(args)
    if (head == "pow") != (len(args) == 2) or (head != "pow" and len(args) != 1):
        raise TypeError("Wrong number of arguments")
    return float(_APPLY[head](*args))
