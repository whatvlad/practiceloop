"""Typed native solution visuals declared by topics (ADR-006).

Archived records use stored solution fields without replay or regenerated graphs.
"""

import json
import re
from copy import deepcopy
from functools import lru_cache
from typing import Any

from app.engine import practice as engine
from app.engine.codes import parse_code
from app.engine.generators.integrals import IntegralGenerator
from app.engine.generators.multiple import DoubleIntegrals
from app.engine.rendering import Issued
from app.visuals.region2d import region2d_setup
from app.visuals.single import definite_data, indefinite
from app.visuals.solid3d import solid3d_setup

VERSION = 1
MAX_BYTES = 8 * 1024


def statement_visual(record: dict[str, object]) -> dict[str, Any] | None:
    """Only the given geometry, without solution objects or answers."""
    if str(record.get("generator_version")).startswith("geometry-practice-"):
        return deepcopy(_geometry_issued(record).statement_visual)
    from app.visuals.geometry import statement_visual as geometry_statement

    return geometry_statement(record)


def _geometry_issued(record: dict[str, object]) -> Issued:
    """Read prepared geometry; arbitrary permanent codes rebuild in the worker."""
    try:
        issued = engine.pooled(record)
    except ValueError:
        issued = None
    if issued is None or issued.statement_visual is None:
        from app.api.codes import _opened

        code = record.get("code")
        if not isinstance(code, str):
            raise ValueError("Invalid geometry record")
        issued = _opened(code).problem.issued()
    if issued.record != record:
        raise ValueError("Geometry record differs from its code")
    return issued


def statement_projection(record: object) -> dict[str, Any]:
    """Project only the prepared public geometry of a supported record."""
    from app.visuals.geometry import _VERSIONS

    if not isinstance(record, dict) or (
        record.get("generator_version") not in _VERSIONS
        and not str(record.get("generator_version")).startswith("geometry-practice-")
    ):
        return {}
    visual = _geometry_issued(record).statement_visual
    return {"statementVisual": visual} if visual is not None else {}


def build_visual(record: dict[str, object]) -> dict[str, Any] | None:
    """The `visual` of a stored record, or None when its version declares none."""
    return deepcopy(_build(json.dumps(record, sort_keys=True, separators=(",", ":"))))


@lru_cache(maxsize=1024)
def _build(canonical: str) -> dict[str, Any] | None:
    record = json.loads(canonical)
    version = record.get("generator_version")
    if engine.is_engine_record(record):
        generators = engine._registry()
        code = parse_code(record["code"], generators)
        generator = generators.get_code(code.prefix, code.version)
        if generator.version != version:
            raise ValueError("Visual record version differs from its code")
        if callable(getattr(generator, "solution_visual", None)) or generator.version in {
            "local-complex-v1",
            "local-conversion-v1",
            "local-conversion-polar-v1",
            "complex-argument-v1",
            "complex-de-moivre-v1",
            "complex-root-v1",
        }:
            try:
                issued = engine.pooled(record)
            except ValueError:
                # Arbitrary permanent codes rebuild under the existing worker
                # limits; the returned private model is from the SAME code.
                from app.api.codes import _opened

                issued = _opened(record["code"]).problem.issued()
            return issued.visual
        visual = engine.visual(str(version))
        if visual is None:
            return None
        if visual == "single-integral" and isinstance(generator, IntegralGenerator):
            data = generator.data(generator.draw(code.seed))
            built = definite_data(data) if data.lower is not None else indefinite(data)
        elif visual in {"region2d", "solid3d"} and isinstance(generator, DoubleIntegrals):
            multiple = generator.data(generator.draw(code.seed))
            built = (
                region2d_setup(multiple.setup)
                if visual == "region2d"
                else solid3d_setup(multiple.setup)
            )
        else:
            raise ValueError("No builder for the engine visual of this version")
        spec = {**built, "version": VERSION}
        if len(json.dumps(spec, separators=(",", ":"))) > MAX_BYTES:
            raise ValueError("Visual spec exceeds 8 KB")
        return spec
    return None


def solution_payload(steps: Any, record: dict[str, object]) -> dict[str, Any]:
    """The worked solution as the API returns it: the steps, and the visual if any."""
    visual = build_visual(record)
    rendered = list(steps)
    version = record.get("generator_version")
    from app.visuals.geometry import _VERSIONS

    if (version in _VERSIONS or str(version).startswith("geometry-practice-")) and not any(
        step.get("visual") for step in rendered
    ):
        prepared = _geometry_issued(record).steps
        if len(prepared) == len(rendered):
            rendered = [
                {
                    **step,
                    **({"visual": source["visual"]} if source.get("visual") else {}),
                    **({"rules": source["rules"]} if source.get("rules") else {}),
                }
                for step, source in zip(rendered, prepared, strict=True)
            ]
    if version in {
        "local-polynomial-roots-v1",
        "local-polynomial-division-v1",
        "local-polynomial-scalar-v1",
    }:
        from app.engine.algebra_practice.local_polynomial_generator import RULES as division_rules
        from app.engine.algebra_practice.local_polynomial_roots_generator import RULES as root_rules

        generator = engine._registry().get(str(version))
        keys = {text: key for key, text in generator.step_text.items()}
        rules_by_key = root_rules if version == "local-polynomial-roots-v1" else division_rules
        rendered = [
            {**step, **({"rules": list(rules_by_key[key])} if key in rules_by_key else {})}
            for step in rendered
            for key in (keys.get(step["say"], ""),)
        ]
    if version == "local-determinant-v4":
        for index, step in enumerate(rendered):
            match = re.search(r"\\det\\begin\{pmatrix\}(.+?)\\end\{pmatrix\}", step["latex"])
            if not match:
                continue
            try:
                matrix = [
                    [int(value) for value in row.split("&")] for row in match.group(1).split(r"\\")
                ]
            except ValueError:
                continue
            if not 2 <= len(matrix) <= 5 or any(len(row) != len(matrix) for row in matrix):
                continue
            row_match = re.search(r"\\text\{Row (\d+):\}", step["latex"])
            if row_match and 1 <= int(row_match.group(1)) <= len(matrix):
                row = int(row_match.group(1)) - 1
                rendered[index] = {
                    **step,
                    "minorExpansion": {
                        "matrix": matrix,
                        "row": row,
                        "columns": [i for i, value in enumerate(matrix[row]) if value != 0],
                    },
                }
            else:
                rendered[index] = {**step, "determinantMatrix": matrix}
    if version == "complex-de-moivre-v1" and len(rendered) >= 8:
        from app.engine.algebra_practice.solution_rules import ARGUMENT, DEMOIVRE, MODULUS, POLAR

        for index, rule in ((2, MODULUS), (3, ARGUMENT), (5, POLAR), (7, DEMOIVRE)):
            rendered[index] = {**rendered[index], "rules": [rule]}
    if version in {
        "local-modulus-practice-v1",
        "local-modulus-circle-v1",
        "local-complex-v1",
        "local-conversion-v1",
        "local-conversion-polar-v1",
        "complex-argument-v1",
        "complex-root-v1",
    }:
        from app.engine.algebra_practice.solution_rules import complex_rules

        generator = engine._registry().get(str(version))
        keys = {text: key for key, text in generator.step_text.items()}
        rendered = [
            {**step, **({"rules": rules} if rules else {})}
            for step in rendered
            for rules in (complex_rules(str(version), keys.get(step["say"], "")),)
        ]
    return {"steps": rendered, **({"visual": visual} if visual is not None else {})}
