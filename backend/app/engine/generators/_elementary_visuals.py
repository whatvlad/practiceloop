"""Private inverse curves, with the inverse obtained by reflecting the same points."""

import math
from typing import Any

from app.engine.generators._elementary_common import ElementaryParams


def inverse_diagram(template: str, params: ElementaryParams) -> dict[str, Any]:
    a, b, c, v = params.a, params.b, params.c, params.variant
    curves: list[list[list[float]]] = []
    closed: list[list[float]] = []
    continuation = False

    def grid(lo: float, hi: float, count: int = 40) -> list[float]:
        return [lo + (hi - lo) * i / (count - 1) for i in range(count)]

    if template == "inverse-mobius":
        extent = float(max(a + b + 4, b + 4, 6))
        for left, right in (
            (-extent, b - (a + b) / (extent + 1)),
            (b + (a + b) / (extent - 1), extent),
        ):
            curves.append([[x, (x + a) / (x - b)] for x in grid(left, right, 32)])
    elif template == "inverse-quadratic-branch":
        direction = 1 if v % 2 else -1
        curves.append([[a + direction * t, t * t - b] for t in grid(0.0, 2.0)])
        closed.append(curves[0][0])
        continuation = True
        extent = float(max(a + 3, b + 3, 6))
    elif template == "inverse-negative-fourth":
        curves.append([[-t, -a * t**4] for t in grid(0.0, (16 / a) ** 0.25)])
        closed.append(curves[0][0])
        continuation = True
        extent = 18.0
    elif template == "inverse-semicircle-branch":
        curves.append([[x, b - math.sqrt(max(0.0, a * a - x * x))] for x in grid(float(-a), 0.0)])
        closed.extend((curves[0][0], curves[0][-1]))
        extent = float(max(a, b) + 2)
    elif template == "inverse-exponential":
        extent = float(max(b + 3, 6))
        logarithm = math.log(c + 1) if v % 2 else 1.0
        end = min(extent, (b + math.log(extent) / logarithm) / a)
        curves.append([[x, math.exp((a * x - b) * logarithm)] for x in grid(-extent, end)])
    elif template == "inverse-logarithm":
        extent = float(max(a + 3, 6))
        end = min(extent, math.log(extent + a) / math.log(b + 1))
        curves.append([[(b + 1) ** y - a, y] for y in grid(-extent, end)])
    else:
        raise ValueError(template)
    paths: list[dict[str, Any]] = [
        {"label": "y=x", "points": [[-extent, -extent], [extent, extent]]}
    ]
    for index, curve in enumerate(curves, 1):
        paths.extend(
            (
                {"label": f"Function branch {index}", "points": curve, "arrow": continuation},
                {
                    "label": f"Inverse branch {index}",
                    "points": [[y, x] for x, y in curve],
                    "arrow": continuation,
                },
            )
        )
    points: list[dict[str, Any]] = []
    for x, y in closed:
        points.extend(
            (
                {"label": "Function included endpoint", "x": x, "y": y, "included": True},
                {"label": "Inverse included endpoint", "x": y, "y": x, "included": True},
            )
        )
    return {
        "kind": "plot2d",
        "version": 1,
        "title": "Function and its inverse",
        "description": (
            "Each inverse point reflects its original across y=x. "
            "Arrows and unmarked ends indicate continuation."
        ),
        "x": [-extent, extent],
        "y": [-extent, extent],
        "xLabel": "x",
        "yLabel": "y",
        "paths": paths,
        "points": points,
    }
