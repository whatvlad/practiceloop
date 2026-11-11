"""#271: independent tails, asymptotic comparisons and unbounded applications."""

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

IMPROPER = [g for g in generators() if g.evaluate.__module__.endswith("._improper_integrals")]
CONVERGENT = {"IPAA", "IPAD", "IPAE", "IPAG", "IPAI", "IPAJ", "IPAK", "IPAM", "IPAP"}


def number(value):
    return mp.mpf(str(sp.N(value, 40)))


def original_function(prefix, a, b, c):
    numerator_base = c + 1
    denominator_base = numerator_base + b
    functions = {
        "IPAA": lambda x: a / (x * (x - b)),
        "IPAB": lambda x: b * mp.sqrt(x) / (x + a),
        "IPAC": lambda x: a * x * mp.cos(b * x),
        "IPAD": lambda x: a * mp.exp(-b * x) / mp.sqrt(c + mp.exp(-b * x)),
        "IPAE": lambda x: a / ((x + b) ** 2 + c * c),
        "IPAF": lambda x: a * x * mp.exp(b * x),
        "IPAG": lambda x: a / (x * (mp.sqrt(x) + b)),
        "IPAH": lambda x: a / (mp.sqrt(x) + b) ** 2,
        "IPAI": lambda x: a * x * (x + b) / (x**4 + x + c),
        "IPAJ": lambda x: (
            a * (mp.power(numerator_base, x) + 1) / (mp.power(denominator_base, x) + 1)
        ),
        "IPAK": lambda x: (a * x + mp.sin(b * x)) / x**3,
        "IPAL": lambda x: (a + c + 1 + a * mp.cos(b * x)) / (mp.sqrt(x) + c + 1),
        "IPAM": lambda x: (a * mp.sqrt(x) + b) / (x * (x + c)),
        "IPAN": lambda x: a * x * x / mp.sqrt(x**5 - b),
        "IPAO": lambda x: mp.expm1(mp.mpf(a) / x),
        "IPAP": lambda x: mp.sin(mp.mpf(a) / x) ** 2,
        "IPAQ": lambda x: a * x * x / (x**3 - b * mp.sin(c * x)),
    }
    return functions[prefix]


def check_comparison(prefix, a, b, c):
    function = original_function(prefix, a, b, c)
    if prefix == "IPAL":
        for x in ((c + 1) ** 2, 100, 10000):
            assert function(mp.mpf(x)) * mp.sqrt(x) >= (c + 1) / 2
        return
    if prefix == "IPAJ":
        x = mp.mpf(200)
        ratio = function(x) / mp.power(mp.mpf(c + 1) / (c + 1 + b), x)
        assert abs(ratio - a) < mp.mpf("1e-18")
        return
    powers = {
        "IPAG": (mp.mpf("1.5"), a),
        "IPAH": (1, a),
        "IPAI": (2, a),
        "IPAK": (2, a),
        "IPAM": (mp.mpf("1.5"), a),
        "IPAN": (mp.mpf("0.5"), a),
        "IPAO": (1, a),
        "IPAP": (2, a * a),
        "IPAQ": (1, a),
    }
    power, coefficient = powers[prefix]
    x = mp.mpf("1e16")
    ratio = function(x) * x**power
    assert abs(ratio - coefficient) < mp.mpf("1e-6")
    assert (power > 1) == (prefix in CONVERGENT)


@pytest.mark.parametrize("generator", IMPROPER, ids=lambda g: g.prefix)
def test_full_sweep_checks_original_tails_and_comparison_orders(generator):
    seen = set()
    checked_answers = set()
    with mp.workdps(40):
        for seed in sweep(1000):
            params = generator.draw(seed)
            coefficients = params.a, params.b, params.c
            if coefficients in seen:
                continue
            seen.add(coefficients)
            a, b, c = coefficients
            task = generator.build(params)
            answer = task.answer
            prefix = generator.prefix
            if prefix in {"IPAA", "IPAD"}:
                assert answer.components[0].expected == "converges"
                lo = b + c if prefix == "IPAA" else 0
                actual = mp.quad(original_function(prefix, a, b, c), [lo, mp.inf])
                assert abs(actual - number(answer.components[1].expected)) < mp.mpf("1e-28")
            elif prefix == "IPAE":
                function = original_function(prefix, a, b, c)
                left = mp.quad(function, [-mp.inf, 0])
                right = mp.quad(function, [0, mp.inf])
                assert answer.components[0].expected == "converges"
                for part, value in zip(
                    answer.components[1:], (left, right, left + right), strict=True
                ):
                    assert abs(number(part.expected) - value) < mp.mpf("1e-28")
            elif prefix == "IPAF":
                assert answer.components[0].expected == "diverges"
                left = mp.quad(original_function(prefix, a, b, c), [-mp.inf, 0])
                assert abs(left - number(answer.components[1].expected)) < mp.mpf("1e-28")
                assert answer.components[2].expected == answer.components[3].expected == sp.oo
                assert original_function(prefix, a, b, c)(10) > mp.exp(9)
            elif prefix == "IPAB":
                assert answer.components[0].expected == "diverges"
                assert answer.components[1].expected == sp.oo
                x = mp.mpf("1e16")
                assert abs(original_function(prefix, a, b, c)(x) * mp.sqrt(x) - b) < mp.mpf("1e-12")
            elif prefix == "IPAC":
                assert answer.components[0].expected == "diverges"
                assert answer.components[1].expected == "does_not_exist"
                function = original_function(prefix, a, b, c)
                lo = 2 * mp.pi / b
                for n in (2, 4):
                    assert abs(mp.quad(function, [lo, 2 * mp.pi * n / b])) < mp.mpf("1e-25")
                    assert mp.quad(function, [lo, (2 * mp.pi * n + mp.pi / 2) / b]) > n * mp.mpf(
                        a
                    ) / (b * b)
            elif prefix == "IPAR":
                actual = mp.quad(lambda x, a=a, b=b: a / (x * x + b * b), [-mp.inf, 0, mp.inf])
                assert abs(number(answer.expected) - actual) < mp.mpf("1e-28")
            elif prefix == "IPAS":
                actual = mp.quad(lambda x, a=a, b=b: mp.pi * (a * mp.exp(-b * x)) ** 2, [0, mp.inf])
                assert abs(number(answer.expected) - actual) < mp.mpf("1e-28")
            elif prefix == "IPAT":
                power = mp.mpf(b + 1) / 2
                assert answer.expected == ("finite" if power > 1 else "infinite")
                for x in (mp.mpf(1), mp.mpf(10), mp.mpf(100)):
                    radius = a / x**power
                    slope = -a * power / x ** (power + 1)
                    density = 2 * mp.pi * radius * mp.sqrt(1 + slope * slope)
                    assert density >= 2 * mp.pi * radius
                    assert density <= 2 * mp.pi * radius * mp.sqrt(1 + (a * power) ** 2)
            else:
                assert answer.expected == ("converges" if prefix in CONVERGENT else "diverges")
                check_comparison(prefix, a, b, c)
            if answer not in checked_answers:
                contract = getattr(answer, "contract", None)
                tree = parse_answer_input(source(answer), answer.kind, contract=contract)
                assert answer.check(tree) == "correct"
                checked_answers.add(answer)
            if prefix in {"IPAC", "IPAR", "IPAS", "IPAT"}:
                visual = validate_plot(generator.solution_visual(params))
                assert "pdfliteral" in graph(visual)
                if prefix != "IPAC":
                    assert visual["paths"][-1]["points"][0][1] == 0
