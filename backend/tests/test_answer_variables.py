"""ADR-005 answer variables: y, z, r and theta, only where a template declares them."""

from __future__ import annotations

import subprocess
import sys
import time
from typing import Any

import pytest
import sympy as sp
from engine_fixtures import check, native_record

from app.engine import practice as engine
from app.engine.answers._symbolic import variable_symbol
from app.engine.answers.expression import ExpressionAnswer
from app.math_input import (
    MathInputError,
    MathInputTooLong,
    declared_variables,
    parse_math_input,
)
from app.services import math_worker
from app.services.math_worker import AnswerCheck, build_expression, check_answer, record_variables

linux_only = pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux worker")

X, Y, Z, THETA = (sp.Symbol(name, real=True) for name in ("x", "y", "z", "theta"))
R = sp.Symbol("r", real=True)
XY = {"x", "y"}
XYZ = {"x", "y", "z"}
POLAR = {"r", "theta"}
CYLINDRICAL = {"r", "theta", "z"}
COMPLEX = {"i"}  # #221: the imaginary unit


def tree(source: str, variables: set[str]) -> Any:
    return build_expression(parse_math_input(source, variables))


# Shared with frontend/src/answerSyntax.test.ts (VARIABLE_SUPPORTED).
@pytest.mark.parametrize(
    ("source", "variables", "expected"),
    [
        # The implicit-multiplication rule: a letter run splits into the longest names.
        ("2xy", XY, 2 * X * Y),
        ("x y", XY, X * Y),
        ("xy^2", XY, X * Y**2),
        ("2r", POLAR, 2 * R),
        ("r theta", POLAR, R * THETA),
        ("rtheta", POLAR, R * THETA),
        ("rθ", POLAR, R * THETA),
        ("2r θ^2", POLAR, 2 * R * THETA**2),
        ("rcos(theta)", POLAR, R * sp.cos(THETA)),
        ("r^2sin(θ)cos(θ)", POLAR, R**2 * sp.sin(THETA) * sp.cos(THETA)),
        ("xsin(y)", XY, X * sp.sin(Y)),
        ("ye^(xy)", XY, Y * sp.exp(X * Y)),
        ("e^(xy)", XY, sp.exp(X * Y)),
        ("ex", XY, sp.E * X),
        ("pixy", XY, sp.pi * X * Y),
        ("exp(x)y", XY, sp.exp(X) * Y),
        ("xyz", XYZ, X * Y * Z),
        ("2x*y + y/z", XYZ, 2 * X * Y + Y / Z),
        ("r^2 z", CYLINDRICAL, R**2 * Z),
        ("θ - theta", POLAR, sp.Integer(0)),
        ("sqrt(x^2 + y^2)", XY, sp.sqrt(X**2 + Y**2)),
        ("ln|xy|", XY, sp.log(sp.Abs(X * Y))),
        ("atan(y/x)", XY, sp.atan(Y / X)),
        ("sec^2(xy)", XY, sp.sec(X * Y) ** 2),
        ("3pi/4", POLAR, 3 * sp.pi / 4),
        ("y²x³", XY, Y**2 * X**3),
        ("3-4i", COMPLEX, 3 - 4 * sp.I),
        ("2i-1", COMPLEX, 2 * sp.I - 1),
        ("sqrt(3)/2+i/2", COMPLEX, sp.sqrt(3) / 2 + sp.I / 2),
        ("i^2", COMPLEX, sp.Integer(-1)),
    ],
)
def test_declared_variables_are_read(source: str, variables: set[str], expected: Any) -> None:
    assert sp.simplify(tree(source, variables) - expected) == 0


# Shared with frontend/src/answerSyntax.test.ts (VARIABLE_REJECTED).
@pytest.mark.parametrize(
    ("source", "variables"),
    [
        ("x + y", POLAR),  # an answer in r, θ does not accept x, y
        ("r", XY),
        ("theta", XY),
        ("z", XY),
        ("x + C", XY),  # no arbitrary constant outside integration topics
        ("a", XY),
        ("xa", XY),
        ("xq", XY),
        ("t", POLAR),
        ("thet", POLAR),
        ("x(y+1)", XY),  # a letter before a bracket still reads as a function call
        ("x^y", XY),
        ("r^theta", POLAR),
        ("sin xy", XY),
        ("y(x)", XY),
        ("2 3x", XY),
        ("x**y", XY),
        ("1e3x", XY),
        ("α", POLAR),
        ("i*x", XY),
        ("x+i", COMPLEX),
        ("3+4j", COMPLEX),
        ("3+4I", COMPLEX),
        ("2^i", COMPLEX),
    ],
)
def test_other_symbols_are_invalid(source: str, variables: set[str]) -> None:
    with pytest.raises(MathInputError):
        parse_math_input(source, variables)


@pytest.mark.parametrize("source", ["y + z", "xy", "2xy", "r theta", "θ", "theta", "x y z"])
def test_integration_grammar_is_unchanged_without_a_declaration(source: str) -> None:
    with pytest.raises(MathInputError):
        parse_math_input(source)


def test_integration_constant_still_works_without_a_declaration() -> None:
    assert parse_math_input("x + C") == parse_math_input("x+C")


def test_theta_and_greek_theta_read_the_same() -> None:
    assert parse_math_input("r θ", POLAR) == parse_math_input("r theta", POLAR)
    assert parse_math_input("ϑ", POLAR) == parse_math_input("theta", POLAR)


def test_declarations_are_validated() -> None:
    assert declared_variables({"r": "positive", "theta": "real"}) == {
        "r": "positive",
        "theta": "real",
    }
    for bad in ({}, {"r": "real"}, {"theta": "positive"}, {"w": "real"}, ["x"], None):
        with pytest.raises(ValueError):
            declared_variables(bad)
    with pytest.raises(ValueError):
        parse_math_input("w", {"w"})


# Every parser limit, reached through the new variables (adversarial corpus).
@pytest.mark.parametrize(
    ("source", "variables", "message"),
    [
        ("xy" * 65, XY, "tokens"),
        ("+".join("r" for _ in range(65)), POLAR, "tokens"),
        ("+".join("r" for _ in range(49)), POLAR, "nodes"),
        ("xy" * 24 + "x", XY, "nodes"),
        ("(" * 13 + "theta" + ")" * 13, POLAR, "nesting"),
        ("+".join("sin(xy)" for _ in range(17)), XY, "function"),
        ("123456789y", XY, "Numeric literal"),
        ("1.1234567r", POLAR, "Numeric literal"),
        ("y^13", XY, "Exponent"),
        ("theta^(1/13)", POLAR, "Exponent"),
        ("sin^13(r)", POLAR, "Exponent"),
        ("e^(z^13)", XYZ, "Exponent"),
        ("|x + |y||", XY, "Nested"),
        ("y/0", XY, "Division by zero"),
        ("x^(y)", XY, "Variable exponents"),
    ],
)
def test_limits_hold_with_variables(source: str, variables: set[str], message: str) -> None:
    with pytest.raises(MathInputError, match=message):
        parse_math_input(source, variables)


def test_input_length_counts_theta_as_written_out() -> None:
    # θ becomes `theta`, so 52 of them are 260 bytes: over the 256-byte limit.
    with pytest.raises(MathInputTooLong):
        parse_math_input("θ" * 52, POLAR)
    with pytest.raises(MathInputTooLong):
        parse_math_input("x" * 257, XY)


@pytest.mark.parametrize(
    "source",
    [
        "xy" * 24,
        "+".join("theta" for _ in range(42)),
        "(" * 12 + "theta" + ")" * 12,
        "+".join("sin(xy)" for _ in range(16)),
        "12345678y",
        "y^12",
        "r^(-12)",
        "theta^(1/12)",
    ],
)
def test_exact_boundaries_remain_accepted_with_variables(source: str) -> None:
    parse_math_input(source, {"x", "y", "r", "theta"})


def problem(expected: Any, **variables: Any) -> ExpressionAnswer:
    return ExpressionAnswer(expected, variables)


def symbols(**variables: Any) -> list[Any]:
    return [variable_symbol(name, domain) for name, domain in variables.items()]


def _partial_xy() -> ExpressionAnswer:
    x, y = symbols(x="real", y="real")
    return problem(y * sp.cos(x * y), x="real", y="real")


def _polar() -> ExpressionAnswer:
    r, theta = symbols(r="positive", theta="real")
    return problem(r * sp.cos(theta) ** 2, r="positive", theta="real")


def _log_positive() -> ExpressionAnswer:
    x, y = symbols(x="positive", y="real")
    return problem(2 * sp.log(x) + y, x="positive", y="real")


def _log_real() -> ExpressionAnswer:
    x, y = symbols(x="real", y="real")
    return problem(sp.log(x**2) + y, x="real", y="real")


def _cylindrical() -> ExpressionAnswer:
    r, theta, z = symbols(r="positive", theta="real", z="real")
    return problem(z * r**2 * sp.sin(theta), r="positive", theta="real", z="real")


@pytest.mark.parametrize(
    ("make", "variables", "answer", "expected"),
    [
        (_partial_xy, XY, "y cos(xy)", "correct"),
        (_partial_xy, XY, "cos(x*y)*y", "correct"),
        (_partial_xy, XY, "x cos(xy)", "incorrect"),
        (_partial_xy, XY, "cos(xy)", "incorrect"),
        (_partial_xy, XY, "y cos(yx) + 0x", "correct"),
        (_polar, POLAR, "r cos^2(theta)", "correct"),
        (_polar, POLAR, "r*(1 + cos(2θ))/2", "correct"),
        (_polar, POLAR, "sqrt(r^2) cos^2(θ)", "correct"),  # r > 0
        (_polar, POLAR, "|r| cos^2(theta)", "correct"),
        (_polar, POLAR, "r - r sin^2(theta)", "correct"),
        (_polar, POLAR, "r sin^2(theta)", "incorrect"),
        (_polar, POLAR, "r cos(theta)", "incorrect"),
        (_log_positive, XY, "ln(x^2) + y", "correct"),  # same on x > 0
        (_log_real, XY, "2ln(x) + y", "incorrect"),  # not real for x < 0
        # SymPy cannot prove ln(x²) = 2ln|x|: undecided is inconclusive, never a guess.
        (_log_real, XY, "2ln|x| + y", "inconclusive"),
        (_log_real, XY, "ln(x^2) + y", "correct"),
        (_cylindrical, CYLINDRICAL, "r^2 z sin(θ)", "correct"),
        (_cylindrical, CYLINDRICAL, "r z sin(θ)", "incorrect"),
        (_partial_xy, XY, "y cos(xy) + 0/(y - y)", "invalid"),
    ],
)
def test_equivalence_on_the_declared_domain(
    make: Any, variables: set[str], answer: str, expected: str
) -> None:
    assert check(parse_math_input(answer, variables), make()) == expected


@pytest.mark.parametrize(
    ("make", "variables", "answer"),
    [
        (_partial_xy, XY, "y cos(xy)"),
        (_partial_xy, XY, "x y^2 e^(xy) sin(x)"),
        (_polar, POLAR, "r*(1 + cos(2θ))/2"),
        (_polar, POLAR, "r cos^2(theta) + (sin^2(theta) + cos^2(theta) - 1)r"),
        (_log_real, XY, "2ln|x| + y"),  # the slowest: undecided after sampling
        (_cylindrical, CYLINDRICAL, "r^2 z sin(θ)"),
        (_cylindrical, CYLINDRICAL, "z r^2 (2 sin(θ/2) cos(θ/2))"),
    ],
)
def test_representative_checks_fit_half_the_worker_cpu_limit(
    make: Any, variables: set[str], answer: str
) -> None:
    # ADR-005 check budget: at most 1 s CPU in CI, half the worker's 2 s limit.
    started = time.process_time()
    check(parse_math_input(answer, variables), make())
    assert time.process_time() - started < math_worker.CPU_SECONDS / 2


ADVERSARIAL = [
    ("e^(e^(e^(e^(xy))))", XY),
    ("(x+y)^12 * (x-y)^12 * (x+2y)^12", XY),
    ("sin(" * 12 + "r theta" + ")" * 12, POLAR),
    ("((r+theta)^12 + 1)^12", POLAR),
    ("e^(x^12 y^12) * sin(x^12) * cos(y^12) * tan(x y)", XY),
    ("abs(abs(abs(abs(r - 1) - theta) - 3) - z)", CYLINDRICAL),
    ("sqrt(sqrt(sqrt(sqrt(sqrt(sqrt(x^12 + y^12 + z^12))))))", XYZ),
    ("ln(abs(ln(abs(ln(abs(xyz))))))", XYZ),
]

_LIMITED_CHECK = """
import sys
from app.services.math_worker import _apply_limits
_apply_limits()
import sympy as sp
from app.engine.answers.expression import ExpressionAnswer
from app.engine.answers._symbolic import variable_symbol
from app.math_input import parse_math_input
names = sys.argv[2].split(",")
domains = {name: "positive" if name == "r" else "real" for name in names}
expected = sp.Add(*(variable_symbol(name, domain) for name, domain in domains.items()))
print(ExpressionAnswer(expected, domains).check(parse_math_input(sys.argv[1], names)))
"""


@linux_only
@pytest.mark.parametrize(("answer", "variables"), ADVERSARIAL)
def test_adversarial_multivariable_answers_end_within_the_worker_limits(
    answer: str, variables: set[str]
) -> None:
    started = time.monotonic()
    result = subprocess.run(  # noqa: S603 - fixed trusted argv, no shell
        (sys.executable, "-B", "-c", _LIMITED_CHECK, answer, ",".join(sorted(variables))),
        capture_output=True,
        timeout=math_worker.WALL_SECONDS + 3,
        check=False,
    )
    assert time.monotonic() - started < math_worker.WALL_SECONDS + 3
    # A decided result, or the CPU/memory limit stopping the child: never a hang.
    if result.returncode == 0:
        assert result.stdout.strip() in {b"correct", b"incorrect", b"invalid", b"inconclusive"}
    assert b"ModuleNotFoundError" not in result.stderr and b"ImportError" not in result.stderr


@linux_only
def test_public_expression_checker_starts_under_the_limits() -> None:
    result = subprocess.run(  # noqa: S603 - fixed trusted test script
        (sys.executable, "-B", "-c", _LIMITED_CHECK, "x+y", "x,y"),
        capture_output=True,
        timeout=math_worker.WALL_SECONDS,
        check=False,
    )
    assert result.returncode == 0 and result.stdout.strip() == b"correct", result.stderr


def test_record_variables_are_read_and_validated() -> None:
    assert record_variables(native_record("basic", "power")) is None
    record = engine.issue("partial-derivatives", 4, seed=199).record
    variables = record_variables(record)
    assert variables["r"] == "positive" and variables["theta"] == "real"
    assert set(variables) <= {"r", "theta", "z"}
    with pytest.raises(ValueError):
        record_variables({**record, "variables": {"r": "real"}})


def test_answers_are_parsed_with_the_record_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_args: Any, **_kwargs: Any) -> None:
        pytest.fail("worker started for an undeclared variable")

    monkeypatch.setattr(math_worker.subprocess, "Popen", forbidden)
    record = engine.issue("partial-derivatives", 4, seed=199).record
    assert check_answer("x + y", record) == AnswerCheck("invalid")
    with pytest.raises(ValueError):
        check_answer("r", {**record, "variables": {"r": "real"}})


@linux_only
def test_a_record_whose_variables_differ_from_its_template_cannot_be_replayed() -> None:
    record = {
        **native_record("basic", "power", 2, power=3),
        "variables": {"x": "real", "y": "real"},
    }
    with pytest.raises(ValueError):
        check_answer("2xy", record)
