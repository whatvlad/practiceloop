import json
import random
from dataclasses import replace
from itertools import product
from typing import Any

import pytest
import sympy as sp
from sympy.calculus.util import continuous_domain

from app.generators.basic import (
    BASIC_TEMPLATES,
    C,
    SolutionStep,
    X,
    _verify,
    generate_basic,
    replay_basic,
)

# Independent acceptance table: all parameter combinations exposed by v1.
CASES = {
    "constant": (1, "real", (1,), (2,)),
    "power": (1, "real", (1,), (2, 3, 4)),
    "exponential": (1, "real", (1,), (2,)),
    "sine": (1, "real", (1,), (2,)),
    "cosine": (1, "real", (1,), (2,)),
    "sum": (2, "real", (1, 2), (2, 3, 4)),
    "negative_power": (3, "nonzero", (1,), (2, 3, 4)),
    "fractional_power": (3, "positive", (1,), (2,)),
    "reciprocal": (3, "nonzero", (1,), (2,)),
    "expand_square": (4, "real", (1, 2), (2,)),
    "expand_and_split": (5, "nonzero", (1, 2), (2,)),
}
RECORDS = [
    {
        "generator_version": "basic-v1",
        "template": name,
        "coefficient": coefficient,
        "secondary": secondary,
        "power": power,
    }
    for name, (_, _, secondaries, powers) in CASES.items()
    for coefficient, secondary, power in product(
        (1, 2, 3) if name == "expand_and_split" else (-3, -2, -1, 1, 2, 3),
        secondaries,
        powers,
    )
]


@pytest.mark.parametrize("record", RECORDS)
def test_complete_parameter_corpus(record: dict[str, Any]) -> None:
    problem = replay_basic(record)
    expected_level, expected_domain, _, _ = CASES[record["template"]]
    assert problem.difficulty == expected_level
    assert problem.template.domain == expected_domain
    assert not problem.template.is_definite
    assert problem.integrand.free_symbols == {X} or not problem.integrand.free_symbols
    assert problem.antiderivative.free_symbols == {X}
    assert not problem.integrand.atoms(sp.Float)
    assert not problem.antiderivative.atoms(sp.Float)
    assert continuous_domain(problem.integrand, X, sp.S.Reals) == problem.domain
    assert problem.domain.is_subset(continuous_domain(problem.antiderivative, X, sp.S.Reals))

    # Prove equality on each whole component, including negative x for log|x|.
    probes = (
        [sp.Symbol("u", real=True)]
        if expected_domain == "real"
        else [sp.Symbol("u", positive=True)]
    )
    if expected_domain == "nonzero":
        probes.append(sp.Symbol("v", negative=True))
    for probe in probes:
        derivative = sp.diff(problem.antiderivative, X).subs(X, probe)
        displayed = problem.integrand.subs(X, probe)
        assert sp.simplify(derivative - displayed) == 0
        for step in problem.solution_steps:
            expression = step.expression
            if step.kind in {"integrate", "constant"}:
                expression = sp.diff(expression, X)
            assert sp.simplify((expression - problem.integrand).subs(X, probe)) == 0
            assert step.say and step.latex

    assert problem.solution_steps[-1].kind == "constant"
    for step in problem.solution_steps:
        assert problem.domain.is_subset(continuous_domain(step.expression, X, sp.S.Reals))
    assert problem.solution_steps[-1].expression == problem.antiderivative + C
    assert problem.solution_steps[-1].latex == problem.answer_latex
    assert problem.answer_latex.endswith(" + C")
    assert problem.answer_latex.count(" + C") == 1

    # Parameter JSON, not expression strings or a PRNG state, is the replay contract.
    stored = json.loads(json.dumps(problem.parameters.model_dump(mode="json")))
    assert stored == record
    assert all(
        type(value) is int
        for key, value in stored.items()
        if key not in {"template", "generator_version"}
    )
    assert replay_basic(stored) == problem

    public = problem.public().model_dump()
    assert set(public) == {"topic", "problem_latex"}
    assert public["topic"] == "basic-integrals"
    assert public["problem_latex"].startswith(r"\int")
    assert "+ C" not in public["problem_latex"]
    assert "generator_version" not in public and "solution_steps" not in public


def test_catalogue_covers_the_five_approved_levels() -> None:
    assert {item.name for item in BASIC_TEMPLATES} == set(CASES)
    assert {item.difficulty for item in BASIC_TEMPLATES} == set(range(1, 6))


@pytest.mark.parametrize(
    ("template", "integrand", "primitive"),
    [
        ("constant", sp.Integer(2), 2 * X),
        ("power", 2 * X, X**2),
        ("exponential", 2 * sp.exp(X), 2 * sp.exp(X)),
        ("sine", 2 * sp.sin(X), -2 * sp.cos(X)),
        ("cosine", 2 * sp.cos(X), 2 * sp.sin(X)),
        ("sum", 2 * X + sp.exp(X), X**2 + sp.exp(X)),
        ("negative_power", 2 / X**2, -2 / X),
        ("fractional_power", 2 / sp.sqrt(X), 4 * sp.sqrt(X)),
        ("reciprocal", 2 / X, 2 * sp.log(sp.Abs(X))),
        ("expand_square", 2 * (X + 1) ** 2, 2 * X**3 / 3 + 2 * X**2 + 2 * X),
        (
            "expand_and_split",
            2 * (X + 1) ** 2 + (X + 1) / X,
            2 * X**3 / 3 + 2 * X**2 + 3 * X + sp.log(sp.Abs(X)),
        ),
    ],
)
def test_v1_known_records_keep_their_mathematical_content(
    template: str, integrand: Any, primitive: Any
) -> None:
    problem = replay_basic(
        {
            "generator_version": "basic-v1",
            "template": template,
            "coefficient": 2,
            "secondary": 1,
            "power": 2,
        }
    )
    assert sp.expand(problem.integrand) == sp.expand(integrand)
    assert sp.expand(problem.antiderivative) == sp.expand(primitive)


@pytest.mark.parametrize("difficulty", range(1, 6))
@pytest.mark.parametrize("seed", [0, 1, 17, 2**32 - 1])
def test_seeded_selection_and_replay(difficulty: int, seed: int) -> None:
    before = random.getstate()
    problem = generate_basic(difficulty=difficulty, seed=seed)
    assert problem.difficulty == difficulty
    assert generate_basic(difficulty=difficulty, seed=seed) == problem
    assert random.getstate() == before


@pytest.mark.parametrize("level", [0, 6, -1, True, 1.0, "1", None])
def test_rejects_invalid_difficulty(level: Any) -> None:
    with pytest.raises(ValueError):
        generate_basic(difficulty=level, seed=0)


@pytest.mark.parametrize("seed", [-1, 2**32, True, 1.0, "1", None])
def test_rejects_invalid_seed(seed: Any) -> None:
    with pytest.raises(ValueError):
        generate_basic(difficulty=1, seed=seed)


@pytest.mark.parametrize(
    "change",
    [
        {"generator_version": "basic-v2"},
        {"generator_version": None},
        {"template": "__import__('os')"},
        {"template": "unknown"},
        {"coefficient": 0},
        {"coefficient": 4},
        {"coefficient": -4},
        {"coefficient": True},
        {"coefficient": 1.0},
        {"coefficient": "1"},
        {"coefficient": "x**(9**9)"},
        {"secondary": 0},
        {"secondary": 3},
        {"secondary": False},
        {"power": 1},
        {"power": 5},
        {"power": 10**100},
        {"power": True},
        {"integrand": "sin(x)"},
        {"antiderivative": "x"},
        {"difficulty": 5},
        {"template": "constant", "power": 3},
        {"template": "constant", "secondary": 2},
        {"template": "expand_and_split", "coefficient": -1},
    ],
)
def test_rejects_bad_records_before_symbolic_construction(
    change: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> None:
        pytest.fail("Invalid parameters reached symbolic construction")

    monkeypatch.setattr(sp, "Integer", forbidden)
    with pytest.raises(ValueError):
        replay_basic({**RECORDS[0], **change})


def test_version_and_template_are_required() -> None:
    with pytest.raises(ValueError):
        replay_basic({"template": "constant", "coefficient": 1})
    with pytest.raises(ValueError):
        replay_basic({"generator_version": "basic-v1", "coefficient": 1})


def test_higher_levels_retain_both_intended_rewrites() -> None:
    for record in RECORDS:
        if record["template"] not in {"expand_square", "expand_and_split"}:
            continue
        problem = replay_basic(record)
        square = record["coefficient"] * (X + record["secondary"]) ** 2
        rewrites = [step.kind for step in problem.solution_steps[:-2]]
        if problem.difficulty == 4:
            assert problem.integrand == square
            assert rewrites == ["expand"]
        else:
            assert square in problem.integrand.args
            assert rewrites == ["expand", "split_fraction"]
            assert sp.limit(X * problem.integrand, X, 0) != 0
            assert problem.domain.contains(0) is sp.false
            assert r"x\ne0" in problem.public().problem_latex
        assert tuple(rewrites) == problem.template.auxiliary_transformations


def test_candidate_with_incorrect_step_is_rejected() -> None:
    problem = generate_basic(difficulty=5, seed=0)
    corrupted = replace(
        problem, solution_steps=(SolutionStep("integrate", X), problem.solution_steps[-1])
    )
    with pytest.raises(RuntimeError, match="symbolic verification"):
        _verify(corrupted)


def test_missing_constant_or_inconsistent_final_answer_is_rejected() -> None:
    problem = generate_basic(difficulty=3, seed=0)
    for corrupted in (
        replace(problem, solution_steps=()),
        replace(problem, solution_steps=problem.solution_steps[:-1]),
        replace(problem, antiderivative=problem.antiderivative + 1),
    ):
        with pytest.raises(RuntimeError, match="arbitrary constant"):
            _verify(corrupted)


def test_numeric_coefficients_stay_pedagogically_small() -> None:
    for record in RECORDS:
        problem = replay_basic(record)
        for expression in (sp.expand(problem.integrand), sp.expand(problem.antiderivative)):
            for number in expression.atoms(sp.Rational):
                assert abs(number.p) <= 15
                assert number.q <= 4
