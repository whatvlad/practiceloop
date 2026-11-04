"""A small, bounded parser for learner-entered mathematical expressions."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Collection, Mapping
from dataclasses import dataclass
from fractions import Fraction
from typing import Literal, cast

MAX_INPUT_BYTES = 256
MAX_TOKENS = 128
MAX_NODES = 96
MAX_NESTING = 12
MAX_FUNCTION_CALLS = 16
MAX_LITERAL_DIGITS = 8
MAX_FRACTION_DIGITS = 6
MAX_EXPONENT_PART = 12

_FUNCTIONS = frozenset(
    {
        "sin",
        "cos",
        "tan",
        "sec",
        "csc",
        "cot",
        "asin",
        "acos",
        "atan",
        "exp",
        "ln",
        "log",
        "sqrt",
        "abs",
    }
)
_NAME_STARTS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

# ADR-005: the variables a template may declare, and the real domain each may have.
# #221: a complex-number answer declares `i`, the imaginary unit, never a variable.
type VariableDomain = Literal["real", "positive", "imaginary"]
ANSWER_VARIABLES: Mapping[str, frozenset[VariableDomain]] = {
    "x": frozenset({"real", "positive"}),
    "y": frozenset({"real", "positive"}),
    "z": frozenset({"real", "positive"}),
    "r": frozenset({"positive"}),
    "theta": frozenset({"real"}),
    "i": frozenset({"imaginary"}),
}
# Names a letter run can be split into when a template declares variables, longest first.
_SPLIT_NAMES = tuple(sorted({*_FUNCTIONS, *ANSWER_VARIABLES, "pi", "e"}, key=len, reverse=True))


class MathInputError(ValueError):
    """The learner input is not in the supported, bounded grammar."""


class MathInputTooLong(MathInputError):
    """Request-size rejection (422/no attempt), unlike invalid mathematical syntax."""


type NodeKind = Literal[
    "number",
    "symbol",
    "unary",
    "binary",
    "function",
    "boolean",
    "finite_set",
    "interval",
    "endpoint",
    "real_set",
    "tuple",
    "category",
]
type NodeValue = str | tuple[int, int]


@dataclass(frozen=True, slots=True)
class MathNode:
    kind: NodeKind
    value: NodeValue
    children: tuple[MathNode, ...] = ()


@dataclass(frozen=True, slots=True)
class _Token:
    kind: str
    value: str


_SUPERSCRIPTS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
_SUPERSCRIPT_RUN = re.compile("⁻?[⁰¹²³⁴⁵⁶⁷⁸⁹]+")


def _normalise(source: str) -> str:
    if not isinstance(source, str):
        raise MathInputError("Input must be text")
    if len(source) > MAX_INPUT_BYTES:
        raise MathInputTooLong("Input length exceeds the supported range")
    replacements: dict[int, str | int | None] = {
        ord("π"): "pi",
        ord("θ"): "theta",
        ord("ϑ"): "theta",
        ord("−"): "-",
        ord("–"): "-",
        ord("×"): "*",
        ord("÷"): "/",
    }
    # NFKC would turn x² into x2 (read as x*2), so superscript runs become powers first.
    powered = _SUPERSCRIPT_RUN.sub(lambda run: "^" + run.group().translate(_SUPERSCRIPTS), source)
    normalised = unicodedata.normalize("NFKC", powered).translate(replacements)
    size_form = normalised.replace("√", "sqrt")
    try:
        encoded = size_form.encode("ascii")
    except UnicodeEncodeError as exc:
        raise MathInputError("Input contains unsupported characters") from exc
    if len(encoded) > MAX_INPUT_BYTES:
        raise MathInputTooLong("Input length exceeds the supported range")
    return normalised


def _split_name(run: str) -> list[str]:
    """ADR-005 rule for templates with declared variables: a run of letters is read
    from the left, each time as the longest function, variable, `pi` or `e` that
    starts there, so `2xy` is 2*x*y, `rtheta` is r*theta and `xsin(y)` is x*sin(y).
    A letter that starts no such name makes the whole answer invalid."""
    names: list[str] = []
    start = 0
    while start < len(run):
        name = next((name for name in _SPLIT_NAMES if run.startswith(name, start)), None)
        if name is None:
            raise MathInputError("Symbol is not allowlisted")
        names.append(name)
        start += len(name)
    return names


def _tokenise(source: str, split_names: bool = False) -> tuple[_Token, ...]:
    tokens: list[_Token] = []
    index = 0
    while index < len(source):
        char = source[index]
        if char.isspace():
            index += 1
            continue
        if char.isdigit() or char == ".":
            start = index
            dots = 0
            while index < len(source) and (source[index].isdigit() or source[index] == "."):
                dots += source[index] == "."
                index += 1
            literal = source[start:index]
            if dots > 1 or literal == ".":
                raise MathInputError("Malformed number")
            integer, dot, fraction = literal.partition(".")
            if len(integer + fraction) > MAX_LITERAL_DIGITS or len(fraction) > MAX_FRACTION_DIGITS:
                raise MathInputError("Numeric literal is too long")
            if index < len(source) and source[index] in "eE":
                raise MathInputError("Scientific notation is not supported")
            tokens.append(_Token("NUMBER", literal))
        elif char in _NAME_STARTS:
            start = index
            while index < len(source) and source[index] in _NAME_STARTS:
                index += 1
            run = source[start:index]
            names = _split_name(run) if split_names else [run]
            tokens.extend(_Token("NAME", name) for name in names)
        elif char == "√":
            tokens.append(_Token("ROOT", char))
            index += 1
        elif char in "+-*/^()|":
            if index + 1 < len(source) and source[index : index + 2] in {"**", "//"}:
                raise MathInputError("Unsupported operator")
            tokens.append(_Token(char, char))
            index += 1
        else:
            raise MathInputError("Input contains unsupported syntax")
        if len(tokens) > MAX_TOKENS:
            raise MathInputError("Expression has too many tokens")
    if not tokens:
        raise MathInputError("Expression is empty")
    return (*tokens, _Token("EOF", ""))


class _Parser:
    def __init__(self, tokens: tuple[_Token, ...], variables: frozenset[str] | None) -> None:
        self.tokens = tokens
        # None is the ADR-003 integration grammar: x, plus one letter for the constant.
        self.variables = variables
        self.position = 0
        self.node_count = 0
        self.function_count = 0
        self.group_depth = 0
        self.inside_absolute = False
        self.extra_symbol: str | None = None

    @property
    def current(self) -> _Token:
        return self.tokens[self.position]

    def advance(self) -> _Token:
        token = self.current
        self.position += 1
        return token

    def expect(self, kind: str) -> None:
        if self.current.kind != kind:
            raise MathInputError("Malformed expression")
        self.advance()

    def node(self, kind: NodeKind, value: NodeValue, *children: MathNode) -> MathNode:
        self.node_count += 1
        if self.node_count > MAX_NODES:
            raise MathInputError("Expression has too many nodes")
        return MathNode(kind, value, children)

    def parse(self) -> MathNode:
        result = self.expression()
        if self.current.kind != "EOF":
            raise MathInputError("Malformed expression")
        return result

    def expression(self, minimum_precedence: int = 0) -> MathNode:
        left = self.prefix()
        while True:
            kind = self.current.kind
            implicit = self._starts_atom(kind) and not (kind == "|" and self.inside_absolute)
            if kind in {"+", "-"}:
                precedence = 10
                operator = kind
            elif kind in {"*", "/"}:
                precedence = 20
                operator = kind
            elif kind == "^":
                precedence = 30
                operator = kind
            elif implicit:
                if kind == "NUMBER" and self.tokens[self.position - 1].kind == "NUMBER":
                    raise MathInputError("Adjacent numbers require an operator")
                precedence = 20
                operator = "*"
            else:
                break
            if precedence < minimum_precedence:
                break
            if not implicit:
                self.advance()
            right = self.expression(precedence if operator == "^" else precedence + 1)
            if operator == "/" and _constant_fraction(right) == 0:
                raise MathInputError("Division by zero is not allowed")
            if operator == "^":
                self._validate_exponent(left, right)
            left = self.node("binary", operator, left, right)
        return left

    def prefix(self) -> MathNode:
        token = self.current
        if token.kind in {"+", "-"}:
            self.advance()
            return self.node("unary", token.kind, self.expression(25))
        if token.kind == "NUMBER":
            self.advance()
            return self.node("number", _number_fraction(token.value))
        if token.kind == "NAME":
            return self._name()
        if token.kind == "ROOT":
            self.advance()
            if self.current.kind not in {"NUMBER", "NAME", "("}:
                raise MathInputError("Square root requires a number, name, or group")
            return self._function("sqrt", self.prefix())
        if token.kind == "(":
            return self._group()
        if token.kind == "|":
            return self._absolute()
        raise MathInputError("Expected a number, symbol, or group")

    def _name(self) -> MathNode:
        name = self.advance().value
        if name in _FUNCTIONS:
            power: MathNode | None = None
            if self.current.kind == "^":
                self.advance()
                power = self._function_power()
            if self.current.kind == "|" and name in {"ln", "log"}:
                argument = self._absolute()
            else:
                if self.current.kind != "(":
                    raise MathInputError("Functions require parentheses")
                argument = self._group()
            result = self._function(name, argument)
            if power is not None:
                self._validate_exponent(result, power)
                result = self.node("binary", "^", result, power)
            return result
        if self.variables is not None:
            if name not in self.variables and name not in {"pi", "e"}:
                raise MathInputError("Variable is not used in this exercise")
        elif name not in {"x", "pi", "e"}:
            if len(name) != 1 or name in {"i", "I", "j", "J"}:
                raise MathInputError("Symbol is not allowlisted")
            if self.extra_symbol not in {None, name}:
                raise MathInputError("Only one arbitrary constant is supported")
            self.extra_symbol = name
        if self.current.kind == "(":
            raise MathInputError("Arbitrary function calls are not supported")
        return self.node("symbol", name)

    def _group(self) -> MathNode:
        self.expect("(")
        self.group_depth += 1
        if self.group_depth > MAX_NESTING:
            raise MathInputError("Expression nesting is too deep")
        result = self.expression()
        self.expect(")")
        self.group_depth -= 1
        return result

    def _absolute(self) -> MathNode:
        if self.inside_absolute:
            raise MathInputError("Nested absolute-value bars are not supported")
        self.expect("|")
        self.inside_absolute = True
        self.group_depth += 1
        if self.group_depth > MAX_NESTING:
            raise MathInputError("Expression nesting is too deep")
        result = self.expression()
        self.expect("|")
        self.group_depth -= 1
        self.inside_absolute = False
        return self._function("abs", result)

    def _function(self, name: str, argument: MathNode) -> MathNode:
        self.function_count += 1
        if self.function_count > MAX_FUNCTION_CALLS:
            raise MathInputError("Expression has too many function calls")
        return self.node("function", name, argument)

    def _function_power(self) -> MathNode:
        sign = ""
        if self.current.kind in {"+", "-"}:
            sign = self.advance().kind
        if self.current.kind != "NUMBER":
            raise MathInputError("Function powers must be numeric")
        numerator = self.node("number", _number_fraction(self.advance().value))
        if sign:
            numerator = self.node("unary", sign, numerator)
        if self.current.kind != "/":
            return numerator
        self.advance()
        if self.current.kind != "NUMBER":
            raise MathInputError("Malformed function power")
        denominator = self.node("number", _number_fraction(self.advance().value))
        if _constant_fraction(denominator) == 0:
            raise MathInputError("Division by zero is not allowed")
        return self.node("binary", "/", numerator, denominator)

    @staticmethod
    def _starts_atom(kind: str) -> bool:
        return kind in {"NUMBER", "NAME", "ROOT", "(", "|"}

    @staticmethod
    def _validate_exponent(base: MathNode, exponent: MathNode) -> None:
        value = _constant_fraction(exponent)
        if value is None:
            if base.kind == "symbol" and base.value == "e":
                return
            raise MathInputError("Variable exponents are only supported for e")
        if abs(value.numerator) > MAX_EXPONENT_PART or value.denominator > MAX_EXPONENT_PART:
            raise MathInputError("Exponent is outside the supported range")


def _number_fraction(literal: str) -> tuple[int, int]:
    integer, dot, fraction = literal.partition(".")
    if not dot:
        return int(integer), 1
    numerator = int((integer or "0") + fraction)
    denominator = 10 ** len(fraction)
    reduced = Fraction(numerator, denominator)
    return reduced.numerator, reduced.denominator


def _constant_fraction(node: MathNode) -> Fraction | None:
    if node.kind == "number":
        numerator, denominator = cast(tuple[int, int], node.value)
        return Fraction(numerator, denominator)
    if node.kind == "unary":
        value = _constant_fraction(node.children[0])
        if value is None:
            return None
        return value if node.value == "+" else -value
    if node.kind == "binary" and node.value in {"+", "-", "*", "/"}:
        left = _constant_fraction(node.children[0])
        right = _constant_fraction(node.children[1])
        if left is None or right is None or (node.value == "/" and right == 0):
            return None
        if node.value == "+":
            return left + right
        if node.value == "-":
            return left - right
        if node.value == "*":
            return left * right
        return left / right
    return None


def declared_variables(value: object) -> dict[str, VariableDomain]:
    """A template's `{variable: domain}` declaration, validated; ValueError otherwise."""
    if not isinstance(value, dict) or not value:
        raise ValueError("Answer variables must be a non-empty mapping")
    for name, domain in value.items():
        if name not in ANSWER_VARIABLES or domain not in ANSWER_VARIABLES[name]:
            raise ValueError("Unsupported answer variable or domain")
    return cast(dict[str, VariableDomain], dict(value))


def parse_math_input(source: str, variables: Collection[str] | None = None) -> MathNode:
    """Parse learner text into a validated internal tree, without invoking SymPy.

    `variables` is the template's declared set (ADR-005). Without it the ADR-003
    integration grammar applies unchanged.
    """
    declared = None if variables is None else frozenset(variables)
    if declared is not None and not declared <= ANSWER_VARIABLES.keys():
        raise ValueError("Unsupported answer variable")
    tokens = _tokenise(_normalise(source), split_names=declared is not None)
    return _Parser(tokens, declared).parse()
