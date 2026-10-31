"""Private task and parameter types shared by new-engine generators."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict

from app.services.math_parser import MathNode

type Outcome = Literal["correct", "incorrect", "missing_constant", "invalid", "inconclusive"]


class Answer(Protocol):
    @property
    def kind(self) -> str: ...

    def latex(self) -> str: ...

    def check(self, tree: MathNode) -> Outcome: ...


class Parameters(BaseModel):
    """Base for validated, immutable generator-specific parameters."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")


@dataclass(frozen=True, slots=True)
class Step:
    text_key: str
    latex: str


@dataclass(frozen=True, slots=True)
class Task:
    statement: str
    steps: tuple[Step, ...]
    answer: Answer
    metadata: Mapping[str, str | int]
    code: str
    generator_version: str


class TaskGenerator[P: Parameters](Protocol):
    @property
    def version(self) -> str: ...

    @property
    def params(self) -> type[P]: ...

    @property
    def answer(self) -> type[Answer]: ...

    @property
    def requires(self) -> tuple[str, ...]: ...

    def draw(self, seed: int) -> P: ...

    def build(self, params: P) -> Task: ...
