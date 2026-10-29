"""Small verified scalar generators for the first Algebra and Analysis syllabus wave."""

from dataclasses import dataclass
from random import Random
from typing import Any, Literal

import sympy as sp
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.problem import PublicProblem

X = sp.Symbol("x", real=True)
Y = sp.Symbol("y", real=True)
type VariableDomain = Literal["real", "positive"]

TOPIC_TEMPLATES: dict[str, tuple[str, ...]] = {
    "matrices": ("determinant",),
    "complex-numbers": ("modulus",),
    "fundamental-theorem-algebra": ("root-sum",),
    "partial-fractions": ("decompose",),
    "functions-and-sequences": ("sequence-value",),
    "limits-and-continuity": ("limit", "continuity"),
    "improper-integrals": ("improper-integral",),
    "series": ("geometric-series",),
    "multivariable-functions": ("partial-value",),
    "differential-equations": ("exponential-solution",),
}


class SymbolicParameters(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    generator_version: str = Field(pattern="^symbolic-v1$")
    topic: str = Field(min_length=3, max_length=48)
    template: str = Field(min_length=3, max_length=32)
    difficulty: int = Field(ge=1, le=5)
    a: int = Field(ge=1, le=5)
    b: int = Field(ge=1, le=5)
    variables: dict[str, VariableDomain] | None = None


@dataclass(frozen=True)
class SymbolicExercise:
    record: dict[str, object]
    topic: str
    difficulty: int
    statement: str
    expected: Any
    variables: dict[str, VariableDomain]
    steps: tuple[dict[str, str], ...]

    @property
    def answer(self) -> str:
        return str(sp.latex(self.expected))

    def public(self) -> PublicProblem:
        return PublicProblem(topic=self.topic, problem_latex=self.statement)


def _build(parameters: SymbolicParameters) -> SymbolicExercise:
    a, b = sp.Integer(parameters.a), sp.Integer(parameters.b)
    topic, template = parameters.topic, parameters.template
    variables: dict[str, VariableDomain] = {}
    if template == "determinant":
        c, d = b + 1, a + 2
        expected = a * d - b * c
        statement = rf"\det\begin{{pmatrix}}{a}&{b}\\{c}&{d}\end{{pmatrix}}"
        steps = (
            {
                "say": "Compute the determinant",
                "latex": rf"{a}\cdot{d}-{b}\cdot{c}={sp.latex(expected)}",
            },
        )
    elif template == "modulus":
        expected = sp.sqrt(a**2 + b**2)
        statement = rf"|{a}+{b}i|"
        steps = (
            {
                "say": "Use the complex modulus formula",
                "latex": rf"\sqrt{{{a}^2+{b}^2}}={sp.latex(expected)}",
            },
        )
    elif template == "root-sum":
        expected = -a
        statement = rf"x^2+{a}x+{b}=0: \text{{sum of the roots}}"
        steps = ({"say": "Apply Viète's formula", "latex": rf"x_1+x_2=-{a}={sp.latex(expected)}"},)
    elif template == "decompose":
        variables = {"x": "real"}
        expected = a / (X + 1) + b / (X + 2)
        numerator = sp.expand(a * (X + 2) + b * (X + 1))
        statement = rf"\frac{{{sp.latex(numerator)}}}{{(x+1)(x+2)}}= ?"
        steps = ({"say": "Split into partial fractions", "latex": sp.latex(expected)},)
    elif template == "sequence-value":
        expected = a * 5 + b
        statement = rf"a_n={a}n+{b};\quad a_5=?"
        steps = ({"say": "Substitute n = 5", "latex": rf"a_5={a}\cdot5+{b}={sp.latex(expected)}"},)
    elif template == "limit":
        expected = 2 * a
        statement = rf"\lim_{{x\to{a}}}\frac{{x^2-{a**2}}}{{x-{a}}}=?"
        steps = (
            {
                "say": "Cancel the common factor",
                "latex": rf"\lim_{{x\to{a}}}(x+{a})={sp.latex(expected)}",
            },
        )
    elif template == "continuity":
        expected = 2 * a
        statement = rf"f(x)=\frac{{x^2-{a**2}}}{{x-{a}}},\quad f({a})=?\text{{ for continuity}}"
        steps = ({"say": "Use the removable limit", "latex": rf"f({a})={sp.latex(expected)}"},)
    elif template == "improper-integral":
        expected = sp.Rational(1, a)
        statement = rf"\int_{{1}}^\infty \frac{{1}}{{x^{{{a + 1}}}}}\,dx=?"
        steps = (
            {"say": "Evaluate the convergent improper integral", "latex": rf"{sp.latex(expected)}"},
        )
    elif template == "geometric-series":
        expected = sp.Rational(a + 1, a)
        statement = rf"\sum_{{n=0}}^\infty \left(\frac{{{a}}}{{{a + 1}}}\right)^n=?"
        steps = (
            {
                "say": "Use the geometric series formula",
                "latex": rf"\frac{{1}}{{1-{a}/{a + 1}}}={sp.latex(expected)}",
            },
        )
    elif template == "partial-value":
        variables = {"x": "real", "y": "real"}
        expected = 2 * a * X * Y + b
        statement = rf"f(x,y)={a}x^2y+{b}y;\quad \frac{{\partial f}}{{\partial x}}=?"
        steps = ({"say": "Differentiate with respect to x", "latex": rf"f_x={sp.latex(expected)}"},)
    elif template == "exponential-solution":
        variables = {"x": "real"}
        expected = sp.exp(a * X)
        statement = rf"y'={a}y,\ y(0)=1;\quad y(x)=?"
        steps = ({"say": "Solve the separable equation", "latex": rf"y(x)={sp.latex(expected)}"},)
    else:
        raise ValueError("Unknown symbolic template")
    record = parameters.model_dump(exclude_none=True)
    if variables:
        record["variables"] = variables
    return SymbolicExercise(
        record, topic, parameters.difficulty, statement, expected, variables, steps
    )


def replay_symbolic(record: dict[str, object]) -> SymbolicExercise:
    parameters = SymbolicParameters.model_validate(record)
    if (
        parameters.topic not in TOPIC_TEMPLATES
        or parameters.template not in TOPIC_TEMPLATES[parameters.topic]
    ):
        raise ValueError("Unknown symbolic topic or template")
    return _build(parameters)


def generate_symbolic(*, topic: str, difficulty: int, seed: int) -> SymbolicExercise:
    if topic not in TOPIC_TEMPLATES or type(difficulty) is not int or difficulty not in range(1, 6):
        raise ValueError("Unsupported symbolic topic or difficulty")
    rng = Random(seed)  # noqa: S311 -- deterministic exercise choice, not a security token
    template = rng.choice(TOPIC_TEMPLATES[topic])
    return replay_symbolic(
        {
            "generator_version": "symbolic-v1",
            "topic": topic,
            "template": template,
            "difficulty": difficulty,
            "a": rng.randint(1, 5),
            "b": rng.randint(1, 5),
        }
    )
