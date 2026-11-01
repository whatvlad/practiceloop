"""Register the v1 generator slice; each generator carries its own code prefix."""

from app.engine.generators.combinations import Combinations
from app.engine.generators.definite import DefiniteIntegral
from app.engine.generators.derivative import Derivative
from app.engine.generators.indefinite import IndefiniteIntegral
from app.engine.generators.partial_fractions import PartialFractions
from app.engine.registry import Registry


def registry() -> Registry:
    result = Registry()
    for generator in (
        PartialFractions(),
        IndefiniteIntegral(),
        DefiniteIntegral(),
        Derivative(),
        Combinations(),
    ):
        result.register(generator)
    result.validate_dependencies()
    return result
