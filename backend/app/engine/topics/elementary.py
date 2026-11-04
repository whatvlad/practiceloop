"""Views in existing practice areas; no source-document topic bank."""

from app.engine.generators.elementary import SPECS

NEW_TOPICS = {
    "logic-and-propositions": ("Logic and propositions", "mathematical-analysis"),
    "real-inequalities": ("Real inequalities", "algebra"),
    "exponential-and-logarithmic": (
        "Exponential and logarithmic equations",
        "mathematical-analysis",
    ),
    "trigonometric-functions": ("Trigonometric functions and equations", "mathematical-analysis"),
}


def placement(template: str) -> str:
    if template.startswith(("trig-", "inverse-trig-")):
        return "trigonometric-functions"
    if template.startswith(("domain-", "composition-", "inverse-")) or template == "parity":
        return "functions-and-sequences"
    if (
        template.startswith(("proposition", "logic-", "quantifier-"))
        or template == "compound-truth"
    ):
        return "logic-and-propositions"
    if template.startswith("equation-"):
        return "polynomial-roots"
    if template.startswith("inequality-"):
        return "real-inequalities"
    return "exponential-and-logarithmic"


ADDITIONS: dict[str, dict[int, tuple[str, ...]]] = {}
for template, level, _, _ in SPECS:
    levels = ADDITIONS.setdefault(placement(template), {})
    levels[level] = (*levels.get(level, ()), f"elementary-{template}-v1")
