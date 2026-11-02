"""Bounded radical exercises corresponding to algebra30 exercises 1(a) and 3(a)."""

from typing import Any, Literal

import sympy as sp
from pydantic import Field, field_validator

from app.engine.answers.expression import ExpressionAnswer
from app.engine.codes import encode
from app.engine.models import Drawn, Outcome, Step, Task, TaskGenerator
from app.engine.prng import DeterministicRNG
from app.math_input import MathNode, build_expression

Radicand = Literal[2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19]
RADICANDS: tuple[Radicand, ...] = (2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19)


class RadicandParams(Drawn):
    radicand: Radicand

    @field_validator("radicand", mode="before")
    @classmethod
    def strict_radicand(cls, value: Any) -> Any:
        if type(value) is not int:
            raise ValueError("Radicand must be an integer")
        return value


class RadicalParams(RadicandParams):
    coefficient: int = Field(ge=1, le=5)
    factor: int = Field(ge=2, le=5)


class RationalizeParams(RadicandParams):
    coefficient: int = Field(ge=1, le=9)


class SimplifiedRadicalAnswer(ExpressionAnswer):
    """Reject an integer square root when a square factor is still inside it."""

    def check(self, tree: MathNode) -> Outcome:
        result = super().check(tree)
        if result != "correct":
            return result
        stack = [tree]
        while stack:
            node = stack.pop()
            root_arg = None
            if node.kind == "function" and node.value == "sqrt":
                root_arg = node.children[0]
            elif node.kind == "binary" and node.value == "^":
                exponent = build_expression(node.children[1], evaluate=True)
                if exponent == sp.Rational(1, 2):
                    root_arg = node.children[0]
            if root_arg is not None:
                number = build_expression(root_arg, evaluate=True)
                if number.is_Integer and number >= 0:
                    root = sp.sqrt(number)
                    if root.is_Integer or root.as_coeff_Mul()[0] != 1:
                        return "incorrect"
            stack.extend(node.children)
        return "correct"


class RationalizedAnswer(ExpressionAnswer):
    """Require equivalent answers to have rational denominators in their input."""

    def check(self, tree: MathNode) -> Outcome:
        result = super().check(tree)
        if result != "correct":
            return result
        stack = [tree]
        while stack:
            node = stack.pop()
            if node.kind == "binary" and node.value == "/":
                if build_expression(node.children[1], evaluate=True).is_rational is not True:
                    return "incorrect"
            if node.kind == "binary" and node.value == "^":
                exponent = build_expression(node.children[1], evaluate=True)
                if exponent.is_negative is True:
                    base = build_expression(node.children[0], evaluate=True)
                    if (base**-exponent).is_rational is not True:
                        return "incorrect"
            stack.extend(node.children)
        return "correct"


class SimplifyRadicals:
    version = "algebra-simplify-radicals-v1"
    prefix = "ASR"
    family = "algebra-simplify-radicals"
    code_version = 1
    params = RadicalParams
    answer = SimplifiedRadicalAnswer
    requires: tuple[str, ...] = ()
    step_text = {
        "simplify_radical": "Extract the square factor from the radical.",
        "combine": "Combine the like radical terms.",
    }

    def draw(self, seed: int) -> RadicalParams:
        rng = DeterministicRNG(seed)
        return RadicalParams(
            seed=seed,
            coefficient=1 + rng.randbelow(5),
            factor=2 + rng.randbelow(4),
            radicand=RADICANDS[rng.randbelow(len(RADICANDS))],
        )

    def build(self, params: RadicalParams) -> Task:
        root = sp.sqrt(params.radicand)
        large = params.factor**2 * params.radicand
        expected = (params.coefficient - params.factor) * root
        if sp.simplify(params.coefficient * root - sp.sqrt(large) - expected) != 0:
            raise ValueError("Radical simplification failed verification")
        return Task(
            statement=(
                rf"Simplify \({params.coefficient}\sqrt{{{params.radicand}}}"
                rf"-\sqrt{{{large}}}\)."
            ),
            steps=(
                Step(
                    "simplify_radical",
                    rf"\sqrt{{{large}}}={params.factor}\sqrt{{{params.radicand}}}",
                ),
                Step(
                    "combine",
                    rf"({params.coefficient}-{params.factor})\sqrt{{{params.radicand}}}={sp.latex(expected)}",
                ),
            ),
            answer=SimplifiedRadicalAnswer(expected, {}),
            metadata={"difficulty": 1, "template": "simplify-radicals"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class RationalizeDenominator:
    version = "algebra-rationalize-denominator-v1"
    prefix = "ARD"
    family = "algebra-rationalize-denominator"
    code_version = 1
    params = RationalizeParams
    answer = RationalizedAnswer
    requires: tuple[str, ...] = ()
    step_text = {
        "conjugate": "Multiply the numerator and denominator by the conjugate.",
        "simplify": "Simplify the denominator using the difference of squares.",
    }

    def draw(self, seed: int) -> RationalizeParams:
        rng = DeterministicRNG(seed)
        return RationalizeParams(
            seed=seed,
            coefficient=1 + rng.randbelow(9),
            radicand=RADICANDS[rng.randbelow(len(RADICANDS))],
        )

    def build(self, params: RationalizeParams) -> Task:
        a, d = params.coefficient, params.radicand
        denominator = a**2 - d
        expected = (a - sp.sqrt(d)) / denominator
        if sp.simplify(expected * (a + sp.sqrt(d)) - 1) != 0:
            raise ValueError("Rationalization failed verification")
        return Task(
            statement=rf"Rationalize the denominator of \(\frac{{1}}{{{a}+\sqrt{{{d}}}}}\).",
            steps=(
                Step(
                    "conjugate",
                    rf"\frac{{1}}{{{a}+\sqrt{{{d}}}}}=\frac{{{a}-\sqrt{{{d}}}}}{{({a}+\sqrt{{{d}}})({a}-\sqrt{{{d}}})}}",
                ),
                Step(
                    "simplify", rf"\frac{{{a}-\sqrt{{{d}}}}}{{{denominator}}}={sp.latex(expected)}"
                ),
            ),
            answer=RationalizedAnswer(expected, {}),
            metadata={"difficulty": 2, "template": "rationalize-denominator"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


def generators() -> tuple[TaskGenerator[Any], ...]:
    return SimplifyRadicals(), RationalizeDenominator()
