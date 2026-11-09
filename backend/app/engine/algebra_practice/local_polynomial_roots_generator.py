"""Local exercises for real roots and factorization of polynomials."""

import sympy as sp

from app.engine.answers.structured import FiniteSetAnswer
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task
from app.engine.prng import DeterministicRNG

X = sp.Symbol("x", real=True)
VARIATIONS = 10**12
POOL = (-3, -2, -1, 0, 1, 2, 3)
RULES = {
    "candidates": (
        {
            "title": "Rational root theorem",
            "latex": (
                r"P(x)=a_nx^n+\cdots+a_0,\quad \frac{p}{q}\in\mathbb{Q},"
                r"\quad P(p/q)=0\Rightarrow p\mid a_0,\;q\mid a_n"
            ),
            "explanation": (
                "For a reduced rational root, the numerator divides the constant "
                "coefficient and the denominator divides the leading coefficient."
            ),
        },
    ),
}


class RootParameters(Drawn):
    level: int
    roots: tuple[int, ...]
    extra: int


class LocalPolynomialRootsGenerator:
    version, prefix, family, code_version = (
        "local-polynomial-roots-v1",
        "LPR",
        "local-polynomial-roots",
        1,
    )
    params, answer, requires = RootParameters, FiniteSetAnswer, ()
    step_text = {
        "rewrite": "Write the original equation.",
        "candidates": (
            "The polynomial is monic, so rational root candidates are "
            "integer divisors of its constant term."
        ),
        "evaluate": "Evaluate the current polynomial at the candidate. A zero identifies a factor.",
        "factor": "Divide by the corresponding linear factor and continue with the quotient.",
        "factorization": "Combine the linear and remaining factors into a factorization.",
        "nonreal": "The remaining quadratic is positive for every real x, so has no real roots.",
        "multiplicity": "Repeated linear factors identify roots of multiplicity greater than one.",
        "result": "List each distinct real root once.",
    }

    def draw(self, seed: int) -> RootParameters:
        level = seed // VARIATIONS + 1
        if level not in (1, 2, 3):
            raise ValueError("Invalid roots seed")
        rng = DeterministicRNG(seed)
        first = rng.randbelow(len(POOL))
        second = rng.randbelow(len(POOL) - 1)
        second += second >= first
        roots = [POOL[first], POOL[second]]
        if level == 2:
            roots.append(
                roots[rng.randbelow(2)] if rng.randbelow(2) == 0 else POOL[rng.randbelow(len(POOL))]
            )
        return RootParameters(
            seed=seed,
            level=level,
            roots=tuple(roots),
            extra=1 + rng.randbelow(3) if level == 3 else 0,
        )

    def build(self, params: RootParameters) -> Task:
        residual = X**2 + params.extra if params.extra else sp.Integer(1)
        polynomial = sp.expand(residual * sp.prod(X - root for root in params.roots))
        roots = tuple(sorted(set(params.roots)))
        steps = [Step("rewrite", rf"{sp.latex(polynomial)}=0")]
        current = polynomial
        candidates_shown = False
        for root in sorted(params.roots, key=lambda value: value != 0):
            if root != 0 and not candidates_shown:
                constant = abs(int(current.subs(X, 0)))
                candidates = sorted(
                    {sign * int(d) for d in sp.divisors(constant) for sign in (-1, 1)}
                )
                steps.append(Step("candidates", r"\{" + ",".join(map(str, candidates)) + r"\}"))
                candidates_shown = True
            value = sp.expand(current).subs(X, root)
            if value != 0:
                raise ValueError("Root verification failed")
            quotient, remainder = sp.div(current, X - root, X)
            if remainder != 0:
                raise ValueError("Factor verification failed")
            steps.extend(
                (
                    Step(
                        "evaluate",
                        rf"\left.\left({sp.latex(current)}\right)\right|_{{x={root}}}={sp.latex(value)}",
                    ),
                    Step(
                        "factor",
                        rf"{sp.latex(current)}=({sp.latex(X - root)})({sp.latex(quotient)})",
                    ),
                )
            )
            current = sp.expand(quotient)
        steps.append(Step("factorization", rf"P(x)={sp.latex(sp.factor(polynomial))}"))
        if params.extra:
            steps.append(Step("nonreal", rf"x^2+{params.extra}>0\quad(x\in\mathbb{{R}})"))
        for root in roots:
            count = params.roots.count(root)
            if count > 1:
                steps.append(
                    Step(
                        "multiplicity",
                        rf"({sp.latex(X - root)})^{{{count}}}\quad\Rightarrow\quad x={root}",
                    )
                )
        steps.append(Step("result", r"\{" + ",".join(map(str, roots)) + r"\}"))
        return Task(
            statement=rf"Find all distinct real roots: \({sp.latex(polynomial)}=0\).",
            steps=tuple(steps),
            answer=FiniteSetAnswer(roots),
            metadata={"difficulty": params.level, "template": "real-roots"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )
