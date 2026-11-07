"""Independent solvers certify full sets rather than replaying constructed roots."""

from functools import cache

import pytest
import sympy as sp
from seed_sweep import sweep
from sympy.calculus.util import continuous_domain, function_range

from app.engine.generators.elementary import generators

GENERATORS = {g.template: g for g in generators()}
X = sp.Symbol("x", real=True)


@cache
def equation_roots(expression, domain):
    return sp.solveset(expression, X, domain=domain)


@cache
def inequality_set(relation):
    return sp.solve_univariate_inequality(relation, X, relational=False)


@cache
def natural_domain(expression):
    return continuous_domain(expression, X, sp.S.Reals)


@pytest.mark.parametrize(
    "template",
    [
        "equation-repeated-polynomial",
        "equation-biquadratic",
        "equation-rational-linear",
        "equation-rational-cancel",
        "inequality-squared-factors",
        "inequality-odd-polynomial",
        "inequality-rational-sign",
        "inequality-rational-subtract",
        "log-equation-quadratic",
    ],
)
def test_thousand_seeds_match_independent_complete_real_solvers(template):
    generator = GENERATORS[template]
    x = X
    for seed in sweep(1000):
        params = generator.draw(seed)
        a, b, c = params.a, params.b, params.c
        target = generator.build(params).answer.expected
        domain = sp.S.Reals
        if template == "equation-repeated-polynomial":
            independently = equation_roots(sp.expand(x * (x - a) ** 2), domain)
        elif template == "equation-biquadratic":
            independently = equation_roots(x**4 + (a - b) * x**2 - a * b, domain)
        elif template == "equation-rational-linear":
            domain -= sp.FiniteSet(sp.Rational(c, 2))
            independently = equation_roots(
                a / (2 * x - c) + b / (x - sp.Rational(c, 2)) - 1, domain
            )
        elif template == "equation-rational-cancel":
            domain -= sp.FiniteSet(a, -a)
            original = (x * x - a * a) / (x**3 - a**3) - (x * x + a * a) / (x**3 + a**3)
            independently = equation_roots(original, domain)
        elif template == "inequality-squared-factors":
            independently = inequality_set(
                sp.expand((4 * x * x - a * a) ** 2 - b * b * (2 * x + a) ** 2) <= 0
            )
        elif template == "inequality-odd-polynomial":
            independently = inequality_set(sp.expand(x * (x * x - a) * (x * x + b)) >= 0)
        elif template == "inequality-rational-sign":
            independently = inequality_set((x * x - a * x) / (x + b) > 0)
        elif template == "inequality-rational-subtract":
            independently = inequality_set((x * x + a * x) / (x - b) > x)
        else:
            domain = inequality_set(x > a).intersect(inequality_set(x * x > a * b))
            polynomial = x * x - a * b - (c + 1) ** b * (x - a)
            independently = equation_roots(polynomial, domain)
        assert independently == target, (template, seed, independently, target)


@pytest.mark.parametrize(
    "template",
    [
        "domain-rational",
        "domain-quartic-root",
        "domain-root-quotient",
        "domain-root-rational",
        "domain-log-ratio",
        "domain-arcsin-affine",
        "domain-arccos-square",
        "domain-arctan-rational",
        "domain-exponential-root",
        "domain-arcsin-square",
    ],
)
def test_thousand_domain_seeds_match_independent_continuity_domains(template):
    generator = GENERATORS[template]
    x = X
    for seed in sweep(1000):
        params = generator.draw(seed)
        a, b, c, v = params.a, params.b, params.c, params.variant
        expressions = {
            "domain-rational": c * x / ((x - a) * (x + b)),
            "domain-quartic-root": sp.sqrt(a**4 - x**4),
            "domain-root-quotient": sp.sqrt(b - x) / sp.sqrt(x + a),
            "domain-root-rational": sp.sqrt(a - x) / (x * x + b),
            "domain-log-ratio": sp.log((x - a) / (x + b)),
            "domain-arcsin-affine": sp.asin(a * x - b),
            "domain-arccos-square": sp.acos((x - a) ** 2 + sp.Rational(v + 1, 8)),
            "domain-arctan-rational": sp.atan(b / (x - a)),
            "domain-exponential-root": sp.exp(sp.sqrt(b * b - (x - a) ** 2)),
            "domain-arcsin-square": sp.asin(x * x - a),
        }
        assert natural_domain(expressions[template]) == generator.build(params).answer.expected, (
            template,
            seed,
        )


U = sp.Symbol("u", real=True)


@cache
def angle_solutions(template, variant):
    u, pi = U, sp.pi
    period = (
        pi if template in {"trig-equation-tangent-sum", "trig-inequality-cotangent"} else 2 * pi
    )
    cell = sp.Interval.Ropen(0, period)
    if template == "trig-equation-sine-sum":
        return equation_angles(sp.sin(u) + sp.sin(2 * u), cell), period
    if template == "trig-equation-tangent-sum":
        zeros = equation_angles(sp.sin(u) * sp.sin(2 * u) * sp.sin(3 * u), cell)
        poles = equation_angles(sp.cos(u) * sp.cos(2 * u) * sp.cos(3 * u), cell)
        return zeros - poles, period
    if template == "trig-equation-exponential":
        return equation_angles(sp.sin(u) ** 2 - sp.Rational(variant % 3 + 1, 4), cell), period
    if template.startswith("trig-domain-"):
        denominators = {
            "trig-domain-tan-ratio": sp.sin(u) * sp.cos(u) * (sp.sin(u) + sp.cos(u)),
            "trig-domain-tan-sum": sp.sin(u) * sp.cos(u),
            "trig-domain-half-angle": sp.cos(u / 2),
            "trig-domain-double-angle": sp.Integer(1),
        }
        return cell - equation_angles(denominators[template], cell), period
    if template == "trig-inequality-sine":
        threshold = (sp.Rational(1, 2), sp.sqrt(2) / 2, sp.sqrt(3) / 2)[variant % 3]
        return sp.solve_univariate_inequality(
            sp.sin(u) >= threshold, u, relational=False, domain=cell
        ), period
    if template == "trig-inequality-sine-cosine":
        solved = sp.solve_univariate_inequality(
            sp.sin(u) + sp.cos(u) >= sp.sqrt(3) / 2, u, relational=False, domain=cell
        )
        # The independent tangent-half-angle solver uses atan roots. Certify
        # their principal branches exactly before comparing endpoint forms.
        alpha = sp.asin(sp.sqrt(6) / 4)
        ratio = (sp.sqrt(3) - sp.sqrt(5)) / (sp.sqrt(3) + sp.sqrt(5))
        assert 0 < sp.sqrt(6) / 4 < sp.sqrt(2) / 2  # 0 < alpha < pi/4
        replacements = {}
        for tangent, angle in ((ratio, alpha - sp.pi / 4), (1 / ratio, -alpha - sp.pi / 4)):
            assert sp.simplify(sp.expand_trig(sp.tan(angle)) - tangent) == 0
            replacements[sp.atan(tangent)] = angle
        return solved.xreplace(replacements), period
    if template == "trig-inequality-cotangent":
        # Partition the entire stated cell at every zero and pole. A generic
        # trig inequality solver may only return one primitive subperiod.
        critical = sorted(
            equation_angles(sp.sin(2 * u) * sp.cos(2 * u), cell) | sp.FiniteSet(period)
        )
        pieces = []
        for left, right in zip(critical, critical[1:], strict=False):
            midpoint = (left + right) / 2
            sign = sp.simplify(sp.cos(2 * midpoint) / sp.sin(2 * midpoint))
            if sign < 0:
                pieces.append(sp.Interval.open(left, right))
        return sp.Union(*pieces), period
    raise AssertionError(template)


@cache
def equation_angles(expression, domain):
    return sp.solveset(expression, U, domain=domain)


@cache
def affine_preimage(base, period, slope, phase):
    target_period = period / abs(slope)
    preimage = sp.imageset(sp.Lambda(U, (U - phase) / slope), base)
    return sp.Union(
        *(sp.imageset(sp.Lambda(X, X + k * target_period), preimage) for k in range(-2, 3))
    ).intersect(sp.Interval.Ropen(0, target_period))


@pytest.mark.parametrize(
    "template",
    [
        "trig-domain-tan-ratio",
        "trig-domain-tan-sum",
        "trig-domain-half-angle",
        "trig-domain-double-angle",
        "trig-equation-sine-sum",
        "trig-equation-tangent-sum",
        "trig-equation-exponential",
        "trig-inequality-sine",
        "trig-inequality-sine-cosine",
        "trig-inequality-cotangent",
    ],
)
def test_thousand_periodic_seeds_match_complete_independent_angle_solvers(template):
    generator = GENERATORS[template]
    for seed in sweep(1000):
        params = generator.draw(seed)
        base, period = angle_solutions(template, params.variant)
        slope = (
            -params.b if template == "trig-inequality-sine" and params.variant >= 3 else params.b
        )
        independent = affine_preimage(base, period, slope, params.a * sp.pi / 6)
        actual = generator.build(params).answer
        assert actual.period == period / params.b
        assert independent == actual.base, (template, seed, independent, actual.base)


def test_mixed_cosine_equation_has_exactly_the_two_declared_root_lattices():
    u, pi = U, sp.pi
    factorization = -2 * sp.sin(7 * u / 4 + pi / 4) * sp.sin(9 * u / 4 - pi / 4)
    assert sp.trigsimp(sp.expand_trig(factorization - (sp.cos(4 * u) - sp.sin(u / 2)))) == 0
    generator = GENERATORS["trig-equation-cos-mixed"]
    for seed in sweep(1000):
        params = generator.draw(seed)
        first, second = generator.build(params).answer.components
        assert first.period == 4 * pi / (9 * params.b)
        assert second.period == 4 * pi / (7 * params.b)
        for branch, multiplier, offset in ((first, 9, -pi), (second, 7, pi)):
            for root in branch.base:
                congruence = sp.simplify(
                    (multiplier * (params.b * root + params.a * pi / 6) + offset) / (4 * pi)
                )
                assert congruence.is_integer is True


def same_constant(left, right):
    return left == right or sp.simplify(sp.expand_log(left - right, force=True)) == 0


def same_set(left, right):
    if left == right:
        return True
    if isinstance(left, sp.FiniteSet) and isinstance(right, sp.FiniteSet):
        return len(left) == len(right) and all(
            any(same_constant(first, second) for second in right) for first in left
        )
    if isinstance(left, sp.Interval) and isinstance(right, sp.Interval):
        return (
            left.left_open == right.left_open
            and left.right_open == right.right_open
            and same_constant(left.start, right.start)
            and same_constant(left.end, right.end)
        )
    return False


def logarithmic_image(solution, base):
    if isinstance(solution, sp.FiniteSet):
        return sp.FiniteSet(*(sp.log(root) / sp.log(base) for root in solution))
    if isinstance(solution, sp.Interval):
        lower = -sp.oo if solution.start == 0 else sp.log(solution.start) / sp.log(base)
        upper = sp.oo if solution.end == sp.oo else sp.log(solution.end) / sp.log(base)
        return sp.Interval(lower, upper, solution.left_open, solution.right_open)
    if isinstance(solution, sp.Union):
        return sp.Union(*(logarithmic_image(piece, base) for piece in solution.args))
    return solution


@pytest.mark.parametrize(
    "template",
    [
        "exponential-linear",
        "exponential-substitution",
        "exponential-reciprocal-exponent",
        "exponential-mixed-bases",
        "exponential-product-inequality",
        "exponential-reciprocal-substitution",
        "exponential-rational-inequality",
        "log-equation-power",
        "log-equation-difference",
        "log-inequality-linear",
        "log-inequality-difference",
        "log-inequality-opposite-bases",
    ],
)
def test_thousand_exponential_logarithmic_seeds_match_independent_transformed_solvers(template):
    generator = GENERATORS[template]
    x = X
    positive = sp.Interval.open(0, sp.oo)
    for seed in sweep(1000):
        params = generator.draw(seed)
        a, b, c, v = params.a, params.b, params.c, params.variant
        if template == "exponential-linear":
            solved = equation_roots(b * x - c - (v + 1), sp.S.Reals)
        elif template == "exponential-substitution":
            solved = logarithmic_image(
                equation_roots((c + 1) ** 2 * x * x - (c + 1) * (a + b) * x + a * b, positive),
                c + 1,
            )
        elif template == "exponential-reciprocal-exponent":
            solved = inequality_set((x + b) / x > c)
        elif template == "exponential-mixed-bases":
            solved = equation_roots(
                (x + b) * sp.log(a + 1) - (2 * x + c) * sp.log(c + 1), sp.S.Reals
            )
        elif template == "exponential-product-inequality":
            solved = inequality_set(
                x * sp.log(a + 1) + (x + c) * sp.log(b + 1) < 2 * x * sp.log((a + 1) * (b + 1))
            )
        elif template == "exponential-reciprocal-substitution":
            solved = logarithmic_image(inequality_set(x - 1 / x > c).intersect(positive), a + 1)
        elif template == "exponential-rational-inequality":
            solved = logarithmic_image(
                inequality_set(1 / (x - a) < 1 / (x * x - a * a)).intersect(positive), b + 1
            )
        elif template == "log-equation-power":
            solved = equation_roots(x**a - (c + 1) ** b, positive)
        elif template == "log-equation-difference":
            domain = inequality_set(x + a > 0).intersect(inequality_set(x - b > 0))
            solved = equation_roots((x + a) / (x - b) - (c + 1) ** (v + 1), domain)
        elif template == "log-inequality-linear":
            base = sp.Rational(1, b + 1) if v % 2 else sp.Integer(b + 1)
            comparison = a - c * x < base**a if base < 1 else a - c * x > base**a
            solved = inequality_set(comparison).intersect(inequality_set(a - c * x > 0))
        elif template == "log-inequality-difference":
            domain = inequality_set((a + 1) * x - b > 0).intersect(inequality_set(x - c > 0))
            solved = inequality_set(((a + 1) * x - b) / (x - c) > v + 1).intersect(domain)
        else:
            domain = inequality_set(x - a > 0).intersect(inequality_set(2 * x - b > 0))
            solved = inequality_set((x - a) / (2 * x - b) > (c + 1) ** v).intersect(domain)
        assert same_set(solved, generator.build(params).answer.expected), (
            template,
            seed,
            solved,
            generator.build(params).answer.expected,
        )


@cache
def inverse_certificate(function, source_domain, inverse, inverse_domain):
    assert function_range(function, X, source_domain) == inverse_domain
    assert function_range(inverse, X, inverse_domain) == source_domain
    composition = sp.simplify(sp.expand_log(function.subs(X, inverse) - X, force=True))
    # The semicircle's stated inverse domain lies below its top endpoint.
    for absolute in composition.atoms(sp.Abs):
        argument = absolute.args[0]
        nonnegative = inequality_set(argument >= 0)
        if inverse_domain.is_subset(nonnegative):
            composition = composition.xreplace({absolute: argument})
        elif inverse_domain.is_subset(inequality_set(argument <= 0)):
            composition = composition.xreplace({absolute: -argument})
    assert sp.simplify(composition) == 0


@pytest.mark.parametrize(
    "template",
    [
        "inverse-mobius",
        "inverse-quadratic-branch",
        "inverse-negative-fourth",
        "inverse-exponential",
        "inverse-logarithm",
        "inverse-semicircle-branch",
    ],
)
def test_thousand_inverse_seeds_have_the_full_exact_range_and_correct_branch(template):
    generator = GENERATORS[template]
    x = X
    for seed in sweep(1000):
        params = generator.draw(seed)
        a, b, v = params.a, params.b, params.variant
        if template == "inverse-mobius":
            function, domain = (x + a) / (x - b), sp.S.Reals - sp.FiniteSet(b)
        elif template == "inverse-quadratic-branch":
            function = (x - a) ** 2 - b
            domain = sp.Interval(a, sp.oo) if v % 2 else sp.Interval(-sp.oo, a)
        elif template == "inverse-negative-fourth":
            function, domain = -a * x**4, sp.Interval(-sp.oo, 0)
        elif template == "inverse-exponential":
            base = sp.Integer(params.c + 1) if v % 2 else sp.E
            assert base > 1
            function, domain = sp.exp((a * x - b) * sp.log(base)), sp.S.Reals
        elif template == "inverse-logarithm":
            function, domain = sp.log(x + a) / sp.log(b + 1), sp.Interval.open(-a, sp.oo)
        else:
            function, domain = b - sp.sqrt(a * a - x * x), sp.Interval(-a, 0)
        formula, inverse_domain, inverse_range = generator.build(params).answer.components
        assert inverse_range.expected == domain
        inverse_certificate(function, domain, formula.expected, inverse_domain.expected)


@cache
def composition_certificate(outer, outer_condition, inner, actual_formula, actual_domain):
    inner_domain = natural_domain(inner)
    condition = outer_condition.subs(X, inner)
    preimage = sp.S.Reals if condition is sp.S.true else inequality_set(condition)
    assert actual_domain == inner_domain.intersect(preimage)
    assert sp.simplify(outer.subs(X, inner) - actual_formula) == 0


@pytest.mark.parametrize(
    "template",
    [
        "composition-affine",
        "composition-reciprocal-square",
        "composition-root-power",
        "composition-abs-root",
    ],
)
def test_thousand_composition_seeds_retain_inner_and_outer_domain_constraints(template):
    generator = GENERATORS[template]
    x = X
    for seed in sweep(1000):
        params = generator.draw(seed)
        a, b, c, v = params.a, params.b, params.c, params.variant
        if template == "composition-affine":
            first, second = a * x - b, c * x + a
            conditions = (sp.S.true, sp.S.true)
        elif template == "composition-reciprocal-square":
            first, second = a / x, x * x + (v % 3 - 1) * b
            conditions = (sp.Ne(x, 0), sp.S.true)
        elif template == "composition-root-power":
            first, second = sp.sqrt(a * x), b * x**4
            conditions = (x >= 0, sp.S.true)
        else:
            first, second = c * sp.Abs(x), sp.sqrt(b * x + a)
            conditions = (sp.S.true, b * x + a >= 0)
        result = generator.build(params).answer.components
        for index, (outer, condition, inner) in enumerate(
            [
                (first, conditions[0], first),
                (first, conditions[0], second),
                (second, conditions[1], first),
                (second, conditions[1], second),
            ]
        ):
            composition_certificate(
                outer, condition, inner, result[index * 2].expected, result[index * 2 + 1].expected
            )


@pytest.mark.parametrize("template", ["domain-quadratic-rational", "domain-arccot-affine"])
def test_thousand_original_denominator_and_total_arccot_domains(template):
    generator = GENERATORS[template]
    for seed in sweep(1000):
        params = generator.draw(seed)
        if template == "domain-quadratic-rational":
            sign = 1 if params.variant % 2 else -1
            excluded = equation_roots(X + sign * params.b, sp.S.Reals)
            expected = sp.S.Reals - excluded
        else:
            assert (params.a * X + params.b).is_real is True
            expected = sp.S.Reals
        assert generator.build(params).answer.expected == expected


@cache
def parity_certificate(expression, domain):
    if domain != sp.imageset(sp.Lambda(X, -X), domain):
        return "neither"
    if sp.simplify(expression.subs(X, -X) - expression) == 0:
        return "even"
    if sp.simplify(expression.subs(X, -X) + expression) == 0:
        return "odd"
    return "neither"


def test_thousand_parity_seeds_match_the_definition_and_domain_symmetry():
    generator = GENERATORS["parity"]
    x = X
    for seed in sweep(1000):
        params = generator.draw(seed)
        a, b, c, v = params.a, params.b, params.c, params.variant
        expression = (
            sp.sqrt(x**6 + a),
            sp.Abs(x**7 + b * x**3 - c * x),
            a * x / (x**4 + b),
            x + a / x,
            x**3 + a,
            sp.sqrt(x + a),
        )[v]
        assert (
            parity_certificate(expression, natural_domain(expression))
            == generator.build(params).answer.expected
        )


@pytest.mark.parametrize(
    "template", ["log-value-product", "log-value-change-base", "log-value-ratio", "log-value-root"]
)
def test_thousand_logarithmic_value_seeds_match_direct_exact_evaluation(template):
    generator = GENERATORS[template]
    for seed in sweep(1000):
        params = generator.draw(seed)
        a, b, c = params.a, params.b, params.c
        base = sp.Integer(a + 1)

        def logarithm(value, base=base):
            return sp.log(value) / sp.log(base)

        if template == "log-value-product":
            exact = (
                logarithm(base**b / c) + logarithm(c)
                if params.variant % 2
                else logarithm(base**b * c) - logarithm(c)
            )
        elif template == "log-value-change-base":
            exact = logarithm(b + 1) * sp.log(base**c) / sp.log(b + 1)
        elif template == "log-value-ratio":
            exact = (logarithm(base ** (a + b)) - logarithm(base**b)) / (
                logarithm(base ** (b + c)) - logarithm(base**b)
            )
        else:
            exact = logarithm(base ** sp.Rational(b, c))
        assert same_constant(exact, generator.build(params).answer.expected)


@pytest.mark.parametrize("template", ["trig-linearization-square", "trig-linearization-fourth"])
def test_thousand_multiple_angle_seeds_match_independent_trig_reduction(template):
    generator = GENERATORS[template]
    for seed in sweep(1000):
        params = generator.draw(seed)
        function = sp.cos if params.variant % 2 else sp.sin
        original = (
            params.a * function(params.b * X) ** (4 if template.endswith("fourth") else 2)
            + params.c
        )
        assert trig_identity(generator.build(params).answer.expected - original)


@cache
def trig_identity(expression):
    return sp.trigsimp(expression) == 0


@pytest.mark.parametrize(
    "template",
    [
        "inverse-trig-values",
        "inverse-trig-nested",
        "inverse-trig-cot-branch",
        "inverse-trig-atan-cot",
    ],
)
def test_thousand_principal_inverse_trig_seeds_have_independent_exact_values(template):
    generator = GENERATORS[template]
    for seed in sweep(1000):
        params = generator.draw(seed)
        a, b, c, v = params.a, params.b, params.c, params.variant
        actual = generator.build(params).answer.expected
        if template == "inverse-trig-cot-branch":
            angle = (sp.pi / 6, 5 * sp.pi / 6, 7 * sp.pi / 6)[v] if v < 3 else sp.Integer(a + b + c)
            assert 0 < actual < sp.pi
            assert sp.trigsimp(sp.cot(actual) - sp.tan(angle)) == 0
            continue
        if template == "inverse-trig-nested":
            norm = sp.sqrt(a * a + b * b)
            exact = (
                sp.sin(sp.acos(a / norm)),
                sp.tan(sp.acos(a / norm)),
                sp.sin(sp.atan(sp.Rational(a, b))),
            )[v % 3]
        elif template == "inverse-trig-values":
            values = (0, sp.Rational(1, 2), sp.sqrt(2) / 2, sp.sqrt(3) / 2, 1, -sp.sqrt(3) / 2)
            exact = (
                a * sp.asin(values[v]) + b * sp.acos(values[(v + b) % 6])
                if v < 3
                else a * sp.asin(values[v]) / (b * sp.asin(1))
            )
        else:
            value = (0, 1, sp.sqrt(3), 1 / sp.sqrt(3), -1, -sp.sqrt(3))[v]
            # The cotangent equation has exactly one solution in (0,pi).
            principal_cot = sp.acot(value) + (sp.pi if value < 0 else 0)
            exact = (
                a * b * sp.atan(value) * principal_cot
                if v % 2
                else a * sp.atan(value) - b * principal_cot
            )
        assert sp.simplify(exact - actual) == 0, (template, seed, exact, actual)


def test_tangent_equation_factorization_keeps_every_original_pole():
    u = U
    original = sp.sin(u) / sp.cos(u) + sp.sin(2 * u) / sp.cos(2 * u) - sp.sin(3 * u) / sp.cos(3 * u)
    factored = (
        -sp.sin(u) * sp.sin(2 * u) * sp.sin(3 * u) / (sp.cos(u) * sp.cos(2 * u) * sp.cos(3 * u))
    )
    denominator = sp.cos(u) * sp.cos(2 * u) * sp.cos(3 * u)
    numerator = sp.expand_trig(sp.cancel((original - factored) * denominator))
    sine, cosine = sp.symbols("sine cosine", real=True)
    polynomial = sp.Poly(numerator.subs({sp.sin(u): sine, sp.cos(u): cosine}), sine, cosine)
    identity = sp.Poly(sine**2 + cosine**2 - 1, sine, cosine)
    assert polynomial.rem(identity).is_zero


def test_thousand_three_atom_negations_and_nested_not_match_independent_boolean_definitions():
    from itertools import product

    from app.engine.answers.logic import truth

    for seed in sweep(1000):
        generator = GENERATORS["logic-negation-equivalence"]
        params = generator.draw(seed)
        answer = generator.build(params).answer
        for p, q, r in product((False, True), repeat=3):
            first = not p if params.variant % 2 else p
            second = not q if params.variant // 2 % 2 else q
            third = not r if params.c % 2 else r
            assert truth(answer.expected, {"p": p, "q": q, "r": r}) == (first != (second and third))
        generator = GENERATORS["logic-negation-not"]
        params = generator.draw(seed)
        for p in (False, True):
            assert truth(generator.build(params).answer.expected, {"p": p}) == (
                p if params.a % 2 else not p
            )


def test_thousand_quantifier_models_have_explicit_global_witnesses_or_counterexamples():
    for seed in sweep(1000):
        for name in (
            "quantifier-order",
            "quantifier-polynomial",
            "quantifier-cubic-witness",
            "quantifier-total-order",
            "quantifier-power",
            "quantifier-trigonometric",
            "quantifier-product",
        ):
            generator = GENERATORS[name]
            params = generator.draw(seed)
            a, b, c, v = params.a, params.b, params.c, params.variant
            if name == "quantifier-trigonometric":
                # A constant phase works for every x, hence for all three orders.
                assert trig_identity(sp.sin(a * X) + sp.cos(a * X + sp.pi / 2 + 2 * sp.pi * b))
                expected = True
            elif name == "quantifier-product":
                rhs = 0 if v % 2 else c
                assert sp.expand((X - a) * (b - b)) == 0
                expected = rhs == 0
            elif name == "quantifier-order":
                # One fixed y cannot equal both a and a+1; y=x+a is always real.
                assert a != a + 1 and (X + a).is_real is True
                expected = not v % 2
            elif name == "quantifier-cubic-witness":
                # A real cubic is a bijection; all x have a unique real witness.
                assert (X**3).diff(X) == 3 * X**2
                assert -b / a != -(b + 1) / a
                expected = not v % 2
            elif name == "quantifier-polynomial":
                assert (a - a) ** 2 <= b and ((a + b + 1) - a) ** 2 > b
                expected = bool(v % 2)
            elif name == "quantifier-power":
                assert a**a != (a + 1) ** (a + 1)
                expected = not v % 2
            else:
                # Equality is the decisive missing case when both sides are strict.
                assert sp.simplify((a * X + b) - (a * X + b)) == 0
                expected = not v % 2
            assert generator.build(params).answer.expected == ("true" if expected else "false")
