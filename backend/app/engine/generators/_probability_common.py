"""Typed build results and formatting shared by trusted probability generators."""

from dataclasses import dataclass
from fractions import Fraction as F
from typing import Any

import sympy as sp
from pydantic import Field

from app.engine.answers.structured import RealScalarAnswer
from app.engine.blocks.distribution import FiniteDistribution, JointDistribution
from app.engine.models import Answer, Drawn, Step


class ProbabilityParams(Drawn):
    a: int = Field(ge=1, le=5)
    b: int = Field(ge=1, le=5)
    c: int = Field(ge=1, le=5)


@dataclass(frozen=True, slots=True)
class Built:
    statement: str
    steps: tuple[Step, ...]
    answer: Answer


def tex(value: Any) -> str:
    return str(sp.latex(sp.sympify(value)))


def scalar(value: Any) -> RealScalarAnswer:
    return RealScalarAnswer(sp.sympify(value), {})


def finish(statement: str, answer: Answer, formula: str, calculation: str) -> Built:
    return Built(
        statement,
        (
            Step("method", formula),
            Step("substitution", calculation),
            Step("result", answer.latex()),
        ),
        answer,
    )


def finite(p: ProbabilityParams) -> FiniteDistribution:
    return FiniteDistribution.from_weights((-p.a, 0, p.b), (p.a, p.b, p.c))


def table(d: FiniteDistribution) -> str:
    return (
        r"\begin{array}{c|"
        + "c" * len(d.values)
        + "}x&"
        + "&".join(map(tex, d.values))
        + r"\\\hline P(X=x)&"
        + "&".join(map(tex, d.masses))
        + r"\end{array}"
    )


def joint(p: ProbabilityParams) -> JointDistribution:
    a, b, c = p.a, p.b, p.c
    weights = ((a * b + (c % 2 == 0), a * c), (b, c))
    total = sum(sum(row) for row in weights)
    return JointDistribution(
        x=(F(0), F(1)),
        y=(F(0), F(2)),
        masses=tuple(tuple(F(w, total) for w in row) for row in weights),
    )


def joint_table(d: JointDistribution) -> str:
    rows = [tex(x) + "&" + "&".join(map(tex, row)) for x, row in zip(d.x, d.masses, strict=True)]
    return r"\begin{array}{c|cc}X\backslash Y&0&2\\\hline" + r"\\".join(rows) + r"\end{array}"
