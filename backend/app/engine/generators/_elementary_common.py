"""Private bounded data and exact rendering for elementary computational families."""

from dataclasses import dataclass
from typing import Any

import sympy as sp
from pydantic import Field

from app.engine.answers.computational import (
    CategoryAnswer,
    OrderedAnswer,
    RealSetAnswer,
)
from app.engine.answers.domain_formula import DomainFormulaAnswer
from app.engine.models import Answer, Drawn, Step

X = sp.Symbol("x", real=True)
REAL_FORMULA = (("x", "real"),)
TRUTH_CHOICES = ("true", "false")


class ElementaryParams(Drawn):
    a: int = Field(ge=1, le=4)
    b: int = Field(ge=1, le=4)
    c: int = Field(ge=1, le=4)
    variant: int = Field(ge=0, le=5)


@dataclass(frozen=True, slots=True)
class Built:
    statement: str
    answer: Answer
    steps: tuple[Step, ...]
    sets: tuple[tuple[str, Any], ...] = ()


def tex(value: Any) -> str:
    return str(sp.latex(value))


def finish(
    statement: str,
    answer: Answer,
    method: str,
    derivation: str,
    sets: tuple[tuple[str, Any], ...] = (),
) -> Built:
    return Built(
        statement,
        answer,
        (Step("method", method), Step("calculation", derivation), Step("result", answer.latex())),
        sets,
    )


def category(value: bool) -> CategoryAnswer:
    return CategoryAnswer("true" if value else "false", TRUTH_CHOICES)


def expression_set(
    expression: Any, domain: Any, labels: tuple[str, str] = ("Expression", "Domain")
) -> OrderedAnswer:
    return OrderedAnswer((DomainFormulaAnswer(expression, domain), RealSetAnswer(domain)), labels)


def set_diagram(sets: tuple[tuple[str, Any], ...]) -> dict[str, Any] | None:
    """Exact finite endpoints, explicit open/closed marks and clipped infinite rays."""
    if not sets:
        return None
    endpoints = []
    for _, solution in sets:
        for piece in solution.args if isinstance(solution, sp.Union) else (solution,):
            endpoints.extend(
                list(piece)
                if isinstance(piece, sp.FiniteSet)
                else [piece.start, piece.end]
                if isinstance(piece, sp.Interval)
                else []
            )
    finite = [float(x) for x in endpoints if x not in {-sp.oo, sp.oo}]
    lo, hi = (min(finite) - 2.0, max(finite) + 2.0) if finite else (-5.0, 5.0)
    paths, points = [], []
    for row, (label, solution) in enumerate(sets, 1):
        for piece in solution.args if isinstance(solution, sp.Union) else (solution,):
            if piece == sp.S.Reals:
                piece = sp.Interval(-sp.oo, sp.oo)
            if isinstance(piece, sp.Interval):
                start = lo if piece.start == -sp.oo else float(piece.start)
                end = hi if piece.end == sp.oo else float(piece.end)
                vertices = [[start, float(row)], [end, float(row)]]
                if piece.start == -sp.oo and piece.end != sp.oo:
                    vertices.reverse()
                paths.append(
                    {
                        "label": label,
                        "points": vertices,
                        "arrow": piece.start == -sp.oo or piece.end == sp.oo,
                    }
                )
                if piece.start == -sp.oo and piece.end == sp.oo:
                    paths[-1]["label"] = label + " all reals"
                for value, included in (
                    (piece.start, not piece.left_open),
                    (piece.end, not piece.right_open),
                ):
                    if value not in {-sp.oo, sp.oo}:
                        points.append(
                            {
                                "label": label + " endpoint",
                                "x": float(value),
                                "y": float(row),
                                "included": included,
                            }
                        )
            elif isinstance(piece, sp.FiniteSet):
                points.extend(
                    {
                        "label": label + " point",
                        "x": float(value),
                        "y": float(row),
                        "included": True,
                    }
                    for value in piece
                )
    # An empty set is explicitly named in the solution, with no invented geometry.
    if not paths and not points:
        return None
    return {
        "kind": "plot2d",
        "version": 1,
        "title": "Exact real sets",
        "description": (
            "Rows show sets in the plotted window. Filled endpoints are included. "
            "Arrows continue infinite rays."
        ),
        "x": [lo, hi],
        "y": [0.0, float(len(sets) + 1)],
        "xLabel": "x",
        "yLabel": "Set row",
        "paths": paths,
        "points": points,
    }
