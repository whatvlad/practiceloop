"""Configurable generator used by the isolated local preview."""

from typing import Literal

import sympy as sp
from pydantic import Field

from app.engine.blocks.matrices import IntMatrix, draw_entries, pmatrix
from app.engine.codes import encode
from app.engine.generators.matrix_full import MatrixAnswer, _expanded_product, matrix_contract
from app.engine.models import Drawn, Step, Task
from app.engine.prng import DeterministicRNG

OPERATIONS = ("add", "subtract", "multiply", "divide")
VARIATIONS = 10**12


def inverse_steps(matrix: sp.Matrix) -> tuple[Step, ...]:
    """Show each elementary row operation on [B | I] with exact arithmetic."""
    n = matrix.rows
    augmented = matrix.row_join(sp.eye(n))

    def display() -> str:
        columns = "c" * n + "|" + "c" * n
        rows = (" & ".join(sp.latex(augmented[i, j]) for j in range(2 * n)) for i in range(n))
        return rf"\left[\begin{{array}}{{{columns}}}" + r"\\".join(rows) + r"\end{array}\right]"

    steps = [Step("augment", display())]
    for col in range(n):
        pivot = next(row for row in range(col, n) if augmented[row, col] != 0)
        if pivot != col:
            augmented.row_swap(pivot, col)
            steps.append(
                Step(
                    "row_swap",
                    rf"R_{{{col + 1}}}\leftrightarrow R_{{{pivot + 1}}}\quad {display()}",
                )
            )
        scale = augmented[col, col]
        if scale != 1:
            augmented.row_op(col, lambda value, _, divisor=scale: value / divisor)
            steps.append(
                Step(
                    "row_scale",
                    rf"R_{{{col + 1}}}\leftarrow \frac{{R_{{{col + 1}}}}}{{{sp.latex(scale)}}}"
                    rf"\quad {display()}",
                )
            )
        for row in range(n):
            factor = augmented[row, col]
            if row == col or factor == 0:
                continue
            augmented.row_op(row, lambda value, j, f=factor, c=col: value - f * augmented[c, j])
            steps.append(
                Step(
                    "row_eliminate",
                    rf"R_{{{row + 1}}}\leftarrow R_{{{row + 1}}}-({sp.latex(factor)})"
                    rf"R_{{{col + 1}}}\quad {display()}",
                )
            )
    if augmented[:, :n] != sp.eye(n) or augmented[:, n:] != matrix.inv():
        raise ValueError("Failed to construct inverse")
    steps.append(Step("inverse", rf"B^{{-1}}={pmatrix(augmented[:, n:].tolist())}"))
    return tuple(steps)


class Dimensions(Drawn):
    operation: Literal["add", "subtract", "multiply", "divide"]
    level: int = Field(ge=1, le=3)
    rowsA: int = Field(ge=1, le=5)
    colsA: int = Field(ge=1, le=5)
    rowsB: int = Field(ge=1, le=5)
    colsB: int = Field(ge=1, le=5)
    first: IntMatrix
    second: IntMatrix


def make_seed(
    operation: str, level: int, dimensions: tuple[int, int, int, int], variation: int
) -> int:
    a, b, c, d = dimensions
    if (
        operation not in OPERATIONS
        or level not in (1, 2, 3)
        or any(not 1 <= x <= 5 for x in dimensions)
    ):
        raise ValueError("Invalid matrix settings")
    if (
        (operation in ("multiply", "divide") and b != c)
        or (operation == "divide" and c != d)
        or (operation in ("add", "subtract") and (a, b) != (c, d))
    ):
        raise ValueError("Incompatible matrix dimensions")
    if not 0 <= variation < VARIATIONS:
        raise ValueError("Invalid variation")
    index = OPERATIONS.index(operation) * 3 + level - 1
    for dimension in dimensions:
        index = index * 5 + dimension - 1
    return index * VARIATIONS + variation


class LocalMatrixGenerator:
    version = "local-matrix-sized-v1"
    prefix = "MXSIZE"
    family = "local-matrix-sized"
    code_version = 1
    params = Dimensions
    answer = MatrixAnswer
    requires = ()
    step_text = {
        "dimensions": "Check that the matrix dimensions are compatible.",
        "expand": "Calculate each entry from the corresponding entries or row and column.",
        "inverse": "Find the inverse of B. Its determinant is nonzero.",
        "augment": "Write B next to the identity and reduce B using row operations.",
        "row_swap": "Swap the two rows on both sides of the vertical line.",
        "row_scale": "Divide the entire row on both sides by its pivot.",
        "row_eliminate": "Apply the shown row operation on both sides to eliminate the entry.",
        "rewrite": "Replace division by B with multiplication by its inverse on the right.",
        "result": "Calculate the resulting matrix.",
    }

    def draw(self, seed: int) -> Dimensions:
        index = seed // VARIATIONS
        dims = []
        for _ in range(4):
            dims.append(index % 5 + 1)
            index //= 5
        dims.reverse()
        if index >= len(OPERATIONS) * 3:
            raise ValueError("Invalid matrix seed")
        operation, level = OPERATIONS[index // 3], index % 3 + 1
        make_seed(operation, level, tuple(dims), seed % VARIATIONS)
        a, b, c, d = dims
        rng = DeterministicRNG(seed)
        bound = (2, 4, 8)[level - 1]
        first = draw_entries(rng, a, b, bound)
        second = draw_entries(rng, c, d, min(bound, 2) if operation == "divide" else bound)
        if operation == "divide":
            # Unit triangular matrices are always invertible, without retry loops.
            second = tuple(
                tuple(
                    0 if i > j else (1 if second[i][j] >= 0 else -1) if i == j else second[i][j]
                    for j in range(d)
                )
                for i in range(c)
            )
        return Dimensions(
            seed=seed,
            operation=operation,
            level=level,
            rowsA=a,
            colsA=b,
            rowsB=c,
            colsB=d,
            first=first,
            second=second,
        )

    def input_contract(self, params: Dimensions):
        return matrix_contract(params.rowsA, params.colsB)

    def build(self, params: Dimensions) -> Task:
        first, second = sp.Matrix(params.first), sp.Matrix(params.second)
        if params.operation in ("multiply", "divide"):
            multiplier = second.inv() if params.operation == "divide" else second
            result = first * multiplier
            expanded = _expanded_product(first, multiplier)
            symbol, instruction = r"\cdot", "Divide" if params.operation == "divide" else "Multiply"
        else:
            sign = 1 if params.operation == "add" else -1
            result = first + sign * second
            symbol, instruction = ("+", "Add") if sign == 1 else ("-", "Subtract")
            expanded = pmatrix(
                tuple(
                    tuple(f"({first[i, j]}){symbol}({second[i, j]})" for j in range(first.cols))
                    for i in range(first.rows)
                )
            )
        expected = tuple(
            tuple(int(result[i, j]) for j in range(result.cols)) for i in range(result.rows)
        )
        inverse_step = (
            (
                *inverse_steps(second),
                Step(
                    "rewrite",
                    rf"A:B=A\cdot B^{{-1}}={pmatrix(params.first)}"
                    rf"\cdot{pmatrix(multiplier.tolist())}",
                ),
            )
            if params.operation == "divide"
            else ()
        )
        if params.operation == "divide":
            symbol = ":"
        return Task(
            statement=(
                f"{instruction} the matrices: \\("
                f"{pmatrix(params.first)}{symbol}{pmatrix(params.second)}\\)."
            ),
            steps=(
                Step(
                    "dimensions",
                    rf"A: {first.rows}\times {first.cols},\quad "
                    rf"B: {second.rows}\times {second.cols}",
                ),
                *inverse_step,
                Step("expand", expanded),
                Step("result", pmatrix(expected)),
            ),
            answer=MatrixAnswer(expected),
            metadata={"difficulty": params.level, "template": "local-matrix-sized"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class LocalMatrixDivisionGenerator(LocalMatrixGenerator):
    """Division with varied invertible matrices; preserve older preview codes."""

    version = "local-matrix-division-v2"
    prefix = "MXDIV"
    family = "local-matrix-division"

    def draw(self, seed: int) -> Dimensions:
        params = super().draw(seed)
        if params.operation != "divide":
            raise ValueError("Expected division settings")
        size = params.rowsB
        rng = DeterministicRNG(seed)
        first = draw_entries(rng, params.rowsA, params.colsA, (2, 3, 4)[params.level - 1])
        lower = sp.eye(size)
        upper = sp.eye(size)
        for i in range(size):
            for j in range(size):
                if i > j:
                    lower[i, j] = rng.randbelow(3) - 1
                elif i < j:
                    upper[i, j] = rng.randbelow(3) - 1
        if size > 1:
            lower[1, 0] = 1 if rng.randbelow(2) else -1
        matrix = lower * upper
        second = tuple(tuple(int(matrix[i, j]) for j in range(size)) for i in range(size))
        return params.model_copy(update={"first": first, "second": second})


class LeveledMatrixDivisionGenerator(LocalMatrixDivisionGenerator):
    """Use denser invertible matrices at the advanced level."""

    version = "local-matrix-division-v3"
    code_version = 2

    def draw(self, seed: int) -> Dimensions:
        params = super().draw(seed)
        if params.level != 3:
            return params
        size = params.rowsB
        rng = DeterministicRNG(seed)
        lower, upper = sp.eye(size), sp.eye(size)
        for i in range(size):
            for j in range(size):
                if i > j:
                    lower[i, j] = 1 if rng.randbelow(2) else -1
                elif i < j:
                    upper[i, j] = 1 if rng.randbelow(2) else -1
        matrix = lower * upper
        second = tuple(tuple(int(matrix[i, j]) for j in range(size)) for i in range(size))
        return params.model_copy(update={"second": second})
