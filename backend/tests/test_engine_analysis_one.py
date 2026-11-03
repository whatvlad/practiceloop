"""Full #145 template matrix, exact replay/proofs and bounded worker regressions."""

import sys
from fractions import Fraction

import pytest
import sympy as sp
from pydantic import ValidationError

from app.engine.blocks.analysis_one import AnalysisOneForm, bisect_exp, evaluate, exp_bounds
from app.engine.generators.analysis_one import MATRIX, generators
from app.engine.opening import rebuild
from app.engine.practice import input_variables, replay
from app.engine.topics.catalogue import topics
from app.math_input import parse_math_input
from app.services.math_worker import check_answer


@pytest.mark.parametrize("g", generators(), ids=lambda g: g.version)
def test_every_template_is_offered_replays_and_checks_equivalent_answers(g) -> None:
    for seed in range(40):
        params = g.draw(seed)
        task = g.build(params)
        assert g.build(type(params).model_validate_json(params.model_dump_json())) == task
        variables = task.answer.variables or None
        answer = sp.sstr(task.answer.expected).replace("E", "e").replace("**", "^")
        assert (
            task.answer.check(parse_math_input(f"({answer})+0", variables=variables)) == "correct"
        )
        assert (
            task.answer.check(parse_math_input(f"({answer})+1", variables=variables)) == "incorrect"
        )
        assert task.metadata["difficulty"] == g.difficulty
        assert all(step.text_key in g.step_text for step in task.steps)
    opened = rebuild(task.code)
    assert g.version in {c.generator for c in topics()[opened.topic].levels[opened.difficulty]}
    assert replay(opened.problem.issued().record) == task
    assert input_variables(opened.problem.issued().record) == variables


def test_matrix_covers_each_method_and_retains_existing_integral_and_derivative_versions() -> None:
    assert sum(len(k) for levels in MATRIX.values() for k in levels.values()) == 33
    for slug, levels in MATRIX.items():
        assert topics()[slug].mixed_weight == 1
        assert set(levels) == set(range(1, 6))
        for level, kinds in levels.items():
            assert {c.generator for c in topics()[slug].levels[level]} == {
                f"analysis1-{k}-v1" for k in kinds
            }
    assert topics()["derivatives"].levels[1][0].generator == "practice-derivative-v1"


@pytest.mark.parametrize("a", range(1, 6))
def test_bisection_has_exact_sign_certificates_error_bound_and_unique_root(a) -> None:
    midpoint, intervals = bisect_exp(a)
    for i, (lo, hi) in enumerate(intervals):
        assert hi - lo == Fraction(a, 2 ** (i + 1))
        assert exp_bounds(lo)[1] + lo**2 < a + 1
        assert exp_bounds(hi)[0] + hi**2 > a + 1
    assert midpoint == sum(intervals[-1]) / 2
    # Independent high precision root confirms the certified enclosure.
    root = sp.nsolve(sp.exp(sp.Symbol("x")) + sp.Symbol("x") ** 2 - a - 1, 1, prec=60)
    assert abs(root - sp.Rational(midpoint)) <= sp.Rational(a, 128)


def test_bisection_equation_has_no_supported_closed_form() -> None:
    x = sp.Symbol("x")
    with pytest.raises(NotImplementedError):
        sp.solve(sp.exp(x) + x**2 - 2, x)


def test_bounded_params_and_derivative_theorem_and_global_extremum() -> None:
    with pytest.raises(ValidationError):
        AnalysisOneForm(a=6, b=1, c=1)
    for a in range(1, 6):
        p = AnalysisOneForm(a=a, b=2, c=3)
        assert evaluate("mean-value", p).expected == sp.Rational(3, 2)
        assert evaluate("global-extremum", p).expected == -2 * a**3
        assert evaluate("box", p).expected == sp.Rational(2 * a**3, 27)
    for kind in ("limit-left", "limit-right", "limit-infinite", "sequence-oscillation"):
        assert len(evaluate(kind, p).steps) >= 2


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize("g", generators(), ids=lambda g: g.version)
def test_every_added_version_opens_and_checks_inside_the_limited_worker(g) -> None:
    task = g.build(g.draw(145))
    record = {"generator_version": g.version, "code": task.code}
    answer = sp.sstr(task.answer.expected).replace("E", "e").replace("**", "^")
    assert check_answer(answer, record).result == "correct"
    assert check_answer(f"({answer})+1", record).result == "incorrect"
