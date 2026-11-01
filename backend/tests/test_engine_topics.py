"""Topic views select reproducible generator tasks without changing the API."""

import importlib

import pytest
import sympy as sp

from app.engine.answers._symbolic import X
from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.engine.answers.derivative import DerivativeAnswer
from app.engine.codes import parse_code
from app.engine.generators.catalogue import registry
from app.engine.prng import DeterministicRNG


def topic_module():
    return importlib.import_module("app.engine.topics.catalogue")


def test_five_topics_have_nonempty_levels_and_replay_for_many_seeds() -> None:
    topics = topic_module().topics()
    assert set(topics) == {
        "partial-fractions",
        "derivatives",
        "indefinite-integrals",
        "definite-integrals",
        "combinations",
    }
    generators = registry()
    expected_kinds = {
        "partial-fractions": "expression",
        "derivatives": "derivative",
        "indefinite-integrals": "antiderivative",
        "definite-integrals": "number",
        "combinations": "number",
    }
    for topic in topics.values():
        assert topic.slug in topics and topic.area and topic.mixed_weight > 0
        assert topic.levels
        for level, choices in topic.levels.items():
            assert choices
            for seed in range(8):
                task = topic.generate(level, seed, generators)
                assert task.answer.kind == expected_kinds[topic.slug]
                assert task.statement and task.steps
                code = parse_code(task.code, generators)
                generator = generators.get_code(code.prefix, code.version)
                assert generator.build(generator.draw(code.seed)) == task
                if seed == 0:
                    assert topic.generate(level, seed, generators) == task


def test_levels_filter_polynomial_and_rational_parameters() -> None:
    topics = topic_module().topics()
    generators = registry()
    for slug in ("derivatives", "indefinite-integrals", "definite-integrals"):
        for level, rational in ((1, False), (2, True)):
            for seed in range(8):
                task = topics[slug].generate(level, seed, generators)
                code = parse_code(task.code, generators)
                assert bool(DeterministicRNG(code.seed).randbelow(2)) is rational
                if isinstance(task.answer, AntiderivativeAnswer):
                    assert bool(task.answer.integrand.as_numer_denom()[1].has(X)) is rational
                elif isinstance(task.answer, DerivativeAnswer):
                    assert bool(task.answer.domain != sp.S.Reals) is rational
                else:
                    inner = generators.get("indefinite-v1")
                    integral = inner.build(inner.draw(code.seed))
                    assert isinstance(integral.answer, AntiderivativeAnswer)
                    assert bool(integral.answer.integrand.as_numer_denom()[1].has(X)) is rational


def test_definite_topic_shares_indefinite_generator_through_its_wrapper() -> None:
    topics = topic_module().topics()
    indefinite = topics["indefinite-integrals"].levels[1][0]
    definite = topics["definite-integrals"].levels[1][0]
    assert indefinite.generator == definite.generator == "indefinite-v1"
    assert definite.wrapper == "definite-v1"
    assert indefinite.generator in registry().get(definite.wrapper).requires


def test_topic_extension_and_invalid_inputs() -> None:
    module = topic_module()
    extra = module.Topic(
        slug="new-counting-topic",
        area="combinatorics",
        levels={1: (module.Choice("combinations-v1"),)},
        mixed_weight=1,
    )
    assert extra.generate(1, 12, registry()).answer.kind == "number"
    with pytest.raises(ValueError):
        extra.generate(2, 12, registry())
    for bad in (-1, 10**16, True):
        with pytest.raises(ValueError):
            extra.generate(1, bad, registry())
    with pytest.raises(ValueError):
        module.Topic(slug="empty", area="algebra", levels={1: ()}, mixed_weight=1)
    with pytest.raises(ValueError):
        module.Topic(
            slug="bad",
            area="algebra",
            levels={1: (module.Choice("combinations-v1"),)},
            mixed_weight=0,
        )


def test_filter_has_bounded_redraw_and_wrapper_must_depend_on_generator() -> None:
    module = topic_module()
    impossible = module.Topic(
        slug="never",
        area="algebra",
        mixed_weight=1,
        levels={1: (module.Choice("combinations-v1", predicate=lambda _: False),)},
    )
    with pytest.raises(ValueError, match="after 64"):
        impossible.generate(1, 1, registry())
    invalid = module.Topic(
        slug="invalid",
        area="algebra",
        mixed_weight=1,
        levels={1: (module.Choice("combinations-v1", wrapper="definite-v1"),)},
    )
    with pytest.raises(ValueError, match="depend"):
        invalid.generate(1, 1, registry())


def test_a_level_can_choose_between_multiple_generators_deterministically() -> None:
    module = topic_module()
    topic = module.Topic(
        slug="mixed-demo",
        area="algebra",
        mixed_weight=1,
        levels={1: (module.Choice("combinations-v1"), module.Choice("partial-fractions-v1"))},
    )
    generators = registry()
    selected = {topic.generate(1, seed, generators).generator_version for seed in range(20)}
    assert selected == {"combinations-v1", "partial-fractions-v1"}
    assert topic.generate(1, 12, generators) == topic.generate(1, 12, generators)
