"""#264: Taylor formulas, error bounds and certified approximations against mpmath."""

import mpmath as mp
import pytest
import sympy as sp
from test_engine_analysis_limits import source

from app.engine.generators.analysis_limits import generators
from app.engine.generators.catalogue import registry
from app.engine.rendering import render
from app.math_input import parse_answer_input

TAYLOR = [g for g in generators() if g.evaluate.__module__.endswith("_taylor")]
X = sp.Symbol("x", real=True)


def formula(expr):
    return sp.lambdify(X, expr, "mpmath")


def formula_case(name, a, b, c):  # noqa: PLR0911
    """f, x0 and the order n, read from the statement's parameters."""
    if name == "taylor_cubic":
        return lambda x: a * x**3 + b * x, -c, 4
    if name == "taylor_reciprocal_power":
        return lambda x: x ** (-(1 + a % 3)), b, 2
    if name == "taylor_sine_at_pi":
        return lambda x: mp.sin(b * x), mp.pi, 3
    if name == "taylor_exponential":
        return lambda x: mp.exp(-a * x), 0, 3 + c % 3
    if name == "maclaurin_sine":
        return lambda x: mp.sin(x / (b + 1)), 0, 3 + c % 3
    if name == "maclaurin_cosh":
        return lambda x: mp.cosh(a * x), 0, 3 + c % 3
    if name == "maclaurin_cosine":
        return lambda x: mp.cos(a * x), 0, 3 + c % 3
    if name == "maclaurin_exponential_product":
        return lambda x: x * mp.exp(-a * x), 0, 3 + c % 3
    raise AssertionError(name)


def bound_case(name, a, b, c):
    """f, radius and the remainder order of the stated approximation."""
    if name == "error_tangent":
        return mp.tan, mp.pi / (6 * (b + 1)), 3
    if name == "error_cosine_square":
        return lambda x: mp.cos(x) ** 2, mp.mpf(b) / 10, 4
    if name == "error_square_root":
        return lambda x: mp.sqrt(1 + x), mp.mpf(b) / 20, 3
    if name == "error_logarithm":
        return lambda x: mp.log(1 - x), mp.mpf(b) / 20, 4
    if name == "error_inverse_root":
        return lambda x: 1 / mp.sqrt(x + 1), mp.mpf(b) / 20, 3
    raise AssertionError(name)


def approximation_case(name, a, b, c):
    if name == "approximate_reciprocal_e":
        return mp.exp, mp.mpf(-1) / a, mp.mpf(10) ** -(3 + b % 3)
    if name == "approximate_cube_root":
        return lambda x: mp.cbrt(1 + x), mp.mpf(-a) / 1000, mp.mpf(10) ** -(3 + b % 3)
    if name == "approximate_logarithm":
        return lambda x: mp.log(1 + x), mp.mpf(a) / 20, mp.mpf(10) ** -(3 + b % 3)
    if name == "approximate_sine":
        return mp.sin, mp.mpf(a) / 10, mp.mpf(10) ** -(4 + b % 3)
    raise AssertionError(name)


def largest_derivative(f, n, low, high, samples=60):
    return max(abs(mp.diff(f, low + (high - low) * k / samples, n)) for k in range(samples + 1))


def close(left, right, tolerance=1e-12):
    return abs(left - right) <= tolerance * max(1, abs(right))


def check_formula(answer, f, x0, n):
    polynomial, nth = (formula(c.expected) for c in answer.components)
    coefficients = mp.taylor(f, x0, n - 1)
    for x in (x0 + mp.mpf("0.3"), x0 - mp.mpf("0.7"), x0 + mp.mpf("1.1")):
        expected = sum(coefficient * (x - x0) ** k for k, coefficient in enumerate(coefficients))
        assert close(polynomial(x), expected, 1e-15), x
        assert close(nth(x), mp.diff(f, x, n), 1e-10), x


def check_bound(answer, f, radius, n):
    expected = largest_derivative(f, n, -radius, radius) * radius**n / mp.factorial(n)
    assert close(mp.mpf(sp.N(answer.expected, 30)), expected, 1e-8)


def check_approximation(answer, f, point, accuracy):
    order, value = (sp.N(c.expected, 30) for c in answer.components)
    low, high = min(0, point), max(0, point)
    for n in range(1, 30):
        if largest_derivative(f, n, low, high) * abs(point) ** n / mp.factorial(n) <= accuracy:
            break
    assert int(order) == n
    coefficients = mp.taylor(f, 0, n - 1)
    estimate = sum(coefficient * point**k for k, coefficient in enumerate(coefficients))
    assert close(mp.mpf(value), estimate, 1e-20)
    assert abs(estimate - f(point)) <= accuracy


@pytest.mark.parametrize("generator", TAYLOR, ids=lambda g: g.prefix)
def test_thousand_seeds_match_mpmath(generator):
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
            if name.startswith(("taylor_", "maclaurin_")):
                check_formula(answer, *formula_case(name, *triple))
            elif name.startswith("error_"):
                check_bound(answer, *bound_case(name, *triple))
            else:
                check_approximation(answer, *approximation_case(name, *triple))
            contract = generator.input_contract(params)
            assert contract == answer.contract
            tree = parse_answer_input(source(answer), contract.kind, contract=contract)
            assert answer.check(tree) == "correct"
            render(task, registry())
