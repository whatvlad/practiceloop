"""Finite, verified practice catalogue. Records never cross the public API boundary."""

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from typing import Any

import sympy as sp

from app.generators.basic import (
    _POWER_TEMPLATES,
    _SECONDARY_TEMPLATES,
    BASIC_TEMPLATES,
    BasicTemplate,
    X,
    replay_basic,
)
from app.generators.definite import TEMPLATES as DEFINITE_TEMPLATES
from app.generators.definite import difficulty as definite_difficulty
from app.generators.definite import replay_definite, value_latex
from app.generators.derivatives import VERSION as DERIVATIVES_VERSION
from app.generators.derivatives import records as derivative_records
from app.generators.derivatives import replay_derivative
from app.generators.families import _families, replay_family

COEFFICIENTS = (-3, -2, -1, 1, 2, 3)
FAMILY_VERSIONS = frozenset({"substitution-v2", "parts-v1", "rational-v1", "trigonometric-v1"})


@dataclass(frozen=True)
class Exercise:
    record: dict[str, object]
    topic: str
    difficulty: int
    integrand: Any
    primitive: Any
    steps: tuple[dict[str, str], ...]
    statement: str
    # Exact value of a definite integral; None for indefinite exercises.
    value: Any = None
    # False for derivatives (#97): `integrand` is then the function to
    # differentiate, `primitive` its derivative, and the answer has no `+ C`.
    constant: bool = True

    @property
    def template(self) -> BasicTemplate:
        # Only substitution-v1 is checked through this view; its domain is all of R.
        return BasicTemplate("preview", self.difficulty, "real", self.topic)

    @property
    def antiderivative(self) -> Any:
        return self.primitive

    @property
    def answer(self) -> str:
        if self.value is not None:
            return value_latex(self.value)
        if not self.constant:
            return self.steps[-1]["latex"].removeprefix("f'(x) = ")
        return str(sp.latex(self.primitive)) + " + C"


def replay(record: dict[str, object]) -> Exercise:
    """Rebuild a catalogue exercise; its statement carries the template's real domain."""
    if record.get("generator_version") == "basic-v1":
        basic = replay_basic(record)
        return Exercise(
            record,
            "basic-integrals",
            basic.difficulty,
            basic.integrand,
            basic.antiderivative,
            tuple({"say": step.say, "latex": step.latex} for step in basic.solution_steps),
            basic.public().problem_latex,
        )
    if record.get("generator_version") == "definite-v1":
        definite = replay_definite(record)
        return Exercise(
            record,
            definite.topic,
            definite.difficulty,
            definite.integrand,
            definite.antiderivative,
            tuple({"say": step.say, "latex": step.latex} for step in definite.solution_steps),
            definite.statement,
            definite.value,
        )
    if record.get("generator_version") == DERIVATIVES_VERSION:
        derivative = replay_derivative(record)
        return Exercise(
            record,
            derivative.topic,
            derivative.difficulty,
            derivative.function,
            derivative.derivative,
            tuple({"say": step.say, "latex": step.latex} for step in derivative.solution_steps),
            derivative.statement,
            constant=False,
        )
    if record.get("generator_version") in FAMILY_VERSIONS:
        family = replay_family(record)
        return Exercise(
            record,
            family.topic,
            family.difficulty,
            family.integrand,
            family.antiderivative,
            tuple({"say": step.say, "latex": step.latex} for step in family.solution_steps),
            family.public().problem_latex,
        )
    # Only catalogue records are passed here; validate replay before constructing symbols.
    if set(record) != {"generator_version", "family", "a", "b", "scale", "difficulty"}:
        raise ValueError("Invalid record")
    if record["generator_version"] != "substitution-v1" or record["family"] not in (
        "sin",
        "cos",
        "exp",
    ):
        raise ValueError("Unknown version or family")
    a, b, scale, level = (record[key] for key in ("a", "b", "scale", "difficulty"))
    if any(type(v) is not int for v in (a, b, scale, level)):
        raise ValueError("Integer parameters required")
    if a not in (-3, -2, -1, 1, 2, 3) or b not in (1, 2) or level not in (1, 2):
        raise ValueError("Invalid parameters")
    if scale not in ((1,) if level == 1 else (2, 3)):
        raise ValueError("Invalid inner scale")
    inner = X**2 + b if level == 1 else scale * X + b
    u = sp.Symbol("u", real=True)
    outer = a * {"sin": sp.sin, "cos": sp.cos, "exp": sp.exp}[str(record["family"])](u)
    primitive = outer.subs(u, inner)
    integrand = sp.diff(primitive, X)
    outer_derivative = sp.diff(outer, u)
    if sp.simplify(outer_derivative.subs(u, inner) * sp.diff(inner, X) - integrand) != 0:
        raise RuntimeError("Invalid substitution")
    if primitive.is_real is not True or integrand.is_real is not True:
        raise RuntimeError("Invalid real domain")
    from app.content.catalogue import TEXT

    steps = (
        {"say": TEXT["substitute"], "latex": "u = " + str(sp.latex(inner))},
        {"say": TEXT["differentiate"], "latex": rf"du = {sp.latex(sp.diff(inner, X))}\,dx"},
        {
            "say": TEXT["rewrite"],
            "latex": rf"\int {sp.latex(integrand)}\,dx = \int {sp.latex(outer_derivative)}\,du",
        },
        {"say": TEXT["integrate"], "latex": str(sp.latex(outer)) + " + C"},
        {"say": TEXT["substitute_back"], "latex": str(sp.latex(primitive)) + " + C"},
    )
    statement = rf"\int \left({sp.latex(integrand)}\right)\,dx\quad(x\in\mathbb{{R}})"
    return Exercise(record, "substitution", int(level), integrand, primitive, steps, statement)


def _basic_records(difficulty: int) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for template in BASIC_TEMPLATES:
        if template.difficulty != difficulty:
            continue
        # expand_and_split needs positive coefficients so its terms never cancel.
        coefficients = (1, 2, 3) if template.name == "expand_and_split" else COEFFICIENTS
        for a, b, power in product(
            coefficients,
            (1, 2) if template.name in _SECONDARY_TEMPLATES else (1,),
            (2, 3, 4) if template.name in _POWER_TEMPLATES else (2,),
        ):
            records.append(
                dict(
                    generator_version="basic-v1",
                    template=template.name,
                    coefficient=a,
                    secondary=b,
                    power=power,
                )
            )
    return records


def _family_records(topic: str, difficulty: int) -> list[dict[str, object]]:
    return [
        dict(generator_version=version, template=name, coefficient=a)
        for version, (slug, templates, _) in _families().items()
        if slug == topic
        for name, template in templates.items()
        if template.difficulty == difficulty
        for a in COEFFICIENTS
    ]


def _definite_records(topic: str, difficulty: int) -> list[dict[str, object]]:
    # Indefinite records come first, so the guest demo's first exercise is unchanged.
    return [
        dict(generator_version="definite-v1", template=name, coefficient=a)
        for name, template in DEFINITE_TEMPLATES.items()
        if template.topic == topic and definite_difficulty(template) == difficulty
        for a in COEFFICIENTS
    ]


@lru_cache(maxsize=32)
def catalogue(topic: str, difficulty: int) -> tuple[Exercise, ...]:
    """Every verified record of one topic and level; empty cells are an error."""
    if type(difficulty) is not int or difficulty not in range(1, 6):
        raise ValueError("Unsupported practice cell")
    records: list[dict[str, object]] = []
    if topic == "basic-integrals":
        records = _basic_records(difficulty)
    elif topic == "substitution" and difficulty in (1, 2):
        # Saved substitution-v1 records keep their meaning; v2 adds levels 3-5.
        for family, a, b, scale in product(
            ("sin", "cos", "exp"),
            COEFFICIENTS,
            (1, 2),
            (1,) if difficulty == 1 else (2, 3),
        ):
            records.append(
                dict(
                    generator_version="substitution-v1",
                    family=family,
                    a=a,
                    b=b,
                    scale=scale,
                    difficulty=difficulty,
                )
            )
    elif topic == "derivatives":
        records = derivative_records(difficulty)
    else:
        records = _family_records(topic, difficulty)
    if records:
        records += _definite_records(topic, difficulty)
    if not records:
        raise ValueError("Unsupported practice cell")
    return tuple(replay(record) for record in records)
