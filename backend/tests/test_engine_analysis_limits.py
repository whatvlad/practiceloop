"""Check independent oracles, code replay and public contracts for #236."""

import math
import re
import sys
from decimal import Decimal, localcontext
from functools import cache

import pytest
import sympy as sp
from test_engine_elementary import source as computational_source

from app.engine.answers.computational import (
    CategoryAnswer,
    LimitAnswer,
    OrderedAnswer,
    RealSetAnswer,
)
from app.engine.generators.analysis_limits import generators
from app.engine.generators.catalogue import registry
from app.engine.opening import rebuild
from app.engine.rendering import render
from app.math_input import parse_answer_input
from app.services import math_worker


def source(answer):
    if isinstance(answer, LimitAnswer):
        if answer.expected == sp.oo:
            return "inf"
        if answer.expected == -sp.oo:
            return "-inf"
        text = sp.sstr(answer.expected).replace("**", "^")
        return re.sub(r"\bE\b", "e", text)
    if isinstance(answer, OrderedAnswer):
        return "(" + ";".join(map(source, answer.components)) + ")"
    return computational_source(answer)


def different_source(answer):
    if isinstance(answer, LimitAnswer):
        return "-inf" if answer.expected == sp.oo else "inf"
    if isinstance(answer, OrderedAnswer):
        first, *tail = answer.components
        return "(" + ";".join([different_source(first), *map(source, tail)]) + ")"
    if isinstance(answer, CategoryAnswer):
        return next(choice for choice in answer.choices if choice != answer.expected)
    if isinstance(answer, RealSetAnswer):
        return "R" if answer.expected == sp.S.EmptySet else "{}"
    return "1" if answer.expected == 0 else "0"


@cache
def reference(name, a, b, c):
    """Numerical evaluation of the original expressions and exact discrete checks."""
    n = 100_000
    t = 1e-6
    if name == "bound_trigonometric":
        values = [(a + 1 + math.sin(k)) / (b + c + 1 - c * math.cos(k)) for k in range(1, 100)]
        assert all(0 < value <= (a + 2) / (b + 1) for value in values)
        return (
            "both",
            min(x / y for x in (a, a + 2) for y in (b + 1, b + 2 * c + 1)),
            max(x / y for x in (a, a + 2) for y in (b + 1, b + 2 * c + 1)),
        )
    if name == "bound_radical":
        assert a - b * math.sqrt(n + c) < -100
        return "upper_only", a - b * math.sqrt(1 + c)
    if name == "monotone_factorial":
        values = [sp.Rational(b * (a + 2) ** k, math.factorial(k + c)) for k in range(1, 18)]
        last_failure = max(
            (k for k, (x, y) in enumerate(zip(values, values[1:], strict=False), 1) if y >= x),
            default=0,
        )
        return "decreasing", last_failure + 1
    if name == "monotone_radical":
        values = [math.hypot(k - a - 1, math.sqrt(b)) + c for k in range(1, 20)]
        last_failure = max(
            k for k, (x, y) in enumerate(zip(values, values[1:], strict=False), 1) if y <= x
        )
        return "increasing", last_failure + 1
    if name == "definition_reciprocal":
        return a + b / (n + c)
    if name == "definition_growth":
        assert a * n * n + b * n - c > 1_000_000
        return sp.oo
    if name == "rational_leading":
        return (a * n**3 + b * n + c) / (n - (c + 1) * n**3)
    if name == "factorial_limit":
        k = 8000
        return (a * k * k + b) * math.factorial(k) / ((c * k + 1) * math.factorial(k + 1))
    if name == "conjugate_sequence":
        return math.sqrt(n * n + 2 * (a + b) * n + c) - math.sqrt(n * n + 2 * b * n)
    if name == "squeeze_oscillation":
        return (a * n + (-1) ** n) / (b * n + c)
    if name == "squeeze_floor":
        return (math.floor(n * math.sqrt(a + 1)) + c) / (math.floor(n * b * math.sqrt(c + 1)) + c)
    if name == "squeeze_root":
        return (a + c + 1 + math.cos(b * n)) ** (1 / n)
    if name == "squeeze_sum":
        return sum(1 / (a * n * n + b * k + c) for k in range(1, n + 1))
    if name == "exponential_power":
        k = 10_000_000
        return (1 + a / (k + b)) ** (c * k - a)
    if name == "exponential_difference":
        small = (1 + b / (n + a)) ** n
        large = (1 + (b + c) / (n + a)) ** n
        return (1 - small) / (small - large)
    if name == "infinite_exponential":
        assert c + (a + 1) ** 40 - (a + b + 2) ** 40 < -(10**20)
        return -sp.oo
    if name == "bound_conjugate":
        values = [c * (math.sqrt(k + a + b) - math.sqrt(k + b)) for k in range(1, 100)]
        assert all(0 < value <= values[0] for value in values)
        return "both", 0, values[0]
    if name == "monotone_ratio":
        values = [
            sp.Rational((a + b + 2) ** k, (a + 1) ** k + c * (a + b + 1) ** k) for k in range(1, 20)
        ]
        assert values == sorted(set(values))
        return "increasing", 1
    if name == "rational_zero":
        return (a * n + b) / (c * n * n + 1)
    if name == "arithmetic_sum_ratio":
        return sum(a * k + b for k in range(1, n + 1)) / sum(c * k + 1 for k in range(1, n + 1))
    if name == "root_exponential_ratio":
        small, medium, large = a + 1, a + b + 2, a + b + c + 3
        k = 50
        return ((medium**k + small**k) / (large**k + medium**k)) ** (1 / k)
    if name == "logarithmic_power":
        # Numerical sequence evaluation would converge only logarithmically.
        # Differentiate log(1+a*t) at t=0 after t=1/log(n+c).
        t = sp.Symbol("t")
        return sp.exp(b * sp.diff(sp.log(1 + a * t), t).subs(t, 0))
    if name == "infinite_factorial":
        assert (b - a * math.factorial(101)) / (math.factorial(100) + c) < -100
        return -sp.oo
    if name == "divergent_oscillation":
        even = b + a + c / n
        odd = b - a + c / (n + 1)
        assert even - odd > 1
        return "does_not_exist"
    if name == "definition_pole":
        assert (a + b) / t > 1_000_000
        return sp.oo
    if name == "rational_cancellation":
        return (a * (c + t) ** 2 - a * c * c) / (t * (c + t + b))
    if name == "radical_cancellation":
        return (math.sqrt(a * t + b * b) - b) / t
    if name == "exponential_dominance":
        return ((a + 1) ** 100 + c) / ((a + b + 2) ** 100 + b)
    if name == "absolute_jump":
        return b + a * (-t) / abs(-t), b + a * t / abs(t), "does_not_exist"
    if name == "essential_exponential":
        assert math.exp(a / 0.01) > 10**40
        return b + math.exp(-a / t), sp.oo, "does_not_exist"
    if name == "squeeze_function":
        return b + math.sqrt(t * t) * math.sin(a / t**4)
    if name == "infinitesimal_exp_sin":
        return math.expm1(a * t) / math.sin(b * t)
    if name == "infinitesimal_log":
        return math.log1p(a * t) / math.atan(b * t)
    if name == "infinitesimal_power":
        return (1 + a * t) ** (b / t)
    if name == "asymptote_rational":
        x = sp.Symbol("x", real=True)
        num = sp.Poly((a * x + b) * (x * x - b * b) + c, x)
        den = sp.Poly(x * x - b * b, x)
        assert sp.gcd(num, den).degree() == 0
        poles = sp.solveset(den.as_expr(), x, sp.S.Reals)
        quotient, remainder = sp.div(num, den)
        assert remainder.degree() < den.degree()
        return poles, quotient.as_expr(), quotient.as_expr()
    if name == "asymptote_inverse_trig":
        x = sp.Symbol("x", real=True)
        f = a * x + b * sp.atan(x - c)
        assert sp.calculus.util.continuous_domain(f, x, sp.S.Reals) == sp.S.Reals
        offsets = [sp.limit(f - a * x, x, end) for end in (-sp.oo, sp.oo)]
        return (sp.S.EmptySet, *(a * x + v for v in offsets))
    if name == "continuity_sine":
        p, q = sp.symbols("p q")
        branch = p + q * sp.sin(b * sp.Symbol("x"))
        x = next(s for s in branch.free_symbols if s.name == "x")
        result = sp.solve(
            (branch.subs(x, 0) - a, branch.subs(x, sp.pi / (2 * b)) - (a + c)), (p, q)
        )
        return result[p], result[q]
    if name == "continuity_reciprocal":
        p = sp.Symbol("p")
        return sp.solve(a - p / sp.Integer(b) - (c + b), p)[0]
    if name == "discontinuity_arctan":
        return c, b + a * math.atan(-1 / t), b + a * math.atan(1 / t), "jump"
    if name == "discontinuity_oscillatory":
        assert math.isclose(b + a * math.cos(c / (c / (40 * math.pi))), b + a)
        assert math.isclose(b + a * math.cos(c / (-c / (41 * math.pi))), b - a)
        return b, "does_not_exist", "does_not_exist", "oscillatory"
    if name == "certified_root":
        low, high = c, c + a * b
        for _ in range(6):
            mid = (low + high) / 2
            residual = math.exp((mid - c) / b) + ((mid - c) / b) ** 2 - a - 1
            assert abs(residual) > 1e-9
            if residual < 0:
                low = mid
            else:
                high = mid
        return sp.Rational((low + high) / 2), sp.Rational((high - low) / 2)
    if name == "two_sided_absolute":
        return a * t + b, a * t + b, a * t + b
    if name == "squeeze_at_infinity":
        return (a + b * math.cos(c * n)) / (n * n)
    if name == "infinitesimal_inverse_trig":
        return math.asin(a * t) / math.atan(b * t)
    if name == "horizontal_asymptote":
        x = sp.Symbol("x", real=True)
        left, right = [
            sp.limit(((a + b) * sp.exp(c * x) + b) / (1 + sp.exp(c * x)), x, z)
            for z in (-sp.oo, sp.oo)
        ]
        return sp.S.EmptySet, left, right
    if name == "discontinuity_removable":
        limits = tuple(a * ((c + d) ** 2 - c * c) / d for d in (-t, t))
        assert abs(limits[0] - (2 * a * c + b)) > 0.5
        return c, *limits, "removable"
    if name == "discontinuity_infinite":
        assert min(a / d**2 + b for d in (-t, t)) > 1e9
        return c, sp.oo, sp.oo, "infinite"
    if name == "certified_cubic":
        low, high = c, c + a + 1
        for _ in range(5):
            mid = (low + high) / 2
            value = (mid - c) ** 3 + (b + 1) * (mid - c) - a
            if value == 0:
                return sp.Rational(mid), 0
            if value < 0:
                low = mid
            else:
                high = mid
        assert (
            (low - c) ** 3 + (b + 1) * (low - c) - a
            < 0
            < (high - c) ** 3 + (b + 1) * (high - c) - a
        )
        return sp.Rational((low + high) / 2), sp.Rational((high - low) / 2)
    if name == "radical_asymptote":

        def y(x):
            return c + a * (x - b) / math.sqrt(x * x - b * b)

        assert y(-b - t) < -100
        assert abs(y(b + t) - c) < 0.01
        return sp.FiniteSet(-b), y(-100 * n), y(100 * n)
    if name == "high_order_pole":
        x = sp.Symbol("x", real=True)
        f = a * x - c + (a + b) / (x - b) ** (2 * (c + 1))
        assert sp.limit(f, x, b, dir="-") == sp.oo
        assert sp.limit(f, x, b, dir="+") == sp.oo
        line = sp.div(*sp.fraction(sp.together(f)), x)[0]
        return sp.FiniteSet(b), line, line
    if name == "conjugate_at_infinity":
        return math.sqrt(n * n + a * n + c) - n + b
    if name == "removable_trigonometric":
        t = 1e-3
        return a * math.sin(b * t) ** 2 / (1 - math.cos(b * t))
    if name == "power_difference":
        return ((1 + t / c) ** (a / 2) - (1 + t / c) ** ((b + 10) / 2)) / t
    if name == "finite_heine_limit":
        return (c + t) ** 3 + a
    if name == "heine_at_infinity":
        return (-a * n + b) / (n * n + c)
    if name == "continuity_free_parameter":
        p, q = sp.symbols("p q")
        x = sp.Symbol("x", real=True)
        left, middle, right = p * x * x + c, b * x + c, x**3 + q * x + c
        assert (middle - right).subs(x, 0) == 0
        return sp.solve((left - middle).subs(x, -a), p)[0], sp.S.Reals
    if name == "discontinuity_pole_and_hole":
        x = sp.Symbol("x", real=True)
        f = c * (x - b) / ((x + a) * (x - b))
        limits = [tuple(sp.limit(f, x, at, dir=side) for side in ("-", "+")) for at in (-a, b)]
        return (-a, *limits[0], "infinite"), (b, *limits[1], "removable")
    if name == "unique_log_exponential_root":
        base, coefficient = b + 1, c + 1
        target = coefficient * base ** (1 + a % 2) + 2 + a % 2
        for candidate in range(1, base**2 + 1):
            value = (
                coefficient * candidate
                + math.log(candidate, base)
                + math.exp(candidate / base ** (1 + a % 2) - 1)
            )
            if math.isclose(value, target):
                return candidate
        pytest.fail("Missing integer root")
    if name == "scaled_conjugate":
        with localcontext() as ctx:
            ctx.prec = 45
            return float(b * n * (Decimal((a * n) ** 2 - c).sqrt() - a * n))
    if name == "rational_pole_and_domain":
        x = sp.Symbol("x", real=True)
        den = x - c
        numerator = sp.expand((a * x - c) * den + b)
        q, r = sp.div(numerator, den, x)
        assert r != 0
        return (
            sp.calculus.util.continuous_domain(numerator / den, x, sp.S.Reals),
            sp.FiniteSet(c),
            q,
            q,
        )
    if name == "exponential_pole":
        x = sp.Symbol("x", real=True)
        f = b * (a + 1) ** x / ((a + 1) ** x - (a + 1) ** c)
        values = [sp.limit(f, x, at) for at in (-sp.oo, sp.oo)]
        return sp.FiniteSet(c), *values
    reference_257 = reference_sequences(name, a, b, c)
    if reference_257 is not None:
        return reference_257
    raise AssertionError(name)


def last_failure(values, fails):
    """Index after the last consecutive pair that breaks the claimed direction."""
    return 1 + max(
        (k for k, (x, y) in enumerate(zip(values, values[1:], strict=False), 1) if fails(x, y)),
        default=0,
    )


def reference_sequences(name, a, b, c):  # noqa: PLR0911, PLR0912
    """#257 oracles: term tables, exact arithmetic and far-out numerical values."""
    n = 10**7
    if name == "bound_root_exponential":
        with localcontext() as ctx:
            ctx.prec = 120
            shift = 1 + (b - 1) % a
            values = [(Decimal(a + 1) ** k - shift) ** (Decimal(1) / k) for k in range(1, 80)]
        assert all(value < a + 1 for value in values)
        assert min(values) == values[0]
        assert a + 1 - values[-1] < Decimal("1e-20")
        return "both", int(values[0]), a + 1
    if name == "bound_geometric_sum":
        terms = [sp.Rational(c, (a + 1) ** k + b * k) for k in range(1, 40)]
        sums = [sum(terms[:k]) for k in range(1, 40)]
        assert sums == sorted(sums)
        tail = sp.Rational(c, a) / (a + 1) ** 39  # geometric bound on the omitted terms
        assert sums[-1] + tail < sp.Rational(c, a)
        return "both", sums[0], sp.Rational(c, a)
    if name == "monotone_exponential_difference":
        large = a + 1 + (b + 1) // 2
        values = [large**k - b * c * (a + 1) ** k for k in range(1, 60)]
        return "increasing", last_failure(values, lambda x, y: y <= x)
    if name == "monotone_rational":
        values = [sp.Rational(b * k, k * k + a * c * (a + c)) for k in range(1, 60)]
        return "decreasing", last_failure(values, lambda x, y: y >= x)
    if name == "monotone_conjugate":
        with localcontext() as ctx:
            ctx.prec = 50
            values = [
                c * ((Decimal(k * k + 2 * b * k + b * b + a)).sqrt() - k) for k in range(1, 300)
            ]
        return "decreasing", last_failure(values, lambda x, y: y >= x)
    if name == "definition_root":
        return a + c / math.sqrt(n * n + b)
    if name == "definition_exponential":
        assert c * (a + 1) ** 60 - b > 10**18
        return sp.oo
    if name == "product_leading_orders":
        return (a * n + 1) ** 2 * (b * n + 1) ** 4 / (c * n * n + 1) ** 3
    if name == "competing_exponentials":
        small, large = a + 1, a + b + 1
        k = 300
        exact = sp.Rational(large ** (k + 1) - small ** (k + 2), c * large**k - small**k)
        return float(exact)
    if name == "radical_degree":
        return (a * n * math.sqrt(n) + b) / math.sqrt(c * n**3 + 1)
    if name == "root_rational_sum":
        return math.exp(math.log(a / n + b / n**2 + c / n**3) / n)
    if name == "negative_growing_power":
        return math.exp((a - c * n) * math.log1p(b / (n + a)))
    if name == "product_of_powers":
        return math.exp(n * (math.log1p(1 / (a * n)) + math.log1p(c / ((a + b) * n))))
    if name == "reciprocal_power":
        return math.exp(-c * n * math.log1p(b / (a * n)))
    if name == "rational_growth":
        sign = 1 if (a + b + c) % 2 == 0 else -1
        value = (sign * a * n * n + b) / (c * n + 1)
        assert abs(value) > 10**5
        return sp.oo if value > 0 else -sp.oo
    if name == "radical_difference_growth":
        with localcontext() as ctx:
            ctx.prec = 60
            value = (Decimal((c + 1) ** 2 + a - 3) * n * n + b).sqrt() - (c + 1) * n
        if abs(value) < Decimal("1e-5"):
            return 0
        assert abs(value) > 10**5
        return sp.oo if value > 0 else -sp.oo
    if name == "inverse_trig_ratio":
        value = (a * math.atan(n) - b) / math.atan(1 / (c * n))
        assert abs(value) > 10**5
        return sp.oo if value > 0 else -sp.oo
    return None


def assert_answer(answer, expected):
    if isinstance(answer, OrderedAnswer):
        for item, value in zip(answer.components, expected, strict=True):
            assert_answer(item, value)
    elif isinstance(expected, float):
        assert float(answer.expected) == pytest.approx(expected, rel=0.001, abs=0.0001)
    else:
        assert answer.expected == expected


@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.prefix)
def test_thousand_seeds_match_independent_results(generator):
    variants = set()
    registered = registry()
    for seed in range(1000):
        params = generator.draw(seed)
        task = generator.build(params)
        triple = (params.a, params.b, params.c)
        assert_answer(task.answer, reference(generator.evaluate.__name__, *triple))
        if triple in variants:
            continue
        variants.add(triple)
        contract = generator.input_contract(params)
        assert contract == task.answer.contract
        assert len(source(task.answer).encode()) <= 256
        tree = parse_answer_input(source(task.answer), contract.kind, contract=contract)
        assert task.answer.check(tree) == "correct"
        render(task, registered)


@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.prefix)
def test_code_and_visual_replay(generator):
    params = generator.draw(123)
    task = generator.build(params)
    issued = render(task, registry())
    opened = rebuild(task.code)
    assert (opened.topic, opened.difficulty) == (generator.topic, generator.difficulty)
    assert opened.problem.issued() == issued


@pytest.mark.skipif(sys.platform != "linux", reason="Actual Linux resource-limited child")
@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.prefix)
def test_actual_worker_accepts_exact_answer_and_rejects_wrong_answer(generator):
    task = generator.build(generator.draw(123))
    record = {"generator_version": generator.version, "code": task.code}
    assert math_worker.check_answer(source(task.answer), record).result == "correct"
    assert math_worker.check_answer(different_source(task.answer), record).result == "incorrect"
