"""Exact integer matrices for algebra30 linear-algebra exercises (#221).

Every matrix here is drawn from bounded primitive integers. Invertible matrices
are built as a row permutation of a unit lower-triangular factor times an upper
triangular factor with a nonzero diagonal, so no draw needs to be rejected.
"""

from __future__ import annotations

from collections.abc import Sequence
from fractions import Fraction
from itertools import permutations

import sympy as sp

from app.engine.prng import DeterministicRNG

type IntMatrix = tuple[tuple[int, ...], ...]


def draw_entries(rng: DeterministicRNG, rows: int, columns: int, bound: int) -> IntMatrix:
    return tuple(
        tuple(rng.randbelow(2 * bound + 1) - bound for _ in range(columns)) for _ in range(rows)
    )


def draw_invertible(rng: DeterministicRNG, size: int, diagonal: tuple[int, ...]) -> IntMatrix:
    """A row-permuted L*U with off-diagonal entries in [-2, 2] and a chosen U diagonal."""
    pivots = tuple(diagonal[rng.randbelow(len(diagonal))] for _ in range(size))
    lower = [
        [1 if i == j else (rng.randbelow(5) - 2 if j < i else 0) for j in range(size)]
        for i in range(size)
    ]
    upper = [
        [pivots[i] if i == j else (rng.randbelow(5) - 2 if j > i else 0) for j in range(size)]
        for i in range(size)
    ]
    order = tuple(permutations(range(size)))[rng.randbelow(_factorial(size))]
    product = sp.Matrix(lower) * sp.Matrix(upper)
    return tuple(tuple(int(product[row, j]) for j in range(size)) for row in order)


def _factorial(n: int) -> int:
    return 1 if n <= 1 else n * _factorial(n - 1)


def bounded(matrix: IntMatrix, bound: int) -> bool:
    return all(abs(value) <= bound for row in matrix for value in row)


def to_sympy(matrix: IntMatrix) -> sp.Matrix:
    return sp.Matrix([list(row) for row in matrix])


def pmatrix(rows: Sequence[Sequence[object]]) -> str:
    """LaTeX for a matrix given as nested rows of numbers or LaTeX strings."""
    body = r"\\".join("&".join(_cell(value) for value in row) for row in rows)
    return rf"\begin{{pmatrix}}{body}\end{{pmatrix}}"


def _cell(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Fraction):
        value = sp.Rational(value.numerator, value.denominator)
    return str(sp.latex(value))


def linear_form(coefficients: tuple[int, ...], names: tuple[str, ...]) -> str:
    """Terms in the order of the unknowns, omitting zero terms and unit coefficients."""
    terms: list[str] = []
    for coefficient, name in zip(coefficients, names, strict=True):
        if coefficient == 0:
            continue
        size = "" if abs(coefficient) == 1 else str(abs(coefficient))
        sign = "-" if coefficient < 0 else ("+" if terms else "")
        terms.append(f"{sign}{size}{name}")
    return "".join(terms) or "0"


def system_latex(matrix: IntMatrix, rhs: tuple[int, ...], names: tuple[str, ...]) -> str:
    """A linear system in `cases` layout."""
    lines = [f"{linear_form(row, names)}={value}" for row, value in zip(matrix, rhs, strict=True)]
    return "\\begin{cases}" + r"\\".join(lines) + r"\end{cases}"


def row_echelon(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    """Gaussian elimination over exact fractions, with the first nonzero pivot."""
    rows = [list(row) for row in matrix]
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next((r for r in range(pivot_row, len(rows)) if rows[r][column] != 0), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        for r in range(pivot_row + 1, len(rows)):
            factor = rows[r][column] / rows[pivot_row][column]
            rows[r] = [a - factor * b for a, b in zip(rows[r], rows[pivot_row], strict=True)]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return rows


def fractions(matrix: IntMatrix) -> list[list[Fraction]]:
    return [[Fraction(value) for value in row] for row in matrix]


def nonzero_rows(matrix: list[list[Fraction]]) -> int:
    return sum(1 for row in matrix if any(value != 0 for value in row))


def minor(matrix: IntMatrix, row: int, column: int) -> IntMatrix:
    return tuple(
        tuple(value for j, value in enumerate(values) if j != column)
        for i, values in enumerate(matrix)
        if i != row
    )


def det(matrix: IntMatrix) -> int:
    return int(to_sympy(matrix).det(method="bareiss"))
