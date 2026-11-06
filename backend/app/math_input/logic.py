"""Bounded propositional grammar. No symbolic string parser or learner eval."""

import re

from app.math_input.parser import MAX_NESTING, MAX_NODES, MathInputError, MathNode


def parse_logic(text: str, atoms: tuple[str, ...]) -> MathNode:
    tokens = re.findall(r"<->|->|[!&|^()pqr01]|\S", text)
    index = nodes = 0
    precedence = {"<->": 1, "->": 2, "|": 3, "^": 3, "&": 4}

    def node(op: str, *children: MathNode) -> MathNode:
        nonlocal nodes
        nodes += 1
        if nodes > MAX_NODES:
            raise MathInputError("Logic exceeds the shared node budget")
        return MathNode("logic", op, children)

    def expression(minimum: int, depth: int) -> MathNode:
        nonlocal index
        if depth > MAX_NESTING or index >= len(tokens):
            raise MathInputError("Incomplete or excessively nested logical expression")
        lexeme = tokens[index]
        index += 1
        if lexeme == "!":
            left = node("!", expression(5, depth + 1))
        elif lexeme == "(":
            left = expression(1, depth + 1)
            if index >= len(tokens) or tokens[index] != ")":
                raise MathInputError("Unbalanced logical parentheses")
            index += 1
        elif lexeme in atoms or lexeme in {"0", "1"}:
            left = node(lexeme)
        else:
            raise MathInputError("Use declared atoms, 0, 1 and ! & | ^ -> <->")
        while index < len(tokens) and precedence.get(tokens[index], 0) >= minimum:
            op = tokens[index]
            index += 1
            right = expression(precedence[op] + (op != "->"), depth + 1)
            left = node(op, left, right)
        return left

    result = expression(1, 0)
    if index != len(tokens):
        raise MathInputError("Unexpected logical token")
    return result
