"""Invertible matrix exercises for the local preview."""

import sympy as sp

from app.engine.blocks.matrices import IntMatrix, pmatrix
from app.engine.codes import encode
from app.engine.generators.matrix_full import MatrixAnswer, matrix_contract
from app.engine.models import Drawn, Step, Task
from local_determinant_generator import determinant_seed
from local_matrix_generator import (
    VARIATIONS,
    LeveledMatrixDivisionGenerator,
    LocalMatrixGenerator,
    inverse_steps,
    make_seed,
)


class InverseParameters(Drawn):
    matrix: IntMatrix
    level: int


class LocalInverseGenerator:
    version = "local-inverse-v1"
    prefix = "LINV"
    family = "local-inverse"
    code_version = 1
    params = InverseParameters
    answer = MatrixAnswer
    requires = ()
    step_text = {
        "check": "The determinant is nonzero, so the matrix is invertible.",
        "augment": "The identity matrix is placed beside A to form the augmented matrix [A | I].",
        "row_swap": "The two rows are exchanged on both sides of the vertical line.",
        "row_scale": "The entire row is divided by its pivot on both sides of the vertical line.",
        "row_eliminate": "The row operation is applied to both sides to eliminate an entry.",
        "inverse": "The left side is the identity matrix; the right side is the inverse of A.",
    }

    def draw(self, seed: int) -> InverseParameters:
        index = seed // VARIATIONS
        if not 0 <= index < 12:
            raise ValueError("Invalid inverse seed")
        level, size = index // 4 + 1, index % 4 + 2
        source_seed = make_seed("divide", level, (size, size, size, size), seed % VARIATIONS)
        source = LocalMatrixGenerator() if level == 1 else LeveledMatrixDivisionGenerator()
        matrix = source.draw(source_seed).second
        return InverseParameters(seed=seed, matrix=matrix, level=level)

    def input_contract(self, params: InverseParameters):
        return matrix_contract(len(params.matrix), len(params.matrix))

    def build(self, params: InverseParameters) -> Task:
        matrix = sp.Matrix(params.matrix)
        determinant = int(matrix.det())
        if determinant == 0:
            raise ValueError("The matrix must be invertible")
        inverse = matrix.inv()
        expected = tuple(
            tuple(inverse[i, j] for j in range(matrix.cols)) for i in range(matrix.rows)
        )
        steps = list(inverse_steps(matrix))
        steps[-1] = Step("inverse", steps[-1].latex.replace("B^{", "A^{"))
        return Task(
            statement=rf"Find the inverse of the matrix: \(A={pmatrix(params.matrix)}\).",
            steps=(Step("check", rf"\det A={determinant}\ne 0"), *steps),
            answer=MatrixAnswer(expected),
            metadata={"difficulty": params.level, "template": "local-inverse"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


inverse_seed = determinant_seed
