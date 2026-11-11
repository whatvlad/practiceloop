"""#263: convexity, joint monotonicity/convexity and polynomial data against numerical scans."""

import math

import pytest
import sympy as sp
from test_engine_analysis_limits import source
from test_engine_extrema import contains, grid, intervals, safe

from app.engine.generators.analysis_limits import generators
from app.engine.generators.catalogue import registry
from app.engine.rendering import render
from app.math_input import parse_answer_input

CONVEXITY = [g for g in generators() if g.evaluate.__module__.endswith("_convexity")]
PI = math.pi


def convex_case(name, a, b, c):  # noqa: PLR0911
    if name == "convex_cubic":
        return lambda x: a * x * (x - b) * (x - b - c), (-10, 20)
    if name == "convex_exponential_product":
        return lambda x: (x - b) * math.exp(-a * x), (-3, 10)
    if name == "convex_cubic_quotient":
        return lambda x: x**3 / (x * x + 3 * c * c), (-25, 25)
    if name == "convex_log_quadratic":
        return lambda x: a * math.log(c * c + x * x), (-12, 12)
    if name == "convex_reciprocal":
        return lambda x: a / (c * c - x * x), (-12, 12)
    if name == "convex_log_absolute":
        k = 1 + a % 2
        return lambda x: x - b * x**3 / 3 - 2 * b * k**3 * math.log(abs(x)), (-5, 5)
    if name == "convex_trig":
        end = 2 * PI / b
        return (
            lambda x: a * (math.sin(b * x) + math.sin(2 * b * x) / 8) if 0 < x < end else None,
            (-0.3, end + 0.3),
        )
    if name == "convex_exponential_arctan":
        return lambda x: math.exp(a * math.atan(x)), (-10, 10)
    if name == "convex_log_root":
        return lambda x: a * math.log(x / b) / math.sqrt(x), (-1, 200 * b)
    if name == "convex_reversed_exponential":
        return lambda x: (c - x) * math.exp(a * x), (-5, 8)
    raise AssertionError(name)


def joint_case(name, a, b, c):
    """f, window and the required signs of f' and f''."""
    if name == "increasing_convex_quadratic_exponential":
        return lambda x: (x * x + 2 * x - c) * math.exp(-x), (-6, 6), (1, 1)
    if name == "increasing_convex_root_log":
        return lambda x: a * math.sqrt(x) * math.log(x / b), (-1, 3 * b), (1, 1)
    if name == "decreasing_concave_quadratic_exponential":
        return lambda x: (x * x - 6 * x + c) * math.exp(x), (-6, 8), (-1, -1)
    if name == "increasing_concave_arccot":
        return lambda x: x**3 / 3 + c * c * (math.pi / 2 - math.atan(1 / x)), (-6, 6), (1, -1)
    raise AssertionError(name)


def second(g, x, h=1e-4):
    values = [g(x - h), g(x), g(x + h)]
    if None in values:
        return None
    return (values[0] - 2 * values[1] + values[2]) / (h * h)


def first(g, x, h=1e-6):
    values = [g(x - h), g(x + h)]
    if None in values:
        return None
    return (values[1] - values[0]) / (2 * h)


def near_edge(parts, x, tolerance=1e-3):
    return any(min(abs(x - low), abs(x - high)) < tolerance for low, high in parts)


def check_convexity(answer, f, window):
    convex_set, concave_set, points = (c.expected for c in answer.components)
    convex, concave = intervals(convex_set), intervals(concave_set)
    g = safe(f)
    xs = grid(*window, 4001)
    signs = []
    for x in xs:
        curvature = second(g, x)
        if g(x) is None:
            assert not contains(convex, x) and not contains(concave, x), x
        if curvature is None or abs(curvature) < 1e-5 or near_edge(convex + concave, x):
            signs.append((x, None))
            continue
        assert contains(convex, x) == (curvature > 0), (x, curvature)
        assert contains(concave, x) == (curvature < 0), (x, curvature)
        signs.append((x, curvature > 0))
    # Inflections: f'' changes sign around a point where f is defined on both sides.
    step = xs[1] - xs[0]
    claimed = sorted(float(p) for p in points)
    for p in claimed:
        assert g(p) is not None
        left, right = second(g, p - 50 * step), second(g, p + 50 * step)
        assert left is not None and right is not None and left * right < 0, p
    for (x0, s0), (x1, s1) in zip(signs, signs[1:], strict=False):
        if s0 is None or s1 is None or s0 == s1:
            continue
        between = [g(x0 + (x1 - x0) * k / 200) for k in range(201)]
        scale = 10 * max(abs(g(x0)), abs(g(x1)), 1.0)
        if not any(y is None or abs(y) > scale for y in between):
            assert any(x0 - step <= p <= x1 + step for p in claimed), (x0, x1)


def check_joint(answer, f, window, signs):
    parts = intervals(answer.expected)
    g = safe(f)
    for x in grid(*window, 4001):
        slope, curvature = first(g, x), second(g, x)
        if slope is None or curvature is None or near_edge(parts, x):
            assert slope is not None or not contains(parts, x), x
            continue
        if min(abs(slope), abs(curvature)) < 1e-5:
            continue
        wanted = slope * signs[0] > 0 and curvature * signs[1] > 0
        assert contains(parts, x) == wanted, (x, slope, curvature)


def check_polynomial(name, answer, a, b, c):
    p = sp.Poly(answer.expected, sp.Symbol("x", real=True))
    d1, d2 = p.diff(), p.diff().diff()
    assert p.degree() == 3
    if name == "polynomial_extrema":
        low, high = a, a + b
        assert p.LC() == -c and p.eval(0) == a + 1
        assert d1.eval(low) == 0 and d2.eval(low) > 0
        assert d1.eval(high) == 0 and d2.eval(high) < 0
    else:
        point = a
        assert p.LC() == (-1) ** (a + b) * (1 + c % 2)
        assert p.eval(point) == b and d1.eval(point) == c and d2.eval(point) == 0
        assert d2.eval(point - 1) * d2.eval(point + 1) < 0


@pytest.mark.parametrize("generator", CONVEXITY, ids=lambda g: g.prefix)
def test_thousand_seeds_match_numerical_curvature(generator):
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
        if name.startswith("convex_"):
            check_convexity(answer, *convex_case(name, *triple))
        elif name.startswith("polynomial_"):
            check_polynomial(name, answer, *triple)
        else:
            check_joint(answer, *joint_case(name, *triple))
        contract = generator.input_contract(params)
        assert contract == answer.contract
        tree = parse_answer_input(source(answer), contract.kind, contract=contract)
        assert answer.check(tree) == "correct"
        render(task, registry())
