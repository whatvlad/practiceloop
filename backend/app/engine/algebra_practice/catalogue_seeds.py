"""Enumerate local algebra settings when preparing production exercises."""

from collections.abc import Iterator

from app.engine.algebra_practice.local_matrix_generator import make_seed
from app.engine.algebra_practice.rank import rank_seed


def rank_seeds(variation: int) -> Iterator[int]:
    for level in (1, 2, 3):
        for rows in range(2, 6):
            for columns in range(2, 6):
                yield rank_seed(level, rows, columns, variation)


def matrix_seeds(level: int, variation: int) -> Iterator[int]:
    for rows in range(1, 6):
        for inner in range(1, 6):
            for operation in ("add", "subtract"):
                yield make_seed(operation, level, (rows, inner, rows, inner), variation)
            yield make_seed("divide", level, (rows, inner, inner, inner), variation)
            for columns in range(1, 6):
                yield make_seed("multiply", level, (rows, inner, inner, columns), variation)


def mode_seeds(slug: str, level: int, variation: int) -> tuple[tuple[str, str, int], ...]:
    if slug == "vectors":
        from app.engine.generators.eigen_geometry import (
            SOLID_MODES,
            angle_seed,
            area_seed,
            solid_seed,
            vector_expression_seed,
        )
        from app.engine.generators.geometry_practice import VECTOR_MODES, geometry_seed

        return (
            ("vector-expression", "vector-expression-v1", vector_expression_seed(level, variation)),
            (
                "scalar-expression",
                "vector-scalar-expression-v1",
                vector_expression_seed(level, variation),
            ),
            (
                "vector-length",
                "vector-length-practice-v1",
                vector_expression_seed(level, variation),
            ),
            (
                "perpendicular-parameter",
                "vector-perpendicular-parameter-v1",
                vector_expression_seed(level, variation),
            ),
            ("triangle-angle", "vector-triangle-angle-v2", angle_seed(level, variation)),
            (
                "triangle-area",
                "vector-area-practice-v1",
                area_seed(level, "triangle-area", variation),
            ),
            (
                "parallelogram-area",
                "vector-area-practice-v1",
                area_seed(level, "parallelogram-area", variation),
            ),
            *(
                (mode, "vector-solid-practice-v1", solid_seed(level, mode, variation))
                for mode in SOLID_MODES
            ),
            *(
                (mode, f"geometry-practice-{mode}-v1", geometry_seed(level, variation))
                for mode in VECTOR_MODES
            ),
        )
    if slug == "lines-and-planes" and level in (1, 2, 3):
        from app.engine.generators.geometry_practice import MODES as GEOMETRY_MODES
        from app.engine.generators.geometry_practice import VECTOR_MODES, geometry_seed

        result = [
            (mode, f"geometry-practice-{mode}-v1", geometry_seed(level, variation))
            for mode in GEOMETRY_MODES
            if mode not in VECTOR_MODES
        ]
        if variation == 0:
            # Reserve boundary cases inside the expanded geometry cell.
            boundary = (
                ("line-angle", 2),
                ("plane-angle", 2),
                ("line-position", 2),
                ("line-position", 3),
                ("line-plane-position", 2),
                ("same-side", 2),
                *(
                    (mode, 4)
                    for mode in (
                        "point-line-distance",
                        "point-plane-distance",
                        "parallel-line-distance",
                        "skew-line-distance",
                        "parallel-plane-distance",
                    )
                ),
            )
            result.extend(
                (mode, f"geometry-practice-{mode}-v1", geometry_seed(level, case))
                for mode, case in boundary
            )
        return tuple(result)
    if slug == "complex-numbers":
        from app.engine.algebra_practice.selection import modulus_selection

        return tuple(
            (mode, *modulus_selection(level, mode, variation))
            for mode in ("expression", "properties", "geometry")
        )
    if slug == "complex-polar-form" and level in (1, 2, 3):
        mode, version = (
            ("argument", "complex-argument-v1"),
            ("power", "complex-de-moivre-v1"),
            ("root", "complex-root-v1"),
        )[level - 1]
        return ((mode, version, variation),)
    if slug == "polynomial-roots":
        return (("roots", "local-polynomial-roots-v1", (level - 1) * 10**12 + variation),)
    if slug == "partial-fractions":
        from app.engine.algebra_practice.local_polynomial_extras import KINDS

        return (
            (
                "fractions",
                "local-partial-fractions-v1",
                ((level - 1) * len(KINDS) + KINDS.index("fractions")) * 10**12 + variation,
            ),
        )
    if slug == "complex-conversion":
        from app.engine.algebra_practice.local_conversion_generator import DIRECTIONS, VARIATIONS

        return tuple(
            (
                mode,
                "local-conversion-v1" if mode.endswith("-alg") else "local-conversion-polar-v1",
                ((level - 1) * len(DIRECTIONS) + DIRECTIONS.index(mode)) * VARIATIONS + variation,
            )
            for mode in ("alg-trig", "alg-exp", "trig-alg", "exp-alg")
        )
    if slug == "complex-arithmetic":
        from app.engine.algebra_practice.local_complex_generator import complex_seed

        return tuple(
            (mode, "local-complex-v1", complex_seed(level, mode, variation))
            for mode in ("multiply", "divide")
        )
    if slug == "polynomial-division":
        from app.engine.algebra_practice.local_polynomial_generator import MODES, VARIATIONS

        return tuple(
            (
                mode,
                "local-polynomial-division-v1"
                if mode == "division"
                else "local-polynomial-scalar-v1",
                ((level - 1) * len(MODES) + MODES.index(mode)) * VARIATIONS + variation,
            )
            for mode in MODES
        )
    raise ValueError("Unknown mode topic")
