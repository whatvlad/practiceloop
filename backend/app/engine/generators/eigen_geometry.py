"""Eigenvalues, vectors, lines and planes from algebra30 exercises 64-96 (#221).

Every answer is one exact scalar: an eigenvalue, a matrix entry, a scalar triple
product, a cosine, an area, a volume, a distance or a coordinate. Points and
vectors are bounded integers, so results are rationals or square roots.
"""

from dataclasses import replace
from itertools import permutations
from typing import Any, Self

import sympy as sp
from pydantic import Field, model_validator

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.answers.expression import ExpressionAnswer
from app.engine.answers.structured import FiniteSetAnswer
from app.engine.blocks.matrices import IntMatrix, bounded, draw_entries, draw_invertible, pmatrix
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task, TaskGenerator
from app.engine.prng import DeterministicRNG, draw_valid
from app.math_input.contracts import InputContract

ORDINALS = ("first", "second", "third")
type Vector = tuple[int, int, int]


def _vec(v: Any) -> str:
    return "(" + ",".join(str(sp.latex(sp.sympify(c))) for c in v) + ")"


def _ratio(top: Any, bottom: Any) -> str:
    """An unsimplified fraction, as written before rationalizing."""
    return rf"\frac{{{sp.latex(top)}}}{{{sp.latex(bottom)}}}"


def _m(v: Vector) -> sp.Matrix:
    return sp.Matrix(v)


class _Generator:
    code_version = 1
    requires: tuple[str, ...] = ()
    answer = ExpressionAnswer
    difficulty: int
    template: str

    def _task(self, params: Drawn, statement: str, steps: tuple[Step, ...], value: Any) -> Task:
        value = sp.radsimp(sp.sympify(value))
        return Task(
            statement=statement,
            steps=steps,
            answer=ExpressionAnswer(value, {}),
            metadata={"difficulty": self.difficulty, "template": self.template},
            code=encode(self.prefix, self.code_version, params.seed),  # type: ignore[attr-defined]
            generator_version=self.version,  # type: ignore[attr-defined]
        )


# Eigenvalues ----------------------------------------------------------------


class EigenParams(Drawn):
    basis: IntMatrix
    eigenvalues: tuple[int, ...]
    power: int = Field(ge=1, le=6)
    row: int = Field(ge=0, le=2)
    column: int = Field(ge=0, le=2)

    @model_validator(mode="after")
    def valid(self) -> Self:
        size = len(self.basis)
        if (
            size not in (2, 3)
            or len(self.eigenvalues) != size
            or any(len(r) != size for r in self.basis)
        ):
            raise ValueError("Eigen data is 2 x 2 or 3 x 3")
        if abs(sp.Matrix(self.basis).det()) != 1 or not bounded(self.basis, 6):
            raise ValueError("The eigenvector matrix must be unimodular and bounded")
        if any(abs(v) > 4 for v in self.eigenvalues) or max(self.row, self.column) >= size:
            raise ValueError("Eigenvalues and the entry must be in range")
        return self

    def matrix(self) -> sp.Matrix:
        p = sp.Matrix(self.basis)
        return p * sp.diag(*self.eigenvalues) * p.inv()


def _draw_eigen(
    rng: DeterministicRNG, size: int, distinct: bool
) -> tuple[IntMatrix, tuple[int, ...]]:
    def candidate() -> tuple[IntMatrix, tuple[int, ...]]:
        basis = draw_invertible(rng, size, (1, -1))
        values = tuple(rng.randbelow(9) - 4 for _ in range(size))
        return basis, values

    def valid(drawn: tuple[IntMatrix, tuple[int, ...]]) -> bool:
        basis, values = drawn
        a = sp.Matrix(basis) * sp.diag(*values) * sp.Matrix(basis).inv()
        return (
            bounded(basis, 6)
            and all(abs(v) <= 12 for v in a)
            and (not distinct or len(set(values)) == size)
        )

    return draw_valid(candidate, valid)


class LargestEigenvalue(_Generator):
    """Algebra30 65, 69: the eigenvalues from the characteristic polynomial."""

    version = "eigen-largest-v1"
    prefix = "EGL"
    family = "eigen-largest"
    params = EigenParams
    difficulty = 1
    template = "largest-eigenvalue"
    step_text = {
        "characteristic": "Solve the characteristic equation det(A - lambda I) = 0.",
        "roots": "Its roots are the eigenvalues; choose the largest.",
    }

    def draw(self, seed: int) -> EigenParams:
        rng = DeterministicRNG(seed)
        basis, values = _draw_eigen(rng, 2, True)
        return EigenParams(seed=seed, basis=basis, eigenvalues=values, power=1, row=0, column=0)

    def build(self, params: EigenParams) -> Task:
        a = params.matrix()
        lam = sp.Symbol("lambda")
        characteristic = sp.expand((a - lam * sp.eye(len(params.basis))).det())
        roots = sorted(sp.roots(characteristic, lam))
        if roots != sorted(set(params.eigenvalues)):
            raise ValueError("Eigenvalues failed verification")
        return self._task(
            params,
            f"Find the largest eigenvalue of the matrix: \\(A={pmatrix(a.tolist())}\\).",
            (
                Step("characteristic", rf"{sp.latex(characteristic)}=0"),
                Step("roots", r",\ ".join(f"\\lambda={r}" for r in roots)),
            ),
            roots[-1],
        )


class EigenvectorValue(_Generator):
    """Algebra30 64: check Av = lambda v for a given vector and read off lambda."""

    version = "eigen-vector-value-v1"
    prefix = "EGV"
    family = "eigen-vector-value"
    params = EigenParams
    difficulty = 2
    template = "eigenvector-value"
    step_text = {
        "multiply": "Multiply the matrix by the vector.",
        "compare": "The product is a multiple of the vector; the factor is the eigenvalue.",
    }

    def draw(self, seed: int) -> EigenParams:
        rng = DeterministicRNG(seed)
        basis, values = _draw_eigen(rng, 3, False)
        return EigenParams(
            seed=seed, basis=basis, eigenvalues=values, power=1, row=0, column=rng.randbelow(3)
        )

    def build(self, params: EigenParams) -> Task:
        a = params.matrix()
        vector = sp.Matrix(params.basis).col(params.column)
        value = params.eigenvalues[params.column]
        product = a * vector
        if product != value * vector:
            raise ValueError("Eigenvector failed verification")
        return self._task(
            params,
            "The vector v is an eigenvector of A. Find its eigenvalue: "
            rf"\(A={pmatrix(a.tolist())},\quad v={_vec(vector)}\).",
            (
                Step("multiply", rf"Av={_vec(product)}"),
                Step("compare", rf"Av={value}v"),
            ),
            value,
        )


class DiagonalPower(_Generator):
    """Algebra30 69(b): A^n = P D^n P^-1 for a diagonalizable 2 x 2 matrix."""

    version = "eigen-power-v1"
    prefix = "EGP"
    family = "eigen-power"
    params = EigenParams
    difficulty = 3
    template = "matrix-power"
    step_text = {
        "diagonalize": "Diagonalize: A = P D P^-1 with the eigenvectors as the columns of P.",
        "power": "Then A^n = P D^n P^-1.",
        "entry": "Read off the requested entry.",
    }

    def draw(self, seed: int) -> EigenParams:
        rng = DeterministicRNG(seed)
        basis, values = _draw_eigen(rng, 2, True)
        values = tuple(v if abs(v) <= 3 else v // 2 for v in values)
        if values[0] == values[1]:
            values = (values[0], values[1] + 1 if values[1] < 3 else values[1] - 1)
        return EigenParams(
            seed=seed,
            basis=basis,
            eigenvalues=values,
            power=3 + rng.randbelow(4),
            row=rng.randbelow(2),
            column=rng.randbelow(2),
        )

    def build(self, params: EigenParams) -> Task:
        a, p = params.matrix(), sp.Matrix(params.basis)
        n = params.power
        power = p * sp.diag(*params.eigenvalues) ** n * p.inv()
        if power != a**n:
            raise ValueError("Matrix power failed verification")
        value = power[params.row, params.column]
        d = sp.diag(*params.eigenvalues)
        return self._task(
            params,
            f"Using diagonalization, find the entry in the {ORDINALS[params.row]} row and "
            f"{ORDINALS[params.column]} column of A to the power {n}: "
            rf"\(A={pmatrix(a.tolist())}\).",
            (
                Step("diagonalize", rf"P={pmatrix(p.tolist())},\quad D={pmatrix(d.tolist())}"),
                Step("power", rf"A^{{{n}}}={pmatrix(power.tolist())}"),
                Step("entry", rf"(A^{{{n}}})_{{{params.row + 1}{params.column + 1}}}={value}"),
            ),
            value,
        )


class TriangularParams(Drawn):
    matrix: IntMatrix
    power: int = Field(ge=2, le=8)

    @model_validator(mode="after")
    def triangular(self) -> Self:
        if (
            len(self.matrix) != 4
            or any(len(r) != 4 for r in self.matrix)
            or not bounded(self.matrix, 5)
        ):
            raise ValueError("A bounded 4 x 4 matrix is required")
        if any(self.matrix[i][j] for i in range(4) for j in range(i)):
            raise ValueError("The matrix must be upper triangular")
        return self


class TriangularPowerEigenvalue(_Generator):
    """Algebra30 66: eigenvalues of a power of a triangular matrix."""

    version = "eigen-triangular-power-v1"
    prefix = "EGT"
    family = "eigen-triangular-power"
    params = TriangularParams
    difficulty = 4
    template = "triangular-power"
    step_text = {
        "diagonal": "A triangular matrix has its eigenvalues on the diagonal.",
        "power": "A power of an upper triangular matrix is upper triangular with powered diagonal.",
        "largest": "Choose the largest.",
    }

    def draw(self, seed: int) -> TriangularParams:
        rng = DeterministicRNG(seed)
        entries = [list(r) for r in draw_entries(rng, 4, 4, 3)]
        for i in range(4):
            for j in range(i):
                entries[i][j] = 0
        return TriangularParams(
            seed=seed, matrix=tuple(tuple(r) for r in entries), power=2 + rng.randbelow(7)
        )

    def build(self, params: TriangularParams) -> Task:
        a, n = sp.Matrix(params.matrix), params.power
        diagonal = [a[i, i] ** n for i in range(4)]
        value = max(diagonal)
        if sorted(diagonal) != sorted(sp.Matrix([(a**n)[i, i] for i in range(4)])):
            raise ValueError("Triangular power failed verification")
        return self._task(
            params,
            f"Find the largest eigenvalue of A to the power {n}: \\(A={pmatrix(params.matrix)}\\).",
            (
                Step("diagonal", r",\ ".join(str(a[i, i]) for i in range(4))),
                Step("power", r",\ ".join(f"({a[i, i]})^{{{n}}}={a[i, i] ** n}" for i in range(4))),
                Step("largest", rf"\lambda_{{\max}}={value}"),
            ),
            value,
        )


class MatrixFromEigenvectors(DiagonalPower):
    """Algebra30 67: the matrix with given eigenpairs, A = P D P^-1."""

    version = "eigen-from-pairs-v1"
    prefix = "EGM"
    family = "eigen-from-pairs"
    difficulty = 5
    template = "matrix-from-eigenpairs"
    step_text = {
        "columns": "Put the eigenvectors as the columns of P and the eigenvalues on D.",
        "product": "Calculate A = P D P^-1.",
        "entry": "Read off the requested entry.",
    }

    def build(self, params: EigenParams) -> Task:
        p, d = sp.Matrix(params.basis), sp.diag(*params.eigenvalues)
        a = p * d * p.inv()
        for k in range(2):
            if a * p.col(k) != params.eigenvalues[k] * p.col(k):
                raise ValueError("Eigenpairs failed verification")
        (l1, l2), v1, v2 = params.eigenvalues, p.col(0), p.col(1)
        value = a[params.row, params.column]
        return self._task(
            params,
            f"A 2 x 2 matrix A has the eigenvalue {l1} with eigenvector v1 and the eigenvalue "
            f"{l2} with eigenvector v2. Find the entry in the {ORDINALS[params.row]} row and "
            f"{ORDINALS[params.column]} column of A: "
            rf"\(v_1={_vec(v1)},\quad v_2={_vec(v2)}\).",
            (
                Step("columns", rf"P={pmatrix(p.tolist())},\quad D={pmatrix(d.tolist())}"),
                Step("product", rf"A={pmatrix(a.tolist())}"),
                Step("entry", rf"a_{{{params.row + 1}{params.column + 1}}}={value}"),
            ),
            value,
        )


# Vectors --------------------------------------------------------------------


def vector_expression_seed(level: int, variation: int) -> int:
    if level not in (1, 2, 3) or not 0 <= variation < 10**12:
        raise ValueError("Invalid vector-expression settings")
    return (level - 1) * 10**12 + variation


class VectorExpressionParameters(Drawn):
    level: int = Field(ge=1, le=3)
    u: Vector
    v: Vector
    w: Vector

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.seed // 10**12 != self.level - 1:
            raise ValueError("Vector-expression seed and level differ")
        if any(abs(component) > 2 for vector in (self.u, self.v, self.w) for component in vector):
            raise ValueError("Vector coordinates exceed the practice range")
        if any(vector == (0, 0, 0) for vector in (self.u, self.v, self.w)):
            raise ValueError("The given vectors must be nonzero")
        u, v, w = (_m(vector) for vector in (self.u, self.v, self.w))
        if u == v or u.cross(w) == sp.zeros(3, 1) or (2 * u - v).cross(w) == sp.zeros(3, 1):
            raise ValueError("Vector construction is degenerate")
        return self


class VectorExpression:
    """Ordered vector operations, including algebra30 72(c) and 72(g)."""

    version, prefix, family, code_version = "vector-expression-v1", "VEC", "vector-expression", 1
    params, answer, requires = VectorExpressionParameters, OrderedAnswer, ()
    step_text = {
        "subtract": "Subtract the vectors coordinate by coordinate.",
        "cross": "Calculate the cross product in the indicated order.",
        "combine": "First calculate the linear combination inside the brackets.",
        "finish": "Subtract v from the cross product, coordinate by coordinate.",
        "norm": "Find the length of u from its coordinates.",
        "scale": "Multiply every coordinate of v by the length of u.",
        "finish_scaled": "Subtract w from the scaled vector, coordinate by coordinate.",
    }

    def input_contract(self, params: VectorExpressionParameters) -> InputContract:
        return InputContract(
            "tuple",
            components=(InputContract("formula"),) * 3,
            labels=("x component", "y component", "z component"),
        )

    def draw(self, seed: int) -> VectorExpressionParameters:
        level = seed // 10**12 + 1
        if level not in (1, 2, 3):
            raise ValueError("Invalid vector-expression seed")
        rng = DeterministicRNG(seed)

        def candidate() -> tuple[Vector, Vector, Vector]:
            return tuple(tuple(rng.randbelow(5) - 2 for _ in range(3)) for _ in range(3))  # type: ignore[return-value]

        def valid(vectors: tuple[Vector, Vector, Vector]) -> bool:
            u, v, w = (_m(vector) for vector in vectors)
            return (
                all(vector != (0, 0, 0) for vector in vectors)
                and u != v
                and u.cross(w) != sp.zeros(3, 1)
                and (2 * u - v).cross(w) != sp.zeros(3, 1)
            )

        u, v, w = draw_valid(candidate, valid)
        return VectorExpressionParameters(seed=seed, level=level, u=u, v=v, w=w)

    def build(self, params: VectorExpressionParameters) -> Task:
        u, v, w = (_m(vector) for vector in (params.u, params.v, params.w))
        steps: tuple[Step, ...]
        if params.level == 1:
            result = u - v
            expression = "u-v"
            givens = rf"u={_vec(u)},\ v={_vec(v)}"
            steps = (Step("subtract", rf"u-v={_vec(result)}"),)
        elif params.level == 2 and params.seed % 2:
            length = u.norm()
            scaled = length * v
            result = scaled - w
            expression = r"|u|v-w"
            givens = rf"u={_vec(u)},\ v={_vec(v)},\ w={_vec(w)}"
            steps = (
                Step("norm", rf"|u|={sp.latex(length)}"),
                Step("scale", rf"|u|v={_vec(scaled)}"),
                Step("finish_scaled", rf"|u|v-w={_vec(result)}"),
            )
        elif params.level == 2:
            cross = u.cross(w)
            result = cross - v
            expression = r"u\times w-v"
            givens = rf"u={_vec(u)},\ v={_vec(v)},\ w={_vec(w)}"
            steps = (
                Step("cross", rf"u\times w={_vec(cross)}"),
                Step("finish", rf"u\times w-v={_vec(result)}"),
            )
        else:
            combined = 2 * u - v
            result = combined.cross(w)
            expression = r"(2u-v)\times w"
            givens = rf"u={_vec(u)},\ v={_vec(v)},\ w={_vec(w)}"
            steps = (
                Step("combine", rf"2u-v={_vec(combined)}"),
                Step("cross", rf"(2u-v)\times w={_vec(result)}"),
            )
        answer = OrderedAnswer(
            tuple(FormulaAnswer(component) for component in result),
            ("x component", "y component", "z component"),
        )
        return Task(
            statement=rf"Calculate the following vector: \({expression},\quad {givens}\).",
            steps=steps,
            answer=answer,
            metadata={"difficulty": params.level, "template": "vector-expression"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


def scalar_expression_seed(level: int, variation: int) -> int:
    return vector_expression_seed(level, variation)


class ScalarVectorExpression(_Generator):
    """A length, a dot product after subtraction, or a scalar triple product."""

    version, prefix, family, code_version = (
        "vector-scalar-expression-v1",
        "VSC",
        "vector-scalar-expression",
        1,
    )
    params, difficulty, template = VectorExpressionParameters, 1, "vector-scalar-expression"
    step_text = {
        "length": "Find the length of v from its coordinates.",
        "difference": "First subtract v from w, coordinate by coordinate.",
        "dot": "Multiply corresponding coordinates and add the products.",
        "cross": "Calculate u cross v in the indicated order.",
        "length_w": "Calculate the length of w.",
        "dot_vw": "Calculate the dot product of v and w.",
        "scalar_difference": "Subtract the dot product from the length.",
    }

    def draw(self, seed: int) -> VectorExpressionParameters:
        return VectorExpression().draw(seed)

    def build(self, params: VectorExpressionParameters) -> Task:
        u, v, w = (_m(vector) for vector in (params.u, params.v, params.w))
        steps: tuple[Step, ...]
        if params.level == 1 and params.seed % 2:
            expression = r"u\cdot w"
            givens = rf"u={_vec(u)},\ w={_vec(w)}"
            value = u.dot(w)
            steps = (Step("dot", rf"u\cdot w={sp.latex(value)}"),)
        elif params.level == 1:
            expression = r"|v|"
            givens = rf"v={_vec(v)}"
            value = v.norm()
            steps = (Step("length", rf"|v|={sp.latex(value)}"),)
        elif params.level == 2 and params.seed % 2:
            expression = r"|w|-v\cdot w"
            givens = rf"v={_vec(v)},\ w={_vec(w)}"
            length, dot = w.norm(), v.dot(w)
            value = length - dot
            steps = (
                Step("length_w", rf"|w|={sp.latex(length)}"),
                Step("dot_vw", rf"v\cdot w={sp.latex(dot)}"),
                Step("scalar_difference", rf"|w|-v\cdot w={sp.latex(value)}"),
            )
        elif params.level == 2:
            expression = r"u\cdot(w-v)"
            givens = rf"u={_vec(u)},\ v={_vec(v)},\ w={_vec(w)}"
            difference = w - v
            value = u.dot(difference)
            steps = (
                Step("difference", rf"w-v={_vec(difference)}"),
                Step("dot", rf"u\cdot(w-v)={sp.latex(value)}"),
            )
        else:
            expression = r"(u\times v)\cdot w"
            givens = rf"u={_vec(u)},\ v={_vec(v)},\ w={_vec(w)}"
            cross = u.cross(v)
            value = cross.dot(w)
            steps = (
                Step("cross", rf"u\times v={_vec(cross)}"),
                Step("dot", rf"(u\times v)\cdot w={sp.latex(value)}"),
            )
        return replace(
            self._task(
                params,
                rf"Calculate the following scalar: \({expression},\quad {givens}\).",
                steps,
                value,
            ),
            metadata={"difficulty": params.level, "template": "vector-scalar-expression"},
        )


def length_seed(level: int, variation: int) -> int:
    return vector_expression_seed(level, variation)


class VectorLengthParameters(Drawn):
    level: int = Field(ge=1, le=3)
    a: int = Field(ge=1, le=5)
    b: int = Field(ge=1, le=5)
    angle: int

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.seed // 10**12 != self.level - 1 or self.angle not in (60, 90, 120):
            raise ValueError("Invalid vector-length settings")
        if self.level == 1 and self.angle != 90:
            raise ValueError("Level one requires perpendicular vectors")
        return self


class VectorLengthPractice(_Generator):
    """Lengths from perpendicularity, an angle, or the parallelogram identity."""

    version, prefix, family, code_version = (
        "vector-length-practice-v1",
        "VLN",
        "vector-length-practice",
        1,
    )
    params, difficulty, template = VectorLengthParameters, 1, "vector-length-practice"
    step_text = {
        "dot": "Use the given angle to find the dot product.",
        "identity": "Relate the sum and difference using the parallelogram identity.",
        "squared": "Find the square of the requested length.",
        "length": "Take the nonnegative square root to obtain the length.",
    }

    def draw(self, seed: int) -> VectorLengthParameters:
        level = seed // 10**12 + 1
        if level not in (1, 2, 3):
            raise ValueError("Invalid vector-length seed")
        rng = DeterministicRNG(seed)
        a, b = rng.randbelow(5) + 1, rng.randbelow(5) + 1
        angle = 90 if level == 1 else (60, 90, 120)[rng.randbelow(3)]
        return VectorLengthParameters(seed=seed, level=level, a=a, b=b, angle=angle)

    def build(self, params: VectorLengthParameters) -> Task:
        a, b = sp.Integer(params.a), sp.Integer(params.b)
        cosine = sp.cos(sp.pi * params.angle / 180)
        dot = a * b * cosine
        squared = a**2 + b**2 - 2 * dot
        value = sp.sqrt(squared)
        if params.level == 1:
            statement = (
                "Vectors u and v are perpendicular. Find the length of their difference: "
                rf"\(|u|={a},\ |v|={b},\quad |u-v|=?\)."
            )
        elif params.level == 2:
            statement = (
                "Find the length of the difference using the given angle between u and v: "
                rf"\(|u|={a},\ |v|={b},\ \theta={params.angle}^\circ,\quad |u-v|=?\)."
            )
        else:
            sum_length = sp.sqrt(a**2 + b**2 + 2 * dot)
            statement = (
                "Find the length of the difference from the given lengths: "
                rf"\(|u|={a},\ |v|={b},\ |u+v|={sp.latex(sum_length)},\quad |u-v|=?\)."
            )
        first = (
            Step("identity", r"|u+v|^2+|u-v|^2=2|u|^2+2|v|^2")
            if params.level == 3
            else Step("dot", rf"u\cdot v=|u||v|\cos({params.angle}^\circ)={sp.latex(dot)}")
        )
        steps = (
            first,
            Step("squared", rf"|u-v|^2={sp.latex(squared)}"),
            Step("length", rf"|u-v|=\sqrt{{{sp.latex(squared)}}}={sp.latex(value)}"),
        )
        return replace(
            self._task(params, statement, steps, value),
            metadata={"difficulty": params.level, "template": "vector-length-practice"},
        )


def parameter_seed(level: int, variation: int) -> int:
    return vector_expression_seed(level, variation)


class PerpendicularParameters(Drawn):
    level: int = Field(ge=1, le=3)
    a: int = Field(ge=1, le=5)
    b: int = Field(ge=1, le=5)
    u: Vector
    v: Vector

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.seed // 10**12 != self.level - 1:
            raise ValueError("Parameter seed and level differ")
        if self.u == (0, 0, 0) or self.v == (0, 0, 0):
            raise ValueError("The vectors must be nonzero")
        if any(abs(value) > 5 for vector in (self.u, self.v) for value in vector):
            raise ValueError("Vector coordinates exceed the practice range")
        if self.level == 2 and _m(self.u).cross(_m(self.v)) == sp.zeros(3, 1):
            raise ValueError("Level two needs nonparallel vectors")
        if self.level == 3 and (
            _m(self.u).dot(_m(self.v)) != 0
            or _m(self.u).dot(_m(self.u)) != self.a**2
            or _m(self.v).dot(_m(self.v)) != self.b**2
        ):
            raise ValueError("Level three requires perpendicular vectors with the given lengths")
        return self


class PerpendicularParameter:
    """All parameters for which two vector expressions are perpendicular."""

    version, prefix, family, code_version = (
        "vector-perpendicular-parameter-v1",
        "VPP",
        "vector-perpendicular-parameter",
        1,
    )
    params, answer, requires = PerpendicularParameters, FiniteSetAnswer, ()
    step_text = {
        "norms": "Calculate the squared lengths of the given vectors.",
        "perpendicular": "Use the perpendicularity of u and v to find their dot product.",
        "expand": "Set the dot product to zero and expand it.",
        "squared": "Isolate the square of the parameter.",
        "roots": "Include both real values of the parameter.",
    }

    def draw(self, seed: int) -> PerpendicularParameters:
        level = seed // 10**12 + 1
        if level not in (1, 2, 3):
            raise ValueError("Invalid perpendicular-parameter seed")
        rng = DeterministicRNG(seed)
        a, b = rng.randbelow(5) + 1, rng.randbelow(5) + 1
        if level == 2:
            for offset in range(64):
                variation = (seed % 10**12 + offset) % 10**12
                drawn = VectorExpression().draw(vector_expression_seed(level, variation))
                if _m(drawn.u).cross(_m(drawn.v)) != sp.zeros(3, 1):
                    u, v = drawn.u, drawn.v
                    break
            else:
                raise ValueError("No nonparallel vector pair after 64 draws")
        else:
            u, v = (a, 0, 0), (0, b, 0)
        return PerpendicularParameters(seed=seed, level=level, a=a, b=b, u=u, v=v)

    def squared_lengths(self, params: PerpendicularParameters) -> tuple[Any, Any]:
        if params.level == 2:
            return _m(params.u).dot(_m(params.u)), _m(params.v).dot(_m(params.v))
        return sp.Integer(params.a**2), sp.Integer(params.b**2)

    def build(self, params: PerpendicularParameters) -> Task:
        squared_u, squared_v = self.squared_lengths(params)
        factor = 2 if params.level == 3 else 1
        root = sp.radsimp(sp.sqrt(squared_u / (factor * squared_v)))
        answer = FiniteSetAnswer((-root, root))
        expression = (
            r"(u+\alpha v)\cdot(u-2\alpha v)" if factor == 2 else r"(u+\alpha v)\cdot(u-\alpha v)"
        )
        leading: tuple[Step, ...]
        if params.level == 2:
            givens = rf"u={_vec(params.u)},\ v={_vec(params.v)}"
            leading = (Step("norms", rf"|u|^2={squared_u},\quad |v|^2={squared_v}"),)
        else:
            givens = rf"|u|={params.a},\ |v|={params.b}"
            leading = (Step("perpendicular", r"u\cdot v=0"),) if factor == 2 else ()
        qualification = "Given u and v are perpendicular, find" if factor == 2 else "Find"
        statement = (
            f"{qualification} all real values of alpha that satisfy the condition: "
            + rf"\({givens},\quad {expression}=0\)."
        )
        steps = (
            *leading,
            Step("expand", rf"{expression}={squared_u}-{factor * squared_v}\alpha^2=0"),
            Step("squared", rf"\alpha^2=\frac{{{squared_u}}}{{{factor * squared_v}}}"),
            Step("roots", rf"\alpha\in {answer.latex()}"),
        )
        return Task(
            statement=statement,
            steps=steps,
            answer=answer,
            metadata={"difficulty": params.level, "template": "vector-perpendicular-parameter"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class PointsParams(Drawn):
    points: tuple[Vector, ...]

    @model_validator(mode="after")
    def valid(self) -> Self:
        if len(self.points) not in (3, 4) or any(abs(c) > 6 for p in self.points for c in p):
            raise ValueError("Three or four bounded points are required")
        a = _m(self.points[0])
        edges = [_m(p) - a for p in self.points[1:]]
        if edges[0].cross(edges[1]) == sp.zeros(3, 1):
            raise ValueError("The first three points must not be collinear")
        if len(edges) == 3 and sp.Matrix.hstack(*edges).det() == 0:
            raise ValueError("The four points must not be coplanar")
        return self


def _draw_points(rng: DeterministicRNG, count: int) -> tuple[Vector, ...]:
    def candidate() -> tuple[Vector, ...]:
        return tuple(
            (rng.randbelow(11) - 5, rng.randbelow(11) - 5, rng.randbelow(11) - 5)
            for _ in range(count)
        )

    def valid(points: tuple[Vector, ...]) -> bool:
        a = _m(points[0])
        edges = [_m(p) - a for p in points[1:]]
        if edges[0].cross(edges[1]) == sp.zeros(3, 1):
            return False
        return len(edges) < 3 or sp.Matrix.hstack(*edges).det() != 0

    return draw_valid(candidate, valid)


NAMES = ("A", "B", "C", "D")


def _points_latex(points: tuple[Vector, ...]) -> str:
    return r",\ ".join(f"{n}={_vec(p)}" for n, p in zip(NAMES, points, strict=False))


class TripleProduct(_Generator):
    """Algebra30 72(i): the scalar triple product (u x v) . w."""

    version = "vector-triple-product-v1"
    prefix = "VTP"
    family = "vector-triple-product"
    params = PointsParams
    difficulty = 1
    template = "triple-product"
    step_text = {
        "cross": "Calculate the cross product u x v.",
        "dot": "Take its dot product with w.",
    }

    def draw(self, seed: int) -> PointsParams:
        return PointsParams(seed=seed, points=_draw_points(DeterministicRNG(seed), 4))

    def build(self, params: PointsParams) -> Task:
        u, v, w = (_m(p) for p in params.points[1:])
        cross = u.cross(v)
        value = cross.dot(w)
        if value != sp.Matrix.hstack(u, v, w).det():
            raise ValueError("Triple product failed verification")
        return self._task(
            params,
            "Calculate the scalar triple product of u, v and w: "
            rf"\(u={_vec(u)},\ v={_vec(v)},\ w={_vec(w)},\quad (u\times v)\cdot w=?\).",
            (
                Step("cross", rf"u\times v={_vec(cross)}"),
                Step("dot", rf"(u\times v)\cdot w={value}"),
            ),
            value,
        )


class TriangleAngle(_Generator):
    """Algebra30 73: the cosine of a triangle's angle at a vertex."""

    version = "vector-triangle-angle-v1"
    prefix = "VTA"
    family = "vector-triangle-angle"
    params = PointsParams
    difficulty = 2
    template = "triangle-angle"
    step_text = {
        "edges": "Form the vectors from B to A and from B to C.",
        "cosine": "Divide their dot product by the product of their lengths.",
    }

    def draw(self, seed: int) -> PointsParams:
        return PointsParams(seed=seed, points=_draw_points(DeterministicRNG(seed), 3))

    def build(self, params: PointsParams) -> Task:
        a, b, c = (_m(p) for p in params.points)
        ba, bc = a - b, c - b
        value = sp.radsimp(ba.dot(bc) / (ba.norm() * bc.norm()))
        if sp.simplify(sp.cos(sp.acos(value)) - value) != 0 or abs(value) >= 1:
            raise ValueError("Triangle angle failed verification")
        return self._task(
            params,
            "Find the cosine of the triangle's angle at the vertex B: "
            rf"\({_points_latex(params.points)}\).",
            (
                Step("edges", rf"\vec{{BA}}={_vec(ba)},\quad \vec{{BC}}={_vec(bc)}"),
                Step(
                    "cosine",
                    rf"\cos\angle B={_ratio(ba.dot(bc), ba.norm() * bc.norm())}={sp.latex(value)}",
                ),
            ),
            value,
        )


def angle_seed(level: int, variation: int) -> int:
    if level not in (1, 2, 3) or not 0 <= variation < 10**12:
        raise ValueError("Invalid angle settings")
    return (level - 1) * 10**12 + variation


class AngleParameters(PointsParams):
    level: int = Field(ge=1, le=3)

    @model_validator(mode="after")
    def valid_level(self) -> Self:
        if self.seed // 10**12 != self.level - 1:
            raise ValueError("Angle seed and level differ")
        return self


class TriangleAngleDegrees(_Generator):
    """The angle itself, in degrees, with increasingly involved constructions."""

    version = "vector-triangle-angle-v2"
    prefix = TriangleAngle.prefix
    family = TriangleAngle.family
    code_version = 2
    params = AngleParameters
    difficulty = 1
    template = "triangle-angle-degrees"
    step_text = {
        "midpoint": "Find the midpoint M of BC, coordinate by coordinate.",
        "edges": "Form the two vectors that start at the required vertex.",
        "products": "Calculate the dot product and the lengths of both vectors.",
        "cosine": "Divide the dot product by the product of the lengths.",
        "angle": "Choose the angle between 0 and 180 degrees with this cosine.",
    }

    def draw(self, seed: int) -> AngleParameters:
        level = seed // 10**12 + 1
        if level not in (1, 2, 3):
            raise ValueError("Invalid angle seed")
        rng = DeterministicRNG(seed)
        shapes = (
            ((1, 0, 0), (1, 1, 0)),
            ((1, 1, 0), (1, 0, 1)),
            ((1, 0, 0), (0, 1, 0)),
            ((1, 1, 0), (-1, 0, 1)),
            ((1, 0, 0), (-1, 1, 0)),
        )
        axes = tuple(permutations(range(3)))

        def candidate() -> tuple[Vector, ...]:
            first, second = shapes[rng.randbelow(len(shapes))]
            order = axes[rng.randbelow(len(axes))]
            signs = tuple(1 if rng.randbelow(2) else -1 for _ in range(3))
            scale_u, scale_v = rng.randbelow(2) + 1, rng.randbelow(2) + 1
            u = tuple(scale_u * signs[i] * first[order[i]] for i in range(3))
            v = tuple(scale_v * signs[i] * second[order[i]] for i in range(3))
            origin = tuple(rng.randbelow(3) - 1 for _ in range(3))
            if level == 3:
                a = origin
                b = tuple(origin[i] + u[i] for i in range(3))
                c = tuple(origin[i] + 2 * v[i] - u[i] for i in range(3))
            else:
                b = origin
                a = tuple(origin[i] + u[i] for i in range(3))
                c = tuple(origin[i] + v[i] for i in range(3))
            return (a, b, c)  # type: ignore[return-value]

        points = draw_valid(candidate, lambda ps: all(abs(x) <= 6 for p in ps for x in p))
        return AngleParameters(seed=seed, level=level, points=points)

    def build(self, params: AngleParameters) -> Task:
        a, b, c = (_m(point) for point in params.points)
        leading: tuple[Step, ...]
        if params.level == 3:
            midpoint = (b + c) / 2
            u, v = b - a, midpoint - a
            names = (r"\vec{AB}", r"\vec{AM}")
            statement = (
                "M is the midpoint of BC in triangle ABC. Find angle BAM in degrees: "
                rf"\({_points_latex(params.points)}\)."
            )
            leading = (Step("midpoint", rf"M=\frac{{B+C}}{{2}}={_vec(midpoint)}"),)
        else:
            u, v = a - b, c - b
            names = (r"\vec u", r"\vec v") if params.level == 1 else (r"\vec{BA}", r"\vec{BC}")
            statement = (
                "Find the angle between the vectors in degrees: "
                rf"\(u={_vec(u)},\ v={_vec(v)}\)."
                if params.level == 1
                else "Find the angle at B of triangle ABC in degrees: "
                rf"\({_points_latex(params.points)}\)."
            )
            leading = ()
        if params.level > 1:
            leading += (Step("edges", rf"{names[0]}={_vec(u)},\quad {names[1]}={_vec(v)}"),)
        dot, length_u, length_v = u.dot(v), u.norm(), v.norm()
        cosine = sp.radsimp(dot / (length_u * length_v))
        angle = sp.simplify(180 * sp.acos(cosine) / sp.pi)
        if angle not in (45, 60, 90, 120, 135):
            raise ValueError("Angle must be a standard nondegenerate angle")
        steps = (
            *leading,
            Step(
                "products",
                rf"{names[0]}\cdot {names[1]}={dot},\quad "
                rf"|{names[0]}|={sp.latex(length_u)},\quad |{names[1]}|={sp.latex(length_v)}",
            ),
            Step("cosine", rf"\cos\theta={_ratio(dot, length_u * length_v)}={sp.latex(cosine)}"),
            Step("angle", rf"\theta={sp.latex(angle)}^\circ"),
        )
        return replace(
            self._task(params, statement, steps, angle),
            metadata={"difficulty": params.level, "template": "triangle-angle-degrees"},
        )


AREA_MODES = ("triangle-area", "parallelogram-area")


def area_seed(level: int, mode: str, variation: int) -> int:
    if level not in (1, 2, 3) or mode not in AREA_MODES or not 0 <= variation < 10**12:
        raise ValueError("Invalid area settings")
    return ((level - 1) * len(AREA_MODES) + AREA_MODES.index(mode)) * 10**12 + variation


class AreaParameters(PointsParams):
    level: int = Field(ge=1, le=3)
    mode: str

    @model_validator(mode="after")
    def valid_settings(self) -> Self:
        if self.mode not in AREA_MODES or self.seed // 10**12 != (
            (self.level - 1) * len(AREA_MODES) + AREA_MODES.index(self.mode)
        ):
            raise ValueError("Area seed and settings differ")
        return self


class AreaPractice(_Generator):
    """Areas of triangles and parallelograms with source-style coordinates."""

    version, prefix, family, code_version = (
        "vector-area-practice-v1",
        "VAP",
        "vector-area-practice",
        1,
    )
    params, difficulty, template = AreaParameters, 1, "vector-area-practice"
    step_text = {
        "midpoint": "Find the midpoint M of BC, coordinate by coordinate.",
        "edges": "Form the two edge vectors from their endpoints.",
        "cross": "Calculate the cross product of the two edge vectors.",
        "area": "Use the length of the cross product to find the requested area.",
    }

    def draw(self, seed: int) -> AreaParameters:
        index, variation = divmod(seed, 10**12)
        level = index // len(AREA_MODES) + 1
        if level not in (1, 2, 3):
            raise ValueError("Invalid area seed")
        mode = AREA_MODES[index % len(AREA_MODES)]
        points = TriangleAngleDegrees().draw(angle_seed(level, variation)).points
        return AreaParameters(seed=seed, level=level, mode=mode, points=points)

    def build(self, params: AreaParameters) -> Task:
        a, b, c = (_m(point) for point in params.points)
        triangle = params.mode == "triangle-area"
        leading: tuple[Step, ...] = ()
        if params.level == 1:
            u, v = a - b, c - b
            names = (r"\vec u", r"\vec v")
            figure = (
                "triangle with adjacent edge vectors" if triangle else "parallelogram spanned by"
            )
            statement = rf"Find the area of the {figure}: \(u={_vec(u)},\ v={_vec(v)}\)."
        elif params.level == 2:
            u, v = b - a, c - a
            names = (r"\vec{AB}", r"\vec{AC}")
            figure = "triangle ABC" if triangle else "parallelogram spanned by AB and AC"
            statement = rf"Find the area of the {figure}: \({_points_latex(params.points)}\)."
        else:
            midpoint = (b + c) / 2
            u, v = b - a, midpoint - a
            names = (r"\vec{AB}", r"\vec{AM}")
            figure = "triangle ABM" if triangle else "parallelogram spanned by AB and AM"
            statement = (
                f"M is the midpoint of BC. Find the area of the {figure}: "
                rf"\({_points_latex(params.points)}\)."
            )
            leading = (Step("midpoint", rf"M=\frac{{B+C}}{{2}}={_vec(midpoint)}"),)
        if params.level > 1:
            leading += (Step("edges", rf"{names[0]}={_vec(u)},\quad {names[1]}={_vec(v)}"),)
        cross = u.cross(v)
        norm = cross.norm()
        value = norm / 2 if triangle else norm
        if sp.simplify(norm**2 - (u.dot(u) * v.dot(v) - u.dot(v) ** 2)) != 0:
            raise ValueError("Area cross product failed verification")
        factor = r"\frac{1}{2}" if triangle else ""
        steps = (
            *leading,
            Step("cross", rf"{names[0]}\times {names[1]}={_vec(cross)}"),
            Step("area", rf"S={factor}|{names[0]}\times {names[1]}|={sp.latex(value)}"),
        )
        return replace(
            self._task(params, statement, steps, value),
            metadata={"difficulty": params.level, "template": params.mode},
        )


class TriangleArea(_Generator):
    """Algebra30 78(a): half the length of a cross product."""

    version = "vector-triangle-area-v1"
    prefix = "VTR"
    family = "vector-triangle-area"
    params = PointsParams
    difficulty = 3
    template = "triangle-area"
    step_text = {
        "cross": "Calculate the cross product of two edge vectors.",
        "area": "The area is half of its length.",
    }

    def draw(self, seed: int) -> PointsParams:
        return PointsParams(seed=seed, points=_draw_points(DeterministicRNG(seed), 3))

    def build(self, params: PointsParams) -> Task:
        a, b, c = (_m(p) for p in params.points)
        cross = (b - a).cross(c - a)
        value = cross.norm() / 2
        heron = sp.sqrt((b - a).norm() ** 2 * (c - a).norm() ** 2 - (b - a).dot(c - a) ** 2) / 2
        if sp.simplify(value - heron) != 0:
            raise ValueError("Triangle area failed verification")
        return self._task(
            params,
            f"Find the area of the triangle ABC: \\({_points_latex(params.points)}\\).",
            (
                Step("cross", rf"\vec{{AB}}\times\vec{{AC}}={_vec(cross)}"),
                Step("area", rf"P=\frac{{1}}{{2}}|\vec{{AB}}\times\vec{{AC}}|={sp.latex(value)}"),
            ),
            value,
        )


class TetrahedronVolume(_Generator):
    """Algebra30 78(b): a sixth of the absolute triple product."""

    version = "vector-tetrahedron-volume-v1"
    prefix = "VTV"
    family = "vector-tetrahedron-volume"
    params = PointsParams
    difficulty = 4
    template = "tetrahedron-volume"
    step_text = {
        "edges": "Form the three edge vectors from A.",
        "volume": "The volume is a sixth of the absolute value of their triple product.",
    }

    def draw(self, seed: int) -> PointsParams:
        return PointsParams(seed=seed, points=_draw_points(DeterministicRNG(seed), 4))

    def build(self, params: PointsParams) -> Task:
        a = _m(params.points[0])
        edges = [_m(p) - a for p in params.points[1:]]
        triple = sp.Matrix.hstack(*edges).det()
        value = sp.Rational(abs(triple), 6)
        if edges[0].cross(edges[1]).dot(edges[2]) != triple:
            raise ValueError("Tetrahedron volume failed verification")
        return self._task(
            params,
            f"Find the volume of the tetrahedron ABCD: \\({_points_latex(params.points)}\\).",
            (
                Step(
                    "edges",
                    r",\ ".join(
                        rf"\vec{{A{n}}}={_vec(e)}" for n, e in zip("BCD", edges, strict=True)
                    ),
                ),
                Step("volume", rf"V=\frac{{1}}{{6}}|{triple}|={sp.latex(value)}"),
            ),
            value,
        )


class TetrahedronHeight(TetrahedronVolume):
    """Algebra30 79: the height from D is 3V divided by the area of ABC."""

    version = "vector-tetrahedron-height-v1"
    prefix = "VTH"
    family = "vector-tetrahedron-height"
    difficulty = 5
    template = "tetrahedron-height"
    step_text = {
        "volume": "Calculate the volume from the triple product.",
        "base": "Calculate the area of the base ABC.",
        "height": "The height is three times the volume divided by the base area.",
    }

    def build(self, params: PointsParams) -> Task:
        a, b, c, d = (_m(p) for p in params.points)
        normal = (b - a).cross(c - a)
        volume = sp.Rational(abs(normal.dot(d - a)), 6)
        base = normal.norm() / 2
        value = sp.radsimp(3 * volume / base)
        if sp.simplify(value - abs(normal.dot(d - a)) / normal.norm()) != 0:
            raise ValueError("Tetrahedron height failed verification")
        return self._task(
            params,
            "Find the height of the tetrahedron ABCD dropped from D: "
            rf"\({_points_latex(params.points)}\).",
            (
                Step("volume", rf"V={sp.latex(volume)}"),
                Step("base", rf"P_{{ABC}}={sp.latex(base)}"),
                Step("height", rf"h=\frac{{3V}}{{P_{{ABC}}}}={sp.latex(value)}"),
            ),
            value,
        )


SOLID_MODES = ("tetrahedron-volume", "tetrahedron-height", "parallelepiped-area")


def solid_seed(level: int, mode: str, variation: int) -> int:
    if level not in (1, 2, 3) or mode not in SOLID_MODES or not 0 <= variation < 10**12:
        raise ValueError("Invalid solid settings")
    return ((level - 1) * len(SOLID_MODES) + SOLID_MODES.index(mode)) * 10**12 + variation


class SolidParameters(PointsParams):
    level: int = Field(ge=1, le=3)
    mode: str

    @model_validator(mode="after")
    def valid_settings(self) -> Self:
        if self.mode not in SOLID_MODES or self.seed // 10**12 != (
            (self.level - 1) * len(SOLID_MODES) + SOLID_MODES.index(self.mode)
        ):
            raise ValueError("Solid seed and settings differ")
        if len(self.points) != 4:
            raise ValueError("A solid needs four noncoplanar points")
        return self


class SolidPractice(_Generator):
    """Source-style tetrahedron and parallelepiped calculations."""

    version, prefix, family, code_version = (
        "vector-solid-practice-v1",
        "VSP",
        "vector-solid-practice",
        1,
    )
    params, difficulty, template = SolidParameters, 1, "vector-solid-practice"
    step_text = {
        "midpoint": "Find the midpoint N of CD, coordinate by coordinate.",
        "edges": "Form the three edge vectors from their endpoints.",
        "cross": "Calculate a normal vector to the base using the cross product.",
        "base": "The base triangle has half the area of the spanned parallelogram.",
        "triple": "Take the dot product of the base normal and the third edge.",
        "volume": "Divide the absolute scalar triple product by six.",
        "height": "Use the volume and base area to find the perpendicular height.",
        "face_uv": "Find the area of the face spanned by the first two edges.",
        "face_uw": "Find the area of the face spanned by the first and third edges.",
        "face_vw": "Find the area of the face spanned by the second and third edges.",
        "surface": "Add the three face areas and double for the opposite faces.",
    }

    def draw(self, seed: int) -> SolidParameters:
        index, _ = divmod(seed, 10**12)
        level = index // len(SOLID_MODES) + 1
        if level not in (1, 2, 3):
            raise ValueError("Invalid solid seed")
        mode = SOLID_MODES[index % len(SOLID_MODES)]
        rng = DeterministicRNG(seed)

        def candidate() -> tuple[Vector, ...]:
            a = (rng.randbelow(3) - 1, rng.randbelow(3) - 1, rng.randbelow(3) - 1)

            def endpoint() -> Vector:
                return (
                    a[0] + rng.randbelow(5) - 2,
                    a[1] + rng.randbelow(5) - 2,
                    a[2] + rng.randbelow(5) - 2,
                )

            return (a, endpoint(), endpoint(), endpoint())

        def valid(points: tuple[Vector, ...]) -> bool:
            a, b, c, d = (_m(point) for point in points)
            determinant = (b - a).cross(c - a).dot(d - a)
            return bool(0 < abs(determinant) <= 24)

        points = draw_valid(candidate, valid)
        return SolidParameters(seed=seed, level=level, mode=mode, points=points)

    def build(self, params: SolidParameters) -> Task:
        a, b, c, d = (_m(point) for point in params.points)
        target = (c + d) / 2 if params.level == 3 else d
        u, v, w = b - a, c - a, target - a
        third = "N" if params.level == 3 else "D"
        names = (r"\vec{AB}", r"\vec{AC}", rf"\vec{{A{third}}}")
        if params.mode == "tetrahedron-volume":
            question = f"the volume of tetrahedron ABC{third}"
        elif params.mode == "tetrahedron-height":
            question = f"the height from {third} to the plane ABC"
        else:
            question = f"the surface area of the parallelepiped spanned by AB, AC and A{third}"
        leading: tuple[Step, ...] = ()
        if params.level == 1:
            statement = (
                f"Find {question} given these adjacent edges from A: "
                rf"\(\vec{{AB}}={_vec(u)},\ \vec{{AC}}={_vec(v)},\ "
                rf"\vec{{AD}}={_vec(w)}\)."
            )
        else:
            prefix = "N is the midpoint of CD. " if params.level == 3 else ""
            statement = f"{prefix}Find {question}: " + rf"\({_points_latex(params.points)}\)."
            if params.level == 3:
                leading += (Step("midpoint", rf"N=\frac{{C+D}}{{2}}={_vec(target)}"),)
            leading += (
                Step(
                    "edges",
                    rf"{names[0]}={_vec(u)},\quad {names[1]}={_vec(v)},\quad {names[2]}={_vec(w)}",
                ),
            )
        normal = u.cross(v)
        triple = normal.dot(w)
        if triple != sp.det(sp.Matrix.hstack(u, v, w)):
            raise ValueError("Scalar triple product failed verification")
        if params.mode == "parallelepiped-area":
            face_areas = (normal.norm(), u.cross(w).norm(), v.cross(w).norm())
            value = 2 * sum(face_areas)
            steps = (
                leading
                + tuple(
                    Step(key, rf"|{first}\times {second}|={sp.latex(area)}")
                    for key, first, second, area in (
                        ("face_uv", names[0], names[1], face_areas[0]),
                        ("face_uw", names[0], names[2], face_areas[1]),
                        ("face_vw", names[1], names[2], face_areas[2]),
                    )
                )
                + (
                    Step(
                        "surface",
                        rf"S=2\left({'+'.join(sp.latex(area) for area in face_areas)}\right)"
                        rf"={sp.latex(value)}",
                    ),
                )
            )
        else:
            volume = abs(triple) / 6
            value = volume if params.mode == "tetrahedron-volume" else abs(triple) / normal.norm()
            steps = leading + (Step("cross", rf"{names[0]}\times {names[1]}={_vec(normal)}"),)
            if params.mode == "tetrahedron-height":
                steps += (
                    Step(
                        "base",
                        rf"S_{{ABC}}=\frac{{1}}{{2}}|{names[0]}\times {names[1]}|"
                        rf"={sp.latex(normal.norm() / 2)}",
                    ),
                )
            steps += (
                Step(
                    "triple", rf"({names[0]}\times {names[1]})\cdot {names[2]}={sp.latex(triple)}"
                ),
                Step("volume", rf"V=\frac{{|{sp.latex(triple)}|}}{{6}}={sp.latex(volume)}"),
            )
            if params.mode == "tetrahedron-height":
                steps += (
                    Step("height", rf"h=\frac{{3V}}{{S_{{ABC}}}}={sp.latex(sp.radsimp(value))}"),
                )
        return replace(
            self._task(params, statement, steps, value),
            metadata={"difficulty": params.level, "template": params.mode},
        )


# Lines and planes -----------------------------------------------------------


def _plane(normal: sp.Matrix, offset: Any) -> str:
    expression = sum(int(n) * s for n, s in zip(normal, sp.symbols("x y z"), strict=True)) + offset
    return f"{sp.latex(expression)}=0"


class PointPlaneDistance(_Generator):
    """Algebra30 86(b): the distance from D to the plane through A, B and C."""

    version = "geometry-point-plane-distance-v1"
    prefix = "GPP"
    family = "geometry-point-plane-distance"
    params = PointsParams
    difficulty = 1
    template = "point-plane-distance"
    step_text = {
        "normal": "A normal vector is the cross product of two edge vectors.",
        "plane": "Write the plane through A with this normal.",
        "distance": "Use the point-to-plane distance formula.",
    }

    def draw(self, seed: int) -> PointsParams:
        return PointsParams(seed=seed, points=_draw_points(DeterministicRNG(seed), 4))

    def build(self, params: PointsParams) -> Task:
        a, b, c, d = (_m(p) for p in params.points)
        normal = (b - a).cross(c - a)
        normal = normal / sp.gcd(list(normal))
        offset = -normal.dot(a)
        value = sp.radsimp(abs(normal.dot(d) + offset) / normal.norm())
        if any(normal.dot(p) + offset != 0 for p in (a, b, c)):
            raise ValueError("Plane failed verification")
        return self._task(
            params,
            "Find the distance from the point D to the plane through A, B and C: "
            rf"\({_points_latex(params.points)}\).",
            (
                Step("normal", rf"n={_vec(normal)}"),
                Step("plane", _plane(normal, offset)),
                Step(
                    "distance",
                    rf"d={_ratio(abs(normal.dot(d) + offset), normal.norm())}={sp.latex(value)}",
                ),
            ),
            value,
        )


class PlanesParams(Drawn):
    normal: Vector
    offsets: tuple[int, int]
    scale: int = Field(ge=1, le=3)
    second: Vector

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.normal == (0, 0, 0) or self.second == (0, 0, 0):
            raise ValueError("Normals must be nonzero")
        if any(abs(c) > 6 for c in (*self.normal, *self.second)) or any(
            abs(o) > 20 for o in self.offsets
        ):
            raise ValueError("Plane data is outside the declared range")
        return self


def _draw_planes(rng: DeterministicRNG) -> PlanesParams:
    def vector() -> Vector:
        return draw_valid(
            lambda: (rng.randbelow(9) - 4, rng.randbelow(9) - 4, rng.randbelow(9) - 4),
            lambda v: v != (0, 0, 0),
        )

    first = vector()
    second = draw_valid(vector, lambda v: _m(v).cross(_m(first)) != sp.zeros(3, 1))
    return PlanesParams(
        seed=0,
        normal=first,
        offsets=(rng.randbelow(41) - 20, rng.randbelow(41) - 20),
        scale=1 + rng.randbelow(3),
        second=second,
    )


class ParallelPlanesDistance(_Generator):
    """Algebra30 86(e): two parallel planes, one written with a multiple of the normal."""

    version = "geometry-parallel-planes-v1"
    prefix = "GPL"
    family = "geometry-parallel-planes"
    params = PlanesParams
    difficulty = 2
    template = "parallel-planes"
    step_text = {
        "scale": "Divide the second equation so that both planes have the same normal.",
        "distance": "The distance is the difference of the free terms over the normal's length.",
    }

    def draw(self, seed: int) -> PlanesParams:
        rng = DeterministicRNG(seed)
        drawn = _draw_planes(rng)
        offsets = draw_valid(
            lambda: (rng.randbelow(41) - 20, rng.randbelow(41) - 20), lambda o: o[0] != o[1]
        )
        return drawn.model_copy(update={"seed": seed, "offsets": offsets})

    def build(self, params: PlanesParams) -> Task:
        n = _m(params.normal)
        d1, d2 = params.offsets
        if d1 == d2:
            raise ValueError("The planes must differ")
        k = params.scale
        value = sp.radsimp(sp.Rational(abs(d1 - d2), 1) / n.norm())
        point = _plane_point(n, d1)
        if sp.simplify(abs(n.dot(point) + d2) / n.norm() - value) != 0:
            raise ValueError("Parallel planes failed verification")
        return self._task(
            params,
            "Find the distance between the parallel planes: "
            rf"\(\pi_1:\ {_plane(n, d1)},\quad \pi_2:\ {_plane(k * n, k * d2)}\).",
            (
                Step("scale", rf"\pi_2:\ {_plane(n, d2)}"),
                Step(
                    "distance",
                    rf"d=\frac{{|{d1}-({d2})|}}{{{sp.latex(n.norm())}}}={sp.latex(value)}",
                ),
            ),
            value,
        )


def _plane_point(normal: sp.Matrix, offset: int) -> sp.Matrix:
    index = next(i for i in range(3) if normal[i] != 0)
    point = sp.zeros(3, 1)
    point[index] = sp.Rational(-offset, normal[index])
    return point


class PlanesAngle(ParallelPlanesDistance):
    """Algebra30 89: the cosine of the angle between two planes."""

    version = "geometry-planes-angle-v1"
    prefix = "GPA"
    family = "geometry-planes-angle"
    difficulty = 3
    template = "planes-angle"
    step_text = {
        "normals": "The angle between the planes is the acute angle between their normals.",
        "cosine": "Divide the absolute dot product by the product of the lengths.",
    }

    def draw(self, seed: int) -> PlanesParams:
        return _draw_planes(DeterministicRNG(seed)).model_copy(update={"seed": seed})

    def build(self, params: PlanesParams) -> Task:
        n1, n2 = _m(params.normal), _m(params.second)
        value = sp.radsimp(abs(n1.dot(n2)) / (n1.norm() * n2.norm()))
        if not 0 <= value < 1:
            raise ValueError("Planes angle failed verification")
        d1, d2 = params.offsets
        return self._task(
            params,
            "Find the cosine of the angle between the planes: "
            rf"\(\pi_1:\ {_plane(n1, d1)},\quad \pi_2:\ {_plane(n2, d2)}\).",
            (
                Step("normals", rf"n_1={_vec(n1)},\quad n_2={_vec(n2)}"),
                Step(
                    "cosine",
                    rf"\cos\varphi={_ratio(abs(n1.dot(n2)), n1.norm() * n2.norm())}"
                    rf"={sp.latex(value)}",
                ),
            ),
            value,
        )


class LinePlaneParams(Drawn):
    point: Vector
    direction: Vector
    normal: Vector
    parameter: int = Field(ge=-3, le=3)
    coordinate: int = Field(ge=0, le=2)

    @model_validator(mode="after")
    def valid(self) -> Self:
        if any(abs(c) > 5 for c in (*self.point, *self.direction, *self.normal)):
            raise ValueError("Line and plane data is outside the declared range")
        if _m(self.direction).dot(_m(self.normal)) == 0 or self.normal == (0, 0, 0):
            raise ValueError("The line must cross the plane")
        return self


def _line(point: Vector, direction: Vector) -> str:
    coordinates = sp.symbols("x y z")
    t = sp.Symbol("t")
    rows = [
        f"{sp.latex(c)}={sp.latex(p + d * t)}"
        for c, p, d in zip(coordinates, point, direction, strict=True)
    ]
    return r"\begin{cases}" + r"\\".join(rows) + r"\end{cases}"


class LinePlaneIntersection(_Generator):
    """Algebra30 82(b): substitute the line into the plane, then read a coordinate."""

    version = "geometry-line-plane-v1"
    prefix = "GLP"
    family = "geometry-line-plane"
    params = LinePlaneParams
    difficulty = 4
    template = "line-plane-intersection"
    step_text = {
        "substitute": "Substitute the parametric equations into the plane's equation.",
        "parameter": "Solve for the parameter.",
        "point": "Substitute it back to get the intersection point.",
    }

    def draw(self, seed: int) -> LinePlaneParams:
        rng = DeterministicRNG(seed)

        def vector() -> Vector:
            return (rng.randbelow(7) - 3, rng.randbelow(7) - 3, rng.randbelow(7) - 3)

        point = vector()
        direction = draw_valid(vector, lambda v: v != (0, 0, 0))
        normal = draw_valid(vector, lambda n: _m(n).dot(_m(direction)) != 0)
        return LinePlaneParams(
            seed=seed,
            point=point,
            direction=direction,
            normal=normal,
            parameter=rng.randbelow(7) - 3,
            coordinate=rng.randbelow(3),
        )

    def build(self, params: LinePlaneParams) -> Task:
        p, d, n = _m(params.point), _m(params.direction), _m(params.normal)
        crossing = p + params.parameter * d
        offset = -n.dot(crossing)
        t = sp.Symbol("t")
        solved = sp.solve(n.dot(p + t * d) + offset, t)
        if solved != [params.parameter]:
            raise ValueError("Line and plane intersection failed verification")
        name = "xyz"[params.coordinate]
        return self._task(
            params,
            f"Find the {name}-coordinate of the intersection point of the line and the plane: "
            rf"\({_line(params.point, params.direction)},\quad {_plane(n, offset)}\).",
            (
                Step("substitute", rf"{sp.latex(sp.expand(n.dot(p + t * d) + offset))}=0"),
                Step("parameter", rf"t={params.parameter}"),
                Step("point", rf"P={_vec(crossing)}"),
            ),
            crossing[params.coordinate],
        )


class ReflectionParams(Drawn):
    normal: Vector
    offset: int = Field(ge=-20, le=20)
    point: Vector
    coordinate: int = Field(ge=0, le=2)

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.normal == (0, 0, 0) or any(abs(c) > 5 for c in (*self.normal, *self.point)):
            raise ValueError("Reflection data is outside the declared range")
        return self


class PlaneReflection(_Generator):
    """Algebra30 96: the mirror image of a point in a plane."""

    version = "geometry-plane-reflection-v1"
    prefix = "GPR"
    family = "geometry-plane-reflection"
    params = ReflectionParams
    difficulty = 5
    template = "plane-reflection"
    step_text = {
        "foot": "Project the point onto the plane along the normal.",
        "reflect": "The image is twice the projection minus the point.",
    }

    def draw(self, seed: int) -> ReflectionParams:
        rng = DeterministicRNG(seed)
        normal = draw_valid(
            lambda: (rng.randbelow(7) - 3, rng.randbelow(7) - 3, rng.randbelow(7) - 3),
            lambda v: v != (0, 0, 0),
        )
        return ReflectionParams(
            seed=seed,
            normal=normal,
            offset=rng.randbelow(41) - 20,
            point=(rng.randbelow(11) - 5, rng.randbelow(11) - 5, rng.randbelow(11) - 5),
            coordinate=rng.randbelow(3),
        )

    def build(self, params: ReflectionParams) -> Task:
        n, p = _m(params.normal), _m(params.point)
        t = -(n.dot(p) + params.offset) / sp.Integer(n.dot(n))
        foot = p + t * n
        image = 2 * foot - p
        if n.dot(foot) + params.offset != 0 or (image - p).cross(n) != sp.zeros(3, 1):
            raise ValueError("Reflection failed verification")
        name = "xyz"[params.coordinate]
        return self._task(
            params,
            f"Find the {name}-coordinate of the reflection of P in the plane: "
            rf"\(P={_vec(p)},\quad {_plane(n, params.offset)}\).",
            (
                Step("foot", rf"P_0={_vec(foot)}"),
                Step("reflect", rf"P'=2P_0-P={_vec(image)}"),
            ),
            image[params.coordinate],
        )


def generators() -> tuple[TaskGenerator[Any], ...]:
    return (
        LargestEigenvalue(),
        EigenvectorValue(),
        DiagonalPower(),
        TriangularPowerEigenvalue(),
        MatrixFromEigenvectors(),
        VectorExpression(),
        ScalarVectorExpression(),
        VectorLengthPractice(),
        PerpendicularParameter(),
        AreaPractice(),
        SolidPractice(),
        TripleProduct(),
        TriangleAngle(),
        TriangleAngleDegrees(),
        TriangleArea(),
        TetrahedronVolume(),
        TetrahedronHeight(),
        PointPlaneDistance(),
        ParallelPlanesDistance(),
        PlanesAngle(),
        LinePlaneIntersection(),
        PlaneReflection(),
    )
