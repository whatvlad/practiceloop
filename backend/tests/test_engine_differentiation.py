"""#195: full derivative curriculum, exact variable metadata, archive and workers."""

import sys
from types import FrameType
from typing import Any

import pytest
import sympy as sp

from app.api import practice
from app.engine import practice as engine
from app.engine.answers.expression import ExpressionAnswer
from app.engine.blocks.differentiation import partial, single
from app.engine.generators.differentiation import PartialDerivatives, SingleDerivatives
from app.generators import derivatives as old_single
from app.generators import partial as old_partial
from app.services import archive
from app.services.math_parser import parse_math_input
from app.services.math_worker import check_answer, record_variables

CASES = [(slug, level) for slug in ("derivatives", "partial-derivatives") for level in range(1, 6)]


def answer_text(record: dict[str, object]) -> str:
    return (
        str(engine.replay(record).answer.expected)
        .replace("**", "^")
        .replace("E", "e")
        .replace("Abs", "abs")
    )


def test_all_single_rules_steps_domains_and_levels_are_retained() -> None:
    assert single.TEMPLATES.keys() == old_single.TEMPLATES.keys()
    for name, template in single.TEMPLATES.items():
        assert (template.difficulty, template.domain, template.rules) == (
            old_single.TEMPLATES[name].difficulty,
            old_single.TEMPLATES[name].domain,
            old_single.TEMPLATES[name].rules,
        )
        for coefficient in (-3, -2, -1, 1, 2, 3):
            data = single.DerivativeForm(template=name, coefficient=coefficient).evaluate()
            previous = old_single.replay_derivative(
                {
                    "generator_version": "derivatives-v1",
                    "template": name,
                    "coefficient": coefficient,
                }
            )
            assert data.function == previous.function
            assert sp.simplify(data.derivative - previous.derivative) == 0
            assert [s.latex for s in data.solution_steps] == [
                s.latex for s in previous.solution_steps
            ]


def test_all_partial_templates_variables_domains_and_proofs_are_retained() -> None:
    assert partial.TEMPLATES.keys() == old_partial.TEMPLATES.keys()
    for name, template in partial.TEMPLATES.items():
        previous = old_partial.TEMPLATES[name]
        assert (template.difficulty, template.kind, template.coefficients) == (
            previous.difficulty,
            previous.kind,
            previous.coefficients,
        )
        assert partial.VARIABLES[name] == old_partial.declared(previous)
        for coefficient in template.coefficients:
            data = partial.PartialForm(template=name, coefficient=coefficient).evaluate()
            old = old_partial.replay_partial(
                {
                    "generator_version": "partial-v1",
                    "template": name,
                    "coefficient": coefficient,
                    "variables": old_partial.declared(previous),
                }
            )
            assert data.statement == old.statement
            assert sp.simplify(data.answer - old.answer) == 0
            assert [s.latex for s in data.steps] == [s.latex for s in old.solution_steps]


@pytest.mark.parametrize("slug,level", CASES)
def test_each_derivative_cell_checks_with_its_exact_declared_variables(
    slug: str, level: int
) -> None:
    entry, old = engine.ENGINE_TOPICS[slug], practice._LEGACY_TOPICS[slug]
    assert (tuple(entry.levels), entry.mixed_weight, entry.space_cm) == (
        old.levels,
        old.mixed_weight,
        old.space_cm,
    )
    issued = engine.issue(slug, level, seed=195)
    variables = record_variables(issued.record)
    assert set(issued.record) == {"generator_version", "code"}
    assert (
        engine.check(issued.record, parse_math_input(answer_text(issued.record), variables))
        == "correct"
    )
    assert (
        engine.check(
            issued.record, parse_math_input(f"({answer_text(issued.record)}) + 1", variables)
        )
        == "incorrect"
    )
    assert archive.is_archived(slug, {"generator_version": "legacy"})
    assert not archive.is_archived(slug, issued.record)
    assert practice.capacity(slug, level) == 64
    assert slug in practice.mixed_topics("derivatives", level, worksheet=True)[0]


def test_code_derived_variable_metadata_calls_no_sympy_and_returns_fresh_mappings() -> None:
    records = [engine.issue("partial-derivatives", level, seed=195).record for level in range(1, 6)]
    calls = []

    def profile(frame: FrameType, event: str, _arg: Any) -> None:
        if event == "call" and frame.f_globals.get("__name__", "").startswith("sympy"):
            calls.append(frame.f_code.co_name)

    previous = sys.getprofile()
    engine._registry.cache_clear()
    sys.setprofile(profile)
    try:
        mappings = [record_variables(record) for record in records]
    finally:
        sys.setprofile(previous)
    assert not calls and all(mappings)
    for record, mapping in zip(records, mappings, strict=True):
        original = dict(mapping)
        mapping.clear()
        assert record_variables(record) == original


def test_partial_positive_domain_and_theta_grammar_are_unchanged() -> None:
    form = partial.PartialForm(template="logarithm_factor", coefficient=1)
    data = form.evaluate()
    answer = ExpressionAnswer(data.answer, data.variables)
    assert data.variables == {"x": "real", "y": "positive"}
    assert answer.check(parse_math_input("ln(y^2)/2", data.variables)) == "correct"
    record = engine.issue("partial-derivatives", 4, seed=195).record
    variables = record_variables(record)
    assert variables["r"] == "positive" and variables["theta"] == "real"
    assert (
        engine.check(
            record, parse_math_input(answer_text(record).replace("theta", "\u03b8"), variables)
        )
        == "correct"
    )


@pytest.mark.parametrize(
    "generator", [SingleDerivatives(), PartialDerivatives()], ids=lambda g: g.version
)
def test_derivative_drawn_parameters_replay_through_json(generator: Any) -> None:
    params = generator.draw(195)
    assert generator.build(
        generator.params.model_validate_json(params.model_dump_json())
    ) == generator.build(params)


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize("slug,level", CASES)
def test_every_derivative_level_checks_in_the_limited_worker(slug: str, level: int) -> None:
    record = engine.issue(slug, level, seed=195).record
    assert check_answer(answer_text(record), record).result == "correct"
