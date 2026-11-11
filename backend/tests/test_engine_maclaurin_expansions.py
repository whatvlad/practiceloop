"""#275: independent symbolic Taylor coefficients and direct high derivatives."""

from functools import cache

import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source

from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot

X = sp.Symbol("x", real=True)
MACLAURIN = [g for g in generators() if g.evaluate.__module__.endswith("._maclaurin_expansions")]
DERIVATIVES = {"SRCB", "SRCC", "SRCD", "SRCE"}


def original_function(prefix, a, b, c):
    cases = {
        "SRBV": a / (1 - b * X),
        "SRBW": a * sp.sin(b * X),
        "SRBX": a * X ** (c + 1) * sp.exp(-b * X),
        "SRBY": a * X**3 / (b * b + X * X),
        "SRBZ": a * (sp.exp(b * X) + sp.exp(-b * X)) / 2,
        "SRCA": a * sp.sin(b * X) ** 2,
        "SRCB": a * X**2 * sp.cos(X),
        "SRCC": a * X * sp.exp(-X),
        "SRCD": (1 + a % 2) * X**3 / (1 + X * X),
        "SRCE": a * X * sp.sin(X / 2) ** 2,
        "SRCF": a / (1 + b * X) ** 2,
        "SRCG": a * X * sp.exp(-b * X),
        "SRCH": a * sp.log(1 + b * X * X),
        "SRCI": a * sp.atan(b * X),
    }
    return cases[prefix]


@cache
def original_coefficients(function):
    polynomial = sp.series(function, X, 0, 14).removeO().expand()
    return tuple(polynomial.coeff(X, degree) for degree in range(14))


@cache
def direct_derivative(function, order):
    return sp.simplify(sp.diff(function, X, order).subs(X, 0))


def coefficient(prefix, amplitude, scale, c, degree):
    if prefix == "SRBV":
        return amplitude * scale**degree
    if prefix in {"SRBW", "SRCI"}:
        if degree % 2 == 0:
            return sp.S.Zero
        index = (degree - 1) // 2
        denominator = sp.factorial(degree) if prefix == "SRBW" else degree
        return (-1) ** index * amplitude * scale**degree / denominator
    if prefix in {"SRBX", "SRCG"}:
        shift = c + 1 if prefix == "SRBX" else 1
        index = degree - shift
        return sp.S.Zero if index < 0 else amplitude * (-scale) ** index / sp.factorial(index)
    if prefix == "SRBY":
        if degree < 3 or degree % 2 == 0:
            return sp.S.Zero
        return amplitude * (-scale) ** ((degree - 3) // 2)
    if prefix == "SRBZ":
        return sp.S.Zero if degree % 2 else amplitude * scale**degree / sp.factorial(degree)
    if prefix in {"SRCA", "SRCH"}:
        if degree < 2 or degree % 2:
            return sp.S.Zero
        index = degree // 2
        if prefix == "SRCA":
            return (-1) ** (index + 1) * amplitude * scale**degree / sp.factorial(degree)
        return (-1) ** (index + 1) * amplitude * scale**index / index
    if prefix == "SRCF":
        return amplitude * (degree + 1) * (-scale) ** degree
    raise AssertionError(prefix)


def convergence_domain(prefix, b):
    if prefix in {"SRBV", "SRCF"}:
        return sp.Interval.open(-sp.Rational(1, b), sp.Rational(1, b))
    if prefix == "SRBY":
        return sp.Interval.open(-b, b)
    if prefix == "SRCH":
        return sp.Interval(-1 / sp.sqrt(b), 1 / sp.sqrt(b))
    if prefix == "SRCI":
        return sp.Interval(-sp.Rational(1, b), sp.Rational(1, b))
    return sp.S.Reals


@pytest.mark.parametrize("generator", MACLAURIN, ids=lambda g: g.prefix)
def test_full_sweep_reconstructs_complete_coefficients_and_high_derivatives(generator):
    seen = set()
    checked_answers = set()
    for seed in sweep(1000):
        params = generator.draw(seed)
        coefficients = params.a, params.b, params.c
        if coefficients in seen:
            continue
        seen.add(coefficients)
        a, b, c = coefficients
        answer = generator.build(params).answer
        prefix = generator.prefix
        function = original_function(prefix, a, b, c)
        if prefix in DERIVATIVES:
            orders = {
                "SRCB": 42 + 2 * ((b + c) % 9),
                "SRCC": 15 + b + c,
                "SRCD": 3 + 2 * (1 + (b + c) % 4),
                "SRCE": 6 + c,
            }
            assert answer.expected == direct_derivative(function, orders[prefix])
        else:
            amplitude, scale, domain = (part.expected for part in answer.components)
            actual = original_coefficients(function)
            for degree, value in enumerate(actual):
                assert sp.simplify(coefficient(prefix, amplitude, scale, c, degree) - value) == 0
            assert domain == convergence_domain(prefix, b)
            visual = validate_plot(generator.solution_visual(params))
            assert "pdfliteral" in graph(visual)
            if domain != sp.S.Reals:
                assert visual["points"][0]["included"] == (not domain.left_open)
                assert visual["points"][1]["included"] == (not domain.right_open)
        if answer not in checked_answers:
            tree = parse_answer_input(source(answer), answer.kind, contract=answer.contract)
            assert answer.check(tree) == "correct"
            checked_answers.add(answer)
