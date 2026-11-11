"""#262: monotonicity, extrema and optimization answers against numerical scans of the statement."""

import math

import pytest
import sympy as sp
from test_engine_analysis_limits import source

from app.engine.generators.analysis_limits import generators
from app.engine.generators.catalogue import registry
from app.engine.rendering import render
from app.math_input import parse_answer_input

EXTREMA = [g for g in generators() if g.evaluate.__module__.endswith("_extrema")]
E, PI = math.e, math.pi


def ln(x):
    return math.log(x)


def safe(f):
    """None outside the real domain."""

    def g(x):
        try:
            value = f(x)
        except (ValueError, ZeroDivisionError, OverflowError):
            return None
        if value is None or isinstance(value, complex) or not math.isfinite(value):
            return None
        return value

    return g


def grid(low, high, n=8001):
    return [low + (high - low) * k / (n - 1) for k in range(n)]


def intervals(answer_set):
    """Float (open) intervals of a union of open intervals, for fast membership tests."""
    if answer_set == sp.S.EmptySet:
        return []
    parts = answer_set.args if isinstance(answer_set, sp.Union) else (answer_set,)
    return [(float(part.start), float(part.end)) for part in parts]


def contains(parts, x):
    return any(low < x < high for low, high in parts)


def monotone_case(name, a, b, c):  # noqa: PLR0911
    """f and the scan window; f is evaluated only from the statement."""
    if name == "monotone_cubic":
        p, q = a, a + 2 * b
        return lambda x: x**3 - 1.5 * (p + q) * x**2 + 3 * p * q * x, (-10, 30)
    if name == "monotone_trig_difference":
        end = 2 * PI / b
        return (
            lambda x: a * (math.sin(b * x) - math.cos(b * x)) if 0 <= x <= end else None,
            (-0.5, end + 0.5),
        )
    if name == "monotone_linear_reciprocal":
        return lambda x: a * x + b / x, (-6, 6)
    if name == "monotone_cubic_over_quadratic":
        return lambda x: x**3 / (c - x * x), (-8, 8)
    if name == "monotone_root_quotient":
        return lambda x: math.sqrt(x * x - c * c) / (a * x), (-12, 12)
    if name == "monotone_exponential_product":
        return lambda x: (x - b) * math.exp(-a * x), (-3, 10)
    if name == "monotone_log_square":
        return lambda x: x * ln(x / b) ** 2, (-1, 12)
    if name == "monotone_log_quotient":
        return lambda x: a * x / ln(x / b), (-1, 20)
    if name == "monotone_exponential_difference":
        base = a + 1
        return lambda x: c * base ** (x + 1) - (base * base) ** x, (-6, 6)
    if name == "monotone_reciprocal_log":
        return lambda x: a / x + b * ln(x), (-1, 8)
    if name == "monotone_power_log":
        return lambda x: a * x ** (b + 1) * ln(x), (-1, 3)
    raise AssertionError(name)


def extrema_case(name, a, b, c):  # noqa: PLR0911
    if name == "extrema_cubic":
        return lambda x: x**3 - a * x * x + c, (-5, 8)
    if name == "extrema_linear_reciprocal":
        return lambda x: a * x + b / x, (-6, 6)
    if name == "extrema_exponential_quotient":
        return lambda x: (a + 1) ** x / (b * x), (-5, 5)
    if name == "extrema_shifted_exponential":
        return lambda x: (x + b) * math.exp(-a * x), (-8, 8)
    if name == "extrema_rational":
        return lambda x: (x + b) / (x * x + 1), (-15, 15)
    if name == "extrema_absolute_quadratic":
        return lambda x: abs((x + a) * (x - b - c)), (-10, 15)
    if name == "extrema_x_log":
        return lambda x: a * x * ln(x / b), (-1, 12)
    if name == "extrema_root_cubic":
        edge = c * math.sqrt(3)  # zeros of the radicand 3c^2x - x^3
        return (
            lambda x: (
                a * math.sqrt(max(3 * c * c * x - x**3, 0.0))
                if 3 * c * c * x - x**3 > -1e-9
                else math.sqrt(-1)
            ),
            (-14, 14),
            (-edge, 0.0, edge),
        )
    if name == "extrema_arctan_log":
        return lambda x: a * math.atan(x) - b * ln(1 + x * x), (-10, 10)
    if name == "extrema_none":
        return lambda x: a * (math.atan(x) - x) - b * x**3, (-6, 6)
    if name == "extrema_exponential_shift":
        return lambda x: (x - b) * math.exp(a * x), (-6, 8)
    raise AssertionError(name)


def global_case(name, a, b, c):  # noqa: PLR0911
    """f and the closed interval: stated, or the natural domain found by the oracle."""
    if name == "global_cubic":
        p, q = a, a + 1
        return lambda x: 2 * x**3 - 3 * (p + q) * x * x + 6 * p * q * x, (p - 1, q + 1 + b % 2)
    if name == "global_reciprocal_quadratic":
        return lambda x: 1 / ((x - b) ** 2 + c), (b - 3, b + 1)
    if name == "global_root_difference":
        return lambda x: math.sqrt(a + x) - math.sqrt(b - x), natural(
            lambda x: math.sqrt(a + x) - math.sqrt(b - x)
        )
    if name == "global_absolute_exponential":
        k = b + 1
        return lambda x: (x - k) ** 2 * math.exp(abs(x)), (-1, k + 1)
    if name == "global_absolute_parabola":
        k = c + 1
        return lambda x: 1 - abs(k * k - x * x), (-(k + 2), 1)
    if name == "global_sine_cubic":
        m = a + 3
        return lambda x: math.sin(x) ** 3 - m * math.sin(x), (-PI / 2, PI / 2)
    if name == "global_semicircle_root":

        def f(x):
            return a * math.sqrt(c * c - (x - b) ** 2)

        return f, natural(f)
    if name == "global_cosine_quotient":
        p, q = ((5, 4), (5, 3), (13, 5), (13, 12), (17, 8))[a - 1]
        return lambda x: math.cos(x) / (p + q * math.sin(x)), (0, 2 * PI)
    if name == "global_rational_interval":
        return lambda x: a * x / (x * x - c * x + c * c), (0, 2 * c)
    if name == "global_root_product":
        r = 5 * a
        return lambda x: x * math.sqrt(r * r - x * x), (-3 * a, 4 * a)
    raise AssertionError(name)


def natural(f, low=-60.0, high=60.0):
    """The bounded natural domain of f, found by bisection on where f is defined."""
    g = safe(f)
    inside = [x for x in grid(low, high, 24001) if g(x) is not None]
    left, right = inside[0], inside[-1]
    step = (high - low) / 24000
    for _ in range(80):
        middle = (left - step + left) / 2
        if g(middle) is not None:
            left = middle
        else:
            step /= 2
    step = (high - low) / 24000
    for _ in range(80):
        middle = (right + step + right) / 2
        if g(middle) is not None:
            right = middle
        else:
            step /= 2
    return left, right


def check_monotone(answer, f, window):
    increasing, decreasing = (intervals(component.expected) for component in answer.components)
    g = safe(f)
    h = 1e-6
    for x in grid(*window, 3001):
        here, left, right = g(x), g(x - h), g(x + h)
        if None in (here, left, right):
            if here is None:
                assert not contains(increasing, x) and not contains(decreasing, x), x
            continue
        slope = (right - left) / (2 * h)
        if abs(slope) < 1e-6 or any(
            min(abs(x - e) for e in ends) < 1e-4 for ends in increasing + decreasing
        ):
            continue
        assert contains(increasing, x) == (slope > 0), (x, slope)
        assert contains(decreasing, x) == (slope < 0), (x, slope)


def scan_extrema(f, window):
    g = safe(f)
    xs = grid(*window, 20001)
    ys = [g(x) for x in xs]
    found = {"min": [], "max": []}
    for i, y in enumerate(ys):
        if y is None:
            continue
        if i in (0, len(ys) - 1) or ys[i - 1] is None or ys[i + 1] is None:
            continue  # closed domain ends are checked separately in check_extrema
        neighbours = [ys[i - 1], ys[i + 1]]
        if all(y <= n for n in neighbours) and any(y < n for n in neighbours):
            found["min"].append((xs[i], y))
        if all(y >= n for n in neighbours) and any(y > n for n in neighbours):
            found["max"].append((xs[i], y))
    return found, (window[1] - window[0]) / 20000


def check_extrema(answer, f, window, ends=()):
    min_points, min_values, max_points, max_values = (c.expected for c in answer.components)
    found, step = scan_extrema(f, window)
    g = safe(f)
    for end in ends:  # closed ends of the domain where f is defined
        near = [g(end + d) for d in (-1e-6, 1e-6)]
        values = [y for y in near if y is not None]
        if all(g(end) < y for y in values):
            found["min"].append((end, g(end)))
        elif all(g(end) > y for y in values):
            found["max"].append((end, g(end)))
    for kind, points, values in (("min", min_points, min_values), ("max", max_points, max_values)):
        claimed = sorted(float(p) for p in points)
        scanned = found[kind]
        assert len(claimed) == len(scanned), (kind, claimed, scanned)
        for p, (x, y) in zip(claimed, sorted(scanned), strict=True):
            assert abs(p - x) <= 2 * step, (kind, p, x)
            assert any(math.isclose(float(v), y, rel_tol=1e-4, abs_tol=1e-4) for v in values)
        assert len({round(float(v), 4) for v in values}) == len({round(y, 4) for _, y in scanned})


def check_global(answer, f, interval):
    g = safe(f)
    xs = [x for x in grid(*interval, 20001) if g(x) is not None]
    step = xs[1] - xs[0]
    low, high = (float(c.expected) for c in answer.components)
    for value, largest in ((low, False), (high, True)):
        sign = -1 if largest else 1
        x0 = min(xs, key=lambda x: sign * g(x))
        span = (max(x0 - step, xs[0]), min(x0 + step, xs[-1]))
        x1 = best(
            lambda x, sign=sign: g(x) if g(x) is not None else sign * math.inf,
            *span,
            largest=largest,
            n=101,
        )
        extreme = min((g(x0), g(x1)), key=lambda y: sign * y)
        assert math.isclose(value, extreme, rel_tol=1e-6, abs_tol=1e-6), (value, extreme)


def best(objective, low, high, *, largest=False, n=20001):
    """Argument of the extreme value of a unimodal objective on a grid, then golden refinement."""
    sign = -1 if largest else 1
    xs = grid(low, high, n)
    i = min(range(len(xs)), key=lambda k: sign * objective(xs[k]))
    lo, hi = xs[max(i - 1, 0)], xs[min(i + 1, len(xs) - 1)]
    ratio = (math.sqrt(5) - 1) / 2
    for _ in range(200):
        m1, m2 = hi - ratio * (hi - lo), lo + ratio * (hi - lo)
        if sign * objective(m1) < sign * objective(m2):
            hi = m2
        else:
            lo = m1
    return (lo + hi) / 2


def optimum(name, a, b, c):  # noqa: PLR0911
    if name == "fenced_plots":
        left, top, bottom = 100 * (a + 1), 100 * b, 100 * c
        total = left + top + bottom
        y = best(lambda y: 2 * total / y + 3 * y + (top + bottom) / y, 1, 500)
        return total / y, y
    if name == "pipeline":
        depth, ratio, shore = 4 + 2 * a, 2 + c % 2, 4 + 2 * a + 4 * b
        return (best(lambda x: ratio * math.hypot(depth, x) + shore - x, 0, shore),)
    if name == "container":
        side = (a + 1) / 2
        floor, wall = 10 * (b + 1), 10 * (c + 1)
        volume = floor * side**3 / wall
        s = best(lambda s: 2 * floor * s * s + 4 * wall * volume / s, 0.01, 50)
        return s, volume / (s * s)
    if name == "incircle_triangle":
        area = 3 * a * math.sqrt(3)

        def radius(alpha):
            leg = math.sqrt(2 * area / math.sin(alpha))
            return area / (leg + leg * math.sin(alpha / 2))

        alpha = best(radius, 0.01, PI - 0.01, largest=True)
        return alpha, radius(alpha)
    if name == "parabola_rectangle":
        k = c + 1
        x = best(lambda x: 2 * x * a * (k * k - x * x), 0, k, largest=True)
        return 2 * x, a * (k * k - x * x)
    if name == "semicircle_rectangle":
        r = a + 1
        x = best(lambda x: 2 * x * math.sqrt(r * r - x * x), 0, r, largest=True)
        return 2 * x, math.sqrt(r * r - x * x)
    if name == "semicircle_waste":
        r = a + 1
        x = best(lambda x: 2 * x * math.sqrt(r * r - x * x), 0, r, largest=True)
        return (PI * r * r / 2 - 2 * x * math.sqrt(r * r - x * x),)
    if name == "circle_square":
        r = a + 1
        t = best(lambda t: math.cos(t) * math.sin(t), 0, PI / 2, largest=True)
        return 2 * r * math.cos(t), 2 * r * math.sin(t)
    raise AssertionError(name)


@pytest.mark.parametrize("generator", EXTREMA, ids=lambda g: g.prefix)
def test_thousand_seeds_match_numerical_scans(generator):
    name = generator.evaluate.__name__
    seen = set()
    for seed in range(1000):
        params = generator.draw(seed)
        triple = (params.a, params.b, params.c)
        if triple in seen:
            continue
        seen.add(triple)
        task = generator.build(params)
        answer = task.answer
        if name.startswith("monotone_"):
            check_monotone(answer, *monotone_case(name, *triple))
        elif name.startswith("extrema_"):
            check_extrema(answer, *extrema_case(name, *triple))
        elif name.startswith("global_"):
            check_global(answer, *global_case(name, *triple))
        else:
            values = getattr(answer, "components", (answer,))
            for component, expected in zip(values, optimum(name, *triple), strict=True):
                assert math.isclose(float(component.expected), expected, rel_tol=1e-5), name
        contract = generator.input_contract(params)
        assert contract == answer.contract
        tree = parse_answer_input(source(answer), contract.kind, contract=contract)
        assert answer.check(tree) == "correct"
        render(task, registry())
