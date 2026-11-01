"""#195: full derivative curriculum, exact variable metadata, archive and workers."""

import sys
from types import FrameType
from typing import Any

import pytest
from engine_fixtures import PUBLISHED_TOPICS

from app.api import practice
from app.engine import practice as engine
from app.engine.answers.expression import ExpressionAnswer
from app.engine.blocks.differentiation import partial
from app.engine.generators.differentiation import PartialDerivatives, SingleDerivatives
from app.math_input import parse_math_input
from app.services import archive
from app.services.math_worker import check_answer, record_variables

CASES = [(slug, level) for slug in ("derivatives", "partial-derivatives") for level in range(1, 6)]


def answer_text(record: dict[str, object]) -> str:
    return (
        str(engine.replay(record).answer.expected)
        .replace("**", "^")
        .replace("E", "e")
        .replace("Abs", "abs")
    )


@pytest.mark.parametrize("slug,level", CASES)
def test_each_derivative_cell_checks_with_its_exact_declared_variables(
    slug: str, level: int
) -> None:
    entry, old = engine.ENGINE_TOPICS[slug], PUBLISHED_TOPICS[slug]
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
