"""Static worksheet graphs from ADR-006 visual specs (#130, ADR-007 amendment).

pdfTeX draws them without any TeX package: lines and fills are raw PDF operators
in `\\pdfliteral`, and labels are LaTeX placed with the picture environment of the
LaTeX kernel. Every number comes from the server-built spec and every label from
the spec's server-generated LaTeX, so nothing a user typed reaches the page.

The kinds follow the site's views: `definite` (the curve and the shaded area),
`indefinite` (f and an antiderivative with the marked points), `region2d` (the
region in the plane; the 3D surface stays online) and `solid3d` (a wireframe of
the solid in a fixed oblique view).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Sequence
from typing import Any

from app.visuals.expression import Tree, evaluate

Point = tuple[float, float]

# Picture size in bp (1/72 in) and the inset of the plot area for tick labels.
WIDTH, HEIGHT = 230.0, 145.0
_LEFT, _BOTTOM, _RIGHT, _TOP = 22.0, 14.0, 12.0, 10.0
_SAMPLES = 241
_TICKS = 6
_KAPPA = 0.5523  # Bezier handle length of a quarter circle
_VIEW_AZIMUTH = math.radians(35)
_VIEW_ELEVATION = math.radians(25)


def _n(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def _tick_label(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return str(round(value))
    return f"{value:.3g}"


def nice_ticks(low: float, high: float, target: int = _TICKS) -> list[float]:
    """Round tick positions inside [low, high]: steps of 1, 2 or 5 times a power of ten."""
    span = high - low
    if not (math.isfinite(span) and span > 0):
        return []
    magnitude = 10 ** math.floor(math.log10(span / target))
    # The 1, 2 or 5 step whose tick count is closest to the target.
    steps = [m * magnitude for m in (1, 2, 5, 10)]
    step = min(steps, key=lambda size: abs(span / size - target))
    first = math.ceil(low / step - 1e-9)
    ticks = []
    k = first
    while k * step <= high + 1e-9 * step:
        ticks.append(round(k * step, 10) + 0.0)
        k += 1
    return ticks


class Canvas:
    """A plot area mapping a data window onto the picture, collecting PDF operators and labels."""

    def __init__(
        self,
        x: Sequence[float],
        y: Sequence[float],
        *,
        width: float = WIDTH,
        height: float = HEIGHT,
        equal: bool = False,
        inset: tuple[float, float, float, float] = (_LEFT, _BOTTOM, _RIGHT, _TOP),
    ) -> None:
        self.width, self.height = width, height
        left, bottom, right, top = inset
        self.box = (left, bottom, width - right, height - top)
        x0, x1 = float(x[0]), float(x[1])
        y0, y1 = float(y[0]), float(y[1])
        if not (x1 > x0 and y1 > y0):
            raise ValueError("Empty window")
        if equal:
            # One unit is the same length on both axes; the window grows to fill the box.
            scale = min((self.box[2] - left) / (x1 - x0), (self.box[3] - bottom) / (y1 - y0))
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            hx, hy = (self.box[2] - left) / scale / 2, (self.box[3] - bottom) / scale / 2
            x0, x1, y0, y1 = cx - hx, cx + hx, cy - hy, cy + hy
        self.x, self.y = (x0, x1), (y0, y1)
        self._ops: list[str] = []
        self._labels: list[str] = []

    # Coordinates

    def px(self, x: float) -> float:
        left, _, right, _ = self.box
        return left + (x - self.x[0]) / (self.x[1] - self.x[0]) * (right - left)

    def py(self, y: float) -> float:
        _, bottom, _, top = self.box
        return bottom + (y - self.y[0]) / (self.y[1] - self.y[0]) * (top - bottom)

    def _clamp(self, y: float) -> float:
        span = self.y[1] - self.y[0]
        return min(max(y, self.y[0] - 4 * span), self.y[1] + 4 * span)

    # Drawing

    def op(self, text: str) -> None:
        self._ops.append(text)

    def path(self, points: Iterable[Point | None], *, close: bool = False) -> str:
        """`m`/`l` operators; None, or a jump across the window, starts a new piece."""
        parts: list[str] = []
        previous: Point | None = None
        for point in points:
            if point is None or not all(math.isfinite(v) for v in point):
                previous = None
                continue
            x, y = point[0], self._clamp(point[1])
            jump = previous is not None and (
                (previous[1] > self.y[1] and y < self.y[0])
                or (previous[1] < self.y[0] and y > self.y[1])
            )
            verb = "m" if previous is None or jump else "l"
            parts.append(f"{_n(self.px(x))} {_n(self.py(y))} {verb}")
            previous = (x, y)
        if close and parts:
            parts.append("h")
        return " ".join(parts)

    def stroke(self, points: Iterable[Point | None], *, width: float = 0.9, dash: str = "",
               gray: float = 0.0, clip: bool = True) -> None:  # fmt: skip
        body = self.path(points)
        if not body:
            return
        self.op("q " + (self._clip() if clip else ""))
        self.op(f"{_n(gray)} G {_n(width)} w 1 J 1 j [{dash}] 0 d {body} S Q")

    def fill(self, points: Iterable[Point | None], *, gray: float = 0.82,
             outline: float | None = None) -> None:  # fmt: skip
        body = self.path(points, close=True)
        if not body:
            return
        paint = "f" if outline is None else f"{_n(outline)} w 0 G 1 j B"
        self.op(f"q {self._clip()}{_n(gray)} g {body} {paint} Q")

    def dot(self, x: float, y: float, *, radius: float = 1.8, hollow: bool = False) -> None:
        if not (self.x[0] <= x <= self.x[1] and self.y[0] <= y <= self.y[1]):
            return
        cx, cy, r, k = self.px(x), self.py(y), radius, radius * _KAPPA
        curve = (
            f"{_n(cx + r)} {_n(cy)} m "
            f"{_n(cx + r)} {_n(cy + k)} {_n(cx + k)} {_n(cy + r)} {_n(cx)} {_n(cy + r)} c "
            f"{_n(cx - k)} {_n(cy + r)} {_n(cx - r)} {_n(cy + k)} {_n(cx - r)} {_n(cy)} c "
            f"{_n(cx - r)} {_n(cy - k)} {_n(cx - k)} {_n(cy - r)} {_n(cx)} {_n(cy - r)} c "
            f"{_n(cx + k)} {_n(cy - r)} {_n(cx + r)} {_n(cy - k)} {_n(cx + r)} {_n(cy)} c h"
        )
        paint = "1 g 0 G 0.7 w B" if hollow else "0 g f"
        self.op(f"q {curve} {paint} Q")

    def label(self, x: float, y: float, latex: str, anchor: str, *, raw: bool = False) -> None:
        """LaTeX math at a point (`raw`: in picture units); `anchor` is a makebox position."""
        px, py = (x, y) if raw else (self.px(x), self.py(y))
        self._labels.append(
            f"\\put({_n(px)},{_n(py)}){{\\makebox(0,0)[{anchor}]{{\\scriptsize${latex}$}}}}"
        )

    def _clip(self) -> str:
        left, bottom, right, top = self.box
        return f"{_n(left)} {_n(bottom)} {_n(right - left)} {_n(top - bottom)} re W n "

    # Axes

    def axes(self, x_name: str = "x", y_name: str = "y") -> None:
        """Axes through 0 when 0 is in view, else along the edge; ticks with their values."""
        left, bottom, right, top = self.box
        on_x = self.y[0] <= 0 <= self.y[1]
        on_y = self.x[0] <= 0 <= self.x[1]
        ay = self.py(0) if on_x else bottom
        ax = self.px(0) if on_y else left
        self.op(f"q 0 G 0.5 w {_n(left)} {_n(ay)} m {_n(right + 4)} {_n(ay)} l S")
        self.op(f"{_n(ax)} {_n(bottom)} m {_n(ax)} {_n(top + 4)} l S")
        # Arrow heads
        self.op(
            f"0 g {_n(right + 6)} {_n(ay)} m {_n(right + 2)} {_n(ay + 1.6)} l "
            f"{_n(right + 2)} {_n(ay - 1.6)} l h f"
        )
        self.op(
            f"{_n(ax)} {_n(top + 6)} m {_n(ax - 1.6)} {_n(top + 2)} l "
            f"{_n(ax + 1.6)} {_n(top + 2)} l h f Q"
        )
        self.label(right + 7, ay, x_name, "l", raw=True)
        self.label(ax + 3, top + 6, y_name, "l", raw=True)
        ticks = ["q 0 G 0.4 w"]
        for t in nice_ticks(*self.x):
            if on_y and abs(t) < 1e-12:
                continue
            ticks.append(f"{_n(self.px(t))} {_n(ay - 1.8)} m {_n(self.px(t))} {_n(ay + 1.8)} l")
            self.label(self.px(t), ay - 2.5, _tick_label(t), "t", raw=True)
        for t in nice_ticks(*self.y):
            if on_x and abs(t) < 1e-12:
                continue
            ticks.append(f"{_n(ax - 1.8)} {_n(self.py(t))} m {_n(ax + 1.8)} {_n(self.py(t))} l")
            self.label(ax - 2.5, self.py(t), _tick_label(t), "r", raw=True)
        if on_x and on_y:
            self.label(ax - 2, ay - 2.5, "0", "tr", raw=True)
        self.op(" ".join(ticks) + " S Q")

    def tex(self) -> str:
        literal = "\\put(0,0){\\pdfliteral{" + " ".join(self._ops) + "}}\n"
        return (
            "{\\setlength{\\unitlength}{1bp}"
            f"\\begin{{picture}}({_n(self.width)},{_n(self.height)})\n"
            + literal
            + "\n".join(self._labels)
            + "\n\\end{picture}}"
        )


def _curve(tree: Tree, low: float, high: float, count: int = _SAMPLES) -> list[Point | None]:
    points: list[Point | None] = []
    for i in range(count):
        x = low + (high - low) * i / (count - 1)
        y = evaluate(tree, {"x": x})
        points.append((x, y) if math.isfinite(y) else None)
    return points


def _caption(text: str, width: float = WIDTH) -> str:
    return f"\\par\\parbox{{{_n(width)}bp}}{{\\footnotesize\\centering {text}\\par}}"


def definite(spec: dict[str, Any]) -> str:
    a, b = float(spec["a"]), float(spec["b"])
    # A row under the plot names the bounds, clear of the tick labels.
    canvas = Canvas(spec["range"], spec["y"], inset=(_LEFT, 24.0, _RIGHT, _TOP))
    f = spec["f"]
    area: list[Point | None] = [(a, 0.0)]
    area += [p for p in _curve(f, a, b, 121) if p is not None]
    area.append((b, 0.0))
    canvas.fill(area)
    canvas.axes()
    canvas.stroke(_curve(f, *canvas.x))
    for value, latex in ((a, spec["aLatex"]), (b, spec["bLatex"])):
        top = evaluate(f, {"x": value})
        canvas.stroke([(value, 0.0), (value, top)], width=0.5, dash="2 1.5")
        canvas.label(canvas.px(value), canvas.box[1] - 12, f"x={latex}", "t", raw=True)
    return canvas.tex() + _caption(
        "The shaded area between $y = f(x)$ and the $x$-axis is the integral; "
        "parts below the axis count as negative."
    )


def indefinite(spec: dict[str, Any]) -> str:
    canvas = Canvas(spec["x"], spec["y"])
    f, big_f = spec["f"], spec["F"]
    canvas.axes()
    canvas.stroke(_curve(f, *canvas.x), width=1.0)
    canvas.stroke(_curve(big_f, *canvas.x), width=1.0, dash="4 2", gray=0.35)
    for point in spec.get("points", []):
        x, kind = float(point["x"]), point["kind"]
        if kind == "zero":
            canvas.dot(x, 0.0)
        elif kind == "extremum":
            canvas.dot(x, evaluate(big_f, {"x": x}), hollow=True)
        elif kind == "inflection":
            canvas.dot(x, evaluate(big_f, {"x": x}), radius=1.4, hollow=True)
        elif kind == "pole":
            canvas.stroke([(x, canvas.y[0]), (x, canvas.y[1])], width=0.4, dash="1 1.5")
    return canvas.tex() + _caption(
        "Solid: the integrand $f(x)$. Dashed: the antiderivative $F(x)$ with $C = 0$. "
        "Filled dots: zeros of $f$; open dots: extrema and inflection points of $F$."
    )


def _xy(system: str, values: dict[str, float]) -> Point:
    if system in ("polar", "cylindrical"):
        return values["r"] * math.cos(values["theta"]), values["r"] * math.sin(values["theta"])
    return values["x"], values["y"]


def _loop(inner: Sequence[Any], outer: Sequence[Any], count: int = 61) -> list[dict[str, float]]:
    """Parameter values around the region's boundary: inner low edge, outer end,
    inner high edge back, outer start. `inner` bounds are functions of the outer variable."""
    (v_name, v_low, v_high), (u_name, u_low, u_high) = inner, outer
    a, b = evaluate(u_low, {}), evaluate(u_high, {})
    if not (math.isfinite(a) and math.isfinite(b)):
        raise ValueError("Outer bounds must be numbers")

    def at(u: float, edge: Tree) -> dict[str, float]:
        return {u_name: u, v_name: evaluate(edge, {u_name: u})}

    def across(u: float, forward: bool) -> list[dict[str, float]]:
        g, h = evaluate(v_low, {u_name: u}), evaluate(v_high, {u_name: u})
        steps = range(count) if forward else range(count - 1, -1, -1)
        return [{u_name: u, v_name: g + (h - g) * j / (count - 1)} for j in steps]

    us = [a + (b - a) * i / (count - 1) for i in range(count)]
    return (
        [at(u, v_low) for u in us]
        + across(b, True)
        + [at(u, v_high) for u in reversed(us)]
        + across(a, False)
    )


def region2d(spec: dict[str, Any]) -> str:
    inner, outer = spec["bounds"]
    boundary = [_xy(spec["system"], values) for values in _loop(inner, outer)]
    window = spec["window"]
    canvas = Canvas(window["x"], window["y"], equal=True)
    canvas.fill(boundary, gray=0.82, outline=0.8)
    canvas.axes()
    return canvas.tex() + _caption(
        "The region of integration $D$ in the $xy$-plane; the integral adds $f$ over it."
    )


def _project(x: float, y: float, z: float) -> Point:
    sa, ca = math.sin(_VIEW_AZIMUTH), math.cos(_VIEW_AZIMUTH)
    return (
        y * ca - x * sa,
        z * math.cos(_VIEW_ELEVATION) - (x * ca + y * sa) * math.sin(_VIEW_ELEVATION),
    )


def solid3d(spec: dict[str, Any]) -> str:
    (z_name, z_low, z_high), middle, outer = spec["bounds"]
    system = spec["system"]

    def corner(values: dict[str, float], edge: Tree) -> tuple[float, float, float]:
        x, y = _xy(system, values)
        return x, y, evaluate(edge, {**values, "x": x, "y": y})

    loop = _loop(middle, outer)
    bottom = [corner(v, z_low) for v in loop]
    top = [corner(v, z_high) for v in loop]
    # Top-surface grid: lines of constant outer and constant middle parameter.
    (m_name, m_low, m_high), (u_name, u_low, u_high) = middle, outer
    a, b = evaluate(u_low, {}), evaluate(u_high, {})
    grid: list[list[tuple[float, float, float]]] = []
    for i in range(1, 5):
        u = a + (b - a) * i / 5
        g, h = evaluate(m_low, {u_name: u}), evaluate(m_high, {u_name: u})
        grid.append([corner({u_name: u, m_name: g + (h - g) * j / 30}, z_high) for j in range(31)])
    for j in range(1, 5):
        line = []
        for i in range(31):
            u = a + (b - a) * i / 30
            g, h = evaluate(m_low, {u_name: u}), evaluate(m_high, {u_name: u})
            line.append(corner({u_name: u, m_name: g + (h - g) * j / 5}, z_high))
        grid.append(line)
    window = spec["window"]
    reach = [max(abs(v) for v in window[name]) for name in "xyz"]
    axes = [(reach[0] * 1.15, 0.0, 0.0), (0.0, reach[1] * 1.15, 0.0), (0.0, 0.0, reach[2] * 1.15)]
    flat = [_project(*p) for p in [*bottom, *top, *axes, (0.0, 0.0, 0.0)] if _finite(p)]
    xs, ys = [p[0] for p in flat], [p[1] for p in flat]
    pad_x, pad_y = 0.04 * (max(xs) - min(xs)), 0.04 * (max(ys) - min(ys))
    canvas = Canvas(
        [min(xs) - pad_x, max(xs) + pad_x],
        [min(ys) - pad_y, max(ys) + pad_y],
        height=165.0,
        equal=True,
        inset=(8.0, 8.0, 8.0, 8.0),
    )

    def flat_path(points: Iterable[tuple[float, float, float]]) -> list[Point | None]:
        return [_project(*p) if _finite(p) else None for p in points]

    origin = _project(0.0, 0.0, 0.0)
    for name, end in zip("xyz", axes, strict=True):
        tip = _project(*end)
        canvas.stroke([origin, tip], width=0.5, clip=False)
        canvas.label(tip[0], tip[1], name, {"x": "tr", "y": "l", "z": "b"}[name])
    for line in grid:
        canvas.stroke(flat_path(line), width=0.35, gray=0.55)
    canvas.stroke(flat_path(bottom), width=0.6, dash="3 2", gray=0.25)
    edges = len(loop) // 8
    for k in range(0, len(loop), max(edges, 1)):
        canvas.stroke(flat_path([bottom[k], top[k]]), width=0.45, gray=0.3)
    canvas.stroke(flat_path(top), width=1.0)
    return canvas.tex() + _caption(
        "The solid $E$ between its bottom surface (dashed) and top surface, in an oblique view."
    )


def _finite(point: Sequence[float]) -> bool:
    return all(math.isfinite(v) for v in point)


DRAWERS: dict[str, Callable[[dict[str, Any]], str]] = {
    "definite": definite,
    "indefinite": indefinite,
    "region2d": region2d,
    "solid3d": solid3d,
}


def graph(spec: dict[str, Any] | None) -> str:
    """The picture and caption for a visual spec, or "" when there is none to draw."""
    if spec is None:
        return ""
    drawer = DRAWERS.get(spec.get("kind", ""))
    if drawer is None:
        raise ValueError("Visual kind has no worksheet graph")
    return drawer(spec)
