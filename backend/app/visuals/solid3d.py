"""#114: the `solid3d` visual of triple-v1 records (ADR-006).

The spec is the solution's set-up without its integrand: the coordinate system
and the bounds innermost first, `z` between two surfaces over a planar region.
The browser draws the bottom and top surfaces over the region and the side walls
along its boundary. The integrand, a scalar field, is not part of the spec.
"""

import math
from typing import Any

from app.engine.blocks.multiple.setup import SetupLike, bounds_latex
from app.visuals.expression import to_tree
from app.visuals.region2d import _interval, _numeric

KIND = "solid3d"

# Parameter grid used to find the window; the browser meshes its own grid.
_SAMPLES = 41
# Margin around the solid's bounding box, as a fraction of its largest side.
_MARGIN = 0.06


def solid_points(setup: SetupLike, samples: int = _SAMPLES) -> list[tuple[float, float, float]]:
    """Points (x, y, z) on the bottom and top surfaces over a grid of the region.

    `s` runs over the outer interval and `t` from the middle lower to the middle
    upper bound, exactly as the browser does it.
    """
    (z, z_low, z_high), (middle, middle_low, middle_high), (outer, outer_low, outer_high) = (
        setup.bounds
    )
    low = _numeric((outer,), middle_low)
    high = _numeric((outer,), middle_high)
    bottom = _numeric((middle, outer), z_low)
    top = _numeric((middle, outer), z_high)
    a, b = float(outer_low), float(outer_high)
    points = []
    for i in range(samples):
        u = a + (b - a) * i / (samples - 1)
        g, h = low(u), high(u)
        for j in range(samples):
            v = g + (h - g) * j / (samples - 1)
            x, y = to_xy(setup, v, u)
            points.extend([(x, y, bottom(v, u)), (x, y, top(v, u))])
    return points


def to_xy(setup: SetupLike, middle: float, outer: float) -> tuple[float, float]:
    values = {str(setup.bounds[1][0]): middle, str(setup.bounds[2][0]): outer}
    if setup.system == "cylindrical":
        return values["r"] * math.cos(values["theta"]), values["r"] * math.sin(values["theta"])
    return values["x"], values["y"]


def solid3d_setup(setup: SetupLike) -> dict[str, Any]:
    """Render the typed solution setup shared by native and old records."""
    if len(setup.bounds) != 3 or setup.system not in ("cartesian", "cylindrical"):
        raise ValueError("solid3d needs a three-level Cartesian or cylindrical set-up")
    if str(setup.bounds[0][0]) != "z":
        raise ValueError("solid3d needs z innermost")
    points = solid_points(setup)
    axes: list[list[Any]] = [[p[k] for p in points] for k in range(3)]
    side = max(max(axis) - min(axis) for axis in axes)
    margin = _MARGIN * side
    return {
        "kind": KIND,
        "system": setup.system,
        "bounds": [
            [str(variable), to_tree(lower), to_tree(upper)]
            for variable, lower, upper in setup.bounds
        ],
        "window": {
            name: _interval(axis, margin=margin) for name, axis in zip("xyz", axes, strict=True)
        },
        "solid": bounds_latex(setup),
    }
