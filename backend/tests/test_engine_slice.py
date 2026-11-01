"""Behavioural checks for the isolated generator slice."""

import importlib
import math
import subprocess
import sys
from fractions import Fraction

import pytest
import sympy as sp

from app.engine.answers._symbolic import X, components
from app.engine.answers.antiderivative import AntiderivativeAnswer
from app.engine.answers.derivative import DerivativeAnswer
from app.engine.answers.expression import ExpressionAnswer
from app.engine.answers.number import NumberAnswer
from app.engine.codes import parse_code
from app.services.math_parser import parse_math_input


def catalogue():
    return importlib.import_module("app.engine.generators.catalogue").registry()


@pytest.mark.parametrize(
    "version",
    ["partial-fractions-v1", "indefinite-v1", "definite-v1", "derivative-v1", "combinations-v1"],
)
def test_registered_generators_replay_codes_and_have_steps(version: str) -> None:
    registry = catalogue()
    registry.validate_dependencies()
    generator = registry.get(version)
    for seed in (0, 1, 123, 9999999999999999):
        params = generator.draw(seed)
        restored = generator.params.model_validate_json(params.model_dump_json())
        task = generator.build(restored)
        assert task == generator.build(generator.draw(seed))
        code = parse_code(task.code, registry)
        assert code.seed == seed
        assert registry.get_code(code.prefix, code.version).version == version
        assert task.generator_version == version
        assert task.statement and task.steps
        assert all(step.text_key and step.latex for step in task.steps)
    for bad in (-1, 10**16, True):
        with pytest.raises(ValueError):
            generator.draw(bad)


def test_partial_fraction_answer_reconstructs_input_and_poles() -> None:
    generator = catalogue().get("partial-fractions-v1")
    task = generator.build(generator.draw(123))
    assert isinstance(task.answer, ExpressionAnswer)
    decomposition = task.answer.expected
    assert len(sp.Add.make_args(decomposition)) >= 2
    assert sp.cancel(sp.together(decomposition) - decomposition) == 0
    assert task.answer.check(parse_math_input(str(decomposition))) == "correct"


def test_indefinite_integrals_are_correct_and_compose_partial_fractions() -> None:
    registry = catalogue()
    generator = registry.get("indefinite-v1")
    assert "partial-fractions-v1" in generator.requires
    forms = set()
    for seed in range(12):
        task = generator.build(generator.draw(seed))
        assert isinstance(task.answer, AntiderivativeAnswer)
        for replacement, variable, _ in components(task.answer.domain):
            difference = sp.diff(task.answer.primitive.subs(X, replacement), variable)
            difference /= sp.diff(replacement, variable)
            assert sp.simplify(difference - task.answer.integrand.subs(X, replacement)) == 0
        rational = task.answer.integrand.as_numer_denom()[1].has(X)
        forms.add(rational)
        if rational:
            partial = registry.get("partial-fractions-v1")
            source = partial.build(partial.draw(seed))
            assert isinstance(source.answer, ExpressionAnswer)
            assert sp.cancel(task.answer.integrand - source.answer.expected) == 0
            assert any(step in task.steps for step in source.steps)
    assert forms == {False, True}


def test_definite_integrals_wrap_indefinite_and_return_exact_fraction() -> None:
    registry = catalogue()
    indefinite = registry.get("indefinite-v1")
    definite = registry.get("definite-v1")
    assert "indefinite-v1" in definite.requires
    forms = set()
    for seed in range(12):
        inner = indefinite.build(indefinite.draw(seed))
        outer = definite.build(definite.draw(seed))
        assert isinstance(inner.answer, AntiderivativeAnswer)
        assert isinstance(outer.answer, NumberAnswer)
        assert outer.steps[: len(inner.steps)] == inner.steps
        assert inner.answer.domain.contains(-1) and inner.answer.domain.contains(1)
        expected = sp.integrate(inner.answer.integrand, (X, -1, 1))
        assert expected.is_Rational
        assert Fraction(int(expected.p), int(expected.q)) == outer.answer.expected
        forms.add(inner.answer.integrand.as_numer_denom()[1].has(X))
    assert forms == {False, True}


def test_derivatives_cover_polynomial_and_rational_functions() -> None:
    generator = catalogue().get("derivative-v1")
    forms = set()
    for seed in range(12):
        task = generator.build(generator.draw(seed))
        assert isinstance(task.answer, DerivativeAnswer)
        # The first solution step records the function being differentiated.
        expression = task.metadata["function"]
        tree = parse_math_input(str(expression))
        from app.services.math_worker import _build_sympy

        original = _build_sympy(tree, evaluate=True)
        assert sp.simplify(task.answer.expected - sp.diff(original, X)) == 0
        forms.add(original.as_numer_denom()[1].has(X))
    assert forms == {False, True}


def test_combinations_use_exact_integer_arithmetic() -> None:
    generator = catalogue().get("combinations-v1")
    for seed in range(20):
        task = generator.build(generator.draw(seed))
        assert isinstance(task.answer, NumberAnswer)
        n, k = task.metadata["n"], task.metadata["k"]
        assert type(n) is int and type(k) is int and 0 <= k <= n
        assert task.answer.expected == math.comb(n, k)
        assert task.answer.check(parse_math_input(str(math.comb(n, k)))) == "correct"


def test_combination_generation_and_check_do_not_load_sympy() -> None:
    script = (
        "import sys; from app.engine.generators.combinations import Combinations; "
        "from app.services.math_parser import parse_math_input; "
        "g = Combinations(); task = g.build(g.draw(123)); "
        "assert task.answer.check(parse_math_input(str(task.answer.expected))) == 'correct'; "
        "assert 'sympy' not in sys.modules"
    )
    result = subprocess.run(  # noqa: S603 - fixed Python command without a shell
        (sys.executable, "-c", script), capture_output=True, timeout=5, check=False
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")


def test_rational_antiderivative_accepts_its_result_and_rejects_wrong_answer() -> None:
    generator = catalogue().get("indefinite-v1")
    task = generator.build(generator.draw(0))
    answer = task.answer
    assert isinstance(answer, AntiderivativeAnswer)
    assert answer.integrand.as_numer_denom()[1].has(X)
    source = str(answer.primitive).replace("**", "^").replace("log", "ln").replace("Abs", "abs")
    assert answer.check(parse_math_input(source + "+C")) == "correct"
    assert answer.check(parse_math_input(source)) == "missing_constant"
    assert answer.check(parse_math_input("x+C")) == "incorrect"
