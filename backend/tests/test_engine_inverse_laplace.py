"""#290: check inverse transforms by quadrature and forced equations by residuals."""

import math

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source
from test_engine_double_integrals_cartesian import quad
from test_engine_separable_odes import as_function, close

from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

INVERSES = [g for g in generators() if g.evaluate.__module__.endswith("._inverse_laplace")]


def original_transform(prefix, a, b, c, s):
    if prefix == "LTAP":
        return (b + c) / (s + a), -a
    if prefix == "LTAQ":
        return (a * s + b) / (s * s + 2 * c * s + c * c + b * b), -c
    if prefix == "LTAR":
        return c / ((s - a) * (s - a - b)), a + b
    if prefix == "LTAS":
        return (s + a + b) / ((s + a) * (s - b) * (s * s + c * c)), b
    if prefix == "LTAT":
        return c * (s * s + b * b) / (s * s * (s * s - a * a) ** 2), a
    if prefix == "LTAU":
        return (s + c + a + b) / ((s + c) ** 2 + (a + b) ** 2), -c
    if prefix == "LTAV":
        return (c + b / s) / (s - a), a
    if prefix == "LTAW":
        return b * c / ((s * s + c * c) * (s - a)), a
    if prefix == "LTAX":
        return (b * s + c + a * b) / (s * (s + a)), 0
    if prefix == "LTAY":
        return (b / (s + a) - c) / (s * (s + a)), -a if b == a * c else 0
    if prefix == "LTAZ":
        return (1 + c / (s * s + c * c)) / ((s - a) ** 2 + b * b), a
    if prefix == "LTBA":
        return (b / s + c / s**2) / (s * (s - 2 * a)), 2 * a
    if prefix == "LTBB":
        return 2 * b * c / (s**3 * (s + a) ** 2), 0
    if prefix == "LTBC":
        return (2 + 1 / (s + c) ** 2) / ((s + a) ** 2 + b * b), -min(a, c)
    raise AssertionError(prefix)


def residual(prefix, a, b, c, t, y, d, dd):
    if prefix == "LTAV":
        return d - a * y - b
    if prefix == "LTAW":
        return d - a * y - b * mp.sin(c * t)
    if prefix == "LTAX":
        return dd + a * d
    if prefix == "LTAY":
        return dd + a * d - b * mp.exp(-a * t)
    if prefix == "LTAZ":
        return dd - 2 * a * d + (a * a + b * b) * y - mp.sin(c * t)
    if prefix == "LTBA":
        return dd - 2 * a * d - b - c * t
    if prefix == "LTBB":
        return dd + 2 * a * d + a * a * y - b * c * t * t
    if prefix == "LTBC":
        return dd + 2 * a * d + (a * a + b * b) * y - t * mp.exp(-c * t)
    raise AssertionError(prefix)


def verify_residual(prefix, answer, a, b, c):
    y = as_function(answer)
    start = {"LTAV": c, "LTAX": b}.get(prefix, 0)
    derivative = {"LTAX": c, "LTAY": -c, "LTAZ": 1, "LTBC": 2}.get(prefix, 0)
    close(y(mp.mpf(0)), start)
    if prefix >= "LTAX":
        close(mp.diff(y, 0), derivative)
    for t in map(mp.mpf, ("0.2", "0.7")):
        close(residual(prefix, a, b, c, t, y(t), mp.diff(y, t), mp.diff(y, t, 2)), 0)


@pytest.mark.parametrize("generator", INVERSES, ids=lambda item: item.prefix)
def test_inverse_transform_and_forcing_independently(generator):
    seen = set()
    prefix = generator.prefix
    time = sp.Symbol("t", real=True)
    with mp.workdps(48):
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
            solution, convergence = answer.components
            assert solution.domain == sp.Interval(0, sp.oo)
            _, boundary = original_transform(prefix, *coefficients, 100)
            assert convergence.expected == sp.Interval.open(boundary, sp.oo)
            if prefix >= "LTAV":
                verify_residual(prefix, solution, *coefficients)
            numeric_y = sp.lambdify(time, solution.expected, "math")
            for margin in (2.7, 4.3):
                s = boundary + margin
                expected, _ = original_transform(prefix, *coefficients, s)
                stop = 60 / margin
                numeric = math.fsum(
                    quad(
                        lambda t, rate=s, y=numeric_y: math.exp(-rate * t) * y(t),
                        i * stop / 24,
                        (i + 1) * stop / 24,
                    )
                    for i in range(24)
                )
                assert numeric == pytest.approx(expected, rel=3e-9, abs=3e-10)
            assert graph(validate_plot(generator.solution_visual(params)))
