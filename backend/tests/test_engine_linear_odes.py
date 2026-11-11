"""#288: independent linear residuals, singular branches, and trapezoid geometry."""

import math

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source
from test_engine_separable_odes import as_function, close

from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

LINEAR = [g for g in generators() if g.evaluate.__module__.endswith("._linear_odes")]


def residual(prefix, t, y, dy, a, b, c):
    if prefix == "ODAP":
        return dy + a * y - b * mp.sin(c * t)
    if prefix == "ODAQ":
        return dy + 2 * a * (t - c) * y - b * mp.exp(-a * (t - c) ** 2)
    if prefix == "ODAR":
        return t * dy - 2 * y - (b + c) * t**3 * mp.cos(a * t)
    if prefix == "ODAS":
        return t * dy - 2 * y - (a + b) * t ** (c + 3)
    if prefix == "ODAT":
        return t * dy - a * t * y - (b + c) * mp.exp(a * t)
    if prefix == "ODAU":
        return (t + a) * dy - y - (b + c) * t
    if prefix == "ODAV":
        return dy - a * y - b
    if prefix == "ODAW":
        return dy - a * (y + b) * mp.sin(t)
    if prefix == "ODAX":
        return t * dy + y - a * t - b
    if prefix == "ODAY":
        return mp.sin(t) * mp.cos(t) * dy - y - (a + b) * mp.sin(t) ** 3
    raise AssertionError(prefix)


def verify_family(prefix, parts, a, b, c):
    p, h = map(as_function, parts[:2])
    assert parts[2].expected == sp.S.Reals
    if prefix == "ODAT":
        assert parts[3].expected == sp.S.Reals - sp.FiniteSet(0)
    elif prefix == "ODAU":
        assert parts[3].expected == sp.S.Reals - sp.FiniteSet(-a)
    else:
        assert parts[3].expected == sp.S.Reals
    for t in (mp.mpf("-0.3") - a, mp.mpf("0.4")):
        for constant in (-2, 0, 3):
            close(
                residual(
                    prefix,
                    t,
                    p(t) + constant * h(t),
                    mp.diff(p, t) + constant * mp.diff(h, t),
                    a,
                    b,
                    c,
                ),
                0,
            )
    if prefix in ("ODAR", "ODAS"):
        close(p(0), 0)
        close(h(0), 0)
        close(mp.diff(p, 0), 0)
        close(mp.diff(h, 0), 0)
    if prefix == "ODAU":
        t = mp.mpf(-a) + mp.mpf("1e-18")
        assert abs(mp.diff(p, t)) > 30


def verify_ivp(prefix, parts, a, b, c):
    solution = as_function(parts[0])
    if prefix == "ODAV":
        t0, y0 = mp.mpf(c), b + c
        expected_domain = sp.S.Reals
    elif prefix == "ODAW":
        t0, y0 = mp.pi / (c + 2), -b if c % 2 == 0 else b + c
        expected_domain = sp.S.Reals
    elif prefix == "ODAX":
        t0, y0 = mp.mpf(c), 0
        expected_domain = sp.Interval.open(0, sp.oo)
    else:
        t0, y0 = mp.pi / (c + 3), 0
        expected_domain = sp.Interval.open(0, sp.pi / 2)
    assert parts[1].expected == parts[0].domain == expected_domain
    close(solution(t0), y0)
    for t in (t0, mp.mpf("0.21")):
        close(residual(prefix, t, solution(t), mp.diff(solution, t), a, b, c), 0)
    if prefix == "ODAX":
        assert abs(solution(mp.mpf("1e-12"))) > mp.mpf("1e8")


def verify_tangent(parts, diagram, a, b, c):
    p, h = map(as_function, parts[:2])
    lo, hi = map(as_function, parts[3:])
    area = a + b + c
    assert parts[2].expected == sp.S.Reals
    for t in (mp.mpf("0.75"), mp.mpf("1.5")):
        lower, upper = lo(t), hi(t)
        close(p(t) + lower * h(t), 0)
        close(p(t) + upper * h(t) - t * (mp.diff(p, t) + upper * mp.diff(h, t)), 0)
        for constant in ((lower + upper) / 2, mp.mpf(0)):
            y = p(t) + constant * h(t)
            intercept = y - t * (mp.diff(p, t) + constant * mp.diff(h, t))
            assert y > 0 and intercept > 0
            close(t * (y + intercept) / 2, area)
    vertices = diagram["paths"][2]["points"]
    shoelace = math.fsum(
        x * v - u * y for (x, y), (u, v) in zip(vertices, vertices[1:], strict=False)
    )
    assert abs(shoelace) / 2 == pytest.approx(area)


@pytest.mark.parametrize("generator", LINEAR, ids=lambda item: item.prefix)
def test_linear_ode_independently(generator):
    seen = set()
    prefix = generator.prefix
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
            diagram = validate_plot(generator.solution_visual(params))
            assert graph(diagram)
            if prefix <= "ODAU":
                verify_family(prefix, answer.components, *coefficients)
            elif prefix <= "ODAY":
                verify_ivp(prefix, answer.components, *coefficients)
            else:
                verify_tangent(answer.components, diagram, *coefficients)
