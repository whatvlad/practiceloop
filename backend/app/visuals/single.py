"""Specs for single integrals (#112): `definite` and `indefinite` (ADR-006).

Windows and marked points are computed here with SymPy and floats, never in the
browser. Every number in a spec is a float the plot can use directly.
"""

import math
from typing import Any

import sympy as sp
from sympy.calculus.util import continuous_domain

from app.engine.answers._symbolic import X
from app.engine.blocks.integral_forms.form import IntegralData
from app.visuals.expression import Tree, evaluate, to_tree

_SAMPLES = 801
# Points closer than this fraction of the window are one point.
_SAME_POINT = 1e-6
_MAX_POINTS = 48
_MAX_SIGN_CHANGES = 8
_TOUCH = 1e-9


def _f(value: Any) -> float:
    return round(float(value), 10)


def _samples(tree: Tree, lo: float, hi: float, count: int = _SAMPLES) -> list[float]:
    return [evaluate(tree, {"x": lo + (hi - lo) * i / (count - 1)}) for i in range(count)]


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, round(q * (len(ordered) - 1))))]


def _y_window(values: list[float], keep: list[float] | None = None) -> list[float]:
    """A readable vertical window: central values, always 0, and every value in `keep`."""
    finite = [v for v in values if math.isfinite(v)]
    if not finite:
        raise ValueError("Nothing to plot")
    lo = min(0.0, _quantile(finite, 0.05))
    hi = max(0.0, _quantile(finite, 0.95))
    for value in keep or []:
        if math.isfinite(value):
            lo, hi = min(lo, value), max(hi, value)
    span = max(hi - lo, 1.0)
    return [_f(lo - 0.12 * span), _f(hi + 0.12 * span)]


def _component(integrand: Any, lower: Any, upper: Any) -> sp.Interval:
    """The interval of continuity of the integrand that contains [lower, upper]."""
    domain = continuous_domain(integrand, X, sp.S.Reals)
    parts = domain.args if isinstance(domain, sp.Union) else (domain,)
    for part in parts:
        if isinstance(part, sp.Interval) and sp.Interval(lower, upper).is_subset(part):
            return part
    raise ValueError("Bounds are not inside one interval of continuity")


def definite_data(problem: Any) -> dict[str, Any]:
    """Render already rebuilt integral data; shared by old and native records."""
    a, b = float(problem.lower), float(problem.upper)
    margin = max(1.0, (b - a) / 2)
    part = _component(problem.integrand, problem.lower, problem.upper)
    lo, hi = a - margin, b + margin
    # An open end (a pole or the edge of the domain) stays a quarter of the gap away.
    if part.start.is_finite and float(part.start) >= lo:
        lo = float(part.start) + (0.25 * (a - float(part.start)) if part.left_open else 0)
    if part.end.is_finite and float(part.end) <= hi:
        hi = float(part.end) - (0.25 * (float(part.end) - b) if part.right_open else 0)
    f = to_tree(problem.integrand)
    inside = _samples(f, a, b, 201)
    if not all(math.isfinite(v) for v in inside):
        raise ValueError("The integrand is not finite on the bounds")
    # The window fits the original area; outside the bounds the curve may leave it.
    return {
        "kind": "definite",
        "f": f,
        "a": _f(a),
        "b": _f(b),
        "aLatex": str(sp.latex(problem.lower)),
        "bLatex": str(sp.latex(problem.upper)),
        "range": [_f(lo), _f(hi)],
        "y": _y_window(inside, inside),
        "value": str(sp.latex(problem.value)),
    }


def _x_window(integrand: Any, f: Tree, primitive: Tree) -> list[float]:
    """The widest of a few symmetric windows in which f and F stay readable.

    Readable: most values are small and f does not oscillate faster than the eye
    can follow (sin(x^2 + 1) does on [-2pi, 2pi]).
    """
    periodic = integrand.has(sp.sin, sp.cos, sp.tan)
    candidates = (2 * math.pi, math.pi, 2.0, 1.5) if periodic else (4.0, 3.0, 2.0, 1.5)
    for half in candidates:
        ys = _samples(f, -half, half)
        values = ys + _samples(primitive, -half, half)
        finite = [abs(v) for v in values if math.isfinite(v)]
        changes = sum(1 for u, v in zip(ys, ys[1:], strict=False) if u * v < 0)
        if finite and _quantile(finite, 0.9) <= 40 and changes <= _MAX_SIGN_CHANGES:
            return [-half, half]
    return [-candidates[-1], candidates[-1]]


def _roots(tree: Tree, lo: float, hi: float) -> list[float]:
    """Real zeros in [lo, hi] of a tree SymPy built: sign changes refined by bisection,
    and zeros that only touch the axis (x^2 at 0) as minima of |f| that reach 0.

    Floats, not solveset: solveset takes seconds on these trigonometric forms and
    can return sets that are not finite; plotting needs only float positions.
    """
    xs = [lo + (hi - lo) * i / (_SAMPLES - 1) for i in range(_SAMPLES)]
    ys = [evaluate(tree, {"x": x}) for x in xs]
    roots: list[float] = []
    for i in range(_SAMPLES):
        if ys[i] == 0:
            roots.append(xs[i])
            continue
        if i + 1 < _SAMPLES and ys[i] * ys[i + 1] < 0:
            roots.append(_bisect(tree, xs[i], xs[i + 1], ys[i]))
        elif 0 < i < _SAMPLES - 1 and abs(ys[i]) <= min(abs(ys[i - 1]), abs(ys[i + 1])):
            x = _touch(tree, xs[i - 1], xs[i + 1])
            if abs(evaluate(tree, {"x": x})) < _TOUCH:
                roots.append(x)
    return [x + 0.0 for x in roots]


def _bisect(tree: Tree, left: float, right: float, at_left: float) -> float:
    for _ in range(60):
        middle = (left + right) / 2
        value = evaluate(tree, {"x": middle})
        if not math.isfinite(value) or value == 0:
            return middle
        if (value < 0) == (at_left < 0):
            left = middle
        else:
            right = middle
    return (left + right) / 2


def _touch(tree: Tree, left: float, right: float) -> float:
    """The minimum of |f| on a short interval around a sampled local minimum."""
    for _ in range(80):
        one, two = left + (right - left) / 3, right - (right - left) / 3
        if abs(evaluate(tree, {"x": one})) <= abs(evaluate(tree, {"x": two})):
            right = two
        else:
            left = one
    return (left + right) / 2


def _changes_sign(tree: Tree, x: float, step: float) -> bool:
    before, after = evaluate(tree, {"x": x - step}), evaluate(tree, {"x": x + step})
    return math.isfinite(before) and math.isfinite(after) and before * after < 0


def _poles(integrand: Any, lo: float, hi: float) -> list[float]:
    """Points of the window where |f| grows without bound, from SymPy's limits."""
    gaps = sp.Interval(lo, hi) - continuous_domain(integrand, X, sp.Interval(lo, hi))
    edges = gaps.boundary if not isinstance(gaps, sp.FiniteSet) else gaps
    poles = []
    for point in edges if isinstance(edges, sp.FiniteSet) else []:
        if not lo < float(point) < hi:
            continue
        sides = [sp.limit(sp.Abs(integrand), X, point, direction) for direction in ("+", "-")]
        if any(side is sp.oo for side in sides):
            poles.append(float(point))
    return sorted(poles)


def indefinite(exercise: IntegralData) -> dict[str, Any]:
    integrand, primitive = exercise.integrand, exercise.primitive
    f, big_f = to_tree(integrand), to_tree(primitive)
    lo, hi = _x_window(integrand, f, big_f)
    step = (hi - lo) * 1e-4
    points: list[dict[str, Any]] = []
    for x in _roots(f, lo, hi):
        points.append({"x": _f(x), "kind": "zero"})
        # A zero where f changes sign is an extremum of every antiderivative.
        if _changes_sign(f, x, step):
            points.append({"x": _f(x), "kind": "extremum"})
    derivative = sp.diff(integrand, X)
    tree = to_tree(derivative)
    points += [
        {"x": _f(x), "kind": "inflection"}
        for x in _roots(tree, lo, hi)
        if _changes_sign(tree, x, step)
    ]
    points += [{"x": _f(x), "kind": "pole"} for x in _poles(integrand, lo, hi)]
    points = _distinct(sorted(points, key=lambda p: (p["x"], p["kind"])), (hi - lo) * _SAME_POINT)
    if len(points) > _MAX_POINTS:
        raise ValueError("Too many marked points for one window")
    values = _samples(f, lo, hi) + _samples(big_f, lo, hi)
    return {
        "kind": "indefinite",
        "f": f,
        "F": big_f,
        "x": [_f(lo), _f(hi)],
        "y": _y_window(values),
        "points": points,
    }


def _distinct(points: list[dict[str, Any]], tolerance: float) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for point in points:
        if not any(
            p["kind"] == point["kind"] and abs(p["x"] - point["x"]) <= tolerance for p in kept
        ):
            kept.append(point)
    return kept
