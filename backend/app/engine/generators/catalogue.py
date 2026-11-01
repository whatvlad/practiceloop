"""Register the v1 generator slice; each generator carries its own code prefix."""

from typing import Any

from app.engine.generators.algebra import algebra_generators
from app.engine.generators.analysis import analysis_generators
from app.engine.generators.combinations import Combinations
from app.engine.generators.definite import DefiniteIntegral
from app.engine.generators.derivative import Derivative
from app.engine.generators.differentiation import PartialDerivatives, SingleDerivatives
from app.engine.generators.indefinite import IndefiniteIntegral
from app.engine.generators.integrals import integral_generators
from app.engine.generators.multiple import DoubleIntegrals, TripleIntegrals
from app.engine.generators.partial_fractions import PartialFractions
from app.engine.models import TaskGenerator
from app.engine.registry import Registry


def registry() -> Registry:
    result = Registry()
    generators: tuple[TaskGenerator[Any], ...] = (
        PartialFractions(),
        IndefiniteIntegral(),
        DefiniteIntegral(),
        Derivative(),
        Combinations(),
        *integral_generators(),
        DoubleIntegrals(),
        TripleIntegrals(),
        SingleDerivatives(),
        PartialDerivatives(),
        *algebra_generators(),
        *analysis_generators(),
    )
    for generator in generators:
        result.register(generator)
    result.validate_dependencies()
    return result
