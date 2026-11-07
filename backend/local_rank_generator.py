"""Matrix rank exercises for the isolated local preview."""

import sympy as sp

from app.engine.answers.computational import FormulaAnswer
from app.engine.blocks.matrices import IntMatrix, draw_entries, pmatrix
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task
from app.engine.prng import DeterministicRNG
from app.math_input.contracts import InputContract

VARIATIONS = 10**12


def rank_seed(level: int, rows: int, columns: int, variation: int) -> int:
    if (
        level not in (1, 2, 3)
        or rows not in (2, 3, 4, 5)
        or columns not in (2, 3, 4, 5)
        or not 0 <= variation < VARIATIONS
    ):
        raise ValueError("Invalid rank settings")
    return ((level - 1) * 16 + (rows - 2) * 4 + columns - 2) * VARIATIONS + variation


class RankParameters(Drawn):
    matrix: IntMatrix
    level: int


class LocalRankGenerator:
    version = "local-rank-v1"
    prefix = "LRANK"
    family = "local-rank"
    code_version = 1
    params = RankParameters
    answer = FormulaAnswer
    requires = ()
    step_text = {
        "start": "Elementary row operations preserve the rank of a matrix.",
        "swap": "The two rows are exchanged to obtain a nonzero pivot.",
        "scale": "The pivot row is divided by its leading entry.",
        "eliminate": "A multiple of the pivot row is subtracted to eliminate an entry below it.",
        "count": "The rank equals the number of nonzero rows in row echelon form.",
    }

    def draw(self, seed: int) -> RankParameters:
        index = seed // VARIATIONS
        if not 0 <= index < 48:
            raise ValueError("Invalid rank seed")
        level, shape = index // 16 + 1, index % 16
        rows, columns = shape // 4 + 2, shape % 4 + 2
        rng = DeterministicRNG(seed)
        rank = rng.randbelow(min(rows, columns) + 1)
        if rank == 0:
            matrix = tuple((0,) * columns for _ in range(rows))
        else:
            bound = (1, 2, 3)[level - 1]
            left = sp.Matrix(draw_entries(rng, rows, rank, bound))
            right = sp.Matrix(draw_entries(rng, rank, columns, bound))
            product = left * right
            matrix = tuple(tuple(int(product[i, j]) for j in range(columns)) for i in range(rows))
        return RankParameters(seed=seed, matrix=matrix, level=level)

    def input_contract(self, _params: RankParameters) -> InputContract:
        return InputContract("formula")

    def build(self, params: RankParameters) -> Task:
        matrix = sp.Matrix(params.matrix)
        reduced = matrix.copy()

        def display() -> str:
            rows = (
                " & ".join(sp.latex(reduced[i, j]) for j in range(reduced.cols))
                for i in range(reduced.rows)
            )
            return (
                rf"\left[\begin{{array}}{{{'c' * reduced.cols}}}"
                + r"\\".join(rows)
                + r"\end{array}\right]"
            )

        steps = [Step("start", display())]
        pivot_row = 0
        for col in range(matrix.cols):
            pivot = next((r for r in range(pivot_row, matrix.rows) if reduced[r, col] != 0), None)
            if pivot is None:
                continue
            if pivot != pivot_row:
                reduced.row_swap(pivot, pivot_row)
                steps.append(
                    Step(
                        "swap",
                        rf"R_{{{pivot_row + 1}}}\leftrightarrow R_{{{pivot + 1}}}\quad {display()}",
                    )
                )
            value = reduced[pivot_row, col]
            if value != 1:
                reduced.row_op(pivot_row, lambda entry, _, factor=value: entry / factor)
                steps.append(
                    Step(
                        "scale",
                        rf"R_{{{pivot_row + 1}}}\leftarrow "
                        rf"R_{{{pivot_row + 1}}}/({sp.latex(value)})"
                        rf"\quad {display()}",
                    )
                )
            for r in range(pivot_row + 1, matrix.rows):
                factor = reduced[r, col]
                if factor:
                    reduced.row_op(
                        r, lambda entry, j, f=factor, p=pivot_row: entry - f * reduced[p, j]
                    )
                    steps.append(
                        Step(
                            "eliminate",
                            rf"R_{{{r + 1}}}\leftarrow R_{{{r + 1}}}-({sp.latex(factor)})"
                            rf"R_{{{pivot_row + 1}}}\quad {display()}",
                        )
                    )
            pivot_row += 1
            if pivot_row == matrix.rows:
                break
        if pivot_row != matrix.rank():
            raise ValueError("Rank verification failed")
        return Task(
            statement=rf"Find the rank of the matrix: \({pmatrix(params.matrix)}\).",
            steps=(*steps, Step("count", rf"\operatorname{{rank}} A={pivot_row}")),
            answer=FormulaAnswer(pivot_row),
            metadata={"difficulty": params.level, "template": "local-rank"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )
