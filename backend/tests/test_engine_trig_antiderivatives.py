"""#267: differentiate the returned primitives against the original trigonometric forms."""

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input

X = sp.Symbol("x", real=True)
TRIG = [g for g in generators() if g.evaluate.__module__.endswith("._trig_antiderivatives")]


def reference(prefix, a, c, u):
    sine = mp.sin(u)
    cosine = mp.cos(u)
    tangent = mp.tan(u)
    forms = {
        "INCJ": lambda: sine**3,
        "INCK": lambda: sine**4 * cosine**3,
        "INCL": lambda: mp.cos(u + c) ** 4,
        "INCM": lambda: sine**3 * cosine**6,
        "INCN": lambda: cosine**2 * mp.cos(2 * u),
        "INCO": lambda: mp.sin(2 * u) ** 2 * sine**2,
        "INCP": lambda: 1 / sine,
        "INCQ": lambda: (1 + tangent) / cosine,
        "INCR": lambda: sine**2 / (1 + cosine),
        "INCS": lambda: 1 / (1 + (c**2 + 2 * c) * cosine**2),
        "INCT": lambda: 1 / (1 - tangent),
        "INCU": lambda: sine**5 / cosine**3,
        "INCV": lambda: 1 / (sine + tangent),
        "INCW": lambda: 1 / (sine + cosine),
        "INCX": lambda: 1 / (2 * (c + 1) * sine + (c**2 + 2 * c) * cosine + c**2 + 2 * c + 2),
        "INCY": lambda: sine**4,
    }
    return a * forms[prefix]()


@pytest.mark.parametrize("generator", TRIG, ids=lambda g: g.prefix)
def test_primitives_match_the_original_trigonometric_integrands(generator):
    seen = set()
    checked_answers = set()
    with mp.workdps(40):
        for seed in sweep(1000):
            params = generator.draw(seed)
            coefficients = (params.a, params.b, params.c)
            if coefficients in seen:
                continue
            seen.add(coefficients)
            answer = generator.build(params).answer
            assert isinstance(answer, AntiderivativeAnswer)
            primitive = sp.lambdify(X, answer.primitive, "mpmath")
            integrand = sp.lambdify(X, answer.integrand, "mpmath")
            angles = ("0.2", "0.4", "0.6") if generator.prefix == "INCT" else ("0.2", "0.7", "1.2")
            if answer.domain == sp.S.Reals or answer.domain.start < 0:
                angles = ("-1.1", *angles)
            for angle in angles:
                u = mp.mpf(angle)
                x = u / params.b
                expected = reference(generator.prefix, params.a, params.c, u)
                assert abs(mp.diff(primitive, x) - expected) < mp.mpf("1e-32")
                assert abs(integrand(x) - expected) < mp.mpf("1e-32")
            if answer not in checked_answers:
                assert answer.check(parse_answer_input(source(answer), answer.kind)) == "correct"
                checked_answers.add(answer)
