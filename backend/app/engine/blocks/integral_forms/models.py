"""Typed mathematical output of an integral form, independent of task generators."""

from dataclasses import dataclass
from typing import Any

import sympy as sp


@dataclass(frozen=True)
class MethodTemplate:
    difficulty: int
    domain: Any
    primary_method: str
    auxiliary_transformations: tuple[str, ...] = ()


@dataclass(frozen=True)
class MethodStep:
    kind: str
    expression: Any

    @property
    def latex(self) -> str:
        return str(sp.latex(self.expression))
