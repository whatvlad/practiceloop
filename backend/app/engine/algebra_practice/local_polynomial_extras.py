"""Local polynomial operations, complex-root counts and partial fractions."""

from typing import Any, cast

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.blocks.polynomial import Polynomial
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task
from app.engine.prng import DeterministicRNG
from app.math_input.contracts import InputContract

X = sp.Symbol("x", real=True)
VARIATIONS = 10**12
KINDS = ("add", "subtract", "multiply", "fundamental", "fractions")


class ExtrasParams(Drawn):
    level: int
    kind: str
    first: tuple[int, ...]
    second: tuple[int, ...]
    roots: tuple[int, int]
    coefficients: tuple[int, int, int]


class PolynomialExtras:
    version, prefix, family, code_version = (
        "local-polynomial-extra-v1",
        "LPE",
        "local-polynomial-extra",
        1,
    )
    params, requires = ExtrasParams, ()
    answer: Any = FormulaAnswer
    step_text = {
        "rewrite": "Write the original problem.",
        "group": "Apply the selected operation and collect terms with the same power of x.",
        "degree": "Identify the degree of the nonconstant polynomial.",
        "theorem": "A degree n polynomial has n complex roots counted with multiplicity.",
        "domain": "The original denominator must be nonzero.",
        "form": "Choose the partial-fraction form according to the denominator factors.",
        "clear": "Multiply both sides by the denominator to obtain a polynomial identity.",
        "first": "Substitute the first root of the denominator to isolate its coefficient.",
        "second": "Use the indicated substitution or compare leading coefficients.",
        "third": "Substitute x = 0 into the identity and solve for the remaining coefficient.",
        "result": "Write the result.",
    }

    def draw(self, seed: int) -> ExtrasParams:
        index = seed // VARIATIONS
        if not 0 <= index < 15:
            raise ValueError("Invalid polynomial exercise seed")
        level, kind = index // len(KINDS) + 1, KINDS[index % len(KINDS)]
        rng = DeterministicRNG(seed)
        first = Polynomial.draw(rng, level + 1).coefficients
        second = Polynomial.draw(rng, level).coefficients
        roots_pool = (-3, -2, -1, 1, 2, 3)
        i = rng.randbelow(6)
        j = rng.randbelow(5)
        j += j >= i
        return ExtrasParams(
            seed=seed,
            level=level,
            kind=kind,
            first=first,
            second=second,
            roots=(roots_pool[i], roots_pool[j]),
            coefficients=(rng.randbelow(7) - 3, rng.randbelow(7) - 3, rng.randbelow(7) - 3),
        )

    def input_contract(self, params: ExtrasParams) -> InputContract:
        return cast(InputContract, cast(Any, self.build(params).answer).contract)

    def build(self, params: ExtrasParams) -> Task:
        f = sp.Add(*(c * X**i for i, c in enumerate(params.first)))
        g = sp.Add(*(c * X**i for i, c in enumerate(params.second)))
        latex = sp.latex
        answer: OrderedAnswer | FormulaAnswer
        steps = []
        if params.kind in {"add", "subtract", "multiply"}:
            sign = {"add": "+", "subtract": "-", "multiply": r"\cdot"}[params.kind]
            result = sp.expand({"add": f + g, "subtract": f - g, "multiply": f * g}[params.kind])
            expression = rf"\left({latex(f)}\right){sign}\left({latex(g)}\right)"
            statement = rf"Calculate the polynomial: \({expression}\)."
            steps = [
                Step("rewrite", expression),
                Step("group", rf"{expression}={latex(result)}"),
                Step("result", latex(result)),
            ]
            answer = FormulaAnswer(result, (("x", "real"),))
        elif params.kind == "fundamental":
            a, b = params.roots
            polynomial = sp.expand((X - a) ** params.level * (X - b) * (X**2 + 1))
            degree = int(sp.degree(polynomial, X))
            expression = rf"{latex(polynomial)}=0"
            statement = rf"Count all complex roots including multiplicity: \({expression}\)."
            steps = [
                Step("rewrite", expression),
                Step("degree", rf"\deg P={degree}"),
                Step("theorem", rf"n={degree}"),
                Step("result", rf"{degree}"),
            ]
            answer = FormulaAnswer(degree)
        else:
            a, b = params.roots
            A, B, C = params.coefficients
            repeated = params.level > 1
            d1, d2 = X - a, X - b
            denominator = sp.expand(d1 ** (2 if repeated else 1) * d2)
            numerator = (
                sp.expand(A * d1 * d2 + B * d2 + C * d1**2)
                if repeated
                else sp.expand(A * d2 + B * d1)
            )
            divisor_latex = rf"({latex(d1)}){'^2' if repeated else ''}({latex(d2)})"
            expression = rf"\frac{{{latex(numerator)}}}{{{divisor_latex}}}"
            statement = rf"Find the partial-fraction coefficients: \({expression}\)."
            if params.level == 3:
                c = abs(b)
                quadratic = X**2 + c
                numerator = sp.expand(A * quadratic + (B * X + C) * d1)
                expression = rf"\frac{{{latex(numerator)}}}{{({latex(d1)})({latex(quadratic)})}}"
                form = rf"\frac{{A}}{{{latex(d1)}}}+\frac{{Bx+C}}{{{latex(quadratic)}}}"
                identity = rf"{latex(numerator)}=A({latex(quadratic)})+(Bx+C)({latex(d1)})"
                leading = sp.Poly(numerator, X).coeff_monomial(X**2)
                steps = [
                    Step("rewrite", expression),
                    Step("domain", rf"x\ne {a}"),
                    Step("form", form),
                    Step("clear", identity),
                    Step("first", rf"A=\frac{{{latex(numerator.subs(X, a))}}}{{{a * a + c}}}={A}"),
                    Step("second", rf"A+B={latex(leading)}\quad\Rightarrow\quad B={B}"),
                    Step(
                        "third", rf"C=\frac{{{latex(numerator.subs(X, 0))}-({A})({c})}}{{{-a}}}={C}"
                    ),
                    Step("result", rf"A={A},\quad B={B},\quad C={C}"),
                ]
                answer = OrderedAnswer(tuple(FormulaAnswer(v) for v in (A, B, C)), ("A", "B", "C"))
            elif repeated:
                form = (
                    rf"\frac{{A}}{{{latex(d1)}}}+\frac{{B}}{{({latex(d1)})^2}}"
                    rf"+\frac{{C}}{{{latex(d2)}}}"
                )
                identity = (
                    rf"{latex(numerator)}=A({latex(d1)})({latex(d2)})"
                    rf"+B({latex(d2)})+C({latex(d1)})^2"
                )
                steps = [
                    Step("rewrite", expression),
                    Step("domain", rf"x\ne {a},\quad x\ne {b}"),
                    Step("form", form),
                    Step("clear", identity),
                    Step("first", rf"B=\frac{{{latex(numerator.subs(X, a))}}}{{{a - b}}}={B}"),
                    Step("second", rf"C=\frac{{{latex(numerator.subs(X, b))}}}{{({b - a})^2}}={C}"),
                    Step(
                        "third",
                        rf"A=\frac{{{latex(numerator.subs(X, 0))}-({B})({-b})"
                        rf"-({C})({-a})^2}}{{({-a})({-b})}}={A}",
                    ),
                    Step("result", rf"A={A},\quad B={B},\quad C={C}"),
                ]
                answer = OrderedAnswer(tuple(FormulaAnswer(v) for v in (A, B, C)), ("A", "B", "C"))
            else:
                form = rf"\frac{{A}}{{{latex(d1)}}}+\frac{{B}}{{{latex(d2)}}}"
                identity = rf"{latex(numerator)}=A({latex(d2)})+B({latex(d1)})"
                steps = [
                    Step("rewrite", expression),
                    Step("domain", rf"x\ne {a},\quad x\ne {b}"),
                    Step("form", form),
                    Step("clear", identity),
                    Step("first", rf"A=\frac{{{latex(numerator.subs(X, a))}}}{{{a - b}}}={A}"),
                    Step("second", rf"B=\frac{{{latex(numerator.subs(X, b))}}}{{{b - a}}}={B}"),
                    Step("result", rf"A={A},\quad B={B}"),
                ]
                answer = OrderedAnswer(tuple(FormulaAnswer(v) for v in (A, B)), ("A", "B"))
            statement = rf"Find the partial-fraction coefficients: \({expression}={form}\)."
            steps[0] = Step("rewrite", rf"{expression}={form}")
            if sp.expand(denominator) == 0:
                raise ValueError("Invalid denominator")
        return Task(
            statement=statement,
            steps=tuple(steps),
            answer=answer,
            metadata={"difficulty": params.level, "template": params.kind},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class PartialFractionsExtras(PolynomialExtras):
    version, prefix, family = "local-partial-fractions-v1", "LPF", "local-partial-fractions"
    answer = OrderedAnswer
