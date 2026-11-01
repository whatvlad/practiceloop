"""#194: exact multiple integrals, retained geometry, codes, archive and workers."""

import sys

import pytest
from engine_fixtures import PUBLISHED_TOPICS

from app.api import practice
from app.engine import practice as engine
from app.engine.blocks.multiple.form import MultipleForm
from app.engine.generators.multiple import DoubleIntegrals, TripleIntegrals
from app.math_input import parse_math_input
from app.services import archive
from app.services.math_worker import check_answer
from app.visuals.spec import build_visual

CASES = [
    (slug, level) for slug in ("double-integrals", "triple-integrals") for level in range(1, 6)
]


def answer_text(record: dict[str, object]) -> str:
    return str(engine.replay(record).answer.expected).replace("**", "^").replace("E", "e")


@pytest.mark.parametrize("slug,level", CASES)
def test_every_multiple_cell_checks_and_keeps_its_visual_and_worksheet(
    slug: str, level: int
) -> None:
    entry = engine.ENGINE_TOPICS[slug]
    old = PUBLISHED_TOPICS[slug]
    assert (tuple(entry.levels), entry.mixed_weight, entry.space_cm) == (
        old.levels,
        old.mixed_weight,
        old.space_cm,
    )
    issued = engine.issue(slug, level, seed=194)
    assert archive.is_archived(slug, {"generator_version": "legacy"})
    assert not archive.is_archived(slug, issued.record)
    answer = answer_text(issued.record)
    assert engine.check(issued.record, parse_math_input(answer)) == "correct"
    assert engine.check(issued.record, parse_math_input(f"({answer}) + 1")) == "incorrect"
    assert engine.check(issued.record, parse_math_input(f"({answer}) + C")) != "correct"
    visual = build_visual(issued.record)
    assert visual and visual["kind"] == entry.visual
    assert practice.capacity(slug, level) == 64
    assert slug in practice.mixed_topics("mathematical-analysis", level, worksheet=True)[0]


@pytest.mark.parametrize(
    "generator", [DoubleIntegrals(), TripleIntegrals()], ids=lambda g: g.version
)
def test_typed_multiple_parameters_replay_and_reject_wrong_dimensions(
    generator: DoubleIntegrals,
) -> None:
    params = generator.draw(194)
    assert generator.build(
        generator.params.model_validate_json(params.model_dump_json())
    ) == generator.build(params)
    wrong = TripleIntegrals().draw(194) if generator.dimension == 2 else DoubleIntegrals().draw(194)
    with pytest.raises(ValueError, match="dimension"):
        generator.build(wrong)


@pytest.mark.parametrize("dimension", [2, 3])
def test_invalid_multiple_variants_are_refused_before_symbolic_work(dimension: int) -> None:
    for template, index, coefficient in [
        ("unknown", 0, 1),
        ("box_product", 9, 1),
        ("rectangle_product", 0, 0),
    ]:
        with pytest.raises(ValueError):
            MultipleForm(
                dimension=dimension, template=template, variant=index, coefficient=coefficient
            )


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize("slug,level", CASES)
def test_every_multiple_level_checks_inside_the_limited_worker(slug: str, level: int) -> None:
    issued = engine.issue(slug, level, seed=194)
    assert check_answer(answer_text(issued.record), issued.record).result == "correct"
