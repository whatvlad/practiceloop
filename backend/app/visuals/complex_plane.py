"""Bounded solution diagrams for the complex plane."""

import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.visuals.plot2d import Finite


class ComplexPlane(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    kind: Literal["complex-plane"]
    version: Literal[1]
    mode: Literal["circle", "modulus"]
    first: tuple[Finite, Finite]
    second: None
    result: None
    power: None
    radius: float | None = Field(default=None, gt=0, le=1e8, allow_inf_nan=False)
    firstLabel: str | None = Field(default=None, max_length=120)


def validate_visual(value: object) -> dict[str, Any]:
    if isinstance(value, dict) and value.get("kind") == "complex-plane":
        diagram = ComplexPlane.model_validate_json(json.dumps(value, allow_nan=False))
        if diagram.mode == "circle" and diagram.radius is None:
            raise ValueError("Circle diagram requires a radius")
        return diagram.model_dump(mode="json", exclude_none=True) | {
            "second": None, "result": None, "power": None,
        }
    from app.visuals.plot2d import validate_plot

    return validate_plot(value)
