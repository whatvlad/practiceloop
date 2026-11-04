"""Independent elementary mathematics and full-contract generator integration."""

import json
import re
from functools import cache
from pathlib import Path

import pytest
import sympy as sp

from app.engine.answers.computational import (
    CategoryAnswer,
    FormulaAnswer,
    OrderedAnswer,
    PeriodicSetAnswer,
    RealSetAnswer,
)
from app.engine.answers.domain_formula import DomainFormulaAnswer
from app.engine.answers.logic import LogicAnswer
from app.engine.generators.catalogue import registry
from app.engine.generators.elementary import build_form, generators
from app.engine.rendering import render
from app.math_input import parse_answer_input


def expression_source(value):
    text = sp.sstr(value).replace("**", "^").replace("Abs(", "abs(")
    return re.sub(
        r"x\^(\d+)",
        lambda m: (
            "(" + "*".join("x^" + str(min(12, n)) for n in range(int(m[1]), 0, -12)) + ")"
            if int(m[1]) > 12
            else m[0]
        ),
        text,
    )


def set_source(value):
    if value == sp.S.Reals:
        return "R"
    if value == sp.S.EmptySet:
        return "{}"
    if isinstance(value, sp.Union):
        return " U ".join(map(set_source, value.args))
    if isinstance(value, sp.FiniteSet):
        return "{" + ",".join(map(expression_source, value)) + "}"
    return (
        ("(" if value.left_open else "[")
        + expression_source(value.start).replace("-oo", "-inf")
        + ","
        + expression_source(value.end).replace("oo", "inf")
        + (")" if value.right_open else "]")
    )


def source(answer):
    if isinstance(answer, CategoryAnswer):
        return answer.expected
    if isinstance(answer, (FormulaAnswer, DomainFormulaAnswer)):
        return expression_source(answer.expected)
    if isinstance(answer, RealSetAnswer):
        return set_source(answer.expected)
    if isinstance(answer, OrderedAnswer):
        return "(" + ";".join(map(source, answer.components)) + ")"
    if isinstance(answer, PeriodicSetAnswer):
        return "(" + expression_source(answer.period) + ";" + set_source(answer.base) + ")"
    if isinstance(answer, LogicAnswer):

        def visit(node):
            if not node.children:
                return str(node.value)
            if node.value == "!":
                return "!(" + visit(node.children[0]) + ")"
            return "(" + visit(node.children[0]) + str(node.value) + visit(node.children[1]) + ")"

        return visit(answer.expected)
    raise TypeError(type(answer))


@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.template)
@pytest.mark.parametrize("seed", [3, 200, 999])
def test_every_elementary_canonical_target_fits_aggregate_grammar_and_checks(generator, seed):
    params = generator.draw(seed)
    task = generator.build(params)
    text = source(task.answer)
    assert len(text.encode()) <= 256, (generator.template, text)
    contract = generator.input_contract(params)
    assert contract == task.answer.contract
    tree = parse_answer_input(text, task.answer.kind, contract=contract)
    assert task.answer.check(tree) == "correct", (generator.template, text)
    issued = render(task, registry())
    assert issued.statement and issued.steps


def test_original_denominator_holes_remain_rejected_on_restricted_domains():
    x = sp.Symbol("x", real=True)
    answer = DomainFormulaAnswer(x, sp.Interval(0, 2))

    def verdict(text):
        return answer.check(parse_answer_input(text, "formula", contract=answer.contract))

    assert verdict("x") == "correct"
    assert verdict("x*(x-1)/(x-1)") == "invalid"
    assert verdict("x+0/(x-1)") == "invalid"
    assert verdict("sqrt(x^2)") == "correct"
    assert verdict("-sqrt(x^2)") == "incorrect"


@cache
def certify_canonical(answer):
    text = source(answer)
    tree = parse_answer_input(text, answer.kind, contract=answer.contract)
    assert answer.check(tree) == "correct", text


@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.template)
def test_thousand_seeds_preserve_full_targets_and_input_budgets(generator):
    for seed in range(1000):
        params = generator.draw(seed)
        task = generator.build(params)
        assert task == generator.build(generator.draw(seed))
        assert task.answer.contract == generator.input_contract(params)
        certify_canonical(task.answer)


@pytest.mark.parametrize("name", ["trig-linearization-square", "trig-linearization-fourth"])
def test_linearization_requires_the_requested_linear_cosine_representation(name):
    generator = next(g for g in generators() if g.template == name)
    params = generator.draw(200)
    answer = generator.build(params).answer
    function = "cos" if params.variant % 2 else "sin"
    power = 4 if name.endswith("fourth") else 2
    original = f"{params.a}*{function}({params.b}*x)^{power}+{params.c}"
    assert (
        answer.check(parse_answer_input(original, "formula", contract=answer.contract)) == "invalid"
    )


@pytest.mark.parametrize(
    "example",
    json.loads((Path(__file__).parent / "fixtures/elementary_worked_examples.json").read_text()),
)
def test_independently_hand_worked_examples(example):
    answer = build_form(example["template"], *example["parameters"]).answer
    tree = parse_answer_input(example["answer"], answer.kind, contract=answer.contract)
    assert answer.check(tree) == "correct", example
    assert example["derivation"]
