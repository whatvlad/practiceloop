"""#285: independent numerical integration of the original planar functions and heights."""

import math

import pytest
from seed_sweep import sweep
from test_engine_analysis_limits import source
from test_engine_double_integrals_cartesian import quad

from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

POLAR = [g for g in generators() if g.evaluate.__module__.endswith("._polar_integrals")]
PI = math.pi


def radial_integral(function, angles, inner, outer, *, center=(0, 0), segments=1):
    def angular(theta):
        lo, hi = inner(theta), outer(theta)

        def radially(r):
            x = center[0] + r * math.cos(theta)
            y = center[1] + r * math.sin(theta)
            return function(x, y) * r

        ends = [lo + (hi - lo) * i / segments for i in range(segments + 1)]
        return math.fsum(
            quad(radially, start, end) for start, end in zip(ends, ends[1:], strict=False)
        )

    return quad(angular, *angles)


def independent(prefix, a, b, c):
    def zero(theta):
        return 0

    def unit(x, y):
        return 1

    if prefix == "DIAY":
        return radial_integral(lambda x, y: a * x * y, (PI / 6, PI / 3), zero, lambda t: b + c)
    if prefix == "DIAZ":
        return radial_integral(
            lambda x, y: a * x * y * y, (-PI / 2, PI / 2), lambda t: b, lambda t: b + c
        )
    if prefix == "DIBA":
        return radial_integral(
            lambda x, y: c * y * y * math.exp(a * (x * x + y * y)),
            (0, PI / 2),
            zero,
            lambda t: math.sqrt(b),
        )
    if prefix == "DIBB":
        return radial_integral(
            lambda x, y: a * c * x * x, (0, PI), zero, lambda t: 2 * b * math.sin(t)
        )
    if prefix == "DIBC":
        return radial_integral(
            lambda x, y: a * c * (x * x + y * y),
            (0, PI / 4),
            lambda t: b * math.sin(t),
            lambda t: b * math.cos(t),
        )
    if prefix == "DIBD":
        return radial_integral(
            lambda x, y: a * c * y, (-PI / 2, 0), zero, lambda t: 2 * b * math.cos(t)
        )
    if prefix == "DIBE":
        return radial_integral(
            lambda x, y: c * math.sin(a * (x * x + y * y)),
            (0, 2 * PI),
            zero,
            lambda t: PI * math.sqrt(b),
            segments=12,
        )
    if prefix == "DIBF":
        return radial_integral(
            lambda x, y: math.log1p(a * (x * x + y * y)), (0, 2 * PI), lambda t: b, lambda t: b + c
        )
    if prefix == "DIBG":
        return quad(lambda y: 3 * a - y - y * y / (4 * a), 0, 2 * a)
    if prefix == "DIBH":
        return radial_integral(
            unit, (0, PI), lambda t: 2 * b * math.sin(t), lambda t: 2 * (b + c) * math.sin(t)
        )
    if prefix == "DIBI":
        vertices = [
            ((3 * u + v) / 4, (u - v) / 4)
            for u, v in ((a, 0), (a + b, 0), (a + b, c), (a, c), (a, 0))
        ]
        return (
            abs(sum(x * v - y * u for (x, y), (u, v) in zip(vertices, vertices[1:], strict=False)))
            / 2
        )
    if prefix == "DIBJ":
        return radial_integral(
            unit, (PI / 3, 2 * PI / 3), zero, lambda t: 2 * (b + c) * math.sin(t)
        )
    if prefix == "DIBK":
        return radial_integral(
            lambda x, y: math.sqrt(25 * a * a - x * x - y * y) - (x * x + y * y) / a + 13 * a,
            (0, 2 * PI),
            zero,
            lambda t: 4 * a,
        )
    if prefix == "DIBL":
        radius = a + b + c
        return quad(lambda z: PI * (radius * radius - z * z), a, radius)
    if prefix == "DIBM":
        return radial_integral(
            lambda x, y: a * c * (x * x + y * y), (0, PI), zero, lambda t: 2 * b * math.sin(t)
        )
    if prefix == "DIBN":

        def height(x, y):
            return max(0, min(b, b + c - x * x - y * y))

        lower = radial_integral(height, (0, 2 * PI), zero, lambda t: math.sqrt(c))
        upper = radial_integral(
            height, (0, 2 * PI), lambda t: math.sqrt(c), lambda t: math.sqrt(b + c)
        )
        return lower + upper
    if prefix == "DIBO":
        return radial_integral(
            lambda x, y: x * y, (0, 2 * PI), zero, lambda t: a, center=(a + b, a + c)
        )
    if prefix == "DIBP":
        return radial_integral(
            lambda x, y: c - b * y - (x * x + y * y) / (2 * a),
            (0, 2 * PI),
            zero,
            lambda t: math.sqrt(2 * a * c + a * a * b * b),
            center=(0, -a * b),
        )
    raise AssertionError(prefix)


@pytest.mark.parametrize("generator", POLAR, ids=lambda item: item.prefix)
def test_polar_integral_against_independent_numerical_integration(generator):
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
        assert float(answer.expected) == pytest.approx(
            independent(generator.prefix, *coefficients), rel=2e-9, abs=2e-9
        )
        assert graph(validate_plot(generator.solution_visual(params)))
