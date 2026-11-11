"""#279: independently verify tangent planes and directional linearizations."""

import mpmath as mp
import pytest
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.answers.computational import OrderedAnswer
from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

TANGENTS_AND_ESTIMATES = [
    g for g in generators() if g.evaluate.__module__.endswith("._tangent_linear")
]


def tangent_data(prefix, a, b, c):
    if prefix == "MVBB":
        return lambda x, y: a * x**2 * mp.sqrt(y + 1), (c, (b + 1) ** 2 - 1)
    if prefix == "MVBC":
        return lambda x, y: mp.exp(a * x + b * y), (1 + c % 3, -1)
    if prefix == "MVBD":
        return lambda x, y: a * mp.asin(x) / ((b + c) * mp.acos(y)), (
            -mp.mpf("0.5"),
            mp.sqrt(3) / 2,
        )
    if prefix == "MVBE":
        return lambda x, y: (a + x - b * y) ** (c + 2), (0, 0)
    if prefix == "MVBF":
        return lambda x, y: mp.exp(a * x + b * y) - mp.exp(c - b * y), (mp.mpf(c) / a, 0)
    if prefix == "MVBG":
        return lambda x, y: mp.atan(a * x / y), None
    if prefix == "MVBH":
        return lambda x, y: a * x**2 + b * y**2, (
            -mp.mpf(1) / (2 * a * c),
            -mp.mpf(1) / (2 * b * c),
        )
    raise AssertionError(prefix)


def linear_data(prefix, a, b, c):
    if prefix == "MVBI":
        return (
            lambda x, y: x ** (a + 2) * y ** (b + 1),
            (1, 1),
            (mp.mpf(c) / 100, -mp.mpf(b) / 1000),
        )
    if prefix == "MVBJ":
        return (
            lambda x, y, z: mp.root(x**3 + y**3 + z**3, 3),
            (3, 4, 5),
            (mp.mpf(a) / 100, mp.mpf(b) / 100, mp.mpf(c) / 100),
        )
    if prefix == "MVBK":
        return lambda x, y: x * mp.exp(y), (a + 2, 0), (-mp.mpf(b) / 100, mp.mpf(c) / 100)
    if prefix == "MVBL":
        return lambda x, y: mp.cos(x) / y, (0, a + 1), (mp.mpf(b) / 100, -mp.mpf(c) / 100)
    if prefix == "MVBM":
        return lambda x, y: mp.pi * x * x * y, (100 + 10 * a, 300 + 10 * b), (c, c)
    if prefix == "MVBN":
        return (
            lambda x, y, z: mp.sqrt(x * x + y * y + z * z),
            (a + 2, b + 3, c + 10),
            (mp.mpf("0.02"),) * 3,
        )
    if prefix == "MVBO":
        return (
            lambda x, y, z: x * y * z,
            (a + 3, b + 4, c + 5),
            (mp.mpf(a) / 100, mp.mpf(b) / 100, mp.mpf(c) / 100),
        )
    raise AssertionError(prefix)


def close(actual, expected):
    assert abs(actual - expected) <= mp.mpf("1e-35") * max(1, abs(expected))


def verify_tangent(prefix, values, visual, coefficients):
    function, coordinate = tangent_data(prefix, *coefficients)
    if coordinate is None:
        x, y, z = values
        close(z, function(x, y))
        p = mp.diff(lambda s: function(s, y), x)
        q = mp.diff(lambda s: function(x, s), y)
        close(p, coefficients[1])
        close(q, coefficients[2])
    else:
        p, q, offset = values
        x, y = coordinate
        z = function(x, y)
        close(p, mp.diff(lambda s: function(s, y), x))
        close(q, mp.diff(lambda s: function(x, s), y))
        close(p * x + q * y + offset, z)
        if prefix == "MVBH":
            close(-p * coefficients[2], 1)
            close(-q * coefficients[2], 1)
    assert visual["points"][0]["x"] == 0
    assert visual["points"][0]["y"] == pytest.approx(float(z))
    for slope, line in zip((p, q), visual["paths"][1::2], strict=True):
        for displacement, height in line["points"]:
            assert height == pytest.approx(float(z) + float(slope) * displacement)


def verify_estimate(prefix, values, visual, coefficients):
    function, base, delta = linear_data(prefix, *coefficients)

    def along(t):
        return function(*(x + t * step for x, step in zip(base, delta, strict=True)))

    initial = along(0)
    change = mp.diff(along, 0)
    if prefix == "MVBO":
        close(values[0], change / initial)
    else:
        close(values[0], change)
        if len(values) == 2:
            close(values[1], initial + change)
    assert visual["points"][0]["y"] == pytest.approx(float(initial + change))
    assert visual["points"][1]["y"] == pytest.approx(float(along(1)))


@pytest.mark.parametrize("generator", TANGENTS_AND_ESTIMATES, ids=lambda item: item.prefix)
def test_tangent_or_estimate_against_independent_derivatives(generator):
    seen = set()
    prefix = generator.prefix
    with mp.workdps(50):
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
            components = answer.components if isinstance(answer, OrderedAnswer) else (answer,)
            values = tuple(mp.mpf(str(part.expected.evalf(45))) for part in components)
            visual = validate_plot(generator.solution_visual(params))
            assert graph(visual)
            if prefix <= "MVBH":
                verify_tangent(prefix, values, visual, coefficients)
            else:
                verify_estimate(prefix, values, visual, coefficients)
