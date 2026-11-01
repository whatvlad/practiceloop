"""#193: integral curriculum, native answer kinds, pools, archive and worker checks."""

import sys
from itertools import product

import pytest
import sympy as sp
from engine_fixtures import PUBLISHED_TOPICS

from app.api import practice
from app.engine import practice as engine
from app.engine.answers._symbolic import X, components
from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.engine.blocks.integral_forms.form import BOUNDS, METHODS, IntegralForm
from app.engine.generators.integrals import IntegralGenerator, integral_generators
from app.math_input import parse_math_input
from app.services import archive
from app.services.math_worker import check_answer
from app.visuals.spec import build_visual

MIGRATED = {
    "basic-integrals": (1, 2, 3, 4, 5),
    "substitution": (1, 2, 3, 4, 5),
    "integration-by-parts": (1, 2, 3),
    "rational-functions": (1, 2, 3, 4, 5),
    "trigonometric-integrals": (1, 2, 3, 4, 5),
    "definite-integrals": (1, 2, 3, 4, 5),
}


def answer_text(record: dict[str, object]) -> str:
    answer = engine.replay(record).answer
    value = answer.primitive if isinstance(answer, AntiderivativeAnswer) else answer.expected
    return str(value).replace("**", "^").replace("Abs", "abs").replace("E", "e") + (
        " + C" if isinstance(answer, AntiderivativeAnswer) else ""
    )


def test_migrated_topics_keep_levels_weights_worksheet_space_and_archive_legacy() -> None:
    for slug, levels in MIGRATED.items():
        entry = engine.ENGINE_TOPICS[slug]
        old = PUBLISHED_TOPICS[slug]
        assert tuple(entry.levels) == old.levels == levels
        assert (entry.mixed_weight, entry.space_cm) == (old.mixed_weight, old.space_cm)
        assert archive.is_archived(slug, {"generator_version": "legacy"})
        assert not archive.is_archived(slug, engine.issue(slug, levels[0], seed=0).record)
        for level in levels:
            assert practice.capacity(slug, level) == 64


@pytest.mark.parametrize("generator", integral_generators(), ids=lambda g: g.version)
def test_forms_have_exact_primitives_and_valid_bounds(generator: IntegralGenerator) -> None:
    family = generator.form_family
    for name in METHODS[family].TEMPLATES:
        if generator.bounded and (family, name) not in BOUNDS:
            continue
        coefficients = (1, 2, 3) if name == "expand_and_split" else (-3, -2, -1, 1, 2, 3)
        for coefficient in coefficients:
            form = IntegralForm(family=family, template=name, coefficient=coefficient)
            data = form.evaluate(generator.bounded)
            for replacement, variable, _ in components(data.domain):
                derivative = sp.diff(data.primitive.subs(X, replacement), variable)
                derivative /= sp.diff(replacement, variable)
                assert (
                    sp.simplify(sp.trigsimp(derivative - data.integrand.subs(X, replacement))) == 0
                )
            if generator.bounded:
                assert sp.Interval(data.lower, data.upper).is_subset(data.domain)
                assert (
                    sp.simplify(
                        data.value
                        - data.primitive.subs(X, data.upper)
                        + data.primitive.subs(X, data.lower)
                    )
                    == 0
                )
                assert data.value.is_real and data.value.is_finite


@pytest.mark.parametrize(
    "slug,level", [(s, level) for s, levels in MIGRATED.items() for level in levels]
)
def test_each_cell_checks_its_own_answer_and_builds_the_existing_visual(
    slug: str, level: int
) -> None:
    issued = engine.issue(slug, level, seed=193)
    assert engine.check(issued.record, parse_math_input(answer_text(issued.record))) == "correct"
    spec = build_visual(issued.record)
    assert spec is not None and spec["kind"] in {"indefinite", "definite"}
    if slug == "definite-integrals":
        assert spec["kind"] == "definite"


@pytest.mark.parametrize("family", ["basic", "substitution", "parts", "rational", "trigonometric"])
def test_native_indefinite_answers_keep_the_constant_policy(family: str) -> None:
    generator = next(g for g in integral_generators() if g.form_family == family and not g.bounded)
    task = generator.build(generator.draw(193))
    record = {"generator_version": task.generator_version, "code": task.code}
    text = answer_text(record)
    assert task.answer.check(parse_math_input(text)) == "correct"
    assert task.answer.check(parse_math_input(text.removesuffix(" + C"))) == "missing_constant"
    assert task.answer.check(parse_math_input(text + " + x")) == "incorrect"


def test_recent_records_are_excluded_without_rebuilding_a_task() -> None:
    pool = engine.pool("basic-integrals", 1)
    recent = tuple(problem.issued().record for problem in pool[:32])
    for seed in range(64):
        assert engine.issue("basic-integrals", 1, seed=seed, recent=recent).record not in recent


@pytest.mark.parametrize("family,template", list(product(["basic", "substitution"], ["unknown"])))
def test_malformed_parameters_are_refused(family: str, template: str) -> None:
    with pytest.raises(ValueError):
        IntegralForm(family=family, template=template, coefficient=1)


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize(
    "slug,level", [(s, level) for s, levels in MIGRATED.items() for level in levels]
)
def test_each_migrated_cell_checks_inside_the_limited_worker(slug: str, level: int) -> None:
    issued = engine.issue(slug, level, seed=193)
    assert check_answer(answer_text(issued.record), issued.record).result == "correct"
