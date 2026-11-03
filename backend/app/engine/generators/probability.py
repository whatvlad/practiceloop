"""Frozen independently versioned Probability and Statistics generator providers."""

from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, ClassVar

from app.engine.answers.structured import (
    BooleanAnswer,
    FiniteSetAnswer,
    IntervalAnswer,
    RealScalarAnswer,
)
from app.engine.generators import _probability_continuous as continuous
from app.engine.generators import _probability_discrete as discrete
from app.engine.generators import _probability_events as events
from app.engine.generators import _probability_inference as inference
from app.engine.generators import _probability_statistics as statistics
from app.engine.generators._probability_common import Built, ProbabilityParams
from app.engine.models import Answer, Task, TaskGenerator
from app.engine.prng import DeterministicRNG

# Published identity is explicit and independent of any topic ordering.
SPECS = (
    ("events-equal", 1, "PSAA", "expression"),
    ("events-complement", 2, "PSAB", "expression"),
    ("events-at-least-one", 2, "PSAC", "expression"),
    ("events-union", 3, "PSAD", "expression"),
    ("events-intersection", 3, "PSAE", "expression"),
    ("events-selection", 4, "PSAF", "expression"),
    ("events-set", 4, "PSAG", "finite_set"),
    ("events-independence", 5, "PSAH", "boolean"),
    ("conditional-table", 1, "PSAI", "expression"),
    ("conditional-replacement", 2, "PSAJ", "expression"),
    ("conditional-without", 2, "PSAK", "expression"),
    ("conditional-total", 3, "PSAL", "expression"),
    ("conditional-bayes-two", 4, "PSAM", "expression"),
    ("conditional-bayes-three", 5, "PSAN", "expression"),
    ("conditional-tree", 5, "PSAO", "expression"),
    ("finite-normalize", 1, "PSAP", "expression"),
    ("finite-point", 2, "PSAQ", "expression"),
    ("finite-cdf", 2, "PSAR", "expression"),
    ("finite-tail", 3, "PSAS", "expression"),
    ("finite-support", 3, "PSAT", "finite_set"),
    ("finite-jump", 4, "PSAU", "expression"),
    ("finite-transform", 5, "PSAV", "expression"),
    ("discrete-bernoulli", 1, "PSAW", "expression"),
    ("discrete-binomial", 2, "PSAX", "expression"),
    ("discrete-geometric", 3, "PSAY", "expression"),
    ("discrete-hypergeometric", 4, "PSAZ", "expression"),
    ("discrete-poisson", 5, "PSBA", "expression"),
    ("continuous-uniform", 1, "PSBB", "expression"),
    ("continuous-normalize", 2, "PSBC", "expression"),
    ("continuous-support", 2, "PSBD", "interval"),
    ("continuous-piecewise-cdf", 3, "PSBE", "expression"),
    ("continuous-interval", 3, "PSBF", "expression"),
    ("continuous-exponential-tail", 4, "PSBG", "expression"),
    ("continuous-memoryless", 4, "PSBH", "expression"),
    ("continuous-exponential-quantile", 4, "PSBI", "expression"),
    ("continuous-normal-standardize", 5, "PSBJ", "expression"),
    ("continuous-normal-probability", 5, "PSBK", "expression"),
    ("continuous-normal-quantile", 5, "PSBL", "expression"),
    ("moments-mean", 1, "PSBM", "expression"),
    ("moments-variance", 2, "PSBN", "expression"),
    ("moments-deviation", 2, "PSBO", "expression"),
    ("moments-affine-mean", 3, "PSBP", "expression"),
    ("moments-affine-variance", 3, "PSBQ", "expression"),
    ("moments-marginal", 4, "PSBR", "expression"),
    ("moments-conditional", 4, "PSBS", "expression"),
    ("moments-covariance", 5, "PSBT", "expression"),
    ("moments-correlation", 5, "PSBU", "expression"),
    ("moments-independence", 5, "PSBV", "boolean"),
    ("sample-mean", 1, "PSBW", "expression"),
    ("sample-weighted", 1, "PSBX", "expression"),
    ("sample-median", 2, "PSBY", "expression"),
    ("sample-modes", 2, "PSBZ", "finite_set"),
    ("sample-quartile", 3, "PSCA", "expression"),
    ("sample-iqr", 3, "PSCB", "expression"),
    ("sample-population-variance", 4, "PSCC", "expression"),
    ("sample-sample-variance", 4, "PSCD", "expression"),
    ("sample-deviation", 4, "PSCE", "expression"),
    ("sample-correlation", 5, "PSCF", "expression"),
    ("sample-slope", 5, "PSCG", "expression"),
    ("sample-intercept", 5, "PSCH", "expression"),
    ("ci-mean-z", 1, "PSCI", "interval"),
    ("ci-mean-t", 2, "PSCJ", "interval"),
    ("ci-lower", 3, "PSCK", "interval"),
    ("ci-upper", 3, "PSCL", "interval"),
    ("ci-proportion", 4, "PSCM", "interval"),
    ("ci-paired", 5, "PSCN", "interval"),
    ("ci-difference", 5, "PSCO", "interval"),
    ("test-z-statistic", 1, "PSCP", "expression"),
    ("test-z-decision", 2, "PSCQ", "boolean"),
    ("test-t-statistic", 3, "PSCR", "expression"),
    ("test-t-decision", 3, "PSCS", "boolean"),
    ("test-proportion", 4, "PSCT", "boolean"),
    ("test-paired", 5, "PSCU", "boolean"),
    ("test-difference", 5, "PSCV", "boolean"),
)

_MODULES = {
    "events": events,
    "conditional": events,
    "finite": discrete,
    "discrete": discrete,
    "continuous": continuous,
    "moments": statistics,
    "sample": statistics,
    "ci": inference,
    "test": inference,
}

_BUILDERS: dict[str, Callable[[str, ProbabilityParams], Built]] = {
    "events": events.evaluate,
    "conditional": events.evaluate,
    "finite": discrete.evaluate,
    "discrete": discrete.evaluate,
    "continuous": continuous.evaluate,
    "moments": statistics.evaluate,
    "sample": statistics.evaluate,
    "ci": inference.evaluate,
    "test": inference.evaluate,
}


@lru_cache(maxsize=4096)
def _build(template: str, a: int, b: int, c: int) -> Built:
    # Only mathematical values are cached; seed/code never enter this result.
    return _BUILDERS[template.split("-")[0]](template, ProbabilityParams(seed=0, a=a, b=b, c=c))


@dataclass(frozen=True)
class Probability:
    template: str
    difficulty: int
    prefix: str
    code_version = 1
    params = ProbabilityParams
    answer: ClassVar[type[Answer]] = RealScalarAnswer
    requires: tuple[str, ...] = ()

    @property
    def version(self) -> str:
        return f"probability-{self.template}-v1"

    @property
    def family(self) -> str:
        return f"probability-{self.template}"

    @property
    def step_text(self) -> dict[str, str]:
        module = _MODULES[self.template.split("-")[0]]
        return {
            "method": module.REASONS[self.template],
            "substitution": "Substitute the stated data and simplify the requested quantity.",
            "result": "Write the requested answer.",
        }

    def draw(self, seed: int) -> ProbabilityParams:
        rng = DeterministicRNG(seed)
        return ProbabilityParams(
            seed=seed, a=1 + rng.randbelow(5), b=1 + rng.randbelow(5), c=1 + rng.randbelow(5)
        )

    def build(self, params: ProbabilityParams) -> Task:
        from app.engine.codes import encode

        data = _build(self.template, params.a, params.b, params.c)
        declared_kind = getattr(self.answer, "kind", None)
        if not isinstance(declared_kind, str) or data.answer.kind != declared_kind:
            raise ValueError("Built answer differs from declared input kind")
        return Task(
            data.statement,
            data.steps,
            data.answer,
            {"difficulty": self.difficulty, "template": self.template},
            encode(self.prefix, 1, params.seed),
            self.version,
        )


class BooleanProbability(Probability):
    answer = BooleanAnswer


class SetProbability(Probability):
    answer = FiniteSetAnswer


class IntervalProbability(Probability):
    answer = IntervalAnswer


def generators() -> tuple[TaskGenerator[Any], ...]:
    classes = {
        "expression": Probability,
        "boolean": BooleanProbability,
        "finite_set": SetProbability,
        "interval": IntervalProbability,
    }
    return tuple(classes[kind](name, level, prefix) for name, level, prefix, kind in SPECS)
