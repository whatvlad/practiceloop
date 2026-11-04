"""Independent exact sets, full targets, domains and bounded grammar regressions."""

import json
from pathlib import Path

import pytest
import sympy as sp

from app.engine.answers.computational import (
    CategoryAnswer,
    FormulaAnswer,
    LimitAnswer,
    OrderedAnswer,
    PeriodicSetAnswer,
    RealSetAnswer,
)
from app.math_input import MathInputError, MathInputTooLong, parse_answer_input, parse_math_input
from app.math_input.contracts import InputContract


def contract_from(data):
    return InputContract(
        data["kind"],
        tuple(data.get("symbols", {}).items()),
        tuple(contract_from(c) for c in data.get("components", ())),
        tuple(data.get("labels", ())),
        tuple(data.get("choices", ())),
    )


CORPUS = json.loads(
    (Path(__file__).parent / "fixtures/computational_answer_syntax.json").read_text(
        encoding="utf-8"
    )
)


@pytest.mark.parametrize("case", CORPUS)
def test_shared_computational_grammar_corpus(case):
    contract = contract_from(case["contract"])
    if case["valid"]:
        parse_answer_input(case["text"], contract.kind, contract=contract)
    else:
        with pytest.raises(MathInputError):
            parse_answer_input(case["text"], contract.kind, contract=contract)


def test_periodic_convention_and_tagged_limits():
    answer = PeriodicSetAnswer(2 * sp.pi, sp.FiniteSet(0, sp.pi))
    assert verdict(answer, "(2*pi;{pi,0})") == "correct"
    assert verdict(answer, "(2*pi;{0})") == "incorrect"
    # The task must explicitly require its declared canonical base cell/period.
    assert verdict(answer, "(4*pi;{0,pi,2*pi,3*pi})") == "incorrect"
    assert verdict(LimitAnswer(sp.oo), "+inf") == "correct"
    assert verdict(LimitAnswer(sp.oo), "-inf") == "incorrect"
    assert verdict(LimitAnswer(sp.pi / 2), "pi/2") == "correct"
    assert verdict(LimitAnswer(sp.pi / 2), "inf") == "incorrect"
    assert verdict(LimitAnswer("does_not_exist"), "does_not_exist") == "correct"


def verdict(answer, source):
    tree = parse_answer_input(source, answer.kind, contract=answer.contract)
    return answer.check(tree)


@pytest.mark.parametrize(
    "source",
    [
        "(-inf,0) U (0,inf)",
        "R\\{0}",
        "(-inf,-1] U (-1,0) U (0,inf)",
    ],
)
def test_set_equivalence_by_independent_complement(source):
    expected = sp.S.Reals - sp.FiniteSet(0)
    assert verdict(RealSetAnswer(expected), source) == "correct"


@pytest.mark.parametrize(
    "source,result",
    [
        ("[0,1] U {2} U (2,3]", "correct"),
        ("[0,1] U [2,3]", "correct"),
        ("[0,1) U [2,3]", "incorrect"),
        ("[0,3]", "incorrect"),
        ("[1,0]", "invalid"),
        ("{0,1,2,3}", "incorrect"),
        ("[0,sqrt(-1)]", "invalid"),
        ("[0,1+0*(1/0)]", "invalid"),
    ],
)
def test_set_closure_gaps_order_and_undefined_intermediates(source, result):
    try:
        actual = verdict(RealSetAnswer(sp.Interval(0, 1) | sp.Interval(2, 3)), source)
    except MathInputError:
        actual = "invalid"
    assert actual == result


def test_empty_singleton_all_reals_and_duplicate_points():
    assert verdict(RealSetAnswer(sp.S.EmptySet), "{}") == "correct"
    assert verdict(RealSetAnswer(sp.FiniteSet(sp.sqrt(2))), "{sqrt(8)/2,sqrt(2)}") == "correct"
    assert verdict(RealSetAnswer(sp.S.Reals), "(-inf,0] U (0,inf)") == "correct"
    assert verdict(RealSetAnswer(sp.S.Reals), "R") == "correct"


def test_ordered_full_gradient_and_mixed_result():
    x, y = sp.symbols("x y", real=True)
    f = x**2 * y + y**3
    gradient = tuple(sp.diff(f, v).subs({x: 2, y: -1}) for v in (x, y))
    answer = OrderedAnswer(
        tuple(FormulaAnswer(v) for v in gradient), ("x component", "y component")
    )
    assert verdict(answer, "(-4;7)") == "correct"
    assert verdict(answer, "(7;-4)") == "incorrect"
    assert verdict(answer, "(-4;sqrt(49))") == "correct"
    with pytest.raises(MathInputError):
        verdict(answer, "sqrt(65)")  # norm cannot substitute for the full vector
    mixed = OrderedAnswer(
        (answer, RealSetAnswer(sp.Interval.open(0, sp.oo))), ("Gradient", "Domain")
    )
    assert verdict(mixed, "((-4;7);(0,inf))") == "correct"


def test_symbolic_parameters_have_local_assumptions_and_preserve_old_allowlist():
    a = sp.Symbol("a", positive=True)
    x = sp.Symbol("x", real=True)
    answer = FormulaAnswer(a * (x + 1), (("a", "positive"), ("x", "real")))
    assert verdict(answer, "a*x+a") == "correct"
    assert verdict(answer, "sqrt(a)^2*(x+1)") == "correct"
    assert verdict(answer, "a*x") == "incorrect"
    assert verdict(answer, "a*x+a+0/(x-2)") == "invalid"
    with pytest.raises(MathInputError):
        verdict(answer, "b*x+b")
    with pytest.raises(ValueError):
        parse_math_input("a*x", {"a", "x"})
    with pytest.raises(MathInputError):
        parse_math_input("a*x", {"x"})


@pytest.mark.parametrize("source", ["x/x", "1+0/(x-2)", "sqrt(x)^2-x+1", "1+0*ln(x)"])
def test_domain_holes_before_simplification(source):
    assert verdict(FormulaAnswer(1, (("x", "real"),)), source) == "invalid"


def test_integer_parameter_and_ode_constants_are_distinct_from_coordinates():
    c = sp.Symbol("C", real=True)
    x = sp.Symbol("x", real=True)
    assert verdict(FormulaAnswer(0, (("k", "integer"),)), "sin(pi*k)") == "correct"
    ode = FormulaAnswer(c * sp.exp(x), (("C", "real"), ("x", "real")))
    assert verdict(ode, "exp(x)*C") == "correct"
    # Formula identity checks do NOT certify a general solution's completeness.
    assert verdict(ode, "exp(x)") == "incorrect"


def test_categories_and_private_data_never_appear_in_public_contract():
    answer = CategoryAnswer("conditional", ("absolute", "conditional", "divergent"))
    assert verdict(answer, "conditional") == "correct"
    assert verdict(answer, "absolute") == "incorrect"
    assert answer.contract.public() == {
        "kind": "category",
        "maxBytes": 256,
        "choices": ["absolute", "conditional", "divergent"],
    }
    with pytest.raises(MathInputError):
        verdict(answer, "2")


@pytest.mark.parametrize(
    "kind,source",
    [
        ("real_set", "[0,1] or [2,3]"),
        ("real_set", "R\\{x}"),
        ("real_set", "[0,inf]"),
        ("real_set", "{__import__(os)}"),
        ("real_set", "{1}U"),
        ("real_set", "[0,1]U[2,3]U[4,5]U[6,7]U[8,9]U[10,11]U[12,13]U[14,15]U{16}"),
    ],
)
def test_malformed_and_injection_inputs(kind, source):
    with pytest.raises(MathInputError):
        parse_answer_input(source, kind, contract=InputContract(kind))


def test_nested_budgets_are_shared_and_kind_comes_from_generator():
    with pytest.raises(ValueError):
        parse_answer_input("R", "real_set")
    spec = InputContract("tuple", components=(InputContract("formula"),) * 8, labels=("Value",) * 8)
    with pytest.raises(MathInputError):
        parse_answer_input(
            "(" + ";".join("sin(cos(sin(1)))" for _ in range(8)) + ")", "tuple", contract=spec
        )
    with pytest.raises(MathInputTooLong):
        parse_answer_input(
            "(" + ";".join("1+" * 20 + "1" for _ in range(8)) + ")", "tuple", contract=spec
        )
    with pytest.raises(ValueError):
        InputContract("formula", symbols=(("os", "real"),))


@pytest.mark.parametrize("text", ["3/5", "sin(x)+C", "2xy", "{1,2}", "[-inf,2]"])
def test_old_grammars_do_not_gain_new_syntax(text):
    if text == "{1,2}":
        assert parse_answer_input(text, "finite_set").kind == "finite_set"
    elif text == "[-inf,2]":
        with pytest.raises(MathInputError):
            parse_answer_input(text, "interval")
    else:
        try:
            expected = parse_math_input(text)
        except MathInputError:
            with pytest.raises(MathInputError):
                parse_answer_input(text, "expression")
        else:
            assert parse_answer_input(text, "expression") == expected
