"""Public geometry selectors only. No parameters, code versions or answers."""

import json
from importlib.resources import files
from typing import Literal

GeometryExerciseMode = Literal[
    "point-collinearity",
    "parallel-vector",
    "unit-perpendiculars",
    "constrained-vector",
    "plane-equation",
    "plane-parameterisation",
    "line-equation",
    "containing-plane",
    "perpendicular-line",
    "parallel-parameter",
    "normal-parameters",
    "planes-common-point",
    "planes-common-line",
    "planes-three-lines",
    "line-angle",
    "plane-angle",
    "point-line-distance",
    "point-plane-distance",
    "parallel-line-distance",
    "skew-line-distance",
    "parallel-plane-distance",
    "line-line-intersection",
    "line-plane-intersection",
    "equidistant-plane",
    "point-line-projection",
    "point-plane-projection",
    "line-plane-projection",
    "directed-point-line-projection",
    "directed-point-plane-projection",
    "directed-line-plane-projection",
    "same-side",
    "line-reflection",
    "plane-reflection",
    "line-position",
    "line-plane-position",
]

_public = json.loads(
    files("app.content").joinpath("geometry_modes.json").read_text(encoding="utf-8")
)
GEOMETRY_OPTIONS: dict[str, dict[str, str]] = _public["modes"]


def geometry_modes(topic: str) -> frozenset[str]:
    return frozenset(mode for mode, data in GEOMETRY_OPTIONS.items() if data["topic"] == topic)
