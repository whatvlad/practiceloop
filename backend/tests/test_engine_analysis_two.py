"""Analysis II: coverage, exact independent proofs, frozen reuse and bounded checks."""

import sys

import pytest
import sympy as sp
from pydantic import ValidationError

from app.engine.blocks.analysis_two import AnalysisTwoForm, X
from app.engine.blocks.multiple.form import MultipleForm
from app.engine.blocks.multiple.setup import R, integrand_with_jacobian, integrate_setup
from app.engine.blocks.real_constants import canonical_arctangents
from app.engine.generators import _analysis_improper, _analysis_multivariable, _analysis_ode
from app.engine.generators import _analysis_series as series
from app.engine.generators.analysis_two import SPECS, generators
from app.engine.generators.differentiation import PartialDerivatives
from app.engine.generators.multiple import DoubleIntegrals, TripleIntegrals
from app.engine.opening import rebuild
from app.engine.practice import input_variables, replay
from app.engine.topics.analysis_two import MATRIX
from app.engine.topics.catalogue import topics
from app.math_input import parse_math_input
from app.services.math_worker import check_answer


def text(task) -> str:
    return sp.sstr(task.answer.expected).replace("**", "^").replace("E", "e")


@pytest.mark.parametrize("g", generators(), ids=lambda g: g.version)
def test_every_template_replays_and_checks_equivalence_without_domain_holes(g) -> None:
    for seed in range(40):
        params = g.draw(seed)
        task = g.build(params)
        assert task == g.build(type(params).model_validate_json(params.model_dump_json()))
        variables = task.answer.variables or None
        answer = text(task)
        assert len(answer.encode("ascii")) <= 256
        assert (
            task.answer.check(parse_math_input(f"({answer})+0", variables=variables)) == "correct"
        )
        assert (
            task.answer.check(parse_math_input(f"({answer})+1", variables=variables)) == "incorrect"
        )
        assert (
            task.answer.check(parse_math_input(f"({answer})+0/(x-2)", variables=variables))
            == "invalid"
        )
        assert all(s.text_key in g.step_text for s in task.steps)
    opened = rebuild(task.code)
    assert opened.difficulty == task.metadata["difficulty"] == g.difficulty
    assert g.template in MATRIX[opened.topic][g.difficulty]
    assert replay(opened.problem.issued().record) == task
    assert input_variables(opened.problem.issued().record) == variables


def test_matrix_is_complete_and_reuses_existing_partial_and_multiple_integrals() -> None:
    assert len(SPECS) == len({prefix for _, _, prefix in SPECS}) == 47
    assert {k for levels in MATRIX.values() for kinds in levels.values() for k in kinds} == {
        kind for kind, _, _ in SPECS
    }
    for slug, levels in MATRIX.items():
        assert set(levels) == set(range(1, 6))
        assert topics()[slug].mixed_weight == 1
        for level, kinds in levels.items():
            assert {f"analysis2-{kind}-v1" for kind in kinds} <= {
                c.generator for c in topics()[slug].levels[level]
            }
    for slug, generator in (
        ("partial-derivatives", PartialDerivatives()),
        ("double-integrals", DoubleIntegrals()),
        ("triple-integrals", TripleIntegrals()),
    ):
        assert all(
            {c.generator for c in choices} == {generator.version}
            for choices in topics()[slug].levels.values()
        )


@pytest.mark.parametrize(
    "template", ["polar_disk", "polar_annulus", "polar_sector", "polar_conversion"]
)
def test_retained_double_integral_regions_bounds_and_jacobian_are_still_explicit(template) -> None:
    data = MultipleForm(dimension=2, template=template, variant=0, coefficient=1).evaluate()
    assert data.setup.system == "polar" and len(data.setup.bounds) == 2
    assert sp.simplify(integrand_with_jacobian(data.setup) - data.setup.integrand * R) == 0
    assert sp.simplify(integrate_setup(data.setup) - data.value) == 0
    assert data.statement and all(s.latex for s in data.steps)
    assert any(r"\,r\,dr" in s.latex for s in data.steps)


@pytest.mark.parametrize("change", [{"a": 0}, {"b": 6}, {"c": True}, {"a": 1.5}, {"extra": 2}])
def test_parameters_are_strict_bounded_and_forbid_extra_data(change) -> None:
    with pytest.raises(ValidationError):
        AnalysisTwoForm.model_validate({"a": 1, "b": 1, "c": 1, **change})


@pytest.mark.parametrize("a,b,c", [(1, 1, 1), (2, 3, 4), (5, 4, 2)])
def test_improper_values_match_independent_symbolic_integrals(a, b, c) -> None:
    p = AnalysisTwoForm(a=a, b=b, c=c)
    for kind, integrand, lower in (
        ("improper-power-tail", sp.Rational(a) / X ** (c + 1), b),
        ("improper-exponential", sp.exp(-a * X), b),
        ("improper-arctangent", a / (X**2 + b**2), c),
        ("improper-decay-mass", a * sp.exp(-a * X), b),
        ("improper-volume", sp.pi * a * a / X**2, 1),
    ):
        expected = _analysis_improper.evaluate(kind, p).expected
        actual = sp.integrate(integrand, (X, lower, sp.oo))
        assert sp.simplify(canonical_arctangents(expected) - canonical_arctangents(actual)) == 0


def test_arctangent_reciprocal_identity_is_exact_on_the_positive_real_branch() -> None:
    from app.engine.answers.real_function import ConstantExpressionAnswer

    t = sp.Symbol("t", positive=True)
    identity = sp.atan(t) + sp.atan(1 / t)
    assert sp.simplify(sp.diff(identity, t)) == 0
    assert identity.subs(t, 1) == sp.pi / 2
    answer = ConstantExpressionAnswer(
        sp.Rational(2, 3) * (sp.pi / 2 - sp.atan(sp.Rational(4, 3))), {}
    )
    assert answer.check(parse_math_input("2/3*atan(3/4)")) == "correct"
    assert answer.check(parse_math_input("2/3*(pi/2+atan(4/3))")) == "incorrect"


@pytest.mark.parametrize("c", range(1, 6))
def test_leibniz_absolute_convergence_and_power_interval_endpoints(c) -> None:
    p = AnalysisTwoForm(a=2, b=3, c=c)
    exponent = 1 + c % 2
    absolute = sp.summation(
        1 / sp.Symbol("n", positive=True, integer=True) ** exponent,
        (sp.Symbol("n", positive=True, integer=True), 1, sp.oo),
    )
    assert series.evaluate("series-alternating", p).expected == (1 if absolute.is_finite else 2)
    power = c % 3
    # Endpoint series are alternating n^-p on the left, positive n^-p on the right.
    expected = {0: 0, 1: 1, 2: 3}[power]
    interval = series.evaluate("series-power-interval", p)
    assert interval.expected == expected
    full = next(s.latex for s in interval.steps if s.latex.startswith("I="))
    assert (
        full
        == {
            0: r"I=(\frac{5}{2},\frac{7}{2})",
            1: r"I=[\frac{5}{2},\frac{7}{2})",
            2: r"I=[\frac{5}{2},\frac{7}{2}]",
        }[power]
    )


@pytest.mark.parametrize("c", range(1, 6))
@pytest.mark.parametrize(
    "kind", ["series-taylor", "series-maclaurin-sine", "series-maclaurin-cosine"]
)
def test_taylor_coefficients_equal_independently_differentiated_functions(kind, c) -> None:
    p = AnalysisTwoForm(a=2, b=3, c=c)
    value = series.evaluate(kind, p).expected
    if kind == "series-taylor":
        function, center, degree = sp.exp(2 * (X - 3)), 3, 1 + c % 3
    else:
        sine = kind.endswith("sine") and not kind.endswith("cosine")
        function, center = (sp.sin(2 * X) if sine else sp.cos(2 * X)), 0
        degree = 2 * (1 + c % 3) + int(sine)
    assert sp.Poly(value, X).degree() == degree
    for k in range(degree + 1):
        assert (
            sp.simplify(
                sp.diff(value, X, k).subs(X, center) - sp.diff(function, X, k).subs(X, center)
            )
            == 0
        )


def test_multivariable_results_match_fixed_independent_vector_and_optimization_examples() -> None:
    p = AnalysisTwoForm(a=2, b=3, c=4)
    expected = {
        "multivariable-gradient-two": sp.sqrt(2257),
        "multivariable-directional": sp.Rational(64, 5),
        "multivariable-third-partial": 288,
        "multivariable-differential-two": -sp.Rational(1, 6),
        "multivariable-differential-three": sp.Rational(77, 12),
        "multivariable-gradient-three": 2 * sp.sqrt(29),
        "multivariable-constrained": sp.Rational(96, 5),
        "multivariable-box": sp.Rational(8, 27),
    }
    for kind, value in expected.items():
        assert sp.simplify(_analysis_multivariable.evaluate(kind, p).expected - value) == 0
    assert r"\leq" in _analysis_multivariable.evaluate("multivariable-domain-two", p).steps[1].latex
    assert "<4" in _analysis_multivariable.evaluate("multivariable-domain-three", p).steps[1].latex


@pytest.mark.parametrize("kind", [kind for kind, _, _ in SPECS if kind.startswith("ode-")])
def test_ode_solution_matches_independent_dsolve_with_the_stated_initial_data(kind) -> None:
    p = AnalysisTwoForm(a=2, b=3, c=4)
    y = sp.Function("y")(X)
    equations = {
        "ode-separable-exponential": (sp.diff(y, X) - 2 * X * y, 3, None),
        "ode-separable-root": (sp.diff(y, X) - 2 * X / y, 3, None),
        "ode-linear": (sp.diff(y, X) + 2 * y - 3 * X - 4, 4, None),
        "ode-linear-variable": (sp.diff(y, X) - 4 * X * y - 4 * X, 3, None),
        "ode-harmonic": (sp.diff(y, X, 2) + 4 * y, 3, 8),
        "ode-distinct-roots": (sp.diff(y, X, 2) - 4 * y, 3, 14),
        "ode-repeated-root": (sp.diff(y, X, 2) - 4 * sp.diff(y, X) + 4 * y, 3, 10),
        "ode-resonance": (sp.diff(y, X, 2) + 4 * y - 3 * sp.sin(2 * X), 4, 0),
        "ode-laplace-exponential": (sp.diff(y, X) + 2 * y - 3 * sp.exp(4 * X), 3, None),
        "ode-laplace-oscillator": (sp.diff(y, X, 2) + 4 * y - 3, 0, 4),
    }
    equation, initial, slope = equations[kind]
    ics = {y.subs(X, 0): initial}
    if slope is not None:
        ics[sp.diff(y, X).subs(X, 0)] = slope
    solved = sp.dsolve(sp.Eq(equation, 0), y, ics=ics)
    if isinstance(solved, list):
        solved = next(s for s in solved if s.rhs.subs(X, 0) == initial)
    assert sp.simplify(solved.rhs - _analysis_ode.evaluate(kind, p).expected) == 0


@pytest.mark.parametrize("kind", ["ode-laplace-exponential", "ode-laplace-oscillator"])
def test_laplace_table_matches_independent_sympy_transform(kind) -> None:
    solution = _analysis_ode.evaluate(kind, AnalysisTwoForm(a=2, b=3, c=4)).expected
    actual = sp.laplace_transform(solution, X, _analysis_ode.S, noconds=True)
    assert sp.cancel(actual - _analysis_ode.laplace_table(solution)) == 0


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize("g", generators(), ids=lambda g: g.version)
def test_every_added_version_checks_inside_the_limited_worker(g) -> None:
    task = g.build(g.draw(146))
    record = {"generator_version": g.version, "code": task.code}
    answer = text(task)
    assert check_answer(answer, record).result == "correct"
    assert check_answer(f"({answer})+1", record).result == "incorrect"
    if task.answer.variables:
        assert check_answer(f"({answer})+0/(x-2)", record).result == "invalid"
