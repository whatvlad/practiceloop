"""Private, release-local verified pools (#192). Build before activating a release.

Run ``python -m app.engine.catalogue`` from backend/. Requests only load and pick
rendered data; they never build a missing pool or fall back to a generator.
"""

from __future__ import annotations

import logging
from copy import deepcopy
from functools import cache
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.engine.codes import format_code, parse_code
from app.engine.generators.catalogue import registry
from app.engine.registry import Registry
from app.engine.rendering import Issued, render
from app.engine.topics.catalogue import Topic, topics

logger = logging.getLogger(__name__)
POOL_SIZE = 64
ATTEMPTS_PER_SLOT = 4
CATALOGUE_PATH = Path(__file__).resolve().parents[2] / ".engine-catalogue.json"


class StoredModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class StoredStep(StoredModel):
    say: str = Field(min_length=1)
    latex: str = Field(min_length=1)


class StoredProblem(StoredModel):
    code: str
    generator_version: str
    statement: str = Field(min_length=1)
    answer_latex: str = Field(min_length=1)
    steps: tuple[StoredStep, ...] = Field(min_length=1)
    visual: dict[str, Any] | None = None

    @field_validator("visual")
    @classmethod
    def valid_visual(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        from app.visuals.plot2d import validate_plot

        return validate_plot(value)

    @classmethod
    def from_issued(cls, issued: Issued) -> StoredProblem:
        return cls(
            code=str(issued.record["code"]),
            generator_version=str(issued.record["generator_version"]),
            statement=issued.statement,
            answer_latex=issued.answer_latex,
            steps=tuple(StoredStep(**step) for step in issued.steps),
            visual=issued.visual,
        )

    def issued(self) -> Issued:
        # Fresh containers: callers cannot mutate the cached private catalogue.
        return Issued(
            self.statement,
            {"generator_version": self.generator_version, "code": self.code},
            self.answer_latex,
            tuple({"say": step.say, "latex": step.latex} for step in self.steps),
            deepcopy(self.visual),
        )


class StoredCell(StoredModel):
    topic: str
    level: int = Field(ge=1, le=5)
    problems: tuple[StoredProblem, ...]


class Catalogue(StoredModel):
    format_version: Literal[1] = 1
    pool_size: int = Field(ge=1)
    cells: tuple[StoredCell, ...]

    def validate_cells(self, entries: dict[str, Topic], generators: Registry) -> None:
        expected = {(slug, level) for slug, topic in entries.items() for level in topic.levels}
        actual = [(cell.topic, cell.level) for cell in self.cells]
        if set(actual) != expected or len(actual) != len(expected):
            raise ValueError("Catalogue cells differ from the engine topics")
        for cell in self.cells:
            versions = {c.generator for c in entries[cell.topic].levels[cell.level]}
            if (
                len(cell.problems) != self.pool_size
                or len({p.code for p in cell.problems}) != self.pool_size
            ):
                raise ValueError(f"Incomplete catalogue pool: {cell.topic} level {cell.level}")
            for problem in cell.problems:
                code = parse_code(problem.code, generators)
                if (
                    format_code(code, generators) != problem.code
                    or generators.get_code(code.prefix, code.version).version
                    != problem.generator_version
                    or problem.generator_version not in versions
                ):
                    raise ValueError("Catalogue code and generator differ")


def build(
    entries: dict[str, Topic] | None = None,
    generators: Registry | None = None,
    *,
    pool_size: int = POOL_SIZE,
) -> Catalogue:
    """Bounded, deterministic build of every declared cell, including unserved topics.

    Generators verify their mathematics in build(). Failed candidates are skipped
    within a finite cap; an unfillable cell aborts the entire catalogue.
    """
    if type(pool_size) is not int or pool_size < 1:
        raise ValueError("Pool size must be positive")
    entries = topics() if entries is None else entries
    generators = registry() if generators is None else generators
    cells = []
    for slug, topic in entries.items():
        for level in sorted(topic.levels):
            problems: dict[str, StoredProblem] = {}
            for seed in range(pool_size * ATTEMPTS_PER_SLOT):
                try:
                    task = topic.generate(level, seed, generators)
                except ValueError:
                    logger.warning("Catalogue rejected %s level %d seed %d", slug, level, seed)
                    continue
                problem = StoredProblem.from_issued(render(task, generators))
                problems.setdefault(problem.code, problem)
                if len(problems) == pool_size:
                    break
            if len(problems) != pool_size:
                raise ValueError(f"Cannot fill catalogue pool: {slug} level {level}")
            cells.append(StoredCell(topic=slug, level=level, problems=tuple(problems.values())))
    result = Catalogue(pool_size=pool_size, cells=tuple(cells))
    result.validate_cells(entries, generators)
    return result


def write(path: Path = CATALOGUE_PATH) -> Catalogue:
    """Publish only a complete file; a failed build leaves the previous file alone."""
    result = build()
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(result.model_dump_json(exclude_none=True), encoding="utf-8")
    temporary.replace(path)
    load.cache_clear()
    return result


@cache
def load() -> Catalogue:
    """Strict structural validation only: no task generation or symbolic work."""
    result = Catalogue.model_validate_json(CATALOGUE_PATH.read_bytes())
    if result.pool_size != POOL_SIZE:
        raise ValueError("Catalogue pool size differs from this release")
    result.validate_cells(topics(), registry())
    return result


def pool(slug: str, level: int) -> tuple[StoredProblem, ...]:
    if type(level) is not int:
        raise ValueError("Unknown topic level")
    for cell in load().cells:
        if (cell.topic, cell.level) == (slug, level):
            return cell.problems
    raise ValueError("Unknown catalogue cell")


def lookup(record: dict[str, object]) -> Issued:
    if set(record) != {"generator_version", "code"}:
        raise ValueError("Invalid new-engine record")
    for cell in load().cells:
        for problem in cell.problems:
            if (
                problem.code == record["code"]
                and problem.generator_version == record["generator_version"]
            ):
                return problem.issued()
    raise ValueError("Record is not in this release's catalogue")


if __name__ == "__main__":
    catalogue = write()
    print(f"Verified engine catalogue: {len(catalogue.cells)} cells x {catalogue.pool_size} codes")
