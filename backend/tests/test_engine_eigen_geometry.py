"""#221: eigenvalues, vectors, lines and planes (algebra30 exercises 64-96)."""

import sys

import pytest
import sympy as sp
from pydantic import ValidationError

from app.engine.generators.eigen_geometry import (
    DiagonalPower,
    EigenParams,
    EigenvectorValue,
    LargestEigenvalue,
    LinePlaneIntersection,
    LinePlaneParams,
    MatrixFromEigenvectors,
    ParallelPlanesDistance,
    PlaneReflection,
    PlanesAngle,
    PlanesParams,
    PointPlaneDistance,
    PointsParams,
    ReflectionParams,
    TetrahedronHeight,
    TetrahedronVolume,
    TriangleAngle,
    TriangleArea,
    TriangularParams,
    TriangularPowerEigenvalue,
    TripleProduct,
    generators,
)
from app.engine.opening import rebuild
from app.engine.practice import input_variables, replay
from app.engine.topics.catalogue import topics
from app.math_input import parse_math_input
from app.services.math_worker import check_answer

TOPIC_OF = {
    LargestEigenvalue.version: ("eigenvalues", 1),
    EigenvectorValue.version: ("eigenvalues", 2),
    DiagonalPower.version: ("eigenvalues", 3),
    TriangularPowerEigenvalue.version: ("eigenvalues", 4),
    MatrixFromEigenvectors.version: ("eigenvalues", 5),
    TripleProduct.version: ("vectors", 1),
    TriangleAngle.version: ("vectors", 2),
    TriangleArea.version: ("vectors", 3),
    TetrahedronVolume.version: ("vectors", 4),
    TetrahedronHeight.version: ("vectors", 5),
    PointPlaneDistance.version: ("lines-and-planes", 1),
    ParallelPlanesDistance.version: ("lines-and-planes", 2),
    PlanesAngle.version: ("lines-and-planes", 3),
    LinePlaneIntersection.version: ("lines-and-planes", 4),
    PlaneReflection.version: ("lines-and-planes", 5),
}


def text(value: sp.Expr) -> str:
    return sp.sstr(value).replace("**", "^")


def check(task, answer: str) -> str:
    return task.answer.check(parse_math_input(answer))


def test_every_generator_is_offered_at_its_declared_level() -> None:
    declared = topics()
    assert {g.version for g in generators()} == set(TOPIC_OF)
    for version, (slug, level) in TOPIC_OF.items():
        assert version in {choice.generator for choice in declared[slug].levels[level]}
        assert declared[slug].mixed_weight == 1


@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.version)
def test_tasks_replay_open_and_accept_only_their_own_answer(generator) -> None:
    slug, level = TOPIC_OF[generator.version]
    for seed in range(150):
        params = generator.draw(seed)
        task = generator.build(params)
        assert task == generator.build(type(params).model_validate_json(params.model_dump_json()))
        assert task.metadata["difficulty"] == level
        expected = text(task.answer.expected)
        assert check(task, expected) == "correct"
        assert check(task, f"({expected})+1") == "incorrect"
    opened = rebuild(task.code)
    assert (opened.topic, opened.difficulty) == (slug, level)
    assert replay(opened.problem.issued().record) == task
    # The worker reads the grammar from the code before parsing an answer.
    input_variables(opened.problem.issued().record)


def test_eigen_tasks_match_pdf_exercises_64_66_67_and_69() -> None:
    # 65, 69: the largest root of the characteristic polynomial.
    symmetric = EigenParams(
        seed=0, basis=((1, 0), (1, 1)), eigenvalues=(4, -3), power=1, row=0, column=0
    )
    a = symmetric.matrix()
    assert LargestEigenvalue().build(symmetric).answer.expected == max(a.eigenvals())
    # 64: Av = lambda v for the drawn eigenvector.
    vector = EigenvectorValue().draw(3)
    task = EigenvectorValue().build(vector)
    assert task.answer.expected == vector.eigenvalues[vector.column]
    # 66: the eigenvalues of A^8 for a triangular A are the 8th powers of its diagonal.
    triangular = TriangularParams(
        seed=0, matrix=((1, 2, -2, 0), (0, 2, 3, 1), (0, 0, 2, 5), (0, 0, 0, 0)), power=8
    )
    assert TriangularPowerEigenvalue().build(triangular).answer.expected == 256
    # 67: eigenvalue 1 with (1, 2) and -1 with (2, 1) need a non-unimodular basis, so the
    # generator uses unimodular bases; the identity A v = lambda v is still checked.
    pairs = EigenParams(
        seed=0, basis=((1, 1), (1, 2)), eigenvalues=(1, -1), power=3, row=1, column=0
    )
    built = MatrixFromEigenvectors().build(pairs)
    assert built.answer.expected == pairs.matrix()[1, 0]
    with pytest.raises(ValidationError):
        EigenParams(seed=0, basis=((1, 2), (2, 1)), eigenvalues=(1, -1), power=1, row=0, column=0)
    with pytest.raises(ValidationError):
        TriangularParams(
            seed=0, matrix=((1, 0, 0, 0), (1, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), power=2
        )


def test_matrix_powers_match_direct_multiplication() -> None:
    for seed in range(200):
        params = DiagonalPower().draw(seed)
        power = params.matrix() ** params.power
        assert DiagonalPower().build(params).answer.expected == power[params.row, params.column]


def test_vector_tasks_match_pdf_exercises_72_73_78_and_79() -> None:
    # 72(i): (u x v) . w for u = (2, 1, 1), v = (1, -2, 2), w = (1, 3, -5).
    triple = PointsParams(seed=0, points=((0, 0, 0), (2, 1, 1), (1, -2, 2), (1, 3, -5)))
    assert (
        TripleProduct().build(triple).answer.expected
        == sp.Matrix([[2, 1, 1], [1, -2, 2], [1, 3, -5]]).det()
    )
    # 73: A = (-1, -2, 4), B = (-4, -2, 0), C = (3, -2, 1); the angle at B is 45 degrees.
    angle = TriangleAngle().build(
        PointsParams(seed=0, points=((-1, -2, 4), (-4, -2, 0), (3, -2, 1)))
    )
    assert sp.simplify(angle.answer.expected - 1 / sp.sqrt(2)) == 0
    assert check(angle, "sqrt(2)/2") == "correct" and check(angle, "1/sqrt(2)") == "correct"
    # 78(a): A = (1, 2, 0), B = (3, 0, -3), C = (5, 2, 6): area 7 sqrt(5) ... checked by Heron.
    area = TriangleArea().build(PointsParams(seed=0, points=((1, 2, 0), (3, 0, -3), (5, 2, 6))))
    ab, ac = sp.Matrix([2, -2, -3]), sp.Matrix([4, 0, 6])
    assert sp.simplify(area.answer.expected - ab.cross(ac).norm() / 2) == 0
    # 78(b): A = (2, -1, 1), B = (5, 5, 4), C = (3, 2, -1), D = (4, 1, 3): volume 3.
    volume = TetrahedronVolume().build(
        PointsParams(seed=0, points=((2, -1, 1), (5, 5, 4), (3, 2, -1), (4, 1, 3)))
    )
    assert volume.answer.expected == 3
    # 79: A = (0, 0, 2), B = (3, 0, 5), C = (1, 1, 0), D = (4, 1, 2): height 1/sqrt(11).
    height = TetrahedronHeight().build(
        PointsParams(seed=0, points=((0, 0, 2), (3, 0, 5), (1, 1, 0), (4, 1, 2)))
    )
    assert sp.simplify(height.answer.expected - 1 / sp.sqrt(11)) == 0
    with pytest.raises(ValidationError):
        PointsParams(seed=0, points=((0, 0, 0), (1, 1, 1), (2, 2, 2)))


def test_plane_tasks_match_pdf_exercises_82_86_89_and_96() -> None:
    # 86(e) style: 2x - y + 2z + 9 = 0 and 4x - 2y + 4z - 20 = 0 are 19/3 apart.
    planes = ParallelPlanesDistance().build(
        PlanesParams(seed=0, normal=(2, -1, 2), offsets=(9, -10), scale=2, second=(1, 0, 0))
    )
    assert r"4 x - 2 y + 4 z - 20=0" in planes.statement
    assert planes.answer.expected == sp.Rational(19, 3)
    # 89(c): 6x + 3y - 2z = 0 and x + 2y + 6z - 12 = 0 are perpendicular.
    angle = PlanesAngle().build(
        PlanesParams(seed=0, normal=(6, 3, -2), offsets=(0, -12), scale=1, second=(1, 2, 6))
    )
    assert angle.answer.expected == 0
    # 96 style: the reflection of P = (3, -4, -5) in the plane x = 0.
    image = PlaneReflection().build(
        ReflectionParams(seed=0, normal=(1, 0, 0), offset=0, point=(3, -4, -5), coordinate=0)
    )
    assert image.answer.expected == -3
    crossing = LinePlaneIntersection().build(
        LinePlaneParams(
            seed=0,
            point=(1, -3, 3),
            direction=(-2, 2, 1),
            normal=(2, -1, 3),
            parameter=1,
            coordinate=2,
        )
    )
    assert crossing.answer.expected == 4
    with pytest.raises(ValidationError):
        LinePlaneParams(
            seed=0,
            point=(0, 0, 0),
            direction=(1, 0, 0),
            normal=(0, 1, 0),
            parameter=0,
            coordinate=0,
        )


def test_distances_match_an_independent_projection() -> None:
    for seed in range(200):
        params = PointPlaneDistance().draw(seed)
        a, b, c, d = (sp.Matrix(p) for p in params.points)
        normal = (b - a).cross(c - a)
        expected = abs(normal.dot(d - a)) / normal.norm()
        task = PointPlaneDistance().build(params)
        assert sp.simplify(task.answer.expected - expected) == 0


@pytest.mark.skipif(sys.platform != "linux", reason="Linux resource limits")
@pytest.mark.parametrize("generator", generators(), ids=lambda g: g.version)
def test_geometry_answers_are_checked_in_the_limited_worker(generator) -> None:
    task = generator.build(generator.draw(147))
    record = {"generator_version": generator.version, "code": task.code}
    answer = text(task.answer.expected)
    assert check_answer(answer, record).result == "correct"
    assert check_answer(f"({answer})+1", record).result == "incorrect"
