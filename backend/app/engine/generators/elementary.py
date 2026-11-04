"""Immutable elementary computational providers for AM1 1--23 (#235)."""

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from app.engine.answers.computational import (
    CategoryAnswer,
    FormulaAnswer,
    OrderedAnswer,
    RealSetAnswer,
)
from app.engine.answers.logic import LogicAnswer
from app.engine.codes import encode
from app.engine.generators import _elementary_equations as equations
from app.engine.generators import _elementary_functions as functions
from app.engine.generators import _elementary_logic as logic
from app.engine.generators import _elementary_trigonometry as trigonometry
from app.engine.generators._elementary_common import Built, ElementaryParams, set_diagram
from app.engine.generators._elementary_visuals import inverse_diagram
from app.engine.models import Answer, Task, TaskGenerator
from app.engine.prng import DeterministicRNG
from app.math_input.contracts import InputContract

# Prefixes are explicitly frozen; later deliveries append independent identities.
SPECS = (
    ("proposition", 1, "EFAA", "category"),
    ("compound-truth", 2, "EFAB", "category"),
    ("logic-negation-and", 2, "EFAC", "logic"),
    ("logic-negation-or", 2, "EFAD", "logic"),
    ("logic-negation-implication", 3, "EFAE", "logic"),
    ("logic-negation-equivalence", 3, "EFAF", "logic"),
    ("logic-negation-xor", 3, "EFAG", "logic"),
    ("quantifier-polynomial", 3, "EFAH", "category"),
    ("quantifier-order", 4, "EFAI", "category"),
    ("domain-rational", 1, "EFAJ", "real_set"),
    ("domain-quartic-root", 2, "EFAK", "real_set"),
    ("domain-root-quotient", 3, "EFAL", "real_set"),
    ("domain-log-ratio", 4, "EFAM", "real_set"),
    ("domain-arcsin-affine", 1, "EFAN", "real_set"),
    ("domain-arccos-square", 2, "EFAO", "real_set"),
    ("domain-arctan-rational", 2, "EFAP", "real_set"),
    ("parity", 2, "EFAQ", "category"),
    ("composition-affine", 1, "EFAR", "tuple"),
    ("composition-reciprocal-square", 3, "EFAS", "tuple"),
    ("composition-root-power", 3, "EFAT", "tuple"),
    ("composition-abs-root", 4, "EFAU", "tuple"),
    ("inverse-mobius", 2, "EFAV", "tuple"),
    ("inverse-quadratic-branch", 3, "EFAW", "tuple"),
    ("inverse-negative-fourth", 3, "EFAX", "tuple"),
    ("inverse-exponential", 2, "EFAY", "tuple"),
    ("inverse-logarithm", 2, "EFAZ", "tuple"),
    ("inverse-semicircle-branch", 4, "EFBA", "tuple"),
    ("equation-repeated-polynomial", 1, "EFBB", "real_set"),
    ("equation-biquadratic", 2, "EFBC", "real_set"),
    ("equation-rational-linear", 2, "EFBD", "real_set"),
    ("equation-rational-cancel", 4, "EFBE", "real_set"),
    ("inequality-squared-factors", 3, "EFBF", "real_set"),
    ("inequality-odd-polynomial", 3, "EFBG", "real_set"),
    ("inequality-rational-sign", 3, "EFBH", "real_set"),
    ("inequality-rational-subtract", 4, "EFBI", "real_set"),
    ("exponential-linear", 1, "EFBJ", "real_set"),
    ("exponential-substitution", 3, "EFBK", "real_set"),
    ("exponential-reciprocal-exponent", 4, "EFBL", "real_set"),
    ("exponential-mixed-bases", 3, "EFBM", "real_set"),
    ("exponential-product-inequality", 3, "EFBN", "real_set"),
    ("exponential-reciprocal-substitution", 4, "EFBO", "real_set"),
    ("log-value-product", 1, "EFBP", "formula"),
    ("log-value-change-base", 2, "EFBQ", "formula"),
    ("log-value-ratio", 3, "EFBR", "formula"),
    ("log-equation-power", 1, "EFBS", "real_set"),
    ("log-equation-difference", 2, "EFBT", "real_set"),
    ("log-equation-quadratic", 3, "EFBU", "real_set"),
    ("log-inequality-linear", 2, "EFBV", "real_set"),
    ("log-inequality-difference", 4, "EFBW", "real_set"),
    ("log-inequality-opposite-bases", 4, "EFBX", "real_set"),
    ("trig-domain-tan-ratio", 3, "EFBY", "tuple"),
    ("trig-domain-tan-sum", 3, "EFBZ", "tuple"),
    ("trig-domain-half-angle", 4, "EFCA", "tuple"),
    ("trig-linearization-square", 2, "EFCB", "formula"),
    ("trig-linearization-fourth", 3, "EFCC", "formula"),
    ("inverse-trig-values", 1, "EFCD", "formula"),
    ("inverse-trig-nested", 3, "EFCE", "formula"),
    ("inverse-trig-cot-branch", 4, "EFCF", "formula"),
    ("trig-equation-cos-mixed", 5, "EFCG", "tuple"),
    ("trig-equation-sine-sum", 2, "EFCH", "tuple"),
    ("trig-equation-tangent-sum", 5, "EFCI", "tuple"),
    ("trig-equation-exponential", 4, "EFCJ", "tuple"),
    ("trig-inequality-sine", 3, "EFCK", "tuple"),
    ("trig-inequality-sine-cosine", 4, "EFCL", "tuple"),
    ("trig-inequality-cotangent", 5, "EFCM", "tuple"),
    ("domain-root-rational", 2, "EFCN", "real_set"),
    ("domain-arccot-affine", 1, "EFCO", "real_set"),
    ("log-value-root", 2, "EFCP", "formula"),
    ("exponential-rational-inequality", 4, "EFCQ", "real_set"),
    ("trig-domain-double-angle", 2, "EFCR", "tuple"),
    ("inverse-trig-atan-cot", 2, "EFCS", "formula"),
    ("quantifier-cubic-witness", 4, "EFCT", "category"),
    ("quantifier-total-order", 3, "EFCU", "category"),
    ("proposition-triangle", 1, "EFCV", "category"),
    ("quantifier-power", 3, "EFCW", "category"),
    ("quantifier-trigonometric", 4, "EFCX", "category"),
    ("logic-negation-not", 1, "EFCY", "logic"),
    ("domain-exponential-root", 3, "EFCZ", "real_set"),
    ("domain-arcsin-square", 3, "EFDA", "real_set"),
    ("domain-quadratic-rational", 1, "EFDB", "real_set"),
    ("quantifier-product", 4, "EFDC", "category"),
)

_ANSWERS: dict[str, type[Answer]] = {
    "category": CategoryAnswer,
    "logic": LogicAnswer,
    "formula": FormulaAnswer,
    "tuple": OrderedAnswer,
    "real_set": RealSetAnswer,
}


def describe(template: str) -> InputContract:
    if template.startswith("trig-") or template.startswith("inverse-trig-"):
        if template.startswith("trig-linearization-"):
            return InputContract("formula", symbols=(("x", "real"),))
        if template.startswith("inverse-trig-"):
            return InputContract("formula")
        periodic = InputContract(
            "tuple",
            components=(InputContract("formula"), InputContract("real_set")),
            labels=("Period", "Base set"),
        )
        if template == "trig-equation-cos-mixed":
            return InputContract(
                "tuple", components=(periodic, periodic), labels=("First branch", "Second branch")
            )
        return periodic
    if template.startswith("proposition"):
        return InputContract(
            "category", choices=("true_proposition", "false_proposition", "not_a_proposition")
        )
    if template.startswith("logic-negation-"):
        atoms = (
            ("p",)
            if template.endswith("-not")
            else ("p", "q", "r")
            if template.endswith("-equivalence")
            else ("p", "q")
        )
        return InputContract("logic", choices=atoms)
    if template == "compound-truth" or template.startswith("quantifier-"):
        return InputContract("category", choices=("true", "false"))
    if template == "parity":
        return InputContract("category", choices=("even", "odd", "neither"))
    if template.startswith("domain-"):
        return InputContract("real_set")
    if template.startswith(
        ("equation-", "inequality-", "exponential-", "log-equation-", "log-inequality-")
    ):
        return InputContract("real_set")
    if template.startswith("log-value-"):
        return InputContract("formula")
    formula = InputContract("formula", symbols=(("x", "real"),))
    real_set = InputContract("real_set")
    if template.startswith("composition-"):
        return InputContract(
            "tuple",
            components=(formula, real_set) * 4,
            labels=tuple(
                name + suffix
                for name in ("FF", "FG", "GF", "GG")
                for suffix in (" expression", " domain")
            ),
        )
    if template.startswith("inverse-"):
        return InputContract(
            "tuple",
            components=(formula, real_set, real_set),
            labels=("Inverse expression", "Inverse domain", "Inverse range"),
        )
    raise ValueError(template)


@lru_cache(maxsize=8192)
def build_form(template: str, a: int, b: int, c: int, variant: int) -> Built:
    params = ElementaryParams(seed=0, a=a, b=b, c=c, variant=variant)
    if template.startswith("trig-") or template.startswith("inverse-trig-"):
        return trigonometry.evaluate(template, params)
    elif template.startswith(("domain-", "composition-", "inverse-")) or template == "parity":
        return functions.evaluate(template, params)
    elif template.startswith(("equation-", "inequality-", "exponential-", "log-")):
        return equations.evaluate(template, params)
    return logic.evaluate(template, params)


@dataclass(frozen=True)
class Elementary:
    template: str
    difficulty: int
    prefix: str
    kind: str
    code_version = 1
    params = ElementaryParams
    requires: tuple[str, ...] = ()

    @property
    def version(self) -> str:
        return f"elementary-{self.template}-v1"

    @property
    def family(self) -> str:
        return f"elementary-{self.template}"

    @property
    def answer(self) -> type[Answer]:
        return _ANSWERS[self.kind]

    @property
    def step_text(self) -> dict[str, str]:
        return {
            "method": "Apply the stated definition and retain every domain restriction.",
            "calculation": "Substitute the sampled parameters and compute exactly.",
            "result": "Read off the complete requested result.",
        }

    def draw(self, seed: int) -> ElementaryParams:
        rng = DeterministicRNG(seed)
        return ElementaryParams(
            seed=seed,
            a=1 + rng.randbelow(4),
            b=1 + rng.randbelow(4),
            c=1 + rng.randbelow(4),
            variant=rng.randbelow(6),
        )

    def input_contract(self, params: ElementaryParams) -> InputContract:
        return describe(self.template)

    def build(self, params: ElementaryParams) -> Task:
        built = build_form(self.template, params.a, params.b, params.c, params.variant)
        return Task(
            built.statement,
            built.steps,
            built.answer,
            {"difficulty": self.difficulty, "template": self.template},
            encode(self.prefix, 1, params.seed),
            self.version,
        )

    def solution_visual(self, params: ElementaryParams) -> dict[str, Any] | None:
        if self.template.startswith("inverse-") and not self.template.startswith("inverse-trig-"):
            return inverse_diagram(self.template, params)
        return set_diagram(
            build_form(self.template, params.a, params.b, params.c, params.variant).sets
        )


def generators() -> tuple[TaskGenerator[Any], ...]:
    return tuple(Elementary(*spec) for spec in SPECS)
