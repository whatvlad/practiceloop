from __future__ import annotations

import pytest
from sympy import Abs, E, Rational, Symbol, log, pi, simplify, sin, sqrt

from app.services.math_parser import MathInputError, MathInputTooLong, parse_math_input
from app.services.math_worker import _build_sympy

X = Symbol("x", real=True)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("3pi", 3 * pi),
        ("3*pi", 3 * pi),
        ("3π", 3 * pi),
        ("3/5", Rational(3, 5)),
        ("sqrt(3)", sqrt(3)),
        ("√3", sqrt(3)),
        ("e^2", E**2),
        ("e^(-x)", E ** (-X)),
        ("e^(2*x+1)", E ** (2 * X + 1)),
        ("pi/4 + 2", pi / 4 + 2),
        ("３π − 2×x ÷ 4", 3 * pi - X / 2),
        ("2(x+1)", 2 * (X + 1)),
        ("√(x+1)", sqrt(X + 1)),
        (".125 + 0.5", Rational(5, 8)),
        ("-x^2", -(X**2)),
        ("x^(-1/2)", X ** Rational(-1, 2)),
        ("sin^-2(x)", sin(X) ** -2),
        ("sin^1/2(x)", sin(X) ** Rational(1, 2)),
        ("|x|+|x+1|", Abs(X) + Abs(X + 1)),
        ("log|x|", log(Abs(X))),
        ("x+C+2C", X + 3 * Symbol("C", real=True)),
        ("2x + (x+1)(x-1)", 2 * X + (X + 1) * (X - 1)),
        ("sin^2(x) + ln|x|", sin(X) ** 2 + log(Abs(X))),
    ],
)
def test_supported_notation(source: str, expected: object) -> None:
    assert simplify(_build_sympy(parse_math_input(source)) - expected) == 0


@pytest.mark.parametrize(
    "source",
    [
        "__import__('os')",
        "x.real",
        "open(x)",
        "f(x)",
        "lambda x: x",
        "y + z",
        "i + 1",
        "sin x",
        "x**2",
        "1//2",
        "1e6",
        "[x]",
        "x, y",
        "|x + |x||",
        "1/0",
        "x^x",
        "x^13",
        "x^(1/13)",
        "x^-13",
        "sin^13(x)",
        "sin^1/0(x)",
        "sin^x(x)",
        "e^13",
        "e^(-1/13)",
        "e^(x^13)",
        "1/(-0.0)",
        "1 2",
        "sin()",
        "sin(x,x)",
        "x+",
        "(x",
        "x)",
        "||x||",
        "√-3",
        "√",
        "1..2",
        "nan",
        "oo",
        "x[0]",
        "x=1",
        "x!",
        "α",
        "",
        "   ",
    ],
)
def test_unsafe_or_unsupported_input_is_rejected(source: str) -> None:
    with pytest.raises(MathInputError):
        parse_math_input(source)


def test_input_length_is_bounded_before_tokenisation() -> None:
    with pytest.raises(MathInputTooLong, match="length"):
        parse_math_input("1" * 257)
    assert parse_math_input(" " * 255 + "x") == parse_math_input("x")
    with pytest.raises(MathInputTooLong):
        parse_math_input(" " * 255 + "π")
    with pytest.raises(MathInputError) as invalid:
        parse_math_input("")
    assert not isinstance(invalid.value, MathInputTooLong)


def test_token_count_is_bounded() -> None:
    with pytest.raises(MathInputError, match="tokens"):
        parse_math_input("+".join("1" for _ in range(65)))


def test_node_count_is_bounded() -> None:
    with pytest.raises(MathInputError, match="nodes"):
        parse_math_input("+".join("1" for _ in range(49)))


def test_group_nesting_is_bounded() -> None:
    with pytest.raises(MathInputError, match="nesting"):
        parse_math_input("(" * 13 + "x" + ")" * 13)


def test_function_count_is_bounded() -> None:
    with pytest.raises(MathInputError, match="function"):
        parse_math_input("+".join("sin(x)" for _ in range(17)))


@pytest.mark.parametrize("source", ["123456789", "1.1234567", "000000001", "123.123456"])
def test_numeric_literal_length_is_bounded(source: str) -> None:
    with pytest.raises(MathInputError, match="Numeric literal"):
        parse_math_input(source)


@pytest.mark.parametrize(
    "source",
    [
        "12345678",
        "12.123456",
        "x^12",
        "x^(-12)",
        "x^(1/12)",
        "(" * 12 + "x" + ")" * 12,
        "+".join("sin(x)" for _ in range(16)),
        "+" * 95 + "x",
    ],
)
def test_exact_boundaries_remain_accepted(source: str) -> None:
    parse_math_input(source)
