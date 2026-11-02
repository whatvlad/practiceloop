"""Determinants, inverses, linear systems and rank from algebra30 exercises 14-40 (#221).

Every task asks for one exact scalar, so it uses the existing expression answer:
a determinant, one entry of an inverse or unknown matrix, one unknown of a
system, a rank, a number of free parameters or a parameter value.
"""

from fractions import Fraction
from itertools import permutations
from typing import Any, Literal, Self

import sympy as sp
from pydantic import Field, model_validator

from app.engine.answers.expression import ExpressionAnswer
from app.engine.blocks.matrices import (
    IntMatrix,
    bounded,
    det,
    draw_entries,
    draw_invertible,
    fractions,
    minor,
    nonzero_rows,
    pmatrix,
    row_echelon,
    system_latex,
    to_sympy,
)
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task, TaskGenerator
from app.engine.prng import DeterministicRNG, draw_valid

ORDINALS = ("first", "second", "third", "fourth")


def _square(matrix: IntMatrix, size: int, bound: int) -> None:
    if len(matrix) != size or any(len(row) != size for row in matrix):
        raise ValueError(f"Matrix must be {size} x {size}")
    if not bounded(matrix, bound):
        raise ValueError("Matrix entries are outside the declared range")


def _task(
    generator: Any,
    params: Drawn,
    statement: str,
    steps: tuple[Step, ...],
    value: Any,
    difficulty: int,
    template: str,
) -> Task:
    return Task(
        statement=statement,
        steps=steps,
        answer=ExpressionAnswer(sp.sympify(value), {}),
        metadata={"difficulty": difficulty, "template": template},
        code=encode(generator.prefix, generator.code_version, params.seed),
        generator_version=generator.version,
    )


def _signed(sign: int, coefficient: int, inner: str) -> str:
    value = sign * coefficient
    return rf"{'-' if value < 0 else '+'}{abs(value)}\cdot {inner}"


def _laplace(matrix: IntMatrix, row: int) -> tuple[str, str, int]:
    """The cofactor expansion along `row`, the same with minor values, and the total."""
    symbolic, numeric, total = [], [], 0
    for column, entry in enumerate(matrix[row]):
        if entry == 0:
            continue
        sign = (-1) ** (row + column)
        part = minor(matrix, row, column)
        value = det(part)
        total += sign * entry * value
        symbolic.append(_signed(sign, entry, rf"\det{pmatrix(part)}"))
        numeric.append(_signed(sign, entry, f"({value})"))
    return "".join(symbolic).lstrip("+"), "".join(numeric).lstrip("+"), total


class DeterminantParams(Drawn):
    matrix: IntMatrix

    @model_validator(mode="after")
    def shape(self) -> Self:
        _square(self.matrix, len(self.matrix), 4)
        if len(self.matrix) not in (3, 4):
            raise ValueError("Determinants are 3 x 3 or 4 x 4")
        if len(self.matrix) == 4 and not any(row.count(0) >= 2 for row in self.matrix):
            raise ValueError("A 4 x 4 matrix needs a row with two zeros")
        return self


class Determinant3:
    version = "algebra-determinant-3x3-v1"
    prefix = "DTR"
    family = "algebra-determinant"
    code_version = 1
    params = DeterminantParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    size = 3
    difficulty = 1
    step_text = {
        "laplace": "Expand along the row with the most zeros, alternating the cofactor signs.",
        "minors": "Calculate each smaller determinant.",
        "result": "Add the terms.",
    }

    def draw(self, seed: int) -> DeterminantParams:
        rng = DeterministicRNG(seed)
        return DeterminantParams(seed=seed, matrix=draw_entries(rng, 3, 3, 4))

    def build(self, params: DeterminantParams) -> Task:
        matrix = params.matrix
        if len(matrix) != self.size:
            raise ValueError("Matrix size belongs to another generator")
        row = max(range(self.size), key=lambda r: (matrix[r].count(0), -r))
        symbolic, numeric, total = _laplace(matrix, row)
        if total != det(matrix) or total != to_sympy(matrix).det(method="berkowitz"):
            raise ValueError("Determinant failed verification")
        return _task(
            self,
            params,
            rf"Calculate \(\det{pmatrix(matrix)}\).",
            (
                Step("laplace", rf"\det A={symbolic or '0'}"),
                Step("minors", rf"\det A={numeric or '0'}"),
                Step("result", rf"\det A={total}"),
            ),
            total,
            self.difficulty,
            f"determinant-{self.size}x{self.size}",
        )


class Determinant4(Determinant3):
    version = "algebra-determinant-4x4-v1"
    prefix = "DTF"
    family = "algebra-determinant-4x4"
    size = 4
    difficulty = 4

    def draw(self, seed: int) -> DeterminantParams:
        rng = DeterministicRNG(seed)
        entries = [list(row) for row in draw_entries(rng, 4, 4, 3)]
        row = rng.randbelow(4)
        first = rng.randbelow(4)
        second = (first + 1 + rng.randbelow(3)) % 4
        entries[row][first] = entries[row][second] = 0
        return DeterminantParams(seed=seed, matrix=tuple(tuple(r) for r in entries))


class ScalingParams(Drawn):
    size: int = Field(ge=2, le=7)
    determinant: int = Field(ge=-3, le=3)
    scale: Literal[-3, -2, -1, 2, 3]
    power: int = Field(ge=1, le=3)
    transpose: bool

    @model_validator(mode="after")
    def nonzero(self) -> Self:
        if self.determinant == 0:
            raise ValueError("The given determinant must be nonzero")
        return self


class DeterminantScaling:
    """Algebra30 exercise 15: det(cA) = c^n det A, det(A^m) = (det A)^m, det A^T = det A."""

    version = "algebra-determinant-scaling-v1"
    prefix = "DTS"
    family = "algebra-determinant-scaling"
    code_version = 1
    params = ScalingParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    step_text = {
        "scale": "A scalar multiplies every row, so it comes out once per row.",
        "power": "The determinant of a product is the product of the determinants.",
        "result": "Substitute the given determinant.",
    }

    def draw(self, seed: int) -> ScalingParams:
        rng = DeterministicRNG(seed)
        determinant = (1 + rng.randbelow(3)) * (1 - 2 * rng.randbelow(2))
        return ScalingParams(
            seed=seed,
            size=2 + rng.randbelow(6),
            determinant=determinant,
            scale=(-3, -2, -1, 2, 3)[rng.randbelow(5)],
            power=1 + rng.randbelow(3),
            transpose=rng.randbelow(2) == 1,
        )

    def build(self, params: ScalingParams) -> Task:
        n, d, c, m = params.size, params.determinant, params.scale, params.power
        base = "A^{T}" if params.transpose else "A"
        powered = base if m == 1 else (f"({base})^{{{m}}}" if params.transpose else f"A^{{{m}}}")
        scaled = f"-{powered}" if c == -1 else f"{c}{powered}"
        expected = sp.Integer(c) ** n * sp.Integer(d) ** m
        # An independent instance: any n x n matrix with determinant d gives the same value.
        sample = sp.diag(d, *([1] * (n - 1))) + sp.Matrix(n, n, lambda i, j: int(j == i + 1))
        sample = sample.T if params.transpose else sample
        if sample.det() != d or (c * sample**m).det() != expected:
            raise ValueError("Determinant scaling failed verification")
        return _task(
            self,
            params,
            "Use the properties of determinants to find the value: "
            rf"\(A\in\mathbb{{R}}^{{{n}\times {n}}},\ \det A={d},\quad \det({scaled})=?\).",
            (
                Step("scale", rf"\det({scaled})=({c})^{{{n}}}\det({powered})"),
                Step("power", rf"\det({powered})=(\det A)^{{{m}}}"),
                Step("result", rf"({c})^{{{n}}}\cdot({d})^{{{m}}}={expected}"),
            ),
            expected,
            2,
            "determinant-scaling",
        )


ROW_SYMBOLS = (sp.symbols("a b c"), sp.symbols("d e f"), sp.symbols("g h i"))
PERMUTATIONS = tuple(permutations(range(3)))


class RowOperationParams(Drawn):
    determinant: int = Field(ge=-9, le=9)
    order: int = Field(ge=0, le=5)
    scales: tuple[int, int, int]
    target: int = Field(ge=0, le=2)
    source: int = Field(ge=0, le=2)
    multiple: int = Field(ge=-3, le=3)

    @model_validator(mode="after")
    def valid(self) -> Self:
        if self.determinant == 0 or self.target == self.source:
            raise ValueError("Need a nonzero determinant and two different rows")
        if any(s == 0 or abs(s) > 4 for s in self.scales):
            raise ValueError("Row scales must be nonzero and at most 4")
        return self


class DeterminantRowOperations:
    """Algebra30 exercise 14: swapped, scaled and combined rows of a known determinant."""

    version = "algebra-determinant-rows-v1"
    prefix = "DRO"
    family = "algebra-determinant-rows"
    code_version = 1
    params = RowOperationParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    step_text = {
        "combine": "Adding a multiple of one row to another does not change the determinant.",
        "scale": "Take each row's factor out of the determinant.",
        "swap": "Each exchange of two rows changes the sign.",
        "result": "Substitute the given determinant.",
    }

    def draw(self, seed: int) -> RowOperationParams:
        rng = DeterministicRNG(seed)
        target = rng.randbelow(3)
        return RowOperationParams(
            seed=seed,
            determinant=(1 + rng.randbelow(9)) * (1 - 2 * rng.randbelow(2)),
            order=rng.randbelow(6),
            scales=tuple(  # type: ignore[arg-type]
                (1, 1, 2, 3, -1, -2, -3, 4)[rng.randbelow(8)] for _ in range(3)
            ),
            target=target,
            source=(target + 1 + rng.randbelow(2)) % 3,
            multiple=rng.randbelow(7) - 3,
        )

    def build(self, params: RowOperationParams) -> Task:
        order = PERMUTATIONS[params.order]
        rows = [
            [s * value for value in ROW_SYMBOLS[o]]
            for s, o in zip(params.scales, order, strict=True)
        ]
        added = ROW_SYMBOLS[order[params.source]]
        rows[params.target] = [
            v + params.multiple * a for v, a in zip(rows[params.target], added, strict=True)
        ]
        swaps = sum(1 for i in range(3) for j in range(i + 1, 3) if order[i] > order[j])
        sign = -1 if swaps % 2 else 1
        factor = sign * params.scales[0] * params.scales[1] * params.scales[2]
        original = sp.Matrix(ROW_SYMBOLS)
        if sp.expand(sp.Matrix(rows).det() - factor * original.det()) != 0:
            raise ValueError("Row operations failed verification")
        expected = factor * params.determinant
        given = pmatrix([[sp.latex(v) for v in row] for row in ROW_SYMBOLS])
        changed = pmatrix([[sp.latex(v) for v in row] for row in rows])
        scaled = pmatrix([[sp.latex(v) for v in ROW_SYMBOLS[o]] for o in order])
        product = r"\cdot ".join(f"({s})" for s in params.scales)
        unmixed = [
            [sp.latex(s * v) for v in ROW_SYMBOLS[o]]
            for s, o in zip(params.scales, order, strict=True)
        ]
        return _task(
            self,
            params,
            "Use the properties of determinants to find the second determinant: "
            rf"\(\det{given}={params.determinant},\quad \det{changed}=?\).",
            (
                Step("combine", rf"\det{changed}=\det{pmatrix(unmixed)}"),
                Step("scale", rf"={product}\cdot\det{scaled}"),
                Step("swap", rf"\det{scaled}={'-' if sign < 0 else ''}{params.determinant}"),
                Step("result", rf"{product}\cdot({sign * params.determinant})={expected}"),
            ),
            expected,
            2,
            "determinant-rows",
        )


class SingularParams(Drawn):
    matrix: IntMatrix
    row: int = Field(ge=0, le=2)
    column: int = Field(ge=0, le=2)

    @model_validator(mode="after")
    def solvable(self) -> Self:
        _square(self.matrix, 3, 5)
        if self.matrix[self.row][self.column] != 0:
            raise ValueError("The parameter's position holds 0 in the stored matrix")
        if det(minor(self.matrix, self.row, self.column)) == 0:
            raise ValueError("The parameter must appear in the determinant")
        return self


class SingularParameter:
    """Algebra30 exercise 19: the parameter value making a matrix non-invertible."""

    version = "algebra-singular-parameter-v1"
    prefix = "DSG"
    family = "algebra-invertibility"
    code_version = 1
    params = SingularParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    step_text = {
        "condition": "A matrix is invertible exactly when its determinant is not zero.",
        "laplace": "Expand the determinant along the row that contains the parameter.",
        "solve": "Solve the linear equation for the parameter.",
    }

    def draw(self, seed: int) -> SingularParams:
        rng = DeterministicRNG(seed)
        row, column = rng.randbelow(3), rng.randbelow(3)

        def candidate() -> IntMatrix:
            entries = [list(r) for r in draw_entries(rng, 3, 3, 4)]
            entries[row][column] = 0
            return tuple(tuple(r) for r in entries)

        matrix = draw_valid(candidate, lambda m: det(minor(m, row, column)) != 0)
        return SingularParams(seed=seed, matrix=matrix, row=row, column=column)

    def build(self, params: SingularParams) -> Task:
        p = sp.Symbol("p")
        entries = [[sp.Integer(v) for v in row] for row in params.matrix]
        entries[params.row][params.column] = p
        determinant = sp.expand(sp.Matrix(entries).det())
        slope = (-1) ** (params.row + params.column) * det(
            minor(params.matrix, params.row, params.column)
        )
        offset = det(params.matrix)
        if determinant != slope * p + offset:
            raise ValueError("Parameter determinant failed verification")
        value = sp.Rational(-offset, slope)
        if sp.Matrix(entries).subs(p, value).det() != 0:
            raise ValueError("Parameter value failed verification")
        return _task(
            self,
            params,
            "Find the value of p for which the matrix is not invertible: "
            rf"\({pmatrix(entries)}\).",
            (
                Step("condition", rf"\det{pmatrix(entries)}=0"),
                Step("laplace", rf"{sp.latex(determinant)}=0"),
                Step("solve", rf"p={sp.latex(value)}"),
            ),
            value,
            3,
            "singular-parameter",
        )


class InverseParams(Drawn):
    matrix: IntMatrix
    row: int = Field(ge=0, le=2)
    column: int = Field(ge=0, le=2)

    @model_validator(mode="after")
    def invertible(self) -> Self:
        _square(self.matrix, len(self.matrix), 12)
        if len(self.matrix) not in (2, 3) or max(self.row, self.column) >= len(self.matrix):
            raise ValueError("Inverse entries come from a 2 x 2 or 3 x 3 matrix")
        if det(self.matrix) == 0:
            raise ValueError("Matrix must be invertible")
        return self


def _inverse_steps(matrix: IntMatrix) -> tuple[sp.Matrix, tuple[Step, ...]]:
    a = to_sympy(matrix)
    determinant = det(matrix)
    adjugate = a.adjugate()
    inverse = adjugate / determinant
    if a * inverse != sp.eye(len(matrix)):
        raise ValueError("Inverse failed verification")
    return inverse, (
        Step("determinant", rf"\det A={determinant}"),
        Step("adjugate", rf"A^{{-1}}=\frac{{1}}{{{determinant}}}{pmatrix(adjugate.tolist())}"),
        Step("inverse", rf"A^{{-1}}={pmatrix(inverse.tolist())}"),
    )


class InverseEntry:
    version = "algebra-inverse-2x2-v1"
    prefix = "INV"
    family = "algebra-inverse"
    code_version = 1
    params = InverseParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    size = 2
    difficulty = 1
    step_text = {
        "determinant": "Calculate the determinant; it must not be zero.",
        "adjugate": "Transpose the matrix of cofactors and divide it by the determinant.",
        "inverse": "Simplify every entry of the inverse.",
        "entry": "Read off the requested entry.",
    }

    def draw(self, seed: int) -> InverseParams:
        rng = DeterministicRNG(seed)
        matrix = draw_invertible(rng, self.size, (1, -1, 2, -2, 3))
        return InverseParams(
            seed=seed,
            matrix=matrix,
            row=rng.randbelow(self.size),
            column=rng.randbelow(self.size),
        )

    def build(self, params: InverseParams) -> Task:
        if len(params.matrix) != self.size:
            raise ValueError("Matrix size belongs to another generator")
        inverse, steps = _inverse_steps(params.matrix)
        value = inverse[params.row, params.column]
        return _task(
            self,
            params,
            f"Find the entry in the {ORDINALS[params.row]} row and "
            f"{ORDINALS[params.column]} column of the inverse matrix: "
            rf"\(A={pmatrix(params.matrix)},\quad A^{{-1}}=?\).",
            (
                *steps,
                Step(
                    "entry",
                    rf"(A^{{-1}})_{{{params.row + 1}{params.column + 1}}}={sp.latex(value)}",
                ),
            ),
            value,
            self.difficulty,
            f"inverse-{self.size}x{self.size}",
        )


class InverseEntry3(InverseEntry):
    version = "algebra-inverse-3x3-v1"
    prefix = "INVT"
    family = "algebra-inverse-3x3"
    size = 3
    difficulty = 2

    def draw(self, seed: int) -> InverseParams:
        rng = DeterministicRNG(seed)
        matrix = draw_invertible(rng, 3, (1, -1, 2, -2))
        return InverseParams(
            seed=seed, matrix=matrix, row=rng.randbelow(3), column=rng.randbelow(3)
        )


class MatrixEquationParams(Drawn):
    matrix: IntMatrix
    unknown: IntMatrix
    left: bool
    row: int = Field(ge=0, le=1)
    column: int = Field(ge=0, le=1)

    @model_validator(mode="after")
    def invertible(self) -> Self:
        _square(self.matrix, 2, 12)
        _square(self.unknown, 2, 3)
        if det(self.matrix) == 0:
            raise ValueError("Coefficient matrix must be invertible")
        return self


class MatrixEquation:
    """Algebra30 exercises 13 and 22: solve XA = C or AX = C with an inverse."""

    version = "algebra-matrix-equation-v1"
    prefix = "MEQ"
    family = "algebra-matrix-equation"
    code_version = 1
    params = MatrixEquationParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    step_text = {
        "isolate": "Multiply both sides by the inverse of A on the same side as A.",
        "inverse": "Find the inverse of A.",
        "multiply": "Multiply the matrices.",
        "entry": "Read off the requested entry.",
    }

    def draw(self, seed: int) -> MatrixEquationParams:
        rng = DeterministicRNG(seed)
        return MatrixEquationParams(
            seed=seed,
            matrix=draw_invertible(rng, 2, (1, -1, 2, -2)),
            unknown=draw_entries(rng, 2, 2, 3),
            left=rng.randbelow(2) == 1,
            row=rng.randbelow(2),
            column=rng.randbelow(2),
        )

    def build(self, params: MatrixEquationParams) -> Task:
        a, x = to_sympy(params.matrix), to_sympy(params.unknown)
        c = a * x if params.left else x * a
        inverse = a.inv()
        solved = inverse * c if params.left else c * inverse
        if solved != x or (a * solved if params.left else solved * a) != c:
            raise ValueError("Matrix equation failed verification")
        equation = (
            rf"{pmatrix(params.matrix)}X={pmatrix(c.tolist())}"
            if params.left
            else rf"X{pmatrix(params.matrix)}={pmatrix(c.tolist())}"
        )
        isolated = r"X=A^{-1}C" if params.left else r"X=CA^{-1}"
        value = x[params.row, params.column]
        return _task(
            self,
            params,
            f"Find the entry in the {ORDINALS[params.row]} row and "
            f"{ORDINALS[params.column]} column of the unknown matrix X: "
            rf"\({equation}\).",
            (
                Step("isolate", isolated),
                Step("inverse", rf"A^{{-1}}={pmatrix(inverse.tolist())}"),
                Step("multiply", rf"X={pmatrix(x.tolist())}"),
                Step("entry", rf"x_{{{params.row + 1}{params.column + 1}}}={value}"),
            ),
            value,
            3,
            "matrix-equation",
        )


class SystemParams(Drawn):
    matrix: IntMatrix
    solution: tuple[int, ...]
    target: int = Field(ge=0, le=3)

    @model_validator(mode="after")
    def unique(self) -> Self:
        size = len(self.matrix)
        _square(self.matrix, size, 12)
        if size not in (2, 3, 4) or len(self.solution) != size or self.target >= size:
            raise ValueError("Systems have 2, 3 or 4 unknowns")
        if any(abs(v) > 4 for v in self.solution) or det(self.matrix) == 0:
            raise ValueError("A system needs a unique, bounded solution")
        return self


def _names(size: int) -> tuple[str, ...]:
    return ("x", "y", "z")[:size] if size < 4 else ("x_1", "x_2", "x_3", "x_4")


class CramerRule:
    version = "algebra-cramer-2x2-v1"
    prefix = "CRA"
    family = "algebra-cramer"
    code_version = 1
    params = SystemParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    size = 2
    difficulty = 1
    step_text = {
        "main": "Calculate the determinant of the coefficient matrix; it is not zero.",
        "replaced": "Replace the unknown's column by the right-hand side and calculate.",
        "ratio": "Divide the two determinants.",
    }

    def draw(self, seed: int) -> SystemParams:
        rng = DeterministicRNG(seed)
        matrix = draw_invertible(rng, self.size, (1, -1, 2, -2))
        solution = tuple(rng.randbelow(9) - 4 for _ in range(self.size))
        return SystemParams(
            seed=seed, matrix=matrix, solution=solution, target=rng.randbelow(self.size)
        )

    def build(self, params: SystemParams) -> Task:
        if len(params.matrix) != self.size:
            raise ValueError("System size belongs to another generator")
        a = to_sympy(params.matrix)
        rhs = a * sp.Matrix(params.solution)
        replaced = a.copy()
        replaced[:, params.target] = rhs
        main, numerator = det(params.matrix), int(replaced.det(method="bareiss"))
        value = sp.Rational(numerator, main)
        if value != params.solution[params.target] or a.LUsolve(rhs) != sp.Matrix(params.solution):
            raise ValueError("Cramer's rule failed verification")
        name = _names(self.size)[params.target]
        system = system_latex(params.matrix, tuple(int(v) for v in rhs), _names(self.size))
        return _task(
            self,
            params,
            f"Use Cramer's rule to find {name} in the system: "
            rf"\({system}\).",
            (
                Step("main", rf"W=\det{pmatrix(params.matrix)}={main}"),
                Step("replaced", rf"W_{{{name}}}=\det{pmatrix(replaced.tolist())}={numerator}"),
                Step(
                    "ratio",
                    rf"{name}=\frac{{W_{{{name}}}}}{{W}}=\frac{{{numerator}}}{{{main}}}={value}",
                ),
            ),
            value,
            self.difficulty,
            f"cramer-{self.size}x{self.size}",
        )


class CramerRule3(CramerRule):
    version = "algebra-cramer-3x3-v1"
    prefix = "CRT"
    family = "algebra-cramer-3x3"
    size = 3
    difficulty = 2


def _augmented(rows: list[list[Fraction]] | IntMatrix) -> str:
    columns = len(rows[0]) - 1
    body = r"\\".join(
        "&".join(
            str(sp.latex(sp.Rational(v.numerator, v.denominator) if isinstance(v, Fraction) else v))
            for v in row
        )
        for row in rows
    )
    return rf"\left(\begin{{array}}{{{'c' * columns}|c}}{body}\end{{array}}\right)"


class GaussianElimination(CramerRule):
    """Algebra30 exercise 31: reduce the augmented matrix to echelon form."""

    version = "algebra-gauss-3x3-v1"
    prefix = "GAU"
    family = "algebra-gauss"
    size = 3
    difficulty = 3
    step_text = {
        "augmented": "Write the augmented matrix of the system.",
        "echelon": "Use row operations to reach row echelon form.",
        "back": "Solve from the last equation upwards.",
    }

    def build(self, params: SystemParams) -> Task:
        if len(params.matrix) != self.size:
            raise ValueError("System size belongs to another generator")
        a = to_sympy(params.matrix)
        rhs = tuple(int(v) for v in a * sp.Matrix(params.solution))
        augmented = tuple(row + (b,) for row, b in zip(params.matrix, rhs, strict=True))
        echelon = row_echelon(fractions(augmented))
        solution = [Fraction(0)] * self.size
        for r in reversed(range(self.size)):
            known = sum(echelon[r][c] * solution[c] for c in range(r + 1, self.size))
            solution[r] = (echelon[r][-1] - known) / echelon[r][r]
        if tuple(solution) != tuple(Fraction(v) for v in params.solution):
            raise ValueError("Gaussian elimination failed verification")
        names = _names(self.size)
        name = names[params.target]
        value = params.solution[params.target]
        listed = ",\\ ".join(f"{n}={v}" for n, v in zip(names, params.solution, strict=True))
        return _task(
            self,
            params,
            f"Use Gaussian elimination to find {name.replace('_', '')} in the system: "
            rf"\({system_latex(params.matrix, rhs, names)}\).",
            (
                Step("augmented", _augmented(augmented)),
                Step("echelon", _augmented(echelon)),
                Step("back", listed),
            ),
            value,
            self.difficulty,
            f"gauss-{self.size}x{self.size}",
        )


class GaussianElimination4(GaussianElimination):
    version = "algebra-gauss-4x4-v1"
    prefix = "GAF"
    family = "algebra-gauss-4x4"
    size = 4
    difficulty = 4

    def draw(self, seed: int) -> SystemParams:
        rng = DeterministicRNG(seed)
        matrix = draw_invertible(rng, 4, (1, -1))
        solution = tuple(rng.randbelow(7) - 3 for _ in range(4))
        return SystemParams(seed=seed, matrix=matrix, solution=solution, target=rng.randbelow(4))


class RankParams(Drawn):
    matrix: IntMatrix
    rank: int = Field(ge=1, le=3)
    solution: tuple[int, int, int, int] | None = None

    @model_validator(mode="after")
    def shape(self) -> Self:
        if len(self.matrix) != 3 or any(len(row) != 4 for row in self.matrix):
            raise ValueError("Rank exercises use a 3 x 4 matrix")
        if not bounded(self.matrix, 12) or not _full_support(self.matrix):
            raise ValueError("Rows and columns must be nonzero and bounded")
        if self.solution is not None and any(abs(v) > 2 for v in self.solution):
            raise ValueError("Particular solution is outside the declared range")
        return self


def _full_support(matrix: IntMatrix) -> bool:
    return all(any(row) for row in matrix) and all(
        any(column) for column in zip(*matrix, strict=True)
    )


def _draw_rank(rng: DeterministicRNG) -> tuple[IntMatrix, int]:
    return draw_valid(lambda: _draw_rank_once(rng), lambda drawn: _full_support(drawn[0]))


def _draw_rank_once(rng: DeterministicRNG) -> tuple[IntMatrix, int]:
    """B (3 x r, unit lower) times C (r x 4, unit upper): rank exactly r, nonzero rows."""
    rank = 1 + rng.randbelow(3)
    left = [
        [
            1
            if i == j
            else ((1, -1, 2, -2)[rng.randbelow(4)] if j == 0 else rng.randbelow(5) - 2)
            if j < i
            else 0
            for j in range(rank)
        ]
        for i in range(3)
    ]
    for i in range(rank, 3):
        if not any(left[i]):
            left[i][0] = 1
    right = [
        [1 if i == j else (rng.randbelow(5) - 2 if j > i else 0) for j in range(4)]
        for i in range(rank)
    ]
    product = sp.Matrix(left) * sp.Matrix(right)
    order = PERMUTATIONS[rng.randbelow(6)]
    return tuple(tuple(int(product[r, c]) for c in range(4)) for r in order), rank


class MatrixRank:
    version = "algebra-rank-v1"
    prefix = "RNK"
    family = "algebra-rank"
    code_version = 1
    params = RankParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    step_text = {
        "echelon": "Use row operations to reach row echelon form.",
        "count": "The rank is the number of nonzero rows.",
    }

    def draw(self, seed: int) -> RankParams:
        rng = DeterministicRNG(seed)
        matrix, rank = _draw_rank(rng)
        return RankParams(seed=seed, matrix=matrix, rank=rank)

    def build(self, params: RankParams) -> Task:
        echelon = row_echelon(fractions(params.matrix))
        if nonzero_rows(echelon) != params.rank or to_sympy(params.matrix).rank() != params.rank:
            raise ValueError("Rank failed verification")
        return _task(
            self,
            params,
            rf"Find the rank of the matrix: \({pmatrix(params.matrix)}\).",
            (
                Step("echelon", pmatrix(echelon)),
                Step("count", rf"\operatorname{{rank}}A={params.rank}"),
            ),
            params.rank,
            1,
            "rank",
        )


class FreeParameters:
    """Algebra30 exercise 29: Kronecker-Capelli without solving the system."""

    version = "algebra-free-parameters-v1"
    prefix = "SYP"
    family = "algebra-consistency"
    code_version = 1
    params = RankParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    step_text = {
        "echelon": "Reduce the augmented matrix to row echelon form.",
        "ranks": "The coefficient and augmented matrices have equal ranks, so solutions exist.",
        "count": "Subtract the rank from the number of unknowns.",
    }

    def draw(self, seed: int) -> RankParams:
        rng = DeterministicRNG(seed)
        matrix, rank = _draw_rank(rng)
        solution = tuple(rng.randbelow(5) - 2 for _ in range(4))
        return RankParams(seed=seed, matrix=matrix, rank=rank, solution=solution)  # type: ignore[arg-type]

    def build(self, params: RankParams) -> Task:
        if params.solution is None:
            raise ValueError("A consistent system needs a particular solution")
        a = to_sympy(params.matrix)
        rhs = tuple(int(v) for v in a * sp.Matrix(params.solution))
        augmented = tuple(row + (b,) for row, b in zip(params.matrix, rhs, strict=True))
        echelon = row_echelon(fractions(augmented))
        rank = nonzero_rows([row[:-1] for row in echelon])
        if rank != params.rank or nonzero_rows(echelon) != rank or a.rank() != rank:
            raise ValueError("Consistency failed verification")
        names = ("x_1", "x_2", "x_3", "x_4")
        return _task(
            self,
            params,
            "Without solving, find the number of free parameters in the general "
            "solution for the unknowns x1, x2, x3, x4: "
            rf"\({system_latex(params.matrix, rhs, names)}\).",
            (
                Step("echelon", _augmented(echelon)),
                Step("ranks", rf"\operatorname{{rank}}A=\operatorname{{rank}}[A|b]={rank}"),
                Step("count", rf"4-{rank}={4 - rank}"),
            ),
            4 - rank,
            2,
            "free-parameters",
        )


class NontrivialParams(Drawn):
    matrix: IntMatrix
    eigenvalues: tuple[int, int]

    @model_validator(mode="after")
    def distinct(self) -> Self:
        _square(self.matrix, 2, 12)
        if self.eigenvalues[0] == self.eigenvalues[1] or not bounded((self.eigenvalues,), 9):
            raise ValueError("Need two distinct bounded parameter values")
        return self


class NontrivialSolutions:
    """Algebra30 exercise 37: values of a parameter giving nonzero solutions."""

    version = "algebra-nontrivial-parameter-v1"
    prefix = "SNT"
    family = "algebra-parameter-system"
    code_version = 1
    params = NontrivialParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    step_text = {
        "homogeneous": "Move every term to the left: a homogeneous system has a nonzero "
        "solution exactly when its determinant is zero.",
        "solve": "Solve the quadratic equation.",
        "largest": "Choose the larger value.",
    }

    def draw(self, seed: int) -> NontrivialParams:
        rng = DeterministicRNG(seed)

        def candidate() -> tuple[IntMatrix, tuple[int, int]]:
            basis = to_sympy(draw_invertible(rng, 2, (1, -1)))
            first = rng.randbelow(9) - 4
            second = rng.randbelow(8) - 4
            second += second >= first
            product = basis * sp.diag(first, second) * basis.inv()
            return tuple(tuple(int(v) for v in product.row(r)) for r in range(2)), (first, second)

        matrix, values = draw_valid(candidate, lambda m: bounded(m[0], 12))
        return NontrivialParams(seed=seed, matrix=matrix, eigenvalues=values)

    def build(self, params: NontrivialParams) -> Task:
        lam = sp.Symbol("lambda")
        (a, b), (c, d) = params.matrix
        characteristic = sp.expand((a - lam) * (d - lam) - b * c)
        roots = sorted(sp.roots(characteristic, lam))
        if roots != sorted(params.eigenvalues):
            raise ValueError("Parameter values failed verification")
        x, y = sp.symbols("x y")
        system = (
            rf"\begin{{cases}}{sp.latex(a * x + b * y)}=\lambda x\\"
            rf"{sp.latex(c * x + d * y)}=\lambda y\end{{cases}}"
        )
        shifted = pmatrix([[sp.latex(a - lam), b], [c, sp.latex(d - lam)]])
        return _task(
            self,
            params,
            "Find the largest value of the parameter for which the system has a "
            "solution other than x = y = 0: "
            rf"\({system}\).",
            (
                Step("homogeneous", rf"\det{shifted}={sp.latex(characteristic)}=0"),
                Step("solve", rf"\lambda_1={roots[0]},\quad \lambda_2={roots[1]}"),
                Step("largest", rf"\lambda={roots[1]}"),
            ),
            roots[1],
            5,
            "nontrivial-parameter",
        )


def generators() -> tuple[TaskGenerator[Any], ...]:
    return (
        Determinant3(),
        Determinant4(),
        DeterminantScaling(),
        DeterminantRowOperations(),
        SingularParameter(),
        InverseEntry(),
        InverseEntry3(),
        MatrixEquation(),
        CramerRule(),
        CramerRule3(),
        GaussianElimination(),
        GaussianElimination4(),
        MatrixRank(),
        FreeParameters(),
        NontrivialSolutions(),
    )
