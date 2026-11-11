"""Cross-family replay and exact-answer sweep under the project's seed cap."""

import json

import sympy as sp
from seed_sweep import sweep

from app.engine import practice
from app.engine.algebra_practice.catalogue_seeds import mode_seeds
from app.engine.generators.catalogue import registry
from app.engine.opening import rebuild
from app.math_input import parse_answer_input
from app.services.math_worker import MAX_OUTPUT_BYTES
from app.visuals.complex_plane import validate_visual


def _scalar(value):
    return sp.sstr(value).replace("**", "^")


def test_geometry_modes_replay_check_exact_answers_and_bound_worker_payloads() -> None:
    generators = registry()
    seen = set()
    modes = mode_seeds("vectors", 1, 0)
    for index in sweep(1000):
        level = index // len(modes) % 3 + 1
        variation = index // (len(modes) * 3)
        mode, version, seed = mode_seeds("vectors", level, variation)[index % len(modes)]
        generator = generators.get(version)
        task = generator.build(generator.draw(seed))
        opened = rebuild(task.code)
        assert (opened.topic, opened.difficulty) == ("vectors", level)
        issued = opened.problem.issued()
        assert practice.public_settings(issued.record) == {"exerciseMode": mode}
        assert issued.statement_visual is not None
        validate_visual(issued.statement_visual)
        assert all(step.get("visual") and step.get("rules") for step in issued.steps)
        assert "answer" not in json.dumps(issued.statement_visual).lower()
        assert len(opened.model_dump_json().encode()) <= MAX_OUTPUT_BYTES
        answer = task.answer
        if answer.kind == "tuple":
            source = "(" + ";".join(_scalar(part.expected) for part in answer.components) + ")"
        elif answer.kind == "finite_set":
            source = "{" + ",".join(_scalar(value) for value in answer.expected) + "}"
        else:
            source = _scalar(answer.expected)
        tree = parse_answer_input(
            source, answer.kind, contract=practice.input_contract(issued.record)
        )
        assert answer.check(tree) == "correct"
        seen.add((mode, level))
    assert len(seen) == 3 * len(modes)
