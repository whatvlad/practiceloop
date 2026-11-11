"""Bounded solution diagrams for the complex plane."""

import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.visuals.plot2d import Finite


class ComplexPlane(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    kind: Literal["complex-plane"]
    version: Literal[1]
    mode: Literal[
        "circle", "modulus", "argument", "add", "subtract", "multiply", "divide", "power", "root"
    ]
    first: tuple[Finite, Finite]
    second: tuple[Finite, Finite] | None
    result: tuple[Finite, Finite] | None
    power: int | None = Field(ge=1, le=20)
    radius: float | None = Field(default=None, gt=0, le=1e8, allow_inf_nan=False)
    firstLabel: str | None = Field(default=None, max_length=120)


def validate_visual(value: object) -> dict[str, Any]:
    if isinstance(value, dict) and value.get("kind") == "geometry3d":
        from app.visuals.geometry import validate_geometry

        return validate_geometry(value)
    if isinstance(value, dict) and value.get("kind") == "complex-plane":
        diagram = ComplexPlane.model_validate_json(json.dumps(value, allow_nan=False))
        if diagram.mode == "circle" and diagram.radius is None:
            raise ValueError("Circle diagram requires a radius")
        if diagram.mode in {"add", "subtract", "multiply", "divide"} and (
            diagram.second is None or diagram.result is None
        ):
            raise ValueError("Complex operation needs operands and result")
        if diagram.mode == "root" and diagram.result is None:
            raise ValueError("Root diagram needs a result")
        if diagram.mode == "power" and (diagram.result is None or diagram.power is None):
            raise ValueError("Power diagram needs a result and exponent")
        return diagram.model_dump(mode="json", exclude_none=True) | {
            "second": list(diagram.second) if diagram.second is not None else None,
            "result": list(diagram.result) if diagram.result is not None else None,
            "power": diagram.power,
        }
    from app.visuals.plot2d import validate_plot

    return validate_plot(value)
