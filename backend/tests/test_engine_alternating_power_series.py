"""#274: original alternating magnitudes and every power-series endpoint."""

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

SERIES = [g for g in generators() if g.evaluate.__module__.endswith("._alternating_power_series")]
POWER = {"SRBQ", "SRBR", "SRBS", "SRBT", "SRBU"}


def magnitude(prefix, a, b, c, n):
    small = a + 1
    middle = small + b
    large = middle + c
    cases = {
        "SRBH": lambda: b * (mp.sqrt(n * n + a * a) - n),
        "SRBI": lambda: mp.power(small, n) / (mp.power(middle, n) + mp.power(large, n)),
        "SRBJ": lambda: mp.sin(mp.pi / ((a + 2) * n)),
        "SRBK": lambda: b * mp.power(a + 1, n) / mp.factorial(n),
        "SRBL": lambda: mp.mpf(c) / (mp.power(a + 1, n) + b),
        "SRBM": lambda: a * n / (n * n + b * b),
        "SRBN": lambda: mp.power(a * n / (b * n + c), n),
        "SRBO": lambda: b * mp.expm1(mp.mpf(a) / n),
        "SRBP": lambda: abs(mp.sin(a * n + c)) / mp.power(b + 1, n),
    }
    return cases[prefix]()


def power_term(prefix, a, b, c, x, n):
    cases = {
        "SRBQ": lambda: mp.power((x - a) / (b * mp.e), n) / n ** (1 + c % 2),
        "SRBR": lambda: mp.power(a * x - b, n),
        "SRBS": lambda: mp.power(c * (x - a), n) / mp.factorial(n),
        "SRBT": lambda: mp.power(a * (x + b), n) / (mp.power(c + 2, n) - mp.power(c + 1, n)),
        "SRBU": lambda: n * mp.power(x + a, 2 * n) / (mp.power(b + 1, n) + c),
    }
    return cases[prefix]()


def check_power_domain(prefix, a, b, c, answer, visual):
    if prefix == "SRBS":
        assert answer.expected == sp.S.Reals
        for x in (a - 10, a + 10):
            ratio = abs(
                power_term(prefix, a, b, c, mp.mpf(x), mp.mpf(10001))
                / power_term(prefix, a, b, c, mp.mpf(x), mp.mpf(10000))
            )
            assert ratio < 1
        assert all(path.get("arrow") for path in visual["paths"])
        return
    if prefix == "SRBQ":
        radius = mp.mpf(b) * mp.e
        left = sp.Integer(a) - b * sp.E
        right = sp.Integer(a) + b * sp.E
        center = mp.mpf(a)
        include_left = True
        include_right = c % 2 == 1
    elif prefix == "SRBR":
        center = mp.mpf(b) / a
        radius = mp.mpf(1) / a
        left, right = sp.Rational(b - 1, a), sp.Rational(b + 1, a)
        include_left = include_right = False
    elif prefix == "SRBT":
        center = mp.mpf(-b)
        radius = mp.mpf(c + 2) / a
        left, right = -b - sp.Rational(c + 2, a), -b + sp.Rational(c + 2, a)
        include_left = include_right = False
    else:
        center = mp.mpf(-a)
        radius = mp.sqrt(b + 1)
        left, right = -a - sp.sqrt(b + 1), -a + sp.sqrt(b + 1)
        include_left = include_right = False
    assert answer.expected == sp.Interval(
        left, right, left_open=not include_left, right_open=not include_right
    )
    for side in (-1, 1):
        inside = center + side * radius / 2
        outside = center + side * radius * mp.mpf("1.5")
        n = mp.mpf(500)
        inner_root = mp.exp(mp.log(abs(power_term(prefix, a, b, c, inside, n))) / n)
        outer_root = mp.exp(mp.log(abs(power_term(prefix, a, b, c, outside, n))) / n)
        assert inner_root < 1 < outer_root
    for endpoint, marker, included in zip(
        (left, right), visual["points"], (include_left, include_right), strict=True
    ):
        assert marker["x"] == pytest.approx(float(endpoint))
        assert marker["included"] == included
    if prefix == "SRBQ":
        for n in (4, 5, 100):
            left_term = power_term(prefix, a, b, c, center - radius, mp.mpf(n))
            right_term = power_term(prefix, a, b, c, center + radius, mp.mpf(n))
            assert abs(left_term - (-1) ** n / mp.mpf(n) ** (1 + c % 2)) < mp.mpf("1e-25")
            assert abs(right_term - 1 / mp.mpf(n) ** (1 + c % 2)) < mp.mpf("1e-25")
    else:
        for x in (center - radius, center + radius):
            assert abs(power_term(prefix, a, b, c, x, mp.mpf(100))) > mp.mpf("0.9")


@pytest.mark.parametrize("generator", SERIES, ids=lambda g: g.prefix)
def test_full_sweep_checks_alternation_absolute_convergence_and_endpoints(generator):
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
            answer = generator.build(params).answer
            prefix = generator.prefix
            if prefix in POWER:
                visual = validate_plot(generator.solution_visual(params))
                check_power_domain(prefix, a, b, c, answer, visual)
                assert "pdfliteral" in graph(visual)
            elif prefix in {"SRBH", "SRBI", "SRBJ", "SRBK"}:
                assert answer.expected == "converges"
                start = max(b + 1, a + 1) if prefix in {"SRBJ", "SRBK"} else 1
                values = [magnitude(prefix, a, b, c, mp.mpf(n)) for n in range(start, start + 10)]
                assert all(u > v > 0 for u, v in zip(values[:-1], values[1:], strict=True))
                end = mp.mpf("1e8") if prefix in {"SRBH", "SRBJ"} else mp.mpf(1000)
                assert 0 < magnitude(prefix, a, b, c, end) < mp.mpf("1e-6")
            elif prefix in {"SRBM", "SRBO"}:
                assert answer.expected == "conditional"
                start = b + c if prefix == "SRBM" else 1
                values = [magnitude(prefix, a, b, c, mp.mpf(n)) for n in range(start, start + 10)]
                assert all(u > v > 0 for u, v in zip(values[:-1], values[1:], strict=True))
                n = mp.mpf("1e8")
                coefficient = a if prefix == "SRBM" else a * b
                assert abs(n * magnitude(prefix, a, b, c, n) - coefficient) < mp.mpf("1e-5")
            elif prefix == "SRBN":
                n = mp.mpf(1000000)
                value = magnitude(prefix, a, b, c, n)
                assert abs(mp.exp(mp.log(value) / n) - mp.mpf(a) / b) < mp.mpf("1e-4")
                assert answer.expected == ("absolute" if a < b else "diverges")
                if a == b:
                    assert value > mp.mpf("0.001")
            else:
                assert answer.expected == "absolute"
                base = a + 1 if prefix == "SRBL" else b + 1
                scale = c if prefix == "SRBL" else 1
                for n in (1, 5, 20):
                    assert magnitude(prefix, a, b, c, mp.mpf(n)) <= scale / mp.power(base, n)
            if answer not in checked_answers:
                tree = parse_answer_input(source(answer), answer.kind, contract=answer.contract)
                assert answer.check(tree) == "correct"
                checked_answers.add(answer)
