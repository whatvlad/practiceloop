"""#273: ratios and nth roots of the original positive series terms."""

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input

SERIES = [g for g in generators() if g.evaluate.__module__.endswith("._series_ratio_root")]


def original_term(prefix, a, b, c, n):
    multiple = 2 + c % 2
    small = a
    first = a + b
    second = a + c
    large = a + b + c
    cases = {
        "SRAU": lambda: mp.power(a + b + 1, n) / mp.factorial(multiple * n),
        "SRAV": lambda: (mp.power(a + 1, n) + b) / (n ** (c + 2) + 1),
        "SRAW": lambda: b * mp.power(a, n) * mp.factorial(n) / mp.power(n, n),
        "SRAX": lambda: c * mp.power(n, n) / (mp.power(a + 1, n) * mp.factorial(n)),
        "SRAY": lambda: c * mp.power(a, n) * mp.factorial(n) ** 2 / mp.factorial(2 * n),
        "SRAZ": lambda: mp.power(a * n + b, 2 * n) / mp.power(c * n * n + 1, n),
        "SRBA": lambda: (
            (mp.power(a + 1, n) + mp.power(a + b + 1, n))
            / (mp.power(a + b + 1, n) + mp.power(a + b + c + 1, n))
        ),
        "SRBB": lambda: mp.power(a, n) * mp.power(n / (n + b), n * n),
        "SRBC": lambda: c * mp.power(mp.atan(a * n / (n + b)), n),
        "SRBD": lambda: c * n ** ((a + 1) * (c + 1)) / mp.power(b + 1, n),
        "SRBE": lambda: b * mp.power(a, n) * mp.power(n, n) / mp.factorial(n) ** 2,
        "SRBF": lambda: c * mp.power(a, n) * mp.power(n, n) / mp.factorial(n),
        "SRBG": lambda: (
            mp.factorial(first * n)
            * mp.factorial(second * n)
            / (mp.factorial(large * n) * mp.factorial(small * n))
        ),
    }
    return cases[prefix]()


@pytest.mark.parametrize("generator", SERIES, ids=lambda g: g.prefix)
def test_full_sweep_checks_original_ratios_roots_and_sequence_limits(generator):
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
            if prefix in {"SRBD", "SRBE", "SRBG"}:
                assert answer.expected == 0
                assert original_term(prefix, a, b, c, mp.mpf(1000)) < mp.mpf("1e-20")
                ratio = original_term(prefix, a, b, c, mp.mpf(1001)) / original_term(
                    prefix, a, b, c, mp.mpf(1000)
                )
                assert 0 < ratio < 1
            elif prefix == "SRBF":
                assert answer.expected == sp.oo
                assert original_term(prefix, a, b, c, mp.mpf(1000)) > mp.mpf("1e20")
            else:
                n = mp.mpf(1000000)
                term = original_term(prefix, a, b, c, n)
                if prefix in {"SRAU", "SRAV", "SRAW", "SRAX", "SRAY"}:
                    observed = original_term(prefix, a, b, c, n + 1) / term
                else:
                    observed = mp.exp(mp.log(term) / n)
                exact = answer.components[0].expected
                limit = mp.mpf(str(sp.N(exact, 40)))
                assert abs(observed - limit) < mp.mpf("1e-4")
                if exact == 1:
                    assert prefix in {"SRAY", "SRAZ"}
                    assert original_term(prefix, a, b, c, mp.mpf(20)) >= 1
                    expected = "diverges"
                else:
                    expected = "converges" if limit < 1 else "diverges"
                assert answer.components[1].expected == expected
            if answer not in checked_answers:
                tree = parse_answer_input(source(answer), answer.kind, contract=answer.contract)
                assert answer.check(tree) == "correct"
                checked_answers.add(answer)
