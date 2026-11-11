"""ADR-007 worksheet PDFs: one .tex file from a fixed template, one sandboxed pdflatex pass.

The template's only inputs are server-generated LaTeX (statements, answers and
solution steps from the verified catalogue, graphs from
app.services.worksheet_graphs), catalogue text and enum options; users never
type into it. pdflatex runs in a fresh child (app.services.tex_worker) with no
shell escape, paranoid file access, CPU, memory and file-size limits, a wall-clock
limit, in a new temporary directory that is deleted in every case. The log
never reaches the response.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import threading
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

WALL_SECONDS = 20.0
QUEUE_SECONDS = 10.0
MAX_PDF_BYTES = 5 * 1024 * 1024
PAPERS = {"a4": "a4paper", "letter": "letterpaper"}
# One compile at a time on the VM; the API is one process.
COMPILE_SLOT = threading.BoundedSemaphore(1)
_WORKER = (sys.executable, "-I", "-B", str(Path(__file__).with_name("tex_worker.py")))


class TexBusy(RuntimeError):
    """Another compile held the slot for longer than QUEUE_SECONDS."""


class TexRenderError(RuntimeError):
    """pdflatex failed, timed out or is missing; the message is for logs and tests only."""


@dataclass(frozen=True)
class PrintedStep:
    say: str  # catalogue text, escaped in the template
    latex: str


@dataclass(frozen=True)
class PrintedProblem:
    statement: str
    answer: str
    space_cm: float
    steps: Sequence[PrintedStep] = ()
    # A picture from app.services.worksheet_graphs, or "" for none.
    graph: str = ""
    prompt_graph: str = ""


@dataclass(frozen=True)
class PrintedGroup:
    label: str
    problems: Sequence[PrintedProblem]


_TEXT_ESCAPES = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "$": r"\$",
    "&": r"\&",
    "#": r"\#",
    "%": r"\%",
    "_": r"\_",
    "^": r"\^{}",
    "~": r"\~{}",
    # Catalogue step text names polar angles; CI compiles every step, so a new
    # character fails there first.
    "θ": r"$\theta$",
    "π": r"$\pi$",
}


def escape_text(value: str) -> str:
    """Plain text for the template; catalogue labels need it only defensively."""
    return "".join(_TEXT_ESCAPES.get(char, char) for char in value)


_PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[%(paper)s,margin=2cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{multicol}
\setlength{\parindent}{0pt}
\setlength{\columnsep}{1cm}
\pagestyle{plain}
%% Shrinks, never enlarges, math wider than the column.
\newcommand{\plfit}[2]{\resizebox{\ifdim\width>#1#1\else\width\fi}{!}{#2}}
\newcommand{\plnumber}[1]{\makebox[2em][l]{\textbf{#1.}}}
\begin{document}
{\Large\bfseries MathLoop worksheet}\hfill %(date)s\par
\vspace{0.6cm}
Name:~\rule{7cm}{0.4pt}\hfill Date:~\rule{4cm}{0.4pt}\par
\vspace{0.4cm}
"""


def _problem(number: int, problem: PrintedProblem) -> str:
    # The statement and its writing space share one unbreakable box (one page).
    prompt = (
        "\\par\\begin{center}\n" + problem.prompt_graph + "\n\\end{center}\n"
        if problem.prompt_graph
        else ""
    )
    return (
        "\\par\\noindent\\begin{minipage}{\\linewidth}\n"
        f"\\plnumber{{{number}}}"
        f"\\plfit{{\\dimexpr\\linewidth-2em\\relax}}{{$\\displaystyle {problem.statement}$}}\n"
        f"{prompt}\\par\\rule{{0pt}}{{{problem.space_cm:.2f}cm}}\n"
        "\\end{minipage}\\par\\medskip\n"
    )


def _solution(number: int, problem: PrintedProblem) -> str:
    # One unbreakable box per problem: the statement, its steps and its graph.
    fit = "\\plfit{\\dimexpr\\linewidth-2em\\relax}"
    parts = [
        "\\par\\noindent\\begin{minipage}{\\linewidth}\n",
        f"\\plnumber{{{number}}}{fit}{{$\\displaystyle {problem.statement}$}}\\par\\smallskip\n",
    ]
    for step in problem.steps:
        parts.append(
            f"\\hspace*{{2em}}\\parbox{{\\dimexpr\\linewidth-2em\\relax}}"
            f"{{\\small {escape_text(step.say)}}}\\par\n"
            f"\\hspace*{{2em}}{fit}{{$\\displaystyle {step.latex}$}}\\par\\smallskip\n"
        )
    illustration = problem.graph or problem.prompt_graph
    if illustration:
        parts.append("\\par\\smallskip\\begin{center}\n" + illustration + "\n\\end{center}\n")
    parts.append("\\end{minipage}\\par\\bigskip\n")
    return "".join(parts)


def render_tex(
    groups: Sequence[PrintedGroup],
    *,
    paper: str,
    columns: int,
    answer_key: bool,
    day: date,
    solutions: bool = False,
) -> str:
    if paper not in PAPERS or columns not in (1, 2):
        raise ValueError("Unsupported page options")
    parts = [_PREAMBLE % {"paper": PAPERS[paper], "date": day.isoformat()}]
    if columns == 2:
        # Unbalanced: problems fill the left column first, like a printed sheet.
        parts.append("\\begin{multicols*}{2}\n")
    number = 0
    answers: list[str] = []
    worked: list[str] = []
    for group in groups:
        parts.append(f"\\section*{{{escape_text(group.label)}}}\n")
        for problem in group.problems:
            number += 1
            parts.append(_problem(number, problem))
            answers.append(
                f"\\plnumber{{{number}}}"
                f"\\plfit{{\\dimexpr\\linewidth-2em\\relax}}{{${problem.answer}$}}\\par\n"
            )
            worked.append(_solution(number, problem))
    if columns == 2:
        parts.append("\\end{multicols*}\n")
    if answer_key and answers:
        parts.append("\\clearpage\n\\section*{Answers}\n\\begin{multicols}{2}\\small\n")
        parts.extend(answers)
        parts.append("\\end{multicols}\n")
    if solutions and worked:
        parts.append("\\clearpage\n\\section*{Solutions}\n")
        parts.extend(worked)
    parts.append("\\end{document}\n")
    return "".join(parts)


def _pdflatex() -> str:
    path = shutil.which("pdflatex", path="/usr/bin:/bin:/usr/local/bin")
    if path is None:
        raise TexRenderError("pdflatex is not installed")
    return path


def _log_tail(directory: Path) -> str:
    try:
        lines = (directory / "worksheet.log").read_text("utf-8", "replace").splitlines()
    except OSError:
        return ""
    # From the first error on, which names the failing line of worksheet.tex.
    start = next((i for i, line in enumerate(lines) if line.startswith("!")), len(lines) - 20)
    return "\n".join(lines[max(start, 0) : start + 20])


def _run(tex: str, directory: Path) -> bytes:
    if not sys.platform.startswith("linux"):
        raise TexRenderError("The resource-limited TeX worker requires Linux")
    (directory / "worksheet.tex").write_text(tex, "utf-8")
    argv = (
        _pdflatex(),
        "-no-shell-escape",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-no-mktex=tfm",
        "-no-mktex=pk",
        "-output-directory=" + str(directory),
        "worksheet.tex",
    )
    env = {
        "PATH": "/usr/bin:/bin",
        "HOME": str(directory),
        "LANG": "C.UTF-8",
        # kpathsea: no reads of dot files or paths outside the TeX tree and this
        # directory, no writes outside it, and no shell escape whatever the config.
        "openin_any": "p",
        "openout_any": "p",
        "shell_escape": "f",
        "TEXMFOUTPUT": str(directory),
        "TEXMFVAR": str(directory / "texmf-var"),
    }
    try:
        # Fixed trusted argv and environment, no shell; the input is the file above.
        process = subprocess.run(  # noqa: S603
            (*_WORKER, *argv),
            cwd=directory,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=WALL_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        # subprocess.run kills and reaps the child before raising.
        raise TexRenderError("pdflatex exceeded its wall-clock limit") from exc
    except OSError as exc:
        raise TexRenderError("pdflatex could not run") from exc
    pdf = directory / "worksheet.pdf"
    if process.returncode != 0 or not pdf.is_file():
        raise TexRenderError(f"pdflatex failed ({process.returncode}):\n{_log_tail(directory)}")
    data = pdf.read_bytes()
    if len(data) > MAX_PDF_BYTES or not data.startswith(b"%PDF-"):
        raise TexRenderError("pdflatex produced no usable PDF")
    return data


def compile_pdf(tex: str, *, queue_seconds: float = QUEUE_SECONDS) -> bytes:
    """The PDF bytes, or TexBusy / TexRenderError. Leaves no files behind."""
    if not COMPILE_SLOT.acquire(timeout=queue_seconds):
        raise TexBusy("A worksheet is already compiling")
    try:
        directory = Path(tempfile.mkdtemp(prefix="mathloop-tex-"))
        try:
            return _run(tex, directory)
        finally:
            shutil.rmtree(directory, ignore_errors=True)
    finally:
        COMPILE_SLOT.release()


def filename(day: date) -> str:
    return f"mathloop-worksheet-{day.isoformat()}.pdf"
