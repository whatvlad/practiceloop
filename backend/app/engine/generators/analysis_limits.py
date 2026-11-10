"""Frozen providers for the computational sequence and continuity expansion (#236)."""

from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from pydantic import Field

from app.engine.answers.computational import (
    CategoryAnswer,
    FormulaAnswer,
    LimitAnswer,
    OrderedAnswer,
)
from app.engine.codes import encode
from app.engine.generators import _function_limits as functions
from app.engine.generators import _sequence_limits as sequences
from app.engine.generators._elementary_common import Built
from app.engine.models import Answer, Drawn, Task
from app.engine.prng import DeterministicRNG
from app.math_input.contracts import InputContract

LIMIT = InputContract("limit_result")
CONSTANT = InputContract("formula")
BOUNDS_KIND = InputContract("category", choices=sequences.BOUNDS)
BOUNDS = InputContract(
    "tuple", components=(BOUNDS_KIND, CONSTANT, CONSTANT), labels=sequences.BOUND_LABELS
)
UPPER = InputContract("tuple", components=(BOUNDS_KIND, CONSTANT), labels=sequences.UPPER_LABELS)
TAIL = InputContract(
    "tuple",
    components=(InputContract("category", choices=sequences.MONOTONICITY), CONSTANT),
    labels=sequences.MONOTONICITY_LABELS,
)
SIDES = InputContract("tuple", components=(LIMIT, LIMIT, LIMIT), labels=functions.SIDES)
ASYMPTOTES = InputContract(
    "tuple",
    components=(
        InputContract("real_set"),
        *(InputContract("formula", symbols=functions.REAL_X),) * 2,
    ),
    labels=functions.ASYMPTOTES,
)
DOMAIN_ASYMPTOTES = InputContract(
    "tuple",
    components=(InputContract("real_set"), *ASYMPTOTES.components),
    labels=functions.DOMAIN_ASYMPTOTES,
)
JOINS = InputContract("tuple", components=(CONSTANT, CONSTANT), labels=functions.JOINS)
DISCONTINUITY = InputContract(
    "tuple",
    components=(CONSTANT, LIMIT, LIMIT, InputContract("category", choices=functions.DISCONTINUITY)),
    labels=functions.DISCONTINUITY_LABELS,
)
FREE_JOIN = InputContract(
    "tuple", components=(CONSTANT, InputContract("real_set")), labels=functions.UNRESTRICTED_JOIN
)
TWO_DISCONTINUITIES = InputContract(
    "tuple", components=(DISCONTINUITY, DISCONTINUITY), labels=functions.TWO_LOCATIONS
)
ROOT = InputContract("tuple", components=(CONSTANT, CONSTANT), labels=functions.ROOT)
# #259: asymptotes by the slope and offset limits at each end of the domain.
REAL_SET = InputContract("real_set")
ENDS = InputContract(
    "tuple", components=(REAL_SET, LIMIT, LIMIT, LIMIT, LIMIT), labels=functions.ENDS
)
RIGHT_END = InputContract("tuple", components=(REAL_SET, LIMIT, LIMIT), labels=functions.RIGHT_END)
PERIODIC = InputContract("tuple", components=(CONSTANT, REAL_SET), labels=("Period", "Base set"))
PERIODIC_ENDS = InputContract(
    "tuple", components=(PERIODIC, LIMIT, LIMIT, LIMIT, LIMIT), labels=functions.ENDS
)
CONTINUITY_AT = InputContract(
    "tuple",
    components=(LIMIT, LIMIT, InputContract("category", choices=functions.CONTINUITY_CLASSES)),
    labels=functions.CONTINUITY_AT,
)
ANSWERS: dict[str, type[Answer]] = {
    "category": CategoryAnswer,
    "formula": FormulaAnswer,
    "limit_result": LimitAnswer,
    "tuple": OrderedAnswer,
}

SEQUENCES = "functions-and-sequences"
FUNCTIONS = "limits-and-continuity"
# Explicit prefixes are permanent and independent of the order of these entries.
SPECS = (
    (sequences.bound_trigonometric, SEQUENCES, 2, "SLAA", BOUNDS),
    (sequences.bound_radical, SEQUENCES, 1, "SLAB", UPPER),
    (sequences.monotone_factorial, SEQUENCES, 4, "SLAC", TAIL),
    (sequences.monotone_radical, SEQUENCES, 3, "SLAD", TAIL),
    (sequences.definition_reciprocal, SEQUENCES, 2, "SLAE", LIMIT),
    (sequences.definition_growth, SEQUENCES, 2, "SLAF", LIMIT),
    (sequences.rational_leading, SEQUENCES, 3, "SLAG", LIMIT),
    (sequences.factorial_limit, SEQUENCES, 4, "SLAH", LIMIT),
    (sequences.conjugate_sequence, SEQUENCES, 4, "SLAI", LIMIT),
    (sequences.squeeze_oscillation, SEQUENCES, 3, "SLAJ", LIMIT),
    (sequences.squeeze_floor, SEQUENCES, 4, "SLAK", LIMIT),
    (sequences.squeeze_root, SEQUENCES, 4, "SLAL", LIMIT),
    (sequences.squeeze_sum, SEQUENCES, 5, "SLAM", LIMIT),
    (sequences.exponential_power, SEQUENCES, 4, "SLAN", LIMIT),
    (sequences.exponential_difference, SEQUENCES, 5, "SLAO", LIMIT),
    (sequences.infinite_exponential, SEQUENCES, 3, "SLAP", LIMIT),
    (sequences.bound_conjugate, SEQUENCES, 2, "SLAQ", BOUNDS),
    (sequences.monotone_ratio, SEQUENCES, 4, "SLAR", TAIL),
    (sequences.rational_zero, SEQUENCES, 2, "SLAS", LIMIT),
    (sequences.arithmetic_sum_ratio, SEQUENCES, 3, "SLAT", LIMIT),
    (sequences.root_exponential_ratio, SEQUENCES, 5, "SLAU", LIMIT),
    (sequences.logarithmic_power, SEQUENCES, 5, "SLAV", LIMIT),
    (sequences.infinite_factorial, SEQUENCES, 4, "SLAW", LIMIT),
    (sequences.divergent_oscillation, SEQUENCES, 3, "SLAX", LIMIT),
    (sequences.scaled_conjugate, SEQUENCES, 4, "SLAY", LIMIT),
    (functions.definition_pole, FUNCTIONS, 1, "FLAA", LIMIT),
    (functions.rational_cancellation, FUNCTIONS, 2, "FLAB", LIMIT),
    (functions.radical_cancellation, FUNCTIONS, 3, "FLAC", LIMIT),
    (functions.exponential_dominance, FUNCTIONS, 2, "FLAD", LIMIT),
    (functions.absolute_jump, FUNCTIONS, 2, "FLAE", SIDES),
    (functions.essential_exponential, FUNCTIONS, 4, "FLAF", SIDES),
    (functions.squeeze_function, FUNCTIONS, 3, "FLAG", LIMIT),
    (functions.infinitesimal_exp_sin, FUNCTIONS, 3, "FLAH", LIMIT),
    (functions.infinitesimal_log, FUNCTIONS, 4, "FLAI", LIMIT),
    (functions.infinitesimal_power, FUNCTIONS, 5, "FLAJ", LIMIT),
    (functions.asymptote_rational, FUNCTIONS, 4, "FLAK", ASYMPTOTES),
    (functions.asymptote_inverse_trig, FUNCTIONS, 4, "FLAL", ASYMPTOTES),
    (functions.continuity_sine, FUNCTIONS, 4, "FLAM", JOINS),
    (functions.continuity_reciprocal, FUNCTIONS, 3, "FLAN", CONSTANT),
    (functions.discontinuity_arctan, FUNCTIONS, 4, "FLAO", DISCONTINUITY),
    (functions.discontinuity_oscillatory, FUNCTIONS, 5, "FLAP", DISCONTINUITY),
    (functions.certified_root, FUNCTIONS, 5, "FLAQ", ROOT),
    (functions.two_sided_absolute, FUNCTIONS, 2, "FLAR", SIDES),
    (functions.squeeze_at_infinity, FUNCTIONS, 2, "FLAS", LIMIT),
    (functions.infinitesimal_inverse_trig, FUNCTIONS, 4, "FLAT", LIMIT),
    (functions.horizontal_asymptote, FUNCTIONS, 3, "FLAU", ASYMPTOTES),
    (functions.discontinuity_removable, FUNCTIONS, 3, "FLAV", DISCONTINUITY),
    (functions.discontinuity_infinite, FUNCTIONS, 3, "FLAW", DISCONTINUITY),
    (functions.certified_cubic, FUNCTIONS, 5, "FLAX", ROOT),
    (functions.radical_asymptote, FUNCTIONS, 5, "FLAY", ASYMPTOTES),
    (functions.high_order_pole, FUNCTIONS, 4, "FLAZ", ASYMPTOTES),
    (functions.conjugate_at_infinity, FUNCTIONS, 3, "FLBA", LIMIT),
    (functions.removable_trigonometric, FUNCTIONS, 2, "FLBB", LIMIT),
    (functions.power_difference, FUNCTIONS, 4, "FLBC", LIMIT),
    (functions.finite_heine_limit, FUNCTIONS, 1, "FLBD", LIMIT),
    (functions.heine_at_infinity, FUNCTIONS, 2, "FLBE", LIMIT),
    (functions.continuity_free_parameter, FUNCTIONS, 4, "FLBF", FREE_JOIN),
    (functions.discontinuity_pole_and_hole, FUNCTIONS, 5, "FLBG", TWO_DISCONTINUITIES),
    (functions.unique_log_exponential_root, FUNCTIONS, 4, "FLBH", CONSTANT),
    (functions.rational_pole_and_domain, FUNCTIONS, 4, "FLBI", DOMAIN_ASYMPTOTES),
    (functions.exponential_pole, FUNCTIONS, 4, "FLBJ", ASYMPTOTES),
    # #257
    (sequences.bound_root_exponential, SEQUENCES, 3, "SLAZ", BOUNDS),
    (sequences.bound_geometric_sum, SEQUENCES, 4, "SLBA", BOUNDS),
    (sequences.monotone_exponential_difference, SEQUENCES, 4, "SLBB", TAIL),
    (sequences.monotone_rational, SEQUENCES, 3, "SLBC", TAIL),
    (sequences.monotone_conjugate, SEQUENCES, 3, "SLBD", TAIL),
    (sequences.definition_root, SEQUENCES, 2, "SLBE", LIMIT),
    (sequences.definition_exponential, SEQUENCES, 2, "SLBF", LIMIT),
    (sequences.product_leading_orders, SEQUENCES, 4, "SLBG", LIMIT),
    (sequences.competing_exponentials, SEQUENCES, 4, "SLBH", LIMIT),
    (sequences.radical_degree, SEQUENCES, 3, "SLBI", LIMIT),
    (sequences.root_rational_sum, SEQUENCES, 4, "SLBJ", LIMIT),
    (sequences.negative_growing_power, SEQUENCES, 4, "SLBK", LIMIT),
    (sequences.product_of_powers, SEQUENCES, 5, "SLBL", LIMIT),
    (sequences.reciprocal_power, SEQUENCES, 3, "SLBM", LIMIT),
    (sequences.rational_growth, SEQUENCES, 2, "SLBN", LIMIT),
    (sequences.radical_difference_growth, SEQUENCES, 3, "SLBO", LIMIT),
    (sequences.inverse_trig_ratio, SEQUENCES, 3, "SLBP", LIMIT),
    (sequences.root_exponential_sum, SEQUENCES, 4, "SLBQ", LIMIT),
    (sequences.root_polynomial, SEQUENCES, 3, "SLBR", LIMIT),
    (sequences.quartic_conjugate, SEQUENCES, 4, "SLBS", LIMIT),
    (sequences.conjugate_ratio, SEQUENCES, 4, "SLBT", LIMIT),
    (sequences.factorial_degree_ratio, SEQUENCES, 4, "SLBU", LIMIT),
    (sequences.exponential_product_ratio, SEQUENCES, 4, "SLBV", LIMIT),
    (sequences.reciprocal_exponential_conjugate, SEQUENCES, 5, "SLBW", LIMIT),
    (sequences.product_radical, SEQUENCES, 3, "SLBX", LIMIT),
    (functions.rational_substitution, FUNCTIONS, 1, "FLBK", LIMIT),
    (functions.radical_quotient_zero, FUNCTIONS, 2, "FLBL", LIMIT),
    (functions.power_difference_quotient, FUNCTIONS, 3, "FLBM", LIMIT),
    (functions.leading_power_quotient, FUNCTIONS, 3, "FLBN", LIMIT),
    (functions.conjugate_minus_infinity, FUNCTIONS, 4, "FLBO", LIMIT),
    (functions.tangent_ratio, FUNCTIONS, 2, "FLBP", LIMIT),
    (functions.radical_linear_ratio, FUNCTIONS, 2, "FLBQ", LIMIT),
    (functions.cancelling_reciprocals, FUNCTIONS, 3, "FLBR", LIMIT),
    (functions.bounded_inverse_trig, FUNCTIONS, 3, "FLBS", SIDES),
    (functions.squeeze_arctan, FUNCTIONS, 3, "FLBT", LIMIT),
    (functions.sine_product_square, FUNCTIONS, 2, "FLBU", LIMIT),
    (functions.sine_radical, FUNCTIONS, 3, "FLBV", LIMIT),
    (functions.arctan_at_infinity, FUNCTIONS, 3, "FLBW", LIMIT),
    (functions.cosine_ratio_half_pi, FUNCTIONS, 4, "FLBX", LIMIT),
    (functions.log_cube_root, FUNCTIONS, 4, "FLBY", LIMIT),
    (functions.log_near_one, FUNCTIONS, 4, "FLBZ", LIMIT),
    (functions.tangent_power, FUNCTIONS, 5, "FLCA", LIMIT),
    (functions.root_difference, FUNCTIONS, 4, "FLCB", LIMIT),
    (functions.sine_quadratic_ratio, FUNCTIONS, 4, "FLCC", LIMIT),
    (functions.log_difference_infinity, FUNCTIONS, 3, "FLCD", LIMIT),
    (functions.log_quadratic_at_point, FUNCTIONS, 3, "FLCE", LIMIT),
    (functions.sine_power_product, FUNCTIONS, 3, "FLCF", LIMIT),
    (functions.radical_growth_asymptotes, FUNCTIONS, 4, "FLCG", RIGHT_END),
    (functions.oscillatory_remainder, FUNCTIONS, 4, "FLCH", ENDS),
    (functions.exponential_zero_denominator, FUNCTIONS, 5, "FLCI", ENDS),
    (functions.trig_periodic_poles, FUNCTIONS, 5, "FLCJ", PERIODIC_ENDS),
    (functions.continuity_log_ratio, FUNCTIONS, 4, "FLCK", CONTINUITY_AT),
    (functions.exp_join, FUNCTIONS, 5, "FLCL", JOINS),
    (functions.quartic_cubic_oblique, FUNCTIONS, 4, "FLCM", ENDS),
    (functions.radical_oblique_right, FUNCTIONS, 5, "FLCN", RIGHT_END),
    (functions.radical_quotient_right, FUNCTIONS, 4, "FLCO", RIGHT_END),
    (functions.rational_oblique_pole, FUNCTIONS, 3, "FLCP", DOMAIN_ASYMPTOTES),
    (functions.rational_oblique_pole_left, FUNCTIONS, 3, "FLCQ", DOMAIN_ASYMPTOTES),
)


class LimitParams(Drawn):
    a: int = Field(ge=1, le=5)
    b: int = Field(ge=1, le=5)
    c: int = Field(ge=1, le=5)


@lru_cache(maxsize=8192)
def build_form(evaluate: Callable[[int, int, int], Built], a: int, b: int, c: int) -> Built:
    return evaluate(a, b, c)


@dataclass(frozen=True, slots=True)
class AnalysisLimits:
    evaluate: Callable[[int, int, int], Built]
    topic: str
    difficulty: int
    prefix: str
    contract: InputContract
    code_version = 1
    params = LimitParams
    requires: tuple[str, ...] = ()

    @property
    def family(self) -> str:
        return "analysis1-limits-" + self.evaluate.__name__.replace("_", "-")

    @property
    def version(self) -> str:
        return self.family + "-v1"

    @property
    def answer(self) -> type[Answer]:
        return ANSWERS[self.contract.kind]

    @property
    def step_text(self) -> dict[str, str]:
        return {
            "method": "Identify the applicable definition or method.",
            "calculation": "Work with the given parameters.",
            "result": "Read off the exact result.",
        }

    def draw(self, seed: int) -> LimitParams:
        rng = DeterministicRNG(seed)
        return LimitParams(
            seed=seed, a=1 + rng.randbelow(5), b=1 + rng.randbelow(5), c=1 + rng.randbelow(5)
        )

    def input_contract(self, params: LimitParams) -> InputContract:
        return self.contract

    def build(self, params: LimitParams) -> Task:
        built = build_form(self.evaluate, params.a, params.b, params.c)
        return Task(
            built.statement,
            built.steps,
            built.answer,
            {"difficulty": self.difficulty},
            encode(self.prefix, self.code_version, params.seed),
            self.version,
        )

    def solution_visual(self, params: LimitParams) -> dict[str, Any] | None:
        from app.engine.generators._limit_visuals import diagrams

        diagram = diagrams.get(self.evaluate)
        if diagram is None:
            return None
        return diagram(params.a, params.b, params.c)


def generators() -> tuple[AnalysisLimits, ...]:
    return tuple(AnalysisLimits(*spec) for spec in SPECS)
