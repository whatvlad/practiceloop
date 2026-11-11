"""#266: check rational primitives against the original polynomial fractions."""

import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input

X = sp.Symbol("x", real=True)
RATIONAL = [g for g in generators() if g.evaluate.__module__.endswith("._rational_antiderivatives")]


def reference(prefix, a, b, c):
    """The expanded numerator and denominator, independent of the decomposition."""
    forms = {
        "INBN": (a, (X - b) ** (c + 4)),
        "INBO": (a, X + b),
        "INBP": (c, (b - (a + 1) * X) ** 3),
        "INBQ": (c, (a + 1) * X + b),
        "INBR": (c, X**2 + 2 * a * X + a**2 + (b + 1) ** 2),
        "INBS": (2 * c * X + 2 * a * c, X**2 + 2 * a * X + a**2 + (b + 1) ** 2),
        "INBT": (2 * c * X - 2 * a * c + b, X**2 - 2 * a * X + a**2 + (b + 1) ** 2),
        "INBU": (a * X + a * b - c, (a + 1) * (X**2 + 2 * b * X + b**2 + (c + 1) ** 2)),
        "INBV": (c * X + b, X**2 - a * X),
        "INBW": (c * X**2, X + b),
        "INBX": (c, X**3 - a * X**2),
        "INBY": (c * X**4, X**2 - a**2),
        "INBZ": (c, X**4 + (a**2 + (a + b) ** 2) * X**2 + a**2 * (a + b) ** 2),
        "INCA": (2 * c * (a + 1) * (X + b), (a + 1) * (X**2 + 2 * b * X + b**2 + (c + 1) ** 2)),
        "INCB": (b + 1, X**2 + 2 * a * X + a**2 + (b + c) ** 2),
        "INCC": (c, X**3 - a**2 * X),
        "INCD": (-a * X + a * b + c, X**2 - 2 * b * X + b**2 + (a + c) ** 2),
        "INCE": (c * X**2, X**2 - 2 * a * X + a**2 + (a + b) ** 2),
        "INCF": (c, X**3 + a**2 * X),
        "INCG": (c * X, X**4 - a**4),
        "INCH": ((b + 1) * X**2 + c * X + a**2, X**3 + a**2 * X),
        "INCI": (c * X, b**2 - a**2 * X**2),
    }
    return forms[prefix]


@pytest.mark.parametrize("generator", RATIONAL, ids=lambda g: g.prefix)
def test_primitives_differentiate_to_the_original_fraction(generator):
    seen = set()
    verified = set()
    for seed in sweep(1000):
        params = generator.draw(seed)
        coefficients = (params.a, params.b, params.c)
        if coefficients in seen:
            continue
        seen.add(coefficients)
        answer = generator.build(params).answer
        assert isinstance(answer, AntiderivativeAnswer)
        numerator, denominator = reference(generator.prefix, *coefficients)
        key = (answer, numerator, denominator)
        if key in verified:
            continue
        assert sp.cancel(sp.diff(answer.primitive, X) * denominator - numerator) == 0
        assert sp.cancel(answer.integrand * denominator - numerator) == 0
        poles = set(sp.Poly(denominator, X).real_roots())
        assert all(pole not in answer.domain for pole in poles)
        endpoints = {answer.domain.start, answer.domain.end} - {-sp.oo, sp.oo}
        assert endpoints <= poles
        tree = parse_answer_input(source(answer), answer.kind)
        assert answer.check(tree) == "correct"
        verified.add(key)
