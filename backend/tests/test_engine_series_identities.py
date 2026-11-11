"""#276: independent coefficients and direct numerical sums, including the source erratum."""

from functools import cache

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

X = sp.Symbol("x", real=True)
IDENTITIES = [g for g in generators() if g.evaluate.__module__.endswith("._series_identities")]
FUNCTIONS = {"SRCJ", "SRCK", "SRCL"}


def original_term(prefix, a, b, c, n, x):
    base = b + c + 1
    offset = 1 + (b - 1) % a
    cases = {
        "SRCJ": lambda: a * n * mp.power(b * x, n),
        "SRCK": lambda: a * n * (n + 1) * mp.power(b * x, n),
        "SRCL": lambda: a * mp.power(b * x, n) / mp.factorial(n),
        "SRCM": lambda: mp.mpf(a) / ((n + 1) * mp.power(b + 1, n)),
        "SRCN": lambda: (a * n - offset) / mp.power(c + 1, n),
        "SRCO": lambda: a * n * (n + 1) / mp.power(base, n),
        "SRCP": lambda: a * n / ((n + 1) * mp.power(base, n)),
    }
    return cases[prefix]()


@cache
def coefficients(function):
    polynomial = sp.series(function, X, 0, 13).removeO().expand()
    return tuple(polynomial.coeff(X, degree) for degree in range(13))


@pytest.mark.parametrize("generator", IDENTITIES, ids=lambda g: g.prefix)
def test_full_sweep_checks_original_coefficients_and_numerical_series(generator):
    seen = set()
    checked_answers = set()
    with mp.workdps(40):
        for seed in sweep(1000):
            params = generator.draw(seed)
            values = params.a, params.b, params.c
            if values in seen:
                continue
            seen.add(values)
            a, b, c = values
            answer = generator.build(params).answer
            prefix = generator.prefix
            if prefix in FUNCTIONS:
                actual = coefficients(answer.expected)
                assert actual[0] == 0
                for degree in range(1, 13):
                    numerator = (
                        a * degree * b**degree
                        if prefix == "SRCJ"
                        else a * degree * (degree + 1) * b**degree
                    )
                    expected = (
                        sp.Integer(numerator)
                        if prefix != "SRCL"
                        else sp.Rational(a * b**degree, sp.factorial(degree))
                    )
                    assert actual[degree] == expected
                for sign in (-1, 1):
                    x = mp.mpf(sign) / (2 * b)
                    total = mp.fsum(original_term(prefix, a, b, c, n, x) for n in range(1, 201))
                    value = mp.mpf(str(sp.N(answer.expected.subs(X, sp.Rational(sign, 2 * b)), 40)))
                    assert abs(total - value) < mp.mpf("1e-28")
                visual = validate_plot(generator.solution_visual(params))
                assert "pdfliteral" in graph(visual)
                if prefix == "SRCL":
                    false_value = -a * mp.log(mp.mpf("0.5"))
                    true_value = a * mp.expm1(mp.mpf("0.5"))
                    assert abs(true_value - false_value) > mp.mpf("0.01")
                    false_input = f"-{a}*log(1-{b}*x)"
                    assert (
                        answer.check(
                            parse_answer_input(false_input, answer.kind, contract=answer.contract)
                        )
                        != "correct"
                    )
            else:
                start = 0 if prefix == "SRCM" else 2 if prefix == "SRCN" else 1
                total = mp.fsum(original_term(prefix, a, b, c, n, 0) for n in range(start, 201))
                expected = mp.mpf(str(sp.N(answer.expected, 40)))
                assert abs(total - expected) < mp.mpf("1e-28")
            if answer not in checked_answers:
                tree = parse_answer_input(source(answer), answer.kind, contract=answer.contract)
                assert answer.check(tree) == "correct"
                checked_answers.add(answer)
