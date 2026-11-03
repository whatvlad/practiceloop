"""Strict bounded records and exact result data shared by Analysis II blocks."""

from dataclasses import dataclass
from typing import Any

import sympy as sp
from pydantic import Field

from app.engine.models import Parameters, Step
from app.math_input import VariableDomain

X, Y, Z = sp.symbols("x y z", real=True)
N = sp.Symbol("n", integer=True, positive=True)
T = sp.Symbol("t", real=True)
B = sp.Symbol("B", positive=True)


class AnalysisTwoForm(Parameters):
    a: int = Field(ge=1, le=5)
    b: int = Field(ge=1, le=5)
    c: int = Field(ge=1, le=5)


@dataclass(frozen=True)
class AnalysisTwoData:
    statement: str
    expected: Any
    variables: dict[str, VariableDomain]
    steps: tuple[Step, ...]


def finish(
    statement: str, expected: Any, proof: Any, details: tuple[str, ...], *, symbolic: bool = False
) -> AnalysisTwoData:
    expected, proof = sp.sympify(expected), sp.sympify(proof)
    if sp.simplify(expected - proof) != 0 or expected.is_finite is False:
        raise ValueError("Analysis II exact certificate failed")
    return AnalysisTwoData(
        statement,
        expected,
        {"x": "real"} if symbolic else {},
        tuple(Step("reason", line) for line in details) + (Step("result", sp.latex(expected)),),
    )
