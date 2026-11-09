"""Render a verified task into private storage fields, outside request-time picking."""

import re
from dataclasses import dataclass
from typing import Any

from app.engine.models import Task
from app.engine.registry import Registry

_INLINE_MATH = re.compile(r"\\\((.*?)\\\)", re.DOTALL)


@dataclass(frozen=True, slots=True)
class Issued:
    statement: str
    record: dict[str, object]
    answer_latex: str
    steps: tuple[dict[str, str], ...]
    visual: dict[str, Any] | None = None


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
    generator = generators.get(task.generator_version)
    step_text = generator.step_text
    from app.math_input.contracts import COMPUTATIONAL_KINDS, InputContract

    if task.answer.kind in COMPUTATIONAL_KINDS:
        from app.engine.codes import parse_code

        if task.answer.kind != getattr(generator.answer, "kind", None):
            raise ValueError("Built answer kind differs from generator metadata")
        code = parse_code(task.code, generators)
        if generators.get_code(code.prefix, code.version).version != task.generator_version:
            raise ValueError("Task version and code differ")
        describe = getattr(generator, "input_contract", None)
        if not callable(describe):
            raise ValueError("Computational generator must declare its input contract")
        contract = describe(generator.draw(code.seed))
        if (
            not isinstance(contract, InputContract)
            or getattr(task.answer, "contract", None) != contract
        ):
            raise ValueError("Answer and public input contract differ")
    visual = None
    build_visual = getattr(generator, "solution_visual", None)
    if callable(build_visual):
        from app.engine.codes import parse_code
        from app.visuals.complex_plane import validate_visual

        code = parse_code(task.code, generators)
        built = build_visual(generator.draw(code.seed))
        if built is not None:
            visual = validate_visual(built)
    elif generator.version in {
        "local-complex-v1",
        "local-conversion-v1",
        "local-conversion-polar-v1",
        "complex-argument-v1",
        "complex-de-moivre-v1",
        "complex-root-v1",
    }:
        from app.engine.algebra_practice.complex_visual import complex_visual
        from app.engine.codes import parse_code
        from app.visuals.complex_plane import validate_visual

        code = parse_code(task.code, generators)
        built = complex_visual(generator, generator.draw(code.seed), task)
        if built is not None:
            visual = validate_visual(built)
    steps = []
    for step in task.steps:
        if step.text_key not in step_text:
            raise ValueError(f"No learner text for step {step.text_key}")
        steps.append({"say": step_text[step.text_key], "latex": step.latex})
    if generator.version == "complex-de-moivre-v1":
        from app.engine.algebra_practice.polar_steps import de_moivre_steps
        from app.engine.codes import parse_code

        code = parse_code(task.code, generators)
        steps = de_moivre_steps(generator.draw(code.seed))
    return Issued(
        statement=statement_latex(task.statement),
        record={"generator_version": task.generator_version, "code": task.code},
        answer_latex=task.answer.latex(),
        steps=tuple(steps),
        visual=visual,
    )
