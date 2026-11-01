"""Register the v1 generator slice and its permanent code prefixes."""

from app.engine.generators.combinations import Combinations
from app.engine.generators.definite import DefiniteIntegral
from app.engine.generators.derivative import Derivative
from app.engine.generators.indefinite import IndefiniteIntegral
from app.engine.generators.partial_fractions import PartialFractions
from app.engine.registry import Registry


def registry() -> Registry:
    result = Registry()
    for generator, prefix, family in (
        (PartialFractions(), "PFR", "partial-fractions"),
        (IndefiniteIntegral(), "INT", "indefinite"),
        (DefiniteIntegral(), "DEF", "definite"),
        (Derivative(), "DRV", "derivative"),
        (Combinations(), "CMB", "combinations"),
    ):
        result.register(generator)
        result.register_code(prefix, family, 1, generator.version)
    result.validate_dependencies()
    return result
