"""Native generators for the remaining existing analysis topics (#197)."""

from typing import Any

from pydantic import Field

from app.engine.answers.expression import ExpressionAnswer
from app.engine.blocks.analysis import AnalysisForm, AnalysisKind
from app.engine.codes import encode
from app.engine.models import Drawn, Task, TaskGenerator
from app.engine.prng import DeterministicRNG
from app.math_input import VariableDomain


class AnalysisParams(Drawn):
    difficulty: int = Field(ge=1, le=5)
    form: AnalysisForm


class AnalysisGenerator:
    version: str
    prefix: str
    family: str
    templates: tuple[AnalysisKind, ...]
    code_version = 1
    params = AnalysisParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    step_text = {
        "sequence": "Substitute n = 5",
        "limit": "Cancel the common factor",
        "continuity": "Use the removable limit",
        "improper": "Evaluate the convergent improper integral",
        "series": "Use the geometric series formula",
        "partial": "Differentiate with respect to x; hold y constant",
        "ode": "Solve the separable equation and apply y(0) = 1",
    }

    def draw(self, seed: int) -> AnalysisParams:
        rng = DeterministicRNG(seed)
        return AnalysisParams(
            seed=seed,
            difficulty=1 + rng.randbelow(5),
            form=AnalysisForm(
                kind=self.templates[rng.randbelow(len(self.templates))],
                a=1 + rng.randbelow(5),
                b=1 + rng.randbelow(5),
            ),
        )

    def build(self, params: AnalysisParams) -> Task:
        if params.form.kind not in self.templates:
            raise ValueError("Analysis form belongs to a different generator")
        data = params.form.evaluate()
        variables: dict[str, VariableDomain] = {}
        if params.form.kind == "partial-value":
            variables = {"x": "real", "y": "real"}
        elif params.form.kind == "exponential-solution":
            variables = {"x": "real"}
        return Task(
            statement=rf"Calculate \({data.statement}\).",
            steps=data.steps,
            answer=ExpressionAnswer(data.expected, variables),
            metadata={"difficulty": params.difficulty, "template": params.form.kind},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class Sequences(AnalysisGenerator):
    version = "practice-sequence-v1"
    prefix = "SEQ"
    family = "practice-sequence"
    templates: tuple[AnalysisKind, ...] = ("sequence-value",)


class Limits(AnalysisGenerator):
    version = "practice-limits-v1"
    prefix = "LIM"
    family = "practice-limits"
    templates: tuple[AnalysisKind, ...] = ("limit", "continuity")


class ImproperIntegrals(AnalysisGenerator):
    version = "practice-improper-v1"
    prefix = "IMP"
    family = "practice-improper"
    templates: tuple[AnalysisKind, ...] = ("improper-integral",)


class Series(AnalysisGenerator):
    version = "practice-series-v1"
    prefix = "SER"
    family = "practice-series"
    templates: tuple[AnalysisKind, ...] = ("geometric-series",)


class MultivariableFunctions(AnalysisGenerator):
    version = "practice-multivariable-v1"
    prefix = "MVF"
    family = "practice-multivariable"
    templates: tuple[AnalysisKind, ...] = ("partial-value",)

    def input_variables(self, params: AnalysisParams) -> dict[str, VariableDomain]:
        return {"x": "real", "y": "real"}


class DifferentialEquations(AnalysisGenerator):
    version = "practice-ode-v1"
    prefix = "ODE"
    family = "practice-ode"
    templates: tuple[AnalysisKind, ...] = ("exponential-solution",)

    def input_variables(self, params: AnalysisParams) -> dict[str, VariableDomain]:
        return {"x": "real"}


def analysis_generators() -> tuple[AnalysisGenerator, ...]:
    return (
        Sequences(),
        Limits(),
        ImproperIntegrals(),
        Series(),
        MultivariableFunctions(),
        DifferentialEquations(),
    )


def generators() -> tuple[TaskGenerator[Any], ...]:
    """Contribute this module's frozen versions to registry discovery."""
    return analysis_generators()
