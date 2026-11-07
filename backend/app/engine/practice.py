"""Serve new-engine topics through the practice API (#169).

The private record of a new-engine problem is its problem code and generator
version only; the task is rebuilt from the code whenever the answer is checked,
so the stored code alone reproduces the problem. Nothing here crosses the public
API except the statement, and, after a reveal, the answer and solution steps.
"""

import secrets
from functools import cache
from typing import Any

from app.engine.catalogue import lookup
from app.engine.catalogue import pool as pool
from app.engine.codes import parse_code
from app.engine.generators.catalogue import registry
from app.engine.models import Outcome, Task
from app.engine.registry import Registry
from app.engine.rendering import Issued, render
from app.engine.rendering import statement_latex as statement_latex
from app.engine.topics.catalogue import Topic, topics
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
) -> Issued:
    """Pick rendered private data; even a cold symbolic cell runs no SymPy."""
    topic = ENGINE_TOPICS[slug]
    if type(level) is not int or level not in topic.levels:
        raise ValueError("Unknown topic level")
    complete = pool(slug, level)
    if matrix_options is not None:
        if slug != "matrix-operations" or not matrix_options_supported(level, matrix_options):
            raise ValueError("Invalid matrix settings")
        wanted = (matrix_options["operation"], matrix_options["size"])
        complete = tuple(
            problem
            for problem in complete
            if matrix_classification(problem.issued().record) == wanted
        )
        if not complete:
            raise ValueError("No matrix problems match these settings")
    candidates = tuple(p for p in complete if p.issued().record not in recent) or complete
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


def input_contract(record: dict[str, object]) -> InputContract | None:
    """Optional plain contract from the same frozen draw, never an expected answer."""
    kind = input_kind(record)  # validates record/version/code before any helper call
    if kind not in COMPUTATIONAL_KINDS:
        return None
    code = parse_code(record["code"], _registry())  # type: ignore[arg-type]
    generator = _registry().get_code(code.prefix, code.version)
    describe = getattr(generator, "input_contract", None)
    if not callable(describe):
        raise ValueError("Generator must declare its computational grammar")
    contract = describe(generator.draw(code.seed))
    if not isinstance(contract, InputContract) or contract.kind != kind:
        raise ValueError("Generator contract differs from answer kind")
    return contract
