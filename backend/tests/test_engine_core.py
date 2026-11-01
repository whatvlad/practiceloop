"""The new core is usable without connecting it to the existing practice API."""

from dataclasses import dataclass
from typing import ClassVar

import pytest
from pydantic import ValidationError

from app.engine.models import Answer, Drawn, Outcome, Step, Task, TaskGenerator
from app.engine.registry import Registry
from app.services.math_parser import MathNode, parse_math_input


class TinyParams(Drawn):
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
    params = TinyParams
    answer = TinyAnswer
    step_text = {"read_number": "Read the number."}

    def __init__(
        self,
        requires: tuple[str, ...] = (),
        version: str = "tiny-v1",
        prefix: str | None = None,
        family: str | None = None,
        code_version: int = 1,
    ) -> None:
        self.version = version
        self.requires = requires
        # Each test generator gets its own family unless a test shares one.
        name = version.rsplit("-v", 1)[0]
        self.family = family or name
        self.prefix = prefix or "T" + "".join(char for char in name.upper() if char.isalpha())[:7]
        self.code_version = code_version

    def draw(self, seed: int) -> TinyParams:
        return TinyParams(seed=seed, number=seed)

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
        TinyParams.model_validate({"seed": 3, "number": "3"})
    with pytest.raises(ValidationError):
        TinyParams(seed=3, number=3).number = 4
    with pytest.raises(ValidationError):
        TinyParams.model_validate({"seed": 3, "number": 3, "extra": 1})
    with pytest.raises(ValidationError):
        TinyParams.model_validate({"seed": 10**16, "number": 3})


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
    no_text = TinyGenerator(version="no-text-v1")
    no_text.step_text = {"read_number": " "}  # type: ignore[assignment]
    with pytest.raises(ValueError, match="step text"):
        registry.register(no_text)


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
