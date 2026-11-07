"""Seed counts for randomised generator sweeps.

Hosted CI (``CI`` is set by GitHub Actions) always runs the full count each test
asks for. Local runs default to a short smoke sweep so agent and developer
iterations stay fast; set ``PRACTICELOOP_SEEDS`` to choose the cap, for example
``PRACTICELOOP_SEEDS=1000`` to reproduce the full CI sweep locally.
"""

from __future__ import annotations

import os

LOCAL_DEFAULT = 50


def seed_cap() -> int | None:
    """Return the local seed cap, or ``None`` for the full count."""
    configured = os.environ.get("PRACTICELOOP_SEEDS", "").strip()
    if configured:
        return max(1, int(configured))
    if os.environ.get("CI"):
        return None
    return LOCAL_DEFAULT


def sweep(full: int) -> range:
    """Seeds 0..full-1 in CI, capped by ``seed_cap()`` elsewhere."""
    cap = seed_cap()
    return range(full if cap is None else min(full, cap))
