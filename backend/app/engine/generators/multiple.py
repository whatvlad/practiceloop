"""Native Cartesian, polar and cylindrical multiple-integral generators (#194)."""

from typing import Literal

from app.engine.answers.expression import ExpressionAnswer
from app.engine.blocks.multiple.form import MultipleData, MultipleForm
from app.engine.codes import encode
from app.engine.models import Drawn, Task
from app.engine.prng import DeterministicRNG


class MultipleParams(Drawn):
    form: MultipleForm


class DoubleIntegrals:
    version = "practice-double-v1"
    prefix = "DBL"
    family = "practice-double"
    code_version = 1
    params = MultipleParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    dimension: Literal[2, 3] = 2
    step_text = {
        "describe_region": "Describe the region with bounds for each variable.",
        "describe_polar": "Describe the region in polar coordinates.",
        "write_iterated": "Write the double integral as an iterated integral.",
        "reverse_order": "Reverse the order of integration over the same region.",
        "polar_change": "Use x = r cos theta, y = r sin theta and dA = r dr dtheta.",
        "integrate_inner": "Integrate the inner integral, keeping outer variables constant.",
        "integrate_outer": "Integrate between the outer bounds.",
        "check_other": "Check the value using the other setup of the same region.",
        "multiple_value": "Simplify the exact value of the integral.",
    }

    def draw(self, seed: int) -> MultipleParams:
        return MultipleParams(
            seed=seed, form=MultipleForm.draw(DeterministicRNG(seed), self.dimension)
        )

    def data(self, params: MultipleParams) -> MultipleData:
        if params.form.dimension != self.dimension:
            raise ValueError("Multiple-integral parameters have another dimension")
        return params.form.evaluate()

    def build(self, params: MultipleParams) -> Task:
        data = self.data(params)
        return Task(
            statement=rf"Calculate \({data.statement}\).",
            steps=data.steps,
            answer=ExpressionAnswer(data.value, {}),
            metadata={
                "difficulty": params.form.difficulty,
                "template": params.form.template,
                "variant": params.form.variant,
            },
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class TripleIntegrals(DoubleIntegrals):
    version = "practice-triple-v1"
    prefix = "TPL"
    family = "practice-triple"
    dimension: Literal[2, 3] = 3
    step_text = {
        **DoubleIntegrals.step_text,
        "describe_solid": "Describe the solid with bounds for each variable.",
        "cylindrical_change": "Use x = r cos theta, y = r sin theta and dV = r dz dr dtheta.",
        "write_triple": "Write the triple integral as an iterated integral.",
        "integrate_middle": "Integrate the middle integral, keeping the outer variable constant.",
    }
