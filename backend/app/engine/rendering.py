"""Render a verified task into private storage fields, outside request-time picking."""

import re
from dataclasses import dataclass

from app.engine.models import Task
from app.engine.registry import Registry

_INLINE_MATH = re.compile(r"\\\((.*?)\\\)", re.DOTALL)


@dataclass(frozen=True, slots=True)
class Issued:
    statement: str
    record: dict[str, object]
    answer_latex: str
    steps: tuple[dict[str, str], ...]


def statement_latex(statement: str) -> str:
    """Turn text with inline math into the single LaTeX string the UI renders."""
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


def render(task: Task, generators: Registry) -> Issued:
    step_text = generators.get(task.generator_version).step_text
    steps = []
    for step in task.steps:
        if step.text_key not in step_text:
            raise ValueError(f"No learner text for step {step.text_key}")
        steps.append({"say": step_text[step.text_key], "latex": step.latex})
    return Issued(
        statement=statement_latex(task.statement),
        record={"generator_version": task.generator_version, "code": task.code},
        answer_latex=task.answer.latex(),
        steps=tuple(steps),
    )
