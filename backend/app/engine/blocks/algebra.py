"""Exact bounded scalar Algebra forms, independent of legacy records (#196)."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import Any, Literal

import sympy as sp
from pydantic import Field

from app.engine.models import Parameters, Step

X = sp.Symbol("x", real=True)
type AlgebraKind = Literal["determinant", "modulus", "root-sum", "decompose"]


class AlgebraForm(Parameters):
    kind: AlgebraKind
    a: int = Field(ge=1, le=5)
    b: int = Field(ge=1, le=5)

    def evaluate(self) -> AlgebraData:
        return _evaluate(self)


@dataclass(frozen=True)
class AlgebraData:
    statement: str
    expected: Any
    steps: tuple[Step, ...]


@cache
def _evaluate(form: AlgebraForm) -> AlgebraData:
    a, b = sp.Integer(form.a), sp.Integer(form.b)
    if form.kind == "determinant":
        c, d = b + 1, a + 2
        expected = a * d - b * c
        proof = sp.Matrix([[a, b], [c, d]]).det()
        statement = rf"\det\begin{{pmatrix}}{a}&{b}\\{c}&{d}\end{{pmatrix}}"
        steps = (Step("determinant", rf"{a}\cdot{d}-{b}\cdot{c}={sp.latex(expected)}"),)
    elif form.kind == "modulus":
        expected = sp.sqrt(a**2 + b**2)
        proof = sp.Abs(a + b * sp.I)
        statement = rf"|{a}+{b}i|"
        steps = (Step("modulus", rf"\sqrt{{{a}^2+{b}^2}}={sp.latex(expected)}"),)
    elif form.kind == "root-sum":
        expected = -a
        # Include complex roots and count repeated roots with multiplicity.
        proof = sum(sp.Poly(X**2 + a * X + b, X).all_roots())
        statement = rf"x^2+{a}x+{b}=0: \text{{sum of the roots}}"
        steps = (Step("root_sum", rf"x_1+x_2=-{a}={sp.latex(expected)}"),)
    else:
        expected = a / (X + 1) + b / (X + 2)
        numerator = sp.expand(a * (X + 2) + b * (X + 1))
        proof = sp.apart(numerator / ((X + 1) * (X + 2)), X)
        statement = rf"\frac{{{sp.latex(numerator)}}}{{(x+1)(x+2)}}= ?"
        steps = (Step("decompose", sp.latex(expected)),)
    if sp.simplify(expected - proof) != 0:
        raise ValueError("Algebra form failed its independent exact proof")
    return AlgebraData(statement, expected, steps)
