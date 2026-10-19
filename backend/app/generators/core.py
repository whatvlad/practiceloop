"""Finite, verified preview catalogue. Records never cross the public API boundary."""

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from typing import Any

import sympy as sp

from app.generators.basic import BasicTemplate, X, replay_basic


@dataclass(frozen=True)
class Exercise:
    record: dict[str, object]
    topic: str
    difficulty: int
    integrand: Any
    primitive: Any
    steps: tuple[dict[str, str], ...]

    @property
    def template(self) -> BasicTemplate:
        return BasicTemplate("preview", self.difficulty, "real", self.topic)

    @property
    def antiderivative(self) -> Any:
        return self.primitive

    @property
    def statement(self) -> str:
        return rf"\int \left({sp.latex(self.integrand)}\right)\,dx\quad(x\in\mathbb{{R}})"

    @property
    def answer(self) -> str:
        return str(sp.latex(self.primitive)) + " + C"


def replay(record: dict[str, object]) -> Exercise:
    if record.get("generator_version") == "basic-v1":
        problem = replay_basic(record)
        if problem.difficulty not in (1, 2):
            raise ValueError("Unsupported preview level")
        return Exercise(
            record,
            "basic-integrals",
            problem.difficulty,
            problem.integrand,
            problem.antiderivative,
            tuple({"say": step.say, "latex": step.latex} for step in problem.solution_steps),
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
    return Exercise(record, "substitution", int(level), integrand, primitive, steps)


@lru_cache(maxsize=4)
def catalogue(topic: str, difficulty: int) -> tuple[Exercise, ...]:
    if topic not in ("basic-integrals", "substitution") or difficulty not in (1, 2):
        raise ValueError("Unsupported preview cell")
    records: list[dict[str, object]] = []
    if topic == "basic-integrals":
        names = (
            ("constant", "power", "exponential", "sine", "cosine") if difficulty == 1 else ("sum",)
        )
        for name in names:
            for a, b, power in product(
                (-3, -2, -1, 1, 2, 3),
                (1, 2) if name == "sum" else (1,),
                (2, 3, 4) if name in ("power", "sum") else (2,),
            ):
                records.append(
                    dict(
                        generator_version="basic-v1",
                        template=name,
                        coefficient=a,
                        secondary=b,
                        power=power,
                    )
                )
    else:
        for family, a, b, scale in product(
            ("sin", "cos", "exp"),
            (-3, -2, -1, 1, 2, 3),
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
    return tuple(replay(record) for record in records)
