"""Plain, bounded grammar metadata for new computational answer versions (#234).

No expected values or symbolic construction belong in this module. Existing
answer kinds keep their original parsers and variable allowlists.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

Domain = Literal["real", "positive", "integer"]
COMPUTATIONAL_KINDS = frozenset(
    {"real_set", "tuple", "category", "formula", "limit_result", "logic"}
)
PARAMETER_NAMES = frozenset({"a", "b", "c", "C", "D", "k", "m", "n", "t", "s"})
COORDINATE_NAMES = frozenset({"x", "y", "z", "r", "theta"})
_MATRIX_NAMES = ("one", "two", "three", "four", "five")


@dataclass(frozen=True, slots=True)
class InputContract:
    kind: str
    symbols: tuple[tuple[str, Domain], ...] = ()
    components: tuple[InputContract, ...] = ()
    labels: tuple[str, ...] = ()
    choices: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.kind not in COMPUTATIONAL_KINDS:
            raise ValueError("Unknown computational contract")
        if len(self.symbols) > 8 or len(dict(self.symbols)) != len(self.symbols):
            raise ValueError("Invalid symbol declaration")
        for name, domain in self.symbols:
            if name not in PARAMETER_NAMES | COORDINATE_NAMES or domain not in {
                "real",
                "positive",
                "integer",
            }:
                raise ValueError("Unsupported local symbol or domain")
        if self.symbols and self.kind != "formula":
            raise ValueError("Only formula components declare symbols")
        if self.kind == "tuple":
            if not 1 <= len(self.components) <= 8 or len(self.labels) != len(self.components):
                raise ValueError("Tuple needs bounded labelled components")
            if any(not re.fullmatch(r"[A-Za-z][A-Za-z -]{0,39}", x) for x in self.labels):
                raise ValueError("Invalid component label")
        elif self.components or self.labels:
            raise ValueError("Unexpected components")
        if self.kind == "category":
            if not 2 <= len(self.choices) <= 8 or len(set(self.choices)) != len(self.choices):
                raise ValueError("Category needs distinct choices")
            if any(not re.fullmatch(r"[a-z][a-z_]{0,31}", x) for x in self.choices):
                raise ValueError("Invalid category choice")
        elif self.kind == "logic":
            if not 1 <= len(self.choices) <= 3 or len(set(self.choices)) != len(self.choices):
                raise ValueError("Logic needs one to three distinct atoms")
            if any(atom not in {"p", "q", "r"} for atom in self.choices):
                raise ValueError("Unsupported propositional atom")
        elif self.choices:
            raise ValueError("Unexpected category choices")
        matrix = (
            self.kind == "tuple"
            and 1 <= len(self.components) <= 5
            and self.labels
            == tuple(f"Matrix row {name}" for name in _MATRIX_NAMES[: len(self.components)])
            and all(
                row.kind == "tuple"
                and 1 <= len(row.components) <= 5
                and len(row.components) == len(self.components[0].components)
                and row.labels
                == tuple(f"Column {name}" for name in _MATRIX_NAMES[: len(row.components)])
                and all(cell.kind == "formula" for cell in row.components)
                for row in self.components
            )
        )
        stack = [(self, 0)]
        count = 0
        while stack:
            node, depth = stack.pop()
            count += 1
            if depth > 3 or count > (31 if matrix else 16):
                raise ValueError("Contract is too complex")
            stack.extend((child, depth + 1) for child in node.components)

    def public(self) -> dict[str, object]:
        result: dict[str, object] = {"kind": self.kind, "maxBytes": 256}
        if self.symbols:
            result["symbols"] = dict(self.symbols)
        if self.components:
            result["components"] = [part.public() for part in self.components]
            result["labels"] = list(self.labels)
        if self.choices:
            result["choices"] = list(self.choices)
        if self.kind == "real_set":
            result["maxItems"] = 8
        return result
