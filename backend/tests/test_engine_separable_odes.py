"""#287: verify decay observations, branch residuals, initial values and maximal intervals."""

import mpmath as mp
import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

FAMILIES = [g for g in generators() if g.evaluate.__module__.endswith("._separable_odes")]


def exact(expression):
    return mp.mpf(str(sp.N(expression, 42)))


def close(actual, expected):
    assert abs(actual - expected) <= mp.mpf("1e-34") * max(1, abs(expected))


def as_function(component):
    return sp.lambdify(sp.Symbol(component.variable, real=True), component.expected, "mpmath")


def check_decay(prefix, parts, a, b, c):
    values = tuple(exact(part.expected) for part in parts)
    if prefix == "ODAA":
        initial, rate = values
        assert rate > 0
        close(initial * mp.exp(-rate * a), c * (b + 1))
        close(initial * mp.exp(-2 * rate * a), c)
    elif prefix == "ODAB":
        remaining, rate = values
        close(mp.exp(-rate * 20 * a * (c + 1)), mp.mpf("0.5"))
        close(remaining, (50 + 10 * c) * mp.exp(-rate * 20 * a * b))
    else:
        half = 2 * (b + 2) * a
        for t, percent in zip((2 * a, half // 2, (c + 1) * half), values, strict=True):
            close(mp.log(percent / 100), -mp.log(2) * t / half)


def check_general(prefix, parts, a, b, c):
    f = as_function(parts[0])
    constants, equilibria = (part.expected for part in parts[1:3])
    one = mp.mpf(1)
    if prefix == "ODAD":
        assert constants == sp.Interval.open(0, sp.oo)
        assert equilibria == sp.S.EmptySet
        k = a + b
        for sign in (-1, 1):

            def y(t, sign=sign):
                return sign * mp.sqrt(k + f(t))

            t = mp.mpf("0.25")
            close(y(t) * mp.diff(y, t), -k * t)
        close(f(-one), -k)
        close(f(one), -k)
    elif prefix == "ODAE":
        assert constants == sp.S.Reals
        assert equilibria == sp.FiniteSet(0)
        assert parts[3].expected == sp.FiniteSet(0)
        k = a + b + c
        for t in (-one, one):

            def y(s):
                return f(s) - k / 2

            close(y(t), 0)
            close(mp.diff(y, t), k * t)
        eps = mp.mpf("1e-40")
        assert abs(f(eps) / eps) < mp.mpf("1e-38")
    elif prefix == "ODAF":
        assert constants == sp.S.Reals - sp.FiniteSet(0)
        assert equilibria == sp.FiniteSet(-b, b)
        for t in (-a - one, a + one):
            for sign in (-1, 1):

                def y(s, sign=sign):
                    return sign * mp.sqrt(b * b + f(s))

                close(t * (y(t) ** 2 - b * b) + y(t) * (t * t - a * a) * mp.diff(y, t), 0)
    elif prefix == "ODAG":
        assert constants == sp.Interval.open(-sp.oo, sp.pi / 2)
        assert equilibria == sp.FiniteSet(-1, 1)
        k = mp.mpf(a) / (b + c)

        def y(t):
            return mp.sin(max(-mp.pi / 2, min(mp.pi / 2, f(t) - 2)))

        for angle in (-2, 0, 2):
            t = ((angle + 2) / k) ** 2 if angle > -2 else (mp.mpf("0.1") / k) ** 2
            close(2 * mp.sqrt(t) * mp.diff(y, t), k * mp.sqrt(max(0, 1 - y(t) ** 2)))
    elif prefix == "ODAH":
        assert constants == sp.S.Reals - sp.FiniteSet(0)
        assert equilibria == sp.FiniteSet(0)
        assert parts[0].domain == constants
        for t in (-one, one):
            close(t * mp.diff(f, t) + (a + b) * f(t), 0)
    else:
        assert constants == sp.S.Reals - sp.FiniteSet(0)
        assert equilibria == sp.FiniteSet(0)
        close(f(0), 1)
        t = mp.mpf("0.15")
        close(mp.diff(f, t), (a * mp.exp(b * t) + c) * f(t))


def check_waiting(parts, a, b, c):
    f, g = map(as_function, parts[:2])
    k = mp.mpf(a) / (a + b + c)
    assert parts[2].expected == sp.Interval(0, sp.Rational(a, a + b + c))
    assert parts[3].expected == sp.Interval.open(-1, 1)

    def y(t):
        return g(max(0, (k if t < 0 else k / 2) - f(t)))

    close(y(0), 1)
    for t in map(mp.mpf, ("-0.9", "-0.4", "0.4", "0.95")):
        close(k * t * mp.sqrt(1 - y(t) ** 2) + y(t) * mp.sqrt(1 - t * t) * mp.diff(y, t), 0)
    close(y(mp.mpf("0.5")), 1)
    assert y(mp.mpf("0.95")) < 1


def check_implicit(prefix, parts, a, b, c):
    g, f = map(as_function, parts[:2])
    k = exact(parts[2].expected)
    domain = parts[3].expected
    y = mp.mpf(b)
    if prefix == "ODAL":
        t = mp.exp(c)
        assert domain == sp.Interval.open(0, sp.oo)
        close(mp.diff(g, y), 1 + 1 / y)
        close(mp.diff(f, t), a / t)
    else:
        t = mp.mpf(0)
        assert domain == sp.S.Reals
        close(mp.diff(g, y), 1 / y + y)
        close(mp.diff(f, t), mp.mpf(a) / c)
    close(g(y), f(t) + k)


def check_explicit(prefix, parts, a, b, c):
    solution = as_function(parts[0])
    domain = parts[1].expected
    assert domain == parts[0].domain
    if prefix == "ODAJ":
        assert domain == sp.Interval.open(0, sp.pi)
        close(solution(mp.pi / 2), mp.exp(c))
        for t in (mp.pi / 5, mp.pi / 2):
            y = solution(t)
            close(mp.diff(solution, t) * mp.sin(t), (a + b) * y * mp.log(y))
    elif prefix == "ODAN":
        assert domain == sp.Interval.open(-a, sp.oo)
        close(solution(mp.mpf(0)), -1 / (c * (a + mp.mpf(b * a**3) / 3)))
        for t in (-a + mp.mpf("0.2"), mp.mpf(1)):
            close(mp.diff(solution, t), c * (1 + b * t * t) * solution(t) ** 2)
        assert abs(solution(-a + mp.mpf("1e-12"))) > mp.mpf("1e8")
    else:
        left = sp.log(sp.Rational(a, a + b * c)) / c
        assert domain == sp.Interval.open(left, sp.oo)
        close(solution(0), mp.log(b))
        for t in (0, mp.mpf("0.3")):
            close(mp.exp(solution(t)) * (mp.diff(solution, t) - c), a)
        assert solution(exact(left) + mp.mpf("1e-12")) < -20


@pytest.mark.parametrize("generator", FAMILIES, ids=lambda item: item.prefix)
def test_decay_or_separable_family_independently(generator):
    seen = set()
    prefix = generator.prefix
    with mp.workdps(48):
        for seed in sweep(1000):
            params = generator.draw(seed)
            coefficients = params.a, params.b, params.c
            if coefficients in seen:
                continue
            seen.add(coefficients)
            answer = generator.build(params).answer
            tree = parse_answer_input(
                source(answer), generator.contract.kind, contract=generator.contract
            )
            assert answer.check(tree) == "correct"
            assert graph(validate_plot(generator.solution_visual(params)))
            if prefix <= "ODAC":
                check_decay(prefix, answer.components, *coefficients)
            elif prefix <= "ODAI":
                check_general(prefix, answer.components, *coefficients)
            elif prefix == "ODAK":
                check_waiting(answer.components, *coefficients)
            elif prefix in ("ODAL", "ODAM"):
                check_implicit(prefix, answer.components, *coefficients)
            else:
                check_explicit(prefix, answer.components, *coefficients)
