"""#130: static worksheet graphs drawn from ADR-006 specs, without TeX."""

from __future__ import annotations

import re

import pytest

from app.api.practice import TOPICS
from app.engine.practice import ENGINE_TOPICS
from app.services.worksheet_graphs import DRAWERS, graph, nice_ticks
from app.services.worksheets import catalogue_records
from app.visuals.spec import build_visual

# The PDF path, painting and graphics-state operators the drawer emits.
_NUMBER = re.compile(r"\[?-?[\d.]*\]?")
_OPERATORS = {"q", "Q", "m", "l", "c", "h", "S", "f", "B", "re", "W", "n", "w", "J", "j",
              "d", "g", "G"}  # fmt: skip


def first_records() -> list[dict[str, object]]:
    """The first record of every generator version with a visual, at every level."""
    first: dict[tuple[object, int], dict[str, object]] = {}
    for slug, topic in TOPICS.items():
        if ENGINE_TOPICS[slug].visual is None:
            continue
        for level in topic.levels:
            for record in catalogue_records(slug, level):
                if (record["generator_version"], level) not in first:
                    first.setdefault((record["generator_version"], level), record)
    return [record for record in first.values() if build_visual(record) is not None]


def literals(picture: str) -> list[str]:
    return re.findall(r"\\pdfliteral\{([^}]*)\}", picture)


def test_every_served_visual_kind_has_a_drawer() -> None:
    kinds = {build_visual(record)["kind"] for record in first_records()}  # type: ignore[index]
    assert kinds == {"definite", "indefinite", "region2d", "solid3d", "plot2d"}
    # A reusable visual can precede its curriculum consumer (#234). Its own
    # renderer/print tests live with the computational extension provider.
    assert kinds <= set(DRAWERS)


@pytest.mark.parametrize("record", first_records(), ids=lambda r: str(r["generator_version"]))
def test_a_graph_is_a_picture_of_pdf_operators_and_math_labels(record: dict[str, object]) -> None:
    picture = graph(build_visual(record))
    assert picture.startswith("{\\setlength{\\unitlength}{1bp}\\begin{picture}(")
    assert "\\end{picture}}" in picture and "\\footnotesize" in picture
    [literal] = literals(picture)
    words = {word for word in literal.split() if not _NUMBER.fullmatch(word)}
    assert words <= _OPERATORS, words - _OPERATORS
    # Every label is a zero-size box of math, so it cannot break the picture.
    box = r"\\put\([^)]*\)\{\\makebox\(0,0\)\[\w*\]\{\\scriptsize\$[^$]*\$\}\}"
    labels = re.findall(box, picture)
    assert len(labels) == picture.count("\\makebox")


def test_no_visual_means_no_graph() -> None:
    record = catalogue_records("derivatives", 1)[0]
    assert build_visual(record) is None
    assert graph(None) == ""
    with pytest.raises(ValueError):
        graph({"kind": "unknown"})


@pytest.mark.parametrize(
    ("low", "high", "ticks"),
    [
        (-2.0, 2.0, [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]),
        (-6.4, 6.4, [-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0]),
        (0.0, 30.0, [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]),
        (1.0, 1.0, []),
    ],
)
def test_ticks_are_round_numbers_inside_the_window(
    low: float, high: float, ticks: list[float]
) -> None:
    assert nice_ticks(low, high) == ticks
