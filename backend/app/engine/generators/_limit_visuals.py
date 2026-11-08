"""Solution-only plots for limit and continuity families with geometric results."""

import math
from collections.abc import Callable
from typing import Any

from app.engine.blocks.analysis_one import bisect_exp
from app.engine.generators import _function_limits as forms
from app.engine.generators._elementary_common import Built

Path = dict[str, Any]
Point = dict[str, Any]


def path(label: str, lo: float, hi: float, f: Callable[[float], float]) -> Path:
    xs = [lo + (hi - lo) * i / 31 for i in range(32)]
    return {"label": label, "points": [[x, f(x)] for x in xs]}


def point(label: str, x: float, y: float, *, included: bool) -> Point:
    return {"label": label, "x": x, "y": y, "included": included}


def plot(
    title: str, description: str, paths: list[Path], points: list[Point] | None = None
) -> dict[str, Any]:
    markers = points or []
    coords = [p for line in paths for p in line["points"]]
    coords.extend([p["x"], p["y"]] for p in markers)
    xs, ys = zip(*coords, strict=True)
    xpad = (max(xs) - min(xs)) * 0.06
    ypad = (max(ys) - min(ys)) * 0.08 or 1.0
    return {
        "kind": "plot2d",
        "version": 1,
        "title": title,
        "description": description,
        "x": [min(xs) - xpad, max(xs) + xpad],
        "y": [min(ys) - ypad, max(ys) + ypad],
        "xLabel": "x",
        "yLabel": "y",
        "paths": paths,
        "points": markers,
    }


def absolute_jump(a: int, b: int, c: int) -> dict[str, Any]:
    return plot(
        "One-sided limits",
        "Open markers show the two distinct limit values. The function is undefined at the join.",
        [
            path("Left branch", c - 3, c, lambda _: float(b - a)),
            path("Right branch", c, c + 3, lambda _: float(b + a)),
        ],
        [
            point("Left limit", c, b - a, included=False),
            point("Right limit", c, b + a, included=False),
        ],
    )


def essential_exponential(a: int, b: int, c: int) -> dict[str, Any]:
    stop = c + a / 3
    return plot(
        "One-sided exponential limits",
        "The left branch approaches the open marker. The right branch grows without bound.",
        [
            path(
                "Left branch",
                c - a * 3,
                c,
                lambda x: b + math.exp(a / (x - c)) if x != c else float(b),
            ),
            path("Right branch", stop, c + a * 3, lambda x: b + math.exp(a / (x - c))),
        ],
        [point("Left limit", c, b, included=False)],
    )


def asymptote_rational(a: int, b: int, c: int) -> dict[str, Any]:
    extent = b + 5
    gap = min(0.2, c / (4 * b))

    def line(x: float) -> float:
        return a * x + b

    def f(x: float) -> float:
        return line(x) + c / (x * x - b * b)

    return plot(
        "Vertical and oblique asymptotes",
        "The plotted branches end before the poles. The vertical lines mark both poles.",
        [
            path("Left branch", -extent, -b - gap, f),
            path("Middle branch", -b + gap, b - gap, f),
            path("Right branch", b + gap, extent, f),
            path("Oblique asymptote", -extent, extent, line),
            {
                "label": "Left vertical asymptote",
                "points": [[-b, -a * extent], [-b, a * extent + b]],
            },
            {
                "label": "Right vertical asymptote",
                "points": [[b, -a * extent], [b, a * extent + b]],
            },
        ],
    )


def asymptote_inverse_trig(a: int, b: int, c: int) -> dict[str, Any]:
    left, right = c - 10, c + 10
    return plot(
        "Distinct oblique asymptotes",
        "The branch approaches a different line in each direction.",
        [
            path("Function", left, right, lambda x: a * x + b * math.atan(x - c)),
            path("Left asymptote", left, c, lambda x: a * x - b * math.pi / 2),
            path("Right asymptote", c, right, lambda x: a * x + b * math.pi / 2),
        ],
    )


def continuity_sine(a: int, b: int, c: int) -> dict[str, Any]:
    join = math.pi / (2 * b)
    return plot(
        "Continuous sine join",
        "The three branches meet at the two included points for the computed parameters.",
        [
            path("Left branch", -2, 0, lambda _: float(a)),
            path("Sine branch", 0, join, lambda x: a + c * math.sin(b * x)),
            path("Right branch", join, join + 2, lambda _: float(a + c)),
        ],
        [
            point("First join", 0, a, included=True),
            point("Second join", join, a + c, included=True),
        ],
    )


def continuity_reciprocal(a: int, b: int, c: int) -> dict[str, Any]:
    parameter = b * (a - c - b)
    return plot(
        "Continuous reciprocal join",
        "The left and right branches meet at the included point.",
        [
            path("Reciprocal branch", -b - 4, -b, lambda x: a + parameter / x),
            path("Linear branch", -b, 3 - b, lambda x: c - x),
        ],
        [point("Join", -b, b + c, included=True)],
    )


def discontinuity_arctan(a: int, b: int, c: int) -> dict[str, Any]:
    return plot(
        "Jump discontinuity",
        "The open markers are the one-sided limits. The filled marker is the function value.",
        [
            path(
                "Left branch",
                c - 4,
                c,
                lambda x: b - a * math.pi / 2 if x == c else b + a * math.atan(1 / (x - c)),
            ),
            path(
                "Right branch",
                c,
                c + 4,
                lambda x: b + a * math.pi / 2 if x == c else b + a * math.atan(1 / (x - c)),
            ),
        ],
        [
            point("Left limit", c, b - a * math.pi / 2, included=False),
            point("Right limit", c, b + a * math.pi / 2, included=False),
            point("Assigned value", c, b, included=True),
        ],
    )


def discontinuity_oscillatory(a: int, b: int, c: int) -> dict[str, Any]:
    points = [point("Assigned value", b, b, included=True)]
    for sign in (-1, 1):
        for k in range(1, 7):
            points.extend(
                (
                    point(
                        "Upper subsequence", b + sign * c / (2 * k * math.pi), b + a, included=True
                    ),
                    point(
                        "Lower subsequence",
                        b + sign * c / ((2 * k + 1) * math.pi),
                        b - a,
                        included=True,
                    ),
                )
            )
    return plot(
        "Oscillation near the join",
        "Samples from both sides reach two different heights arbitrarily close to the join.",
        [],
        points,
    )


def certified_root(a: int, b: int, c: int) -> dict[str, Any]:
    mid, intervals = bisect_exp(a)
    lo, hi = (float(c + b * t) for t in intervals[-1])

    def residual(x: float) -> float:
        t = (x - c) / b
        return math.exp(t) + t * t - (a + 1)

    width = hi - lo
    return plot(
        "Certified root bracket",
        "The residual crosses zero inside the marked bracket. The midpoint is the approximation.",
        [
            path("Residual", lo - width, hi + width, residual),
            {"label": "Certified interval", "points": [[lo, 0], [hi, 0]]},
        ],
        [
            point("Lower endpoint", lo, 0, included=True),
            point("Upper endpoint", hi, 0, included=True),
            point("Midpoint", float(c + b * mid), 0, included=True),
        ],
    )


def two_sided_absolute(a: int, b: int, c: int) -> dict[str, Any]:
    return plot(
        "Equal one-sided limits",
        "The two branches approach the same open point.",
        [
            path("Left branch", c - 3, c, lambda x: b + a * (c - x)),
            path("Right branch", c, c + 3, lambda x: b + a * (x - c)),
        ],
        [point("Limit", c, b, included=False)],
    )


def horizontal_asymptote(a: int, b: int, c: int) -> dict[str, Any]:
    return plot(
        "Horizontal asymptotes",
        "At the left and right ends the function approaches the marked constant lines.",
        [
            path("Function", -6, 6, lambda x: a + b - a / (math.exp(c * x) + 1)),
            path("Left asymptote", -6, 0, lambda _: float(b)),
            path("Right asymptote", 0, 6, lambda _: float(a + b)),
        ],
    )


def discontinuity_removable(a: int, b: int, c: int) -> dict[str, Any]:
    return plot(
        "Removable discontinuity",
        "The assigned value differs from the common limit at the hole.",
        [path("Linear branch", c - 2, c + 2, lambda x: a * (x + c))],
        [
            point("Common limit", c, 2 * a * c, included=False),
            point("Assigned value", c, 2 * a * c + b, included=True),
        ],
    )


def discontinuity_infinite(a: int, b: int, c: int) -> dict[str, Any]:
    return plot(
        "Infinite discontinuity",
        "Both branches grow without bound at the pole. The filled marker is the assigned value.",
        [
            path("Left branch", c - 4, c - 0.4, lambda x: a / (x - c) ** 2 + b),
            path("Right branch", c + 0.4, c + 4, lambda x: a / (x - c) ** 2 + b),
        ],
        [point("Assigned value", c, b, included=True)],
    )


def certified_cubic(a: int, b: int, c: int) -> dict[str, Any]:
    left, right = forms.cubic_brackets(a, b)[-1]
    lo, hi = float(c + left), float(c + right)
    mid = (lo + hi) / 2
    pad = max(hi - lo, 0.1)
    return plot(
        "Certified cubic root",
        "The function crosses zero within the marked interval.",
        [path("Polynomial", lo - pad, hi + pad, lambda x: (x - c) ** 3 + (b + 1) * (x - c) - a)],
        [
            point("Lower endpoint", lo, 0, included=True),
            point("Upper endpoint", hi, 0, included=True),
            point("Midpoint", mid, 0, included=True),
        ],
    )


def radical_asymptote(a: int, b: int, c: int) -> dict[str, Any]:
    def f(x: float) -> float:
        return c + a * (x - b) / math.sqrt(x * x - b * b)

    extent = b + 12
    return plot(
        "Radical domain endpoints",
        "The negative endpoint is a pole. The open marker is the finite positive-endpoint limit.",
        [
            path("Left branch", -extent, -b - 0.2, f),
            path("Right branch", b + 0.02, extent, f),
            path("Left asymptote", -extent, 0, lambda _: float(c - a)),
            path("Right asymptote", 0, extent, lambda _: float(c + a)),
            {"label": "Vertical asymptote", "points": [[-b, f(-b - 0.2)], [-b, c + a + 1]]},
        ],
        [point("Finite limit", b, c, included=False)],
    )


def high_order_pole(a: int, b: int, c: int) -> dict[str, Any]:
    def f(x: float) -> float:
        return a * x - c + (a + b) / (x - b) ** (2 * (c + 1))

    return plot(
        "Even-order pole",
        "Both branches rise at the pole and approach the oblique line at infinity.",
        [
            path("Left branch", b - 6, b - 0.85, f),
            path("Right branch", b + 0.85, b + 6, f),
            path("Oblique asymptote", b - 6, b + 6, lambda x: a * x - c),
            {
                "label": "Vertical asymptote",
                "points": [[b, a * (b - 6) - c], [b, max(f(b - 0.85), f(b + 0.85))]],
            },
        ],
    )


def continuity_free_parameter(a: int, b: int, c: int) -> dict[str, Any]:
    return plot(
        "Continuity with a free parameter",
        "The displayed right branch uses q=0. Every q gives the same value at the join.",
        [
            path("Quadratic branch", -a - 2, -a, lambda x: c - b * x * x / a),
            path("Linear branch", -a, 0, lambda x: b * x + c),
            path("Cubic branch for q=0", 0, 2, lambda x: x**3 + c),
        ],
        [
            point("First join", -a, c - a * b, included=True),
            point("Second join", 0, c, included=True),
        ],
    )


def discontinuity_pole_and_hole(a: int, b: int, c: int) -> dict[str, Any]:
    def f(x: float) -> float:
        return c / (x + a)

    return plot(
        "A pole and a hole",
        "The pole separates the branches. At the hole the assigned value differs from the limit.",
        [
            path("Left of pole", -a - 4, -a - 0.3, f),
            path("Between pole and hole", -a + 0.3, b, f),
            path("Right of hole", b, b + 4, f),
        ],
        [
            point("Assigned value at pole", -a, 0, included=True),
            point("Limit at hole", b, f(b), included=False),
            point("Assigned value at hole", b, 0, included=True),
        ],
    )


def unique_log_exponential_root(a: int, b: int, c: int) -> dict[str, Any]:
    base, coefficient = b + 1, c + 1
    root = base ** (1 + a % 2)
    target = coefficient * root + 2 + a % 2
    return plot(
        "Unique positive root",
        "A strictly increasing function crosses the target at the marked point.",
        [
            path(
                "Function",
                root / 4,
                root * 2,
                lambda x: coefficient * x + math.log(x, base) + math.exp(x / root - 1),
            ),
            path("Target", root / 4, root * 2, lambda _: float(target)),
        ],
        [point("Root", root, target, included=True)],
    )


def rational_pole_and_domain(a: int, b: int, c: int) -> dict[str, Any]:
    def f(x: float) -> float:
        return a * x - c + b / (x - c)

    return plot(
        "Domain and simple pole",
        "The branches are separated by the excluded location and approach the oblique line.",
        [
            path("Left branch", c - 6, c - 0.2, f),
            path("Right branch", c + 0.2, c + 6, f),
            path("Oblique asymptote", c - 6, c + 6, lambda x: a * x - c),
            {"label": "Vertical asymptote", "points": [[c, f(c - 0.2)], [c, f(c + 0.2)]]},
        ],
    )


def exponential_pole(a: int, b: int, c: int) -> dict[str, Any]:
    def f(x: float) -> float:
        return float(b / (1 - float(a + 1) ** (c - x)))

    return plot(
        "Exponential pole and horizontal lines",
        "The branches approach different horizontal lines and diverge at the common pole.",
        [
            path("Left branch", c - 8, c - 0.3, f),
            path("Right branch", c + 0.3, c + 8, f),
            path("Left asymptote", c - 8, c, lambda _: 0.0),
            path("Right asymptote", c, c + 8, lambda _: float(b)),
            {"label": "Vertical asymptote", "points": [[c, f(c - 0.3)], [c, f(c + 0.3)]]},
        ],
    )


diagrams: dict[Callable[[int, int, int], Built], Callable[[int, int, int], dict[str, Any]]] = {
    forms.absolute_jump: absolute_jump,
    forms.essential_exponential: essential_exponential,
    forms.asymptote_rational: asymptote_rational,
    forms.asymptote_inverse_trig: asymptote_inverse_trig,
    forms.continuity_sine: continuity_sine,
    forms.continuity_reciprocal: continuity_reciprocal,
    forms.discontinuity_arctan: discontinuity_arctan,
    forms.discontinuity_oscillatory: discontinuity_oscillatory,
    forms.certified_root: certified_root,
    forms.two_sided_absolute: two_sided_absolute,
    forms.horizontal_asymptote: horizontal_asymptote,
    forms.discontinuity_removable: discontinuity_removable,
    forms.discontinuity_infinite: discontinuity_infinite,
    forms.certified_cubic: certified_cubic,
    forms.radical_asymptote: radical_asymptote,
    forms.high_order_pole: high_order_pole,
    forms.continuity_free_parameter: continuity_free_parameter,
    forms.discontinuity_pole_and_hole: discontinuity_pole_and_hole,
    forms.unique_log_exponential_root: unique_log_exponential_root,
    forms.rational_pole_and_domain: rational_pole_and_domain,
    forms.exponential_pole: exponential_pole,
}
