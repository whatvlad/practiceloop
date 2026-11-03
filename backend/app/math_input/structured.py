"""Bounded answer-kind grammar; the kind comes from a trusted generator only."""

from collections.abc import Collection

from app.math_input.parser import (
    MAX_FUNCTION_CALLS,
    MAX_NODES,
    MAX_TOKENS,
    MathInputError,
    MathNode,
    _normalise,
    _tokenise,
    parse_math_input,
)

STRUCTURED_KINDS = frozenset({"boolean", "finite_set", "interval"})
MAX_SET_ITEMS = 8


def _split(source: str) -> list[str]:
    parts, start, depth = [], 0, 0
    for i, character in enumerate(source):
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
        elif character == "," and depth == 0:
            parts.append(source[start:i])
            start = i + 1
        if depth < 0:
            raise MathInputError("Unbalanced component")
    if depth:
        raise MathInputError("Unbalanced component")
    parts.append(source[start:])
    return parts


def parse_answer_input(
    source: str, kind: str, variables: Collection[str] | None = None
) -> MathNode:
    if kind not in STRUCTURED_KINDS:
        return parse_math_input(source, variables)
    if not isinstance(source, str):
        raise MathInputError("Input must be text")
    text = _normalise(source.replace("∞", "inf")).strip()
    if kind == "boolean":
        if text not in {"true", "false"}:
            raise MathInputError("Choose yes or no")
        return MathNode("boolean", text)
    if kind == "finite_set":
        if not (text.startswith("{") and text.endswith("}")):
            raise MathInputError("Use a finite set")
        parts = _split(text[1:-1]) if text[1:-1].strip() else []
        if len(parts) > MAX_SET_ITEMS:
            raise MathInputError("Too many set entries")
        value = "finite"
    else:
        if len(text) < 5 or text[0] not in "[(" or text[-1] not in "])":
            raise MathInputError("Use an interval with two endpoints")
        parts = _split(text[1:-1])
        if len(parts) != 2:
            raise MathInputError("An interval has two endpoints")
        value = text[0] + text[-1]
    children, token_count = [], 2 + len(parts)
    for index, part in enumerate(parts):
        part = part.strip()
        if kind == "interval" and part in {"-inf", "inf", "+inf"}:
            negative = part == "-inf"
            if (index == 0) != negative or text[index * (len(text) - 1)] != (
                "(" if negative else ")"
            ):
                raise MathInputError("Infinite endpoints must be open and correctly signed")
            children.append(MathNode("endpoint", "-inf" if negative else "inf"))
            token_count += 1
        else:
            children.append(parse_math_input(part, {}))
            token_count += len(_tokenise(part, split_names=True))
    root = MathNode("finite_set" if kind == "finite_set" else "interval", value, tuple(children))
    stack, nodes, functions = [root], 0, 0
    while stack:
        node = stack.pop()
        nodes += 1
        functions += node.kind == "function"
        stack.extend(node.children)
    if nodes > MAX_NODES or functions > MAX_FUNCTION_CALLS or token_count > MAX_TOKENS:
        raise MathInputError("Structured answer exceeds the shared complexity budget")
    return root
