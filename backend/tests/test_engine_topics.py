"""Topic views select reproducible generator tasks without changing the API."""

import importlib
import logging

import pytest
import sympy as sp

from app.engine.answers._symbolic import X
from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.engine.answers.derivative import DerivativeAnswer
from app.engine.codes import parse_code
from app.engine.generators.catalogue import registry
from app.engine.generators.combinations import CombinationParams, Combinations
from app.engine.generators.definite import DefiniteParams
from app.engine.generators.indefinite import IndefiniteIntegral
from app.engine.generators.partial_fractions import PartialFractionParams
from app.engine.models import Task
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
        "basic-integrals",
        "substitution",
        "integration-by-parts",
        "rational-functions",
        "trigonometric-integrals",
        "double-integrals",
        "triple-integrals",
        "partial-derivatives",
        "matrices",
        "complex-numbers",
        "fundamental-theorem-algebra",
        "algebraic-expressions",
        "polynomial-division",
        "determinants",
        "inverse-matrices",
        "linear-systems",
        "matrix-rank",
        "functions-and-sequences",
        "limits-and-continuity",
        "improper-integrals",
        "series",
        "multivariable-functions",
        "differential-equations",
    }
    generators = registry()
    expected_kinds = {
        "partial-fractions": "expression",
        "derivatives": "derivative",
        "indefinite-integrals": "antiderivative",
        "definite-integrals": "expression",
        "combinations": "number",
        "double-integrals": "expression",
        "triple-integrals": "expression",
        "partial-derivatives": "expression",
    }
    for topic in topics.values():
        assert topic.slug in topics and topic.area and topic.mixed_weight >= 0
        assert topic.levels
        for level, choices in topic.levels.items():
            assert choices
            for seed in range(8):
                task = topic.generate(level, seed, generators)
                if topic.slug in expected_kinds:
                    assert task.answer.kind == expected_kinds[topic.slug]
                else:
                    assert task.answer.kind in {"antiderivative", "expression"}
                assert task.statement and task.steps
                code = parse_code(task.code, generators)
                generator = generators.get_code(code.prefix, code.version)
                assert generator.build(generator.draw(code.seed)) == task
                if seed == 0:
                    assert topic.generate(level, seed, generators) == task


def test_levels_filter_polynomial_and_rational_parameters() -> None:
    topics = topic_module().topics()
    generators = registry()
    for slug in ("indefinite-integrals",):
        for level, rational in ((1, False), (2, True)):
            for seed in range(8):
                task = topics[slug].generate(level, seed, generators)
                code = parse_code(task.code, generators)
                params = generators.get_code(code.prefix, code.version).draw(code.seed)
                if isinstance(params, DefiniteParams):
                    params = params.integral
                assert params.rational is rational
                assert isinstance(params.function, PartialFractionParams) is rational
                if isinstance(task.answer, AntiderivativeAnswer):
                    assert bool(task.answer.integrand.as_numer_denom()[1].has(X)) is rational
                elif isinstance(task.answer, DerivativeAnswer):
                    assert bool(task.answer.domain != sp.S.Reals) is rational


def test_definite_parameters_hold_the_indefinite_parameters_of_the_same_seed() -> None:
    generators = registry()
    definite, indefinite = generators.get("definite-v1"), generators.get("indefinite-v1")
    assert "indefinite-v1" in definite.requires
    for seed in range(20):
        params = definite.draw(seed)
        assert params.integral == indefinite.draw(seed)
        integral = IndefiniteIntegral().integrate(params.integral)
        assert definite.build(params).steps[:-1] == integral.steps


def test_topic_extension_and_invalid_inputs() -> None:
    module = topic_module()
    extra = module.Topic(
        slug="new-counting-topic",
        area="algebra",
        levels={1: (module.Choice("combinations-v1"),)},
        mixed_weight=1,
        title="Demo",
        space_cm=4,
    )
    assert extra.generate(1, 12, registry()).answer.kind == "number"
    with pytest.raises(ValueError):
        extra.generate(2, 12, registry())
    for bad in (-1, 10**16, True):
        with pytest.raises(ValueError):
            extra.generate(1, bad, registry())
    with pytest.raises(ValueError):
        module.Topic(
            slug="empty", area="algebra", levels={1: ()}, mixed_weight=1, title="Demo", space_cm=4
        )
    with pytest.raises(ValueError, match="area"):
        module.Topic(
            slug="bad-area",
            area="analysis",
            levels={1: (module.Choice("combinations-v1"),)},
            mixed_weight=1,
            title="Demo",
            space_cm=4,
        )
    with pytest.raises(ValueError):
        module.Topic(
            slug="bad",
            area="algebra",
            levels={1: (module.Choice("combinations-v1"),)},
            mixed_weight=-1,
            title="Demo",
            space_cm=4,
        )
    for product in ({"title": ""}, {"space_cm": 0}):
        with pytest.raises(ValueError, match="title and positive worksheet space"):
            module.Topic(
                slug="bad-product",
                area="algebra",
                levels={1: (module.Choice("combinations-v1"),)},
                mixed_weight=1,
                **{"title": "Demo", "space_cm": 4, **product},
            )


def test_filter_has_bounded_redraw() -> None:
    module = topic_module()
    impossible = module.Topic(
        slug="never",
        area="algebra",
        mixed_weight=1,
        title="Demo",
        space_cm=4,
        levels={1: (module.Choice("combinations-v1", predicate=lambda _: False),)},
    )
    with pytest.raises(ValueError, match="after 64"):
        impossible.generate(1, 1, registry())


def test_a_candidate_that_fails_to_build_is_redrawn_and_logged(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    module = topic_module()
    topic = module.Topic(
        "combinations",
        "algebra",
        {1: (module.Choice("combinations-v1"),)},
        1,
        title="Combinations",
        space_cm=4,
    )
    generators = registry()
    expected = topic.generate(1, 5, generators)
    first = DeterministicRNG(5)
    first.randbelow(1)
    rejected = first.randbelow(10**16)
    build = Combinations.build

    def flaky(self: Combinations, params: CombinationParams) -> Task:
        if params.seed == rejected:
            raise ValueError("cannot build")
        return build(self, params)

    monkeypatch.setattr(Combinations, "build", flaky)
    with caplog.at_level(logging.WARNING, logger=module.__name__):
        task = topic.generate(1, 5, generators)
    assert task != expected and task.generator_version == "combinations-v1"
    assert parse_code(task.code, generators).seed == first.randbelow(10**16)
    assert [record.getMessage() for record in caplog.records] == [
        f"combinations-v1 did not build seed {rejected}; drawing the next candidate"
    ]
    monkeypatch.setattr(Combinations, "build", lambda *_: (_ for _ in ()).throw(ValueError()))
    with pytest.raises(ValueError, match="after 64"):
        topic.generate(1, 5, generators)


def test_a_level_can_choose_between_multiple_generators_deterministically() -> None:
    module = topic_module()
    topic = module.Topic(
        slug="mixed-demo",
        area="algebra",
        mixed_weight=1,
        title="Demo",
        space_cm=4,
        levels={1: (module.Choice("combinations-v1"), module.Choice("partial-fractions-v1"))},
    )
    generators = registry()
    selected = {topic.generate(1, seed, generators).generator_version for seed in range(20)}
    assert selected == {"combinations-v1", "partial-fractions-v1"}
    assert topic.generate(1, 12, generators) == topic.generate(1, 12, generators)
