"""#284: independently integrate scalar problems and test reversed region membership."""

import math

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.answers.computational import OrderedAnswer
from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

DOUBLE = [g for g in generators() if g.evaluate.__module__.endswith("._double_integrals")]
NODES, WEIGHTS = mp.gauss_quadrature(24, "legendre")
QUADRATURE = [(float(x), float(w)) for x, w in zip(NODES, WEIGHTS, strict=True)]


def quad(function, lower, upper):
    middle = (lower + upper) / 2
    radius = (upper - lower) / 2
    return radius * math.fsum(
        weight * function(middle + radius * node) for node, weight in QUADRATURE
    )


def ordinary_integral(prefix, a, b, c):
    if prefix == "DIAA":
        return lambda x, y: a * x + x * y - b * x * x - c * y, 0, 1, lambda x: (0, 1)
    if prefix == "DIAB":
        return lambda x, y: x / (y * y), 1, a + 1, lambda x: (b, b + c)
    if prefix == "DIAC":
        return lambda x, y: 1 / (x + y + c) ** 3, 0, a, lambda x: (0, b)
    if prefix == "DIAD":
        return (
            lambda x, y: c * x * math.sin(x * y),
            0,
            1 / (a + 1),
            lambda x: (math.pi, (b + 1) * math.pi),
        )
    if prefix == "DIAE":
        return lambda x, y: math.exp(a * x - b * y), 0, 1, lambda x: (-c, 0)
    if prefix == "DIAF":
        return lambda x, y: (x + y) * math.exp(-a * x), 0, b, lambda x: (0, c)
    if prefix == "DIAG":
        return lambda x, y: b * y / (x * x), 1, a + 1, lambda x: (c * x, c * x * x)
    if prefix == "DIAJ":
        return lambda y, x: math.sqrt(y * y + c * c), 0, a, lambda y: (0, b * y)
    if prefix == "DIAQ":
        return lambda x, y: b * c * x * y * y, -a - 1, a, lambda x: (x, a * (a + 1) - x * x)
    if prefix == "DIAR":
        return lambda y, x: a * c * x * x * y, -(2 + (b - 1) % 3), -1, lambda y: (-y * y, 1 / y)
    if prefix == "DIAS":
        return lambda y, x: math.exp(a * x / y), 1 / (b + 1), c, lambda y: (0, y * y)
    if prefix == "DIAT":
        return lambda x, y: a * x * y + b * x * x, -2, 0, lambda x: (x * x + 3 * x + c, x + c)
    if prefix == "DIAU":
        return lambda x, y: a * c * x * x * math.exp(x * y), 0, b, lambda x: (x, b)
    if prefix == "DIAV":
        return lambda x, y: c * x / (x * x + y * y), a, a + b, lambda x: (x, math.sqrt(3) * x)
    if prefix == "DIAW":
        return (
            lambda x, y: math.exp(c * x * x),
            0,
            math.sqrt(math.log(a + 1)),
            lambda x: (0, 2 * b * x),
        )
    if prefix == "DIAX":
        return lambda y, x: 2 * b * x - 3 * c * y + 2, 0, math.pi, lambda y: (-a, math.sin(y))
    raise AssertionError(prefix)


def independent_integral(prefix, a, b, c):
    if prefix == "DIAH":
        # Substitute y=x+c²xt² in the inner quadrature.
        return quad(
            lambda x: quad(
                lambda t: b * x * x * math.sqrt(c * c * x * t * t) * 2 * c * c * x * t, 0, 1
            ),
            1,
            a + 1,
        )
    if prefix == "DIAI":
        # Substitute x=a sin(t) to avoid a square-root endpoint in the quadrature.
        return quad(
            lambda t: (
                quad(lambda y: b * (a * math.sin(t)) ** 3 + c * y**3, 0, a * math.cos(t))
                * a
                * math.cos(t)
            ),
            -math.pi / 2,
            math.pi / 2,
        )
    integrand, lower, upper, limits = ordinary_integral(prefix, a, b, c)
    return quad(lambda t: quad(lambda s: integrand(t, s), *limits(t)), lower, upper)


def original_region(prefix, a, b, c):
    if prefix == "DIAK":
        return (-a, a), (-b, a * c), lambda x, y: -b <= y <= c * abs(x)
    if prefix == "DIAL":
        r = math.hypot(a, b)
        return (-a, a), (-r, 0), lambda x, y: y >= -math.sqrt(r * r - x * x)
    if prefix == "DIAM":
        return (
            (0, 4 * a),
            (0, 4 * a),
            lambda x, y: math.sqrt(max(0, 4 * a * x - x * x)) <= y <= 2 * math.sqrt(a * x),
        )
    if prefix == "DIAN":
        r = math.sqrt(2 * a)
        return (-a, a), (-r, r), lambda x, y: y * y - a <= x <= y * y / 2
    if prefix == "DIAO":
        return (math.pi / 2, math.pi), (-1, 1), lambda x, y: math.cos(x) <= y <= math.sin(x)
    if prefix == "DIAP":
        return (1, math.exp(a)), (0, a), lambda x, y: math.log(x) <= y
    raise AssertionError(prefix)


def verify_reversed(prefix, answer, a, b, c):
    pieces = answer.components if isinstance(answer.components[0], OrderedAnswer) else (answer,)
    coordinate = "x" if prefix == "DIAN" else "y"
    variable = sp.Symbol(coordinate, real=True)
    reverse = []
    for piece in pieces:
        lo, hi, lower, upper = piece.components
        assert lower.variable == upper.variable == coordinate
        assert lower.domain == upper.domain == sp.Interval(lo.expected, hi.expected)
        reverse.append(
            (
                float(lo.expected),
                float(hi.expected),
                sp.lambdify(variable, lower.expected, "math"),
                sp.lambdify(variable, upper.expected, "math"),
            )
        )
    x_range, y_range, contains = original_region(prefix, a, b, c)
    for i in range(27):
        x = x_range[0] + (i + 0.37) * (x_range[1] - x_range[0]) / 27
        for j in range(29):
            y = y_range[0] + (j + 0.41) * (y_range[1] - y_range[0]) / 29
            outer, inner = (x, y) if coordinate == "x" else (y, x)
            matches = sum(
                lo <= outer <= hi and lower(outer) <= inner <= upper(outer)
                for lo, hi, lower, upper in reverse
            )
            assert matches == int(contains(x, y))


@pytest.mark.parametrize("generator", DOUBLE, ids=lambda item: item.prefix)
def test_cartesian_integral_or_reversal_independently(generator):
    seen = set()
    for seed in sweep(1000):
        params = generator.draw(seed)
        coefficients = params.a, params.b, params.c
        if coefficients in seen:
            continue
        seen.add(coefficients)
        answer = generator.build(params).answer
        tree = parse_answer_input(
            source(answer), generator.contract.kind, contract=generator.contract
        )
        assert answer.check(tree) == "correct"
        assert graph(validate_plot(generator.solution_visual(params)))
        if isinstance(answer, OrderedAnswer):
            verify_reversed(generator.prefix, answer, *coefficients)
        else:
            numeric = independent_integral(generator.prefix, *coefficients)
            assert float(answer.expected) == pytest.approx(numeric, rel=2e-10, abs=2e-10)
