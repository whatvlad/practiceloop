"""Serve new-engine topics through the practice API (#169).

The private record of a new-engine problem is its problem code and generator
version only; the task is rebuilt from the code whenever the answer is checked,
so the stored code alone reproduces the problem. Nothing here crosses the public
API except the statement, and, after a reveal, the answer and solution steps.
"""

import re
import secrets
from dataclasses import dataclass
from functools import cache
from typing import Any

from app.engine.codes import parse_code
from app.engine.generators.catalogue import registry
from app.engine.models import Outcome, Task
from app.engine.registry import Registry
from app.engine.topics.catalogue import Topic, topics
from app.services.math_parser import MathNode

# Public topic slug -> new-engine topic slug. Other public topics stay on the old engine.
ENGINE_TOPICS = {"combinations": "combinations"}

# Learner-facing text for each step key the served generators use.
STEP_TEXT = {"combinations": "Evaluate the binomial coefficient."}

_INLINE_MATH = re.compile(r"\\\((.*?)\\\)", re.DOTALL)


@dataclass(frozen=True, slots=True)
class Issued:
    statement: str
    record: dict[str, object]
    answer_latex: str
    steps: tuple[dict[str, str], ...]


@cache
def _registry() -> Registry:
    return registry()


@cache
def _topics() -> dict[str, Topic]:
    return topics()


def levels(slug: str) -> tuple[int, ...]:
    return tuple(sorted(_topics()[ENGINE_TOPICS[slug]].levels))


def statement_latex(statement: str) -> str:
    """Turn "Text \\(math\\) text" into one LaTeX string, as problemLatex is rendered."""
    parts: list[str] = []
    position = 0
    for match in _INLINE_MATH.finditer(statement):
        if match.start() > position:
            parts.append(_text(statement[position : match.start()]))
        parts.append(match.group(1))
        position = match.end()
    if position < len(statement):
        parts.append(_text(statement[position:]))
    return "".join(parts)


def _text(value: str) -> str:
    if re.search(r"[\\{}$%&#^_~]", value):
        raise ValueError("Statement text must be plain")
    return rf"\text{{{value}}}"


def _public(task: Task) -> Issued:
    steps = []
    for step in task.steps:
        if step.text_key not in STEP_TEXT:
            raise ValueError(f"No learner text for step {step.text_key}")
        steps.append({"say": STEP_TEXT[step.text_key], "latex": step.latex})
    return Issued(
        statement=statement_latex(task.statement),
        record={"generator_version": task.generator_version, "code": task.code},
        answer_latex=task.answer.latex(),
        steps=tuple(steps),
    )


def issue(slug: str, level: int, seed: int | None = None) -> Issued:
    """A fresh problem of a public new-engine topic; the seed only picks it."""
    topic = _topics()[ENGINE_TOPICS[slug]]
    chosen = secrets.randbelow(10**16) if seed is None else seed
    return _public(topic.generate(level, chosen, _registry()))


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
