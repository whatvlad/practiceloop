"""Registry of private generators and validation of their dependencies."""

from typing import Any

from app.engine.models import Parameters, TaskGenerator


class Registry:
    def __init__(self) -> None:
        self._generators: dict[str, TaskGenerator[Any]] = {}

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
