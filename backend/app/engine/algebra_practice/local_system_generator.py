"""Locally generated linear systems with a unique solution."""

import sympy as sp

from app.engine.algebra_practice.local_determinant_generator import determinant_seed
from app.engine.algebra_practice.local_inverse_generator import LocalInverseGenerator
from app.engine.answers.computational import FormulaAnswer, OrderedAnswer
from app.engine.blocks.matrices import system_latex
from app.engine.codes import encode
from app.engine.models import Drawn, Step, Task
from app.engine.prng import DeterministicRNG
from app.math_input.contracts import InputContract


class SystemParameters(Drawn):
    matrix: tuple[tuple[int, ...], ...]
    solution: tuple[int, ...]
    level: int


class LocalSystemGenerator:
    version, prefix, family, code_version = "local-system-v1", "LSYS", "local-system", 1
    params, answer, requires = SystemParameters, OrderedAnswer, ()
    step_text = {
        "start": "The coefficients and constants form an augmented matrix.",
        "swap": "The two rows are exchanged to obtain a nonzero pivot.",
        "scale": "The pivot row is divided by its leading entry.",
        "eliminate": "A multiple of the pivot row is subtracted from the selected row.",
        "result": "The final augmented matrix gives the value of each unknown.",
    }

    def draw(self, seed: int) -> SystemParameters:
        inverse = LocalInverseGenerator().draw(seed)
        rng = DeterministicRNG(seed)
        size = len(inverse.matrix)
        solution = tuple(rng.randbelow(7) - 3 for _ in range(size))
        return SystemParameters(
            seed=seed, matrix=inverse.matrix, solution=solution, level=inverse.level
        )

    def input_contract(self, params: SystemParameters) -> InputContract:
        return self._answer(params).contract

    def _answer(self, params: SystemParameters) -> OrderedAnswer:
        return OrderedAnswer(
            tuple(FormulaAnswer(x) for x in params.solution),
            tuple(
                f"Variable {name}"
                for name in ("one", "two", "three", "four", "five")[: len(params.solution)]
            ),
        )

    def build(self, params: SystemParameters) -> Task:
        matrix = sp.Matrix(params.matrix)
        rhs = matrix * sp.Matrix(params.solution)
        reduced = matrix.row_join(rhs)
        n = matrix.rows

        def display() -> str:
            lines = (" & ".join(sp.latex(reduced[i, j]) for j in range(n + 1)) for i in range(n))
            return (
                rf"\left[\begin{{array}}{{{'c' * n}|c}}" + r"\\".join(lines) + r"\end{array}\right]"
            )

        steps = [Step("start", display())]
        for col in range(n):
            pivot = next(i for i in range(col, n) if reduced[i, col] != 0)
            if pivot != col:
                reduced.row_swap(pivot, col)
                steps.append(
                    Step(
                        "swap",
                        rf"R_{{{col + 1}}}\leftrightarrow R_{{{pivot + 1}}}\quad {display()}",
                    )
                )
            value = reduced[col, col]
            if value != 1:
                reduced.row_op(col, lambda entry, _, factor=value: entry / factor)
                steps.append(
                    Step(
                        "scale",
                        rf"R_{{{col + 1}}}\leftarrow R_{{{col + 1}}}/({sp.latex(value)})"
                        rf"\quad {display()}",
                    )
                )
            for row in range(n):
                factor = reduced[row, col]
                if row != col and factor:
                    reduced.row_op(row, lambda entry, j, f=factor, p=col: entry - f * reduced[p, j])
                    steps.append(
                        Step(
                            "eliminate",
                            rf"R_{{{row + 1}}}\leftarrow R_{{{row + 1}}}-"
                            rf"({sp.latex(factor)})R_{{{col + 1}}}\quad {display()}",
                        )
                    )
        if reduced[:, :n] != sp.eye(n) or tuple(reduced[:, n]) != params.solution:
            raise ValueError("System verification failed")
        names = tuple(f"x_{i + 1}" for i in range(n))
        answer = self._answer(params)
        equations = system_latex(params.matrix, tuple(map(int, rhs)), names)
        return Task(
            statement=rf"Solve the system: \({equations}\).",
            steps=(
                *steps,
                Step(
                    "result",
                    r",\quad ".join(
                        rf"{name}={value}"
                        for name, value in zip(names, params.solution, strict=True)
                    ),
                ),
            ),
            answer=answer,
            metadata={"difficulty": params.level, "template": "local-system"},
            code=encode(self.prefix, self.code_version, params.seed),
            generator_version=self.version,
        )


system_seed = determinant_seed
