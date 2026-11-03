"""Private code replay and declarative topic views, including the shipped MVP slice."""

from dataclasses import replace
from functools import partial

from pydantic import Field

from app.engine import practice
from app.engine.catalogue import StoredModel, StoredProblem
from app.engine.codes import format_code, parse_code
from app.engine.models import Drawn
from app.engine.topics.catalogue import Choice, Topic, _analysis_level, _polynomial, _rational


class OpenedCode(StoredModel):
    topic: str
    difficulty: int = Field(ge=1, le=5)
    problem: StoredProblem


def _historical_views() -> tuple[Topic, ...]:
    # These registered engine versions remain permanent even after their topic
    # starts issuing a newer curriculum. They reference existing public topic rows.
    aliases = (
        ("partial-fractions", {1: (Choice("partial-fractions-v1"),)}),
        (
            "derivatives",
            {
                1: (Choice("derivative-v1", _polynomial),),
                2: (Choice("derivative-v1", _rational),),
            },
        ),
        ("basic-integrals", {1: (Choice("indefinite-v1", _polynomial),)}),
        ("rational-functions", {3: (Choice("indefinite-v1", _rational),)}),
        ("definite-integrals", {1: (Choice("definite-v1"),)}),
        (
            "functions-and-sequences",
            {
                level: (Choice("practice-sequence-v1", partial(_analysis_level, level)),)
                for level in range(1, 6)
            },
        ),
        (
            "limits-and-continuity",
            {
                level: (Choice("practice-limits-v1", partial(_analysis_level, level)),)
                for level in range(1, 6)
            },
        ),
    )
    analysis_two_aliases = tuple(
        (
            slug,
            {level: (Choice(version, partial(_analysis_level, level)),) for level in range(1, 6)},
        )
        for slug, version in (
            ("improper-integrals", "practice-improper-v1"),
            ("series", "practice-series-v1"),
            ("multivariable-functions", "practice-multivariable-v1"),
            ("differential-equations", "practice-ode-v1"),
        )
    )
    return tuple(
        replace(practice.ENGINE_TOPICS[slug], levels=levels, served=False)
        for slug, levels in (*aliases, *analysis_two_aliases)
    )


def _cell(version: str, params: Drawn) -> tuple[str, int]:
    for topic in (*practice.ENGINE_TOPICS.values(), *_historical_views()):
        for level, choices in topic.levels.items():
            if any(c.generator == version and c.predicate(params) for c in choices):
                return topic.slug, level
    raise ValueError("No practice view for this problem code")


def rebuild(text: str) -> OpenedCode:
    """Symbolic construction: called only under the math worker's resource limits."""
    generators = practice._registry()
    code = parse_code(text, generators)
    generator = generators.get_code(code.prefix, code.version)
    params = generator.draw(code.seed)
    topic, level = _cell(generator.version, params)
    task = generator.build(params)
    if task.code != format_code(code, generators):
        raise ValueError("Code did not reproduce the requested task")
    return OpenedCode(
        topic=topic,
        difficulty=level,
        problem=StoredProblem.from_issued(practice._public(task)),
    )
