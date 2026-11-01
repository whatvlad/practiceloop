"""Private task and parameter types shared by new-engine generators.

`Answer`, `Outcome`, `Task` and `TaskGenerator` are frozen since #189; changing
them needs an ADR-008 amendment.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

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


class Drawn(Parameters):
    """Parameters a generator drew from a seed; the seed becomes the problem code."""

    seed: int = Field(ge=0, lt=10**16)


@dataclass(frozen=True, slots=True)
class Step:
    text_key: str
    latex: str


@dataclass(frozen=True, slots=True)
class Task:
    statement: str
    steps: tuple[Step, ...]
    answer: Answer
    # Display and test data only; no generator or topic reads another task's metadata.
    metadata: Mapping[str, str | int]
    code: str
    generator_version: str


class TaskGenerator[P: Drawn](Protocol):
    """A versioned generator: `draw` makes all PRNG calls, `build` is pure over them."""

    @property
    def version(self) -> str: ...

    @property
    def prefix(self) -> str: ...

    @property
    def family(self) -> str: ...

    @property
    def code_version(self) -> int: ...

    @property
    def params(self) -> type[P]: ...

    @property
    def answer(self) -> type[Answer]: ...

    @property
    def requires(self) -> tuple[str, ...]: ...

    @property
    def step_text(self) -> Mapping[str, str]: ...

    def draw(self, seed: int) -> P: ...

    def build(self, params: P) -> Task: ...
