"""Which generator versions get which visual (ADR-006), and the cached builder.

Every catalogue version is either in BUILDERS or declared in NO_VISUAL; the
catalogue-wide test in tests/test_visuals.py keeps that true. A spec is built from
the replayed exercise only, so it reveals nothing the solution steps do not.
"""

import json
from collections.abc import Callable
from functools import lru_cache
from typing import Any

from app.generators.core import Exercise, replay
from app.visuals.single import definite, indefinite

VERSION = 1
MAX_BYTES = 8 * 1024

BUILDERS: dict[str, Callable[[Exercise], dict[str, Any]]] = {
    "definite-v1": definite,
    "basic-v1": indefinite,
    "substitution-v1": indefinite,
    "substitution-v2": indefinite,
    "parts-v1": indefinite,
    "rational-v1": indefinite,
    "trigonometric-v1": indefinite,
}
# Double (#113) and triple (#114) integrals move to BUILDERS with their kinds;
# derivatives have no visual in ADR-006.
NO_VISUAL = frozenset({"double-v1", "triple-v1", "derivatives-v1", "partial-v1"})


def build_visual(record: dict[str, object]) -> dict[str, Any] | None:
    """The `visual` of a stored record, or None when its version declares none."""
    return _build(json.dumps(record, sort_keys=True, separators=(",", ":")))


@lru_cache(maxsize=1024)
def _build(canonical: str) -> dict[str, Any] | None:
    record = json.loads(canonical)
    version = record.get("generator_version")
    if version in NO_VISUAL:
        return None
    builder = BUILDERS.get(version)
    if builder is None:
        raise ValueError("Generator version declares no visual decision")
    spec = {**builder(replay(record)), "version": VERSION}
    if len(json.dumps(spec, separators=(",", ":"))) > MAX_BYTES:
        raise ValueError("Visual spec exceeds 8 KB")
    return spec


def solution_payload(steps: Any, record: dict[str, object]) -> dict[str, Any]:
    """The worked solution as the API returns it: the steps, and the visual if any."""
    visual = build_visual(record)
    return {"steps": list(steps), **({"visual": visual} if visual is not None else {})}
