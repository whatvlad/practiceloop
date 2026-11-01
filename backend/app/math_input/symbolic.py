"""Public safe SymPy construction from an already validated MathNode, never strings."""

from typing import Any, cast

from app.math_input.parser import MathNode


def build_expression(node: MathNode, evaluate: bool = False) -> Any:
    # Import after child resource limits are active; never parse learner strings in SymPy.
    import sympy as sp

    if node.kind == "number":
        numerator, denominator = cast(tuple[int, int], node.value)
        return sp.Rational(numerator, denominator)
    if node.kind == "symbol":
        if node.value == "pi":
            return sp.pi
        if node.value == "e":
            return sp.E
        return sp.Symbol(node.value, real=True)
    if node.kind == "unary":
        child = build_expression(node.children[0], evaluate)
        return child if node.value == "+" else sp.Mul(sp.Integer(-1), child, evaluate=evaluate)
    if node.kind == "function":
        functions = {
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "sec": sp.sec,
            "csc": sp.csc,
            "cot": sp.cot,
            "asin": sp.asin,
            "acos": sp.acos,
            "atan": sp.atan,
            "exp": sp.exp,
            "ln": sp.log,
            "log": sp.log,
            "sqrt": sp.sqrt,
            "abs": sp.Abs,
        }
        return functions[cast(str, node.value)](
            build_expression(node.children[0], evaluate), evaluate=evaluate
        )
    left = build_expression(node.children[0], evaluate)
    right = build_expression(node.children[1], evaluate)
    if node.value == "+":
        return sp.Add(left, right, evaluate=evaluate)
    if node.value == "-":
        return sp.Add(left, sp.Mul(sp.Integer(-1), right, evaluate=evaluate), evaluate=evaluate)
    if node.value == "*":
        return sp.Mul(left, right, evaluate=evaluate)
    if node.value == "/":
        return sp.Mul(left, sp.Pow(right, sp.Integer(-1), evaluate=evaluate), evaluate=evaluate)
    return sp.Pow(left, right, evaluate=evaluate)
