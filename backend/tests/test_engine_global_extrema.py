"""#282: independent feasible-region, least-squares and skew-line checks."""

import math

import pytest
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.answers.computational import OrderedAnswer
from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

GLOBAL = [g for g in generators() if g.evaluate.__module__.endswith("._global_extrema")]


def region(prefix):
    if prefix == "MVDA":
        return lambda u, v: 2 * u**3 + 4 * u * u + v * v - 2 * u * v, (
            (u, u * u + t * (4 - u * u)) for u in (i / 8 for i in range(-16, 17)) for t in GRID
        )
    if prefix == "MVDB":
        return lambda u, v: math.sqrt(max(0, v - u * u)) + math.sqrt(max(0, u - v * v)), (
            (u, u * u + t * (math.sqrt(u) - u * u)) for u in GRID for t in GRID
        )
    if prefix == "MVDC":
        return lambda u, v: math.sqrt(max(0, 1 - u * u)) + math.sqrt(max(0, 4 - u * u - v * v)), (
            (u, (2 * t - 1) * math.sqrt(4 - u * u)) for u in (2 * s - 1 for s in GRID) for t in GRID
        )
    if prefix == "MVDD":
        return lambda u, v: u * u - v * v, ((u, 1 + u + t * (1 - u)) for u in GRID for t in GRID)
    if prefix == "MVDE":
        return lambda u, v: u**4 + v**4, (
            (r * math.cos(math.tau * t), r * math.sin(math.tau * t)) for r in GRID for t in GRID
        )
    if prefix == "MVDF":
        return lambda u, v: (u + v) * math.exp(-u - 2 * v), (
            (8 * u, 8 * v) for u in GRID for v in GRID
        )
    raise AssertionError(prefix)


GRID = tuple(i / 12 for i in range(13))
COUNTS = {
    "MVDA": (1, 2),
    "MVDB": (2, 1),
    "MVDC": (4, 1),
    "MVDD": (1, 1),
    "MVDE": (1, 4),
    "MVDF": (1, 1),
}


def verify_extrema(prefix, values, visual, a, b, c):
    objective, samples = region(prefix)
    min_x, min_y, minimum = values[:3]
    max_x, max_y, maximum = values[5:8] if prefix == "MVDB" else values[3:6]
    assert c * objective(min_x / a, min_y / b) == pytest.approx(minimum, abs=1e-6)
    assert c * objective(max_x / a, max_y / b) == pytest.approx(maximum)
    assert all(minimum - 1e-9 <= c * objective(u, v) <= maximum + 1e-9 for u, v in samples)
    for kind, height, count in zip(
        ("Minimum", "Maximum"), (minimum, maximum), COUNTS[prefix], strict=True
    ):
        markers = [point for point in visual["points"] if point["label"] == kind]
        assert len({(point["x"], point["y"]) for point in markers}) == count
        for marker in markers:
            assert c * objective(marker["x"] / a, marker["y"] / b) == pytest.approx(
                height, abs=1e-6
            )
    if prefix == "MVDA":
        assert values[6:] == pytest.approx((2 * a, 4 * b))
        assert max_x < values[6]
    elif prefix == "MVDB":
        assert values[3:5] == pytest.approx((a, b))
        assert min_x < values[3]
    elif prefix == "MVDC":
        assert min_x > 0 and min_y > 0
    elif prefix == "MVDE":
        assert max_x > 0 and max_y == 0


def verify_least_squares(values, a, b, c):
    x, y, minimum = values
    vertices = ((-a, b + c), (a, b), (2 * a, -c))
    distances = [math.dist((x, y), vertex) ** 2 for vertex in vertices]
    assert sum(distances) == pytest.approx(minimum, abs=1e-6)
    for dx, dy in ((1, 0), (0, 1), (1, 1), (-1, -1)):
        trial = sum(math.dist((x + dx, y + dy), vertex) ** 2 for vertex in vertices)
        assert trial > minimum
        assert trial - minimum == pytest.approx(3 * (dx * dx + dy * dy))


def verify_skew(distance, visual, a, b, c):
    first_origin, second_origin = (0, b, -a), (1, 0, b)
    direction_cross = (0, 0, 1 + a * c)
    delta = tuple(q - p for p, q in zip(first_origin, second_origin, strict=True))
    assert distance == pytest.approx(
        abs(sum(d * n for d, n in zip(delta, direction_cross, strict=True)))
        / math.hypot(*direction_cross)
    )
    first, second, connector = visual["paths"]
    assert connector["points"][0][0] == connector["points"][1][0]
    assert connector["points"][1][1] - connector["points"][0][1] == pytest.approx(distance)
    for line, foot in zip((first, second), connector["points"], strict=True):
        midpoint = [(u + v) / 2 for u, v in zip(*line["points"], strict=True)]
        assert midpoint == pytest.approx(foot)


@pytest.mark.parametrize("generator", GLOBAL, ids=lambda item: item.prefix)
def test_global_extrema_or_distance(generator):
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
        parts = answer.components if isinstance(answer, OrderedAnswer) else (answer,)
        values = tuple(float(part.expected) for part in parts)
        visual = validate_plot(generator.solution_visual(params))
        assert graph(visual)
        if generator.prefix == "MVDG":
            verify_least_squares(values, *coefficients)
        elif generator.prefix == "MVDH":
            verify_skew(values[0], visual, *coefficients)
        else:
            verify_extrema(generator.prefix, values, visual, *coefficients)
