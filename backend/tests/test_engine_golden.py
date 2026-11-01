"""#170: golden problems, code replay and a seed sweep for the new generator engine.

The golden fixture pins sample codes of every generator version to their
statement, steps and answer. A shipped version never changes its output, so a
SymPy, Python or engine change that alters one of them fails here. A new
generator version adds its own entries; an existing entry is never rewritten.
"""

import json
from functools import cache
from pathlib import Path
from typing import Any

import pytest

from app.engine.answers import _symbolic
from app.engine.codes import parse_code
from app.engine.generators import indefinite
from app.engine.generators.catalogue import registry
from app.engine.models import Task
from app.engine.topics.catalogue import topics

GOLDEN = json.loads(
    (Path(__file__).parent / "fixtures" / "engine_golden_v1.json").read_text(encoding="utf-8")
)
SWEEP_SEEDS = range(1000)
# The rational families have few distinct functions, so most sweep seeds repeat
# an antiderivative check; caching this pure check keeps the sweep within CI time.
_cached_is_primitive = cache(_symbolic.is_primitive)


def snapshot(task: Task) -> dict[str, Any]:
    return {
        "code": task.code,
        "statement": task.statement,
        "steps": [[step.text_key, step.latex] for step in task.steps],
        "answer_kind": task.answer.kind,
        "answer_latex": task.answer.latex(),
        "metadata": dict(task.metadata),
    }


def rebuild(code: str) -> Task:
    generators = registry()
    parsed = parse_code(code, generators)
    generator = generators.get_code(parsed.prefix, parsed.version)
    return generator.build(generator.draw(parsed.seed))


def test_every_generator_version_has_golden_problems() -> None:
    # Registry has no public listing; the private map is the set of shipped versions.
    assert set(GOLDEN) == set(registry()._generators)
    for version, items in GOLDEN.items():
        assert len(items) >= 3, version
        assert len({item["code"] for item in items}) == len(items), version


@pytest.mark.parametrize(
    "version, expected", [(v, item) for v, items in GOLDEN.items() for item in items]
)
def test_golden_code_rebuilds_its_pinned_problem(version: str, expected: dict[str, Any]) -> None:
    task = rebuild(expected["code"])
    assert task.generator_version == version
    assert snapshot(task) == expected


@pytest.mark.parametrize("version", sorted(GOLDEN))
def test_the_same_code_gives_the_same_task_in_any_spelling(version: str) -> None:
    code = GOLDEN[version][0]["code"]
    task = rebuild(code)
    assert rebuild(code) == task
    for spelling in (code.lower(), code.replace("-", " "), code.replace("-", "")):
        assert rebuild(spelling) == task


def test_dependency_graph_and_topic_views_are_valid() -> None:
    generators = registry()
    generators.validate_dependencies()
    for topic in topics().values():
        for choices in topic.levels.values():
            for choice in choices:
                generators.get(choice.generator)
                if choice.wrapper is not None:
                    assert choice.generator in generators.get(choice.wrapper).requires


@pytest.mark.parametrize(
    "slug, level", [(slug, level) for slug, topic in topics().items() for level in topic.levels]
)
def test_every_topic_level_gives_a_valid_problem_for_every_swept_seed(
    slug: str, level: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(indefinite, "is_primitive", _cached_is_primitive)
    generators = registry()
    topic = topics()[slug]
    versions = {choice.wrapper or choice.generator for choice in topic.levels[level]}
    for seed in SWEEP_SEEDS:
        # A seed that exhausts the 64-draw cap, or a generator that rejects its own
        # parameters, raises ValueError here and fails the sweep.
        task = topic.generate(level, seed, generators)
        assert task.generator_version in versions
        assert task.answer.kind == generators.get(task.generator_version).answer.kind
        assert task.statement and task.steps and task.answer.latex()
        code = parse_code(task.code, generators)
        assert generators.get_code(code.prefix, code.version).version == task.generator_version
