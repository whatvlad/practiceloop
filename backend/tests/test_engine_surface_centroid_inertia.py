"""#286: independent surface quadrature, centroid moments and inertia axes."""

import math

import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source
from test_engine_double_integrals_cartesian import quad

from app.engine.answers.computational import OrderedAnswer
from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

FAMILIES = [g for g in generators() if g.evaluate.__module__.endswith("._surface_centroid_inertia")]


def patch(prefix, a, b, c):
    if prefix == "DIBQ":
        return (
            2
            * math.pi
            * sum(
                quad(
                    lambda r: r * math.sqrt(1 + 4 * (b + c) ** 2 * r * r),
                    a * i / 8,
                    a * (i + 1) / 8,
                )
                for i in range(8)
            )
        )
    if prefix == "DIBR":
        radius = a + b + c

        def section(theta):
            return quad(lambda phi: radius**2 * math.sin(phi), 0, math.pi / 2 - abs(theta))

        return quad(section, -math.pi / 2, 0) + quad(section, 0, math.pi / 2)
    if prefix == "DIBS":
        return 2 * math.pi * quad(lambda r: r * math.hypot(1, c), a / c, (a + b) / c)
    if prefix == "DIBT":
        radius = math.sqrt(3) * a
        return 2 * math.pi * quad(lambda phi: radius**2 * math.sin(phi), 0, math.acos(a / radius))
    raise AssertionError(prefix)


def centroid_x_strip(left, right, lower, upper):
    area = quad(lambda x: upper(x) - lower(x), left, right)
    x_moment = quad(lambda x: x * (upper(x) - lower(x)), left, right)
    y_moment = quad(lambda x: (upper(x) ** 2 - lower(x) ** 2) / 2, left, right)
    return x_moment / area, y_moment / area


def centroid(prefix, a, b, c):
    if prefix == "DIBU":
        return centroid_x_strip(c - a, c + a, lambda x: b * ((x - c) / a) ** 2, lambda x: b)
    if prefix == "DIBV":
        return centroid_x_strip(
            0, math.pi / a, lambda x: 0, lambda x: (b + c) * math.sin(a * x) ** 2
        )
    if prefix == "DIBW":
        return centroid_x_strip(c - 1, c - 1 + a, lambda x: -math.exp(b), lambda x: math.exp(b))
    if prefix == "DIBX":
        h = b + c
        return 0, quad(lambda y: y * 2 * a * (1 - y / h), 0, h) / quad(
            lambda y: 2 * a * (1 - y / h), 0, h
        )

    def width(theta):
        # The substitution x=a sin(theta) includes the Jacobian dx/dtheta.
        return a * math.cos(theta)

    def semicircle(theta):
        return a * math.cos(theta)

    half_area = quad(lambda t: semicircle(t) * width(t), -math.pi / 2, math.pi / 2)
    half_moment = quad(lambda t: semicircle(t) ** 2 * width(t) / 2, -math.pi / 2, math.pi / 2)
    if prefix == "DIBY":
        h = math.sqrt(3) * a
        triangle_area = quad(lambda x: h * (1 - x / a), 0, a) * 2
        triangle_moment = quad(lambda x: (h * (1 - x / a)) ** 2 / 2, 0, a) * 2
        return 0, (triangle_moment - half_moment) / (triangle_area + half_area)
    if prefix == "DIBZ":
        return 0, ((2 * a) ** 3 / 2 - half_moment) / ((2 * a) ** 2 - half_area)
    raise AssertionError(prefix)


def inertia(prefix, a, b, c):
    if prefix == "DICA":
        h = math.sqrt(3) * a

        def width(y):
            return 2 * a * (1 - y / h)

        return (quad(lambda y: y * y * width(y), 0, h) / quad(width, 0, h),)
    if prefix == "DICB":
        h = b + c

        def width(x):
            return h * (1 - (x / a) ** 2)

        return (quad(lambda x: x * x * width(x), -a, a) / quad(width, -a, a),)
    if prefix == "DICC":
        s = a + b + c
        return (quad(lambda x: quad(lambda y: (x - y) ** 2 / 2, 0, s), 0, s) / s**2,)
    if prefix == "DICD":
        radius = a + b
        integral = quad(
            lambda t: quad(lambda r: r**3 * (math.cos(t) - math.sin(t)) ** 2 / 2, 0, radius),
            0,
            math.pi / 2,
        )
        return (integral / (math.pi * radius**2 / 4),)
    if prefix == "DICE":
        radius = a + b + c
        return (quad(lambda r: 2 * math.pi * r**3, 0, radius) / (math.pi * radius**2),)
    if prefix == "DICF":
        sx, sy = a + c, b + c
        area = math.pi * sx * sy
        horizontal = quad(
            lambda t: quad(lambda r: sy**2 * math.sin(t) ** 2 * r**3 * sx * sy, 0, 1),
            0,
            2 * math.pi,
        )
        vertical = quad(
            lambda t: quad(lambda r: sx**2 * math.cos(t) ** 2 * r**3 * sx * sy, 0, 1),
            0,
            2 * math.pi,
        )
        return horizontal / area, vertical / area
    raise AssertionError(prefix)


@pytest.mark.parametrize("generator", FAMILIES, ids=lambda item: item.prefix)
def test_surface_centroid_or_inertia_independently(generator):
    seen = set()
    prefix = generator.prefix
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
        parts = answer.components if isinstance(answer, OrderedAnswer) else (answer,)
        visual = validate_plot(generator.solution_visual(params))
        assert graph(visual)
        if prefix <= "DIBT":
            expected = (patch(prefix, *coefficients),)
        elif prefix <= "DIBZ":
            expected = centroid(prefix, *coefficients)
            marker = visual["points"][0]
            assert (marker["x"], marker["y"]) == pytest.approx(expected)
        else:
            expected = inertia(prefix, *coefficients)
            for part in parts:
                assert part.contract.symbols == (("m", "positive"),)
        for part, numeric in zip(parts, expected, strict=True):
            symbol = sp.Symbol("m", positive=True)
            for mass in (1, 3):
                assert float(part.expected.subs(symbol, mass)) == pytest.approx(
                    numeric * (mass if prefix >= "DICA" else 1), rel=2e-10, abs=2e-10
                )
