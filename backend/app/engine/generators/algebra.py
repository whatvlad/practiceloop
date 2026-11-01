"""Native generators for the current scalar Algebra curriculum (#196)."""

from typing import Any

from pydantic import Field

from app.engine.answers.expression import ExpressionAnswer
from app.engine.blocks.algebra import AlgebraForm, AlgebraKind
from app.engine.codes import encode
from app.engine.models import Drawn, Task, TaskGenerator
from app.engine.prng import DeterministicRNG
from app.math_input import VariableDomain


class AlgebraParams(Drawn):
    difficulty: int = Field(ge=1, le=5)
    form: AlgebraForm


class AlgebraGenerator:
    version: str
    prefix: str
    family: str
    form_kind: AlgebraKind
    code_version = 1
    params = AlgebraParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    step_text = {
        "determinant": "Compute the determinant",
        "modulus": "Use the complex modulus formula",
        "root_sum": "Apply Vi\u00e8te's formula",
        "decompose": "Split into partial fractions",
    }

    def draw(self, seed: int) -> AlgebraParams:
        rng = DeterministicRNG(seed)
        return AlgebraParams(
            seed=seed,
            difficulty=1 + rng.randbelow(5),
            form=AlgebraForm(kind=self.form_kind, a=1 + rng.randbelow(5), b=1 + rng.randbelow(5)),
        )

    def build(self, params: AlgebraParams) -> Task:
        if params.form.kind != self.form_kind:
            raise ValueError("Algebra form belongs to a different generator")
        data = params.form.evaluate()
        variables: dict[str, VariableDomain] = (
            {"x": "real"} if self.form_kind == "decompose" else {}
        )
        return Task(
            statement=rf"Calculate \({data.statement}\).",
            steps=data.steps,
            answer=ExpressionAnswer(data.expected, variables),
            metadata={"difficulty": params.difficulty, "template": self.form_kind},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class Matrices(AlgebraGenerator):
    version = "practice-matrices-v1"
    prefix = "MTR"
    family = "practice-matrices"
    form_kind: AlgebraKind = "determinant"


class ComplexNumbers(AlgebraGenerator):
    version = "practice-complex-v1"
    prefix = "CPX"
    family = "practice-complex"
    form_kind: AlgebraKind = "modulus"


class RootSum(AlgebraGenerator):
    version = "practice-root-sum-v1"
    prefix = "VRS"
    family = "practice-root-sum"
    form_kind: AlgebraKind = "root-sum"


class PracticePartialFractions(AlgebraGenerator):
    version = "practice-partial-fractions-v1"
    prefix = "PFA"
    family = "practice-partial-fractions"
    form_kind: AlgebraKind = "decompose"

    def input_variables(self, params: AlgebraParams) -> dict[str, VariableDomain]:
        return {"x": "real"}


def algebra_generators() -> tuple[AlgebraGenerator, ...]:
    return Matrices(), ComplexNumbers(), RootSum(), PracticePartialFractions()


def generators() -> tuple[TaskGenerator[Any], ...]:
    """Contribute this module's frozen versions to registry discovery."""
    return algebra_generators()
