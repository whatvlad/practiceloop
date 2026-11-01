"""#196: Algebra curriculum, grammar, archive and bounded-worker migration."""

import sys
from typing import Any

import pytest
import sympy as sp
from pydantic import ValidationError

from app.api import practice
from app.engine import practice as engine
from app.engine.blocks.algebra import AlgebraForm
from app.engine.generators.algebra import AlgebraParams, algebra_generators
from app.generators.symbolic import replay_symbolic
from app.services import archive
from app.services.math_parser import MathInputError, parse_math_input
from app.services.math_worker import check_answer, record_variables

KINDS = {
    "matrices": "determinant",
    "complex-numbers": "modulus",
    "fundamental-theorem-algebra": "root-sum",
    "partial-fractions": "decompose",
}
CASES = [(slug, level) for slug in KINDS for level in range(1, 6)]


def answer_text(record: dict[str, object]) -> str:
    return sp.sstr(engine.replay(record).answer.expected).replace("**", "^")


@pytest.mark.parametrize("slug,kind", KINDS.items())
def test_every_existing_formula_and_coefficient_is_preserved(slug: str, kind: str) -> None:
    for a in range(1, 6):
        for b in range(1, 6):
            form = AlgebraForm(kind=kind, a=a, b=b)
            native = form.evaluate()
            old = replay_symbolic(
                dict(
                    generator_version="symbolic-v1",
                    topic=slug,
                    template=kind,
                    difficulty=1,
                    a=a,
                    b=b,
                )
            )
            assert native.statement == old.statement
            assert sp.simplify(native.expected - old.expected) == 0
            assert [step.latex for step in native.steps] == [step["latex"] for step in old.steps]


@pytest.mark.parametrize("slug,level", CASES)
def test_all_algebra_levels_preserve_public_contracts_and_check_answers(
    slug: str, level: int
) -> None:
    entry, old = engine.ENGINE_TOPICS[slug], practice._LEGACY_TOPICS[slug]
    assert (tuple(entry.levels), entry.mixed_weight, entry.space_cm) == (
        old.levels,
        old.mixed_weight,
        old.space_cm,
    )
    issued = engine.issue(slug, level, seed=196)
    assert set(issued.record) == {"generator_version", "code"}
    variables = record_variables(issued.record)
    text = answer_text(issued.record)
    assert engine.check(issued.record, parse_math_input(text, variables)) == "correct"
    assert engine.check(issued.record, parse_math_input(f"({text})+1", variables)) == "incorrect"
    assert archive.is_archived(slug, {"generator_version": "symbolic-v1"})
    assert not archive.is_archived(slug, issued.record)
    assert practice.capacity(slug, level) == 64
    assert slug in practice.mixed_topics("algebra", level, worksheet=True)[0]


def test_partial_fraction_grammar_declares_only_x_and_checks_equivalent_rational_form() -> None:
    record = engine.issue("partial-fractions", 3, seed=196).record
    assert record_variables(record) == {"x": "real"}
    expected = engine.replay(record).answer.expected
    assert (
        engine.check(record, parse_math_input(sp.sstr(sp.together(expected)), {"x"})) == "correct"
    )
    with pytest.raises(MathInputError):
        parse_math_input("x+y", record_variables(record))


@pytest.mark.parametrize("generator", algebra_generators(), ids=lambda g: g.version)
def test_drawn_algebra_parameters_survive_json_and_reject_cross_family(generator: Any) -> None:
    params = generator.draw(196)
    assert generator.build(
        AlgebraParams.model_validate_json(params.model_dump_json())
    ) == generator.build(params)
    other = next(g for g in algebra_generators() if g.form_kind != generator.form_kind)
    with pytest.raises(ValueError, match="different generator"):
        generator.build(other.draw(196))


@pytest.mark.parametrize("change", [{"kind": "unknown"}, {"a": 0}, {"b": 6}, {"a": True}])
def test_invalid_algebra_forms_are_rejected(change: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        AlgebraForm.model_validate({"kind": "determinant", "a": 1, "b": 1, **change})


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize("slug,level", CASES)
def test_all_algebra_levels_check_in_limited_worker(slug: str, level: int) -> None:
    record = engine.issue(slug, level, seed=196).record
    assert check_answer(answer_text(record), record).result == "correct"
