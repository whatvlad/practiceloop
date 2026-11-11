"""#277: independent domain witnesses and multivariable limit checks."""

import itertools

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.answers.logic import truth
from app.engine.answers.region import RegionLogicAnswer
from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

GENERATORS = [
    generator
    for generator in generators()
    if generator.evaluate.__module__.endswith("._multivariable_domains")
]
DELTAS = (-1, 0, 1)


def witnesses(prefix, a, b, c):
    if prefix in ("MVAA", "MVAC"):
        for x, delta in itertools.product(DELTAS, repeat=2):
            boundary = a * mp.sin(b * x) + c if prefix == "MVAA" else a * x**2 + b
            y = boundary + delta
            value = y - boundary if prefix == "MVAA" else boundary - y
            yield (value > 0, value >= 0, value < 0), value > 0
    elif prefix == "MVAB":
        for denominator, numerator in itertools.product(DELTAS, repeat=2):
            product = denominator * numerator
            yield (
                (product >= 0, denominator != 0, product > 0),
                denominator != 0 and numerator / denominator >= 0,
            )
    elif prefix == "MVAD":
        lower, upper = a**2, (a + b) ** 2
        for radius_squared in (0, lower, (lower + upper) / 2, upper, upper + 1):
            denominator = upper - radius_squared
            yield (
                (radius_squared > lower, radius_squared < upper, radius_squared >= lower),
                denominator != 0 and (radius_squared - lower) / denominator > 0,
            )
    elif prefix == "MVAE":
        for x, z in itertools.product(range(a - 1, a + 2), range(b - 1, b + 2)):
            yield (x >= a, z <= b, x > a), mp.im(mp.sqrt(x - a) + c * mp.sqrt(b - z)) == 0
    elif prefix == "MVAF":
        center = a * a + b + c
        lower, upper = center - 1, center + 1
        for radius_squared in (0, lower, center, upper, upper + 1):
            yield (
                (radius_squared >= lower, radius_squared <= upper, radius_squared > lower),
                mp.im(mp.acos(radius_squared - center)) == 0,
            )


def verify_limit(prefix, answer, a, b, c):
    with mp.workdps(40):
        radius = mp.mpf("0.0001")
        for angle in (0, mp.pi / 6, mp.pi / 4, mp.pi / 2):
            x, y = radius * mp.cos(angle), radius * mp.sin(angle)
            if prefix == "MVAG":
                assert abs(mp.sin(a * x**4 - b * y**4) / (c * radius**2)) < mp.mpf("0.000001")
            elif prefix == "MVAH":
                value = (1 - mp.cos(a * x * x + b * y * y)) / (c * radius**4)
                coefficient = a * mp.cos(angle) ** 2 + b * mp.sin(angle) ** 2
                assert abs(value - coefficient**2 / (2 * c)) < mp.mpf("0.0000000001")
            elif prefix == "MVAI":
                assert abs(a * x * y * y / (b * x * x + c * y * y)) < mp.mpf("0.001")
            else:
                assert abs(a * x * x * mp.cos(b / (x**4 + c * y**4))) < mp.mpf("0.000001")
        if prefix == "MVAH":
            assert (
                str(answer.expected) == "does_not_exist"
                if a != b
                else (answer.expected == sp.Rational(a * a, 2 * c))
            )
        else:
            assert answer.expected == 0


@pytest.mark.parametrize("generator", GENERATORS, ids=lambda item: item.prefix)
def test_domain_or_limit(generator):
    seen = set()
    for seed in sweep(1000):
        params = generator.draw(seed)
        coefficients = params.a, params.b, params.c
        if coefficients in seen:
            continue
        seen.add(coefficients)
        built = generator.build(params)
        answer = built.answer
        prefix = generator.prefix
        expected_input = source(answer)
        assert (
            answer.check(
                parse_answer_input(
                    expected_input, generator.contract.kind, contract=generator.contract
                )
            )
            == "correct"
        )
        if isinstance(answer, RegionLogicAnswer):
            rows = set()
            for row, defined in witnesses(prefix, *coefficients):
                rows.add(row)
                assert truth(answer.expected, dict(zip(answer.atoms, row, strict=True))) == defined
            assert rows == set(answer.rows)
            equivalent = "p&!r" if prefix in ("MVAA", "MVAC") else "p&q"
            assert (
                answer.check(
                    parse_answer_input(
                        equivalent, generator.contract.kind, contract=generator.contract
                    )
                )
                == "correct"
            )
            if prefix in ("MVAD", "MVAF"):
                result = answer.check(
                    parse_answer_input(
                        "p&q&r", generator.contract.kind, contract=generator.contract
                    )
                )
                assert result == ("correct" if prefix == "MVAD" else "incorrect")
        else:
            verify_limit(prefix, answer, *coefficients)
        visual = generator.solution_visual(params)
        if visual is not None:
            assert validate_plot(visual) is not None
            assert graph(visual)
