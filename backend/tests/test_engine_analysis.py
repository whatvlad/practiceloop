"""#197: remaining analysis curriculum, corrected mathematics and engine routing."""

import sys
from types import FrameType
from typing import Any

import pytest
import sympy as sp
from engine_fixtures import PUBLISHED_TOPICS
from pydantic import ValidationError
from test_engine_analysis_limits import source as limit_source

from app.api import practice
from app.engine import practice as engine
from app.engine.blocks.analysis import AnalysisForm
from app.engine.codes import encode
from app.engine.generators.analysis import AnalysisParams, analysis_generators
from app.math_input import parse_answer_input, parse_math_input
from app.services import archive
from app.services.math_worker import check_answer, record_variables

TEMPLATES = {
    "functions-and-sequences": ("sequence-value",),
    "limits-and-continuity": ("limit", "continuity"),
    "improper-integrals": ("improper-integral",),
    "series": ("geometric-series",),
    "multivariable-functions": ("partial-value",),
    "differential-equations": ("exponential-solution",),
}
CASES = [(slug, level) for slug in TEMPLATES for level in range(1, 6)]


def answer_text(record: dict[str, object]) -> str:
    answer = engine.replay(record).answer
    if answer.kind == "expression":
        return sp.sstr(answer.expected).replace("**", "^")
    return limit_source(answer)


@pytest.mark.parametrize("a", range(1, 6))
def test_geometric_sum_matches_infinite_sum_and_rejects_previous_wrong_formula(a: int) -> None:
    from app.engine.answers.expression import ExpressionAnswer

    n = sp.Symbol("n", integer=True, nonnegative=True)
    form = AnalysisForm(kind="geometric-series", a=a, b=1)
    result = form.evaluate()
    assert result.expected == sp.summation(sp.Rational(a, a + 1) ** n, (n, 0, sp.oo))
    answer = ExpressionAnswer(result.expected, {})
    assert answer.check(parse_math_input(str(a + 1))) == "correct"
    if a > 1:
        assert answer.check(parse_math_input(f"{a + 1}/{a}")) == "incorrect"


@pytest.mark.parametrize("a,b", [(a, b) for a in range(1, 6) for b in range(1, 6)])
def test_multivariable_derivative_holds_the_by_term_constant(a: int, b: int) -> None:
    from app.engine.answers.expression import ExpressionAnswer

    x, y = sp.symbols("x y", real=True)
    data = AnalysisForm(kind="partial-value", a=a, b=b).evaluate()
    assert data.expected == sp.diff(a * x**2 * y + b * y, x)
    answer = ExpressionAnswer(data.expected, {"x": "real", "y": "real"})
    assert answer.check(parse_math_input(f"{2 * a}*x*y", {"x", "y"})) == "correct"
    assert answer.check(parse_math_input(f"{2 * a}*x*y+{b}", {"x", "y"})) == "incorrect"


@pytest.mark.parametrize("slug,level", CASES)
def test_each_analysis_level_checks_and_preserves_mixed_worksheets_archive(
    slug: str, level: int
) -> None:
    entry, old = engine.ENGINE_TOPICS[slug], PUBLISHED_TOPICS[slug]
    assert (tuple(entry.levels), entry.mixed_weight, entry.space_cm) == (
        old.levels,
        old.mixed_weight,
        old.space_cm,
    )
    record = engine.issue(slug, level, seed=197).record
    assert set(record) == {"generator_version", "code"}
    variables = record_variables(record)
    text = answer_text(record)

    def parse(value: str):
        return parse_answer_input(
            value, engine.input_kind(record), variables, contract=engine.input_contract(record)
        )

    assert engine.check(record, parse(text)) == "correct"
    if engine.input_kind(record) == "expression":
        assert engine.check(record, parse(f"({text})+1")) == "incorrect"
    else:
        # A fixed scalar cannot equal the new complete set or ordered answer.
        assert engine.check(record, parse_math_input("0", variables)) != "correct"
    assert archive.is_archived(slug, {"generator_version": "symbolic-v1"})
    assert not archive.is_archived(slug, record)
    assert practice.capacity(slug, level) == 64
    assert slug in practice.mixed_topics("mathematical-analysis", level, worksheet=True)[0]


def test_analysis_variable_metadata_does_no_symbolic_work_and_returns_fresh_mappings() -> None:
    records = [
        # The historical two-variable version retains its exact grammar after #146.
        {"generator_version": "practice-multivariable-v1", "code": encode("MVF", 1, 197)},
        engine.issue("differential-equations", 5, seed=197).record,
    ]
    calls: list[str] = []

    def profile(frame: FrameType, event: str, _: Any) -> None:
        if event == "call" and frame.f_globals.get("__name__", "").startswith("sympy"):
            calls.append(frame.f_code.co_name)

    previous = sys.getprofile()
    engine._registry.cache_clear()
    sys.setprofile(profile)
    try:
        mappings = [record_variables(r) for r in records]
    finally:
        sys.setprofile(previous)
    assert not calls
    assert mappings == [{"x": "real", "y": "real"}, {"x": "real"}]
    mappings[0].clear()
    assert record_variables(records[0]) == {"x": "real", "y": "real"}


@pytest.mark.parametrize("generator", analysis_generators(), ids=lambda g: g.version)
def test_analysis_drawn_parameters_survive_json_and_reject_other_templates(generator: Any) -> None:
    params = generator.draw(197)
    assert generator.build(
        AnalysisParams.model_validate_json(params.model_dump_json())
    ) == generator.build(params)
    other = next(g for g in analysis_generators() if g.templates != generator.templates)
    with pytest.raises(ValueError, match="different generator"):
        generator.build(other.draw(197))


@pytest.mark.parametrize("change", [{"kind": "unknown"}, {"a": 0}, {"b": 6}, {"a": True}])
def test_invalid_analysis_forms_are_rejected(change: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        AnalysisForm.model_validate({"kind": "limit", "a": 1, "b": 1, **change})


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize("slug,level", CASES)
def test_every_analysis_level_checks_in_limited_worker(slug: str, level: int) -> None:
    record = engine.issue(slug, level, seed=197).record
    assert check_answer(answer_text(record), record).result == "correct"
