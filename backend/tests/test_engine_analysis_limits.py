"""Check independent oracles, code replay and public contracts for #236."""

import math
import re
import sys
from decimal import Decimal, localcontext
from functools import cache

import mpmath
import pytest
import sympy as sp
from test_engine_elementary import source as computational_source

from app.engine.answers.computational import (
    CategoryAnswer,
    LimitAnswer,
    OrderedAnswer,
    PeriodicSetAnswer,
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
    return re.sub(r"\bE\b", "e", computational_source(answer))


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
    if isinstance(answer, PeriodicSetAnswer):
        return "(" + sp.sstr(answer.period) + ";{0})"
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
    return reference_exam_sequences(name, a, b, c)


def reference_exam_sequences(name, a, b, c):  # noqa: PLR0911
    """#257 exam forms, evaluated far out with exact integers or 60-digit decimals."""
    n = 10**7
    with localcontext() as ctx:
        ctx.prec = 60
        if name == "root_exponential_sum":
            k = 20_000
            return math.exp(math.log((a + 1) ** (k + c) + (a + b + 1) ** (k + 1)) / k)
        if name == "root_polynomial":
            return math.exp(math.log(a * n ** (b + 1) + c * n + 1) / n)
        if name == "quartic_conjugate":
            k = Decimal(10**6)
            value = (a * a * k**4 + b * k**3 + c).sqrt() - a * k * k
            assert value > 10**4
            return sp.oo
        if name == "conjugate_ratio":
            k = Decimal(10**6)
            return float(((k * k + a + b).sqrt() - k) / ((k * k + c).sqrt() - k))
        if name == "factorial_degree_ratio":
            k = 20_000
            exact = sp.Rational(
                (a * k + b) * math.factorial(k + 1), k * k * (math.factorial(k) + c)
            )
            return float(exact)
        if name == "exponential_product_ratio":
            k = 200
            exact = sp.Rational(
                ((a + 1) ** k + 1) * ((b + 1) ** (k + 1) + c), ((a + 1) * (b + 1)) ** k + a
            )
            return float(exact)
        if name == "reciprocal_exponential_conjugate":
            ctx.prec = 200
            power = Decimal(a + 1) ** 60
            return float(b / (power * ((power * power + c).sqrt() - power)))
        if name == "product_radical":
            k = Decimal(n)
            return float(c * (((k + a) * (k + b)).sqrt() - k))
    return reference_functions(name, a, b, c)


def signed_infinity(value):
    assert abs(value) > 10**5
    return sp.oo if value > 0 else -sp.oo


def reference_functions(name, a, b, c):  # noqa: PLR0911, PLR0912
    """#258 oracles: 50-digit evaluation of the displayed function next to the point."""
    with mpmath.workdps(50):
        t, big = mpmath.mpf("1e-15"), mpmath.mpf("1e15")
        if name == "rational_substitution":
            return float((c * c - a) / mpmath.mpf(c * c - b * c + b * b))
        if name == "radical_quotient_zero":
            return float((a * t + b * mpmath.sqrt(t)) / (c * mpmath.sqrt(t)))
        if name == "power_difference_quotient":
            low, high = a + 1, a + b + 1
            x = c + t
            return float((x**low - c**low) / (x**high - c**high))
        if name == "leading_power_quotient":
            k = b + 1
            x = big
            return float((a * x**3 + 1) ** k / ((x + 1) ** (k + 2) * (c * x * x + 1) ** (k - 1)))
        if name == "conjugate_minus_infinity":
            x = -big
            return float(mpmath.sqrt(a * a * x * x + (b - 3) * x + c) + a * x)
        if name == "tangent_ratio":
            tan2 = mpmath.tan(mpmath.pi / 2 - t) ** 2
            return float((a * tan2 + b) / (c * tan2 + b + c))
        if name == "radical_linear_ratio":
            return float((mpmath.sqrt(a * a * big**2 + big) + b) / (c * big + 1))
        if name == "cancelling_reciprocals":
            m = b + 1
            return float(sum(c * (1 / (1 - x) - m / (1 - x**m)) for x in (1 - t, 1 + t)) / 2)
        if name == "bounded_inverse_trig":
            sides = [a * x * mpmath.atan(b / x) + c for x in (-t, t)]
            assert all(abs(side - c) < 1e-10 for side in sides)
            return c, c, c
        if name == "squeeze_arctan":
            return float(a * t * t * mpmath.atan(b / t) + c)
        if name == "sine_product_square":
            return float(mpmath.sin(a * t) * mpmath.sin(b * t) / (c * t * t))
        if name == "sine_radical":
            x = c * c + t
            return float(mpmath.sin(a * (x - c * c)) / (mpmath.sqrt(x) - c))
        if name == "arctan_at_infinity":
            value = a * big ** (1 + c % 2) * mpmath.atan(b / big)
            return float(value) if c % 2 == 0 else signed_infinity(value)
        if name == "cosine_ratio_half_pi":
            top, bottom = 2 * a - 1, 2 * b - 1
            bottom += 2 if top == bottom else 0
            x = mpmath.pi / 2 + t
            return float(c * mpmath.cos(top * x) / mpmath.cos(bottom * x))
        if name == "log_cube_root":
            x = t**2  # x^(-1/3) grows slowly
            power = mpmath.mpf(1 + c % 3) / 3
            value = mpmath.log(1 + a * mpmath.cbrt(x)) / (b * x**power)
            return float(value) if c % 3 == 0 else signed_infinity(value)
        if name == "log_near_one":
            x = -c + t
            return float(mpmath.log(a * x * x - a * c * c + 1) / (b * (x + c)))
        if name == "tangent_power":
            return float((1 + a * mpmath.tan(b * t)) ** mpmath.cot(c * t))
        if name == "root_difference":
            return float((mpmath.root(1 + a * t, c + 1) - mpmath.root(1 - b * t, c + 2)) / t)
        if name == "sine_quadratic_ratio":
            x = c + t
            return float(mpmath.sin(b * x * x - b * c * c) / ((x - c) * (x - c + a)))
        if name == "log_difference_infinity":
            return float(a * big * (mpmath.log(c * big + b) - mpmath.log(c * big)))
        if name == "log_quadratic_at_point":
            x = c + t
            return float(mpmath.log(x * x - b * x - (c * c - b * c - 1)) / (x - c))
        if name == "sine_power_product":
            x = mpmath.mpf("1e-6")
            return float(mpmath.sin(a * x**5) / (mpmath.sin(b * x * x) * mpmath.sin(c * x**3)))
    return reference_asymptotes(name, a, b, c)


def slope_and_offset(f, far):
    """Numerical slope and offset of f far out; None when either clearly diverges."""
    slope = f(far) / far
    return slope, f(far) - mpmath.nint(slope) * far


def reference_asymptotes(name, a, b, c):  # noqa: PLR0911, PLR0912, PLR0915
    """#259 oracles: the displayed functions at 50 digits near poles and far out."""
    x = sp.Symbol("x", real=True)
    dne = "does_not_exist"
    with mpmath.workdps(50):
        near, far = mpmath.mpf("1e-12"), mpmath.mpf("1e20")
        if name == "radical_growth_asymptotes":

            def f(x):
                return (a * x * mpmath.sqrt(x) + b) / (x + c)

            assert f(far) / far < 1e-6
            assert f(far) > 1e8
            return sp.S.EmptySet, 0, sp.oo
        if name == "oscillatory_remainder":

            def f(x):
                return (a * x * x + c * x + b * mpmath.sin(x)) / x

            assert abs(f(near) - (b + c)) < 1e-6
            values = [slope_and_offset(f, end) for end in (-far, far)]
            return sp.S.EmptySet, *(float(v) for pair in values for v in pair)
        if name == "exponential_zero_denominator":

            def f(x):
                return b * mpmath.cos(c * x) / (mpmath.exp(a * x) - 1)

            assert f(-near) < -1e9 < 1e9 < f(near)
            k = 10**6
            even, odd = f(-2 * mpmath.pi * k / c), f(-(2 * k + 1) * mpmath.pi / c)
            assert abs(f(-far) / far) < 1e-10
            assert abs(even + b) < 1e-6
            assert abs(odd - b) < 1e-6
            assert abs(f(mpmath.mpf(60))) < 1e-20
            return sp.FiniteSet(0), 0, dne, 0, 0
        if name == "trig_periodic_poles":

            def f(x):
                return (a * mpmath.sin(2 * x) + b * mpmath.cos(x)) / (mpmath.sin(x) - 1) + c

            assert abs(f(mpmath.pi / 2 + near)) > 1e9
            grid = [2 * mpmath.pi * k / 400 for k in range(400)]
            poles = [p for p in grid if abs(mpmath.sin(p) - 1) < 1e-9]
            assert len(poles) == 1
            assert abs(poles[0] - mpmath.pi / 2) < 1e-30
            k = 10**6
            assert abs(f(2 * mpmath.pi * k) / (2 * mpmath.pi * k)) < 1e-5
            assert abs(f(mpmath.pi / 2 + 2 * mpmath.pi * k + near)) / k > 1e3
            return (2 * sp.pi, sp.FiniteSet(sp.pi / 2)), dne, dne, dne, dne
        if name == "continuity_log_ratio":

            def f(x):
                return 1 / (mpmath.log(a * x * x) - mpmath.log(a * x * x + b))

            tiny = mpmath.mpf("1e-100000")
            sides = [f(-tiny), f(tiny)]
            assert all(abs(side) < 1e-5 for side in sides)
            assigned = c % 3 - 1
            return 0, 0, "continuous" if assigned == 0 else "removable"
        if name == "exp_join":
            c = 1 + c % 2  # the generated join point
            p = (mpmath.exp(a * near) - 1) / near
            q = ((mpmath.exp(a * c) - 1) / c + b) / (c * c)
            return float(p), float(q)
        if name == "quartic_cubic_oblique":

            def f(x):
                return (a * x**4 - b * x**3) / (x**3 + c * x)

            assert abs(f(near)) < 1e-6
            values = [slope_and_offset(f, end) for end in (-far, far)]
            return sp.S.EmptySet, *(float(v) for pair in values for v in pair)
        if name == "radical_oblique_right":

            def f(x):
                return (x - c) * mpmath.sqrt(x - a - 2 * b) / mpmath.sqrt(x - a)

            assert mpmath.sqrt(2 * b) > 0  # denominator bounded below on [a+2b, inf)
            return sp.S.EmptySet, *(float(v) for v in slope_and_offset(f, far))
        if name == "radical_quotient_right":

            def f(x):
                return b * mpmath.sqrt(x**3 - c**3) / mpmath.sqrt(x - c)

            assert abs(f(c + near) - b * mpmath.sqrt(3) * c) < 1e-5
            return sp.S.EmptySet, *(float(v) for v in slope_and_offset(f, far))
        if name in {"rational_oblique_pole", "rational_oblique_pole_left"}:
            sign = 1 if name == "rational_oblique_pole" else -1
            numerator = x * (x - sign * b)
            denominator = x - sign * (a + b)
            quotient, remainder = sp.div(numerator, denominator, x)
            assert remainder != 0
            poles = sp.solveset(denominator, x, sp.S.Reals)
            return sp.S.Reals - poles, poles, quotient, quotient
    return reference_lhopital(name, a, b, c)


def assert_answer(answer, expected):
    if isinstance(answer, OrderedAnswer):
        for item, value in zip(answer.components, expected, strict=True):
            assert_answer(item, value)
    elif isinstance(answer, PeriodicSetAnswer):
        assert (answer.period, answer.base) == expected
    elif isinstance(expected, float):
        assert float(answer.expected) == pytest.approx(expected, rel=0.001, abs=0.0001)
    else:
        assert answer.expected == expected


# Derivative versions (#260) share the provider; their oracles are in test_engine_derivatives.
LIMIT_GENERATORS = [
    g
    for g in generators()
    if not g.evaluate.__module__.endswith(("_derivatives", "_extrema", "_convexity"))
]


@pytest.mark.parametrize("generator", LIMIT_GENERATORS, ids=lambda g: g.prefix)
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


def reference_lhopital(name, a, b, c):  # noqa: PLR0911, PLR0912
    """#261 oracles: errors from finite differences, limits at 50 digits near the point."""
    with mpmath.workdps(50):
        t, big = mpmath.mpf("1e-12"), mpmath.mpf("1e12")

        def spread(f, x, step):
            """Half the change of f over x +- step: the differential estimate, independently."""
            return abs(f(x + step) - f(x - step)) / 2

        if name == "error_triangle_area":
            angle = (mpmath.pi / 3, mpmath.pi / 4, mpmath.pi / 6)[b % 3]
            side = 50 * (a + 1)
            return float(spread(lambda x: side * side * mpmath.sin(x) / 2, angle, c / 100))
        if name == "error_sphere_volume":
            d = 2 * (a + 2)
            return float(spread(lambda x: mpmath.pi * x**3 / 6, d, mpmath.mpf(b) / 10**6) * 10**4)
        if name == "error_fall_depth":
            time = mpmath.mpf(30 + 2 * a + b) / 10
            step = mpmath.mpf(1) / (10 if c % 2 else 20)
            return float(spread(lambda x: mpmath.mpf("9.8") * x * x / 2, time, step))
        if name == "error_average_speed":
            distance = 100 * (1 + a % 2)
            time = mpmath.mpf(1000 + 50 * b + 10 * c) / 100 * (1 + a % 2)
            return float(spread(lambda x: distance / x, time, mpmath.mpf(1) / 10**8) * 10**6)
        if name == "log_exponential_growth":
            return float(mpmath.log((a + 1) ** big + b) / (c * big))
        if name == "log_sine_ratio":
            x = a + t
            return float(mpmath.log(mpmath.sin(mpmath.pi * x / (2 * a))) / (b * mpmath.log(x / a)))
        if name == "arctan_difference":
            power = 2 + c % 2
            x = mpmath.mpf("1e-8")
            return float((a * x - mpmath.atan(a * x)) / x**power)
        if name == "double_root_quotient":
            n, x = b + 2, 1 + mpmath.mpf("1e-15")
            return float((x ** (2 * n) - 2 * n * x + 2 * n - 1) / (x**n - n * x + n - 1))
        if name == "log_cosine_ratio":
            bb = b if a != b else a + 1
            return float(mpmath.log(mpmath.cos(a * t)) / mpmath.log(mpmath.cos(bb * t)))
        if name == "root_arccot":
            power = mpmath.sqrt(big) if c % 2 else big
            return float(a * power * mpmath.acot(b * big))
        if name == "power_log_zero":
            return float(a * t**b * mpmath.log(t))
        if name == "tangent_half_angle":
            x = b * mpmath.pi - t
            return float(a * (b * mpmath.pi - x) * mpmath.tan(x / (2 * b)))
        if name == "cosine_difference":
            k = 2 * a + (c % 3 - 1)
            x = mpmath.mpf("1e-6")
            value = a / (1 - mpmath.cos(x)) - k / x**2
            return float(value) if k == 2 * a else signed_infinity(value)
        if name == "cotangent_difference":
            k = a + (c % 3 - 1)
            x = -t
            value = a / x - k * mpmath.cot(x)
            return float(value) if k == a else signed_infinity(value)
        if name == "log_reciprocal_sum":
            x = 1 + t
            return float(a * (1 / mpmath.log(x) + 1 / (1 - x)))
        if name == "log_power_zero":
            x = mpmath.mpf("1e-40")
            return float((-a * mpmath.log(x)) ** (b * x))
        if name == "arctan_power":
            return float((2 / mpmath.pi * mpmath.atan(a * big)) ** (b * big))
        if name == "log_exponent_power":
            x = mpmath.mpf("1e-30")
            return float((1 + a * x) ** (b * mpmath.log(x)))
        if name == "tangent_cosine_power":
            x = mpmath.pi / 2 - mpmath.mpf("1e-30")
            return float((a * mpmath.tan(x)) ** (b * mpmath.cos(x)))
        if name == "exponential_cosh":
            x = mpmath.mpf("1e-10")
            return float((mpmath.exp(a * x) + mpmath.exp(-a * x) - 2) / (b * x * x))
        if name == "one_minus_power":
            x = 1 - mpmath.mpf("1e-30")
            return float((a * (1 - x)) ** mpmath.sin(b * mpmath.pi * x))
        if name == "tangent_log":
            x = mpmath.mpf("1e-30")
            return float(mpmath.tan(a * x) * mpmath.log(x))
        if name == "log_tangent_product":
            x = mpmath.mpf("1e-30")
            return float(a * x * mpmath.log(mpmath.tan(b * x)))
        if name == "differentiable_join":
            # q from continuity at 0, p from matching one-sided difference quotients.
            left = lambda x: mpmath.exp(a * x) + b * x  # noqa: E731
            q = left(0)
            p = (left(0) - left(-t)) / t
            return float(p), float(q)
    return None
