"""Reusable extension through catalogue, public projections and private reveal."""

import sys
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
import sympy as sp

from app.api import codes, practice
from app.engine import catalogue
from app.engine import practice as engine
from app.engine.answers.computational import FormulaAnswer, OrderedAnswer, RealSetAnswer
from app.engine.codes import encode, parse_code
from app.engine.models import Drawn, Step, Task
from app.engine.opening import rebuild
from app.engine.registry import Registry
from app.engine.rendering import render
from app.engine.topics.catalogue import Choice, Topic
from app.math_input.contracts import InputContract
from app.services import math_worker
from app.services.owned_records import ProblemRecord
from app.services.worksheet_graphs import graph
from app.visuals.plot2d import validate_plot
from app.visuals.spec import _build, build_visual, solution_payload


def diagram(seed):
    a = 1 + seed % 3
    return {
        "kind": "plot2d",
        "version": 1,
        "title": "Tangent geometry",
        "description": "The tangent and its point use the sampled parameters.",
        "x": [0, 4],
        "y": [0, 12],
        "xLabel": "x",
        "yLabel": "height",
        "paths": [
            {"label": "Tangent", "points": [[0, 0], [4, 4 * a]], "closed": False, "arrow": False}
        ],
        "points": [{"label": "Contact", "x": 1, "y": a, "included": True}],
    }


class Example:
    version = "computational-test-v1"
    family = "computational-test"
    prefix = "CPT"
    code_version = 1
    params = Drawn
    answer = OrderedAnswer
    requires = ()
    step_text = {"result": "Compute both coordinates."}

    def draw(self, seed):
        return Drawn(seed=seed)

    def input_contract(self, params):
        return InputContract(
            "tuple",
            components=(InputContract("formula"),) * 2,
            labels=("First coordinate", "Second coordinate"),
        )

    def build(self, params):
        a = 1 + params.seed % 3
        return Task(
            r"Find the ordered point \((1,y)\) with \(y=" + str(a) + r"\).",
            (Step("result", rf"(1,{a})"),),
            OrderedAnswer(
                (FormulaAnswer(1), FormulaAnswer(a)), ("First coordinate", "Second coordinate")
            ),
            {},
            encode(self.prefix, 1, params.seed),
            self.version,
        )

    def solution_visual(self, params):
        return diagram(params.seed)


@pytest.fixture
def extension(monkeypatch):
    g = Example()
    registered = Registry()
    registered.register(g)
    topic = Topic(
        "functions-and-sequences",
        "mathematical-analysis",
        {1: (Choice(g.version),)},
        1,
        title="Functions and sequences",
        space_cm=4,
    )
    entries = {topic.slug: topic}
    stored = catalogue.build(entries, registered, pool_size=3)
    monkeypatch.setattr(engine, "_registry", lambda: registered)
    monkeypatch.setattr(engine, "ENGINE_TOPICS", {**engine.ENGINE_TOPICS, **entries})
    monkeypatch.setattr(catalogue, "load", lambda: stored)
    _build.cache_clear()
    codes._opened.cache_clear()
    codes.lookup_limit.reset()
    yield g, registered, topic, stored
    _build.cache_clear()
    codes._opened.cache_clear()


def test_catalogue_replay_copy_projection_and_reveal_use_same_variant(extension, monkeypatch):
    g, registered, topic, stored = extension
    for seed in range(3):
        task = topic.generate(1, seed, registered)
        sampled_seed = parse_code(task.code, registered).seed
        issued = render(task, registered)
        assert stored.cells[0].problems[seed].issued() == issued
        assert engine.replay(issued.record) == task
        opened = rebuild(task.code)
        monkeypatch.setattr(
            codes, "open_problem_code", lambda _, opened=opened: opened.model_dump_json().encode()
        )
        public = codes.lookup(task.code)
        assert set(public["problem"]) == {"topic", "difficulty", "problemLatex", "answerInput"}
        assert public["problem"]["answerInput"] == g.input_contract(g.draw(seed)).public()
        saved = practice._public_problem(
            ProblemRecord(
                uuid4(),
                topic.slug,
                1,
                issued.statement,
                datetime.now(UTC),
                False,
                False,
                generator_data=issued.record,
            ),
            None,
        )
        assert saved["answerInput"] == public["problem"]["answerInput"]
        assert not ({"visual", "answer_latex", "steps", "generator_data"} & saved.keys())
        payload = solution_payload(issued.steps, issued.record)
        assert payload["visual"] == validate_plot(diagram(sampled_seed))
        assert payload["steps"] == list(issued.steps)
        assert "pdfliteral" in graph(payload["visual"])
        payload["visual"]["points"][0]["y"] = 999
        assert build_visual(issued.record)["points"][0]["y"] == 1 + sampled_seed % 3
        # The catalogue and reveal must NOT call a symbolic builder again.
        with monkeypatch.context() as patch:
            patch.setattr(
                g, "solution_visual", lambda _: pytest.fail("Visual regenerated on reveal")
            )
            assert engine.pooled(issued.record).visual == validate_plot(diagram(sampled_seed))
            assert build_visual(issued.record) == validate_plot(diagram(sampled_seed))


def test_contract_mismatch_fails_before_catalogue_publication(extension, monkeypatch):
    g, registered, topic, _ = extension
    task = topic.generate(1, 0, registered)
    monkeypatch.setattr(g, "input_contract", lambda _: InputContract("real_set"))
    with pytest.raises(ValueError, match="contract differ"):
        render(task, registered)
    wrong = replace(task, answer=RealSetAnswer(sp.S.Reals))
    with pytest.raises(ValueError):
        render(wrong, registered)


def test_contract_used_before_worker_and_checked_inside(extension, monkeypatch):
    g, registered, topic, _ = extension
    record = render(topic.generate(1, 1, registered), registered).record
    calls = []
    monkeypatch.setattr(math_worker, "_run_worker", lambda *args: calls.append(args) or b"correct")
    assert math_worker.check_answer("(1;2)", record).result == "correct"
    assert len(calls) == 1
    assert math_worker.check_answer("{1,2}", record).result == "invalid"
    assert len(calls) == 1


@pytest.mark.parametrize("damage", ["extra", "nan", "huge", "closure", "coordinates", "label"])
def test_visual_payload_is_bounded_and_strict(damage):
    data = diagram(0)
    if damage == "extra":
        data["expected"] = 123
    elif damage == "nan":
        data["x"][0] = float("nan")
    elif damage == "huge":
        data["paths"][0]["points"] *= 100
    elif damage == "closure":
        data["paths"][0]["closed"] = "false"
    elif damage == "coordinates":
        data["points"][0]["x"] = 9
    else:
        data["title"] = r"\input{secret}"
    with pytest.raises(ValueError):
        validate_plot(data)


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Requires Linux resource limits")
def test_new_contract_replays_in_real_limited_child():
    from app.engine import generators as package
    from app.engine.generators.catalogue import registry

    filename = "worker_contract_example"
    path = Path(package.__file__).parent / (filename + ".py")
    assert not path.exists(), "Preserve any pre-existing provider"
    source = Path(__file__).parent / "fixtures/computational_provider.py"
    try:
        path.write_text(source.read_text(), encoding="utf-8")
        registered = registry()
        generator = registered.get("worker-contract-example-v1")
        task = generator.build(generator.draw(234))
        record = {"generator_version": generator.version, "code": task.code}
        engine._registry.cache_clear()
        assert math_worker.check_answer("(R\\{0};a*x+a)", record).result == "correct"
        assert math_worker.check_answer("((-inf,0) U (0,inf);a*(x+1))", record).result == "correct"
        assert math_worker.check_answer("(R;a*x+a)", record).result == "incorrect"
        assert math_worker.check_answer("(R\\{0};a*x+a+0/(x-2))", record).result == "invalid"
        assert math_worker.CPU_SECONDS == 2 and math_worker.ADDRESS_SPACE_BYTES == 256 * 1024 * 1024
    finally:
        path.unlink(missing_ok=True)
        sys.modules.pop("app.engine.generators." + filename, None)
        engine._registry.cache_clear()
