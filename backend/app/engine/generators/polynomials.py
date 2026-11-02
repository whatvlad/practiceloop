"""Binomial theorem, polynomial roots, remainders and partial fractions (#221).

Algebra30 exercises 5, 7, 55, 57, 58, 60 and 61-63. Every answer is one exact
integer, rational number or polynomial in x, built from bounded integers and
re-proved with SymPy in the build.
"""

from math import comb
from typing import Any, Literal, Self

import sympy as sp
from pydantic import Field, model_validator

from app.engine.answers.expression import ExpressionAnswer
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task, TaskGenerator
from app.engine.prng import DeterministicRNG, draw_valid
from app.math_input import VariableDomain

X = sp.Symbol("x", real=True)
NONZERO = (-3, -2, -1, 1, 2, 3)


def _poly(expression: Any) -> str:
    return str(sp.latex(sp.Poly(sp.expand(expression), X).as_expr()))


def _signed(value: Any) -> str:
    return "" if value == 0 else f"{'+' if value > 0 else '-'}{abs(value)}"


class _Generator:
    code_version = 1
    requires: tuple[str, ...] = ()
    answer = ExpressionAnswer
    difficulty: int
    template: str
    polynomial_answer = False

    def input_variables(self, params: Any) -> dict[str, VariableDomain] | None:
        return {"x": "real"} if self.polynomial_answer else None

    def _task(self, params: Drawn, statement: str, steps: tuple[Step, ...], value: Any) -> Task:
        return Task(
            statement=statement,
            steps=steps,
            answer=ExpressionAnswer(
                sp.sympify(value), {"x": "real"} if self.polynomial_answer else {}
            ),
            metadata={"difficulty": self.difficulty, "template": self.template},
            code=encode(self.prefix, self.code_version, params.seed),  # type: ignore[attr-defined]
            generator_version=self.version,  # type: ignore[attr-defined]
        )


class CoefficientParams(Drawn):
    a: int = Field(ge=-3, le=3)
    b: int = Field(ge=-4, le=4)
    n: int = Field(ge=3, le=8)
    k: int = Field(ge=0, le=8)

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.a == 0 or self.b == 0 or not 1 <= self.k < self.n:
            raise ValueError("Need nonzero terms and an inner power")
        return self


class BinomialCoefficient(_Generator):
    """Algebra30 5(a, b): one coefficient of (ax + b)^n."""

    version = "binomial-coefficient-v1"
    prefix = "BNC"
    family = "binomial-coefficient"
    params = CoefficientParams
    difficulty = 1
    template = "coefficient"
    step_text = {
        "term": "The general term is C(n, k) times the powers of both summands.",
        "evaluate": "Multiply the binomial coefficient by the powers of the numbers.",
    }

    def draw(self, seed: int) -> CoefficientParams:
        rng = DeterministicRNG(seed)
        n = 3 + rng.randbelow(6)
        return CoefficientParams(
            seed=seed,
            a=NONZERO[rng.randbelow(6)],
            b=(-4, -3, -2, -1, 1, 2, 3, 4)[rng.randbelow(8)],
            n=n,
            k=1 + rng.randbelow(n - 1),
        )

    def build(self, params: CoefficientParams) -> Task:
        a, b, n, k = params.a, params.b, params.n, params.k
        value = comb(n, k) * a**k * b ** (n - k)
        if sp.Poly(sp.expand((a * X + b) ** n), X).coeff_monomial(X**k) != value:
            raise ValueError("Binomial coefficient failed verification")
        return self._task(
            params,
            f"Find the coefficient of x to the power {k} in the expansion: "
            rf"\(({_poly(a * X + b)})^{{{n}}}\).",
            (
                Step("term", rf"\binom{{{n}}}{{{k}}}({a}x)^{{{k}}}({b})^{{{n - k}}}"),
                Step("evaluate", rf"{comb(n, k)}\cdot({a})^{{{k}}}\cdot({b})^{{{n - k}}}={value}"),
            ),
            value,
        )


class ConstantTermParams(Drawn):
    a: int = Field(ge=-3, le=3)
    b: int = Field(ge=-3, le=3)
    p: int = Field(ge=1, le=3)
    q: int = Field(ge=1, le=3)
    n: int = Field(ge=2, le=9)

    @model_validator(mode="after")
    def has_constant(self) -> Self:
        if self.a == 0 or self.b == 0 or (self.p * self.n) % (self.p + self.q) != 0:
            raise ValueError("The expansion must have a constant term")
        return self


class BinomialConstantTerm(_Generator):
    """Algebra30 5(c): the term free of x in (a x^p + b / x^q)^n."""

    version = "binomial-constant-term-v1"
    prefix = "BNT"
    family = "binomial-constant-term"
    params = ConstantTermParams
    difficulty = 2
    template = "constant-term"
    step_text = {
        "power": "In the k-th term the power of x is p(n - k) - qk; set it to zero.",
        "evaluate": "Evaluate that term.",
    }

    def draw(self, seed: int) -> ConstantTermParams:
        rng = DeterministicRNG(seed)

        def candidate() -> tuple[int, int, int]:
            return 1 + rng.randbelow(3), 1 + rng.randbelow(3), 2 + rng.randbelow(8)

        p, q, n = draw_valid(candidate, lambda c: (c[0] * c[2]) % (c[0] + c[1]) == 0)
        return ConstantTermParams(
            seed=seed, a=NONZERO[rng.randbelow(6)], b=NONZERO[rng.randbelow(6)], p=p, q=q, n=n
        )

    def build(self, params: ConstantTermParams) -> Task:
        a, b, p, q, n = params.a, params.b, params.p, params.q, params.n
        k = p * n // (p + q)
        # Term k takes (b/x^q)^k: x^(p(n-k) - qk) = x^0.
        value = comb(n, k) * a ** (n - k) * b**k
        expansion = sp.expand((a * X**p + b / X**q) ** n)
        if expansion.as_coefficients_dict()[sp.Integer(1)] != value:
            raise ValueError("Constant term failed verification")
        first = (
            f"{'-' if a < 0 else ''}{abs(a) if abs(a) != 1 else ''}x{'' if p == 1 else f'^{{{p}}}'}"
        )
        second = rf"{'-' if b < 0 else '+'}\frac{{{abs(b)}}}{{x{'' if q == 1 else f'^{{{q}}}'}}}"
        return self._task(
            params,
            rf"Find the term independent of x in the expansion: \(({first}{second})^{{{n}}}\).",
            (
                Step("power", rf"{p}({n}-k)-{q}k=0\ \Rightarrow\ k={k}"),
                Step(
                    "evaluate",
                    rf"\binom{{{n}}}{{{k}}}({a})^{{{n - k}}}({b})^{{{k}}}={value}",
                ),
            ),
            value,
        )


class ExponentParams(Drawn):
    a: int = Field(ge=-4, le=4)
    n: int = Field(ge=3, le=12)

    @model_validator(mode="after")
    def nonzero(self) -> Self:
        if abs(self.a) < 2:
            raise ValueError("The coefficient must have size at least 2")
        return self


class BinomialExponent(_Generator):
    """Algebra30 7: find n from the coefficient of x^2 in (1 + ax)^n."""

    version = "binomial-exponent-v1"
    prefix = "BNE"
    family = "binomial-exponent"
    params = ExponentParams
    difficulty = 3
    template = "exponent"
    step_text = {
        "coefficient": "The coefficient of x squared is C(n, 2) times a squared.",
        "solve": "Solve the quadratic equation and keep the natural number.",
    }

    def draw(self, seed: int) -> ExponentParams:
        rng = DeterministicRNG(seed)
        return ExponentParams(
            seed=seed, a=(-4, -3, -2, 2, 3, 4)[rng.randbelow(6)], n=3 + rng.randbelow(10)
        )

    def build(self, params: ExponentParams) -> Task:
        a, n = params.a, params.n
        target = comb(n, 2) * a * a
        m = sp.Symbol("n")
        roots = [r for r in sp.solve(m * (m - 1) * a * a / 2 - target, m) if r.is_integer and r > 0]
        if roots != [n]:
            raise ValueError("Binomial exponent failed verification")
        return self._task(
            params,
            f"The coefficient of x squared in the expansion is {target}. Find n: "
            rf"\(({_poly(1 + a * X)})^{{n}}\).",
            (
                Step("coefficient", rf"\binom{{n}}{{2}}\cdot {a * a}={target}"),
                Step("solve", rf"n(n-1)={2 * target // (a * a)}\ \Rightarrow\ n={n}"),
            ),
            n,
        )


class RationalRootParams(Drawn):
    roots: tuple[tuple[int, int], tuple[int, int]]
    quadratic: tuple[int, int]

    @model_validator(mode="after")
    def valid(self) -> Self:
        for p, q in self.roots:
            if not 1 <= q <= 3 or not 1 <= abs(p) <= 6 or sp.gcd(p, q) != 1:
                raise ValueError("Roots are reduced fractions p/q with q from 1 to 3")
        if self.roots[0][0] * self.roots[1][1] == self.roots[1][0] * self.roots[0][1]:
            raise ValueError("Rational roots must differ")
        b, c = self.quadratic
        if abs(b) > 4 or not 1 <= c <= 9 or b * b - 4 * c >= 0:
            raise ValueError("The quadratic factor must have no real roots")
        return self


class RationalRoots(_Generator):
    """Algebra30 55: the largest rational root, via the rational root theorem."""

    version = "polynomial-rational-root-v1"
    prefix = "PRR"
    family = "polynomial-rational-root"
    params = RationalRootParams
    difficulty = 1
    template = "rational-root"
    step_text = {
        "candidates": "Candidates are p/q: p divides the constant term, q the leading coefficient.",
        "test": "Test the candidates; each root found splits off a linear factor.",
        "rest": "The remaining quadratic factor has a negative discriminant.",
    }

    def draw(self, seed: int) -> RationalRootParams:
        rng = DeterministicRNG(seed)

        def root() -> tuple[int, int]:
            q = 1 + rng.randbelow(3)
            return draw_valid(
                lambda: rng.randbelow(13) - 6, lambda p: p != 0 and sp.gcd(p, q) == 1
            ), q

        first = root()
        second = draw_valid(root, lambda r: r[0] * first[1] != first[0] * r[1])
        b = rng.randbelow(9) - 4
        c = draw_valid(lambda: 1 + rng.randbelow(9), lambda c: b * b < 4 * c)
        return RationalRootParams(seed=seed, roots=(first, second), quadratic=(b, c))

    def build(self, params: RationalRootParams) -> Task:
        (p1, q1), (p2, q2) = params.roots
        b, c = params.quadratic
        polynomial = sp.expand((q1 * X - p1) * (q2 * X - p2) * (X**2 + b * X + c))
        rational = sorted({sp.Rational(p1, q1), sp.Rational(p2, q2)})
        found = sorted(r for r in sp.Poly(polynomial, X).ground_roots() if r.is_rational)
        if found != rational:
            raise ValueError("Rational roots failed verification")
        return self._task(
            params,
            f"Find the largest rational root: \\({_poly(polynomial)}\\).",
            (
                Step(
                    "candidates",
                    rf"\pm\frac{{p}}{{q}},\ p\mid {abs(p1 * p2 * c)},\ q\mid {q1 * q2}",
                ),
                Step("test", rf"x_1={sp.latex(rational[0])},\quad x_2={sp.latex(rational[1])}"),
                Step("rest", rf"{_poly(X**2 + b * X + c)},\quad \Delta={b * b - 4 * c}<0"),
            ),
            rational[1],
        )


class KnownRootParams(Drawn):
    real: int = Field(ge=-5, le=5)
    complex_root: tuple[int, int]

    @model_validator(mode="after")
    def non_real(self) -> Self:
        if self.complex_root[1] == 0 or any(abs(v) > 4 for v in self.complex_root):
            raise ValueError("The given root must be non-real and bounded")
        return self


class KnownComplexRoot(_Generator):
    """Algebra30 57: a real cubic with a given complex root; find the real root."""

    version = "polynomial-known-root-v1"
    prefix = "PKR"
    family = "polynomial-known-root"
    params = KnownRootParams
    difficulty = 2
    template = "known-root"
    step_text = {
        "conjugate": "A real polynomial also has the conjugate root.",
        "factor": "Their linear factors multiply to a real quadratic.",
        "divide": "Divide the polynomial by the quadratic to find the last factor.",
    }

    def draw(self, seed: int) -> KnownRootParams:
        rng = DeterministicRNG(seed)
        return KnownRootParams(
            seed=seed,
            real=rng.randbelow(11) - 5,
            complex_root=(
                rng.randbelow(9) - 4,
                (1, 2, 3, 4)[rng.randbelow(4)] * (1 - 2 * rng.randbelow(2)),
            ),
        )

    def build(self, params: KnownRootParams) -> Task:
        a, b = params.complex_root
        z = a + b * sp.I
        quadratic = sp.expand((X - z) * (X - sp.conjugate(z)))
        polynomial = sp.expand((X - params.real) * quadratic)
        quotient, remainder = sp.div(polynomial, quadratic, X)
        if remainder != 0 or sp.expand(polynomial.subs(X, z)) != 0 or quotient != X - params.real:
            raise ValueError("Known root failed verification")
        return self._task(
            params,
            f"Given that {sp.latex(z).replace(' ', '')} is a root, find the real root: "
            rf"\({_poly(polynomial)}\).",
            (
                Step("conjugate", rf"\overline{{x_1}}={sp.latex(sp.conjugate(z))}"),
                Step(
                    "factor",
                    rf"(x-({sp.latex(z)}))(x-({sp.latex(sp.conjugate(z))}))={_poly(quadratic)}",
                ),
                Step("divide", rf"{_poly(polynomial)}=({_poly(quadratic)})({_poly(quotient)})"),
            ),
            params.real,
        )


class FactorParams(Drawn):
    root: int = Field(ge=-4, le=4)
    quadratic: tuple[int, int]
    leading: int = Field(ge=1, le=2)

    @model_validator(mode="after")
    def irreducible(self) -> Self:
        b, c = self.quadratic
        if abs(b) > 4 or not 1 <= c <= 9 or b * b - 4 * c >= 0:
            raise ValueError("The quadratic factor must have no real roots")
        return self


class IrreducibleFactor(_Generator):
    """Algebra30 58(b, c): the irreducible quadratic factor of a real cubic."""

    version = "polynomial-irreducible-factor-v1"
    prefix = "PIF"
    family = "polynomial-irreducible-factor"
    params = FactorParams
    difficulty = 3
    template = "irreducible-factor"
    polynomial_answer = True
    step_text = {
        "root": "Find an integer root among the divisors of the constant term.",
        "divide": "Divide by the corresponding linear factor.",
        "irreducible": "The quotient has a negative discriminant, so it does not factor further.",
    }

    def draw(self, seed: int) -> FactorParams:
        rng = DeterministicRNG(seed)
        b = rng.randbelow(9) - 4
        c = draw_valid(lambda: 1 + rng.randbelow(9), lambda c: b * b < 4 * c)
        return FactorParams(
            seed=seed, root=rng.randbelow(9) - 4, quadratic=(b, c), leading=1 + rng.randbelow(2)
        )

    def build(self, params: FactorParams) -> Task:
        b, c = params.quadratic
        quadratic = params.leading * (X**2 + b * X + c)
        polynomial = sp.expand((X - params.root) * quadratic)
        monic = X**2 + b * X + c
        factors = [sp.expand(f) for f, _ in sp.factor_list(polynomial, X)[1]]
        if b * b - 4 * c >= 0 or sp.expand(monic) not in factors:
            raise ValueError("Irreducible factor failed verification")
        return self._task(
            params,
            "Factor into irreducible real factors and give the monic quadratic factor: "
            rf"\({_poly(polynomial)}\).",
            (
                Step("root", rf"W({params.root})=0"),
                Step("divide", rf"{_poly(polynomial)}=(x-({params.root}))({_poly(quadratic)})"),
                Step("irreducible", rf"\Delta={b * b - 4 * c}<0\ \Rightarrow\ {_poly(monic)}"),
            ),
            monic,
        )


class RemainderConditionParams(Drawn):
    a: int = Field(ge=-5, le=5)
    b: int = Field(ge=-5, le=5)
    leading: int = Field(ge=1, le=3)
    constant: int = Field(ge=-3, le=3)
    points: tuple[int, int, int]

    @model_validator(mode="after")
    def distinct(self) -> Self:
        if len(set(self.points)) != 3 or any(abs(p) > 3 for p in self.points):
            raise ValueError("The three points must be distinct and bounded")
        if 0 in self.points[:2]:
            raise ValueError("The given remainders must determine a and b")
        return self


class RemainderConditions(_Generator):
    """Algebra30 61: two remainders determine a and b; give the third remainder."""

    version = "polynomial-remainder-conditions-v1"
    prefix = "PRC"
    family = "polynomial-remainder-conditions"
    params = RemainderConditionParams
    difficulty = 3
    template = "remainder-conditions"
    step_text = {
        "theorem": "By the remainder theorem, the remainder on division by x - c is W(c).",
        "solve": "Solve the two linear equations for a and b.",
        "evaluate": "Evaluate the polynomial at the third point.",
    }

    def draw(self, seed: int) -> RemainderConditionParams:
        rng = DeterministicRNG(seed)
        first = NONZERO[rng.randbelow(6)]
        second = draw_valid(lambda: NONZERO[rng.randbelow(6)], lambda p: p != first)
        third = draw_valid(lambda: rng.randbelow(7) - 3, lambda p: p not in (first, second))
        return RemainderConditionParams(
            seed=seed,
            a=rng.randbelow(11) - 5,
            b=rng.randbelow(11) - 5,
            leading=1 + rng.randbelow(3),
            constant=rng.randbelow(7) - 3,
            points=(first, second, third),
        )

    def build(self, params: RemainderConditionParams) -> Task:
        a, b = sp.symbols("a b")
        general = params.leading * X**3 + a * X**2 + b * X + params.constant
        actual = general.subs({a: params.a, b: params.b})
        c1, c2, c3 = params.points
        r1, r2 = actual.subs(X, c1), actual.subs(X, c2)
        solved = sp.solve([general.subs(X, c1) - r1, general.subs(X, c2) - r2], [a, b], dict=True)
        if solved != [{a: params.a, b: params.b}]:
            raise ValueError("Remainder conditions failed verification")
        value = actual.subs(X, c3)
        return self._task(
            params,
            f"Dividing by {sp.latex(X - c1)} leaves remainder {r1} and by "
            f"{sp.latex(X - c2)} leaves remainder {r2}. Find the remainder on division by "
            f"{sp.latex(X - c3)}: "
            f"\\(W(x)={params.leading}x^{{3}}+ax^{{2}}+bx{_signed(params.constant)}\\).",
            (
                Step("theorem", rf"W({c1})={r1},\quad W({c2})={r2}"),
                Step("solve", rf"a={params.a},\quad b={params.b}"),
                Step("evaluate", rf"W({c3})={value}"),
            ),
            value,
        )


class DivisibilityParams(Drawn):
    roots: tuple[int, int]
    a: int = Field(ge=-4, le=4)
    b: int = Field(ge=-6, le=6)
    target: Literal["a", "b"]

    @model_validator(mode="after")
    def valid(self) -> Self:
        r1, r2 = self.roots
        if r1 == r2 or not 1 <= abs(r1) <= 3 or not 1 <= abs(r2) <= 3 or self.a == 0:
            raise ValueError("Need two distinct bounded roots and nonzero a, c")
        return self


class Divisibility(_Generator):
    """Algebra30 62: a x^3 + b x^2 + c x + d is divisible by (x - r1)(x - r2)."""

    version = "polynomial-divisibility-v1"
    prefix = "PDB"
    family = "polynomial-divisibility"
    params = DivisibilityParams
    difficulty = 4
    template = "divisibility"
    step_text = {
        "roots": "The polynomial is divisible exactly when both zeros of the divisor are roots.",
        "solve": "Solve the two linear equations.",
    }

    def draw(self, seed: int) -> DivisibilityParams:
        rng = DeterministicRNG(seed)
        r1 = NONZERO[rng.randbelow(6)]
        r2 = draw_valid(lambda: NONZERO[rng.randbelow(6)], lambda r: r != r1)
        return DivisibilityParams(
            seed=seed,
            roots=(r1, r2),
            a=(-4, -3, -2, -1, 1, 2, 3, 4)[rng.randbelow(8)],
            b=rng.randbelow(13) - 6,
            target="a" if rng.randbelow(2) == 0 else "b",
        )

    def build(self, params: DivisibilityParams) -> Task:
        r1, r2 = params.roots
        third = params.a * X + params.b  # W = (x - r1)(x - r2)(a x + b) + 0
        actual = sp.expand((X - r1) * (X - r2) * third)
        coefficients = sp.Poly(actual, X).all_coeffs()
        c, d = coefficients[2], coefficients[3]
        a, b = sp.symbols("a b")
        general = a * X**3 + b * X**2 + c * X + d
        divisor = sp.expand((X - r1) * (X - r2))
        solved = sp.solve([general.subs(X, r1), general.subs(X, r2)], [a, b], dict=True)
        expected = {a: coefficients[0], b: coefficients[1]}
        if solved != [expected] or sp.rem(actual, divisor, X) != 0:
            raise ValueError("Divisibility failed verification")
        target = a if params.target == "a" else b
        return self._task(
            params,
            f"Find {params.target} for which W is divisible by P: "
            f"\\(W(x)=ax^{{3}}+bx^{{2}}{_signed(c)}x{_signed(d)},\\quad P(x)={_poly(divisor)}\\).",
            (
                Step("roots", rf"W({r1})=0,\quad W({r2})=0"),
                Step("solve", rf"a={expected[a]},\quad b={expected[b]}"),
            ),
            expected[target],
        )


class PowerRemainderParams(Drawn):
    exponents: tuple[int, int, int]
    coefficients: tuple[int, int, int]

    @model_validator(mode="after")
    def valid(self) -> Self:
        if any(not 2 <= e <= 99 for e in self.exponents) or len(set(self.exponents)) != 3:
            raise ValueError("Exponents must be distinct and from 2 to 99")
        if any(c == 0 or abs(c) > 3 for c in self.coefficients):
            raise ValueError("Coefficients must be nonzero and bounded")
        return self


class CubicRemainder(_Generator):
    """Algebra30 63(c): remainder of a sum of powers modulo x^3 - x."""

    version = "polynomial-cubic-remainder-v1"
    prefix = "PCR"
    family = "polynomial-cubic-remainder"
    params = PowerRemainderParams
    difficulty = 5
    template = "cubic-remainder"
    polynomial_answer = True
    step_text = {
        "roots": "x^3 - x has the roots -1, 0 and 1, so the remainder R has degree at most 2.",
        "values": "Evaluate the polynomial at the three roots.",
        "interpolate": "Find the quadratic R through these values.",
    }

    def draw(self, seed: int) -> PowerRemainderParams:
        rng = DeterministicRNG(seed)
        first = 2 + rng.randbelow(98)
        second = draw_valid(lambda: 2 + rng.randbelow(98), lambda e: e != first)
        third = draw_valid(lambda: 2 + rng.randbelow(98), lambda e: e not in (first, second))
        return PowerRemainderParams(
            seed=seed,
            exponents=(first, second, third),
            coefficients=tuple(NONZERO[rng.randbelow(6)] for _ in range(3)),  # type: ignore[arg-type]
        )

    def build(self, params: PowerRemainderParams) -> Task:
        polynomial = sum(
            c * X**e for c, e in zip(params.coefficients, params.exponents, strict=True)
        )
        divisor = X**3 - X
        values = {r: polynomial.subs(X, r) for r in (-1, 0, 1)}
        # Through (-1, v), (0, w), (1, u): R = w + (u - v)/2 x + ((u + v)/2 - w) x^2.
        v, w, u = values[-1], values[0], values[1]
        remainder = sp.expand(w + sp.Rational(u - v, 2) * X + (sp.Rational(u + v, 2) - w) * X**2)
        if sp.rem(polynomial, divisor, X) != remainder:
            raise ValueError("Cubic remainder failed verification")
        return self._task(
            params,
            "Without dividing, find the remainder on division by x cubed minus x: "
            f"\\({_poly(polynomial)}\\).",
            (
                Step("roots", r"x^3-x=(x+1)x(x-1)"),
                Step("values", rf"W(-1)={v},\quad W(0)={w},\quad W(1)={u}"),
                Step("interpolate", rf"R(x)={sp.latex(remainder)}"),
            ),
            remainder,
        )


class PartialCoefficientParams(Drawn):
    pole: int = Field(ge=-4, le=4)
    other: int = Field(ge=-4, le=4)
    numerators: tuple[int, int, int]
    quadratic: bool
    target: int = Field(ge=0, le=2)

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.pole == self.other or any(abs(n) > 5 for n in self.numerators):
            raise ValueError("Poles must differ and numerators be bounded")
        if self.numerators[0] == 0 or self.numerators[1] == 0:
            raise ValueError("The leading partial fractions must be present")
        return self


class PartialFractionCoefficient(_Generator):
    """Algebra30 60(c, d, h): one constant when a factor is repeated or quadratic."""

    version = "partial-fraction-coefficient-v1"
    prefix = "PFC"
    family = "partial-fraction-coefficient"
    params = PartialCoefficientParams
    difficulty = 4
    template = "partial-fraction-coefficient"
    step_text = {
        "form": "Write the decomposition with unknown constants.",
        "solve": "Multiply by the denominator and compare coefficients.",
    }

    def draw(self, seed: int) -> PartialCoefficientParams:
        rng = DeterministicRNG(seed)
        pole = rng.randbelow(9) - 4
        other = draw_valid(lambda: rng.randbelow(9) - 4, lambda o: o != pole)
        return PartialCoefficientParams(
            seed=seed,
            pole=pole,
            other=other,
            numerators=(
                (-5, -4, -3, -2, -1, 1, 2, 3, 4, 5)[rng.randbelow(10)],
                (-5, -4, -3, -2, -1, 1, 2, 3, 4, 5)[rng.randbelow(10)],
                rng.randbelow(11) - 5,
            ),
            quadratic=rng.randbelow(2) == 1,
            target=rng.randbelow(3),
        )

    def build(self, params: PartialCoefficientParams) -> Task:
        A, B, C = params.numerators
        p, o = params.pole, params.other
        if params.quadratic:
            # A/(x - p) + (Bx + C)/(x^2 + o^2 + 1)
            quadratic = X**2 + o * o + 1
            pieces = A / (X - p) + (B * X + C) / quadratic
            denominator = sp.expand((X - p) * quadratic)
            form = rf"\frac{{A}}{{{sp.latex(X - p)}}}+\frac{{Bx+C}}{{{_poly(quadratic)}}}"
        else:
            pieces = A / (X - p) + B / (X - p) ** 2 + C / (X - o)
            denominator = sp.expand((X - p) ** 2 * (X - o))
            form = (
                rf"\frac{{A}}{{{sp.latex(X - p)}}}+\frac{{B}}{{({sp.latex(X - p)})^{{2}}}}"
                rf"+\frac{{C}}{{{sp.latex(X - o)}}}"
            )
        numerator = sp.expand(sp.cancel(pieces * denominator))
        if sp.simplify(sp.apart(numerator / denominator, X) - pieces) != 0:
            raise ValueError("Partial fraction coefficient failed verification")
        name = "ABC"[params.target]
        return self._task(
            params,
            f"Find the constant {name} in the decomposition: "
            rf"\(\frac{{{_poly(numerator)}}}{{{_poly(denominator)}}}={form}\).",
            (
                Step("form", form),
                Step("solve", rf"A={A},\quad B={B},\quad C={C}"),
            ),
            params.numerators[params.target],
        )


def generators() -> tuple[TaskGenerator[Any], ...]:
    return (
        BinomialCoefficient(),
        BinomialConstantTerm(),
        BinomialExponent(),
        RationalRoots(),
        KnownComplexRoot(),
        IrreducibleFactor(),
        RemainderConditions(),
        Divisibility(),
        CubicRemainder(),
        PartialFractionCoefficient(),
    )
