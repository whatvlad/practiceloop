"""Validated selection of the frozen algebra generator and problem seed."""

from app.engine.algebra_practice.modulus import (
    VARIATIONS,
    LocalModulusCircle,
    LocalModulusPractice,
)


def modulus_selection(level: int, mode: str, variation: int) -> tuple[str, int]:
    """Return a reproducible version and seed without constructing an answer."""
    if (
        type(level) is not int
        or level not in (1, 2, 3)
        or mode not in ("expression", "properties", "geometry")
        or type(variation) is not int
        or not 0 <= variation < VARIATIONS
    ):
        raise ValueError("Invalid modulus settings")
    version = LocalModulusCircle.version if mode == "geometry" else LocalModulusPractice.version
    index = level - 1 + (3 if mode == "properties" else 0)
    return version, index * VARIATIONS + variation
