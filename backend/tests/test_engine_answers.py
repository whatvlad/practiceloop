"""Checks for new-engine answers and their worker boundary."""

import subprocess
import sys
import time
from fractions import Fraction

import pytest
import sympy as sp

from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.engine.answers.derivative import DerivativeAnswer
from app.engine.answers.expression import ExpressionAnswer
from app.engine.answers.number import NumberAnswer
from app.engine.models import Answer
from app.services.math_parser import parse_math_input

X = sp.Symbol("x", real=True)
Y = sp.Symbol("y", real=True)
NONZERO = sp.Union(sp.Interval.open(-sp.oo, 0), sp.Interval.open(0, sp.oo))


@pytest.mark.parametrize("source", ["1/2", "2/4", "0.5", "(1+2)/6", "sqrt(1)/2"])
def test_number_compares_exact_rationals(source: str) -> None:
    answer: Answer = NumberAnswer(Fraction(1, 2))
    assert answer.check(parse_math_input(source)) == "correct"
    assert answer.latex() == r"\frac{1}{2}"


def test_number_rejects_wrong_undefined_and_nonreal_values() -> None:
    answer = NumberAnswer(2)
    assert answer.check(parse_math_input("1.999999")) == "incorrect"
    assert answer.check(parse_math_input("0*ln(0)+2")) == "invalid"
    assert answer.check(parse_math_input("x+0*ln(0)")) == "invalid"
    assert answer.check(parse_math_input("sqrt(-4)")) == "incorrect"
    assert answer.check(parse_math_input("((10000000^12)^12)^12")) == "inconclusive"


@pytest.mark.parametrize("source", ["pi", "ln(2)", "x-x+2", "sqrt(2)"])
def test_number_does_not_guess_about_symbolic_forms(source: str) -> None:
    assert NumberAnswer(2).check(parse_math_input(source)) == "inconclusive"


def test_number_can_be_imported_without_sympy() -> None:
    result = subprocess.run(  # noqa: S603 - fixed trusted command; no shell
        (
            sys.executable,
            "-c",
            "from app.engine.answers.number import NumberAnswer; "
            "import sys; assert 'sympy' not in sys.modules",
        ),
        capture_output=True,
        timeout=5,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")


def test_answer_types_do_not_import_legacy_generators() -> None:
    result = subprocess.run(  # noqa: S603 - fixed trusted command; no shell
        (
            sys.executable,
            "-c",
            "from app.engine.answers.antiderivative import AntiderivativeAnswer; "
            "from app.engine.answers.derivative import DerivativeAnswer; "
            "from app.engine.answers.expression import ExpressionAnswer; "
            "from app.engine.answers.number import NumberAnswer; "
            "import sys; assert not any(m.startswith('app.generators') for m in sys.modules)",
        ),
        capture_output=True,
        timeout=5,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("2x^3/3 + C", "correct"),
        ("(2x^3 + 7)/3 + k", "correct"),
        ("2x^3/3 - pi*C", "correct"),
        ("2x^3/3 + C^2", "incorrect"),
        ("2x^3/3 + C*x", "incorrect"),
        ("2x^3/3", "missing_constant"),
        ("2x^3/3 + 7", "missing_constant"),
        ("x^3 + C", "incorrect"),
        ("1/(x-x) + C", "invalid"),
    ],
)
def test_antiderivative_constant_and_equivalence_rules(source: str, expected: str) -> None:
    answer: Answer = AntiderivativeAnswer(2 * X**2, 2 * X**3 / 3, sp.S.Reals)
    assert answer.check(parse_math_input(source)) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("ln|x| + C", "correct"),
        ("ln|2x| + C", "correct"),
        ("ln(x) + C", "incorrect"),
        ("ln|x|", "missing_constant"),
        ("ln|x| + abs(x)/x + C", "incorrect"),
    ],
)
def test_antiderivative_checks_all_domain_components(source: str, expected: str) -> None:
    answer = AntiderivativeAnswer(1 / X, sp.log(sp.Abs(X)), NONZERO)
    assert answer.check(parse_math_input(source)) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("4x^3", "correct"),
        ("2*2*x^(4-1)", "correct"),
        ("4x^3 + C", "incorrect"),
        ("4x^3 + 1", "incorrect"),
        ("4*sqrt(x)^6", "invalid"),
    ],
)
def test_derivative_rejects_constants_and_domain_holes(source: str, expected: str) -> None:
    answer: Answer = DerivativeAnswer(4 * X**3, sp.S.Reals)
    assert answer.check(parse_math_input(source)) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("y cos(xy)", "correct"),
        ("cos(x*y)*y", "correct"),
        ("x cos(xy)", "incorrect"),
        ("y cos(xy) + 0/(y-y)", "invalid"),
    ],
)
def test_expression_uses_declared_variables(source: str, expected: str) -> None:
    answer: Answer = ExpressionAnswer(Y * sp.cos(X * Y), {"x": "real", "y": "real"})
    assert answer.check(parse_math_input(source, {"x", "y"})) == expected


def test_symbolic_constant_and_integer_expected_values() -> None:
    assert ExpressionAnswer(sp.pi / 2, {}).check(parse_math_input("pi/2")) == "correct"
    assert ExpressionAnswer(2, {}).check(parse_math_input("x-x+2")) == "correct"
    assert DerivativeAnswer(1, sp.S.Reals).check(parse_math_input("1")) == "correct"
    assert AntiderivativeAnswer(0, 1, sp.S.Reals).check(parse_math_input("1+C")) == "correct"


_LIMITED_CHECK = """
import sys
from app.services.math_worker import _apply_limits
_apply_limits()
import sympy as sp
from app.engine.answers.expression import ExpressionAnswer
from app.services.math_parser import parse_math_input
x = sp.Symbol('x', positive=True)
y = sp.Symbol('y', real=True)
answer = ExpressionAnswer(2 * sp.log(x) + y, {'x': 'positive', 'y': 'real'})
print(answer.check(parse_math_input(sys.argv[1], {'x', 'y'})))
"""

_LIMITED_ANTIDERIVATIVE = """
from app.services.math_worker import _apply_limits
_apply_limits()
import sympy as sp
from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.services.math_parser import parse_math_input
x = sp.Symbol('x', real=True)
domain = sp.Union(sp.Interval.open(-sp.oo, -1), sp.Interval.open(-1, 0),
                  sp.Interval.open(0, sp.oo))
integrand = (x**3 + x + 1) / (x * (x + 1))
primitive = x**2 / 2 - x + sp.log(sp.Abs(x**2 + x))
answer = AntiderivativeAnswer(integrand, primitive, domain)
print(answer.check(parse_math_input('x^2/2 - x + ln|x^2+x| + C')))
"""


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux resource limits")
@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("ln(x^2) + y", "correct"),
        ("x + y", "incorrect"),
        ("2ln(x) + y + 0/(y-y)", "invalid"),
    ],
)
def test_expression_runs_under_worker_limits(source: str, expected: str) -> None:
    started = time.monotonic()
    result = subprocess.run(  # noqa: S603 - fixed trusted command; no shell
        (sys.executable, "-B", "-c", _LIMITED_CHECK, source),
        capture_output=True,
        timeout=3,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    assert result.stdout.strip() == expected.encode("ascii")
    assert time.monotonic() - started < 3


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux resource limits")
def test_rational_antiderivative_runs_under_worker_limits() -> None:
    started = time.monotonic()
    result = subprocess.run(  # noqa: S603 - fixed trusted command; no shell
        (sys.executable, "-B", "-c", _LIMITED_ANTIDERIVATIVE),
        capture_output=True,
        timeout=3,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    assert result.stdout.strip() == b"correct"
    assert time.monotonic() - started < 3
