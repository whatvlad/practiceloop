"""Discover trusted generator-module providers and validate all frozen versions."""

from importlib import import_module
from pkgutil import iter_modules

from app.engine import generators as package
from app.engine.registry import Registry


def registry() -> Registry:
    result = Registry()
    for name in sorted(info.name for info in iter_modules(package.__path__)):
        if name == "catalogue" or name.startswith("_"):
            continue
        provider = getattr(import_module(f"{package.__name__}.{name}"), "generators", None)
        if provider is None:
            continue
        for generator in provider():
            result.register(generator)
    result.validate_dependencies()
    return result
