"""Local polynomial division, remainder and divisibility exercises."""

from typing import Any, cast

import sympy as sp

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.blocks.polynomial import Polynomial
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task
from app.engine.prng import DeterministicRNG
from app.math_input.contracts import InputContract

X = sp.Symbol("x", real=True)
K = sp.Symbol("k", real=True)
VARIATIONS = 10**12
MODES = ("division", "remainder", "divisibility")


RULES = {
    "identity": (
        {
            "title": "Polynomial division theorem",
            "latex": r"P(x)=D(x)Q(x)+R(x),\quad R=0\;\text{or}\;\deg R<\deg D",
            "explanation": (
                "For a nonzero divisor, the quotient and remainder are unique; "
                "the remainder has lower degree than the divisor."
            ),
        },
    ),
}


class PolynomialParameters(Drawn):
    level: int
    mode: str
    root: int
    quotient: tuple[int, ...]
    remainder: tuple[int, ...]
    divisor: tuple[int, ...]


class LocalPolynomialGenerator:
    version, prefix, family, code_version = (
        "local-polynomial-division-v1",
        "LPD",
        "local-polynomial-division",
        1,
    )
    params, requires = PolynomialParameters, ()
    answer: Any = OrderedAnswer
    step_text = {
        "rewrite": "Write the original problem.",
        "lead": "Divide the leading term by the leading term of the divisor.",
        "multiply": "Multiply the divisor by the new quotient term.",
        "subtract": "Subtract the product and combine like terms. Repeat while possible.",
        "finish": "The remainder has lower degree than the divisor.",
        "identity": "Check the result using dividend equals divisor times quotient plus remainder.",
        "theorem": "For division by x − a, the remainder equals the value of P(a).",
        "substitute": "Substitute the zero of the divisor into the polynomial.",
        "condition": "A polynomial is divisible by x − a exactly when P(a) is zero.",
        "solve": "Solve the resulting equation for the unknown coefficient.",
        "result": "Write the result.",
    }

    def draw(self, seed: int) -> PolynomialParameters:
        index = seed // VARIATIONS
        if not 0 <= index < 9:
            raise ValueError("Invalid polynomial seed")
        level, mode = index // 3 + 1, MODES[index % 3]
        rng = DeterministicRNG(seed)
        root = rng.randbelow(7) - 3
        degree = (1, 2, 3)[level - 1]
        quotient = Polynomial.draw(rng, degree).coefficients
        divisor = (
            (-root, 1)
            if level == 1 or mode != "division"
            else (rng.randbelow(7) - 3, rng.randbelow(7) - 3, 1)
        )
        remainder = (
            (0,)
            if rng.randbelow(2) == 0
            else tuple(rng.randbelow(7) - 3 for _ in range(len(divisor) - 1))
        )
        return PolynomialParameters(
            seed=seed,
            level=level,
            mode=mode,
            root=root,
            quotient=quotient,
            remainder=remainder,
            divisor=divisor,
        )

    def input_contract(self, params: PolynomialParameters) -> InputContract:
        return cast(InputContract, cast(Any, self.build(params).answer).contract)

    def build(self, params: PolynomialParameters) -> Task:
        q = sp.Add(*(v * X**i for i, v in enumerate(params.quotient)))
        divisor = sp.Add(*(v * X**i for i, v in enumerate(params.divisor)))
        rem = sp.Add(*(v * X**i for i, v in enumerate(params.remainder)))
        polynomial = sp.expand(divisor * q + rem)
        latex = sp.latex
        answer: OrderedAnswer | FormulaAnswer
        if params.mode == "division":
            expression = rf"\left({latex(polynomial)}\right)\div\left({latex(divisor)}\right)"
            steps = [Step("rewrite", expression)]
            current = polynomial
            while current != 0 and sp.degree(current, X) >= sp.degree(divisor, X):
                leading = sp.LT(current, X)
                divisor_lead = sp.LT(divisor, X)
                term = sp.cancel(leading / divisor_lead)
                product = sp.expand(term * divisor)
                following = sp.expand(current - product)
                steps.extend(
                    (
                        Step(
                            "lead",
                            rf"\frac{{{latex(leading)}}}{{{latex(divisor_lead)}}}={latex(term)}",
                        ),
                        Step("multiply", rf"({latex(term)})({latex(divisor)})={latex(product)}"),
                        Step(
                            "subtract",
                            rf"\left({latex(current)}\right)-\left({latex(product)}\right)={latex(following)}",
                        ),
                    )
                )
                current = following
            if sp.expand(current - rem) != 0:
                raise ValueError("Long division verification failed")
            steps.extend(
                (
                    Step("finish", rf"Q(x)={latex(q)},\quad R(x)={latex(rem)}"),
                    Step(
                        "identity",
                        rf"{latex(polynomial)}=({latex(divisor)})({latex(q)})+({latex(rem)})",
                    ),
                )
            )
            answer = OrderedAnswer(
                (FormulaAnswer(q, (("x", "real"),)), FormulaAnswer(rem, (("x", "real"),))),
                ("Quotient", "Remainder"),
            )
            statement = rf"Find the quotient and remainder: \({expression}\)."
        else:
            a = params.root
            if params.mode == "remainder":
                expression = rf"P(x)={latex(polynomial)},\quad D(x)={latex(divisor)}"
                substitution = polynomial.subs(X, a)
                coefficients = sp.Poly(polynomial, X).all_coeffs()
                degree = len(coefficients) - 1
                expanded = "+".join(
                    rf"({latex(coefficient)})({a})^{{{degree - i}}}"
                    for i, coefficient in enumerate(coefficients)
                    if coefficient != 0
                )
                steps = [
                    Step("rewrite", expression),
                    Step("theorem", r"R=P(a),\quad D(x)=x-a"),
                    Step("substitute", rf"P({a})={expanded}={latex(substitution)}"),
                    Step("result", rf"R={latex(substitution)}"),
                ]
                answer = FormulaAnswer(substitution)
                statement = rf"Find the remainder: \({expression}\)."
            else:
                base = sp.expand(polynomial - polynomial.subs(X, 0))
                target = -base.subs(X, a)
                expression = rf"P(x)={latex(base + K)},\quad D(x)={latex(divisor)}"
                steps = [
                    Step("rewrite", expression),
                    Step("condition", rf"P({a})=0"),
                    Step("substitute", rf"{latex(base.subs(X, a))}+k=0"),
                    Step("solve", rf"k={latex(target)}"),
                    Step("result", rf"k={latex(target)}"),
                ]
                answer = FormulaAnswer(target)
                statement = rf"Find k so the divisor divides the polynomial: \({expression}\)."
        return Task(
            statement=statement,
            steps=tuple(steps),
            answer=answer,
            metadata={"difficulty": params.level, "template": params.mode},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class LocalPolynomialScalarGenerator(LocalPolynomialGenerator):
    version, prefix, family = "local-polynomial-scalar-v1", "LPS", "local-polynomial-scalar"
    answer = FormulaAnswer
