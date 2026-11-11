"""Private, release-local verified pools (#192). Build before activating a release.

Run ``python -m app.engine.catalogue`` from backend/. Requests only load and pick
rendered data; they never build a missing pool or fall back to a generator.
"""

from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import replace
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


class StoredRule(StoredModel):
    title: str = Field(min_length=1, max_length=120)
    latex: str = Field(min_length=1, max_length=2000)
    explanation: str = Field(min_length=1, max_length=1000)


class StoredStep(StoredModel):
    say: str = Field(min_length=1)
    latex: str = Field(min_length=1)
    visual: dict[str, Any] | None = None
    rules: tuple[StoredRule, ...] = Field(default=(), max_length=4)

    @field_validator("rules", mode="before")
    @classmethod
    def tuple_rules(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @field_validator("visual")
    @classmethod
    def valid_visual(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        from app.visuals.complex_plane import validate_visual

        return validate_visual(value)


class StoredProblem(StoredModel):
    code: str
    generator_version: str
    statement: str = Field(min_length=1)
    answer_latex: str = Field(min_length=1)
    steps: tuple[StoredStep, ...] = Field(min_length=1)
    visual: dict[str, Any] | None = None
    statement_visual: dict[str, Any] | None = None

    @field_validator("visual", "statement_visual")
    @classmethod
    def valid_visual(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        from app.visuals.complex_plane import validate_visual

        return validate_visual(value)

    @classmethod
    def from_issued(cls, issued: Issued) -> StoredProblem:
        return cls(
            code=str(issued.record["code"]),
            generator_version=str(issued.record["generator_version"]),
            statement=issued.statement,
            answer_latex=issued.answer_latex,
            steps=tuple(StoredStep(**step) for step in issued.steps),
            visual=issued.visual,
            statement_visual=issued.statement_visual,
        )

    def issued(self) -> Issued:
        # Fresh containers: callers cannot mutate the cached private catalogue.
        return Issued(
            self.statement,
            {"generator_version": self.generator_version, "code": self.code},
            self.answer_latex,
            tuple(
                {"say": step.say, "latex": step.latex}
                | ({"visual": deepcopy(step.visual)} if step.visual is not None else {})
                | ({"rules": [rule.model_dump() for rule in step.rules]} if step.rules else {})
                for step in self.steps
            ),
            deepcopy(self.visual),
            deepcopy(self.statement_visual),
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
            expanded_matrix = (
                cell.topic == "matrix-operations" and "local-matrix-sized-v1" in versions
            )
            expected_size = self.pool_size + (400 if expanded_matrix else 0)
            if (
                len(cell.problems) != expected_size
                or len({p.code for p in cell.problems}) != expected_size
            ):
                raise ValueError(f"Incomplete catalogue pool: {cell.topic} level {cell.level}")
            if expanded_matrix:
                from app.engine.algebra_practice.catalogue_seeds import matrix_seeds

                actual_seeds = {
                    parse_code(problem.code, generators).seed
                    for problem in cell.problems
                    if problem.generator_version
                    in {"local-matrix-sized-v1", "local-matrix-division-v3"}
                }
                if actual_seeds != set(matrix_seeds(cell.level, 0)) | set(
                    matrix_seeds(cell.level, 1)
                ):
                    raise ValueError("Matrix catalogue settings are incomplete")
            if cell.level <= 3 and self.pool_size >= 16:
                present = {
                    (problem.generator_version, parse_code(problem.code, generators).seed)
                    for problem in cell.problems
                }
                required: set[tuple[str, int]] = set()
                if cell.topic == "matrix-rank" and "local-rank-v1" in versions:
                    from app.engine.algebra_practice.rank import rank_seed

                    required = {
                        ("local-rank-v1", rank_seed(cell.level, rows, cols, 0))
                        for rows in range(2, 6)
                        for cols in range(2, 6)
                    }
                square_version = {
                    "determinants": "local-determinant-v4",
                    "inverse-matrices": "local-inverse-v1",
                    "linear-systems": "local-system-v1",
                }.get(cell.topic)
                if square_version and square_version in versions:
                    from app.engine.algebra_practice.local_determinant_generator import (
                        determinant_seed,
                    )

                    required = {
                        (square_version, determinant_seed(cell.level, size, 0))
                        for size in range(2, 6)
                    }
                if (
                    cell.topic
                    in {
                        "complex-arithmetic",
                        "complex-numbers",
                        "polynomial-division",
                        "complex-conversion",
                        "polynomial-roots",
                        "partial-fractions",
                        "vectors",
                    }
                    or cell.topic == "complex-polar-form"
                ):
                    from app.engine.algebra_practice.catalogue_seeds import mode_seeds

                    modes = mode_seeds(cell.topic, cell.level, 0)
                    if all(version in versions for _, version, _ in modes):
                        required = {(version, seed) for _, version, seed in modes}
                if not required <= present:
                    raise ValueError(
                        f"Catalogue settings incomplete: {cell.topic} level {cell.level}"
                    )
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
            if (
                slug
                in (
                    "complex-arithmetic",
                    "complex-numbers",
                    "polynomial-division",
                    "complex-conversion",
                    "polynomial-roots",
                    "partial-fractions",
                    "complex-polar-form",
                    "vectors",
                )
                and level <= 3
            ):
                from app.engine.algebra_practice.catalogue_seeds import mode_seeds

                local_modes = mode_seeds(slug, level, 0)
                if all(
                    any(c.generator == version for c in topic.levels[level])
                    for _, version, _ in local_modes
                ):
                    count = max(2, pool_size // (len(local_modes) + 1)) if slug == "vectors" else 2
                    for variation in range(count):
                        for _, version, seed in mode_seeds(slug, level, variation):
                            if len(problems) == pool_size:
                                break
                            generator = generators.get(version)
                            task = generator.build(generator.draw(seed))
                            problem = StoredProblem.from_issued(render(task, generators))
                            problems[problem.code] = problem
                    if len(problems) == pool_size:
                        cells.append(
                            StoredCell(topic=slug, level=level, problems=tuple(problems.values()))
                        )
                        continue
                    local_versions = {version for _, version, _ in local_modes}
                    legacy = tuple(
                        c for c in topic.levels[level] if c.generator not in local_versions
                    )
                    if not legacy:
                        variation = 2
                        while len(problems) < pool_size:
                            for _, version, seed in mode_seeds(slug, level, variation):
                                generator = generators.get(version)
                                task = generator.build(generator.draw(seed))
                                problem = StoredProblem.from_issued(render(task, generators))
                                problems.setdefault(problem.code, problem)
                                if len(problems) == pool_size:
                                    break
                            variation += 1
                        cells.append(
                            StoredCell(topic=slug, level=level, problems=tuple(problems.values()))
                        )
                        continue
                    topic = replace(topic, levels={**topic.levels, level: legacy})
            local_version = {
                "determinants": "local-determinant-v4",
                "inverse-matrices": "local-inverse-v1",
                "linear-systems": "local-system-v1",
            }.get(slug)
            if local_version and any(
                choice.generator == local_version for choice in topic.levels[level]
            ):
                from app.engine.algebra_practice.local_determinant_generator import determinant_seed

                generator = generators.get(local_version)
                for variation in (0, 1):
                    for size in range(2, 6):
                        if len(problems) == pool_size:
                            break
                        seed = determinant_seed(level, size, variation)
                        task = generator.build(generator.draw(seed))
                        problem = StoredProblem.from_issued(render(task, generators))
                        problems[problem.code] = problem
                if len(problems) == pool_size:
                    cells.append(
                        StoredCell(topic=slug, level=level, problems=tuple(problems.values()))
                    )
                    continue
                legacy = tuple(
                    choice for choice in topic.levels[level] if choice.generator != local_version
                )
                topic = replace(topic, levels={**topic.levels, level: legacy})
            expanded_matrix = slug == "matrix-operations" and any(
                c.generator == "local-matrix-sized-v1" for c in topic.levels[level]
            )
            if expanded_matrix:
                legacy = tuple(
                    c for c in topic.levels[level] if not c.generator.startswith("local-matrix-")
                )
                topic = replace(topic, levels={**topic.levels, level: legacy})
            if slug == "matrix-rank" and any(
                choice.generator == "local-rank-v1" for choice in topic.levels[level]
            ):
                from app.engine.algebra_practice.rank import rank_seed

                generator = generators.get("local-rank-v1")
                old_choices = tuple(
                    choice for choice in topic.levels[level] if choice.generator != "local-rank-v1"
                )
                count = min(32, pool_size) if old_choices else pool_size
                for index in range(count):
                    rows, columns = 2 + index % 16 // 4, 2 + index % 4
                    seed = rank_seed(level, rows, columns, index // 16)
                    task = generator.build(generator.draw(seed))
                    problem = StoredProblem.from_issued(render(task, generators))
                    problems[problem.code] = problem
                if not old_choices or len(problems) == pool_size:
                    cells.append(
                        StoredCell(topic=slug, level=level, problems=tuple(problems.values()))
                    )
                    continue
                topic = replace(topic, levels={**topic.levels, level: old_choices})
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
            if expanded_matrix:
                from app.engine.algebra_practice.catalogue_seeds import matrix_seeds
                from app.engine.algebra_practice.local_matrix_generator import (
                    OPERATIONS,
                    VARIATIONS,
                )

                for variation in (0, 1):
                    for seed in matrix_seeds(level, variation):
                        operation = OPERATIONS[(seed // VARIATIONS) // (3 * 5**4)]
                        version = (
                            "local-matrix-division-v3"
                            if operation == "divide" and level > 1
                            else "local-matrix-sized-v1"
                        )
                        generator = generators.get(version)
                        task = generator.build(generator.draw(seed))
                        problem = StoredProblem.from_issued(render(task, generators))
                        problems[problem.code] = problem
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
    print(
        f"Verified engine catalogue: {len(catalogue.cells)} cells, "
        f"{sum(len(cell.problems) for cell in catalogue.cells)} codes"
    )
