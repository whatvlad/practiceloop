"""#113: the `region2d` visual of double-v1 records (ADR-006).

The spec is the solution's set-up as it is: the coordinate system, the bounds
innermost first and the integrand in that system's variables without the
Jacobian, scaled by the record's coefficient. The browser draws the region from
the bounds and meshes the surface `z = f` over the same parameter grid, so the
spec carries nothing the solution steps do not already show.
"""

import math
from collections.abc import Callable
from typing import Any

import sympy as sp

from app.engine.blocks.multiple.setup import SetupLike, bounds_latex
from app.generators.core import Exercise
from app.generators.double import solution_setup
from app.visuals.expression import to_tree

KIND = "region2d"

# Parameter grid used to find the window; the browser meshes its own grid.
_SAMPLES = 41
# Margin around the region's bounding box, as a fraction of its larger side.
_MARGIN = 0.08


def _numeric(variables: tuple[Any, ...], expression: Any) -> Callable[..., float]:
    function = sp.lambdify(variables, expression, "math")

    def value(*args: float) -> float:
        try:
            result = complex(function(*args))
        except (ArithmeticError, ValueError):
            return math.nan
        return result.real if abs(result.imag) < 1e-12 else math.nan

    return value


def parameter_points(setup: SetupLike, samples: int = _SAMPLES) -> list[tuple[float, float]]:
    """The (inner, outer) parameter values on a grid over the region.

    `s` runs over the outer interval and `t` from the inner lower to the inner
    upper bound, exactly as the browser does it.
    """
    (inner, inner_low, inner_high), (outer, outer_low, outer_high) = setup.bounds
    low = _numeric((outer,), inner_low)
    high = _numeric((outer,), inner_high)
    a, b = float(outer_low), float(outer_high)
    points = []
    for i in range(samples):
        u = a + (b - a) * i / (samples - 1)
        g, h = low(u), high(u)
        for j in range(samples):
            points.append((g + (h - g) * j / (samples - 1), u))
    return points


def to_xy(setup: SetupLike, inner: float, outer: float) -> tuple[float, float]:
    values = {str(setup.bounds[0][0]): inner, str(setup.bounds[1][0]): outer}
    if setup.system == "polar":
        return values["r"] * math.cos(values["theta"]), values["r"] * math.sin(values["theta"])
    return values["x"], values["y"]


def _interval(values: list[float], *, margin: float, include_zero: bool = False) -> list[float]:
    finite = [v for v in values if math.isfinite(v)]
    low, high = min(finite), max(finite)
    if include_zero:
        low, high = min(low, 0.0), max(high, 0.0)
    if high - low < 1e-9:
        low, high = low - 1, high + 1
    return [round(low - margin, 4), round(high + margin, 4)]


def region2d(exercise: Exercise) -> dict[str, Any]:
    return region2d_setup(solution_setup(exercise.record))


def region2d_setup(setup: SetupLike) -> dict[str, Any]:
    """Render the typed solution setup shared by native and old records."""
    if len(setup.bounds) != 2 or setup.system not in ("cartesian", "polar"):
        raise ValueError("region2d needs a two-level Cartesian or polar set-up")
    (inner, _, _), (outer, _, _) = setup.bounds
    f = _numeric((inner, outer), setup.integrand)
    params = parameter_points(setup)
    xy = [to_xy(setup, v, u) for v, u in params]
    xs, ys = [p[0] for p in xy], [p[1] for p in xy]
    side = max(max(xs) - min(xs), max(ys) - min(ys))
    margin = _MARGIN * side
    heights = [f(v, u) for v, u in params]
    # The floor z = 0 is always in view, so the surface stands over the region.
    z_window = _interval(heights, margin=0.0, include_zero=True)
    return {
        "kind": KIND,
        "system": setup.system,
        "bounds": [
            [str(variable), to_tree(lower), to_tree(upper)]
            for variable, lower, upper in setup.bounds
        ],
        "f": to_tree(setup.integrand),
        "window": {
            "x": _interval(xs, margin=margin),
            "y": _interval(ys, margin=margin),
            "z": z_window,
        },
        "region": bounds_latex(setup),
    }
