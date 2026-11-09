"""Bounded determinant exercises for the local preview."""

import sympy as sp

from app.engine.answers.computational import FormulaAnswer
from app.engine.blocks.matrices import IntMatrix, draw_entries, minor, pmatrix
from app.engine.codes import encode
from app.engine.generators.linear_algebra import _laplace
from app.engine.models import Drawn, Step, Task
from app.engine.prng import DeterministicRNG
from app.math_input.contracts import InputContract

VARIATIONS = 10**12


def determinant_seed(level: int, size: int, variation: int) -> int:
    if level not in (1, 2, 3) or size not in (2, 3, 4, 5) or not 0 <= variation < VARIATIONS:
        raise ValueError("Invalid determinant settings")
    return ((level - 1) * 4 + size - 2) * VARIATIONS + variation


class DeterminantParameters(Drawn):
    matrix: IntMatrix
    level: int


class LocalDeterminantGenerator:
    version = "local-determinant-v1"
    prefix = "LDET"
    family = "local-determinant"
    code_version = 1
    params = DeterminantParameters
    answer = FormulaAnswer
    requires = ()
    step_text = {
        "expand2": "Multiply the entries on each diagonal, then subtract the second product.",
        "laplace": "Expand along the indicated row. Cofactor signs alternate by row and column.",
        "minors": "Evaluate each smaller determinant and include its cofactor sign.",
        "result": "Add the terms to obtain the determinant.",
    }

    def draw(self, seed: int) -> DeterminantParameters:
        index = seed // VARIATIONS
        if not 0 <= index < 12:
            raise ValueError("Invalid determinant seed")
        level, size = index // 4 + 1, index % 4 + 2
        rng = DeterministicRNG(seed)
        matrix = draw_entries(rng, size, size, (2, 3, 4)[level - 1])
        return DeterminantParameters(seed=seed, matrix=matrix, level=level)

    def input_contract(self, _params: DeterminantParameters) -> InputContract:
        return InputContract("formula")

    def build(self, params: DeterminantParameters) -> Task:
        matrix = params.matrix
        size = len(matrix)
        result = int(sp.Matrix(matrix).det())
        if size == 2:
            a, b = matrix[0]
            c, d = matrix[1]
            steps = (
                Step("expand2", rf"\det A=({a})\cdot({d})-({b})\cdot({c})"),
                Step("minors", rf"\det A=({a * d})-({b * c})"),
            )
        else:
            row = max(range(size), key=lambda i: (matrix[i].count(0), -i))
            symbolic, numeric, total = _laplace(matrix, row)
            if total != result:
                raise ValueError("Determinant expansion failed verification")
            steps = (
                Step("laplace", rf"\text{{Row {row + 1}:}}\quad \det A={symbolic or '0'}"),
                Step("minors", rf"\det A={numeric or '0'}"),
            )
        return Task(
            statement=rf"Calculate the determinant: \(\det{pmatrix(matrix)}\).",
            steps=(*steps, Step("result", rf"\det A={result}")),
            answer=FormulaAnswer(result),
            metadata={"difficulty": params.level, "template": "local-determinant"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


class DetailedDeterminantGenerator(LocalDeterminantGenerator):
    """Expand larger determinants until every nonzero minor is 3×3."""

    version = "local-determinant-v2"
    code_version = 2
    color_groups = False
    step_text = {
        **LocalDeterminantGenerator.step_text,
        "sarrus": "Add the downward diagonal products and subtract the upward products.",
        "evaluate": "Multiply the entries on each diagonal and combine the products.",
    }

    def build(self, params: DeterminantParameters) -> Task:
        task = super().build(params)

        def colored(value: str, positive: bool) -> str:
            if not self.color_groups:
                return value
            color = "#f17baa" if positive else "#759bff"
            return rf"\color{{{color}}}{{{value}}}"

        def expand(matrix: IntMatrix) -> tuple[Step, ...]:
            size = len(matrix)
            result = int(sp.Matrix(matrix).det())
            determinant = rf"\det{pmatrix(matrix)}"
            if size == 2:
                a, b = matrix[0]
                c, d = matrix[1]
                positive = colored(rf"({a})\cdot({d})", True)
                negative = colored(rf"({b})\cdot({c})", False)
                positive_value = colored(f"({a * d})", True)
                negative_value = colored(f"({b * c})", False)
                return (
                    Step("expand2", rf"{determinant}={positive}-{negative}"),
                    Step("evaluate", rf"{positive_value}-{negative_value}={result}"),
                )
            if size == 3:
                mat = matrix
                positive_terms = (
                    (mat[0][0], mat[1][1], mat[2][2]),
                    (mat[0][1], mat[1][2], mat[2][0]),
                    (mat[0][2], mat[1][0], mat[2][1]),
                )
                negative_terms = (
                    (mat[0][2], mat[1][1], mat[2][0]),
                    (mat[0][0], mat[1][2], mat[2][1]),
                    (mat[0][1], mat[1][0], mat[2][2]),
                )

                def product(items: tuple[int, ...]) -> str:
                    return r"\cdot".join(f"({item})" for item in items)

                def products(items: tuple[tuple[int, ...], ...]) -> str:
                    return "+".join(product(item) for item in items)

                def evaluated(items: tuple[tuple[int, ...], ...]) -> str:
                    return "+".join(f"({a * b * c})" for a, b, c in items)

                positives = colored(rf"\bigl({products(positive_terms)}\bigr)", True)
                negatives = colored(rf"\bigl({products(negative_terms)}\bigr)", False)
                positive_values = colored(rf"\bigl({evaluated(positive_terms)}\bigr)", True)
                negative_values = colored(rf"\bigl({evaluated(negative_terms)}\bigr)", False)
                return (
                    Step("sarrus", rf"{determinant}={positives}-{negatives}"),
                    Step("evaluate", rf"{positive_values}-{negative_values}={result}"),
                )
            row = max(range(size), key=lambda i: (matrix[i].count(0), -i))
            symbolic, numeric, total = _laplace(matrix, row)
            if total != result:
                raise ValueError("Determinant expansion failed verification")
            steps = [
                Step("laplace", rf"\text{{Row {row + 1}:}}\quad {determinant}={symbolic or '0'}")
            ]
            for col, entry in enumerate(matrix[row]):
                if entry:
                    steps.extend(expand(minor(matrix, row, col)))
            steps.append(Step("minors", rf"{determinant}={numeric or '0'}={result}"))
            return tuple(steps)

        from dataclasses import replace

        return replace(
            task, steps=(*expand(params.matrix), Step("result", rf"\det A={task.answer.latex()}"))
        )


class ColoredDeterminantGenerator(DetailedDeterminantGenerator):
    version = "local-determinant-v3"
    code_version = 3
    color_groups = True


class ExplainedDeterminantGenerator(ColoredDeterminantGenerator):
    version = "local-determinant-v4"
    code_version = 4
    step_text = {
        **ColoredDeterminantGenerator.step_text,
        "cofactor": "The top-left sign is positive. Signs alternate across rows and columns.",
        "expand2": "The determinant is the main diagonal product minus the other diagonal product.",
        "sarrus": (
            "The first two columns are repeated. The downward diagonal products are added, "
            "and the upward diagonal products are subtracted."
        ),
        "evaluate": "The diagonal products are calculated and combined with their signs.",
        "laplace": "The determinant is expanded along the selected row using the cofactor signs.",
        "minors": "The minor values are substituted, their signs applied, and the terms added.",
        "result": "Simplifying the expression gives the value of the determinant.",
    }

    def build(self, params: DeterminantParameters) -> Task:
        from dataclasses import replace

        task = super().build(params)
        size = len(params.matrix)
        signs = tuple(
            tuple(
                r"\color{#65df91}{+}" if (i + j) % 2 == 0 else r"\color{#ff829d}{-}"
                for j in range(size)
            )
            for i in range(size)
        )
        rule = Step("cofactor", rf"(-1)^{{i+j}}:\quad {pmatrix(signs)}")
        return replace(task, steps=(rule, *task.steps))
