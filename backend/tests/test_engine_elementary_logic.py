"""Full truth tables, precedence, shared syntax and unchanged legacy grammar."""

import json
from itertools import product
from pathlib import Path

import pytest

from app.engine.answers.logic import LogicAnswer, truth
from app.math_input import MathInputError, parse_answer_input, parse_math_input
from app.math_input.contracts import InputContract

CONTRACT = InputContract("logic", choices=("p", "q"))
CORPUS = json.loads((Path(__file__).parent / "fixtures/logic_answer_syntax.json").read_text())


def parse(text):
    return parse_answer_input(text, "logic", contract=CONTRACT)


@pytest.mark.parametrize("case", CORPUS)
def test_shared_logic_syntax(case):
    if case["valid"]:
        parse(case["text"])
    else:
        with pytest.raises(MathInputError):
            parse(case["text"])


@pytest.mark.parametrize("op", ["&", "|", "^", "->", "<->"])
def test_every_operator_matches_an_independent_truth_table(op):
    for p, q in product((False, True), repeat=2):
        expected = {"&": p and q, "|": p or q, "^": p != q, "->": (not p) or q, "<->": p == q}[op]
        assert truth(parse(f"p {op} q"), {"p": p, "q": q}) is expected


def test_negations_accept_equivalence_over_every_assignment():
    for original, negation in [
        ("p&q", "!p|!q"),
        ("p|q", "!p&!q"),
        ("p->q", "p&!q"),
        ("p<->q", "p^q"),
        ("p^q", "p<->q"),
    ]:
        answer = LogicAnswer(parse(f"!({original})"), CONTRACT.choices)
        assert answer.check(parse(negation)) == "correct"
        assert answer.check(parse(original)) == "incorrect"
    assert LogicAnswer(parse("p->(q->p)"), CONTRACT.choices).check(parse("p->q->p")) == "correct"
    assert LogicAnswer(parse("!p|q&p"), CONTRACT.choices).check(parse("!p|(q&p)")) == "correct"


def test_logic_does_not_expand_historical_math_grammar():
    with pytest.raises(MathInputError):
        parse_math_input("p|q")
    with pytest.raises(ValueError, match="trusted matching contract"):
        parse_answer_input("p|q", "logic")
    with pytest.raises(ValueError):
        InputContract("logic", choices=("os",))


def test_positive_literal_bases_are_opt_in_and_never_evaluate_a_power_tower():
    contract = InputContract("formula", symbols=(("x", "real"),))
    for text in ("3^x", "(1/2)^x", "0.5^x"):
        parse_answer_input(text, "formula", contract=contract)
        with pytest.raises(MathInputError):
            parse_math_input(text)
    tower = "99999999"
    for _ in range(10):
        tower = "(" + tower + "^12)"
    for text in ("(-3)^x", "0^x", tower + "^x"):
        with pytest.raises(MathInputError):
            parse_answer_input(text, "formula", contract=contract)
        with pytest.raises(MathInputError):
            parse_math_input(text)
