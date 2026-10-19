"""Typed, shared educational catalogue. Templates have no dynamic placeholders yet."""

import json
from pathlib import Path
from typing import Literal

type TextKey = Literal[
    "calculate",
    "linearity",
    "rewrite_power",
    "expand",
    "split_fraction",
    "integrate",
    "constant",
    "substitute",
    "differentiate",
    "rewrite",
    "substitute_back",
    "correct",
    "incorrect",
    "invalid",
    "missing_constant",
    "service_error",
    "expired",
    "unsupported",
    "preview",
    "availability",
]
TEXT: dict[TextKey, str] = json.loads(Path(__file__).with_name("en.json").read_text())
