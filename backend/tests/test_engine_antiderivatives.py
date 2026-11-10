"""#265: primitives differentiate back to the stated integrand (numerically, at 40 digits)."""

import mpmath as mp
import pytest
import sympy as sp
from test_engine_analysis_limits import source as computational_source

from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.engine.generators.analysis_limits import generators
from app.engine.generators.catalogue import registry
from app.engine.rendering import render
from app.math_input import parse_answer_input

PRIMITIVES = [g for g in generators() if g.evaluate.__module__.endswith("_antiderivatives")]
X = sp.Symbol("x", real=True)


def integrand(name, a, b, c):  # noqa: PLR0911, PLR0912
    """The stated integrand, rewritten for mpmath, and sample points inside its domain."""
    positive = [mp.mpf("0.3"), mp.mpf("1.7"), mp.mpf("4.2")]
    reals = [mp.mpf("-1.3"), mp.mpf("0.4"), mp.mpf("2.1")]
    p, q = (a, b) if a != b else (a, b + 1)
    table = {
        "sum_of_powers": (lambda x: a * x ** (b + 1) + c / x - (b + 2) * mp.sqrt(x), positive),
        "conjugate_quotient": (lambda x: (c * c - x) / (c + mp.sqrt(x)), positive),
        "polynomial_division": (lambda x: x**4 / (x * x + c * c), reals),
        "double_angle_quotient": (
            lambda x: a * mp.cos(2 * b * x) / (mp.cos(b * x) - mp.sin(b * x)),
            [mp.mpf(-0.5) / b, mp.mpf(0.1) / b, mp.mpf(0.6) / b],
        ),
        "root_powers": (lambda x: (x**a + b * mp.cbrt(x * x) - c) / mp.sqrt(x), positive),
        "exponential_product": (lambda x: mp.exp(-a * x) * (b + 1) ** (c * x), reals),
        "linear_exponential": (lambda x: (x + b) * mp.exp(-a * x), reals),
        "square_exponential": (lambda x: (x + b) ** 2 * mp.exp(a * x), reals),
        "root_arctan": (lambda x: a * mp.sqrt(x) * mp.atan(mp.sqrt(x)), positive),
        "secant_square": (
            lambda x: a * x / mp.cos(b * x) ** 2,
            [mp.mpf("0.1") / b, mp.mpf("0.7") / b, mp.mpf("1.4") / b],
        ),
        "square_sine": (lambda x: a * x * x * mp.sin(b * x), reals),
        "arccos_over_root": (
            lambda x: a * mp.acos(x) / mp.sqrt(x + 1),
            [mp.mpf("-0.8"), mp.mpf("0.1"), mp.mpf("0.9")],
        ),
        "logarithm": (lambda x: a * mp.log(x + b), [-b + mp.mpf("0.5"), mp.mpf(1), mp.mpf(7)]),
        "arccos_scaled": (lambda x: a * mp.acos(x / b), [-0.7 * b, 0.2 * b, 0.9 * b]),
        "exponential_sine": (lambda x: mp.exp(a * x) * mp.sin(b * x), reals),
        "sine_sine": (lambda x: mp.sin(p * x) * mp.sin(q * x), reals),
        "sine_cosine": (lambda x: mp.sin(p * x) * mp.cos(q * x), reals),
        "cosine_cosine": (lambda x: mp.cos(p * x) * mp.cos(q * x), reals),
        "sine_square": (lambda x: b * mp.sin(a * x) ** 2, reals),
        "cosine_fourth": (lambda x: b * mp.cos(a * x) ** 4, reals),
        "logarithm_quadratic": (lambda x: a * mp.log(b * b + x * x), reals),
        "linear_sine_exponential": (lambda x: x * mp.sin(b * x) * mp.exp(a * x), reals),
        "arccot_linear": (lambda x: a * x * mp.acot(b * x), positive),
        "cosine_root": (lambda x: a * mp.cos(b * mp.sqrt(x)) / mp.sqrt(x), positive),
        "root_over_x": (lambda x: mp.sqrt(1 + b * x) / x, positive),
        "cosine_over_root_sine": (lambda x: a * mp.cos(x) / mp.sqrt(b + 1 + mp.sin(x)), reals),
        "sine_of_quadratic": (lambda x: c * x * mp.sin(a * x * x + b), reals),
        "reciprocal_cosh": (lambda x: 1 / mp.cosh(a * x), reals),
        "linear_power": (lambda x: (b - a * x) ** (c + 5), reals),
        "fifth_root": (lambda x: x * x * mp.root(a * x**3 + b, 5), positive),
        "reciprocal_root_sum": (lambda x: 1 / (b + mp.sqrt(x)), positive),
        "logarithm_power": (lambda x: a * mp.log(x) ** b / x, positive),
        "exponential_arctan": (lambda x: mp.exp(a * x) / (mp.exp(2 * a * x) + b * b), reals),
        "sine_over_cosine": (lambda x: c * mp.sin(x) / (a + b - a * mp.cos(x)), reals),
        "cubic_exponential": (lambda x: x**3 * mp.exp(a * x * x), reals),
        "root_over_linear": (lambda x: mp.sqrt(x) / (x + b * b), positive),
        "logarithm_arctan": (lambda x: mp.log(a * mp.atan(x)) / (1 + x * x), positive),
        "sine_cosine_arctan": (
            lambda x: mp.sin(x) * mp.cos(x) * mp.atan(b * mp.sin(x)),
            reals,
        ),
        "root_quotient_value": (lambda x: (x * x + mp.sqrt(x)) / (mp.sqrt(x) + 1), positive),
    }
    return table[name]


def source(answer):
    if isinstance(answer, AntiderivativeAnswer):
        return sp.sstr(answer.primitive).replace("**", "^").replace("E", "e") + " + C"
    return computational_source(answer)


@pytest.mark.parametrize("generator", PRIMITIVES, ids=lambda g: g.prefix)
def test_thousand_seeds_differentiate_back(generator):
    name = generator.evaluate.__name__
    seen = set()
    with mp.workdps(40):
        for seed in range(1000):
            params = generator.draw(seed)
            triple = (params.a, params.b, params.c)
            if triple in seen:
                continue
            seen.add(triple)
            task = generator.build(params)
            answer = task.answer
            f, points = integrand(name, *triple)
            primitive = answer.primitive if isinstance(answer, AntiderivativeAnswer) else None
            if primitive is None:  # a fixed primitive with a stated value
                primitive = answer.expected
                point, value = (
                    (1, sp.Rational(params.c, 3)) if name == "root_quotient_value" else (0, 0)
                )
                assert abs(sp.N(primitive.subs(X, point), 30) - value) < 1e-25
            F = sp.lambdify(X, primitive, "mpmath")  # noqa: N806
            for x in points:
                assert abs(mp.diff(F, x) - f(x)) < 1e-15 * max(1, abs(f(x))), (name, triple, x)
            kind = answer.kind
            tree = parse_answer_input(
                source(answer), kind, contract=getattr(answer, "contract", None)
            )
            assert answer.check(tree) == "correct"
            render(task, registry())
