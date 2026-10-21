"""#101: partial-v1 over its complete corpus, checked as ADR-005 requires."""

import json
import time
from dataclasses import replace

import pytest
import sympy as sp
from pydantic import ValidationError

from app.generators import partial
from app.generators.core import catalogue, replay
from app.generators.partial import TEMPLATES, VERSION, records, replay_partial
from app.services import partial_check

CORPUS = [record for level in range(1, 6) for record in records(level)]
x, y, z, r, theta, C = sp.symbols("x y z r theta C", real=True)


def record(template: str, coefficient: int = 1) -> dict[str, object]:
    return {"generator_version": VERSION, "template": template, "coefficient": coefficient}


def test_every_level_offers_at_least_two_templates() -> None:
    for level in range(1, 6):
        names = {t for t, template in TEMPLATES.items() if template.difficulty == level}
        assert len(names) >= 2, level
        assert len(records(level)) == sum(len(TEMPLATES[n].coefficients) for n in names)


@pytest.mark.parametrize(
    "item", CORPUS, ids=lambda item: f"{item['template']}{item['coefficient']}"
)
def test_every_record_is_proven_and_replays_deterministically(item: dict[str, object]) -> None:
    problem = replay_partial(item)
    again = replay_partial(json.loads(json.dumps(item)), verify=False)
    assert (problem.statement, problem.answer_latex) == (again.statement, again.answer_latex)
    assert problem.solution_steps == again.solution_steps
    assert problem.answer.free_symbols <= set(problem.variables)
    assert problem.answer.is_real is True
    assert problem.answer_latex in problem.solution_steps[-1].latex
    for step in problem.solution_steps:
        assert step.say and step.latex
    if problem.template.kind in {"first", "second"}:
        # The worked solution names the variables held constant.
        assert r"\text{constant}" in problem.solution_steps[0].latex
    if problem.template.kind == "chain":
        kinds = [step.kind for step in problem.solution_steps]
        assert kinds == [
            "coordinate_substitute",
            "chain_partials",
            "chain_rule_sum",
            "simplify_result",
        ]


def test_declared_variables_and_domains() -> None:
    names = lambda name: tuple(v.name for v in TEMPLATES[name].variables)  # noqa: E731
    assert names("polynomial_x") == ("x", "y")
    assert names("three_variables") == ("x", "y", "z")
    assert names("polar_angle") == ("r", "theta")
    assert names("cylindrical_radius") == ("r", "theta", "z")
    assert partial.R.is_positive and partial.Y_POSITIVE.is_positive
    assert partial.THETA.is_real and partial.THETA.is_positive is None
    assert r"r > 0" in replay_partial(record("polar_angle")).statement
    assert r"y > 0" in replay_partial(record("logarithm_factor")).statement


def test_mixed_partials_are_proven_equal_for_smooth_templates() -> None:
    for name, template in TEMPLATES.items():
        built = partial._build(name, template.coefficients[0])
        if template.kind == "second" and "mixed" in name:
            assert built.mixed is not None
            assert sp.simplify(built.mixed[0] - built.mixed[1]) == 0
    # The learner may compute either order; both are the same expression.
    problem = replay_partial(record("mixed_exponential"))
    other_order = sp.diff(x**2 * sp.exp(x * y), x, y)
    assert partial_check.classify(other_order, problem) == "correct"


@pytest.mark.parametrize(
    "bad",
    [
        {},
        {**record("polynomial_x"), "extra": 1},
        {**record("polynomial_x"), "generator_version": "partial-v2"},
        {**record("polynomial_x"), "coefficient": 0},
        {**record("polynomial_x"), "coefficient": 4},
        {**record("polynomial_x"), "coefficient": True},
        {**record("polynomial_x"), "coefficient": "1"},
        {**record("polynomial_x"), "coefficient": 1.0},
        {**record("polynomial_x"), "template": "unknown"},
        {**record("polynomial_x"), "template": "x" * 33},
        record("scaled_polar", -1),
        {"generator_version": VERSION, "template": "polynomial_x"},
    ],
)
def test_malformed_records_are_rejected_before_symbolic_construction(
    bad: dict[str, object], monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*_args: object) -> None:
        pytest.fail("symbolic construction started for a malformed record")

    monkeypatch.setattr(partial, "_build", forbidden)
    with pytest.raises((ValidationError, ValueError)):
        replay_partial(bad)


@pytest.mark.parametrize(
    ("template", "coefficient", "answer", "expected"),
    [
        ("polynomial_x", 2, 6 * x**2 * y, "correct"),
        ("polynomial_x", 2, 3 * x**2 * y * 2, "correct"),
        ("polynomial_x", 2, 6 * x**2 * y + C, "invalid"),
        ("polynomial_x", 2, 6 * x**2 * z, "invalid"),
        ("polynomial_x", 2, 6 * x**2, "incorrect"),
        ("exponential_product", -1, -x * sp.exp(x * y), "correct"),
        ("logarithm_factor", 3, sp.log(y**3), "correct"),
        ("logarithm_factor", 3, 3 * sp.log(sp.Abs(y)), "correct"),
        ("sine_inner", 1, y**2 * sp.cos(y**2 * x), "correct"),
        ("mixed_exponential", 1, x**3 * y * sp.exp(x * y) + 3 * x**2 * sp.exp(x * y), "correct"),
        ("three_variables", 1, 3 * x * y**2 * z**2, "correct"),
        # ADR-005: an answer in r, θ is asked; the same function in x, y is invalid.
        ("polar_angle", 1, r**2 * (sp.cos(theta) ** 2 - sp.sin(theta) ** 2), "correct"),
        ("polar_angle", 1, r**2 * (1 - 2 * sp.sin(theta) ** 2), "correct"),
        ("polar_angle", 1, x**2 - y**2, "invalid"),
        ("polar_angle", 1, r**2 * sp.sin(2 * theta), "incorrect"),
        ("polar_radius", 1, 3 * r**2 * sp.sin(theta) - 3 * r**2 * sp.sin(theta) ** 3, "correct"),
        ("cylindrical_angle", 2, 2 * r * z * sp.cos(theta) - 2 * r * z * sp.sin(theta), "correct"),
        ("cylindrical_radius", 1, 2 * r * z * sp.sin(theta) * sp.cos(theta), "correct"),
        ("scaled_polar", 2, 6 * r, "correct"),
        ("scaled_polar", 2, 6 * sp.Abs(r), "correct"),
        ("scaled_polar", 2, 6 * sp.sqrt(r**2), "correct"),
        ("scaled_polar", 2, -6 * r, "incorrect"),
        ("scaled_cylindrical", 3, 9 * r, "correct"),
    ],
)
def test_equivalent_forms_in_the_declared_variables(
    template, coefficient, answer, expected
) -> None:
    problem = replay_partial(record(template, coefficient))
    assert partial_check.classify(answer, problem) == expected


@pytest.mark.parametrize(
    "item", CORPUS, ids=lambda item: f"{item['template']}{item['coefficient']}"
)
def test_each_declared_mistake_is_diagnosed_and_nothing_else(item: dict[str, object]) -> None:
    problem = replay_partial(item)
    codes = {code for code, _ in problem.mistakes}
    assert codes, "every template declares at least one mistake"
    for code, wrong in problem.mistakes:
        assert partial_check.classify(wrong, problem) == "incorrect"
        assert partial_check.diagnose(wrong, problem) == code
    assert partial_check.diagnose(problem.answer, problem) is None
    assert partial_check.diagnose(problem.answer + 1, problem) is None


def test_ambiguous_matches_get_no_diagnosis() -> None:
    twice = (("jacobian_missing_r", sp.Integer(2)), ("jacobian_sign", sp.Integer(2)))
    problem = replace(replay_partial(record("scaled_polar", 1)), mistakes=twice)
    assert partial_check.diagnose(sp.Integer(2), problem) is None


def test_chain_mistakes_follow_the_shown_terms() -> None:
    problem = replay_partial(record("polar_angle", 2))
    assert partial_check.diagnose(2 * r**2 * sp.cos(theta) ** 2, problem) == "partial_chain_term"
    assert partial_check.diagnose(-2 * r**2 * sp.sin(theta) ** 2, problem) == "partial_chain_term"


def _alternatives(problem: partial.PartialProblem) -> list[sp.Expr]:
    expanded = sp.expand(sp.expand_trig(problem.answer))
    return [problem.answer, expanded, sp.factor(expanded)]


@pytest.mark.parametrize("name", list(TEMPLATES))
def test_checks_fit_half_the_worker_cpu_limit(name: str) -> None:
    """ADR-005 budget: replay plus check of each form in at most 1 s of CPU."""
    item = record(name, TEMPLATES[name].coefficients[-1])
    for answer in _alternatives(replay_partial(item)):
        partial._build.cache_clear()
        start = time.process_time()
        problem = replay_partial(item, verify=False)
        outcome = partial_check.classify(answer, problem)
        assert time.process_time() - start < 1.0
        assert outcome == "correct"


def test_catalogue_offers_every_level_without_definite_variants() -> None:
    for level in range(1, 6):
        cell = catalogue(partial.TOPIC, level)
        assert [e.record for e in cell] == records(level)
        assert all(e.topic == partial.TOPIC and e.difficulty == level for e in cell)
        assert all("+ C" not in e.answer for e in cell)
    exercise = replay(record("polar_angle", 1))
    assert exercise.answer == r"r^{2} \cos{\left(2 \theta \right)}"
