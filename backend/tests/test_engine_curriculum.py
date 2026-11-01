"""Frozen migration corpus: every template and parameter survives legacy removal."""

import pytest
import sympy as sp
from engine_fixtures import CURRICULUM, PUBLISHED_TOPICS

from app.api import practice
from app.engine.blocks.algebra import AlgebraForm
from app.engine.blocks.analysis import AnalysisForm
from app.engine.blocks.differentiation.partial import PartialForm
from app.engine.blocks.differentiation.single import DerivativeForm
from app.engine.blocks.integral_forms.form import IntegralForm
from app.engine.blocks.multiple import double, triple
from app.engine.blocks.multiple.form import MultipleForm
from app.engine.blocks.multiple.setup import Setup, integrate_setup


def test_published_topic_order_levels_weights_and_worksheet_space_are_unchanged() -> None:
    assert list(practice.TOPICS) == list(PUBLISHED_TOPICS)
    for slug, expected in PUBLISHED_TOPICS.items():
        actual = practice.TOPICS[slug]
        assert tuple(actual) == (
            expected.name,
            expected.area,
            expected.levels,
            expected.mixed_weight,
            expected.space_cm,
        )


@pytest.mark.parametrize("row", CURRICULUM["integrals"])
def test_integral_curriculum_snapshot(row: dict) -> None:
    form = IntegralForm.model_validate(row["form"])
    data = form.evaluate()
    assert form.difficulty == row["difficulty"]
    assert sp.sstr(data.integrand) == row["integrand"]
    assert sp.sstr(data.primitive) == row["primitive"]
    assert sp.sstr(data.domain) == row["domain"]
    assert [s.latex for s in data.steps] == row["steps"]


@pytest.mark.parametrize("row", CURRICULUM["single"])
def test_single_derivative_curriculum_snapshot(row: dict) -> None:
    form = DerivativeForm.model_validate(row["form"])
    data = form.evaluate()
    assert form.difficulty == row["difficulty"]
    assert sp.sstr(data.function) == row["function"]
    assert sp.sstr(data.derivative) == row["expected"]
    assert sp.sstr(data.domain) == row["domain"]
    assert [s.latex for s in data.solution_steps] == row["steps"]


@pytest.mark.parametrize("row", CURRICULUM["partial"])
def test_partial_curriculum_snapshot(row: dict) -> None:
    form = PartialForm.model_validate(row["form"])
    data = form.evaluate()
    assert form.difficulty == row["difficulty"]
    assert data.variables == row["variables"]
    assert data.statement == row["statement"]
    assert sp.sstr(data.answer) == row["expected"]
    assert [s.latex for s in data.steps] == row["steps"]


@pytest.mark.parametrize("row", CURRICULUM["multiple"])
def test_multiple_curriculum_snapshot_and_independent_orders(row: dict) -> None:
    form = MultipleForm.model_validate(row["form"])
    template = (double if form.dimension == 2 else triple).TEMPLATES[form.template]
    variant = template.variants[form.variant]
    assert template.difficulty == row["difficulty"] and template.named == row["named"]
    assert sp.sstr(variant.value) == row["value"]
    assert sp.sstr(variant.problem_integrand()) == row["integrand"]
    assert [[sp.sstr(x) for x in b] for b in variant.solution.bounds] == row["bounds"]
    assert sp.sstr(variant.solution.integrand) == row["setup_integrand"]
    assert variant.solution.system == row["system"]
    assert str(getattr(variant, "region", None)) == row["region"]
    assert str(getattr(variant, "solid", None)) == row["solid"]
    data = form.evaluate()
    assert sp.simplify(integrate_setup(data.setup) - data.value) == 0
    if variant.exact_checks:
        for other in variant.checks:
            check = Setup(other.system, variant.problem_integrand(), other.bounds)
            assert sp.simplify(integrate_setup(check) - variant.value) == 0


@pytest.mark.parametrize("kind,form_type", [("algebra", AlgebraForm), ("analysis", AnalysisForm)])
def test_scalar_curriculum_snapshots(kind: str, form_type: type) -> None:
    for row in CURRICULUM[kind]:
        data = form_type.model_validate(row["form"]).evaluate()
        assert data.statement == row["statement"]
        assert sp.sstr(data.expected) == row["expected"]
        assert [s.latex for s in data.steps] == row["steps"]
