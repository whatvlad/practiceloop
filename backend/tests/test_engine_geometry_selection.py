"""Selection uses the normal private catalogue and keeps settings reproducible."""

import re
from dataclasses import replace

import pytest

from app.engine import catalogue, practice
from app.engine.algebra_practice.catalogue_seeds import mode_seeds
from app.engine.generators.catalogue import registry
from app.engine.opening import rebuild
from app.engine.topics.catalogue import topics


@pytest.mark.parametrize("level", (1, 2, 3))
def test_each_vector_mode_is_available_and_opens_at_its_level(level, monkeypatch) -> None:
    topic = topics()["vectors"]
    entries = {"vectors": replace(topic, levels={level: topic.levels[level]})}
    prepared = catalogue.build(entries=entries, generators=registry(), pool_size=16)
    monkeypatch.setattr(practice, "pool", lambda slug, difficulty: prepared.cells[0].problems)
    assert {mode for mode, _, _ in mode_seeds("vectors", level, 0)} == {
        "vector-expression",
        "scalar-expression",
        "vector-length",
        "perpendicular-parameter",
        "triangle-angle",
        "triangle-area",
        "parallelogram-area",
        "tetrahedron-volume",
        "tetrahedron-height",
        "parallelepiped-area",
    }
    for mode in (
        "vector-expression",
        "scalar-expression",
        "vector-length",
        "perpendicular-parameter",
        "triangle-angle",
        "triangle-area",
        "parallelogram-area",
        "tetrahedron-volume",
        "tetrahedron-height",
        "parallelepiped-area",
    ):
        issued = practice.issue("vectors", level, seed=0, exercise_mode=mode)
        assert re.fullmatch(r"\\text\{[^{}]+: \}.*\\text\{\.\}", issued.statement)
        assert practice.public_settings(issued.record) == {"exerciseMode": mode}
        opened = rebuild(str(issued.record["code"]))
        assert (opened.topic, opened.difficulty) == ("vectors", level)
        assert opened.problem.issued().statement == issued.statement
