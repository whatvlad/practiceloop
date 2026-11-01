"""Bounded, independently proved analysis forms for the current syllabus (#197)."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import Any, Literal

import sympy as sp
from pydantic import Field

from app.engine.models import Parameters, Step

X, Y = sp.symbols("x y", real=True)
N = sp.Symbol("n", integer=True, nonnegative=True)
type AnalysisKind = Literal[
    "sequence-value",
    "limit",
    "continuity",
    "improper-integral",
    "geometric-series",
    "partial-value",
    "exponential-solution",
]


class AnalysisForm(Parameters):
    kind: AnalysisKind
    a: int = Field(ge=1, le=5)
    b: int = Field(ge=1, le=5)

    def evaluate(self) -> AnalysisData:
        return _evaluate(self)


@dataclass(frozen=True)
class AnalysisData:
    statement: str
    expected: Any
    steps: tuple[Step, ...]


@cache
def _evaluate(form: AnalysisForm) -> AnalysisData:
    a, b = sp.Integer(form.a), sp.Integer(form.b)
    if form.kind == "sequence-value":
        expected = a * 5 + b
        proof = (a * N + b).subs(N, 5)
        statement = rf"a_n={a}n+{b};\quad a_5=?"
        steps = (Step("sequence", rf"a_5={a}\cdot5+{b}={sp.latex(expected)}"),)
    elif form.kind in ("limit", "continuity"):
        expected = 2 * a
        quotient = (X**2 - a**2) / (X - a)
        left, right = sp.limit(quotient, X, a, dir="-"), sp.limit(quotient, X, a, dir="+")
        if left != right:
            raise ValueError("The removable limit must exist on both sides")
        proof = left
        if form.kind == "limit":
            statement = rf"\lim_{{x\to{a}}}\frac{{x^2-{a**2}}}{{x-{a}}}=?"
            steps = (Step("limit", rf"\lim_{{x\to{a}}}(x+{a})={sp.latex(expected)}"),)
        else:
            statement = rf"f(x)=\frac{{x^2-{a**2}}}{{x-{a}}},\quad f({a})=?\text{{ for continuity}}"
            steps = (Step("continuity", rf"f({a})={sp.latex(expected)}"),)
    elif form.kind == "improper-integral":
        expected = sp.Rational(1, a)
        proof = sp.integrate(X ** (-a - 1), (X, 1, sp.oo))
        statement = rf"\int_{{1}}^\infty \frac{{1}}{{x^{{{a + 1}}}}}\,dx=?"
        steps = (Step("improper", sp.latex(expected)),)
    elif form.kind == "geometric-series":
        # The legacy symbolic-v1 value (a+1)/a was wrong for a>1.
        ratio = a / (a + 1)
        expected = a + 1
        if not 0 < ratio < 1:
            raise ValueError("The geometric series must converge")
        proof = sp.summation(ratio**N, (N, 0, sp.oo))
        statement = rf"\sum_{{n=0}}^\infty \left(\frac{{{a}}}{{{a + 1}}}\right)^n=?"
        steps = (Step("series", rf"\frac{{1}}{{1-{a}/{a + 1}}}={sp.latex(expected)}"),)
    elif form.kind == "partial-value":
        # The held-constant term b*y contributes zero, not b.
        expected = 2 * a * X * Y
        proof = sp.diff(a * X**2 * Y + b * Y, X)
        statement = rf"f(x,y)={a}x^2y+{b}y;\quad \frac{{\partial f}}{{\partial x}}=?"
        steps = (Step("partial", rf"f_x={sp.latex(expected)}"),)
    else:
        expected = sp.exp(a * X)
        if sp.simplify(sp.diff(expected, X) - a * expected) != 0 or expected.subs(X, 0) != 1:
            raise ValueError("The ODE solution must satisfy the equation and initial condition")
        proof = sp.exp(sp.integrate(a, X))
        statement = rf"y'={a}y,\ y(0)=1;\quad y(x)=?"
        steps = (Step("ode", rf"y(x)={sp.latex(expected)}"),)
    if sp.simplify(expected - proof) != 0 or expected.is_finite is False:
        raise ValueError("Analysis form failed its independent exact proof")
    return AnalysisData(statement, expected, steps)
