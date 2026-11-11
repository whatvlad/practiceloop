"""#270: numerical shell, washer and surface integrals from the original profiles."""

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

REVOLUTIONS = [
    g for g in generators() if g.evaluate.__module__.endswith("._revolution_applications")
]


def volume_integral(prefix, a, b, c):
    theta = mp.pi / (b + 3)
    coordinate = a + c
    cases = {
        "INFB": (lambda x: mp.pi * (a * x * (b - x)) ** 2, 0, b),
        "INFC": (lambda x: 2 * mp.pi * x * (a + 1) / mp.sqrt(x * x + b * b), 0, c),
        "INFD": (lambda x: mp.pi * (a * mp.tan(c * x)) ** 2, 0, theta / c),
        "INFE": (lambda x: 2 * mp.pi * x * a * (mp.sqrt(x / b) - (x / b) ** 2), 0, b),
        "INFF": (lambda x: 2 * mp.pi * a * x**4, 0, b),
        "INFG": (lambda x: 2 * mp.pi * x * (mp.mpf(a) / x), b, b + c),
        "INFH": (lambda x: mp.pi * ((2 * a + b - x) ** 2 - (a * (a + b) / x) ** 2), a, a + b),
        "INFI": (lambda x: mp.pi * (a * mp.sin(b * x) * mp.cos(b * x)) ** 2, 0, mp.pi / (2 * b)),
        "INFJ": (
            lambda x: mp.pi * (coordinate**2 - (coordinate - a * mp.sin(b * x)) ** 2),
            0,
            mp.pi / b,
        ),
        "INFK": (lambda x: 2 * mp.pi * (b + c - x) * a * x * (b - x), 0, b),
        "INFT": (
            lambda x: mp.pi * ((a * mp.sin(b * x)) ** 2 - (2 * a * b * x / mp.pi) ** 2),
            0,
            mp.pi / (2 * b),
        ),
        "INFU": (lambda x: mp.pi * (mp.mpf(a) / b * mp.sin(b * x)) ** 2, 0, mp.pi / b),
        "INFV": (
            lambda x: 4 * mp.pi * x * mp.sqrt(max(0, a * a - (x - (a + b + c)) ** 2)),
            b + c,
            2 * a + b + c,
        ),
    }
    return cases[prefix]


def surface_data(prefix, a, b, c):
    lower = mp.mpf(b + 3) / (4 * a)
    cases = {
        "INFL": (
            lambda x: mp.mpf(a) / b * mp.cos(b * x),
            lambda x: -a * mp.sin(b * x),
            0,
            mp.pi / (2 * b),
            False,
        ),
        "INFM": (
            lambda x: mp.sqrt(x + a * a),
            lambda x: 1 / (2 * mp.sqrt(x + a * a)),
            -a * a,
            b + c,
            False,
        ),
        "INFN": (lambda x: a * mp.log(x), lambda x: mp.mpf(a) / x, 1, mp.sqrt(b + c), True),
        "INFO": (lambda x: a * abs(x - b) + c, lambda x: -a if x < b else a, 0, 2 * b, True),
        "INFP": (
            lambda x: mp.sqrt((a + b) ** 2 - x * x),
            lambda x: -x / mp.sqrt((a + b) ** 2 - x * x),
            -a,
            a,
            False,
        ),
        "INFQ": (
            lambda x: mp.sqrt(a * x) * (1 - a * x / 3) / a,
            lambda x: (1 - a * x) / (2 * mp.sqrt(a * x)),
            lower,
            mp.mpf(3) / a,
            False,
        ),
        "INFR": (lambda x: (x - b) / a, lambda x: mp.mpf(1) / a, b, b + c, True),
        "INFS": (lambda x: mp.mpf(a) * x * x / 2, lambda x: a * x, 0, mp.sqrt(b + c), True),
        "INFU": (
            lambda x: mp.mpf(a) / b * mp.sin(b * x),
            lambda x: a * mp.cos(b * x),
            0,
            mp.pi / b,
            False,
        ),
    }
    return cases[prefix]


def surface_integral(prefix, a, b, c):
    curve, slope, lo, hi, vertical = surface_data(prefix, a, b, c)
    for fraction in (mp.mpf("0.2"), mp.mpf("0.7")):
        x = lo + (hi - lo) * fraction
        assert abs(mp.diff(curve, x) - slope(x)) < mp.mpf("1e-27")
    if prefix == "INFM":
        return mp.quad(
            lambda q: 2 * mp.pi * mp.sqrt(q) * mp.sqrt(1 + 1 / (4 * q)), [0, a * a + b + c]
        )
    return mp.quad(
        lambda x: 2 * mp.pi * (x if vertical else curve(x)) * mp.sqrt(1 + slope(x) ** 2), [lo, hi]
    )


@pytest.mark.parametrize("generator", REVOLUTIONS, ids=lambda g: g.prefix)
def test_generated_results_match_independent_revolution_integrals(generator):
    seen = set()
    checked_answers = set()
    with mp.workdps(40):
        for seed in sweep(1000):
            params = generator.draw(seed)
            coefficients = params.a, params.b, params.c
            if coefficients in seen:
                continue
            seen.add(coefficients)
            task = generator.build(params)
            answer = task.answer
            components = answer.components if isinstance(answer, OrderedAnswer) else (answer,)
            expected = [mp.mpf(str(sp.N(part.expected, 40))) for part in components]
            if generator.prefix in {"INFL", "INFM", "INFN", "INFO", "INFP", "INFQ", "INFR", "INFS"}:
                actual = [surface_integral(generator.prefix, *coefficients)]
            else:
                function, lo, hi = volume_integral(generator.prefix, *coefficients)
                actual = [mp.quad(function, [lo, hi])]
                if generator.prefix == "INFU":
                    actual.append(surface_integral(generator.prefix, *coefficients))
            for exact, numeric in zip(expected, actual, strict=True):
                assert numeric > 0
                assert abs(exact - numeric) < mp.mpf("1e-25") * max(1, abs(numeric))
            visual = validate_plot(generator.solution_visual(params))
            axis = visual["paths"][-1]
            assert axis["label"] == "Rotation axis"
            first, last = axis["points"]
            assert first[0] == last[0] or first[1] == last[1]
            if generator.prefix == "INFJ":
                assert first[1] == last[1] == params.a + params.c
            if generator.prefix == "INFK":
                assert first[0] == last[0] == params.b + params.c
            if generator.prefix == "INFV":
                assert min(x for p in visual["paths"][:-1] for x, _ in p["points"]) > 0
            if answer not in checked_answers:
                tree = parse_answer_input(
                    source(answer), answer.kind, contract=getattr(answer, "contract", None)
                )
                assert answer.check(tree) == "correct"
                checked_answers.add(answer)
            if seed < 5:
                assert "pdfliteral" in graph(visual)
