"""Full truth-table equivalence over at most three declared propositional atoms."""

from dataclasses import dataclass
from itertools import product
from typing import ClassVar

from app.engine.models import Outcome
from app.math_input import MathNode
from app.math_input.contracts import InputContract


def truth(tree: MathNode, values: dict[str, bool]) -> bool:
    if tree.kind != "logic":
        raise ValueError("Expected logic tree")
    if not tree.children:
        if tree.value in {"0", "1"}:
            return tree.value == "1"
        return values[str(tree.value)]
    left = truth(tree.children[0], values)
    if tree.value == "!" and len(tree.children) == 1:
        return not left
    if len(tree.children) != 2:
        raise ValueError("Invalid logical arity")
    right = truth(tree.children[1], values)
    match tree.value:
        case "&":
            return left and right
        case "|":
            return left or right
        case "^":
            return left != right
        case "->":
            return not left or right
        case "<->":
            return left == right
        case _:
            raise ValueError("Unknown logical operation")


@dataclass(frozen=True, slots=True)
class LogicAnswer:
    expected: MathNode
    atoms: tuple[str, ...]
    kind: ClassVar[str] = "logic"

    def __post_init__(self) -> None:
        _ = self.contract
        for row in product((False, True), repeat=len(self.atoms)):
            truth(self.expected, dict(zip(self.atoms, row, strict=True)))

    @property
    def contract(self) -> InputContract:
        return InputContract("logic", choices=self.atoms)

    def latex(self) -> str:
        def render(tree: MathNode) -> str:
            if not tree.children:
                return str(tree.value)
            if tree.value == "!":
                return r"\neg " + render(tree.children[0])
            ops = {
                "&": r"\land",
                "|": r"\lor",
                "^": r"\oplus",
                "->": r"\Rightarrow",
                "<->": r"\Leftrightarrow",
            }
            return (
                r"\left("
                + render(tree.children[0])
                + " "
                + ops[str(tree.value)]
                + " "
                + render(tree.children[1])
                + r"\right)"
            )

        return render(self.expected)

    def check(self, tree: MathNode) -> Outcome:
        try:
            for row in product((False, True), repeat=len(self.atoms)):
                values = dict(zip(self.atoms, row, strict=True))
                if truth(tree, values) != truth(self.expected, values):
                    return "incorrect"
            return "correct"
        except (ValueError, KeyError, IndexError):
            return "invalid"
