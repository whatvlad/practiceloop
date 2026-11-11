"""#283: independent optimization constraints and first/second-order checks."""

import math

import pytest
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

APPLICATIONS = [g for g in generators() if g.evaluate.__module__.endswith("._applied_optimization")]


def check_container(prefix, values, a, b, c):
    x, y, height, minimum = values
    if prefix == "MVDI":
        volume = 4 * (a + b + c) ** 3
        wall, horizontal = 1, 1
    else:
        wall = a + b
        horizontal = 2 * (wall + c)
        volume = wall**2 * (wall + c) * (b + 1) ** 3

    def cost(base_x, base_y):
        h = volume / (base_x * base_y)
        return horizontal * base_x * base_y + 2 * wall * h * (base_x + base_y)

    assert x == y
    assert x * y * height == pytest.approx(volume)
    assert cost(x, y) == pytest.approx(minimum)
    assert horizontal * x**3 == pytest.approx(2 * wall * volume)
    for sx, sy in ((0.8, 1), (1.2, 1), (0.5, 2), (2, 0.5), (1.4, 1.4)):
        assert cost(sx * x, sy * y) > minimum


def check_profit(values, a, b, c):
    x, y, maximum = values
    p = 10 * (a + b + 2)
    q = 10 * (a + b + 3 * c + 2)

    def profit(u, v):
        return p * u + q * v - 10 * (u * u - u * v + v * v)

    assert x >= 0 and y >= 0 and x.is_integer() and y.is_integer()
    assert profit(x, y) == pytest.approx(maximum)
    for i in range(2 * int(x) + 1):
        for j in range(2 * int(y) + 1):
            if (i, j) != (x, y):
                assert profit(i, j) < maximum


def check_closest(values, visual, a, b, c):
    x, y, distance = values
    k = 1 + (c - 1) % 2
    chosen = 1 + (a - 1) % 3
    target = k * k * chosen**3 / 2 + b * chosen, (1 - b) / k
    assert y == pytest.approx(k * x * x / 2)
    assert distance == pytest.approx(math.dist((x, y), target))
    assert (target[0] - x) + k * x * (target[1] - y) == pytest.approx(0)
    for delta in (-5, -1, -0.1, 0.1, 1, 5):
        t = x + delta
        assert math.dist((t, k * t * t / 2), target) > distance
    assert visual["paths"][1]["points"] == [list(target), [x, y]]


@pytest.mark.parametrize("generator", APPLICATIONS, ids=lambda item: item.prefix)
def test_applied_optimization_independently(generator):
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
        values = tuple(float(part.expected) for part in answer.components)
        visual = validate_plot(generator.solution_visual(params))
        assert graph(visual)
        if generator.prefix in ("MVDI", "MVDJ"):
            check_container(generator.prefix, values, *coefficients)
        elif generator.prefix == "MVDK":
            check_profit(values, *coefficients)
        else:
            check_closest(values, visual, *coefficients)
