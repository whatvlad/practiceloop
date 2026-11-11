"""#289: independent Laplace quadrature and pre-reveal graph projection."""

import math
from datetime import date

import pytest
import sympy as sp
from seed_sweep import sweep
from test_engine_analysis_limits import source
from test_engine_double_integrals_cartesian import quad

from app.api.worksheets import _print_problem
from app.engine import practice
from app.engine.generators.analysis_limits import generators
from app.math_input import parse_answer_input
from app.services.worksheet_pdf import PrintedGroup, render_tex
from app.services.worksheets import PrintItem

TRANSFORMS = [g for g in generators() if g.evaluate.__module__.endswith("._laplace_transforms")]


def reference(prefix, a, b, c):
    if prefix == "LTAA":
        return lambda t: a * t - b * c, 0, ()
    if prefix == "LTAB":
        return lambda t: a * math.sin((b + c) * t), 0, ()
    if prefix == "LTAC":
        return lambda t: a * c * t ** (b + 1), 0, ()
    if prefix == "LTAD":
        return lambda t: a * t * math.exp(-(b + c) * t), -(b + c), ()
    if prefix == "LTAE":
        return lambda t: a * math.exp(b * t) * math.cos(c * t), b, ()
    if prefix == "LTAF":
        return lambda t: a * c * math.sinh(b * t), b, ()
    if prefix == "LTAG":
        return lambda t: b + c, None, (0, a)
    if prefix == "LTAH":
        return lambda t: (b + c) * (1 - abs(t / a - 1)), None, (0, a, 2 * a)
    if prefix == "LTAI":
        return lambda t: (b + c) * min(t / a, 1), 0, (a,)
    if prefix == "LTAJ":
        return lambda t: a * t - b * math.cos(c * t), 0, ()
    if prefix == "LTAK":
        return lambda t: a + b * t ** (c + 1), 0, ()
    if prefix == "LTAL":
        return lambda t: (a * t + b) * math.exp(c * t), c, ()
    if prefix == "LTAM":
        return lambda t: a * math.sin(b * t) + b * math.cos(c * t), 0, ()
    if prefix == "LTAN":
        return lambda t: a * math.exp(-b * t) * (1 + math.sin(c * t)), -b, ()
    if prefix == "LTAO":
        return lambda t: math.exp(a * t) * (b * math.cos(c * t) - a * math.sin(c * t)), a, ()
    raise AssertionError(prefix)


def integrate(function, s, limits):
    return math.fsum(
        quad(lambda t: math.exp(-s * t) * function(t), lo, hi)
        for lo, hi in zip(limits, limits[1:], strict=False)
    )


@pytest.mark.parametrize("generator", TRANSFORMS, ids=lambda item: item.prefix)
def test_laplace_transform_against_independent_quadrature(generator):
    seen = set()
    prefix = generator.prefix
    s = sp.Symbol("s", real=True)
    for seed in sweep(1000):
        params = generator.draw(seed)
        coefficients = params.a, params.b, params.c
        if coefficients in seen:
            continue
        seen.add(coefficients)
        task = generator.build(params)
        answer = task.answer
        tree = parse_answer_input(
            source(answer), generator.contract.kind, contract=generator.contract
        )
        assert answer.check(tree) == "correct"
        function, threshold, knots = reference(prefix, *coefficients)
        formula = answer.components[0].expected
        if threshold is None:
            assert answer.components[-1].expected == sp.S.Reals
            for sample in (-0.5, 0.0, 1.1):
                value = answer.components[1].expected if sample == 0 else formula.subs(s, sample)
                assert float(value) == pytest.approx(integrate(function, sample, knots), rel=1e-11)
        else:
            assert answer.components[-1].expected == sp.Interval.open(threshold, sp.oo)
            for sample in (threshold + 2.3, threshold + 4.1):
                stop = 60 / (sample - threshold)
                limits = sorted(set([i * stop / 32 for i in range(33)] + list(knots)))
                numeric = integrate(function, sample, limits)
                assert float(formula.subs(s, sample)) == pytest.approx(
                    numeric, abs=1e-10, rel=1e-10
                )


@pytest.mark.parametrize("prefix", ["LTAG", "LTAH", "LTAI"])
def test_prompt_graph_is_available_before_reveal_and_in_exercise_pdf(prefix, monkeypatch):
    generator = next(g for g in TRANSFORMS if g.prefix == prefix)
    issued = practice.render(generator.build(generator.draw(12)), practice._registry())

    def forbidden(*args, **kwargs):
        pytest.fail("Public graph projection rebuilt a symbolic task")

    monkeypatch.setattr(type(generator), "build", forbidden)
    projection = practice.problem_projection(issued.record)
    assert set(projection) == {"answerInput", "promptVisual"}
    assert projection["promptVisual"] == issued.visual
    item = PrintItem(
        0,
        generator.topic,
        generator.difficulty,
        issued.statement,
        issued.answer_latex,
        list(issued.steps),
        issued.record,
    )
    printed = _print_problem(item, False, 0)
    tex = render_tex(
        [PrintedGroup("Laplace transforms", [printed])],
        paper="a4",
        columns=1,
        answer_key=False,
        day=date(2026, 1, 1),
    )
    assert printed.prompt_graph in tex
    assert "pdfliteral" in printed.prompt_graph
    assert issued.answer_latex not in tex
