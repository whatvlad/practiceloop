"""#101: ADR-005 equivalence of a partial-derivative answer. Runs only in the worker.

The answer is an expression in the variables the template declares, each with
its real domain (`r > 0`, `y > 0` where the template says so). Symbolic proof
decides `correct`; exact evaluation at sample points of the domain can only
certify a difference. A symbol the template does not declare is `invalid`, so
an answer written in x, y where r, θ is asked is rejected, as ADR-005 says.
"""

from __future__ import annotations

from typing import Any, Literal

import sympy as sp

from app.generators.partial import PartialProblem

type Outcome = Literal["correct", "incorrect", "invalid", "inconclusive"]

_PRECISION = 50
_TOLERANCE = sp.Float("1e-12", _PRECISION)
# Exact rational points away from 0 and from the multiples of π/4 the templates use.
# Each variable gets its own sequence, so no point lies on a line such as x = y.
_REAL_SAMPLES = (
    ("-1.3", "0.35", "1.15", "2.6", "-0.45", "1.7"),
    ("0.8", "-2.1", "1.45", "-0.6", "2.35", "0.55"),
    ("1.9", "-0.75", "-1.55", "0.65", "2.2", "-0.3"),
)
_POSITIVE_SAMPLES = (
    ("0.35", "1.15", "2.6", "0.8", "1.7", "2.35"),
    ("1.45", "0.55", "2.2", "1.9", "0.65", "1.3"),
)


def _declared(answer: Any, problem: PartialProblem) -> Any | None:
    """Rename the learner's real symbols to the template's, or None for an unknown one."""
    names = {variable.name: variable for variable in problem.variables}
    replacements = {}
    for symbol in answer.free_symbols:
        if symbol.name not in names:
            return None
        replacements[symbol] = names[symbol.name]
    return answer.xreplace(replacements)


def _points(problem: PartialProblem) -> list[dict[Any, Any]]:
    sequences = []
    for index, variable in enumerate(problem.variables):
        table = _POSITIVE_SAMPLES if variable.is_positive else _REAL_SAMPLES
        sequences.append(table[index % len(table)])
    return [
        {v: sp.Rational(s[k]) for v, s in zip(problem.variables, sequences, strict=True)}
        for k in range(len(sequences[0]))
    ]


def _differs(expression: Any, problem: PartialProblem) -> bool:
    """A certified nonzero, undefined or non-real value at some sample point."""
    for point in _points(problem):
        value = expression.evalf(_PRECISION, subs=point)
        if value.has(sp.nan, sp.zoo, sp.oo, -sp.oo) or not value.is_number:
            return True
        if abs(value) > _TOLERANCE:
            return True
    return False


def classify(answer: Any, problem: PartialProblem) -> Outcome:
    """`answer` is the evaluated SymPy form of a parsed learner expression."""
    if answer.has(sp.nan, sp.zoo, sp.oo, -sp.oo):
        return "invalid"
    renamed = _declared(answer, problem)
    if renamed is None:
        return "invalid"
    difference = renamed - problem.answer
    if sp.simplify(difference) == 0:
        return "correct"
    if _differs(difference, problem):
        return "incorrect"
    return "inconclusive"


def diagnose(answer: Any, problem: PartialProblem) -> str | None:
    """The one declared mistake an incorrect answer matches, or None for a general hint.

    Several wrong answers may share one code (each dropped chain-rule term);
    two different codes, or no proven match, give no diagnosis.
    """
    renamed = _declared(answer, problem)
    if renamed is None:
        return None
    codes = {code for code, wrong in problem.mistakes if sp.simplify(renamed - wrong) == 0}
    return codes.pop() if len(codes) == 1 else None
