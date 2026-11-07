"""Local practice for arithmetic with complex numbers in algebraic form."""

import sympy as sp

from app.engine.answers.complex import ComplexAnswer
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task
from app.engine.prng import DeterministicRNG

OPERATIONS = ("add", "subtract", "multiply", "divide")
VARIATIONS = 10**12


def complex_seed(level: int, operation: str, variation: int) -> int:
    if level not in (1, 2, 3) or operation not in OPERATIONS or not 0 <= variation < VARIATIONS:
        raise ValueError("Invalid complex arithmetic settings")
    return ((level - 1) * len(OPERATIONS) + OPERATIONS.index(operation)) * VARIATIONS + variation


def color(latex: str, imaginary: bool = False) -> str:
    shade = "#ffb65c" if imaginary else "#65adff"
    return rf"\color{{{shade}}}{{{latex}}}"


def colored_complex(value, *, show_zero: bool = False) -> str:
    real, imaginary = sp.expand_complex(value).as_real_imag()
    parts = []
    if real != 0 or show_zero:
        parts.append(color(sp.latex(real)))
    if imaginary != 0 or show_zero:
        sign = "-" if imaginary < 0 else "+"
        magnitude = abs(imaginary)
        coefficient = "" if magnitude == 1 else sp.latex(magnitude)
        term = color(coefficient + "i", True)
        parts.append((sign if parts or sign == "-" else "") + term)
    return " ".join(parts) if parts else color("0")


class ComplexParameters(Drawn):
    level: int
    operation: str
    first: tuple[int, int]
    second: tuple[int, int]


class LocalComplexGenerator:
    version, prefix, family, code_version = "local-complex-v1", "LCX", "local-complex", 1
    params, answer, requires = ComplexParameters, ComplexAnswer, ()
    step_text = {
        "rewrite": "Write the original expression.",
        "standard": (
            "Write each number with its real part and its imaginary part. "
            "A missing part has coefficient zero."
        ),
        "parts": (
            "Remove the brackets, keeping the operation in front of each term. "
            "Group the real parts and the coefficients of i separately."
        ),
        "expand": "Multiply each term in the first bracket by each term in the second bracket.",
        "square": "Replace i squared by minus one. Group the real terms and coefficients of i.",
        "conjugate": (
            "Multiply the numerator and denominator by the conjugate of the denominator; "
            "the value of the fraction stays the same."
        ),
        "numerator_expand": (
            "Expand the numerator by multiplying every term in the first bracket "
            "by every term in the second."
        ),
        "numerator_square": (
            "In the numerator, replace i squared by minus one and combine "
            "the real and imaginary terms."
        ),
        "denominator_expand": "Expand the denominator by multiplying the terms in both brackets.",
        "denominator_square": (
            "The imaginary terms cancel in the denominator. Replace i squared by minus one."
        ),
        "fraction": "Substitute the simplified numerator and real denominator into the fraction.",
        "split": "Divide the real and imaginary parts separately by the denominator.",
        "result": "Simplify and write the result in algebraic form.",
    }

    def draw(self, seed: int) -> ComplexParameters:
        index = seed // VARIATIONS
        if not 0 <= index < 12:
            raise ValueError("Invalid complex arithmetic seed")
        level, operation = index // 4 + 1, OPERATIONS[index % 4]
        rng = DeterministicRNG(seed)
        bound = (3, 6, 10)[level - 1]

        def component() -> int:
            return rng.randbelow(2 * bound + 1) - bound

        first = (component(), component())
        second = (component(), component())
        if second == (0, 0):
            second = (1, 1)
        return ComplexParameters(
            seed=seed, level=level, operation=operation, first=first, second=second
        )

    def build(self, params: ComplexParameters) -> Task:
        a, b = params.first
        c, d = params.second
        z, w = a + b * sp.I, c + d * sp.I

        def fmt(value):
            return colored_complex(sp.expand(value))

        # Make zero coefficients explicit before applying the arithmetic rules.
        standard_z = colored_complex(z, show_zero=True)
        standard_w = colored_complex(w, show_zero=True)
        needs_zero = a == 0 or b == 0 or c == 0 or d == 0
        if params.operation in ("add", "subtract"):
            sign = "+" if params.operation == "add" else "-"
            factor = 1 if params.operation == "add" else -1
            value = sp.expand(z + factor * w)
            expression = rf"({sp.latex(z)}) {sign} ({sp.latex(w)})"
            real = color(rf"({a}) {sign} ({c})")
            imaginary = color(rf"(({b}) {sign} ({d}))i", True)
            steps = (Step("parts", rf"{real} + {imaginary}"),)
        elif params.operation == "multiply":
            value = sp.expand(z * w)
            expression = rf"({sp.latex(z)})({sp.latex(w)})"
            steps = (
                Step(
                    "expand",
                    color(rf"({a})({c})")
                    + "+"
                    + color(rf"({a})({d})i", True)
                    + "+"
                    + color(rf"({b})({c})i", True)
                    + "+"
                    + color(rf"({b})({d})i^2"),
                ),
                Step(
                    "square",
                    color(rf"({a * c})-({b * d})") + "+" + color(rf"(({a * d})+({b * c}))i", True),
                ),
            )
        else:
            value = sp.expand(z / w)
            conjugate = sp.conjugate(w)
            numerator = sp.expand(z * conjugate)
            denominator = c * c + d * d
            expression = rf"\frac{{{sp.latex(z)}}}{{{sp.latex(w)}}}"
            numerator_expanded = (
                color(rf"({a})({c})")
                + "+"
                + color(rf"({a})({-d})i", True)
                + "+"
                + color(rf"({b})({c})i", True)
                + "+"
                + color(rf"({b})({-d})i^2")
            )
            numerator_grouped = (
                color(rf"({a * c})-({b * -d})") + "+" + color(rf"(({a * -d})+({b * c}))i", True)
            )
            real, imaginary = sp.expand_complex(numerator).as_real_imag()
            steps = (
                Step(
                    "conjugate",
                    rf"\dfrac{{{color(rf'\left({sp.latex(z)}\right)')}"
                    rf"{color(rf'\left({sp.latex(conjugate)}\right)', True)}}}"
                    rf"{{{color(rf'\left({sp.latex(w)}\right)')}"
                    rf"{color(rf'\left({sp.latex(conjugate)}\right)', True)}}}",
                ),
                Step("numerator_expand", numerator_expanded),
                Step("numerator_square", numerator_grouped + "=" + fmt(numerator)),
                Step(
                    "denominator_expand",
                    color(rf"({c})({c})")
                    + "+"
                    + color(rf"({c})({-d})i", True)
                    + "+"
                    + color(rf"({d})({c})i", True)
                    + "+"
                    + color(rf"({d})({-d})i^2"),
                ),
                Step("denominator_square", rf"({c})^2+({d})^2={denominator}"),
                Step("fraction", rf"\dfrac{{{fmt(numerator)}}}{{{denominator}}}"),
                Step(
                    "split",
                    color(rf"\dfrac{{{sp.latex(real)}}}{{{denominator}}}")
                    + "+"
                    + color(rf"\dfrac{{{sp.latex(imaginary)}}}{{{denominator}}}i", True),
                ),
            )
        if needs_zero:
            if params.operation == "divide":
                standard = rf"\dfrac{{{standard_z}}}{{{standard_w}}}"
            else:
                symbol = {"add": "+", "subtract": "-", "multiply": r"\cdot"}[params.operation]
                standard = rf"\left({standard_z}\right){symbol}\left({standard_w}\right)"
            steps = (Step("standard", standard), *steps)
        return Task(
            statement=rf"Calculate \({expression}\).",
            steps=(Step("rewrite", expression), *steps, Step("result", fmt(value))),
            answer=ComplexAnswer(value),
            metadata={"difficulty": params.level, "template": params.operation},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )
