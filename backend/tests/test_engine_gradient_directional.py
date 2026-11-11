"""#280: independent differences and geometry for the gradient and direction families."""

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

DIRECTIONS = [g for g in generators() if g.evaluate.__module__.endswith("._gradient_directional")]


def numeric_problem(prefix, a, b, c):
    if prefix == "MVBR":
        return lambda x, y: a * x**3 + b * x * y * y + c, (1, -2), ()
    if prefix == "MVBS":
        return lambda x, y: a * mp.log(x + b * mp.log(y)), (c * mp.e, 1), ()
    if prefix == "MVBT":
        return lambda x, y: (1 + a * x * y) ** (b * y + c), (0, 0), ()
    if prefix == "MVBU":
        return lambda x, y, z: a * x * mp.sqrt(y) - b * mp.exp(c * z) * mp.log(y), (0, 1, 0), ()
    if prefix == "MVBV":
        return lambda x, y, z: a * x / (b * y + c * mp.sin(z)), (0, 1, mp.pi), ()
    if prefix == "MVBW":
        return lambda x, y, z: mp.sqrt(a * z + mp.sqrt(b * y + mp.sqrt(c * x))), (1, 1, 1), ()
    if prefix == "MVBX":
        return lambda x, y: a * x * x - b * y * y, (-c - 2, 4), (mp.mpf(12) / 13, mp.mpf(5) / 13)
    if prefix == "MVBY":
        return lambda x, y: a * x - b * y / (x * x) + c * y, (1, 1), (mp.mpf(3) / 5, -mp.mpf(4) / 5)
    if prefix == "MVBZ":
        return (
            lambda x, y, z: mp.exp((1 + a % 3) * x * x * y - b * z),
            (-1, 1 + c % 2, -1),
            (mp.mpf(2) / 3, -mp.mpf(2) / 3, mp.mpf(1) / 3),
        )
    if prefix == "MVCA":
        return lambda x, y: a * y - b * x * x + (a + c) * mp.log(x * y), (-mp.mpf("0.5"), -1), ()
    if prefix == "MVCB":
        return lambda x, y: mp.exp(a * x / 2) * (b * x + c * y * y), (0, 2), ()
    raise AssertionError(prefix)


def close(value, expected):
    assert abs(value - expected) <= mp.mpf("1e-36") * max(1, abs(expected))


def check_nonsmooth(prefix, parts, a, b, c):
    n = c + 1 if prefix == "MVBP" else b + 1
    u, v = mp.mpf(n * n - 1) / (n * n + 1), mp.mpf(2 * n) / (n * n + 1)
    t = mp.mpf("1e-18")
    if prefix == "MVBP":
        for displacement, part in zip((-t, t), parts, strict=False):
            actual = (
                mp.sqrt(a * (u * displacement) ** 2 + b * (v * displacement) ** 2) / displacement
            )
            close(mp.mpf(str(part.expected.evalf(45))), actual)
        assert parts[2].expected == "does_not_exist"
    else:
        for displacement in (-t, t):
            y = v * displacement
            x = c + u * displacement
            original = mp.sign(y) * mp.root(abs(a * x * y), 3)
            assert original / displacement > mp.mpf("1e10")
        assert all(part.expected == sp.oo for part in parts)


def check_smooth(prefix, parts, visual, coefficients):
    values = tuple(mp.mpf(str(part.expected.evalf(45))) for part in parts)
    function, base, unit = numeric_problem(prefix, *coefficients)
    base = tuple(map(mp.mpf, base))
    if unit:
        close(sum(component**2 for component in unit), 1)
        derivative = mp.diff(
            lambda t: function(*(p + t * v for p, v in zip(base, unit, strict=True))), 0
        )
        close(values[0], derivative)
        height = function(*base)
        for t, z in visual["paths"][1]["points"]:
            assert z == pytest.approx(float(height + derivative * t))
        return
    gradient = tuple(
        mp.diff(function, base, tuple(int(i == axis) for i in range(len(base))))
        for axis in range(len(base))
    )
    if prefix not in ("MVCA", "MVCB"):
        for value, derivative in zip(values, gradient, strict=True):
            close(value, derivative)
        return
    x, y = values[-2:]
    assert x > 0
    close(x * x + y * y, 1)
    close(gradient[0] * x + gradient[1] * y, 0)
    if prefix == "MVCA":
        rate, u, v = values[:3]
        close(u * u + v * v, 1)
        close(gradient[0] * u + gradient[1] * v, rate)
        close(rate, mp.norm(gradient))
    for marker in visual["points"]:
        angle = marker["x"]
        assert marker["y"] == pytest.approx(
            float(gradient[0] * mp.cos(angle) + gradient[1] * mp.sin(angle)), abs=1e-9
        )


@pytest.mark.parametrize("generator", DIRECTIONS, ids=lambda item: item.prefix)
def test_gradient_and_direction_against_independent_derivatives(generator):
    seen = set()
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
            parts = answer.components if isinstance(answer, OrderedAnswer) else (answer,)
            visual = generator.solution_visual(params)
            if visual is not None:
                visual = validate_plot(visual)
                assert graph(visual)
            if generator.prefix in ("MVBP", "MVBQ"):
                check_nonsmooth(generator.prefix, parts, *coefficients)
            else:
                check_smooth(generator.prefix, parts, visual, coefficients)
