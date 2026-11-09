"""Production providers for modulus expression and circle exercises."""

from app.engine.algebra_practice.modulus import LocalModulusCircle, LocalModulusPractice


def generators() -> tuple[LocalModulusPractice, LocalModulusCircle]:
    return LocalModulusPractice(), LocalModulusCircle()
