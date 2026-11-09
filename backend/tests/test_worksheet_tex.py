"""Real pdflatex runs for worksheets (#116, ADR-007). CI's "Worksheet TeX" job runs them.

Needs the VM's TeX packages (texlive-latex-base, texlive-latex-recommended,
texlive-fonts-recommended, lmodern) and poppler-utils for pdftotext:
python -m pytest -m tex
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest
from engine_fixtures import catalogue

from app.api.practice import TOPICS
from app.engine.practice import ENGINE_TOPICS
from app.engine.practice import pool as engine_pool
from app.engine.practice import public_replay as replay
from app.services import worksheet_pdf
from app.services.worksheet_graphs import graph
from app.services.worksheet_pdf import (
    PrintedGroup,
    PrintedProblem,
    PrintedStep,
    TexBusy,
    TexRenderError,
    compile_pdf,
    render_tex,
)
from app.services.worksheets import catalogue_records
from app.visuals.spec import build_visual

pytestmark = pytest.mark.tex
DAY = date(2026, 10, 22)


@pytest.fixture(autouse=True)
def scratch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Every compile directory goes here, so a test can prove none is left behind."""
    if shutil.which("pdflatex") is None:
        pytest.fail("pdflatex is required for -m tex")
    root = tmp_path / "tex"
    root.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(root))
    yield root
    assert list(root.iterdir()) == []


def document(body: str) -> str:
    return "\\documentclass{article}\n\\begin{document}\n" + body + "\n\\end{document}\n"


def poppler(tool: str, pdf: bytes, tmp_path: Path, *after: str) -> str:
    """A poppler-utils tool's output for this PDF; `after` follows the file name."""
    path = tmp_path / "out.pdf"
    path.write_bytes(pdf)
    result = subprocess.run(  # noqa: S603 - fixed argv in a test
        [tool, str(path), *after],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def text(pdf: bytes, tmp_path: Path) -> list[str]:
    """Each page's text, via pdftotext."""
    return poppler("pdftotext", pdf, tmp_path, "-").split("\f")[:-1]


def sample(answer_key: bool = True, **options: object) -> str:
    groups = [
        PrintedGroup(
            "Substitution, level 3",
            [
                PrintedProblem(e.statement, e.answer_latex, 6)
                for e in catalogue("substitution", 3)[:2]
            ],
        ),
        PrintedGroup(
            "Triple integrals, level 3",
            [
                PrintedProblem(e.statement, e.answer_latex, 10.5)
                for e in catalogue("triple-integrals", 3)[:2]
            ],
        ),
    ]
    settings: dict[str, object] = {"paper": "a4", "columns": 1}
    settings.update(options)
    return render_tex(groups, answer_key=answer_key, day=DAY, **settings)  # type: ignore[arg-type]


def test_every_catalogue_statement_and_answer_compiles() -> None:
    """A macro only KaTeX knows fails here, before it can reach a worksheet."""
    groups = [
        PrintedGroup(
            f"{topic.name}, level {level}",
            [PrintedProblem(e.statement, e.answer_latex, 0) for e in catalogue(slug, level)],
        )
        for slug, topic in TOPICS.items()
        if slug not in ENGINE_TOPICS
        for level in topic.levels
    ]
    for slug, topic in ENGINE_TOPICS.items():
        for level in topic.levels:
            groups.append(
                PrintedGroup(
                    f"{topic.title}, level {level}",
                    [
                        PrintedProblem(p.statement, p.answer_latex, 0)
                        for p in engine_pool(slug, level)
                    ],
                )
            )
    assert sum(len(group.problems) for group in groups) > 500
    try:
        pdf = compile_pdf(render_tex(groups, paper="a4", columns=2, answer_key=True, day=DAY))
    except TexRenderError as error:
        pytest.fail(f"A catalogue statement or answer does not compile:\n{error}")
    assert pdf.startswith(b"%PDF-")


def steps(exercise: object) -> list[PrintedStep]:
    return [PrintedStep(s["say"], s["latex"]) for s in exercise.steps]  # type: ignore[attr-defined]


@pytest.mark.parametrize("slug", [slug for slug in TOPICS if slug not in ENGINE_TOPICS])
def test_every_catalogue_solution_compiles(slug: str) -> None:
    """#130: every step's text and LaTeX, one topic per document to stay inside the limits."""
    groups = [
        PrintedGroup(
            f"{TOPICS[slug].name}, level {level}",
            [
                PrintedProblem(e.statement, e.answer_latex, 0, steps(e))
                for e in catalogue(slug, level)
            ],
        )
        for level in TOPICS[slug].levels
    ]
    tex = render_tex(groups, paper="a4", columns=1, answer_key=False, day=DAY, solutions=True)
    try:
        pdf = compile_pdf(tex)
    except TexRenderError as error:
        pytest.fail(f"A catalogue solution step does not compile:\n{error}")
    assert pdf.startswith(b"%PDF-")


def test_graphs_of_every_visual_version_compile_beside_their_steps(tmp_path: Path) -> None:
    first: dict[tuple[object, int], dict[str, object]] = {}
    for slug, topic in TOPICS.items():
        if ENGINE_TOPICS[slug].visual is None:
            continue
        for level in topic.levels:
            for record in catalogue_records(slug, level):
                if build_visual(record) is not None:
                    first.setdefault((record["generator_version"], level), record)
    problems = []
    for record in first.values():
        exercise = replay(record)
        picture = graph(build_visual(record))
        problems.append(
            PrintedProblem(exercise.statement, exercise.answer_latex, 0, steps(exercise), picture)
        )
    tex = render_tex(
        [PrintedGroup("Graphs", problems)], paper="a4", columns=1, answer_key=True, day=DAY,
        solutions=True,
    )  # fmt: skip
    assert tex.count("\\pdfliteral") == len(problems) > 10
    pages = text(compile_pdf(tex), tmp_path)
    solutions = "".join(pages[next(i for i, p in enumerate(pages) if "Solutions" in p) :])
    for caption in ("shaded area", "antiderivative", "region of integration", "solid"):
        assert caption in solutions


def test_labels_numbering_and_answers_on_their_own_last_page(tmp_path: Path) -> None:
    pages = text(compile_pdf(sample()), tmp_path)
    whole = "".join(pages[:-1])
    assert "MathLoop worksheet" in pages[0] and "2026-10-22" in pages[0]
    assert "Name:" in pages[0]
    assert whole.index("Substitution, level 3") < whole.index("Triple integrals, level 3")
    for number in ("1.", "2.", "3.", "4."):
        assert number in whole
    assert "Answers" in pages[-1] and "Answers" not in whole
    assert "+C" in pages[-1].replace(" ", "")


def test_no_answer_section_without_the_key(tmp_path: Path) -> None:
    pages = text(compile_pdf(sample(answer_key=False)), tmp_path)
    assert not any("Answers" in page for page in pages)
    assert not any("+C" in page.replace(" ", "") for page in pages)


@pytest.mark.parametrize(("paper", "size"), [("a4", "595.276 x 841.89"), ("letter", "612 x 792")])
@pytest.mark.parametrize("columns", [1, 2])
def test_paper_and_columns(paper: str, size: str, columns: int, tmp_path: Path) -> None:
    info = poppler("pdfinfo", compile_pdf(sample(paper=paper, columns=columns)), tmp_path)
    assert f"{size} pts" in " ".join(info.split())


def test_a_failed_compile_is_an_error_and_leaves_no_files() -> None:
    with pytest.raises(TexRenderError, match="Undefined control sequence"):
        compile_pdf(document("$\\katexonlymacro{x}$"))


def test_a_compile_over_the_wall_clock_limit_is_stopped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(worksheet_pdf, "WALL_SECONDS", 1.0)
    with pytest.raises(TexRenderError, match="wall-clock"):
        compile_pdf(document("\\def\\spin{\\spin}\\spin"))


def test_a_runaway_compile_hits_the_cpu_limit() -> None:
    # 10 s of CPU, inside the 20 s wall clock: the child is killed by RLIMIT_CPU.
    with pytest.raises(TexRenderError, match="failed"):
        compile_pdf(document("\\def\\spin{\\spin}\\spin"))


def test_shell_escape_and_outside_files_are_refused(tmp_path: Path) -> None:
    outside = tmp_path / "outside.txt"
    with pytest.raises(TexRenderError):
        compile_pdf(document(f"\\immediate\\write18{{touch {outside}}}x\\input{{{outside}}}"))
    assert not outside.exists()
    with pytest.raises(TexRenderError):
        compile_pdf(
            document(f"\\newwrite\\f\\immediate\\openout\\f={outside}\\immediate\\write\\f{{x}}")
        )
    assert not outside.exists()
    secret = tmp_path / "secret.tex"
    secret.write_text("SECRET")
    with pytest.raises(TexRenderError):
        compile_pdf(document(f"\\input{{{secret}}}"))


def test_one_compile_at_a_time(monkeypatch: pytest.MonkeyPatch) -> None:
    assert worksheet_pdf.COMPILE_SLOT.acquire(blocking=False)
    try:
        with pytest.raises(TexBusy):
            compile_pdf(document("x"), queue_seconds=0.1)
    finally:
        worksheet_pdf.COMPILE_SLOT.release()
    assert compile_pdf(document("x")).startswith(b"%PDF-")


@pytest.mark.parametrize("slug", sorted(ENGINE_TOPICS))
def test_every_engine_pool_solution_compiles(slug: str) -> None:
    groups = [
        PrintedGroup(
            f"{TOPICS[slug].name}, level {level}",
            [
                PrintedProblem(p.statement, p.answer_latex, 0, steps(p.issued()))
                for p in engine_pool(slug, level)
            ],
        )
        for level in TOPICS[slug].levels
    ]
    source = render_tex(groups, paper="a4", columns=1, answer_key=True, day=DAY, solutions=True)
    assert compile_pdf(source).startswith(b"%PDF-")
