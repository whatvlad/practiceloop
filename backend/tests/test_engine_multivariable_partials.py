"""#278: differentiate the original functions numerically at independent points."""

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.answers.computational import OrderedAnswer
from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input

PARTIALS = [g for g in generators() if g.evaluate.__module__.endswith("._multivariable_partials")]


def numeric_function(prefix, a, b, c):
    if prefix == "MVAK":
        return lambda x, y: a * x**2 / (c * y)
    if prefix == "MVAL":
        return lambda x, y: mp.sqrt(a * x**6 + (b + c) * y**4)
    if prefix == "MVAM":
        return lambda x, y: (a * x**2 - b * y**3) / (c * x * y**2)
    if prefix == "MVAN":
        return lambda x, y: mp.atan((a - b * x * y) / (x + c * y))
    if prefix == "MVAO":
        return lambda x, y: mp.exp(a * mp.cos(b * x / (c * y)))
    if prefix == "MVAP":
        return lambda x, y: a * y * mp.sqrt(b * x**2 + c * y**2)
    if prefix == "MVAQ":
        return lambda x, y: a * mp.log(mp.sqrt(b**2 * x**2 + c * y**2) - b * x)
    if prefix == "MVAR":
        return lambda x, y, z: a * z**2 + b * x * z / y + c * y * z**3
    if prefix == "MVAS":
        return lambda x, y, z: a * x / (b * y**2 + c * z**2)
    if prefix in ("MVAT", "MVAX", "MVAY"):
        return lambda x, y, z: mp.cos(a * x * mp.sin(b * y * mp.cos(c * z)))
    if prefix in ("MVAU", "MVAZ", "MVBA"):
        return lambda x, y, z: mp.sqrt(a * x**2 + mp.sqrt(b * y**2 + mp.sqrt(c * z**2 + 1)))
    if prefix == "MVAV":
        return lambda x, y: mp.log(a * x**2 + b * x * y + c * y**2)
    if prefix == "MVAW":
        return lambda x, y: a * mp.sqrt(x) * mp.sin(b * y / (c * x))
    raise AssertionError(prefix)


NESTED_COORDINATES = {"MVAT": 0, "MVAX": 1, "MVAY": 2, "MVAU": 0, "MVAZ": 1, "MVBA": 2}


def exact_at(answer, point):
    expression = answer.expected
    values = {
        name: sp.Rational(str(value))
        for name, value in zip("xyz"[: len(point)], point, strict=True)
    }
    return mp.mpf(
        str(expression.subs({s: values[s.name] for s in expression.free_symbols}).evalf(45))
    )


@pytest.mark.parametrize("generator", PARTIALS, ids=lambda item: item.prefix)
def test_partial_derivatives_match_independent_difference_quotients(generator):
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
            function = numeric_function(prefix, *coefficients)
            if prefix == "MVAK":
                point = mp.mpf(0), mp.mpf(params.b)
            elif prefix == "MVAL":
                point = mp.mpf(0), mp.mpf(0)
            elif prefix in NESTED_COORDINATES or prefix in ("MVAR", "MVAS"):
                point = tuple(map(mp.mpf, ("1.2", "0.8", "1.3")))
            else:
                point = tuple(map(mp.mpf, ("1.2", "0.8")))
            parts = answer.components if isinstance(answer, OrderedAnswer) else (answer,)
            if prefix in NESTED_COORDINATES:
                coordinates = (NESTED_COORDINATES[prefix],)
            else:
                coordinates = range(len(point))
            numeric = [
                mp.diff(function, point, tuple(int(i == coordinate) for i in range(len(point))))
                for coordinate in coordinates
            ]
            for part, expected in zip(parts[: len(numeric)], numeric, strict=True):
                assert abs(exact_at(part, point) - expected) < mp.mpf("1e-39")
            if prefix in ("MVAV", "MVAW"):
                coefficient = exact_at(parts[-1], point)
                factor = function(*point) if prefix == "MVAW" else 1
                assert abs(
                    sum(x * dx for x, dx in zip(point, numeric, strict=True)) - coefficient * factor
                ) < mp.mpf("1e-39")
