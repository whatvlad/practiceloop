"""Serve new-engine topics through the practice API (#169).

The private record of a new-engine problem is its problem code and generator
version only; the task is rebuilt from the code whenever the answer is checked,
so the stored code alone reproduces the problem. Nothing here crosses the public
API except the statement, and, after a reveal, the answer and solution steps.
"""

import secrets
from functools import cache
from typing import Any

from app.engine.algebra_practice.modulus import LocalModulusCircle, LocalModulusPractice
from app.engine.catalogue import lookup
from app.engine.catalogue import pool as pool
from app.engine.codes import parse_code
from app.engine.generators.catalogue import registry
from app.engine.models import Outcome, Task
from app.engine.registry import Registry
from app.engine.rendering import Issued, render
from app.engine.rendering import statement_latex as statement_latex
from app.engine.topics.catalogue import Topic, topics
from app.geometry_options import geometry_modes
from app.math_input import MathNode, VariableDomain, declared_variables
from app.math_input.contracts import COMPUTATIONAL_KINDS, InputContract

# Public topic slug -> its served engine entry (#191), derived from the topic catalogue;
# never edit it by hand. Other public topics stay on the old engine.
ENGINE_TOPICS: dict[str, Topic] = {slug: t for slug, t in topics().items() if t.served}


@cache
def _registry() -> Registry:
    return registry()


def levels(slug: str) -> tuple[int, ...]:
    return tuple(sorted(ENGINE_TOPICS[slug].levels))


def visual(version: str) -> str | None:
    """The visual its served topics declare for a generator version; one per version."""
    declared = {
        topic.visual
        for topic in ENGINE_TOPICS.values()
        for choices in topic.levels.values()
        for choice in choices
        if choice.generator == version
    }
    if len(declared) > 1:
        raise ValueError(f"Served topics declare different visuals for {version}")
    return next(iter(declared), None)


def _public(task: Task) -> Issued:
    return render(task, _registry())


MATRIX_OPTIONS = {
    1: frozenset((op, size) for op in ("add", "subtract") for size in ("2x2", "3x3"))
    | frozenset(("multiply", size) for size in ("2x2", "3x3", "rectangular")),
    2: frozenset({("multiply", "rectangular"), ("mixed", "rectangular")}),
    3: frozenset({("multiply", "2x2"), ("mixed", "2x2")}),
}


def matrix_options_supported(level: int, options: dict[str, str]) -> bool:
    return set(options) == {"operation", "size"} and (
        options["operation"],
        options["size"],
    ) in MATRIX_OPTIONS.get(level, frozenset())


def issue(
    slug: str,
    level: int,
    seed: int | None = None,
    *,
    recent: tuple[dict[str, object], ...] = (),
    matrix_options: dict[str, str] | None = None,
    modulus_mode: str | None = None,
    rank_dimensions: dict[str, int] | None = None,
    matrix_dimensions: dict[str, Any] | None = None,
    square_size: int | None = None,
    exercise_mode: str | None = None,
) -> Issued:
    """Pick rendered private data; even a cold symbolic cell runs no SymPy."""
    topic = ENGINE_TOPICS[slug]
    if type(level) is not int or level not in topic.levels:
        raise ValueError("Unknown topic level")
    complete = pool(slug, level)
    if exercise_mode is not None:
        supported = {
            "complex-arithmetic": {"multiply", "divide"},
            "polynomial-division": {"division", "remainder", "divisibility"},
            "complex-conversion": {"alg-trig", "alg-exp", "trig-alg", "exp-alg"},
            "polynomial-roots": {"roots"},
            "partial-fractions": {"fractions"},
            "complex-polar-form": {"argument", "power", "root"},
            "vectors": geometry_modes("vectors")
            | {
                "vector-expression",
                "scalar-expression",
                "vector-length",
                "perpendicular-parameter",
                "triangle-angle",
                "triangle-area",
                "parallelogram-area",
                "tetrahedron-volume",
                "tetrahedron-height",
                "parallelepiped-area",
            },
            "lines-and-planes": geometry_modes("lines-and-planes"),
        }
        if level not in (1, 2, 3) or exercise_mode not in supported.get(slug, set()):
            raise ValueError("Invalid exercise mode")
        complete = tuple(
            p
            for p in complete
            if public_settings(p.issued().record).get("exerciseMode") == exercise_mode
        )
        if not complete:
            raise ValueError("No problems match this exercise mode")
    if square_size is not None:
        versions = {
            "determinants": "local-determinant-v4",
            "inverse-matrices": "local-inverse-v1",
            "linear-systems": "local-system-v1",
        }
        if (
            slug not in versions
            or level not in (1, 2, 3)
            or type(square_size) is not int
            or square_size not in (2, 3, 4, 5)
        ):
            raise ValueError("Invalid matrix size")
        complete = tuple(
            p
            for p in complete
            if p.generator_version == versions[slug]
            and (parse_code(p.code, _registry()).seed // 10**12) % 4 + 2 == square_size
        )
        if not complete:
            raise ValueError("No problems match this size")
    if matrix_dimensions is not None:
        from app.engine.algebra_practice.local_matrix_generator import make_seed

        if slug != "matrix-operations" or set(matrix_dimensions) != {
            "operation",
            "rowsA",
            "colsA",
            "rowsB",
            "colsB",
        }:
            raise ValueError("Invalid matrix settings")
        try:
            seed = make_seed(
                matrix_dimensions["operation"],
                level,
                tuple(matrix_dimensions[key] for key in ("rowsA", "colsA", "rowsB", "colsB")),
                0,
            )
        except (ValueError, TypeError) as exc:
            raise ValueError("Invalid matrix settings") from exc
        complete = tuple(
            p
            for p in complete
            if p.generator_version in {"local-matrix-sized-v1", "local-matrix-division-v3"}
            and parse_code(p.code, _registry()).seed // 10**12 == seed // 10**12
        )
        if not complete:
            raise ValueError("No matrix problems match these settings")
    if rank_dimensions is not None:
        if (
            slug != "matrix-rank"
            or level not in (1, 2, 3)
            or set(rank_dimensions) != {"rows", "columns"}
            or any(type(v) is not int or not 2 <= v <= 5 for v in rank_dimensions.values())
        ):
            raise ValueError("Invalid rank dimensions")
        complete = tuple(
            problem
            for problem in complete
            if problem.generator_version == "local-rank-v1"
            and _rank_dimensions(problem.code) == rank_dimensions
        )
        if not complete:
            raise ValueError("No rank problems match these dimensions")
    if slug == "complex-numbers" and modulus_mode is None:
        complete = tuple(
            problem
            for problem in complete
            if problem.generator_version
            not in {LocalModulusCircle.version, LocalModulusPractice.version}
        )
    if modulus_mode is not None:
        if (
            slug != "complex-numbers"
            or level not in (1, 2, 3)
            or modulus_mode not in ("expression", "properties", "geometry")
        ):
            raise ValueError("Invalid modulus settings")
        selected = []
        for problem in complete:
            code = parse_code(problem.code, _registry())
            generator = _registry().get_code(code.prefix, code.version)
            if generator.version == LocalModulusCircle.version:
                matches = modulus_mode == "geometry"
            elif generator.version == LocalModulusPractice.version:
                matches = generator.draw(code.seed).mode == modulus_mode
            else:
                matches = False
            if matches:
                selected.append(problem)
        complete = tuple(selected)
        if not complete:
            raise ValueError("No modulus problems match these settings")
    if matrix_options is not None:
        if slug != "matrix-operations" or not matrix_options_supported(level, matrix_options):
            raise ValueError("Invalid matrix settings")
        wanted = (matrix_options["operation"], matrix_options["size"])
        complete = tuple(
            problem
            for problem in complete
            if not problem.generator_version.startswith("local-matrix-")
            and matrix_classification(problem.issued().record) == wanted
        )
        if not complete:
            raise ValueError("No matrix problems match these settings")
    candidates = tuple(p for p in complete if p.issued().record not in recent) or complete
    if slug in {"vectors", "lines-and-planes"} and level <= 3 and exercise_mode is None:
        # A mode's boundary cases enlarge its pool, not its chance of being selected.
        groups: dict[str, list[Any]] = {}
        for problem in candidates:
            mode = public_settings(problem.issued().record).get(
                "exerciseMode", problem.generator_version
            )
            groups.setdefault(mode, []).append(problem)
        grouped = tuple(groups.values())
        index = secrets.randbelow(len(grouped)) if seed is None else seed % len(grouped)
        candidates = tuple(grouped[index])
        if seed is not None:
            seed //= len(grouped)
    chosen = secrets.randbelow(len(candidates)) if seed is None else seed % len(candidates)
    return candidates[chosen].issued()


def matrix_classification(record: dict[str, object]) -> tuple[str, str]:
    """Derive public exercise settings from the trusted code, without building its answer."""
    parsed = parse_code(str(record["code"]), _registry())
    generator = _registry().get_code(parsed.prefix, parsed.version)
    if generator.version != record.get("generator_version"):
        raise ValueError("Invalid generator record")
    params = generator.draw(parsed.seed)
    if generator.version == "matrix-sum-v2":
        return (
            "add" if params.sign == 1 else "subtract",
            f"{len(params.first)}x{len(params.first)}",
        )
    if generator.version == "matrix-multiply-v1":
        rows, columns = len(params.first), len(params.first[0])
        return ("multiply", f"{rows}x{columns}" if rows == columns else "rectangular")
    if generator.version == "matrix-product-v3":
        return ("multiply", "rectangular")
    if generator.version == "matrix-trig-v2":
        return ("multiply", "2x2")
    if generator.version == "matrix-combination-v3":
        return ("mixed", "rectangular")
    if generator.version == "matrix-commutator-v3":
        return ("mixed", "2x2")
    raise ValueError("Not a current matrix exercise")


def pooled(record: dict[str, object]) -> Issued:
    """Read the rendered fields for a worksheet pick without rebuilding its task."""
    return lookup(record)


def is_engine_record(record: Any) -> bool:
    return isinstance(record, dict) and "code" in record


def _rank_dimensions(code: str) -> dict[str, int]:
    parsed = parse_code(code, _registry())
    shape = (parsed.seed // 10**12) % 16
    return {"rows": shape // 4 + 2, "columns": shape % 4 + 2}


def _matrix_dimensions(code: str) -> dict[str, Any]:
    from app.engine.algebra_practice.local_matrix_generator import OPERATIONS

    parsed = parse_code(code, _registry())
    index = parsed.seed // 10**12
    dims = []
    for _ in range(4):
        dims.append(index % 5 + 1)
        index //= 5
    dims.reverse()
    return dict(
        zip(
            ("operation", "rowsA", "colsA", "rowsB", "colsB"),
            (OPERATIONS[index // 3], *dims),
            strict=True,
        )
    )


def public_settings(record: Any) -> dict[str, Any]:
    """Recover learner-selected settings without exposing answer parameters."""
    if is_engine_record(record) and str(record.get("generator_version")).startswith(
        "geometry-practice-"
    ):
        from app.engine.generators.geometry_practice import GeometryPractice

        parsed = parse_code(record["code"], _registry())
        generator = _registry().get_code(parsed.prefix, parsed.version)
        if (
            not isinstance(generator, GeometryPractice)
            or generator.version != record["generator_version"]
            or parsed.seed >= 3 * 10**12
        ):
            raise ValueError("Invalid geometry settings")
        return {"exerciseMode": generator.mode}
    if is_engine_record(record) and record.get("generator_version") == "vector-solid-practice-v1":
        from app.engine.generators.eigen_geometry import SOLID_MODES

        parsed = parse_code(record["code"], _registry())
        if (
            _registry().get_code(parsed.prefix, parsed.version).version
            != record["generator_version"]
        ):
            raise ValueError("Record version differs from its code")
        index = parsed.seed // 10**12
        if index >= 3 * len(SOLID_MODES):
            raise ValueError("Invalid solid settings")
        return {"exerciseMode": SOLID_MODES[index % len(SOLID_MODES)]}
    if is_engine_record(record) and record.get("generator_version") == "vector-area-practice-v1":
        from app.engine.generators.eigen_geometry import AREA_MODES

        parsed = parse_code(record["code"], _registry())
        if (
            _registry().get_code(parsed.prefix, parsed.version).version
            != record["generator_version"]
        ):
            raise ValueError("Record version differs from its code")
        index = parsed.seed // 10**12
        if index >= 3 * len(AREA_MODES):
            raise ValueError("Invalid area settings")
        return {"exerciseMode": AREA_MODES[index % len(AREA_MODES)]}
    vector_modes = {
        "vector-expression-v1": "vector-expression",
        "vector-scalar-expression-v1": "scalar-expression",
        "vector-length-practice-v1": "vector-length",
        "vector-perpendicular-parameter-v1": "perpendicular-parameter",
        "vector-triangle-angle-v2": "triangle-angle",
    }
    if is_engine_record(record) and record.get("generator_version") in vector_modes:
        parsed = parse_code(record["code"], _registry())
        if (
            _registry().get_code(parsed.prefix, parsed.version).version
            != record["generator_version"]
        ):
            raise ValueError("Record version differs from its code")
        return {"exerciseMode": vector_modes[record["generator_version"]]}
    polar_modes = {
        "complex-argument-v1": "argument",
        "complex-de-moivre-v1": "power",
        "complex-root-v1": "root",
    }
    if is_engine_record(record) and record.get("generator_version") in polar_modes:
        parsed = parse_code(record["code"], _registry())
        if (
            _registry().get_code(parsed.prefix, parsed.version).version
            != record["generator_version"]
        ):
            raise ValueError("Record version differs from its code")
        return {"exerciseMode": polar_modes[record["generator_version"]]}
    if is_engine_record(record) and record.get("generator_version") in {
        "local-polynomial-roots-v1",
        "local-partial-fractions-v1",
    }:
        parsed = parse_code(record["code"], _registry())
        if (
            _registry().get_code(parsed.prefix, parsed.version).version
            != record["generator_version"]
        ):
            raise ValueError("Record version differs from its code")
        return {
            "exerciseMode": "roots"
            if record["generator_version"] == "local-polynomial-roots-v1"
            else "fractions"
        }
    if is_engine_record(record) and record.get("generator_version") in {
        "local-complex-v1",
        "local-polynomial-division-v1",
        "local-polynomial-scalar-v1",
        "local-conversion-v1",
        "local-conversion-polar-v1",
    }:
        parsed = parse_code(record["code"], _registry())
        generator = _registry().get_code(parsed.prefix, parsed.version)
        if generator.version != record["generator_version"]:
            raise ValueError("Record version differs from its code")
        index = parsed.seed // 10**12
        if generator.version.startswith("local-conversion"):
            from app.engine.algebra_practice.local_conversion_generator import DIRECTIONS

            return {"exerciseMode": DIRECTIONS[index % len(DIRECTIONS)]}
        if generator.version == "local-complex-v1":
            from app.engine.algebra_practice.local_complex_generator import OPERATIONS

            return {"exerciseMode": OPERATIONS[index % len(OPERATIONS)]}
        from app.engine.algebra_practice.local_polynomial_generator import MODES

        return {"exerciseMode": MODES[index % len(MODES)]}
    if is_engine_record(record) and record.get("generator_version") in {
        "local-determinant-v4",
        "local-inverse-v1",
        "local-system-v1",
    }:
        parsed = parse_code(record["code"], _registry())
        if (
            _registry().get_code(parsed.prefix, parsed.version).version
            != record["generator_version"]
        ):
            raise ValueError("Record version differs from its code")
        return {"squareSize": (parsed.seed // 10**12) % 4 + 2}
    if is_engine_record(record) and record.get("generator_version") in {
        "local-matrix-sized-v1",
        "local-matrix-division-v3",
    }:
        parsed = parse_code(record["code"], _registry())
        if (
            _registry().get_code(parsed.prefix, parsed.version).version
            != record["generator_version"]
        ):
            raise ValueError("Record version differs from its code")
        return {"matrixDimensions": _matrix_dimensions(record["code"])}
    if is_engine_record(record) and record.get("generator_version") == "local-rank-v1":
        parsed = parse_code(record["code"], _registry())
        if _registry().get_code(parsed.prefix, parsed.version).version != "local-rank-v1":
            raise ValueError("Record version differs from its code")
        return {"rankDimensions": _rank_dimensions(record["code"])}
    if not is_engine_record(record) or record.get("generator_version") not in {
        LocalModulusPractice.version,
        LocalModulusCircle.version,
    }:
        return {}
    code = parse_code(record["code"], _registry())
    generator = _registry().get_code(code.prefix, code.version)
    if generator.version != record["generator_version"]:
        raise ValueError("Record version differs from its code")
    mode = (
        "geometry"
        if generator.version == LocalModulusCircle.version
        else generator.draw(code.seed).mode
    )
    return {"modulusMode": mode}


def replay(record: dict[str, object]) -> Task:
    """Rebuild the task from its stored code; raise ValueError for an unusable record."""
    if set(record) != {"generator_version", "code"} or not isinstance(record["code"], str):
        raise ValueError("Invalid new-engine record")
    code = parse_code(record["code"], _registry())
    generator = _registry().get_code(code.prefix, code.version)
    if generator.version != record["generator_version"]:
        raise ValueError("Record version differs from its code")
    task = generator.build(generator.draw(code.seed))
    if task.code != record["code"]:
        raise ValueError("Rebuilt task has a different code")
    return task


def public_replay(record: dict[str, object]) -> Issued:
    return _public(replay(record))


def input_variables(record: dict[str, object]) -> dict[str, VariableDomain] | None:
    """Optional plain grammar metadata from drawn parameters, without building a task.

    The frozen generator protocol is unchanged. A multivariable generator may
    expose this private helper; its saved record still contains only the code.
    """
    if set(record) != {"generator_version", "code"} or not isinstance(record["code"], str):
        raise ValueError("Invalid new-engine record")
    code = parse_code(record["code"], _registry())
    generator = _registry().get_code(code.prefix, code.version)
    if generator.version != record["generator_version"]:
        raise ValueError("Record version differs from its code")
    if generator.version in {
        "local-complex-v1",
        "local-conversion-v1",
        "local-conversion-polar-v1",
    }:
        return {"i": "imaginary"}
    describe = getattr(generator, "input_variables", None)
    if describe is None:
        return None
    return declared_variables(describe(generator.draw(code.seed)))


def check(record: dict[str, object], tree: MathNode) -> Outcome:
    return replay(record).answer.check(tree)


def input_kind(record: dict[str, object]) -> str:
    """Trusted answer metadata, read without symbolic construction."""
    if set(record) != {"generator_version", "code"} or not isinstance(record["code"], str):
        raise ValueError("Invalid new-engine record")
    code = parse_code(record["code"], _registry())
    generator = _registry().get_code(code.prefix, code.version)
    if generator.version != record["generator_version"]:
        raise ValueError("Record version differs from its code")
    return str(getattr(generator.answer, "kind", "expression"))


def input_projection(record: object) -> dict[str, object]:
    """Only optional input instructions; never private parameters or answers."""
    from app.math_input.structured import STRUCTURED_KINDS

    if not is_engine_record(record):
        return {}
    kind = input_kind(record)  # type: ignore[arg-type]
    if kind in COMPUTATIONAL_KINDS:
        contract = input_contract(record)  # type: ignore[arg-type]
        if contract is None:
            raise ValueError("Missing computational input contract")
        return {"answerInput": contract.public()}
    if kind not in STRUCTURED_KINDS:
        return {}
    descriptor: dict[str, object] = {"kind": kind, "maxBytes": 256}
    if kind == "finite_set":
        descriptor["maxItems"] = 8
    return {"answerInput": descriptor}


def prompt_visual(record: object) -> dict[str, Any] | None:
    """Build only the public diagram from the frozen draw, without constructing the task."""
    if not is_engine_record(record):
        return None
    if not isinstance(record, dict) or not isinstance(record.get("code"), str):
        raise ValueError("Invalid new-engine record")
    code = parse_code(record["code"], _registry())
    generator = _registry().get_code(code.prefix, code.version)
    if generator.version != record.get("generator_version"):
        raise ValueError("Record version differs from its code")
    build = getattr(generator, "prompt_visual", None)
    if not callable(build):
        return None
    diagram = build(generator.draw(code.seed))
    if diagram is None:
        return None
    from app.visuals.plot2d import validate_plot

    return validate_plot(diagram)


def problem_projection(record: object) -> dict[str, object]:
    """Optional public input and prompt data shared by practice, history and code lookup."""
    fields = input_projection(record)
    if (
        isinstance(record, dict)
        and is_engine_record(record)
        and input_kind(record) == "self_review"
    ):
        fields["selfReview"] = True
    diagram = prompt_visual(record)
    if diagram is not None:
        fields["promptVisual"] = diagram
    return fields


def input_contract(record: dict[str, object]) -> InputContract | None:
    """Optional plain contract from the same frozen draw, never an expected answer."""
    kind = input_kind(record)  # validates record/version/code before any helper call
    if kind not in COMPUTATIONAL_KINDS:
        return None
    code = parse_code(record["code"], _registry())  # type: ignore[arg-type]
    generator = _registry().get_code(code.prefix, code.version)
    version = generator.version
    if version.startswith("geometry-practice-"):
        from app.engine.generators.geometry_practice import GeometryPractice, mode_contract

        if not isinstance(generator, GeometryPractice) or code.seed >= 3 * 10**12:
            raise ValueError("Invalid geometry input contract")
        return mode_contract(generator.mode)
    if version == "vector-expression-v1":
        return InputContract(
            "tuple",
            components=(InputContract("formula"),) * 3,
            labels=("x component", "y component", "z component"),
        )
    if version in {"local-matrix-sized-v1", "local-matrix-division-v3", "local-inverse-v1"}:
        from app.engine.generators.matrix_full import matrix_contract

        if version == "local-inverse-v1":
            size = (code.seed // 10**12) % 4 + 2
            return matrix_contract(size, size)
        dimensions = _matrix_dimensions(str(record["code"]))
        return matrix_contract(dimensions["rowsA"], dimensions["colsB"])
    if (
        version == "local-rank-v1"
        or version == "local-determinant-v4"
        or version == "local-polynomial-scalar-v1"
    ):
        return InputContract("formula")
    if version in {
        "local-system-v1",
        "local-conversion-polar-v1",
        "local-polynomial-division-v1",
        "local-partial-fractions-v1",
        "local-modulus-circle-v1",
    }:
        formula = InputContract("formula")
        if version == "local-system-v1":
            count = (code.seed // 10**12) % 4 + 2
            labels = tuple(
                f"Variable {name}" for name in ("one", "two", "three", "four", "five")[:count]
            )
            components = (formula,) * count
        elif version == "local-conversion-polar-v1":
            labels, components = ("Modulus r", "Principal argument"), (formula, formula)
        elif version == "local-modulus-circle-v1":
            labels, components = ("Centre x", "Centre y", "Radius"), (formula, formula, formula)
        elif version == "local-polynomial-division-v1":
            polynomial = InputContract("formula", symbols=(("x", "real"),))
            labels, components = ("Quotient", "Remainder"), (polynomial, polynomial)
        else:
            count = 2 if (code.seed // 10**12) // 5 == 0 else 3
            labels, components = ("A", "B", "C")[:count], (formula,) * count
        return InputContract("tuple", components=components, labels=labels)
    describe = getattr(generator, "input_contract", None)
    if not callable(describe):
        raise ValueError("Generator must declare its computational grammar")
    contract = describe(generator.draw(code.seed))
    if not isinstance(contract, InputContract) or contract.kind != kind:
        raise ValueError("Generator contract differs from answer kind")
    return contract
