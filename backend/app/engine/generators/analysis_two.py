"""Independently versioned Analysis II tasks; published prefix allocation is explicit."""

from dataclasses import dataclass
from typing import Any, ClassVar

from app.engine.answers.expression import ExpressionAnswer
from app.engine.answers.real_function import ConstantExpressionAnswer, FullRealExpressionAnswer
from app.engine.blocks.analysis_two import AnalysisTwoForm
from app.engine.codes import encode
from app.engine.generators import (
    _analysis_improper as analysis_improper,
)
from app.engine.generators import (
    _analysis_multivariable as analysis_multivariable,
)
from app.engine.generators import (
    _analysis_ode as analysis_ode,
)
from app.engine.generators import (
    _analysis_series as analysis_series,
)
from app.engine.models import Drawn, Task, TaskGenerator
from app.engine.prng import DeterministicRNG
from app.math_input import VariableDomain


class AnalysisTwoParams(Drawn):
    form: AnalysisTwoForm


# Generator identity is independent of topic order or later topic-level edits.
SPECS = (
    ("improper-p-test", 1, "AJAA"),
    ("improper-power-tail", 2, "AJAB"),
    ("improper-exponential", 2, "AJAC"),
    ("improper-comparison", 3, "AJAD"),
    ("improper-arctangent", 3, "AJAE"),
    ("improper-log-test", 4, "AJAF"),
    ("improper-divergence", 4, "AJAG"),
    ("improper-decay-mass", 5, "AJAH"),
    ("improper-volume", 5, "AJAI"),
    ("series-p-test", 1, "AJAJ"),
    ("series-term-test", 1, "AJAK"),
    ("series-alternating", 2, "AJAL"),
    ("series-comparison", 2, "AJAM"),
    ("series-root-test", 2, "AJAN"),
    ("series-ratio-test", 3, "AJAO"),
    ("series-log-test", 3, "AJAP"),
    ("series-power-radius", 3, "AJAQ"),
    ("series-power-interval", 4, "AJAR"),
    ("series-entire", 4, "AJAS"),
    ("series-taylor", 5, "AJAT"),
    ("series-maclaurin-sine", 5, "AJAU"),
    ("series-maclaurin-cosine", 5, "AJAV"),
    ("series-maclaurin-log", 5, "AJAW"),
    ("multivariable-domain-two", 1, "AJAX"),
    ("multivariable-domain-three", 1, "AJAY"),
    ("multivariable-value-two", 1, "AJAZ"),
    ("multivariable-value-three", 1, "AJBA"),
    ("multivariable-gradient-two", 2, "AJBB"),
    ("multivariable-directional", 2, "AJBC"),
    ("multivariable-third-partial", 2, "AJBD"),
    ("multivariable-differential-two", 3, "AJBE"),
    ("multivariable-differential-three", 3, "AJBF"),
    ("multivariable-gradient-three", 3, "AJBG"),
    ("multivariable-local-minimum", 4, "AJBH"),
    ("multivariable-classify", 4, "AJBI"),
    ("multivariable-constrained", 5, "AJBJ"),
    ("multivariable-box", 5, "AJBK"),
    ("ode-separable-exponential", 1, "AJBL"),
    ("ode-separable-root", 1, "AJBM"),
    ("ode-linear", 2, "AJBN"),
    ("ode-linear-variable", 2, "AJBO"),
    ("ode-harmonic", 3, "AJBP"),
    ("ode-distinct-roots", 3, "AJBQ"),
    ("ode-repeated-root", 4, "AJBR"),
    ("ode-resonance", 4, "AJBS"),
    ("ode-laplace-exponential", 5, "AJBT"),
    ("ode-laplace-oscillator", 5, "AJBU"),
)

SYMBOLIC = frozenset({"series-taylor", "series-maclaurin-sine", "series-maclaurin-cosine"})

REASONS = {
    "improper-p-test": "Take a finite upper bound, integrate, and test its limit.",
    "improper-power-tail": "Check the primitive and let the upper endpoint tend to infinity.",
    "improper-exponential": "Exponential decay makes the upper endpoint term tend to zero.",
    "improper-comparison": "A positive finite limit of the ratio transfers convergence.",
    "improper-arctangent": "Use the arctangent primitive and its limit at positive infinity.",
    "improper-log-test": "Substitute u = ln(x) and apply the first-kind power criterion.",
    "improper-divergence": "Compare with the divergent harmonic integral.",
    "improper-decay-mass": "Integrate the linear density over the remaining unbounded rod.",
    "improper-volume": "Integrate disk areas and take the first-kind improper limit.",
    "series-p-test": "Positive decreasing terms allow the integral test.",
    "series-term-test": "Convergence requires the individual terms to tend to zero.",
    "series-alternating": "Apply Leibniz, then test the absolute-value series separately.",
    "series-comparison": "Bound the positive terms by a convergent p-series.",
    "series-root-test": "Take the n-th root and compare its limit with 1.",
    "series-ratio-test": "Cancel successive terms and compare the limit with 1.",
    "series-log-test": "Use the integral test and the substitution u = ln(x).",
    "series-power-radius": "Cauchy-Hadamard gives the reciprocal of the coefficient root limit.",
    "series-power-interval": "Find the open interval, then check both endpoint series.",
    "series-entire": "The ratio tends to zero for every fixed real x.",
    "series-taylor": "Use derivatives at the center divided by factorials.",
    "series-maclaurin-sine": "Use the alternating odd-power sine expansion about zero.",
    "series-maclaurin-cosine": "Use the alternating even-power cosine expansion about zero.",
    "series-maclaurin-log": "Read the coefficient from the logarithmic Maclaurin series.",
    "multivariable-domain-two": "The square-root radicand must be nonnegative.",
    "multivariable-domain-three": "The logarithm's argument must be strictly positive.",
    "multivariable-value-two": "Substitute both coordinates into the polynomial.",
    "multivariable-value-three": "Substitute all three coordinates into the polynomial.",
    "multivariable-gradient-two": "Form both partials and take the gradient's norm.",
    "multivariable-directional": "Take the gradient's dot product with a unit vector.",
    "multivariable-third-partial": "Polynomial mixed partials agree in either order.",
    "multivariable-differential-two": "Take the gradient times the displacement.",
    "multivariable-differential-three": "Use all three partials in the differential.",
    "multivariable-gradient-three": "Use all three gradient components in the Euclidean norm.",
    "multivariable-local-minimum": "Check the critical point and Hessian's positivity.",
    "multivariable-classify": "Use the Hessian determinant and its first entry.",
    "multivariable-constrained": "Solve the multiplier equations; prove a quadratic bound.",
    "multivariable-box": "Compare the sole interior critical volume with the zero boundary values.",
    "ode-separable-exponential": "Separate, integrate and use the positive initial value.",
    "ode-separable-root": "Separate and use the positive initial branch.",
    "ode-linear": "Multiply by the integrating factor and apply the initial condition.",
    "ode-linear-variable": "Find the variable-coefficient integrating factor, then integrate.",
    "ode-harmonic": "Use sine and cosine and determine both constants from the initial data.",
    "ode-distinct-roots": "Use the two distinct characteristic roots and the initial data.",
    "ode-repeated-root": "A repeated root needs an x times exponential term.",
    "ode-resonance": "Multiply the resonant trial by x, then apply both initial conditions.",
    "ode-laplace-exponential": "Transform the IVP and split its rational transform.",
    "ode-laplace-oscillator": "Transform with the initial data; invert sine and cosine.",
}


@dataclass(frozen=True)
class AnalysisTwo:
    template: str
    difficulty: int
    prefix: str
    code_version = 1
    params = AnalysisTwoParams
    answer: ClassVar[type[ExpressionAnswer]] = ConstantExpressionAnswer
    requires: tuple[str, ...] = ()

    @property
    def version(self) -> str:
        return f"analysis2-{self.template}-v1"

    @property
    def family(self) -> str:
        return f"analysis2-{self.template}"

    @property
    def step_text(self) -> dict[str, str]:
        return {"reason": REASONS[self.template], "result": "Read off the requested answer."}

    def draw(self, seed: int) -> AnalysisTwoParams:
        rng = DeterministicRNG(seed)
        return AnalysisTwoParams(
            seed=seed,
            form=AnalysisTwoForm(
                a=1 + rng.randbelow(5), b=1 + rng.randbelow(5), c=1 + rng.randbelow(5)
            ),
        )

    def build(self, params: AnalysisTwoParams) -> Task:
        module = {
            "improper": analysis_improper,
            "series": analysis_series,
            "multivariable": analysis_multivariable,
            "ode": analysis_ode,
        }[self.template.split("-")[0]]
        data = module.evaluate(self.template, params.form)
        return Task(
            data.statement,
            data.steps,
            self.answer(data.expected, data.variables),
            {"difficulty": self.difficulty, "template": self.template},
            encode(self.prefix, 1, params.seed),
            self.version,
        )


class SymbolicAnalysisTwo(AnalysisTwo):
    answer = FullRealExpressionAnswer

    def input_variables(self, params: AnalysisTwoParams) -> dict[str, VariableDomain]:
        return {"x": "real"}


def generators() -> tuple[TaskGenerator[Any], ...]:
    return tuple(
        (SymbolicAnalysisTwo if kind in SYMBOLIC or kind.startswith("ode-") else AnalysisTwo)(
            kind, level, prefix
        )
        for kind, level, prefix in SPECS
    )
