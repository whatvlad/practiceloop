"""Acceptance corpus for #100 triple-v1: values, cross-checks, solutions and rejection."""

from dataclasses import replace

import mpmath
import pytest
import sympy as sp

from app.generators.multiple import THETA, Setup, X, jacobian
from app.generators.triple import (
    COEFFICIENTS,
    TEMPLATES,
    Z,
    records,
    replay_triple,
    verify_triple,
)

# Template, level and value at coefficient 1, fixed independently of the code (ADR-005).
CASES = [
    ("box_product", 1, sp.Rational(1, 2)),
    ("box_power", 1, sp.Integer(3)),
    ("box_sum", 2, sp.Integer(2)),
    ("box_linear", 2, sp.Integer(4)),
    ("simplex", 3, sp.Rational(2, 3)),
    ("cylinder_moment", 3, 3 * sp.pi / 2),
    ("cylinder_height", 3, 2 * sp.pi),
    ("cone", 4, 8 * sp.pi / 3),
    ("paraboloid", 4, 8 * sp.pi),
    ("tetrahedron", 4, sp.Rational(2, 3)),
    ("quarter_exponential", 5, sp.pi * (sp.E - 1) / 2),
    ("half_logarithm", 5, sp.pi * sp.log(2) / 2),
]


def record(name: str, coefficient: int = 1) -> dict[str, object]:
    return {"generator_version": "triple-v1", "template": name, "coefficient": coefficient}


def numeric(setup: Setup) -> mpmath.mpf:
    """An independent value: SymPy integrates z exactly, mpmath the outer two variables."""
    (inner, low, high), *outer = setup.bounds
    surface = sp.integrate(setup.integrand * jacobian(setup.system), (inner, low, high))
    (middle, middle_low, middle_high), (last, last_low, last_high) = outer
    f = sp.lambdify((last, middle), surface, "mpmath")
    lower = sp.lambdify(last, middle_low, "mpmath")
    upper = sp.lambdify(last, middle_high, "mpmath")

    def split(low: mpmath.mpf, high: mpmath.mpf) -> list[mpmath.mpf]:
        # The cone's |(x, y)| has a kink at the axis; quadrature needs it as an endpoint.
        return [low, mpmath.mpf(0), high] if low < 0 < high else [low, high]

    return mpmath.quad(
        lambda u: mpmath.quad(lambda v: f(u, v), split(lower(u), upper(u))),
        split(mpmath.mpf(sp.N(last_low, 20)), mpmath.mpf(sp.N(last_high, 20))),
    )


def test_cases_cover_every_template_and_level() -> None:
    assert {name for name, _, _ in CASES} == set(TEMPLATES)
    for level in range(1, 6):
        assert len([name for name, lv, _ in CASES if lv == level]) >= 2


@pytest.mark.parametrize("case", CASES, ids=[case[0] for case in CASES])
@pytest.mark.parametrize("coefficient", COEFFICIENTS)
def test_complete_triple_corpus(case, coefficient) -> None:
    name, level, value = case
    problem = replay_triple(record(name, coefficient))
    assert problem.difficulty == level
    assert problem.topic == "triple-integrals"
    assert sp.simplify(problem.value - coefficient * value) == 0
    for _, wrong in problem.mistakes:
        assert sp.simplify(wrong - problem.value) != 0


@pytest.mark.parametrize("case", CASES, ids=[case[0] for case in CASES])
def test_values_match_numerical_integration_in_both_systems(case) -> None:
    """The solution set-up, and the other system's set-up where the solid allows it."""
    name, _, value = case
    template = TEMPLATES[name]
    setups = [template.setup] + ([template.other] if template.other else [])
    for setup in setups:
        assert abs(numeric(setup) - mpmath.mpf(sp.N(value, 25))) < mpmath.mpf("1e-9")
    for _, wrong_setup, wrong in template.mistakes:
        assert abs(numeric(wrong_setup) - mpmath.mpf(sp.N(wrong, 25))) < mpmath.mpf("1e-9")


def test_cylindrical_solids_are_cross_checked() -> None:
    for name, template in TEMPLATES.items():
        if template.setup.system == "cylindrical":
            assert template.other is not None and template.other.system == "cartesian", name


@pytest.mark.parametrize("name", list(TEMPLATES))
def test_statement_and_solution_steps(name) -> None:
    problem = replay_triple(record(name, 2))
    template = problem.template
    assert "{f}" not in problem.statement
    # Levels 1-3 name the system; levels 4-5 leave the choice to the learner.
    if template.difficulty <= 3:
        assert "coordinates" in problem.statement or problem.statement.startswith(r"\int")
    else:
        assert "coordinates" not in problem.statement
    steps = problem.solution_steps
    says = [step["say"] for step in steps]
    assert says[0].startswith("Describe the solid")
    assert sum(say.startswith("Integrate with respect to") for say in says) == 3
    if template.setup.system == "cylindrical":
        assert r"dV = r\,dz\,dr\,d\theta" in steps[1]["latex"]
    if template.other is not None:
        assert says[-2].startswith("As a check")
    assert steps[-1]["latex"] == problem.answer_latex


def test_records_cover_each_level() -> None:
    for level in range(1, 6):
        cell = records(level)
        assert cell and all(
            set(item) == {"generator_version", "template", "coefficient"} for item in cell
        )


@pytest.mark.parametrize(
    "bad",
    [
        {},
        {**record("box_product"), "extra": 1},
        record("box_product", 0),
        record("box_product", -1),
        record("box_product", 4),
        {**record("box_product"), "coefficient": True},
        {**record("box_product"), "coefficient": "1"},
        {**record("box_product"), "coefficient": 1.0},
        {**record("box_product"), "generator_version": "double-v1"},
        record("sphere"),
        record("x" * 40),
        {"generator_version": "triple-v1", "template": "box_product"},
    ],
)
def test_replay_rejects_bad_records(bad) -> None:
    with pytest.raises(ValueError):
        replay_triple(bad)


def test_verify_rejects_wrong_values_and_mistakes() -> None:
    cone = TEMPLATES["cone"]
    with pytest.raises(RuntimeError, match="value differs"):
        verify_triple(replace(cone, value=3 * sp.pi))
    with pytest.raises(RuntimeError, match="not pedagogically clean"):
        verify_triple(
            replace(
                cone,
                setup=Setup(
                    "cylindrical",
                    sp.Integer(1),
                    (
                        (Z, 0, 2),
                        (sp.Symbol("r", positive=True), 0, sp.Rational(7, 5)),
                        (THETA, 0, 2 * sp.pi),
                    ),
                ),
                value=sp.Rational(98, 25) * sp.pi,
                mistakes=(),
            )
        )
    code, wrong_setup, wrong = cone.mistakes[0]
    with pytest.raises(RuntimeError, match="mistake value differs"):
        verify_triple(replace(cone, mistakes=((code, wrong_setup, wrong + 1),)))
    with pytest.raises(RuntimeError, match="must differ"):
        verify_triple(replace(cone, mistakes=((code, cone.setup, cone.value),)))
    with pytest.raises(RuntimeError, match="integrand differs"):
        verify_triple(replace(cone, integrand=X))


def test_worker_replay_does_not_integrate(monkeypatch) -> None:
    import app.generators.triple as triple

    def fail(_setup: Setup) -> None:
        raise AssertionError("the worker must not integrate")

    monkeypatch.setattr(triple, "integrate_setup", fail)
    for name in TEMPLATES:
        problem = replay_triple(record(name, 3), verify=False)
        assert problem.value.is_number
