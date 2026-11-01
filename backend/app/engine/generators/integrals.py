"""Native engine generators for the approved single-integral curriculum (#193)."""

from typing import Any

import sympy as sp

from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.engine.answers.expression import ExpressionAnswer
from app.engine.blocks.integral_forms.form import Family, IntegralData, IntegralForm
from app.engine.codes import encode
from app.engine.models import Answer, Drawn, Step, Task, TaskGenerator
from app.engine.prng import DeterministicRNG

STEP_TEXT = {
    "linearity": "Integrate each term separately.",
    "rewrite_power": "Write the integrand as a power of x.",
    "expand": "Expand the squared factor.",
    "split_fraction": "Divide each numerator term by x.",
    "integrate": "Apply the standard integral rules to each term.",
    "constant": "Add an arbitrary integration constant C.",
    "factor": "Write the polynomial as a squared factor.",
    "identity": "Apply the trigonometric identity to the integrand.",
    "substitution_integral": "Apply the substitution shown below the integral.",
    "nested_substitution": "Apply the second substitution inside the first.",
    "substitute_back": "Replace u with the original expression.",
    "parts": "Apply integration by parts: integrate one factor and differentiate the other.",
    "repeat_parts": "Apply integration by parts to the remaining integral.",
    "solve_cycle": "Add the remaining integral to both sides, then divide by two.",
    "partial_fractions": "Write the rational function as partial fractions.",
    "polynomial_division": (
        "Divide the numerator by the denominator before splitting the remainder."
    ),
    "evaluate_bounds": (
        "Evaluate the antiderivative at the upper bound and subtract its value at the lower bound."
    ),
    "definite_value": "Simplify the result. A definite integral has no integration constant.",
}


class IntegralParams(Drawn):
    form: IntegralForm


class IntegralGenerator:
    version = "practice-basic-v1"
    prefix = "BAS"
    family = "practice-basic"
    code_version = 1
    params = IntegralParams
    answer: type[Answer] = AntiderivativeAnswer
    requires: tuple[str, ...] = ()
    step_text = STEP_TEXT
    form_family: Family = "basic"
    bounded = False

    def draw(self, seed: int) -> IntegralParams:
        return IntegralParams(
            seed=seed,
            form=IntegralForm.draw(DeterministicRNG(seed), self.form_family, self.bounded),
        )

    def data(self, params: IntegralParams) -> IntegralData:
        if params.form.family != self.form_family:
            raise ValueError("Integral parameters belong to another family")
        return params.form.evaluate(self.bounded)

    def build(self, params: IntegralParams) -> Task:
        data = self.data(params)
        method = tuple(Step(step.kind, step.latex) for step in data.steps)
        primitive = str(sp.latex(data.primitive))
        answer: Answer
        if self.bounded:
            statement = (
                rf"Calculate \(\int_{{{sp.latex(data.lower)}}}^{{{sp.latex(data.upper)}}}"
                rf" \left({sp.latex(data.integrand)}\right)\,dx\)."
            )
            answer = ExpressionAnswer(data.value, {})
            steps = method + (
                Step("integrate", primitive),
                Step(
                    "evaluate_bounds",
                    rf"\left[{primitive}\right]_{{{sp.latex(data.lower)}}}^{{{sp.latex(data.upper)}}}"
                    rf" = {answer.latex()}",
                ),
                Step("definite_value", answer.latex()),
            )
        else:
            statement = (
                rf"Find \(\int \left({sp.latex(data.integrand)}\right)\,dx\)"
                rf" for \(x\in {sp.latex(data.domain)}\)."
            )
            answer = AntiderivativeAnswer(data.integrand, data.primitive, data.domain)
            steps = method + (Step("integrate", primitive), Step("constant", answer.latex()))
        return Task(
            statement=statement,
            steps=steps,
            answer=answer,
            metadata={"difficulty": params.form.difficulty, "template": params.form.template},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class BasicIntegrals(IntegralGenerator):
    pass


class DefiniteBasicIntegrals(BasicIntegrals):
    version = "practice-basic-definite-v1"
    code_version = 2
    answer = ExpressionAnswer
    bounded = True


class SubstitutionIntegrals(IntegralGenerator):
    version = "practice-substitution-v1"
    prefix = "SUB"
    family = "practice-substitution"
    form_family: Family = "substitution"


class DefiniteSubstitutionIntegrals(SubstitutionIntegrals):
    version = "practice-substitution-definite-v1"
    code_version = 2
    answer = ExpressionAnswer
    bounded = True


class PartsIntegrals(IntegralGenerator):
    version = "practice-parts-v1"
    prefix = "IPT"
    family = "practice-parts"
    form_family: Family = "parts"


class DefinitePartsIntegrals(PartsIntegrals):
    version = "practice-parts-definite-v1"
    code_version = 2
    answer = ExpressionAnswer
    bounded = True


class RationalIntegrals(IntegralGenerator):
    version = "practice-rational-v1"
    prefix = "RNI"
    family = "practice-rational"
    form_family: Family = "rational"


class DefiniteRationalIntegrals(RationalIntegrals):
    version = "practice-rational-definite-v1"
    code_version = 2
    answer = ExpressionAnswer
    bounded = True


class TrigonometricIntegrals(IntegralGenerator):
    version = "practice-trigonometric-v1"
    prefix = "TGI"
    family = "practice-trigonometric"
    form_family: Family = "trigonometric"


class DefiniteTrigonometricIntegrals(TrigonometricIntegrals):
    version = "practice-trigonometric-definite-v1"
    code_version = 2
    answer = ExpressionAnswer
    bounded = True


def integral_generators() -> tuple[IntegralGenerator, ...]:
    return (
        BasicIntegrals(),
        DefiniteBasicIntegrals(),
        SubstitutionIntegrals(),
        DefiniteSubstitutionIntegrals(),
        PartsIntegrals(),
        DefinitePartsIntegrals(),
        RationalIntegrals(),
        DefiniteRationalIntegrals(),
        TrigonometricIntegrals(),
        DefiniteTrigonometricIntegrals(),
    )


def generators() -> tuple[TaskGenerator[Any], ...]:
    """Contribute this module's frozen versions to registry discovery."""
    return integral_generators()
