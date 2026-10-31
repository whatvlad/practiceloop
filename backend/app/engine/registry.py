"""Registry of private generators and validation of their dependencies."""

import re
from typing import Any

from app.engine.models import Parameters, TaskGenerator


class Registry:
    def __init__(self) -> None:
        self._generators: dict[str, TaskGenerator[Any]] = {}
        self._prefixes: dict[str, str] = {}
        self._families: dict[str, str] = {}
        self._code_versions: dict[tuple[str, int], str] = {}

    def register(self, generator: TaskGenerator[Any]) -> None:
        version = generator.version
        if not isinstance(version, str) or not version.strip() or version != version.strip():
            raise ValueError("Generator version must be non-empty and have no surrounding space")
        if version in self._generators:
            raise ValueError(f"Duplicate generator version: {version}")
        if not isinstance(generator.params, type) or not issubclass(generator.params, Parameters):
            raise ValueError("Generator parameters must inherit Parameters")
        answer = generator.answer
        kind = getattr(answer, "kind", None)
        if (
            not isinstance(answer, type)
            or not isinstance(kind, str)
            or not kind.strip()
            or not callable(getattr(answer, "latex", None))
            or not callable(getattr(answer, "check", None))
        ):
            raise ValueError("Invalid generator answer metadata")
        requires = generator.requires
        if not isinstance(requires, tuple) or any(
            not isinstance(dep, str) or not dep.strip() or dep != dep.strip() for dep in requires
        ):
            raise ValueError("Generator dependencies must be version strings")
        if len(set(requires)) != len(requires):
            raise ValueError(f"Duplicate dependency for {version}")
        self._generators[version] = generator

    def register_code(self, prefix: str, family: str, version: int, generator_version: str) -> None:
        """Permanently associate a prefix and numeric version with a generator."""
        if not isinstance(prefix, str) or re.fullmatch(r"[A-Z]{2,8}", prefix) is None:
            raise ValueError("Code prefix must be 2 to 8 uppercase ASCII letters")
        if not isinstance(family, str) or re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", family) is None:
            raise ValueError("Invalid generator family")
        if type(version) is not int or not 1 <= version <= 9999:
            raise ValueError("Code version must be an integer from 1 through 9999")
        self.get(generator_version)
        if prefix in self._prefixes and self._prefixes[prefix] != family:
            raise ValueError(f"Code prefix already belongs to another family: {prefix}")
        if family in self._families and self._families[family] != prefix:
            raise ValueError(f"Generator family already has a prefix: {family}")
        key = (prefix, version)
        if key in self._code_versions:
            raise ValueError(f"Duplicate code version: {prefix}-{version}")
        if generator_version in self._code_versions.values():
            raise ValueError(f"Generator version already has a code: {generator_version}")
        self._prefixes[prefix] = family
        self._families[family] = prefix
        self._code_versions[key] = generator_version

    def get_code(self, prefix: str, version: int) -> TaskGenerator[Any]:
        if not isinstance(prefix, str) or type(version) is not int:
            raise ValueError("Invalid code prefix or version")
        try:
            generator_version = self._code_versions[(prefix, version)]
        except KeyError as exc:
            raise ValueError(f"Unknown code prefix or version: {prefix}-{version}") from exc
        return self.get(generator_version)

    def get(self, version: str) -> TaskGenerator[Any]:
        try:
            return self._generators[version]
        except KeyError as exc:
            raise ValueError(f"Unknown generator version: {version}") from exc

    def validate_dependencies(self) -> None:
        visited: set[str] = set()
        visiting: set[str] = set()

        def visit(version: str) -> None:
            if version in visiting:
                raise ValueError(f"Circular dependency at {version}")
            if version in visited:
                return
            generator = self.get(version)
            visiting.add(version)
            for dependency in generator.requires:
                visit(dependency)
            visiting.remove(version)
            visited.add(version)

        for version in self._generators:
            visit(version)
