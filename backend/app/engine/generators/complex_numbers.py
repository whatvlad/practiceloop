"""Complex arithmetic, equations, polar form, De Moivre and roots: algebra30 41-51 (#221).

Answers are exact complex numbers in algebraic form a + bi (`ComplexAnswer`), or a
real principal argument. Every task is built from Gaussian integers or from a
modulus and an angle that is a multiple of pi/4 or pi/6, so values stay exact.
"""

from typing import Any, Literal, Self

import sympy as sp
from pydantic import Field, model_validator

from app.engine.answers.complex import ComplexAnswer
from app.engine.answers.expression import ExpressionAnswer
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task, TaskGenerator
from app.engine.prng import DeterministicRNG
from app.math_input import VariableDomain

IM = sp.I
NONZERO = (-4, -3, -2, -1, 1, 2, 3, 4)
# Arguments in [0, 2pi) whose sine and cosine are square-root expressions.
NICE = tuple(sorted({sp.pi * k / 4 for k in range(8)} | {sp.pi * k / 6 for k in range(12)}))


def _z(re: int, im: int) -> Any:
    return sp.Integer(re) + sp.Integer(im) * IM


def _latex(value: Any) -> str:
    return str(sp.latex(sp.expand(value)))


def _paren(value: Any) -> str:
    return f"({_latex(value)})"


class _Complex:
    code_version = 1
    requires: tuple[str, ...] = ()
    answer: type = ComplexAnswer
    difficulty: int
    template: str

    def input_variables(self, params: Any) -> dict[str, VariableDomain]:
        return {"i": "imaginary"}

    def _task(self, params: Drawn, statement: str, steps: tuple[Step, ...], value: Any) -> Task:
        answer: Any = (
            ExpressionAnswer(value, {}) if self.answer is ExpressionAnswer else ComplexAnswer(value)
        )
        return Task(
            statement=statement,
            steps=steps,
            answer=answer,
            metadata={"difficulty": self.difficulty, "template": self.template},
            code=encode(self.prefix, self.code_version, params.seed),  # type: ignore[attr-defined]
            generator_version=self.version,  # type: ignore[attr-defined]
        )


class PairParams(Drawn):
    first: tuple[int, int]
    second: tuple[int, int]

    @model_validator(mode="after")
    def bounded(self) -> Self:
        values = (*self.first, *self.second)
        if any(abs(v) > 5 for v in values) or self.first[1] == 0 or self.second[1] == 0:
            raise ValueError("Both numbers need bounded parts and a nonzero imaginary part")
        return self


def _draw_pair(rng: DeterministicRNG) -> tuple[tuple[int, int], tuple[int, int]]:
    def one() -> tuple[int, int]:
        return rng.randbelow(11) - 5, NONZERO[rng.randbelow(len(NONZERO))]

    return one(), one()


class ComplexProduct(_Complex):
    """Algebra30 41(b-d): multiply in algebraic form using i^2 = -1."""

    version = "complex-product-v1"
    prefix = "CXM"
    family = "complex-product"
    params = PairParams
    difficulty = 1
    template = "product"
    step_text = {
        "expand": "Multiply out the brackets.",
        "square": "Replace i squared by -1 and collect the real and imaginary parts.",
    }

    def draw(self, seed: int) -> PairParams:
        first, second = _draw_pair(DeterministicRNG(seed))
        return PairParams(seed=seed, first=first, second=second)

    def build(self, params: PairParams) -> Task:
        z, w = _z(*params.first), _z(*params.second)
        (a, b), (c, d) = params.first, params.second
        value = sp.expand(z * w)
        if value != _z(a * c - b * d, a * d + b * c):
            raise ValueError("Complex product failed verification")
        return self._task(
            params,
            rf"Calculate \({_paren(z)}{_paren(w)}\).",
            (
                Step("expand", rf"{a * c}+{_paren(a * d * IM)}+{_paren(b * c * IM)}+({b * d})i^2"),
                Step("square", _latex(value)),
            ),
            value,
        )


class ComplexQuotient(ComplexProduct):
    """Algebra30 41(g, h): divide by multiplying by the conjugate of the denominator."""

    version = "complex-quotient-v1"
    prefix = "CXQ"
    family = "complex-quotient"
    difficulty = 2
    template = "quotient"
    step_text = {
        "conjugate": "Multiply the top and the bottom by the conjugate of the denominator.",
        "simplify": "The denominator becomes a real number; divide each part by it.",
    }

    def build(self, params: PairParams) -> Task:
        quotient, denominator = _z(*params.first), _z(*params.second)
        numerator = sp.expand(quotient * denominator)
        conjugate = sp.conjugate(denominator)
        top, bottom = sp.expand(numerator * conjugate), sp.expand(denominator * conjugate)
        value = sp.expand(top / bottom)
        if value != quotient or not bottom.is_integer:
            raise ValueError("Complex quotient failed verification")
        return self._task(
            params,
            rf"Calculate \(\frac{{{_latex(numerator)}}}{{{_latex(denominator)}}}\).",
            (
                Step(
                    "conjugate",
                    rf"\frac{{{_paren(numerator)}{_paren(conjugate)}}}"
                    rf"{{{_paren(denominator)}{_paren(conjugate)}}}"
                    rf"=\frac{{{_latex(top)}}}{{{bottom}}}",
                ),
                Step("simplify", _latex(value)),
            ),
            value,
        )


class LinearParams(Drawn):
    solution: tuple[int, int]
    coefficient: tuple[int, int]
    conjugate: bool

    @model_validator(mode="after")
    def solvable(self) -> Self:
        if any(abs(v) > 5 for v in (*self.solution, *self.coefficient)):
            raise ValueError("Parts are outside the declared range")
        if self.conjugate and (self.coefficient[1] != 0 or abs(self.coefficient[0]) in (0, 1)):
            raise ValueError("The conjugate coefficient must be real and not 0 or +-1")
        if not self.conjugate and self.coefficient == (0, 0):
            raise ValueError("The coefficient must be nonzero")
        return self


class ComplexLinearEquation(_Complex):
    """Algebra30 42(a, d): solve az = w, or z + q*conj(z) = w by comparing parts."""

    version = "complex-linear-equation-v1"
    prefix = "CXE"
    family = "complex-linear-equation"
    params = LinearParams
    difficulty = 3
    template = "linear-equation"
    step_text = {
        "divide": "Divide both sides by the coefficient of z.",
        "parts": "Write z = x + yi and compare the real and imaginary parts.",
        "solve": "Solve for the real and imaginary parts.",
    }

    def draw(self, seed: int) -> LinearParams:
        rng = DeterministicRNG(seed)
        solution = (rng.randbelow(9) - 4, rng.randbelow(9) - 4)
        conjugate = rng.randbelow(2) == 1
        if conjugate:
            coefficient = ((-3, -2, 2, 3)[rng.randbelow(4)], 0)
        else:
            coefficient = (rng.randbelow(7) - 3, NONZERO[rng.randbelow(len(NONZERO))])
        return LinearParams(
            seed=seed, solution=solution, coefficient=coefficient, conjugate=conjugate
        )

    def build(self, params: LinearParams) -> Task:
        z = _z(*params.solution)
        x, y = params.solution
        if params.conjugate:
            q = params.coefficient[0]
            right = sp.expand(z + q * sp.conjugate(z))
            equation = rf"z{'+' if q > 0 else '-'}{abs(q)}\overline{{z}}={_latex(right)}"
            steps = (
                Step("parts", rf"{1 + q}x+{_paren((1 - q) * sp.Symbol('y') * IM)}={_latex(right)}"),
                Step("solve", rf"x={x},\quad y={y}"),
            )
            check = sp.expand(z + q * sp.conjugate(z)) == right
        else:
            a = _z(*params.coefficient)
            right = sp.expand(a * z)
            equation = rf"{_paren(a)}z={_latex(right)}"
            steps = (
                Step("divide", rf"z=\frac{{{_latex(right)}}}{{{_latex(a)}}}"),
                Step("solve", _latex(z)),
            )
            check = sp.expand(right / a) == z
        if not check:
            raise ValueError("Complex equation failed verification")
        return self._task(params, rf"Solve for z: \({equation}\).", steps, z)


class SquareRootParams(Drawn):
    root: tuple[int, int]

    @model_validator(mode="after")
    def principal(self) -> Self:
        if not 1 <= self.root[0] <= 5 or not 1 <= abs(self.root[1]) <= 5:
            raise ValueError("The root needs a positive real part and a nonzero imaginary part")
        return self


class ComplexSquareRoot(_Complex):
    """Algebra30 42(c): z^2 = w by comparing the parts of (x + yi)^2."""

    version = "complex-square-root-v1"
    prefix = "CXS"
    family = "complex-square-root"
    params = SquareRootParams
    difficulty = 4
    template = "square-root"
    step_text = {
        "parts": "Write z = x + yi and compare the parts of z squared.",
        "modulus": "The modulus of z squared equals the modulus of the right-hand side.",
        "solve": "Solve for x and y and keep the root with a positive real part.",
    }

    def draw(self, seed: int) -> SquareRootParams:
        rng = DeterministicRNG(seed)
        return SquareRootParams(
            seed=seed, root=(1 + rng.randbelow(5), NONZERO[rng.randbelow(len(NONZERO))])
        )

    def build(self, params: SquareRootParams) -> Task:
        z = _z(*params.root)
        w = sp.expand(z**2)
        re, im = sp.re(w), sp.im(w)
        modulus = sp.sqrt(re**2 + im**2)
        # The two square roots of w are z and -z; z is the one with a positive real part.
        if sp.expand(z**2 - w) != 0 or sp.re(z) <= 0 or modulus != sp.Abs(z) ** 2:
            raise ValueError("Complex square root failed verification")
        return self._task(
            params,
            "Find the solution with a positive real part: "
            rf"\(z^{{2}}={_latex(w)}\).",
            (
                Step("parts", rf"x^{{2}}-y^{{2}}={re},\quad 2xy={im}"),
                Step("modulus", rf"x^{{2}}+y^{{2}}={modulus}"),
                Step("solve", rf"z={_latex(z)}"),
            ),
            z,
        )


class QuadraticParams(Drawn):
    roots: tuple[tuple[int, int], tuple[int, int]]

    @model_validator(mode="after")
    def distinct(self) -> Self:
        (a, b), (c, d) = self.roots
        if any(abs(v) > 4 for v in (a, b, c, d)) or a <= c:
            raise ValueError("The first root must have the larger real part")
        if b == 0 and d == 0:
            raise ValueError("At least one root must be non-real")
        return self


class ComplexQuadratic(_Complex):
    """Algebra30 51(a, b): a quadratic with complex coefficients via its discriminant."""

    version = "complex-quadratic-v1"
    prefix = "CXR"
    family = "complex-quadratic"
    params = QuadraticParams
    difficulty = 5
    template = "quadratic"
    step_text = {
        "discriminant": "Calculate the discriminant.",
        "root": "Find a square root of the discriminant.",
        "roots": "Use the quadratic formula and choose the root with the larger real part.",
    }

    def draw(self, seed: int) -> QuadraticParams:
        rng = DeterministicRNG(seed)
        first = (rng.randbelow(9) - 4, rng.randbelow(9) - 4)
        second_re = rng.randbelow(8) - 4
        second_re += second_re >= first[0]
        second = (second_re, NONZERO[rng.randbelow(len(NONZERO))])
        larger, smaller = (first, second) if first[0] > second[0] else (second, first)
        return QuadraticParams(seed=seed, roots=(larger, smaller))

    def build(self, params: QuadraticParams) -> Task:
        z1, z2 = (_z(*root) for root in params.roots)
        p, q = sp.expand(-(z1 + z2)), sp.expand(z1 * z2)
        u = sp.Symbol("u")
        polynomial = sp.expand(u**2 + p * u + q)
        discriminant = sp.expand(p**2 - 4 * q)
        root = sp.expand(z1 - z2)
        if sp.expand(polynomial.subs(u, z1)) != 0 or sp.expand(polynomial.subs(u, z2)) != 0:
            raise ValueError("Quadratic roots failed verification")
        if sp.expand(root**2) != discriminant:
            raise ValueError("Discriminant root failed verification")
        equation = f"z^{{2}}+{_paren(p)}z+{_paren(q)}"
        return self._task(
            params,
            f"Find the solution with the larger real part: \\({equation}=0\\).",
            (
                Step("discriminant", rf"\Delta={_latex(discriminant)}"),
                Step("root", rf"\sqrt{{\Delta}}=\pm{_paren(root)}"),
                Step("roots", rf"z_1={_latex(z1)},\quad z_2={_latex(z2)}"),
            ),
            z1,
        )


class PolarParams(Drawn):
    angle: int = Field(ge=0, le=15)
    scale: int = Field(ge=1, le=4)


def _angle(index: int) -> Any:
    return NICE[index]


def _rectangular(modulus: Any, angle: Any) -> Any:
    return sp.expand(modulus * (sp.cos(angle) + IM * sp.sin(angle)))


def _cis(angle: Any) -> str:
    a = sp.latex(angle)
    return rf"\cos\left({a}\right)+i\sin\left({a}\right)"


def _principal(angle: Any) -> Any:
    reduced = sp.Mod(angle, 2 * sp.pi)
    return reduced - 2 * sp.pi if reduced > sp.pi else reduced


AXES = frozenset(i for i, a in enumerate(NICE) if (a / (sp.pi / 2)).is_integer)


class ComplexArgument(_Complex):
    """Algebra30 45: the principal argument from the algebraic form."""

    version = "complex-argument-v1"
    prefix = "CXG"
    family = "complex-argument"
    params = PolarParams
    answer = ExpressionAnswer
    difficulty = 1
    template = "argument"
    step_text = {
        "modulus": "Calculate the modulus.",
        "trig": "Divide the real and imaginary parts by the modulus to get the cosine and sine.",
        "angle": "Choose the angle in (-pi, pi] with this cosine and sine.",
    }

    def draw(self, seed: int) -> PolarParams:
        rng = DeterministicRNG(seed)
        off_axis = [i for i in range(len(NICE)) if i not in AXES]
        return PolarParams(
            seed=seed, angle=off_axis[rng.randbelow(len(off_axis))], scale=1 + rng.randbelow(4)
        )

    def build(self, params: PolarParams) -> Task:
        sixth = (_angle(params.angle) / (sp.pi / 6)).is_integer
        modulus = sp.Integer(params.scale) * (2 if sixth else sp.sqrt(2))
        z = _rectangular(modulus, _angle(params.angle))
        argument = _principal(_angle(params.angle))
        if sp.simplify(sp.arg(z) - argument) != 0 or not -sp.pi < argument <= sp.pi:
            raise ValueError("Argument failed verification")
        return self._task(
            params,
            rf"Find the principal argument, between −π and π: \(z={_latex(z)}\).",
            (
                Step("modulus", rf"|z|={sp.latex(modulus)}"),
                Step(
                    "trig",
                    rf"\cos\varphi={sp.latex(sp.re(z) / modulus)},\quad"
                    rf"\sin\varphi={sp.latex(sp.simplify(sp.im(z) / modulus))}",
                ),
                Step("angle", rf"\varphi={sp.latex(argument)}"),
            ),
            argument,
        )


BASES = ((1, 1), (1, -1), (-1, 1), (-1, -1))


class DeMoivreParams(Drawn):
    base: int = Field(ge=0, le=11)
    power: int = Field(ge=5, le=20)


def _base(index: int) -> Any:
    """1 +- i, -1 +- i (modulus sqrt 2), sqrt 3 +- i and 1 +- sqrt 3 i signs (modulus 2)."""
    sx, sy = BASES[index % 4]
    if index < 4:
        return _z(sx, sy)
    if index < 8:
        return sx * sp.sqrt(3) + sy * IM
    return sx + sy * sp.sqrt(3) * IM


class DeMoivre(_Complex):
    """Algebra30 46: a power through the trigonometric form, answered as a + bi."""

    version = "complex-de-moivre-v1"
    prefix = "CXD"
    family = "complex-de-moivre"
    params = DeMoivreParams
    difficulty = 2
    template = "de-moivre"
    step_text = {
        "polar": "Write the base in trigonometric form.",
        "power": "By De Moivre's formula, raise the modulus to the power and multiply the angle.",
        "result": "Evaluate the cosine and sine.",
    }

    def draw(self, seed: int) -> DeMoivreParams:
        rng = DeterministicRNG(seed)
        return DeMoivreParams(seed=seed, base=rng.randbelow(12), power=5 + rng.randbelow(16))

    def build(self, params: DeMoivreParams) -> Task:
        base = _base(params.base)
        modulus, angle = sp.Abs(base), sp.arg(base)
        n = params.power
        value = _rectangular(modulus**n, n * angle)
        if sp.expand(base**n - value) != 0:
            raise ValueError("De Moivre power failed verification")
        reduced = _principal(n * angle)
        return self._task(
            params,
            rf"Calculate in the form a + bi: \(({_latex(base)})^{{{n}}}\).",
            (
                Step("polar", rf"{_latex(base)}={sp.latex(modulus)}\left({_cis(angle)}\right)"),
                Step("power", rf"{sp.latex(modulus**n)}\left({_cis(reduced)}\right)"),
                Step("result", _latex(value)),
            ),
            value,
        )


ROOT_ORDERS: tuple[Literal[2, 3, 4, 6], ...] = (2, 3, 4, 6)


class RootParams(Drawn):
    order: Literal[2, 3, 4, 6]
    angle: int = Field(ge=0, le=15)
    scale: int = Field(ge=1, le=2)

    @model_validator(mode="after")
    def principal(self) -> Self:
        if not _angle(self.angle) < 2 * sp.pi / self.order:
            raise ValueError("The first root's argument must be below 2pi/n")
        return self


class ComplexRoot(_Complex):
    """Algebra30 49: the n-th root with the smallest nonnegative argument."""

    version = "complex-root-v1"
    prefix = "CXN"
    family = "complex-root"
    params = RootParams
    difficulty = 3
    template = "nth-root"
    step_text = {
        "polar": "Write the number in trigonometric form.",
        "formula": "The roots have modulus the n-th root of the modulus and arguments "
        "(phi + 2k pi)/n; k = 0 gives the smallest nonnegative argument.",
        "result": "Evaluate the cosine and sine.",
    }

    def draw(self, seed: int) -> RootParams:
        rng = DeterministicRNG(seed)
        order = ROOT_ORDERS[rng.randbelow(4)]
        allowed = [i for i in range(len(NICE)) if NICE[i] < 2 * sp.pi / order]
        return RootParams(
            seed=seed,
            order=order,
            angle=allowed[rng.randbelow(len(allowed))],
            scale=1 + rng.randbelow(2),
        )

    def build(self, params: RootParams) -> Task:
        n, theta = params.order, _angle(params.angle)
        root = _rectangular(sp.Integer(params.scale), theta)
        phi = n * theta
        w = _rectangular(sp.Integer(params.scale) ** n, phi)
        if sp.expand(root**n - w) != 0:
            raise ValueError("Complex root failed verification")
        others = [
            _rectangular(sp.Integer(params.scale), theta + 2 * sp.pi * k / n) for k in range(1, n)
        ]
        if any(sp.expand(r**n - w) != 0 for r in others):
            raise ValueError("Complex roots failed verification")
        return self._task(
            params,
            "Find the solution with the smallest nonnegative argument: "
            rf"\(z^{{{n}}}={_latex(w)}\).",
            (
                Step("polar", rf"{_latex(w)}={params.scale**n}\left({_cis(phi)}\right)"),
                Step("formula", rf"z_0={params.scale}\left({_cis(theta)}\right)"),
                Step("result", rf"z_0={_latex(root)}"),
            ),
            root,
        )


def generators() -> tuple[TaskGenerator[Any], ...]:
    return (
        ComplexProduct(),
        ComplexQuotient(),
        ComplexLinearEquation(),
        ComplexSquareRoot(),
        ComplexQuadratic(),
        ComplexArgument(),
        DeMoivre(),
        ComplexRoot(),
    )
