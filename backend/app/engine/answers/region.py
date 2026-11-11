"""Exact regions expressed by declared predicates and all realizable truth rows."""

from dataclasses import dataclass

from app.engine.answers.logic import LogicAnswer, truth
from app.engine.models import Outcome
from app.math_input import MathNode


@dataclass(frozen=True)
class RegionLogicAnswer(LogicAnswer):
    rows: tuple[tuple[bool, ...], ...]

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.rows or len(set(self.rows)) != len(self.rows):
            raise ValueError("Region must declare distinct realizable truth rows")
        if any(len(row) != len(self.atoms) for row in self.rows):
            raise ValueError("Region truth rows must match the declared predicates")

    def check(self, tree: MathNode) -> Outcome:
        try:
            for row in self.rows:
                values = dict(zip(self.atoms, row, strict=True))
                if truth(tree, values) != truth(self.expected, values):
                    return "incorrect"
            return "correct"
        except (ValueError, KeyError, IndexError):
            return "invalid"
