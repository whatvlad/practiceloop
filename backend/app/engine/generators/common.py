"""Shared seed parameters and code formatting for slice generators."""

from typing import Any

from pydantic import Field

from app.engine.codes import ProblemCode, format_code
from app.engine.models import Parameters, TaskGenerator
from app.engine.registry import Registry


class Seed(Parameters):
    seed: int = Field(ge=0, lt=10**16)


def code(generator: TaskGenerator[Any], prefix: str, family: str, seed: int) -> str:
    registry = Registry()
    registry.register(generator)
    registry.register_code(prefix, family, 1, generator.version)
    return format_code(ProblemCode(prefix, 1, seed), registry)
