"""#221: algebra30 determinants, inverses, linear systems and rank (exercises 14-40)."""

import sys
from itertools import permutations

import pytest
import sympy as sp
from pydantic import ValidationError
from seed_sweep import sweep

from app.engine.generators.linear_algebra import (
    CramerRule,
    CramerRule3,
    Determinant3,
    Determinant4,
    DeterminantParams,
    DeterminantRowOperations,
    DeterminantScaling,
    FreeParameters,
    GaussianElimination,
    GaussianElimination4,
    InverseEntry,
    InverseEntry3,
    InverseParams,
    MatrixEquation,
    MatrixRank,
    NontrivialParams,
    NontrivialSolutions,
    RankParams,
    RowOperationParams,
    ScalingParams,
    SingularParameter,
    SingularParams,
    SystemParams,
    generators,
)
from app.engine.opening import rebuild
from app.engine.practice import input_variables, replay
from app.engine.topics.catalogue import topics
from app.math_input import MathInputError, parse_math_input
from app.services.math_worker import check_answer

TOPIC_OF = {
    Determinant3.version: ("determinants", 1),
    DeterminantScaling.version: ("determinants", 2),
    DeterminantRowOperations.version: ("determinants", 2),
    SingularParameter.version: ("determinants", 3),
    Determinant4.version: ("determinants", 4),
    InverseEntry.version: ("inverse-matrices", 1),
    InverseEntry3.version: ("inverse-matrices", 2),
    MatrixEquation.version: ("inverse-matrices", 3),
    CramerRule.version: ("linear-systems", 1),
    CramerRule3.version: ("linear-systems", 2),
    GaussianElimination.version: ("linear-systems", 3),
    GaussianElimination4.version: ("linear-systems", 4),
    NontrivialSolutions.version: ("linear-systems", 5),
    MatrixRank.version: ("matrix-rank", 1),
    FreeParameters.version: ("matrix-rank", 2),
}


def answer_text(value: sp.Expr) -> str:
    return sp.sstr(value).replace("**", "^")


def check(task, text: str) -> str:
    return task.answer.check(parse_math_input(text))


def test_every_generator_is_offered_at_its_declared_level() -> None:
    declared = topics()
    assert {g.version for g in generators()} == set(TOPIC_OF)
    for version, (slug, level) in TOPIC_OF.items():
        assert version in {choice.generator for choice in declared[slug].levels[level]}
        assert declared[slug].area == "algebra" and declared[slug].mixed_weight == 1


@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.version)
def test_tasks_replay_open_and_accept_only_their_own_answer(generator) -> None:
    slug, level = TOPIC_OF[generator.version]
    for seed in sweep(200):
        params = generator.draw(seed)
        task = generator.build(params)
        assert task == generator.build(type(params).model_validate_json(params.model_dump_json()))
        assert task.metadata["difficulty"] == level
        expected = task.answer.expected
        assert check(task, answer_text(expected)) == "correct"
        assert check(task, f"2*({answer_text(expected)})/2") == "correct"
        assert check(task, f"({answer_text(expected)})+1") == "incorrect"
    opened = rebuild(task.code)
    assert (opened.topic, opened.difficulty) == (slug, level)
    assert replay(opened.problem.issued().record) == task
    # The worker reads the grammar from the code before parsing an answer.
    input_variables(opened.problem.issued().record)


def test_determinants_match_an_independent_expansion() -> None:
    for generator in (Determinant3(), Determinant4()):
        for seed in sweep(300):
            params = generator.draw(seed)
            matrix = sp.Matrix([list(row) for row in params.matrix])
            assert generator.build(params).answer.expected == matrix.det(method="lu")


def test_four_by_four_determinant_has_a_row_with_two_zeros() -> None:
    with pytest.raises(ValidationError):
        DeterminantParams(seed=0, matrix=((1, 2, 3, 4),) * 4)
    with pytest.raises(ValidationError):
        DeterminantParams(seed=0, matrix=((5, 0, 0), (0, 1, 0), (0, 0, 1)))


def test_determinant_scaling_matches_pdf_exercise_15() -> None:
    task = DeterminantScaling().build(
        ScalingParams(seed=0, size=7, determinant=2, scale=2, power=1, transpose=False)
    )
    assert task.answer.expected == 256
    squared = DeterminantScaling().build(
        ScalingParams(seed=0, size=7, determinant=2, scale=-1, power=2, transpose=True)
    )
    assert squared.answer.expected == -4
    with pytest.raises(ValidationError):
        ScalingParams(seed=0, size=7, determinant=0, scale=2, power=1, transpose=False)


def test_row_operations_match_pdf_exercise_14() -> None:
    order = tuple(permutations(range(3)))
    generator = DeterminantRowOperations()
    swapped = RowOperationParams(
        seed=0,
        determinant=6,
        order=order.index((2, 0, 1)),
        scales=(1, 1, 1),
        target=0,
        source=1,
        multiple=0,
    )
    assert generator.build(swapped).answer.expected == 6
    scaled = swapped.model_copy(update={"order": 0, "scales": (3, -1, 4)})
    assert generator.build(scaled).answer.expected == -72
    transposed_rows = swapped.model_copy(update={"order": order.index((0, 2, 1))})
    assert generator.build(transposed_rows).answer.expected == -6
    with pytest.raises(ValidationError):
        RowOperationParams(
            seed=0, determinant=6, order=0, scales=(1, 0, 1), target=0, source=1, multiple=0
        )


def test_singular_parameter_matches_pdf_exercise_19k() -> None:
    params = SingularParams(seed=0, matrix=((3, -1, 0), (5, -2, 3), (-1, 0, -1)), row=0, column=2)
    task = SingularParameter().build(params)
    assert task.answer.expected == 2
    with pytest.raises(ValidationError):
        SingularParams(seed=0, matrix=((0, 1, 1), (0, 1, 1), (0, 1, 1)), row=0, column=0)


def test_inverse_entries_match_pdf_exercises_20_and_21() -> None:
    task = InverseEntry().build(InverseParams(seed=0, matrix=((1, 2), (3, 4)), row=1, column=0))
    assert task.answer.expected == sp.Rational(3, 2)
    assert check(task, "6/4") == "correct" and check(task, "3/4") == "incorrect"
    other = InverseEntry().build(InverseParams(seed=0, matrix=((3, 4), (1, 2)), row=0, column=1))
    assert other.answer.expected == -2
    with pytest.raises(ValidationError):
        InverseParams(seed=0, matrix=((1, 2), (2, 4)), row=0, column=0)


def test_inverse_entries_are_entries_of_the_inverse() -> None:
    for generator in (InverseEntry(), InverseEntry3()):
        for seed in sweep(300):
            params = generator.draw(seed)
            inverse = sp.Matrix([list(row) for row in params.matrix]).inv()
            task = generator.build(params)
            assert task.answer.expected == inverse[params.row, params.column]


def test_matrix_equations_solve_for_the_unknown_matrix() -> None:
    generator = MatrixEquation()
    for seed in sweep(300):
        params = generator.draw(seed)
        a = sp.Matrix([list(row) for row in params.matrix])
        x = sp.Matrix([list(row) for row in params.unknown])
        assert a.det() != 0
        assert generator.build(params).answer.expected == x[params.row, params.column]


def test_gaussian_elimination_matches_pdf_exercise_31a() -> None:
    params = SystemParams(
        seed=0, matrix=((1, 0, -1), (3, 1, 0), (-1, 1, 1)), solution=(-1, 4, -1), target=1
    )
    task = GaussianElimination().build(params)
    assert task.answer.expected == 4
    assert r"x-z=0\\3x+y=1\\-x+y+z=4" in task.statement
    cramer = CramerRule3().build(params)
    assert cramer.answer.expected == 4


def test_systems_have_the_drawn_unique_solution() -> None:
    for generator in (CramerRule(), CramerRule3(), GaussianElimination(), GaussianElimination4()):
        for seed in sweep(300):
            params = generator.draw(seed)
            a = sp.Matrix([list(row) for row in params.matrix])
            b = a * sp.Matrix(params.solution)
            assert list(a.LUsolve(b)) == list(params.solution)
            task = generator.build(params)
            assert task.answer.expected == params.solution[params.target]
    with pytest.raises(ValidationError):
        SystemParams(seed=0, matrix=((1, 2), (2, 4)), solution=(1, 1), target=0)
    with pytest.raises(ValidationError):
        SystemParams(seed=0, matrix=((1, 0), (0, 1)), solution=(5, 1), target=0)


def test_rank_and_free_parameters_follow_kronecker_capelli() -> None:
    seen = set()
    for seed in sweep(300):
        params = MatrixRank().draw(seed)
        matrix = sp.Matrix([list(row) for row in params.matrix])
        assert MatrixRank().build(params).answer.expected == matrix.rank() == params.rank
        system = FreeParameters().draw(seed)
        assert system.solution is not None
        assert FreeParameters().build(system).answer.expected == 4 - system.rank
        seen.add(params.rank)
    assert seen == {1, 2, 3}
    with pytest.raises(ValidationError):
        RankParams(seed=0, matrix=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0)), rank=3)


def test_nontrivial_solutions_match_pdf_exercise_37() -> None:
    task = NontrivialSolutions().build(
        NontrivialParams(seed=0, matrix=((3, 2), (4, 5)), eigenvalues=(1, 7))
    )
    assert task.answer.expected == 7
    with pytest.raises(ValidationError):
        NontrivialParams(seed=0, matrix=((3, 2), (4, 5)), eigenvalues=(2, 2))


def test_malformed_and_variable_answers_are_rejected() -> None:
    task = Determinant3().build(Determinant3().draw(147))
    with pytest.raises(MathInputError):
        parse_math_input("1+")
    assert check(task, "x") in {"invalid", "incorrect"}


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.version)
def test_linear_algebra_answers_are_checked_in_the_limited_worker(generator) -> None:
    task = generator.build(generator.draw(147))
    record = {"generator_version": generator.version, "code": task.code}
    answer = answer_text(task.answer.expected)
    assert check_answer(answer, record).result == "correct"
    assert check_answer(f"({answer})+1", record).result == "incorrect"
