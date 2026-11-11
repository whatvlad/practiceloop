"""#268: numerical quadrature of original integrands and direct Riemann sums."""

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

DEFINITE = [g for g in generators() if g.evaluate.__module__.endswith("._definite_integrals")]


def original_integral(prefix, a, b, c):
    forms = {
        "INCZ": (lambda x: a * mp.sqrt(x) + b / mp.sqrt(x), c, c + 2),
        "INDA": (lambda x: (x - a) / (x + b), 0, c + 1),
        "INDB": (lambda x: c / (x * x + a * a), 0, b + 1),
        "INDC": (lambda x: x * (a + b * x**3), -a, c),
        "INDD": (lambda x: a / x**3 - b / x**2 + c / x**4, 1, a + 1),
        "INDE": (lambda x: a * mp.tan(b * x) ** 2, 0, mp.pi / (3 * b)),
        "INDF": (lambda x: a * x ** (c + 1), 0, 1),
        "INDG": (lambda x: b * mp.cos(mp.pi * x / (a + 2)), 0, 1),
        "INDH": (lambda x: a * mp.sqrt(b + c * x), 0, 1),
        "INDI": (lambda x: c * x * mp.exp(-a * x), -b, 1),
        "INDJ": (lambda x: c * x**2 * mp.exp(a * x), 0, b),
        "INDK": (lambda x: c * mp.log(x) / x**2, mp.exp(mp.mpf(1) / (a + 1)), mp.exp(b)),
        "INDL": (lambda x: a * x * mp.sin(b * x), 0, mp.pi / ((c + 2) * b)),
        "INDM": (lambda x: a * x * (c + mp.cos(b * x)), 0, mp.pi / b),
        "INDN": (lambda x: a * mp.asin(x / b), 0, b),
        "INDO": (lambda x: a * mp.sin(b * x) * mp.exp(c * mp.cos(b * x)), 0, mp.pi / b),
        "INDP": (lambda x: a * x / mp.sqrt(x + b), 1, c + 2),
        "INDQ": (lambda x: a * x * mp.sqrt(x + b), 0, c + 1),
        "INDR": (lambda x: a * mp.log(x), 1, mp.exp(b)),
        "INDS": (lambda x: a / (mp.sqrt(x) * (b - x)), 0, mp.mpf(b) / (c + 1) ** 2),
        "INDT": (lambda x: a * mp.sqrt(max(0, b**2 - x**2)), 0, b),
        "INDU": (lambda x: a * mp.exp(b * x) / (c**2 + mp.exp(2 * b * x)), 0, mp.log(c + 1) / b),
        "INDV": (lambda x: a * x * mp.cos(b * x), 0, mp.pi / b),
    }
    return forms[prefix]


@pytest.mark.parametrize("generator", DEFINITE, ids=lambda g: g.prefix)
def test_values_match_independent_quadrature(generator):
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
            function, lo, hi = original_integral(generator.prefix, *coefficients)
            integral = mp.quad(function, [lo, hi])
            expected = mp.mpf(str(sp.N(task.answer.expected, 40)))
            tolerance = mp.mpf("1e-18") if generator.prefix == "INDS" else mp.mpf("1e-28")
            assert abs(integral - expected) < tolerance * max(1, abs(integral))
            if generator.prefix in {"INDF", "INDG", "INDH"}:
                n = 128
                # Evaluate the original finite sums, before taking their limit.
                if generator.prefix == "INDF":
                    total = params.a * sum(mp.mpf(k) ** (params.c + 1) for k in range(1, n + 1))
                    total /= n ** (params.c + 2)
                elif generator.prefix == "INDG":
                    total = (
                        params.b
                        * sum(mp.cos(mp.pi * k / ((params.a + 2) * n)) for k in range(1, n + 1))
                        / n
                    )
                else:
                    total = (
                        params.a
                        * sum(mp.sqrt(params.b * n + params.c * k) for k in range(1, n + 1))
                        / (n * mp.sqrt(n))
                    )
                assert abs(total - expected) <= abs(function(hi) - function(lo)) / n
            if task.answer not in checked_answers:
                tree = parse_answer_input(
                    source(task.answer), task.answer.kind, contract=task.answer.contract
                )
                assert task.answer.check(tree) == "correct"
                checked_answers.add(task.answer)


@pytest.mark.parametrize("prefix", ["INDF", "INDG", "INDH", "INDT"])
def test_visuals_match_sampled_integrands_and_render_on_worksheets(prefix):
    generator = next(g for g in DEFINITE if g.prefix == prefix)
    for seed in (3, 200, 999):
        params = generator.draw(seed)
        visual = validate_plot(generator.solution_visual(params))
        function, _, _ = original_integral(prefix, params.a, params.b, params.c)
        for x, y in visual["paths"][0]["points"]:
            assert y == pytest.approx(float(function(x)), abs=1e-7)
        if prefix != "INDT":
            for index, rectangle in enumerate(visual["paths"][1:], start=1):
                assert rectangle["points"][2] == pytest.approx(
                    [index / 5, float(function(index / 5))]
                )
        assert "pdfliteral" in graph(visual)
