"""New opt-in computational grammars with one aggregate complexity budget."""

from app.math_input.contracts import InputContract
from app.math_input.parser import (
    MAX_FUNCTION_CALLS,
    MAX_NESTING,
    MAX_NODES,
    MAX_TOKENS,
    MathInputError,
    MathNode,
    _normalise,
    _Parser,
    _tokenise,
)


def split_parts(text: str, separator: str) -> list[str]:
    """Interval brackets may have different closure; track container depth only."""
    depth = start = 0
    parts = []
    for index, char in enumerate(text):
        if char in "([{":
            depth += 1
            if depth > MAX_NESTING:
                raise MathInputError("Answer nesting exceeds the shared budget")
        elif char in ")]}":
            depth -= 1
            if depth < 0:
                raise MathInputError("Unbalanced answer container")
        elif char == separator and depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1
    if depth:
        raise MathInputError("Unbalanced answer container")
    parts.append(text[start:].strip())
    return parts


def parse_computational(source: str, contract: InputContract) -> MathNode:
    # Normalize the COMPLETE text first: nested components do not get 256 bytes each.
    if not isinstance(source, str):
        raise MathInputError("Input must be text")
    text = _normalise(source.replace("∞", "inf").replace("∪", " U ")).strip()
    tree = _parse(text, contract)
    stack = [(tree, 0)]
    nodes = functions = 0
    while stack:
        node, depth = stack.pop()
        nodes += 1
        functions += node.kind == "function"
        if depth > MAX_NESTING:
            raise MathInputError("Answer nesting exceeds the shared budget")
        stack.extend((child, depth + 1) for child in node.children)
    # Structural punctuation and arithmetic tokens share a conservative budget.
    import re

    tokens = len(re.findall(r"[A-Za-z]+|[0-9.]+|[^\s]", text))
    if nodes > MAX_NODES or functions > MAX_FUNCTION_CALLS or tokens > MAX_TOKENS:
        raise MathInputError("Answer exceeds the shared complexity budget")
    return tree


def _parse(text: str, spec: InputContract) -> MathNode:
    if spec.kind == "logic":
        from app.math_input.logic import parse_logic

        return parse_logic(text, spec.choices)
    if spec.kind == "limit_result":
        if text in {"inf", "+inf", "-inf", "does_not_exist"}:
            return MathNode("category", "inf" if text == "+inf" else text)
        return _Parser(_tokenise(text), frozenset()).parse()
    if spec.kind == "formula":
        # Local symbols require explicit multiplication between letter names.
        return _Parser(
            _tokenise(text), frozenset(dict(spec.symbols)), positive_base_powers=True
        ).parse()
    if spec.kind == "category":
        if text not in spec.choices:
            raise MathInputError("Choose one of the declared results")
        return MathNode("category", text)
    if spec.kind == "tuple":
        if not (text.startswith("(") and text.endswith(")")):
            raise MathInputError("Use parentheses and semicolons for ordered components")
        parts = split_parts(text[1:-1], ";")
        if len(parts) != len(spec.components):
            raise MathInputError("Wrong number of ordered components")
        return MathNode(
            "tuple",
            "ordered",
            tuple(_parse(part, child) for part, child in zip(parts, spec.components, strict=True)),
        )
    return _real_set(text)


def _real_set(text: str) -> MathNode:
    from app.math_input.structured import parse_answer_input

    if text == "R":
        return MathNode("real_set", "real")
    if text.startswith("R\\"):
        removed = parse_answer_input(text[2:].strip(), "finite_set")
        return MathNode("real_set", "excluded", (removed,))
    parts = split_parts(text, "U")
    if len(parts) > 8:
        raise MathInputError("Too many set pieces")
    children = []
    for part in parts:
        if part.startswith("{"):
            children.append(parse_answer_input(part, "finite_set"))
        elif part.startswith(("(", "[")):
            children.append(parse_answer_input(part, "interval"))
        else:
            raise MathInputError("Use intervals, finite sets, R or R\\{excluded points}")
    return MathNode("real_set", "union", tuple(children))
