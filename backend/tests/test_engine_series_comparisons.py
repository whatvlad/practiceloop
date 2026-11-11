"""#272: direct finite sums, positive integral interpolations and comparison orders."""

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

SERIES = [g for g in generators() if g.evaluate.__module__.endswith("._series_comparisons")]
CONVERGENT = {
    "SRAA",
    "SRAB",
    "SRAC",
    "SRAE",
    "SRAG",
    "SRAH",
    "SRAI",
    "SRAJ",
    "SRAL",
    "SRAM",
    "SRAP",
    "SRAQ",
    "SRAT",
}


def original_term(prefix, a, b, c, n):
    ratio = mp.mpf(a + b) / (a + b + c)
    terms = {
        "SRAA": lambda: ratio**n,
        "SRAB": lambda: mp.mpf(a) / ((n + b) * (n + b + 1)),
        "SRAC": lambda: a * (n - 1) / mp.factorial(n),
        "SRAD": lambda: a / (mp.sqrt(n + b + 1) + mp.sqrt(n + b)),
        "SRAE": lambda: mp.mpf(a) / (n * n + b * b),
        "SRAF": lambda: a * (n - b) / (n * (n + b)),
        "SRAG": lambda: a * mp.log(n) / n ** (2 + c % 2),
        "SRAH": lambda: a / (n * mp.sqrt(n + b)),
        "SRAI": lambda: a * mp.exp(b * n) / (mp.exp(2 * b * n) + c * c),
        "SRAJ": lambda: (a * n + b) / (n**3 + c),
        "SRAK": lambda: a * mp.sqrt(n * n + b) / (n * n + c),
        "SRAL": lambda: c * mp.sin(mp.pi / ((a + 1) * (b + 1) ** n)),
        "SRAM": lambda: c * (mp.power(a + 1, n) + mp.exp(n)) / (mp.exp(n) + mp.power(a + 2, n)),
        "SRAN": lambda: (
            c * (mp.power(a + b + 1, n) + n) / (n * mp.power(a + b + 1, n) + mp.power(a + 1, n))
        ),
        "SRAO": lambda: a * (n * n + b) / mp.sqrt(c * n**6 - 1),
        "SRAP": lambda: (a * n * n + b) / (n**4 + c),
        "SRAQ": lambda: a * mp.expm1(n) / (mp.power(b + 2, n) - 1),
        "SRAR": lambda: c * mp.power(a + 1, n) * (1 + mp.power(b + 1, -n)),
        "SRAS": lambda: c * mp.sin(mp.pi / ((a + 1) * n * n)) / mp.sin(mp.pi / ((b + 1) * n)),
        "SRAT": lambda: a * (mp.factorial(n) + b) / mp.factorial(n + 2 + c % 2),
    }
    return terms[prefix]()


def number(value):
    return mp.mpf(str(sp.N(value, 40)))


def check_partial_formula(prefix, a, b, c, answer, visual):
    start = {"SRAA": 0, "SRAB": c + 1, "SRAC": 2, "SRAD": 1}[prefix]
    coefficients = [number(part.expected) for part in answer.components[:-2]]
    for end in (start, start + 4, start + 17):
        actual = sum(original_term(prefix, a, b, c, n) for n in range(start, end + 1))
        if prefix == "SRAA":
            expected = coefficients[0] * (1 - (mp.mpf(a + b) / (a + b + c)) ** (end + 1))
        elif prefix == "SRAB":
            expected = coefficients[0] - coefficients[1] / (end + b + 1)
        elif prefix == "SRAC":
            expected = coefficients[0] - coefficients[1] / mp.factorial(end)
        else:
            expected = coefficients[0] * mp.sqrt(end + b + 1) - coefficients[1]
        assert abs(expected - actual) < mp.mpf("1e-30")
    for end, value in visual["paths"][0]["points"]:
        actual = sum(original_term(prefix, a, b, c, n) for n in range(start, int(end) + 1))
        assert value == pytest.approx(float(actual), abs=1e-12)
    classification = answer.components[-2].expected
    assert classification == ("converges" if prefix in CONVERGENT else "diverges")
    total = answer.components[-1].expected
    if prefix == "SRAD":
        assert total == sp.oo and coefficients[0] > 0
    else:
        assert abs(number(total) - coefficients[0]) < mp.mpf("1e-30")


def check_comparison(prefix, a, b, c):
    if prefix in {"SRAE", "SRAF", "SRAG", "SRAH", "SRAI"}:
        start = {"SRAE": c, "SRAF": 3 * b, "SRAG": b + 2, "SRAH": c, "SRAI": c}[prefix]
        for multiplier in (1, 2, 10):
            x = mp.mpf(start * multiplier)
            assert original_term(prefix, a, b, c, x) > 0
            assert mp.diff(lambda t: original_term(prefix, a, b, c, t), x) < 0
    if prefix == "SRAL":
        for n in (1, 5, 20):
            value = original_term(prefix, a, b, c, n)
            bound = c * mp.pi / ((a + 1) * (b + 1) ** n)
            assert 0 < value <= bound
        return
    if prefix == "SRAM":
        for n in (1, 5, 20):
            bound = c * ((mp.mpf(a + 1) / (a + 2)) ** n + (mp.e / (a + 2)) ** n)
            assert 0 < original_term(prefix, a, b, c, n) <= bound
        assert mp.e < a + 2
        return
    if prefix == "SRAN":
        for n in (1, 5, 20):
            assert original_term(prefix, a, b, c, n) >= mp.mpf(c) / (2 * n)
        return
    if prefix in {"SRAI", "SRAQ", "SRAR"}:
        n = mp.mpf(200)
        scale = (
            mp.exp(-b * n)
            if prefix == "SRAI"
            else (mp.e / (b + 2)) ** n
            if prefix == "SRAQ"
            else mp.power(a + 1, n)
        )
        coefficient = c if prefix == "SRAR" else a
        assert abs(original_term(prefix, a, b, c, n) / scale - coefficient) < mp.mpf("1e-18")
        return
    powers = {
        "SRAE": (2, a),
        "SRAF": (1, a),
        "SRAH": (mp.mpf("1.5"), a),
        "SRAJ": (2, a),
        "SRAK": (1, a),
        "SRAO": (1, a / mp.sqrt(c)),
        "SRAP": (2, a),
        "SRAS": (1, mp.mpf(c * (b + 1)) / (a + 1)),
        "SRAT": (2 + c % 2, a),
    }
    if prefix == "SRAG":
        n = mp.mpf("1e10")
        assert abs(original_term(prefix, a, b, c, n) * n ** (2 + c % 2) / mp.log(n) - a) < mp.mpf(
            "1e-30"
        )
        return
    power, coefficient = powers[prefix]
    n = mp.mpf(1000000) if prefix == "SRAT" else mp.mpf("1e12")
    assert abs(original_term(prefix, a, b, c, n) * n**power - coefficient) < mp.mpf("1e-4")
    assert (power > 1) == (prefix in CONVERGENT)


@pytest.mark.parametrize("generator", SERIES, ids=lambda g: g.prefix)
def test_full_sweep_verifies_partial_sums_and_comparison_orders(generator):
    seen = set()
    checked_answers = set()
    with mp.workdps(40):
        for seed in sweep(1000):
            params = generator.draw(seed)
            coefficients = params.a, params.b, params.c
            if coefficients in seen:
                continue
            seen.add(coefficients)
            answer = generator.build(params).answer
            if generator.prefix in {"SRAA", "SRAB", "SRAC", "SRAD"}:
                visual = validate_plot(generator.solution_visual(params))
                check_partial_formula(generator.prefix, *coefficients, answer, visual)
                assert "pdfliteral" in graph(visual)
            else:
                expected = "converges" if generator.prefix in CONVERGENT else "diverges"
                assert answer.expected == expected
                check_comparison(generator.prefix, *coefficients)
            if answer not in checked_answers:
                tree = parse_answer_input(source(answer), answer.kind, contract=answer.contract)
                assert answer.check(tree) == "correct"
                checked_answers.add(answer)
