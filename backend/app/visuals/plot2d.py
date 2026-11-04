"""Bounded parameter-derived solution diagrams, built before catalogue publication."""

from __future__ import annotations

import json
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Finite = Annotated[float, Field(allow_inf_nan=False, ge=-1e8, le=1e8)]
Label = Annotated[str, Field(min_length=1, max_length=120, pattern=r"^[A-Za-z0-9 .,():/+=-]+$")]


class DiagramModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class PlotPath(DiagramModel):
    label: Label
    points: list[tuple[Finite, Finite]] = Field(min_length=2, max_length=96)
    closed: bool = False
    arrow: bool = False


class PlotPoint(DiagramModel):
    label: Label
    x: Finite
    y: Finite
    included: bool = True


class PlotDiagram(DiagramModel):
    kind: Literal["plot2d"] = "plot2d"
    version: Literal[1] = 1
    title: Label
    description: Label
    x: tuple[Finite, Finite]
    y: tuple[Finite, Finite]
    xLabel: Label = "x"
    yLabel: Label = "y"
    paths: list[PlotPath] = Field(max_length=8)
    points: list[PlotPoint] = Field(default_factory=list, max_length=32)

    @field_validator("x", "y")
    @classmethod
    def increasing(cls, value: tuple[float, float]) -> tuple[float, float]:
        if value[0] >= value[1]:
            raise ValueError("Diagram window must increase")
        return value

    @model_validator(mode="after")
    def bounded(self) -> PlotDiagram:
        if sum(len(p.points) for p in self.paths) > 192 or not (self.paths or self.points):
            raise ValueError("Diagram must contain bounded geometry")
        for point in self.points:
            if not (self.x[0] <= point.x <= self.x[1] and self.y[0] <= point.y <= self.y[1]):
                raise ValueError("Marked point lies outside the window")
        if len(self.model_dump_json().encode("utf-8")) > 8192:
            raise ValueError("Diagram exceeds the visual budget")
        return self


def validate_plot(value: object) -> dict[str, Any]:
    """Strict round trip detaches nested mutable data and enforces JSON shape."""
    # JSON mode accepts JSON arrays as fixed coordinate pairs, strict numbers
    # and booleans. No symbolic parsing or arbitrary expression evaluation.
    return PlotDiagram.model_validate_json(json.dumps(value, allow_nan=False)).model_dump(
        mode="json"
    )
