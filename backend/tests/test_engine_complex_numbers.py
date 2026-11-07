"""#221: complex answers in algebraic form and algebra30 exercises 41-51."""

import sys

import pytest
import sympy as sp
from pydantic import ValidationError
from seed_sweep import sweep

from app.engine.answers.complex import ComplexAnswer
from app.engine.generators.complex_numbers import (
    NICE,
    ComplexArgument,
    ComplexLinearEquation,
    ComplexProduct,
    ComplexQuadratic,
    ComplexQuotient,
    ComplexRoot,
    ComplexSquareRoot,
    DeMoivre,
    DeMoivreParams,
    LinearParams,
    PairParams,
    PolarParams,
    QuadraticParams,
    RootParams,
    SquareRootParams,
    generators,
)
from app.engine.opening import rebuild
from app.engine.practice import input_variables, replay
from app.engine.topics.catalogue import topics
from app.math_input import MathInputError, parse_math_input
from app.services.math_worker import check_answer

TOPIC_OF = {
    ComplexProduct.version: ("complex-arithmetic", 1),
    ComplexQuotient.version: ("complex-arithmetic", 2),
    ComplexLinearEquation.version: ("complex-arithmetic", 3),
    ComplexSquareRoot.version: ("complex-arithmetic", 4),
    ComplexQuadratic.version: ("complex-arithmetic", 5),
    ComplexArgument.version: ("complex-polar-form", 1),
    DeMoivre.version: ("complex-polar-form", 2),
    ComplexRoot.version: ("complex-polar-form", 3),
}


def text(value: sp.Expr) -> str:
    return sp.sstr(value).replace("**", "^").replace("I", "i")


def check(task, answer: str) -> str:
    return task.answer.check(parse_math_input(answer, {"i"}))


def test_the_imaginary_unit_is_only_accepted_when_declared() -> None:
    with pytest.raises(MathInputError):
        parse_math_input("3+4i")
    with pytest.raises(MathInputError):
        parse_math_input("3+4i", {"x"})
    assert parse_math_input("3+4i", {"i"}).kind == "binary"


@pytest.mark.parametrize(
    "answer, outcome",
    [
        ("3-4i", "correct"),
        ("-4i+3", "correct"),
        ("3-4*i", "correct"),
        ("(6-8i)/2", "correct"),
        ("3+4i", "incorrect"),
        ("(2-i)^2", "incorrect"),  # equal, but not yet in the form a + bi
        ("25/(3+4i)", "incorrect"),
        ("3", "incorrect"),
        ("3-4i+0/(i-i)", "invalid"),
    ],
)
def test_complex_answers_require_the_algebraic_form(answer: str, outcome: str) -> None:
    assert ComplexAnswer(3 - 4 * sp.I).check(parse_math_input(answer, {"i"})) == outcome


def test_complex_answer_rejects_symbolic_expected_values() -> None:
    with pytest.raises(ValueError):
        ComplexAnswer(sp.Symbol("x") + sp.I)


def test_every_generator_is_offered_at_its_declared_level() -> None:
    declared = topics()
    assert {g.version for g in generators()} == set(TOPIC_OF)
    for version, (slug, level) in TOPIC_OF.items():
        assert version in {choice.generator for choice in declared[slug].levels[level]}
        assert declared[slug].mixed_weight == 1


@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.version)
def test_tasks_replay_open_and_accept_only_their_own_answer(generator) -> None:
    slug, level = TOPIC_OF[generator.version]
    for seed in sweep(200):
        params = generator.draw(seed)
        task = generator.build(params)
        assert task == generator.build(type(params).model_validate_json(params.model_dump_json()))
        assert task.metadata["difficulty"] == level
        expected = text(task.answer.expected)
        assert check(task, expected) == "correct"
        assert check(task, f"({expected})+1") == "incorrect"
        assert check(task, f"({expected})+i") == "incorrect"
    opened = rebuild(task.code)
    assert (opened.topic, opened.difficulty) == (slug, level)
    record = opened.problem.issued().record
    assert replay(record) == task
    assert input_variables(record) == {"i": "imaginary"}


def test_arithmetic_matches_pdf_exercise_41() -> None:
    task = ComplexProduct().build(PairParams(seed=0, first=(1, 1), second=(1, 1)))
    assert task.answer.expected == 2 * sp.I
    assert check(task, "2i") == "correct" and check(task, "(1+i)^2") == "incorrect"
    quotient = ComplexQuotient().build(PairParams(seed=0, first=(-4, 3), second=(-3, 4)))
    assert quotient.answer.expected == -4 + 3 * sp.I
    with pytest.raises(ValidationError):
        PairParams(seed=0, first=(1, 0), second=(1, 1))


def test_linear_equations_have_the_drawn_solution() -> None:
    z = sp.Symbol("z")
    for seed in sweep(300):
        params = ComplexLinearEquation().draw(seed)
        solution = params.solution[0] + params.solution[1] * sp.I
        assert ComplexLinearEquation().build(params).answer.expected == solution
    task = ComplexLinearEquation().build(
        LinearParams(seed=0, solution=(2, 3), coefficient=(3, 0), conjugate=True)
    )
    assert r"z+3\overline{z}=8 - 6 i" in task.statement
    assert sp.solve(z - (2 + 3 * sp.I), z) == [task.answer.expected]
    with pytest.raises(ValidationError):
        LinearParams(seed=0, solution=(1, 1), coefficient=(1, 0), conjugate=True)


def test_square_roots_and_quadratics_match_pdf_exercises_42c_and_51b() -> None:
    root = ComplexSquareRoot().build(SquareRootParams(seed=0, root=(1, 3)))
    assert r"z^{2}=-8 + 6 i" in root.statement and root.answer.expected == 1 + 3 * sp.I
    quadratic = ComplexQuadratic().build(QuadraticParams(seed=0, roots=((2, -1), (1, 2))))
    assert r"z^{2}+(-3 - i)z+(4 + 3 i)=0" in quadratic.statement
    assert quadratic.answer.expected == 2 - sp.I
    with pytest.raises(ValidationError):
        QuadraticParams(seed=0, roots=((1, 2), (1, -2)))


def test_quadratic_roots_solve_the_equation() -> None:
    z = sp.Symbol("z")
    for seed in sweep(300):
        params = ComplexQuadratic().draw(seed)
        (a, b), (c, d) = params.roots
        first, second = a + b * sp.I, c + d * sp.I
        roots = sp.solve(sp.expand((z - first) * (z - second)), z)
        assert ComplexQuadratic().build(params).answer.expected == max(roots, key=sp.re)


def test_polar_form_matches_pdf_exercises_45_46_and_49() -> None:
    angle = NICE.index(4 * sp.pi / 3)
    argument = ComplexArgument().build(PolarParams(seed=0, angle=angle, scale=1))
    assert argument.answer.expected == -2 * sp.pi / 3
    assert argument.answer.check(parse_math_input("-2pi/3", {"i"})) == "correct"
    assert argument.answer.check(parse_math_input("4pi/3", {"i"})) == "incorrect"
    power = DeMoivre().build(DeMoivreParams(seed=0, base=0, power=20))
    assert power.answer.expected == -1024
    assert check(power, "-1024") == "correct" and check(power, "((1+i)^10)^2") == "incorrect"
    root = ComplexRoot().build(RootParams(seed=0, order=2, angle=NICE.index(sp.pi / 4), scale=1))
    assert r"z^{2}=i" in root.statement
    assert root.answer.expected == sp.sqrt(2) / 2 + sp.sqrt(2) * sp.I / 2
    with pytest.raises(ValidationError):
        RootParams(seed=0, order=4, angle=NICE.index(sp.pi), scale=1)


def test_arguments_and_roots_are_independently_correct() -> None:
    for seed in sweep(300):
        argument = ComplexArgument().build(ComplexArgument().draw(seed))
        assert -sp.pi < argument.answer.expected <= sp.pi
        params = ComplexRoot().draw(seed)
        task = ComplexRoot().build(params)
        root = task.answer.expected
        roots = [
            sp.expand(
                params.scale * sp.exp(sp.I * (NICE[params.angle] + 2 * sp.pi * k / params.order))
            )
            for k in range(params.order)
        ]
        assert all(sp.arg(r) % (2 * sp.pi) >= sp.arg(root) % (2 * sp.pi) for r in roots)


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.version)
def test_complex_answers_are_checked_in_the_limited_worker(generator) -> None:
    task = generator.build(generator.draw(147))
    record = {"generator_version": generator.version, "code": task.code}
    answer = text(task.answer.expected)
    assert check_answer(answer, record).result == "correct"
    assert check_answer(f"({answer})+1", record).result == "incorrect"
