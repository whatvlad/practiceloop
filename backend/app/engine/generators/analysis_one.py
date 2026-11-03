"""Analysis I templates with independent frozen versions and structural levels."""

from dataclasses import dataclass
from typing import Any, ClassVar

from app.engine.answers.expression import ExpressionAnswer
from app.engine.answers.real_function import ConstantExpressionAnswer, FullRealExpressionAnswer
from app.engine.blocks.analysis_one import AnalysisOneForm, evaluate
from app.engine.codes import encode
from app.engine.models import Drawn, Task, TaskGenerator
from app.engine.prng import DeterministicRNG
from app.math_input import VariableDomain


class AnalysisOneParams(Drawn):
    form: AnalysisOneForm


# A level describes a method, never a random integer label on the same exercise.
MATRIX: dict[str, dict[int, tuple[str, ...]]] = {
    "functions-and-sequences": {
        1: ("parity", "domain"),
        2: ("composition", "inverse"),
        3: ("sequence-increment", "sequence-bound"),
        4: ("sequence-rational", "sequence-oscillation", "sequence-unbounded"),
        5: ("sequence-exponential", "sequence-radical"),
    },
    "limits-and-continuity": {
        1: ("limit-polynomial", "limit-cancel"),
        2: ("limit-sine", "limit-exponential"),
        3: ("limit-left", "limit-right", "limit-infinite"),
        4: ("limit-infinity", "asymptote", "continuity"),
        5: ("lhopital", "bisection"),
    },
    "differential-calculus": {
        1: ("derivative-definition", "tangent"),
        2: ("differential", "chain"),
        3: ("mean-value", "monotonicity"),
        4: ("local-extremum", "global-extremum"),
        5: ("rectangle", "box"),
    },
}

# These texts describe the operation in the mathematical lines, not an answer
# hidden in metadata. Prefix allocation below is frozen by the golden corpus.
REASONS = {
    "parity": "Replace x by -x and compare with f(x).",
    "domain": "A real square root requires a nonnegative radicand.",
    "composition": "Substitute the entire expression g(x) into f.",
    "inverse": "Solve y = f(x) for x and interchange the names.",
    "sequence-increment": "Subtract consecutive terms; the positive difference proves increase.",
    "sequence-bound": "Prove an upper bound and show that the sequence approaches it.",
    "sequence-rational": "Divide the numerator and denominator by n.",
    "sequence-oscillation": "Two subsequences with different limits rule out convergence.",
    "sequence-unbounded": "Positive linear growth has no finite upper bound.",
    "sequence-exponential": "Take logarithms and use the standard logarithmic limit.",
    "sequence-radical": "Multiply by the conjugate, then divide by n.",
    "limit-polynomial": "A polynomial is continuous; substitute the limiting point.",
    "limit-cancel": "Cancel only away from the limiting point, then take the limit.",
    "limit-sine": "Rescale the variable and use sin(t)/t tending to 1.",
    "limit-exponential": "Rescale and use (exp(t)-1)/t tending to 1.",
    "limit-left": "On the left the absolute value changes the numerator's sign.",
    "limit-right": "On the right the absolute value leaves the numerator positive.",
    "limit-infinite": "A positive numerator divided by a square tending to zero grows unbounded.",
    "limit-infinity": "Divide through by the highest power of x.",
    "asymptote": "Polynomial division separates the line and a remainder tending to zero.",
    "continuity": "The value at the join must equal both one-sided limits.",
    "lhopital": "Both quotients have form 0/0; differentiate twice near zero.",
    "bisection": "The function is continuous and strictly increasing; keep the sign-changing half.",
    "derivative-definition": "Expand the difference quotient and let h tend to zero.",
    "tangent": "The tangent slope equals the derivative, the limit of secant slopes.",
    "differential": "Multiply the derivative at the given point by dx.",
    "chain": "Differentiate the exponential, then multiply by its inner derivative.",
    "mean-value": "Check continuity and differentiability, then equate slope and derivative.",
    "monotonicity": "Factor the derivative and determine its sign on all three intervals.",
    "local-extremum": "A stationary point with negative second derivative is a local maximum.",
    "global-extremum": "Compare every interior stationary value with both endpoint values.",
    "rectangle": "Eliminate one side using the perimeter; maximize the resulting quadratic.",
    "box": "Differentiate the volume and compare the interior maximum with zero endpoint limits.",
}


@dataclass(frozen=True)
class AnalysisOne:
    template: str
    difficulty: int
    prefix: str
    code_version = 1
    params = AnalysisOneParams
    answer: ClassVar[type[ExpressionAnswer]] = ConstantExpressionAnswer
    requires: tuple[str, ...] = ()

    @property
    def version(self) -> str:
        return f"analysis1-{self.template}-v1"

    @property
    def family(self) -> str:
        return f"analysis1-{self.template}"

    @property
    def step_text(self) -> dict[str, str]:
        return {
            "reason": REASONS[self.template],
            "result": "Read off the requested answer.",
        }

    def draw(self, seed: int) -> AnalysisOneParams:
        rng = DeterministicRNG(seed)
        return AnalysisOneParams(
            seed=seed,
            form=AnalysisOneForm(
                a=1 + rng.randbelow(5), b=1 + rng.randbelow(5), c=1 + rng.randbelow(5)
            ),
        )

    def build(self, params: AnalysisOneParams) -> Task:
        data = evaluate(self.template, params.form)
        return Task(
            data.statement,
            data.steps,
            self.answer(data.expected, data.variables),
            {"difficulty": self.difficulty, "template": self.template},
            encode(self.prefix, 1, params.seed),
            self.version,
        )


class SymbolicAnalysisOne(AnalysisOne):
    answer = FullRealExpressionAnswer

    def input_variables(self, params: AnalysisOneParams) -> dict[str, VariableDomain]:
        # Plain metadata only: no SymPy construction on API paths.
        return {"x": "real"}


def generators() -> tuple[TaskGenerator[Any], ...]:
    result: list[TaskGenerator[Any]] = []
    for levels in MATRIX.values():
        for level, kinds in levels.items():
            for kind in kinds:
                index = len(result)
                cls = (
                    SymbolicAnalysisOne
                    if kind in {"composition", "inverse", "asymptote", "chain"}
                    else AnalysisOne
                )
                result.append(cls(kind, level, "AI" + chr(65 + index // 26) + chr(65 + index % 26)))
    return tuple(result)
