"""Versioned full-matrix variants of the existing matrix-operation exercises."""

from dataclasses import dataclass, replace
from typing import Any, ClassVar, Self

import sympy as sp
from pydantic import Field, model_validator

from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.blocks.matrices import IntMatrix, bounded, draw_entries, pmatrix
from app.engine.codes import encode
from app.engine.generators.matrix_operations import (
    MatrixCombination,
    MatrixCommutator,
    MatrixProduct,
    OperationParams,
)
from app.engine.models import Drawn, Outcome, Step, Task, TaskGenerator
from app.engine.prng import DeterministicRNG
from app.math_input import MathNode
from app.math_input.contracts import Domain, InputContract

ORDINALS = ("one", "two", "three", "four", "five")


def matrix_contract(
    rows: int, columns: int, symbols: tuple[tuple[str, Domain], ...] = ()
) -> InputContract:
    scalar = InputContract("formula", symbols=symbols)
    row = InputContract(
        "tuple",
        components=(scalar,) * columns,
        labels=tuple(f"Column {name}" for name in ORDINALS[:columns]),
    )
    return InputContract(
        "tuple",
        components=(row,) * rows,
        labels=tuple(f"Matrix row {name}" for name in ORDINALS[:rows]),
    )


@dataclass(frozen=True, slots=True)
class MatrixAnswer:
    expected: tuple[tuple[Any, ...], ...]
    symbols: tuple[tuple[str, Domain], ...] = ()
    kind: ClassVar[str] = "tuple"

    @property
    def contract(self) -> InputContract:
        return matrix_contract(len(self.expected), len(self.expected[0]), self.symbols)

    def latex(self) -> str:
        return pmatrix(self.expected)

    def check(self, tree: MathNode) -> Outcome:
        rows = tuple(
            OrderedAnswer(
                tuple(FormulaAnswer(value, self.symbols) for value in row),
                self.contract.components[i].labels,
            )
            for i, row in enumerate(self.expected)
        )
        return OrderedAnswer(rows, self.contract.labels).check(tree)


class _FullMatrix:
    answer = MatrixAnswer
    code_version = 2
    prefix: str
    version: str
    difficulty: int
    dimensions: tuple[int, int]

    def input_contract(self, _params: OperationParams) -> InputContract:
        return matrix_contract(*self.dimensions)

    def full_task(self, task: Task, result: sp.Matrix, seed: int) -> Task:
        expected = tuple(
            tuple(int(result[row, col]) for col in range(result.cols)) for row in range(result.rows)
        )
        if (result.rows, result.cols) != self.dimensions:
            raise ValueError("Unexpected matrix dimensions")
        return replace(
            task,
            statement="Calculate the full matrix: " + task.statement.split(": ", 1)[1],
            steps=(
                *tuple(step for step in task.steps if step.text_key != "entry"),
                Step("full", pmatrix(expected)),
            ),
            answer=MatrixAnswer(expected),
            metadata={**task.metadata, "difficulty": self.difficulty},
            code=encode(self.prefix, self.code_version, seed),
            generator_version=self.version,
        )


class MatrixSumParams(Drawn):
    first: IntMatrix
    second: IntMatrix
    sign: int

    @model_validator(mode="after")
    def valid(self) -> Self:
        size = len(self.first)
        if size not in (2, 3) or len(self.second) != size or self.sign not in (-1, 1):
            raise ValueError("Expected square matrices and an addition or subtraction")
        if any(len(row) != size for row in (*self.first, *self.second)):
            raise ValueError("Invalid matrix dimensions")
        if not bounded(self.first, 5) or not bounded(self.second, 5):
            raise ValueError("Matrix entries are outside the declared range")
        return self


class FullMatrixSum:
    version = "matrix-sum-v1"
    prefix = "MSU"
    family = "matrix-sum"
    code_version = 1
    params = MatrixSumParams
    answer = MatrixAnswer
    requires: tuple[str, ...] = ()
    step_text = {"sum": "Add or subtract corresponding entries."}

    def draw(self, seed: int) -> MatrixSumParams:
        rng = DeterministicRNG(seed)
        size = 2 + rng.randbelow(2)
        return MatrixSumParams(
            seed=seed,
            first=draw_entries(rng, size, size, 5),
            second=draw_entries(rng, size, size, 5),
            sign=(-1, 1)[rng.randbelow(2)],
        )

    def input_contract(self, params: MatrixSumParams) -> InputContract:
        return matrix_contract(len(params.first), len(params.first))

    def build(self, params: MatrixSumParams) -> Task:
        expected = tuple(
            tuple(a + params.sign * b for a, b in zip(first, second, strict=True))
            for first, second in zip(params.first, params.second, strict=True)
        )
        operation = "+" if params.sign == 1 else "-"
        instruction = "Add" if params.sign == 1 else "Subtract"
        return Task(
            statement=(
                f"{instruction} the matrices: \\({pmatrix(params.first)}"
                f"{operation}{pmatrix(params.second)}\\)."
            ),
            steps=(Step("sum", pmatrix(expected)),),
            answer=MatrixAnswer(expected),
            metadata={"difficulty": 1, "template": "matrix-sum"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class MatrixTrigParams(Drawn):
    first: int = Field(ge=1, le=4)
    second: int = Field(ge=1, le=4)

    @model_validator(mode="after")
    def distinct(self) -> Self:
        if self.first == self.second:
            raise ValueError("Diagonal entries must be distinct")
        return self


class FullMatrixTrig:
    version = "matrix-trig-v1"
    prefix = "MXTRIG"
    family = "matrix-trig"
    code_version = 1
    params = MatrixTrigParams
    answer = MatrixAnswer
    requires: tuple[str, ...] = ()
    symbols: tuple[tuple[str, Domain], ...] = (("theta", "real"),)
    step_text = {
        "transpose": "Transpose the rotation matrix.",
        "product": "Multiply the matrices and simplify each entry.",
    }

    def draw(self, seed: int) -> MatrixTrigParams:
        rng = DeterministicRNG(seed)
        first = 1 + rng.randbelow(4)
        second = (first + rng.randbelow(3)) % 4 + 1
        return MatrixTrigParams(seed=seed, first=first, second=second)

    def input_contract(self, _params: MatrixTrigParams) -> InputContract:
        return matrix_contract(2, 2, self.symbols)

    def build(self, params: MatrixTrigParams) -> Task:
        theta = sp.Symbol("theta", real=True)
        c, s = sp.cos(theta), sp.sin(theta)
        rotation = sp.Matrix([[c, -s], [s, c]])
        diagonal = sp.diag(params.first, params.second)
        result = rotation * diagonal * rotation.T
        expected = tuple(tuple(result[i, j] for j in range(2)) for i in range(2))
        return Task(
            statement=(
                "Calculate the full matrix: "
                rf"\(RDR^{{T}},\quad R={pmatrix(rotation.tolist())},\ "
                rf"D={pmatrix(diagonal.tolist())}\)."
            ),
            steps=(
                Step("transpose", rf"R^{{T}}={pmatrix(rotation.T.tolist())}"),
                Step("product", rf"RDR^{{T}}={pmatrix(expected)}"),
            ),
            answer=MatrixAnswer(expected, self.symbols),
            metadata={"difficulty": 3, "template": "matrix-trigonometric"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class FullMatrixCombination(_FullMatrix):
    version = "matrix-combination-v2"
    dimensions = (3, 2)
    prefix, family, params = MatrixCombination.prefix, MatrixCombination.family, OperationParams
    requires = MatrixCombination.requires
    difficulty, template = 2, MatrixCombination.template
    step_text = {**MatrixCombination.step_text, "full": "Write the full resulting matrix."}

    def draw(self, seed: int) -> OperationParams:
        return MatrixCombination().draw(seed)

    def build(self, params: OperationParams) -> Task:
        first, second = sp.Matrix(params.first), sp.Matrix(params.second)
        return self.full_task(
            MatrixCombination().build(params),
            params.scales[0] * first.T + params.scales[1] * second,
            params.seed,
        )


class FullMatrixProduct(_FullMatrix):
    version = "matrix-product-v2"
    dimensions = (2, 2)
    prefix, family, params = MatrixProduct.prefix, MatrixProduct.family, OperationParams
    requires = MatrixProduct.requires
    difficulty, template = MatrixProduct.difficulty, MatrixProduct.template
    step_text = {**MatrixProduct.step_text, "full": "Write the full resulting matrix."}

    def draw(self, seed: int) -> OperationParams:
        return MatrixProduct().draw(seed)

    def build(self, params: OperationParams) -> Task:
        return self.full_task(
            MatrixProduct().build(params),
            sp.Matrix(params.first) * sp.Matrix(params.second),
            params.seed,
        )


class FullMatrixCommutator(_FullMatrix):
    version = "matrix-commutator-v2"
    dimensions = (2, 2)
    prefix, family, params = MatrixCommutator.prefix, MatrixCommutator.family, OperationParams
    requires = MatrixCommutator.requires
    difficulty, template = MatrixCommutator.difficulty, MatrixCommutator.template
    step_text = {**MatrixCommutator.step_text, "full": "Write the full resulting matrix."}

    def draw(self, seed: int) -> OperationParams:
        return MatrixCommutator().draw(seed)

    def build(self, params: OperationParams) -> Task:
        first, second = sp.Matrix(params.first), sp.Matrix(params.second)
        return self.full_task(
            MatrixCommutator().build(params), first * second - second * first, params.seed
        )


def _expanded_product(first: sp.Matrix, second: sp.Matrix) -> str:
    """Show every dot product, preserving signs and multiplication order."""
    entries = tuple(
        tuple(
            "+".join(
                rf"({sp.latex(first[i, k])})\cdot({sp.latex(second[k, j])})"
                for k in range(first.cols)
            )
            for j in range(second.cols)
        )
        for i in range(first.rows)
    )
    return pmatrix(entries)


class MatrixMultiplyParams(Drawn):
    first: IntMatrix
    second: IntMatrix

    @model_validator(mode="after")
    def valid(self) -> Self:
        shape = (
            (len(self.first), len(self.first[0]), len(self.second[0]))
            if self.first and self.second and self.first[0] and self.second[0]
            else None
        )
        if shape not in {(2, 2, 2), (3, 3, 3), (2, 3, 2)}:
            raise ValueError("Unsupported multiplication dimensions")
        rows, inner, columns = shape
        if (
            len(self.second) != inner
            or any(len(row) != inner for row in self.first)
            or any(len(row) != columns for row in self.second)
        ):
            raise ValueError("Incompatible matrices")
        if not bounded(self.first, 5) or not bounded(self.second, 5):
            raise ValueError("Matrix entries are outside the declared range")
        return self


class FullMatrixMultiply:
    version = "matrix-multiply-v1"
    prefix = "MXMUL"
    family = "matrix-multiply"
    code_version = 1
    params = MatrixMultiplyParams
    answer = MatrixAnswer
    requires: tuple[str, ...] = ()
    step_text = {
        "dimensions": "Check that the dimensions are compatible.",
        "expand": "Multiply each row of A by each column of B.",
        "full": "Calculate the resulting matrix.",
    }

    def draw(self, seed: int) -> MatrixMultiplyParams:
        rng = DeterministicRNG(seed)
        rows, inner, columns = ((2, 2, 2), (3, 3, 3), (2, 3, 2))[rng.randbelow(3)]
        return MatrixMultiplyParams(
            seed=seed,
            first=draw_entries(rng, rows, inner, 4),
            second=draw_entries(rng, inner, columns, 4),
        )

    def input_contract(self, params: MatrixMultiplyParams) -> InputContract:
        return matrix_contract(len(params.first), len(params.second[0]))

    def build(self, params: MatrixMultiplyParams) -> Task:
        first, second = sp.Matrix(params.first), sp.Matrix(params.second)
        product = first * second
        expected = tuple(
            tuple(int(product[i, j]) for j in range(product.cols)) for i in range(product.rows)
        )
        return Task(
            statement=(
                f"Multiply the matrices: \\({pmatrix(params.first)}{pmatrix(params.second)}\\)."
            ),
            steps=(
                Step(
                    "dimensions",
                    rf"({first.rows}\times {first.cols})({second.rows}\times {second.cols})"
                    rf"={first.rows}\times {second.cols}",
                ),
                Step("expand", _expanded_product(first, second)),
                Step("full", pmatrix(expected)),
            ),
            answer=MatrixAnswer(expected),
            metadata={"difficulty": 1, "template": "matrix-multiply"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class DetailedMatrixSum(FullMatrixSum):
    version = "matrix-sum-v2"
    code_version = 2
    step_text = {
        "expand": "Add or subtract corresponding entries.",
        "sum": "Calculate the resulting matrix.",
    }

    def build(self, params: MatrixSumParams) -> Task:
        task = super().build(params)
        operation = "+" if params.sign == 1 else "-"
        expanded = tuple(
            tuple(f"({a}){operation}({b})" for a, b in zip(first, second, strict=True))
            for first, second in zip(params.first, params.second, strict=True)
        )
        return replace(
            task, steps=(Step("expand", pmatrix(expanded)), Step("sum", task.answer.latex()))
        )


class DetailedMatrixCombination(FullMatrixCombination):
    version = "matrix-combination-v3"
    code_version = 3
    step_text = {
        "transpose": "Transpose A by exchanging rows and columns.",
        "expand": "Multiply by the scalars and combine corresponding entries.",
        "full": "Calculate the resulting matrix.",
    }

    def build(self, params: OperationParams) -> Task:
        task = super().build(params)
        first, second = sp.Matrix(params.first).T, sp.Matrix(params.second)
        p, q = params.scales
        expanded = tuple(
            tuple(
                rf"({p})\cdot({first[i, j]})+({q})\cdot({second[i, j]})" for j in range(first.cols)
            )
            for i in range(first.rows)
        )
        return replace(
            task,
            steps=(
                Step("transpose", rf"A^{{T}}={pmatrix(first.tolist())}"),
                Step("expand", pmatrix(expanded)),
                Step("full", task.answer.latex()),
            ),
        )


class DetailedMatrixProduct(FullMatrixProduct):
    version = "matrix-product-v3"
    code_version = 3
    step_text = {
        "dimensions": "Check that the matrix dimensions are compatible.",
        "expand": "Multiply each row of A by each column of B.",
        "full": "Calculate the resulting matrix.",
    }

    def build(self, params: OperationParams) -> Task:
        task = super().build(params)
        first, second = sp.Matrix(params.first), sp.Matrix(params.second)
        return replace(
            task,
            steps=(
                Step("dimensions", r"(2\times 3)(3\times 2)=2\times 2"),
                Step("expand", rf"AB={_expanded_product(first, second)}"),
                Step("full", rf"AB={task.answer.latex()}"),
            ),
        )


class DetailedMatrixCommutator(FullMatrixCommutator):
    version = "matrix-commutator-v3"
    code_version = 3
    step_text = {
        "expand": "Calculate each entry using a row and a column.",
        "subtract": "Subtract corresponding entries of the two products.",
        "full": "Calculate the resulting matrix.",
    }

    def build(self, params: OperationParams) -> Task:
        task = super().build(params)
        first, second = sp.Matrix(params.first), sp.Matrix(params.second)
        ab, ba = first * second, second * first
        difference = tuple(tuple(f"({ab[i, j]})-({ba[i, j]})" for j in range(2)) for i in range(2))
        return replace(
            task,
            steps=(
                Step("expand", rf"AB={_expanded_product(first, second)}={pmatrix(ab.tolist())}"),
                Step("expand", rf"BA={_expanded_product(second, first)}={pmatrix(ba.tolist())}"),
                Step("subtract", rf"AB-BA={pmatrix(difference)}"),
                Step("full", rf"AB-BA={task.answer.latex()}"),
            ),
        )


class DetailedMatrixTrig(FullMatrixTrig):
    version = "matrix-trig-v2"
    code_version = 2
    step_text = {
        "transpose": "Transpose the rotation matrix.",
        "first_product": "Multiply the rotation matrix by D.",
        "expand": "Multiply each row of RD by each column of the transpose.",
        "product": "Calculate the resulting matrix.",
    }

    def build(self, params: MatrixTrigParams) -> Task:
        task = super().build(params)
        theta = sp.Symbol("theta", real=True)
        c, s = sp.cos(theta), sp.sin(theta)
        rotation = sp.Matrix([[c, -s], [s, c]])
        product = rotation * sp.diag(params.first, params.second)
        return replace(
            task,
            steps=(
                Step("transpose", rf"R^{{T}}={pmatrix(rotation.T.tolist())}"),
                Step("first_product", rf"RD={pmatrix(product.tolist())}"),
                Step("expand", rf"RDR^{{T}}={_expanded_product(product, rotation.T)}"),
                Step("product", rf"RDR^{{T}}={task.answer.latex()}"),
            ),
        )


def detailed_generators() -> tuple[TaskGenerator[Any], ...]:
    return (
        DetailedMatrixSum(),
        DetailedMatrixCombination(),
        DetailedMatrixProduct(),
        DetailedMatrixCommutator(),
        DetailedMatrixTrig(),
    )


def generators() -> tuple[TaskGenerator[Any], ...]:
    return (
        FullMatrixSum(),
        FullMatrixCombination(),
        FullMatrixProduct(),
        FullMatrixCommutator(),
        FullMatrixTrig(),
        FullMatrixMultiply(),
        *detailed_generators(),
    )
