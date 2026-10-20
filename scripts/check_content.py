"""Deterministic STE-inspired checks for our own glossary, not ASD certification."""

import json
import re
import sys
from pathlib import Path
from typing import get_args

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.content.catalogue import TextKey  # noqa: E402

CATALOGUE = ROOT / "backend/app/content/en.json"
INSTRUCTIONS = {
    "factor",
    "identity",
    "substitution_integral",
    "nested_substitution",
    "parts",
    "repeat_parts",
    "solve_cycle",
    "partial_fractions",
    "polynomial_division",
    "calculate",
    "calculate_definite",
    "evaluate_bounds",
    "definite_value",
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
    "incorrect",
    "invalid",
    "missing_constant",
    "unsupported",
}
ACTIONS = {
    "calculate",
    "integrate",
    "write",
    "expand",
    "divide",
    "apply",
    "add",
    "set",
    "differentiate",
    "replace",
    "check",
    "choose",
    "evaluate",
    "simplify",
}


def inspect(entries: dict[str, object]) -> list[str]:
    findings: list[str] = []
    expected = set(get_args(TextKey.__value__))
    for key in sorted(expected - entries.keys()):
        findings.append(f"{key}: critical/missing: Restore the required template.")
    for key, value in entries.items():
        if key not in expected or not isinstance(value, str) or not value.strip():
            findings.append(f"{key}: critical/type: Use a known key and nonempty text.")
            continue
        if re.search(r"[{}<>]", value):
            findings.append(
                f"{key}: critical/placeholder: Remove unsupported placeholders or markup."
            )
        if re.search(r"\b(primitive|constant of integration|obviously|trivially)\b", value, re.I):
            findings.append(
                f"{key}: critical/glossary: Use the approved mathematical term; avoid judgment."
            )
        words = re.findall(r"[A-Za-z]+", value)
        if key in INSTRUCTIONS and (not words or words[0].lower() not in ACTIONS):
            findings.append(f"{key}: critical/action: Begin with a clear approved action verb.")
        score = 100
        for sentence in re.split(r"[.!?]", value):
            if len(sentence.split()) > 20:
                score -= 25
        if not value.endswith("."):
            score -= 25
        if score < 80:
            findings.append(
                f"{key}: score/{score}: Use sentences of at most 20 words ending in a period."
            )
    return findings


def main() -> int:
    entries = json.loads(CATALOGUE.read_text())
    findings = inspect(entries)
    for finding in findings:
        print(f"backend/app/content/en.json:{finding}")
    if not findings:
        print(
            f"Content check passed: {len(entries)} templates, score >=80, no critical violations."
        )
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
