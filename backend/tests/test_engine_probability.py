"""Full approved matrix, independent worked examples and bounded worker checks."""

import sys
from itertools import product

import pytest
import sympy as sp
from pydantic import ValidationError

from app.engine import practice
from app.engine.answers.structured import BooleanAnswer, FiniteSetAnswer, IntervalAnswer
from app.engine.generators._probability_common import ProbabilityParams
from app.engine.generators.probability import SPECS, generators
from app.engine.opening import rebuild
from app.engine.rendering import statement_latex
from app.engine.topics.catalogue import topics
from app.engine.topics.probability import TOPIC_SPECS
from app.math_input import MathInputError, parse_answer_input
from app.services.math_worker import check_answer

R = sp.Rational


def scalar(value):
    return sp.sstr(sp.sympify(value)).replace("**", "^").replace("E", "e")


def source(answer):
    if isinstance(answer, BooleanAnswer):
        return "true" if answer.expected else "false"
    if isinstance(answer, FiniteSetAnswer):
        return "{" + ",".join(map(scalar, answer.expected)) + "}"
    if isinstance(answer, IntervalAnswer):
        return (
            ("(" if answer.left_open else "[")
            + ("-inf" if answer.lower == -sp.oo else scalar(answer.lower))
            + ","
            + ("inf" if answer.upper == sp.oo else scalar(answer.upper))
            + (")" if answer.right_open else "]")
        )
    return scalar(answer.expected)


def wrong(answer):
    if isinstance(answer, BooleanAnswer):
        return "false" if answer.expected else "true"
    if isinstance(answer, FiniteSetAnswer):
        return "{" + ",".join([*map(scalar, answer.expected), "11"]) + "}"
    if isinstance(answer, IntervalAnswer):
        if answer.upper == sp.oo:
            return source(IntervalAnswer(answer.lower + 1, sp.oo, answer.left_open, True))
        return source(
            IntervalAnswer(answer.lower, answer.upper + 1, answer.left_open, answer.right_open)
        )
    return "(" + source(answer) + ")+1"


@pytest.mark.parametrize("g", generators(), ids=lambda g: g.template)
def test_every_bounded_form_accepts_its_answer_and_seed_replay_is_exact(g):
    # All 125 mathematical parameter tuples, independently of draw frequency.
    for a, b, c in product(range(1, 6), repeat=3):
        task = g.build(ProbabilityParams(seed=0, a=a, b=b, c=c))
        text = source(task.answer)
        assert len(text.encode("ascii")) <= 256
        assert task.answer.check(parse_answer_input(text, task.answer.kind, {})) == "correct"
        assert statement_latex(task.statement)
        assert {step.text_key for step in task.steps} <= g.step_text.keys()
    for seed in range(20):
        params = g.draw(seed)
        task = g.build(params)
        assert task == g.build(ProbabilityParams.model_validate_json(params.model_dump_json()))
        opened = rebuild(task.code)
        record = opened.problem.issued().record
        assert practice.replay(record) == task and opened.difficulty == g.difficulty
        assert practice.input_variables(record) is None
        assert (
            task.answer.check(parse_answer_input(wrong(task.answer), task.answer.kind, {}))
            == "incorrect"
        )
        descriptor = practice.input_projection(record)
        assert bool(descriptor) == (task.answer.kind in {"boolean", "finite_set", "interval"})


def test_all_45_approved_cells_and_74_distinct_frozen_identities_are_issued():
    assert len(TOPIC_SPECS) == 9 and len(SPECS) == 74
    assert len({prefix for _, _, prefix, _ in SPECS}) == 74
    declared = {}
    for slug, title, space, levels in TOPIC_SPECS:
        topic = topics()[slug]
        assert topic.area == "probability-statistics" and topic.title == title
        assert topic.space_cm == space and topic.mixed_weight == 1 and topic.served
        assert set(levels) == {1, 2, 3, 4, 5}
        for level, names in levels.items():
            assert {c.generator for c in topic.levels[level]} == {
                f"probability-{name}-v1" for name in names
            }
            declared.update((name, level) for name in names)
    assert declared == {name: level for name, level, _, _ in SPECS}


# Hand-worked answers for a=2,b=3,c=4. These do not read the generator's blocks.
EXAMPLES = {
    "events-equal": R(2, 5),
    "events-complement": R(3, 5),
    "events-at-least-one": R(2882, 3125),
    "events-union": R(9, 11),
    "events-intersection": R(7, 22),
    "events-selection": R(1, 7),
    "events-set": (1, 2, 3, 4, 5, 6),
    "events-independence": False,
    "conditional-table": R(7, 10),
    "conditional-replacement": R(3, 7),
    "conditional-without": R(1, 3),
    "conditional-total": R(4, 7),
    "conditional-bayes-two": R(3, 10),
    "conditional-bayes-three": R(40, 133),
    "conditional-tree": R(4, 7),
    "finite-normalize": R(1, 9),
    "finite-point": R(1, 3),
    "finite-cdf": R(5, 9),
    "finite-tail": R(4, 9),
    "finite-support": (-2, 3),
    "finite-jump": R(1, 3),
    "finite-transform": R(2, 3),
    "discrete-bernoulli": R(4, 7),
    "discrete-binomial": R(432, 2401),
    "discrete-geometric": R(48, 343),
    "discrete-hypergeometric": R(4, 165),
    "discrete-poisson": R(4, 3) * sp.exp(-2),
    "continuous-uniform": R(3, 10),
    "continuous-normalize": R(3, 62),
    "continuous-support": (-2, 3, False, False),
    "continuous-piecewise-cdf": R(125, 188),
    "continuous-interval": R(89, 188),
    "continuous-exponential-tail": sp.exp(-R(8, 5)),
    "continuous-memoryless": sp.exp(-R(8, 5)),
    "continuous-exponential-quantile": R(5, 2) * sp.log(R(7, 4)),
    "continuous-normal-standardize": R(3, 2),
    "continuous-normal-probability": R(6681, 100000),
    "continuous-normal-quantile": R(7, 2),
    "moments-mean": R(8, 9),
    "moments-variance": R(332, 81),
    "moments-deviation": 2 * sp.sqrt(83) / 9,
    "moments-affine-mean": R(50, 9),
    "moments-affine-variance": R(5312, 81),
    "moments-marginal": R(15, 22),
    "moments-conditional": R(1, 3),
    "moments-covariance": R(2, 121),
    "moments-correlation": sp.sqrt(14) / 105,
    "moments-independence": False,
    "sample-mean": R(1, 6),
    "sample-weighted": R(8, 9),
    "sample-median": 0,
    "sample-modes": (-1, 0),
    "sample-quartile": -1,
    "sample-iqr": 2,
    "sample-population-variance": R(41, 36),
    "sample-sample-variance": R(41, 30),
    "sample-deviation": sp.sqrt(R(41, 30)),
    "sample-correlation": sp.sqrt(21) / 7,
    "sample-slope": R(4, 7),
    "sample-intercept": R(20, 21),
    "ci-mean-z": (-R(1663, 375), R(913, 375), False, False),
    "ci-mean-t": (-1 - R(1388, 625) * sp.sqrt(5), -1 + R(1388, 625) * sp.sqrt(5), False, False),
    "ci-lower": (-R(479, 150), sp.oo, False, True),
    "ci-upper": (-sp.oo, R(179, 150), True, False),
    "ci-proportion": (
        R(15, 32) - R(49, 25) * sp.sqrt(R(255, 163840)),
        R(15, 32) + R(49, 25) * sp.sqrt(R(255, 163840)),
        False,
        False,
    ),
    "ci-paired": (
        R(7, 6) - R(2571, 6000) * sp.sqrt(13),
        R(7, 6) + R(2571, 6000) * sp.sqrt(13),
        False,
        False,
    ),
    "ci-difference": (-1 - R(49, 500) * sp.sqrt(481), -1 + R(49, 500) * sp.sqrt(481), False, False),
    "test-z-statistic": -R(5, 3),
    "test-z-decision": False,
    "test-t-statistic": 0,
    "test-t-decision": False,
    "test-proportion": False,
    "test-paired": False,
    "test-difference": False,
}


@pytest.mark.parametrize("g", generators(), ids=lambda g: g.template)
def test_independently_worked_example_for_every_template(g):
    assert set(EXAMPLES) == {name for name, _, _, _ in SPECS}
    task = g.build(ProbabilityParams(seed=0, a=2, b=3, c=4))
    expected = EXAMPLES[g.template]
    answer = task.answer
    if isinstance(answer, BooleanAnswer):
        assert answer.expected is expected
    elif isinstance(answer, FiniteSetAnswer):
        assert set(answer.expected) == set(expected)
    elif isinstance(answer, IntervalAnswer):
        lo, hi, left, right = expected
        assert answer.lower == lo or sp.simplify(answer.lower - lo) == 0
        assert answer.upper == hi or sp.simplify(answer.upper - hi) == 0
        assert (answer.left_open, answer.right_open) == (left, right)
    else:
        assert sp.simplify(answer.expected - expected) == 0


def test_boolean_templates_have_both_outcomes_and_inference_boundary_examples():
    for g in generators():
        if g.answer.kind == "boolean":
            outcomes = {
                g.build(ProbabilityParams(seed=0, a=a, b=b, c=c)).answer.expected
                for a, b, c in product(range(1, 6), repeat=3)
            }
            assert outcomes == {False, True}, g.template


def test_event_set_operations_include_disjoint_intersections_and_empty_differences():
    g = next(g for g in generators() if g.template == "events-set")
    for a, b, c in ((1, 5, 2), (2, 1, 3)):
        task = g.build(ProbabilityParams(seed=0, a=a, b=b, c=c))
        assert task.answer.expected == ()
        assert task.answer.check(parse_answer_input("{}", "finite_set")) == "correct"


@pytest.mark.parametrize("change", [{"a": True}, {"b": 0}, {"c": 6}, {"a": 1.0}, {"extra": 1}])
def test_probability_drawn_parameters_are_strict_and_bounded(change):
    with pytest.raises(ValidationError):
        ProbabilityParams.model_validate({"seed": 0, "a": 1, "b": 1, "c": 1, **change})


@pytest.mark.parametrize("g", generators(), ids=lambda g: g.template)
@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux resource-limited worker")
def test_probability_canonical_and_wrong_answers_fit_worker_limits(g):
    import resource

    task = g.build(g.draw(200))
    record = {"generator_version": g.version, "code": task.code}
    for text, expected in ((source(task.answer), "correct"), (wrong(task.answer), "incorrect")):
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        assert check_answer(text, record).result == expected
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
        assert cpu <= 1.0, (g.template, cpu)


def test_unselected_boolean_and_undefined_structured_components_are_invalid():
    with pytest.raises(MathInputError):
        parse_answer_input("", "boolean")
    for text in ("{x-x}", "{1/0}", "[0,1+0*(1/0)]"):
        with pytest.raises(MathInputError):
            parse_answer_input(text, "interval" if text.startswith("[") else "finite_set")
