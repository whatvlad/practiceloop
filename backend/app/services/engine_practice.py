"""Private adapter for the first new-engine topic in saved practice."""

from collections.abc import Mapping

from app.content.catalogue import TEXT
from app.engine.codes import parse_code
from app.engine.generators.catalogue import registry
from app.engine.models import Task
from app.engine.topics.catalogue import topics
from app.services.math_parser import MathInputError, parse_math_input
from app.services.owned_records import PrivateSolution

VERSION = "combinations-v1"


def replay_combination(record: Mapping[str, object]) -> Task:
    if set(record) != {"generator_version", "code"} or record.get("generator_version") != VERSION:
        raise ValueError("Invalid new-engine record")
    value = record.get("code")
    if not isinstance(value, str):
        raise ValueError("Invalid problem code")
    generators = registry()
    code = parse_code(value, generators)
    generator = generators.get_code(code.prefix, code.version)
    if generator.version != VERSION:
        raise ValueError("Wrong generator for combinations")
    return generator.build(generator.draw(code.seed))


def issue_combination(seed: int) -> tuple[str, PrivateSolution]:
    task = topics()["combinations"].generate(1, seed, registry())
    prefix, suffix = r"Calculate \(", r"\)."
    if not task.statement.startswith(prefix) or not task.statement.endswith(suffix):
        raise ValueError("Unexpected combinations statement")
    statement = task.statement[len(prefix) : -len(suffix)]
    solution = PrivateSolution(
        generator_version=VERSION,
        generator_data={"generator_version": VERSION, "code": task.code},
        answer_latex=task.answer.latex(),
        solution_steps=[{"say": TEXT["combinations"], "latex": step.latex} for step in task.steps],
    )
    return statement, solution


def check_combination(answer: str, record: Mapping[str, object]) -> str:
    task = replay_combination(record)
    try:
        tree = parse_math_input(answer, ())
    except MathInputError:
        return "invalid"
    return task.answer.check(tree)
