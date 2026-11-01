"""Native full-curriculum single and partial derivative generators (#195)."""

from typing import Any

import sympy as sp

from app.engine.answers.derivative import DerivativeAnswer
from app.engine.answers.expression import ExpressionAnswer
from app.engine.blocks.differentiation.partial import PartialForm
from app.engine.blocks.differentiation.single import DerivativeForm
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task, TaskGenerator
from app.engine.prng import DeterministicRNG
from app.math_input import VariableDomain

STEP_TEXT = {
    "split_fraction": "Divide each numerator term by x.",
    "partial_fractions": "Write the rational function as partial fractions.",
    "derivative_standard": "Apply the standard derivative of the function.",
    "derivative_power": "Apply the power rule: multiply by the power, then lower the power by one.",
    "derivative_rewrite_power": "Write each root and reciprocal as a power of x.",
    "derivative_terms": "Differentiate each term separately.",
    "derivative_linear_inner": "Differentiate the outer function, then multiply by the "
    "constant from the inner function.",
    "derivative_chain_rule": "Apply the chain rule: differentiate the outer function, then "
    "multiply by the derivative of the inner function.",
    "derivative_product_rule": "Apply the product rule: differentiate one factor at a time "
    "and add the results.",
    "derivative_quotient_rule": "Apply the quotient rule: (f'g - fg') divided by g squared, "
    "where f is the numerator and g the denominator.",
    "derivative_log_laws": "Apply the logarithm laws to split the logarithm before you "
    "differentiate.",
    "derivative_result": "Simplify the result. A derivative has no arbitrary constant.",
    "partial_hold": "Differentiate with respect to the named variable. Hold every other "
    "variable constant.",
    "partial_second": "Differentiate the first result again with respect to the second variable.",
    "partial_mixed_check": "Check the result in the other order. The function is smooth, so "
    "the mixed partials are equal.",
    "coordinate_substitute": "Write the old variables in terms of the new coordinates.",
    "chain_partials": "Differentiate the function in each old variable, and each old "
    "variable in the new one.",
    "chain_rule_sum": "Add one chain-rule product for each old variable, then write the "
    "result in the new variables.",
    "simplify_result": "Simplify the result in the new variables.",
    "jacobian_matrix": "Write the matrix of the partial derivatives of the old variables in "
    "the new ones.",
    "jacobian_determinant": "Calculate the determinant of the matrix and simplify it.",
}


class SingleDerivativeParams(Drawn):
    form: DerivativeForm


class PartialDerivativeParams(Drawn):
    form: PartialForm


class SingleDerivatives:
    version = "practice-derivative-v1"
    prefix = "SDV"
    family = "practice-derivative"
    code_version = 1
    params = SingleDerivativeParams
    answer = DerivativeAnswer
    requires: tuple[str, ...] = ()
    step_text = STEP_TEXT

    def draw(self, seed: int) -> SingleDerivativeParams:
        return SingleDerivativeParams(seed=seed, form=DerivativeForm.draw(DeterministicRNG(seed)))

    def build(self, params: SingleDerivativeParams) -> Task:
        data = params.form.evaluate()
        statement = (
            rf"Find \(\frac{{d}}{{dx}}\left({sp.latex(data.function)}\right)\)"
            rf" for \(x\in {sp.latex(data.domain)}\)."
        )
        return Task(
            statement=statement,
            steps=tuple(Step(step.kind, step.latex) for step in data.solution_steps),
            answer=DerivativeAnswer(data.derivative, data.domain),
            metadata={"difficulty": params.form.difficulty, "template": params.form.template},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class PartialDerivatives:
    version = "practice-partial-v1"
    prefix = "PDV"
    family = "practice-partial"
    code_version = 1
    params = PartialDerivativeParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    step_text = STEP_TEXT

    def draw(self, seed: int) -> PartialDerivativeParams:
        return PartialDerivativeParams(seed=seed, form=PartialForm.draw(DeterministicRNG(seed)))

    def input_variables(self, params: PartialDerivativeParams) -> dict[str, VariableDomain]:
        return params.form.variables

    def build(self, params: PartialDerivativeParams) -> Task:
        data = params.form.evaluate()
        return Task(
            statement=rf"Calculate \({data.statement}\).",
            steps=tuple(Step(step.kind, step.latex) for step in data.steps),
            answer=ExpressionAnswer(data.answer, data.variables),
            metadata={"difficulty": params.form.difficulty, "template": params.form.template},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


def generators() -> tuple[TaskGenerator[Any], ...]:
    """Contribute this module's frozen versions to registry discovery."""
    return (SingleDerivatives(), PartialDerivatives())
