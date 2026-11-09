"""Production providers for local algebra exercises."""

from typing import Any

from app.engine.algebra_practice.local_complex_generator import LocalComplexGenerator
from app.engine.algebra_practice.local_conversion_generator import (
    LocalConversionGenerator,
    LocalConversionToPolarGenerator,
)
from app.engine.algebra_practice.local_determinant_generator import (
    ColoredDeterminantGenerator,
    DetailedDeterminantGenerator,
    ExplainedDeterminantGenerator,
    LocalDeterminantGenerator,
)
from app.engine.algebra_practice.local_inverse_generator import LocalInverseGenerator
from app.engine.algebra_practice.local_matrix_generator import (
    LeveledMatrixDivisionGenerator,
    LocalMatrixDivisionGenerator,
    LocalMatrixGenerator,
)
from app.engine.algebra_practice.local_polynomial_extras import (
    PartialFractionsExtras,
    PolynomialExtras,
)
from app.engine.algebra_practice.local_polynomial_generator import (
    LocalPolynomialGenerator,
    LocalPolynomialScalarGenerator,
)
from app.engine.algebra_practice.local_polynomial_roots_generator import (
    LocalPolynomialRootsGenerator,
)
from app.engine.algebra_practice.local_system_generator import LocalSystemGenerator
from app.engine.algebra_practice.rank import LocalRankGenerator
from app.engine.models import TaskGenerator


def generators() -> tuple[TaskGenerator[Any], ...]:
    return tuple(
        cls()
        for cls in (
            LocalRankGenerator,
            LocalComplexGenerator,
            LocalConversionGenerator,
            LocalConversionToPolarGenerator,
            LocalDeterminantGenerator,
            DetailedDeterminantGenerator,
            ColoredDeterminantGenerator,
            ExplainedDeterminantGenerator,
            LocalInverseGenerator,
            LocalMatrixGenerator,
            LocalMatrixDivisionGenerator,
            LeveledMatrixDivisionGenerator,
            PolynomialExtras,
            PartialFractionsExtras,
            LocalPolynomialGenerator,
            LocalPolynomialScalarGenerator,
            LocalPolynomialRootsGenerator,
            LocalSystemGenerator,
        )
    )
