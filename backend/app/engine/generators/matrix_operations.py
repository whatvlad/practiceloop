"""Matrix sums, transposes and products from algebra30 exercises 8-9 (#221).

Each task asks for one entry of a matrix expression, so the answer is one exact
integer checked by `ExpressionAnswer`.
"""

from typing import Any, Self

import sympy as sp
from pydantic import Field, model_validator

from app.engine.answers.expression import ExpressionAnswer
from app.engine.blocks.matrices import IntMatrix, bounded, draw_entries, pmatrix
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task, TaskGenerator
from app.engine.prng import DeterministicRNG

ORDINALS = ("first", "second", "third")


class OperationParams(Drawn):
    first: IntMatrix
    second: IntMatrix
    scales: tuple[int, int]
    row: int = Field(ge=0, le=2)
    column: int = Field(ge=0, le=2)

    @model_validator(mode="after")
    def valid(self) -> Self:
        if not bounded(self.first, 6) or not bounded(self.second, 6):
            raise ValueError("Matrix entries are outside the declared range")
        if any(abs(s) > 3 or s == 0 for s in self.scales):
            raise ValueError("Scales must be nonzero and at most 3")
        return self


def _shape(matrix: IntMatrix) -> tuple[int, int]:
    return len(matrix), len(matrix[0])


def _entry_task(
    generator: Any,
    params: OperationParams,
    name: str,
    symbol: str,
    given: str,
    result: sp.Matrix,
    steps: tuple[Step, ...],
) -> Task:
    if not (params.row < result.rows and params.column < result.cols):
        raise ValueError("The requested entry is outside the result")
    value = result[params.row, params.column]
    return Task(
        statement=f"Find the entry in the {ORDINALS[params.row]} row and "
        f"{ORDINALS[params.column]} column of {name}: \\({given}\\).",
        steps=(
            *steps,
            Step("entry", rf"({symbol})_{{{params.row + 1}{params.column + 1}}}={value}"),
        ),
        answer=ExpressionAnswer(sp.Integer(value), {}),
        metadata={"difficulty": generator.difficulty, "template": generator.template},
        code=encode(generator.prefix, generator.code_version, params.seed),
        generator_version=generator.version,
    )


class MatrixCombination:
    """Algebra30 8: a combination such as 2A^T - C of a 2 x 3 and a 3 x 2 matrix."""

    version = "matrix-combination-v1"
    prefix = "MCB"
    family = "matrix-combination"
    code_version = 1
    params = OperationParams
    answer = ExpressionAnswer
    requires: tuple[str, ...] = ()
    difficulty = 1
    template = "combination"
    step_text = {
        "transpose": "Transpose A: its rows become columns.",
        "combine": "Multiply by the scalars and add entry by entry.",
        "entry": "Read off the requested entry.",
    }

    def draw(self, seed: int) -> OperationParams:
        rng = DeterministicRNG(seed)
        return OperationParams(
            seed=seed,
            first=draw_entries(rng, 2, 3, 5),
            second=draw_entries(rng, 3, 2, 5),
            scales=tuple((-3, -2, -1, 1, 2, 3)[rng.randbelow(6)] for _ in range(2)),  # type: ignore[arg-type]
            row=rng.randbelow(3),
            column=rng.randbelow(2),
        )

    def build(self, params: OperationParams) -> Task:
        if _shape(params.first) != (2, 3) or _shape(params.second) != (3, 2):
            raise ValueError("A is 2 x 3 and C is 3 x 2")
        a, c = sp.Matrix(params.first), sp.Matrix(params.second)
        p, q = params.scales
        result = p * a.T + q * c
        if any(result[i, j] != p * a[j, i] + q * c[i, j] for i in range(3) for j in range(2)):
            raise ValueError("Matrix combination failed verification")
        expression = f"{_coefficient(p)}A^{{T}}{'+' if q > 0 else '-'}{_coefficient(abs(q))}C"
        return _entry_task(
            self,
            params,
            "the combination",
            expression,
            rf"{expression},\quad A={pmatrix(params.first)},\ C={pmatrix(params.second)}",
            result,
            (
                Step("transpose", rf"A^{{T}}={pmatrix(a.T.tolist())}"),
                Step("combine", rf"{expression}={pmatrix(result.tolist())}"),
            ),
        )


def _coefficient(value: int) -> str:
    return {1: "", -1: "-"}.get(value, str(value))


class MatrixProduct(MatrixCombination):
    """Algebra30 8: AB of a 2 x 3 and a 3 x 2 matrix, row times column."""

    version = "matrix-product-v1"
    prefix = "MPR"
    family = "matrix-product"
    difficulty = 2
    template = "product"
    step_text = {
        "dimensions": "A 2 x 3 matrix times a 3 x 2 matrix is a 2 x 2 matrix.",
        "row_column": "Each entry is the row of A times the column of B.",
        "entry": "Read off the requested entry.",
    }

    def draw(self, seed: int) -> OperationParams:
        rng = DeterministicRNG(seed)
        return OperationParams(
            seed=seed,
            first=draw_entries(rng, 2, 3, 4),
            second=draw_entries(rng, 3, 2, 4),
            scales=(1, 1),
            row=rng.randbelow(2),
            column=rng.randbelow(2),
        )

    def build(self, params: OperationParams) -> Task:
        if _shape(params.first) != (2, 3) or _shape(params.second) != (3, 2):
            raise ValueError("A is 2 x 3 and B is 3 x 2")
        a, b = sp.Matrix(params.first), sp.Matrix(params.second)
        result = a * b
        i, j = params.row, params.column
        terms = "+".join(f"({a[i, k]})({b[k, j]})" for k in range(3))
        if result[i, j] != sum(a[i, k] * b[k, j] for k in range(3)):
            raise ValueError("Matrix product failed verification")
        return _entry_task(
            self,
            params,
            "AB",
            "AB",
            rf"A={pmatrix(params.first)},\ B={pmatrix(params.second)}",
            result,
            (
                Step("dimensions", r"(2\times 3)(3\times 2)=2\times 2"),
                Step("row_column", rf"(AB)_{{{i + 1}{j + 1}}}={terms}"),
            ),
        )


class MatrixCommutator(MatrixCombination):
    """Algebra30 9(a): AB - BA of two 2 x 2 matrices."""

    version = "matrix-commutator-v1"
    prefix = "MCM"
    family = "matrix-commutator"
    difficulty = 3
    template = "commutator"
    step_text = {
        "products": "Calculate both products; matrix multiplication is not commutative.",
        "difference": "Subtract entry by entry.",
        "entry": "Read off the requested entry.",
    }

    def draw(self, seed: int) -> OperationParams:
        rng = DeterministicRNG(seed)
        return OperationParams(
            seed=seed,
            first=draw_entries(rng, 2, 2, 5),
            second=draw_entries(rng, 2, 2, 5),
            scales=(1, 1),
            row=rng.randbelow(2),
            column=rng.randbelow(2),
        )

    def build(self, params: OperationParams) -> Task:
        if _shape(params.first) != (2, 2) or _shape(params.second) != (2, 2):
            raise ValueError("A and B are 2 x 2")
        a, b = sp.Matrix(params.first), sp.Matrix(params.second)
        ab, ba = a * b, b * a
        result = ab - ba
        if result.trace() != 0:
            raise ValueError("A commutator has trace zero")
        return _entry_task(
            self,
            params,
            "AB - BA",
            "AB-BA",
            rf"A={pmatrix(params.first)},\ B={pmatrix(params.second)}",
            result,
            (
                Step("products", rf"AB={pmatrix(ab.tolist())},\quad BA={pmatrix(ba.tolist())}"),
                Step("difference", rf"AB-BA={pmatrix(result.tolist())}"),
            ),
        )


def generators() -> tuple[TaskGenerator[Any], ...]:
    return (MatrixCombination(), MatrixProduct(), MatrixCommutator())
