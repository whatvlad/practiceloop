"""Production packaging must preserve the local modulus generator contract."""

import pytest
import sympy as sp

from app.engine.algebra_practice.modulus import (
    CircleParameters,
    LocalModulusCircle,
    LocalModulusPractice,
    ModulusPracticeParameters,
)


def test_local_preview_reuses_the_packaged_generator() -> None:
    from local_modulus_generator import LocalModulusCircle as LocalCircle
    from local_modulus_generator import LocalModulusPractice as LocalPractice

    assert LocalCircle is LocalModulusCircle
    assert LocalPractice is LocalModulusPractice


def test_local_registry_can_replay_packaged_modulus_codes() -> None:
    from app.engine.codes import parse_code
    from local_matrix_preview import _registry

    task = LocalModulusCircle().build(LocalModulusCircle().draw(12345))
    catalogue = _registry()
    code = parse_code(task.code, catalogue)
    generator = catalogue.get_code(code.prefix, code.version)
    assert generator.version == LocalModulusCircle.version
    assert generator.build(generator.draw(code.seed)).code == task.code


def test_modulus_generators_are_registered_in_production_topic() -> None:
    from app.engine.codes import parse_code
    from app.engine.generators.catalogue import registry
    from app.engine.topics.catalogue import topics

    catalogue = registry()
    topic = topics()["complex-numbers"]
    for generator in (LocalModulusPractice(), LocalModulusCircle()):
        task = generator.build(generator.draw(123))
        code = parse_code(task.code, catalogue)
        assert catalogue.get_code(code.prefix, code.version).version == generator.version
        assert all(
            any(choice.generator == generator.version for choice in topic.levels[level])
            for level in (1, 2, 3)
        )


def test_production_request_supports_a_modulus_mode() -> None:
    from app.api.practice import GenerateBody

    body = GenerateBody(topic="complex-numbers", difficulty=2, modulusMode="geometry")
    assert body.modulusMode == "geometry"


def test_public_practice_settings_are_recovered_from_modulus_code() -> None:
    from app.engine.practice import public_settings

    for generator, seed, expected in (
        (LocalModulusPractice(), 0, "expression"),
        (LocalModulusPractice(), 3 * 10**12, "properties"),
        (LocalModulusCircle(), 0, "geometry"),
    ):
        task = generator.build(generator.draw(seed))
        record = {"generator_version": task.generator_version, "code": task.code}
        assert public_settings(record) == {"modulusMode": expected}
    assert public_settings(None) == {}


def test_production_picks_only_requested_modulus_kind(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.engine import practice
    from app.engine.catalogue import StoredProblem
    from app.engine.rendering import render

    generators = practice._registry()
    practice_generator = LocalModulusPractice()
    circle_generator = LocalModulusCircle()
    tasks = [
        practice_generator.build(practice_generator.draw(0)),
        practice_generator.build(practice_generator.draw(3 * 10**12)),
        circle_generator.build(circle_generator.draw(0)),
    ]
    candidates = tuple(StoredProblem.from_issued(render(task, generators)) for task in tasks)
    monkeypatch.setattr(practice, "pool", lambda _topic, _level: candidates)
    for kind, expected in zip(("expression", "properties", "geometry"), tasks, strict=True):
        issued = practice.issue("complex-numbers", 1, modulus_mode=kind)
        assert issued.record["code"] == expected.code
    with pytest.raises(ValueError):
        practice.issue("complex-numbers", 1, modulus_mode="invalid")


def test_standard_complex_practice_does_not_include_modulus(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.engine import practice
    from app.engine.catalogue import StoredProblem
    from app.engine.rendering import render
    from app.engine.topics.catalogue import topics

    generators = practice._registry()
    topic = topics()["complex-numbers"]
    tasks = [topic.generate(1, seed, generators) for seed in range(30)]
    candidates = tuple(StoredProblem.from_issued(render(task, generators)) for task in tasks)
    assert any(task.generator_version == LocalModulusCircle.version for task in tasks)
    monkeypatch.setattr(practice, "pool", lambda _topic, _level: candidates)
    for index in range(len(candidates)):
        issued = practice.issue("complex-numbers", 1, seed=index)
        assert issued.record["generator_version"] not in {
            LocalModulusCircle.version, LocalModulusPractice.version,
        }


def test_production_topic_contains_each_modulus_kind_and_opens_codes() -> None:
    from app.engine.generators.catalogue import registry
    from app.engine.opening import rebuild
    from app.engine.topics.catalogue import topics

    catalogue = registry()
    topic = topics()["complex-numbers"]
    for level in (1, 2, 3):
        kinds: set[str] = set()
        for seed in range(64):
            task = topic.generate(level, seed, catalogue)
            if task.generator_version == LocalModulusCircle.version:
                kinds.add("geometry")
            elif task.generator_version == LocalModulusPractice.version:
                kinds.add(str(task.metadata["template"]))
        assert kinds == {"expression", "properties", "geometry"}
        for generator, seed in (
            (LocalModulusPractice(), (level - 1) * 10**12),
            (LocalModulusCircle(), (level - 1) * 10**12),
        ):
            task = generator.build(generator.draw(seed))
            opened = rebuild(task.code)
            assert opened.topic == "complex-numbers"
            assert opened.difficulty == level
            assert opened.problem.code == task.code


def test_packaged_modulus_preserves_exact_answers_and_replay() -> None:
    generator = LocalModulusPractice()
    params = ModulusPracticeParameters(seed=0, level=1, mode="expression", a=1, b=2, c=4, d=-1)
    assert generator.build(params).answer.expected == sp.sqrt(26)
    drawn = generator.draw(12345)
    assert generator.build(generator.draw(drawn.seed)).code == generator.build(drawn).code


def test_packaged_circle_has_exact_centre_and_radius() -> None:
    params = CircleParameters(seed=0, level=3, a=2, b=-3, c=3, d=4, scale=2)
    answer = LocalModulusCircle().build(params).answer
    assert tuple(component.expected for component in answer.components) == (
        sp.Integer(1),
        sp.Rational(-3, 2),
        sp.Rational(5, 2),
    )


def test_circle_solution_visual_survives_production_catalogue() -> None:
    from app.engine.catalogue import StoredProblem
    from app.engine.generators.catalogue import registry
    from app.engine.rendering import render

    generator = LocalModulusCircle()
    params = generator.draw(2 * 10**12 + 123)
    issued = render(generator.build(params), registry())
    restored = StoredProblem.from_issued(issued).issued()
    assert restored.visual == {
        "kind": "complex-plane",
        "version": 1,
        "mode": "circle",
        "first": [float(params.center_x), float(params.center_y)],
        "second": None,
        "result": None,
        "power": None,
        "radius": float(params.radius),
    }


def test_production_catalogue_rejects_invalid_complex_diagrams() -> None:
    from app.engine.catalogue import StoredProblem

    with pytest.raises(ValueError):
        StoredProblem(
            code="code", generator_version="version", statement="x", answer_latex="x",
            steps=({"say": "step", "latex": "x"},),
            visual={"kind": "complex-plane", "version": 1, "mode": "circle",
                    "first": [0, 0], "second": None, "result": None, "power": None,
                    "radius": -1},
        )


def test_modulus_diagrams_can_be_rendered_in_worksheets() -> None:
    from app.engine.generators.catalogue import registry
    from app.engine.rendering import render
    from app.services.worksheet_graphs import graph

    for generator in (LocalModulusCircle(), LocalModulusPractice()):
        params = generator.draw(123)
        issued = render(generator.build(params), registry())
        assert "\\begin{picture}" in graph(issued.visual)


def test_modulus_solution_includes_the_relevant_formula_on_reveal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.engine.generators.catalogue import registry
    from app.engine.rendering import render
    from app.visuals import spec

    generator = LocalModulusCircle()
    task = generator.build(generator.draw(123))
    issued = render(task, registry())
    monkeypatch.setattr(spec, "build_visual", lambda _: None)
    payload = spec.solution_payload(issued.steps, issued.record)
    with_rules = [step for step in payload["steps"] if "rules" in step]
    assert len(with_rules) == 1
    assert with_rules[0]["say"] == generator.step_text["distance"]
    assert with_rules[0]["rules"][0]["title"] == "Modulus as distance"
    assert "rules" not in payload["steps"][0]


def test_modulus_generators_accept_full_engine_seed_range_and_replay() -> None:
    for generator in (LocalModulusPractice(), LocalModulusCircle()):
        for seed in (0, 10**12, 10**16 - 1):
            params = generator.draw(seed)
            assert generator.draw(params.seed) == params
            task = generator.build(params)
            assert generator.build(generator.draw(params.seed)).code == task.code
        for invalid in (-1, 10**16, True):
            with pytest.raises(ValueError):
                generator.draw(invalid)


@pytest.mark.parametrize("level", [1, 2, 3])
@pytest.mark.parametrize("mode", ["expression", "properties", "geometry"])
def test_modulus_selection_preserves_requested_level_and_kind(level: int, mode: str) -> None:
    from app.engine.algebra_practice.selection import modulus_selection
    from local_matrix_preview import _registry

    version, seed = modulus_selection(level, mode, 123)
    params = _registry().get(version).draw(seed)
    assert params.level == level
    if mode == "geometry":
        assert version == LocalModulusCircle.version
    else:
        assert version == LocalModulusPractice.version
        assert params.mode == mode


@pytest.mark.parametrize(
    "level,mode,variation",
    [
        (0, "expression", 0),
        (1, "invalid", 0),
        (1, "geometry", -1),
        (True, "geometry", 1),
        (1, "geometry", 10**12),
    ],
)
def test_modulus_selection_rejects_invalid_input(level: int, mode: str, variation: int) -> None:
    from app.engine.algebra_practice.selection import modulus_selection

    with pytest.raises(ValueError):
        modulus_selection(level, mode, variation)
