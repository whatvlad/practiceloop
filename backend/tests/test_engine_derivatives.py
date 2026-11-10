"""#260: derivative and tangent versions against numerical differentiation of the statement."""

import mpmath
import pytest
import sympy as sp
from test_engine_analysis_limits import source

from app.engine.answers.computational import OrderedAnswer, PeriodicSetAnswer, RealSetAnswer
from app.engine.answers.domain_formula import DomainFormulaAnswer
from app.engine.generators.analysis_limits import generators
from app.engine.generators.catalogue import registry
from app.engine.rendering import render
from app.math_input import parse_answer_input

DERIVATIVES = [g for g in generators() if g.topic == "differential-calculus"]
X = sp.Symbol("x", real=True)
mp = mpmath


def interval(lo, hi):
    return sp.Interval.open(lo, hi)


def functions(name, a, b, c):  # noqa: PLR0911, PLR0912
    """Each displayed function rewritten for mpmath, with its expected domain and sample points."""
    reals = (sp.S.Reals, [-1.3, 0.4, 2.2])
    if name == "definition_power":
        return lambda x: a * x ** (b + 1) + c * x, *reals
    if name == "definition_reciprocal":
        return lambda x: a / (x - b), sp.S.Reals - sp.FiniteSet(b), [b - 1.5, b + 0.7]
    if name == "definition_root":
        return lambda x: a * mp.sqrt(x + c), interval(-c, sp.oo), [-c + 0.3, 1.1, 4.0]
    if name == "definition_sine":
        return lambda x: a * mp.sin(b * x), *reals
    if name == "trig_sum":
        return lambda x: a * mp.sin(x) + b * mp.cot(x), None, [0.3, 1.2, 2.9]
    if name == "exponential_quadratic":
        return lambda x: mp.exp(a * x) * (x * x + b * x + c), *reals
    if name == "rational_quotient":
        return lambda x: (x * x + a) / (x - b), sp.S.Reals - sp.FiniteSet(b), [b - 2, b + 0.5]
    if name == "exponential_square":
        return lambda x: mp.exp(-a * x) * (b * x + c) ** 2, *reals
    if name == "log_arctan_root":
        return (
            lambda x: mp.log(x * x + a + 1) * mp.atan(b * mp.sqrt(x)),
            interval(0, sp.oo),
            [0.2, 1.0, 3.7],
        )
    if name == "exponential_arctan":
        return lambda x: mp.exp(a / x) * mp.atan(b - x), sp.S.Reals - {0}, [-2.0, 0.6, 3.1]
    if name == "log_cosine":
        return lambda x: mp.log(a * mp.cos(x) ** 2 + b), *reals
    if name == "root_arccos":
        return (
            lambda x: a * mp.sqrt(mp.acos(x * x / (c * c))),
            interval(-c, c),
            [-0.8 * c, 0.1 * c, 0.6 * c],
        )
    if name == "constant_over_power":
        return lambda x: mp.sqrt(a) / (x * x + b) ** c, *reals
    if name == "exponential_trig_powers":
        return lambda x: (a + 1) ** (mp.sin(x) ** 2) / (b + 1) ** (mp.cos(x) ** 2), *reals
    if name == "power_of_exponential":
        return lambda x: (mp.exp(-a * x) + b) ** (c + 1), *reals
    if name == "variable_power":
        return lambda x: mp.sin(a * x) ** (b * x), None, [0.2 / a, 1.5 / a, 2.9 / a]
    if name == "inverse_trig_constant":
        return (
            lambda x: (a * (mp.asin(x / c) + mp.acos(x / c)) + b) ** 2,
            interval(-c, c),
            [-0.5 * c, 0.3 * c],
        )
    if name == "logarithm_constant":
        return lambda x: mp.log(a * x) + mp.log(b / x) + c * x, interval(0, sp.oo), [0.5, 3.0]
    if name == "log_constant_quotient":
        return lambda x: mp.log(2000 + 5 * a + b) / (x * x + c), *reals
    if name == "constant_coefficients":
        return lambda x: mp.e**a * mp.sin(b * x) + mp.sqrt(mp.pi) * mp.cos(c * x), *reals
    if name == "root_exponential_domain":
        return (
            lambda x: mp.exp(a * mp.sqrt(2 * b * x - x * x)),
            interval(0, 2 * b),
            [0.3 * b, b, 1.7 * b],
        )
    if name == "arcsine_shifted_square":
        low, high = sp.sqrt(b), sp.sqrt(b + 2)
        middle = float((low + high) / 2)
        return (
            lambda x: a * mp.asin(x * x - b - 1),
            sp.Union(interval(-high, -low), interval(low, high)),
            [-middle, middle],
        )
    raise AssertionError(name)


def tangent_point(name, a, b, c):  # noqa: PLR0911
    """The function and an independently derived contact abscissa (or abscissas)."""
    if name == "tangent_arctan":
        return lambda x: a * mp.atan(x / b), [b]
    if name == "tangent_logarithm":
        return lambda x: mp.log(x * x + b), [c - 3]
    if name == "tangent_tangent_square":
        return lambda x: a * mp.tan(b * x) ** 2, [mp.pi / (4 * b)]
    if name == "tangent_root_exponential":
        return lambda x: mp.sqrt((a + 1) ** x + c), [b]
    if name == "tangent_rational":
        return lambda x: a * x / (b + x * x), [mp.sqrt(c)]
    if name == "tangent_exponential_level":
        f = lambda x: mp.exp(a + b / x)  # noqa: E731
        return f, [mp.findroot(lambda x: f(x) - 1, -1.0)]
    if name == "tangent_arctan_quotient":
        return lambda x: a * mp.atan(x) / x, [(mp.sqrt(3), 1, 1 / mp.sqrt(3))[c % 3]]
    if name == "tangent_exponential_cubic":
        x0 = 1 + b % 3
        f = lambda x: mp.exp(x**3 - a)  # noqa: E731
        level = x0**3 - a  # the stated ordinate is e^level
        return f, [mp.findroot(lambda x: mp.log(f(x)) - level, (0.5, 3.5), solver="bisect")]
    if name == "tangent_parallel_quartic":
        slope = 4 * (1 + c % 2) ** 3 - a
        return lambda x: x**4 - a * x + b, [mp.cbrt((slope + a) / mp.mpf(4))]
    if name == "tangent_angle_root":
        slope = 1 if c % 2 else mp.sqrt(3)
        f = lambda x: a * mp.sqrt(x)  # noqa: E731
        return f, [mp.findroot(lambda x: mp.diff(f, x) - slope, (0.01, 30), solver="bisect")]
    if name == "tangent_perpendicular_xlogx":
        f = lambda x: x * mp.log(x)  # noqa: E731
        return f, [mp.findroot(lambda x: mp.diff(f, x) - (a + 1), 3.0)]
    if name == "tangent_line_intersection":
        f = lambda x: a * x * mp.atan(b / x)  # noqa: E731
        return f, [mp.findroot(lambda x: f(x) - a * mp.pi * x / 4, b + 0.3)]
    if name == "tangent_axis_intersection":
        return lambda x: mp.sin(a * x) - mp.cos(b * x) + c, [0]
    if name == "tangent_horizontal":
        f = lambda x: (x - b) * mp.exp(-a * x)  # noqa: E731
        return f, [mp.findroot(lambda x: mp.diff(f, x), (b, b + 2), solver="bisect")]
    if name == "tangent_pair_perpendicular":
        f = lambda x: a * x / (1 + x * x)  # noqa: E731
        slope = mp.mpf((b + 2) ** 2) / (a * b * (b + 1))
        roots = [mp.findroot(lambda x: mp.diff(f, x) - 1 / slope, s) for s in (-0.5, 0.5)]
        return f, sorted(roots)
    raise AssertionError(name)


def close(left, right):
    return abs(complex(left) - complex(right)) < 1e-12 * max(1, abs(complex(right)))


def value_at(formula, x):
    return sp.N(formula.subs(X, x), 40)


def check_derivative(answer, f, samples):
    with mp.workdps(40):
        for x in samples:
            assert close(value_at(answer.expected, sp.Float(x, 40)), mp.diff(f, x)), x


def check_line(line, f, x0):
    with mp.workdps(40):
        slope = mp.diff(f, x0)
        for x in (x0, x0 + 1):
            assert close(value_at(line.expected, sp.Float(x, 40)), f(x0) + slope * (x - x0))


@pytest.mark.parametrize("generator", DERIVATIVES, ids=lambda g: g.prefix)
def test_thousand_seeds_match_numerical_differentiation(generator):
    name = generator.evaluate.__name__
    seen = set()
    for seed in range(1000):
        params = generator.draw(seed)
        triple = (params.a, params.b, params.c)
        if triple in seen:
            continue
        seen.add(triple)
        task = generator.build(params)
        answer = task.answer
        if name.startswith("tangent_"):
            f, points = tangent_point(name, *triple)
            tangents = answer.components if name == "tangent_pair_perpendicular" else [answer]
            for tangent, x0 in zip(tangents, points, strict=True):
                *head, line = tangent.components
                with mp.workdps(40):
                    if len(head) == 2:  # abscissa and ordinate
                        assert close(sp.N(head[0].expected, 40), x0)
                        assert close(sp.N(head[1].expected, 40), f(x0))
                    elif name in {"tangent_exponential_level", "tangent_exponential_cubic"}:
                        assert close(sp.N(head[0].expected, 40), x0)
                    else:
                        assert close(sp.N(head[0].expected, 40), f(x0))
                check_line(line, f, x0)
        else:
            f, domain, samples = functions(name, *triple)
            formula = answer.components[0] if isinstance(answer, OrderedAnswer) else answer
            assert isinstance(formula, DomainFormulaAnswer)
            check_derivative(formula, f, samples)
            if isinstance(answer, OrderedAnswer):
                excluded = answer.components[1]
                if isinstance(excluded, PeriodicSetAnswer):
                    assert (excluded.period, excluded.base) == (sp.pi, sp.FiniteSet(0))
                else:
                    assert isinstance(excluded, RealSetAnswer)
                    assert excluded.expected == domain
            elif domain is not None:
                assert formula.domain == domain
        contract = generator.input_contract(params)
        assert contract == answer.contract
        tree = parse_answer_input(source(answer), contract.kind, contract=contract)
        assert answer.check(tree) == "correct"
        render(task, registry())
