"""The new core is usable without connecting it to the existing practice API."""

from dataclasses import dataclass
from typing import ClassVar

import pytest
from pydantic import ValidationError

from app.engine.models import Answer, Outcome, Parameters, Step, Task, TaskGenerator
from app.engine.registry import Registry
from app.services.math_parser import MathNode, parse_math_input


class TinyParams(Parameters):
    number: int


@dataclass(frozen=True)
class TinyAnswer:
    kind: ClassVar[str] = "number"
    value: int

    def latex(self) -> str:
        return str(self.value)

    def check(self, tree: MathNode) -> Outcome:
        return "correct" if tree.kind == "number" and tree.value == (self.value, 1) else "incorrect"


class TinyGenerator:
    version = "tiny-v1"
    params = TinyParams
    answer = TinyAnswer

    def __init__(self, requires: tuple[str, ...] = (), version: str = "tiny-v1") -> None:
        self.version = version
        self.requires = requires

    def draw(self, seed: int) -> TinyParams:
        return TinyParams(number=seed)

    def build(self, params: TinyParams) -> Task:
        return Task(
            statement="Give the number.",
            steps=(Step(text_key="read_number", latex=str(params.number)),),
            answer=TinyAnswer(params.number),
            metadata={"difficulty": 1},
            code="test-only",
            generator_version=self.version,
        )


def test_generator_consumer_and_parameter_validation() -> None:
    generator: TaskGenerator[TinyParams] = TinyGenerator()
    registry = Registry()
    registry.register(generator)
    registry.validate_dependencies()
    stored = registry.get("tiny-v1")
    task = stored.build(stored.draw(3))
    answer: Answer = task.answer
    assert answer.latex() == "3"
    assert answer.check(parse_math_input("3")) == "correct"
    assert answer.check(parse_math_input("4")) == "incorrect"
    assert task.steps == (Step(text_key="read_number", latex="3"),)
    assert task.generator_version == "tiny-v1"
    with pytest.raises(ValidationError):
        TinyParams.model_validate({"number": "3"})
    with pytest.raises(ValidationError):
        TinyParams(number=3).number = 4
    with pytest.raises(ValidationError):
        TinyParams.model_validate({"number": 3, "extra": 1})


def test_registry_rejects_duplicate_unknown_and_invalid_metadata() -> None:
    registry = Registry()
    registry.register(TinyGenerator())
    with pytest.raises(ValueError, match="Duplicate generator"):
        registry.register(TinyGenerator())
    with pytest.raises(ValueError, match="Unknown generator"):
        registry.get("missing-v1")
    with pytest.raises(ValueError, match="version"):
        registry.register(TinyGenerator(version=" "))
    with pytest.raises(ValueError, match="Duplicate dependency"):
        registry.register(TinyGenerator(requires=("tiny-v1", "tiny-v1"), version="other-v1"))
    invalid = TinyGenerator(version="invalid-v1")
    invalid.answer = object  # type: ignore[assignment]
    with pytest.raises(ValueError, match="answer metadata"):
        registry.register(invalid)
    invalid_params = TinyGenerator(version="invalid-v1")
    invalid_params.params = object  # type: ignore[assignment]
    with pytest.raises(ValueError, match="parameters"):
        registry.register(invalid_params)


def test_dependency_graph_accepts_shared_dependency_and_rejects_missing_and_cycles() -> None:
    registry = Registry()
    registry.register(TinyGenerator(("base-v1",), "left-v1"))
    with pytest.raises(ValueError, match="Unknown generator"):
        registry.validate_dependencies()
    registry.register(TinyGenerator(version="base-v1"))
    registry.register(TinyGenerator(("base-v1",), "right-v1"))
    registry.register(TinyGenerator(("left-v1", "right-v1"), "top-v1"))
    registry.validate_dependencies()

    cyclic = Registry()
    cyclic.register(TinyGenerator(("b-v1",), "a-v1"))
    cyclic.register(TinyGenerator(("a-v1",), "b-v1"))
    with pytest.raises(ValueError, match="Circular dependency"):
        cyclic.validate_dependencies()
