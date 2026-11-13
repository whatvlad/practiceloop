"""Every advertised mode is issuable through its existing canonical topic."""

from dataclasses import replace

import pytest

from app.engine.algebra_practice.catalogue_seeds import mode_seeds
from app.engine.generators.catalogue import registry
from app.engine.generators.geometry_practice import MODES, GeometryPractice
from app.engine.rendering import render
from app.engine.topics.catalogue import topics


@pytest.mark.parametrize("level", [1, 2, 3])
def test_every_new_mode_is_in_its_canonical_topic_and_prepared_catalogue_settings(level):
    entries = topics()
    candidates = (*mode_seeds("vectors", level, 0), *mode_seeds("lines-and-planes", level, 0))
    indexed = {mode: (version, seed) for mode, version, seed in candidates}
    assert set(MODES) <= set(indexed)
    generators = registry()
    for mode in MODES:
        version, seed = indexed[mode]
        topic = "vectors" if mode in MODES[:4] else "lines-and-planes"
        assert version in {choice.generator for choice in entries[topic].levels[level]}
        generator = generators.get(version)
        params = generator.draw(seed)
        assert params.level == level
        issued = render(generator.build(params), generators)
        assert issued.statement_visual and all(s.get("rules") for s in issued.steps)


@pytest.mark.parametrize("mode", MODES)
def test_request_schema_accepts_each_new_mode_without_broadening_unknown_options(mode):
    from app.api.practice import GenerateBody

    topic = "vectors" if mode in MODES[:4] else "lines-and-planes"
    assert GenerateBody(topic=topic, difficulty=1, exerciseMode=mode).exerciseMode == mode


@pytest.mark.parametrize("topic", ["vectors", "lines-and-planes"])
def test_random_geometry_selects_types_equally_despite_unequal_pool_counts(topic):
    from collections import Counter

    from app.engine import practice

    modes = {
        practice.public_settings(problem.issued().record).get(
            "exerciseMode", problem.generator_version
        )
        for problem in practice.pool(topic, 1)
    }
    chosen = Counter(
        practice.public_settings(issued.record).get(
            "exerciseMode", issued.record["generator_version"]
        )
        for seed in range(len(modes))
        for issued in (practice.issue(topic, 1, seed=seed),)
    )
    assert chosen == dict.fromkeys(modes, 1)


def test_prepared_geometry_code_opens_at_its_level_without_competing_for_a_worker(monkeypatch):
    from app.api import codes
    from app.engine import practice

    problem = next(
        p
        for p in practice.pool("lines-and-planes", 3)
        if p.generator_version == "geometry-practice-planes-three-lines-v1"
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("A verified pooled geometry code must not occupy a symbolic worker")

    codes._opened.cache_clear()
    monkeypatch.setattr(codes, "open_problem_code", forbidden)
    try:
        opened = codes._opened(problem.code)
        assert (opened.topic, opened.difficulty) == ("lines-and-planes", 3)
        assert opened.problem == problem
        public = codes.lookup(problem.code)["problem"]
        assert public["statementVisual"] == problem.statement_visual
        assert not {"answerLatex", "steps", "generator_version", "generator_data"} & public.keys()
    finally:
        codes._opened.cache_clear()


def test_verified_pools_cover_every_mode_and_boundary_case_and_issue_without_symbolic_build(
    monkeypatch,
):
    from app.engine import practice
    from app.engine.catalogue import build
    from app.engine.generators.geometry_practice import VECTOR_MODES

    entries = {
        slug: replace(topic, levels={1: topic.levels[1]})
        for slug, topic in topics().items()
        if slug in {"vectors", "lines-and-planes"}
    }
    catalogue = build(entries, pool_size=64)
    pools = {cell.topic: cell.problems for cell in catalogue.cells}
    assert len(pools["vectors"]) == 64
    assert len(pools["lines-and-planes"]) == 80
    for mode in MODES:
        topic = "vectors" if mode in VECTOR_MODES else "lines-and-planes"
        matching = [
            p
            for p in pools[topic]
            if practice.public_settings(p.issued().record).get("exerciseMode") == mode
        ]
        assert len(matching) >= 2
    # The relative-position and zero-distance cases are stored, not only testable draws.
    expected = {
        "line-position": {0, 1, 2, 3},
        "line-plane-position": {0, 1, 2},
        "same-side": {0, 1, 2},
        "line-angle": {0, 1, 2},
        "plane-angle": {0, 1, 2},
    }
    from app.engine.codes import parse_code

    for mode, cases in expected.items():
        seeds = {
            parse_code(p.code, registry()).seed
            for p in pools["lines-and-planes"]
            if practice.public_settings(p.issued().record).get("exerciseMode") == mode
        }
        assert cases <= seeds
    monkeypatch.setattr(practice, "pool", lambda topic, level: pools[topic])

    def forbidden(*args, **kwargs):
        raise AssertionError("A request must not construct a symbolic geometry task")

    monkeypatch.setattr(GeometryPractice, "draw", forbidden)
    monkeypatch.setattr(GeometryPractice, "build", forbidden)
    for mode in MODES:
        topic = "vectors" if mode in VECTOR_MODES else "lines-and-planes"
        issued = practice.issue(topic, 1, exercise_mode=mode)
        assert practice.public_settings(issued.record) == {"exerciseMode": mode}
        assert practice.input_projection(issued.record)["answerInput"]
