"""Typed native solution visuals declared by topics (ADR-006).

Archived records use stored solution fields without replay or regenerated graphs.
"""

import json
from copy import deepcopy
from functools import lru_cache
from typing import Any

from app.engine import practice as engine
from app.engine.codes import parse_code
from app.engine.generators.integrals import IntegralGenerator
from app.engine.generators.multiple import DoubleIntegrals
from app.visuals.region2d import region2d_setup
from app.visuals.single import definite_data, indefinite
from app.visuals.solid3d import solid3d_setup

VERSION = 1
MAX_BYTES = 8 * 1024


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
        if callable(getattr(generator, "solution_visual", None)):
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
    if version in {"local-modulus-practice-v1", "local-modulus-circle-v1"}:
        from app.engine.algebra_practice.solution_rules import complex_rules

        generator = engine._registry().get(str(version))
        keys = {text: key for key, text in generator.step_text.items()}
        rendered = [
            {**step, **({"rules": rules} if rules else {})}
            for step in rendered
            for rules in (complex_rules(str(version), keys.get(step["say"], "")),)
        ]
    return {"steps": rendered, **({"visual": visual} if visual is not None else {})}
