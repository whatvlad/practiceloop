"""Independent acceptance corpus for #77–#80 and the ADR-003 structural matrix."""

import json
import random
from dataclasses import replace
from itertools import product

import pytest
import sympy as sp
from sympy.calculus.util import continuous_domain

from app.generators.basic import C, X
from app.generators.core import replay as replay_preview
from app.generators.families import (
    FamilyStep,
    _families,
    generate_family,
    replay_family,
    verify_family,
)
from app.services.math_parser import parse_math_input
from app.services.math_worker import _build_sympy

# Version, template, level, integrand, answer at coefficient = 1.
CASES = [
    ("substitution-v2", "visible_pair", 1, 2 * X * sp.cos(X**2), sp.sin(X**2)),
    ("substitution-v2", "affine_factor", 2, sp.cos(2 * X + 1), sp.sin(2 * X + 1) / 2),
    ("substitution-v2", "polynomial_inner", 3, 3 * X**2 * sp.exp(X**3), sp.exp(X**3)),
    ("substitution-v2", "factor_square", 4, X * (X**4 + 2 * X**2 + 1), (X**2 + 1) ** 3 / 6),
    (
        "substitution-v2",
        "identity_nested",
        5,
        X * sp.sin(X**2) * sp.sin(2 * X**2),
        sp.sin(X**2) ** 3 / 3,
    ),
    ("parts-v1", "linear_exponential", 1, X * sp.exp(X), (X - 1) * sp.exp(X)),
    ("parts-v1", "quadratic_exponential", 2, X**2 * sp.exp(X), (X**2 - 2 * X + 2) * sp.exp(X)),
    ("parts-v1", "cyclic_sine", 3, sp.exp(X) * sp.sin(X), sp.exp(X) * (sp.sin(X) - sp.cos(X)) / 2),
    ("rational-v1", "linear_denominator", 1, 1 / X, sp.log(sp.Abs(X))),
    ("rational-v1", "denominator_derivative", 2, 2 * X / (X**2 + 1), sp.log(X**2 + 1)),
    (
        "rational-v1",
        "distinct_factors",
        3,
        1 / (X * (X + 1)),
        sp.log(sp.Abs(X)) - sp.log(sp.Abs(X + 1)),
    ),
    (
        "rational-v1",
        "repeated_factor",
        4,
        1 / (X * (X + 1) ** 2),
        sp.log(sp.Abs(X)) - sp.log(sp.Abs(X + 1)) + 1 / (X + 1),
    ),
    (
        "rational-v1",
        "division_then_fractions",
        5,
        (X**3 + X + 1) / (X * (X + 1)),
        X**2 / 2 - X + sp.log(sp.Abs(X)) + sp.log(sp.Abs(X + 1)),
    ),
    ("trigonometric-v1", "sine", 1, sp.sin(X), -sp.cos(X)),
    ("trigonometric-v1", "double_argument", 2, sp.sin(2 * X), -sp.cos(2 * X) / 2),
    ("trigonometric-v1", "odd_power", 3, sp.sin(X) ** 3, sp.cos(X) ** 3 / 3 - sp.cos(X)),
    ("trigonometric-v1", "even_power", 4, sp.sin(X) ** 2, X / 2 - sp.sin(2 * X) / 4),
    (
        "trigonometric-v1",
        "identity_substitution",
        5,
        (1 - sp.cos(2 * X)) * sp.cos(X) / 2,
        sp.sin(X) ** 3 / 3,
    ),
]
COEFFICIENTS = (-3, -2, -1, 1, 2, 3)


@pytest.mark.parametrize("case,coefficient", tuple(product(CASES, COEFFICIENTS)))
def test_complete_family_corpus(case, coefficient):
    version, name, level, integrand, primitive = case
    record = dict(generator_version=version, template=name, coefficient=coefficient)
    problem = replay_family(record)
    assert problem.difficulty == level
    assert not problem.template.is_definite
    assert sp.expand(problem.integrand - coefficient * integrand) == 0
    assert sp.expand(problem.antiderivative - coefficient * primitive) == 0
    assert continuous_domain(problem.integrand, X, sp.S.Reals) == problem.domain
    assert problem.domain.is_subset(continuous_domain(problem.antiderivative, X, sp.S.Reals))
    assert not problem.antiderivative.has(sp.Integral, sp.Subs)
    assert problem.antiderivative.free_symbols == {X}
    # All primitive values (not expression strings) survive actual JSON round trips.
    stored = json.loads(json.dumps(problem.parameters.model_dump(mode="json")))
    assert stored == record
    assert replay_family(stored) == problem
    assert problem.solution_steps[-1] == FamilyStep("constant", problem.antiderivative + C)
    assert problem.solution_steps[-1].latex == problem.answer_latex
    assert problem.answer_latex.endswith(" + C")
    assert all(step.say and step.latex for step in problem.solution_steps)
    for expression in (
        problem.integrand,
        problem.antiderivative,
        *(s.expression for s in problem.solution_steps),
    ):
        assert not expression.atoms(sp.Float)
        assert not expression.has(sp.zoo, sp.nan, sp.oo, -sp.oo)
        for number in expression.atoms(sp.Rational):
            assert abs(number.p) <= 18
            assert number.q <= 6
    public = problem.public().model_dump()
    assert set(public) == {"topic", "problem_latex"}
    assert "+ C" not in public["problem_latex"]
    assert "generator_version" not in public
    # Every answer fits the existing bounded grammar; no new learner syntax is needed.
    source = str(problem.antiderivative).replace("**", "^").replace("Abs", "abs") + " + C"
    constructed = _build_sympy(parse_math_input(source), evaluate=True)
    assert sp.simplify(constructed - problem.antiderivative - C) == 0


def test_exact_matrix_and_seeded_selection():
    before = random.getstate()
    expected = {(version, name, level) for version, name, level, _, _ in CASES}
    actual = {
        (version, name, template.difficulty)
        for version, (_, templates, _) in _families().items()
        for name, template in templates.items()
    }
    assert actual == expected
    for version, (topic, templates, _) in _families().items():
        for level in {t.difficulty for t in templates.values()}:
            problem = generate_family(topic=topic, difficulty=level, seed=17)
            assert problem == generate_family(topic=topic, difficulty=level, seed=17)
            assert problem.parameters.generator_version == version
            assert problem.difficulty == level
    assert random.getstate() == before


@pytest.mark.parametrize(
    "change",
    [
        {"generator_version": "substitution-v1"},
        {"generator_version": "rational-v9"},
        {"generator_version": None},
        {"template": "__import__('os')"},
        {"template": "sine"},
        {"template": 1},
        {"template": "x" * 33},
        {"coefficient": 0},
        {"coefficient": 4},
        {"coefficient": -4},
        {"coefficient": True},
        {"coefficient": "1"},
        {"coefficient": 1.0},
        {"coefficient": 10**100},
        {"coefficient": "x**(9**9)"},
        {"answer": "x"},
        {"domain": "positive"},
        {"difficulty": 1},
    ],
)
def test_bad_records_fail_before_symbolic_construction(change, monkeypatch):
    _families()  # Import fixed template metadata before instrumenting construction.

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid record reached symbolic construction")

    monkeypatch.setattr(sp, "Integer", forbidden)
    with pytest.raises(ValueError):
        replay_family(
            {
                "generator_version": "rational-v1",
                "template": "distinct_factors",
                "coefficient": 1,
                **change,
            }
        )


@pytest.mark.parametrize("missing", ["generator_version", "template", "coefficient"])
def test_all_replay_fields_are_required(missing):
    record = dict(generator_version="rational-v1", template="distinct_factors", coefficient=1)
    del record[missing]
    with pytest.raises(ValueError):
        replay_family(record)


@pytest.mark.parametrize(
    "change",
    [
        {"topic": "unknown"},
        {"topic": "integration-by-parts", "difficulty": 4},
        {"topic": "integration-by-parts", "difficulty": 5},
        {"difficulty": 0},
        {"difficulty": 6},
        {"difficulty": True},
        {"difficulty": "1"},
        {"difficulty": 1.0},
        {"seed": -1},
        {"seed": 2**32},
        {"seed": True},
        {"seed": 1.0},
    ],
)
def test_unsupported_cells_and_invalid_seeds_are_rejected(change):
    with pytest.raises(ValueError):
        generate_family(**{"topic": "substitution", "difficulty": 1, "seed": 0, **change})


def test_rational_domains_include_every_component_and_exclude_every_pole():
    for name in ("distinct_factors", "repeated_factor", "division_then_fractions"):
        problem = replay_family(dict(generator_version="rational-v1", template=name, coefficient=1))
        assert problem.domain == sp.S.Reals - sp.FiniteSet(-1, 0)
        for x in (-2, sp.Rational(-1, 2), 1):
            assert problem.domain.contains(x) is sp.true
        for pole in (-1, 0):
            assert problem.domain.contains(pole) is sp.false
            assert sp.limit(problem.integrand, X, pole) in (sp.oo, -sp.oo)
        assert problem.antiderivative.has(sp.log(sp.Abs(X)), sp.log(sp.Abs(X + 1)))


def test_structural_methods_are_retained_in_the_steps():
    expected = {
        ("substitution-v2", "factor_square"): [
            "factor",
            "substitution_integral",
            "substitute_back",
        ],
        ("substitution-v2", "identity_nested"): [
            "identity",
            "substitution_integral",
            "nested_substitution",
            "substitute_back",
        ],
        ("parts-v1", "quadratic_exponential"): ["parts", "repeat_parts"],
        ("parts-v1", "cyclic_sine"): ["parts", "repeat_parts", "solve_cycle"],
        ("rational-v1", "division_then_fractions"): ["polynomial_division", "partial_fractions"],
        ("trigonometric-v1", "identity_substitution"): ["identity", "substitution_integral"],
    }
    for (version, name), kinds in expected.items():
        problem = replay_family(dict(generator_version=version, template=name, coefficient=1))
        assert [step.kind for step in problem.solution_steps[:-2]] == kinds
        assert problem.template.auxiliary_transformations


def test_verifier_rejects_wrong_steps_missing_constant_and_wrong_domain():
    problem = replay_family(
        dict(generator_version="rational-v1", template="distinct_factors", coefficient=1)
    )
    for corrupted in (
        replace(problem, solution_steps=()),
        replace(problem, solution_steps=problem.solution_steps[:-1]),
        replace(problem, solution_steps=(FamilyStep("integrate", X), problem.solution_steps[-1])),
        replace(
            problem,
            solution_steps=(
                FamilyStep("integrate", sp.log(X) - sp.log(X + 1)),
                problem.solution_steps[-1],
            ),
        ),
        replace(problem, template=replace(problem.template, domain=sp.S.Reals)),
        replace(problem, antiderivative=sp.log(X)),
    ):
        with pytest.raises(RuntimeError):
            verify_family(corrupted)


def test_existing_preview_versions_are_unchanged_and_new_cells_are_offered():
    record = dict(
        generator_version="substitution-v1", family="sin", a=1, b=1, scale=1, difficulty=1
    )
    problem = replay_preview(record)
    assert problem.primitive == sp.sin(X**2 + 1)
    assert problem.integrand == 2 * X * sp.cos(X**2 + 1)
    from app.api.practice import TOPICS

    assert {topic: cell.levels for topic, cell in TOPICS.items()} == {
        "matrices": (1, 2, 3, 4, 5),
        "complex-numbers": (1, 2, 3, 4, 5),
        "fundamental-theorem-algebra": (1, 2, 3, 4, 5),
        "partial-fractions": (1, 2, 3, 4, 5),
        "combinations": (1,),
        "basic-integrals": (1, 2, 3, 4, 5),
        "substitution": (1, 2, 3, 4, 5),
        "integration-by-parts": (1, 2, 3),
        "rational-functions": (1, 2, 3, 4, 5),
        "trigonometric-integrals": (1, 2, 3, 4, 5),
        "definite-integrals": (1, 2, 3, 4, 5),
        "double-integrals": (1, 2, 3, 4, 5),
        "triple-integrals": (1, 2, 3, 4, 5),
        "derivatives": (1, 2, 3, 4, 5),
        "partial-derivatives": (1, 2, 3, 4, 5),
        "functions-and-sequences": (1, 2, 3, 4, 5),
        "limits-and-continuity": (1, 2, 3, 4, 5),
        "improper-integrals": (1, 2, 3, 4, 5),
        "series": (1, 2, 3, 4, 5),
        "multivariable-functions": (1, 2, 3, 4, 5),
        "differential-equations": (1, 2, 3, 4, 5),
    }
