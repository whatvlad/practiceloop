"""Serve new-engine topics through the practice API (#169).

The private record of a new-engine problem is its problem code and generator
version only; the task is rebuilt from the code whenever the answer is checked,
so the stored code alone reproduces the problem. Nothing here crosses the public
API except the statement, and, after a reveal, the answer and solution steps.
"""

import secrets
from functools import cache
from typing import Any

from app.engine.catalogue import lookup
from app.engine.catalogue import pool as pool
from app.engine.codes import parse_code
from app.engine.generators.catalogue import registry
from app.engine.models import Outcome, Task
from app.engine.registry import Registry
from app.engine.rendering import Issued, render
from app.engine.rendering import statement_latex as statement_latex
from app.engine.topics.catalogue import Topic, topics
from app.services.math_parser import MathNode

# Public topic slug -> its served engine entry (#191), derived from the topic catalogue;
# never edit it by hand. Other public topics stay on the old engine.
ENGINE_TOPICS: dict[str, Topic] = {slug: t for slug, t in topics().items() if t.served}


@cache
def _registry() -> Registry:
    return registry()


def levels(slug: str) -> tuple[int, ...]:
    return tuple(sorted(ENGINE_TOPICS[slug].levels))


def visual(version: str) -> str | None:
    """The visual its served topics declare for a generator version; one per version."""
    declared = {
        topic.visual
        for topic in ENGINE_TOPICS.values()
        for choices in topic.levels.values()
        for choice in choices
        if choice.generator == version
    }
    if len(declared) > 1:
        raise ValueError(f"Served topics declare different visuals for {version}")
    return next(iter(declared), None)


def _public(task: Task) -> Issued:
    return render(task, _registry())


def issue(slug: str, level: int, seed: int | None = None) -> Issued:
    """Pick rendered private data; even a cold symbolic cell runs no SymPy."""
    topic = ENGINE_TOPICS[slug]
    if type(level) is not int or level not in topic.levels:
        raise ValueError("Unknown topic level")
    candidates = pool(slug, level)
    chosen = secrets.randbelow(len(candidates)) if seed is None else seed % len(candidates)
    return candidates[chosen].issued()


def pooled(record: dict[str, object]) -> Issued:
    """Read the rendered fields for a worksheet pick without rebuilding its task."""
    return lookup(record)


def is_engine_record(record: Any) -> bool:
    return isinstance(record, dict) and "code" in record


def replay(record: dict[str, object]) -> Task:
    """Rebuild the task from its stored code; raise ValueError for an unusable record."""
    if set(record) != {"generator_version", "code"} or not isinstance(record["code"], str):
        raise ValueError("Invalid new-engine record")
    code = parse_code(record["code"], _registry())
    generator = _registry().get_code(code.prefix, code.version)
    if generator.version != record["generator_version"]:
        raise ValueError("Record version differs from its code")
    task = generator.build(generator.draw(code.seed))
    if task.code != record["code"]:
        raise ValueError("Rebuilt task has a different code")
    return task


def public_replay(record: dict[str, object]) -> Issued:
    return _public(replay(record))


def check(record: dict[str, object], tree: MathNode) -> Outcome:
    return replay(record).answer.check(tree)
