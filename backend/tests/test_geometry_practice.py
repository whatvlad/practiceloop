"""Hand-derived geometry fixtures and independent incidence invariants."""

import pytest
import sympy as sp
from seed_sweep import sweep

from app.engine.answers.computational import CategoryAnswer, FormulaAnswer, OrderedAnswer
from app.engine.answers.geometry import (
    ParametricGeometryAnswer,
    PlaneEquationAnswer,
    VectorSetAnswer,
)
from app.engine.generators.geometry_practice import (
    MODES,
    GeometryParameters,
    GeometryPractice,
    geometry_seed,
)
from app.math_input.computational import parse_computational


def fixture(level=1, variation=0):
    return GeometryParameters(
        seed=geometry_seed(level, variation),
        level=level,
        p=(1, 2, 3),
        u=(1, 0, 0),
        v=(0, 1, 0),
        w=(1, 1, 1),
        k=2,
    )


def check_task(mode, answer, level=1, variation=0):
    generator = GeometryPractice(mode)
    task = generator.build(fixture(level, variation))
    tree = parse_computational(answer, generator.input_contract(fixture(level, variation)))
    return task.answer.check(tree)


def test_collinearity_does_not_assume_every_generated_triple_is_collinear():
    assert check_task("point-collinearity", "collinear") == "correct"
    assert check_task("point-collinearity", "not_collinear", variation=1) == "correct"


@pytest.mark.parametrize("mode", ["point-collinearity", "unit-perpendiculars"])
def test_vector_difficulty_requires_additional_reconstruction_instead_of_larger_numbers(mode):
    generator = GeometryPractice(mode)
    works = [generator.work(fixture(level)) for level in (1, 2, 3)]
    assert len(works[0].steps) < len(works[1].steps) < len(works[2].steps)


@pytest.mark.parametrize(
    "mode", ["planes-common-point", "planes-common-line", "planes-three-lines"]
)
def test_parameter_diagrams_satisfy_their_explicit_representative_case(mode):
    generator = GeometryPractice(mode)
    for seed in sweep(8):
        params = generator.draw(geometry_seed(3, seed))
        work = generator.work(params)
        p, u, v, w = map(sp.Matrix, (params.p, params.u, params.v, params.w))
        normal = params.k * u + v + (w if mode == "planes-common-point" else sp.zeros(3, 1))
        rhs = (params.k * u + v).dot(p) + (1 if mode == "planes-three-lines" else 0)
        objects = {(o.kind, o.label): o for step in work.steps for o in step.objects}
        plane = objects["plane", "pi three"]
        assert normal.dot(plane.point) == rhs
        assert all(normal.dot(direction) == 0 for direction in plane.vectors)
        if mode == "planes-common-point":
            meeting = objects["point", "S"].point
            assert u.dot(meeting - p) == v.dot(meeting - p) == 0
            assert normal.dot(meeting) == rhs
        elif mode == "planes-three-lines":
            for label, first_normal, second_normal, first_rhs, second_rhs in (
                ("l12", u, v, u.dot(p), v.dot(p)),
                ("l13", u, normal, u.dot(p), rhs),
                ("l23", v, normal, v.dot(p), rhs),
            ):
                line = objects["line", label]
                assert first_normal.dot(line.point) == first_rhs
                assert second_normal.dot(line.point) == second_rhs
                assert first_normal.dot(line.vectors[0]) == second_normal.dot(line.vectors[0]) == 0


def test_prescribed_parallel_vector_keeps_sign_and_all_coordinates():
    assert check_task("parallel-vector", "(2/3;2/3;2/3)") == "correct"
    assert check_task("parallel-vector", "(-2/3;-2/3;-2/3)") == "incorrect"


def test_all_unit_perpendiculars_include_both_orientations():
    assert check_task("unit-perpendiculars", "((0;0;-1);(0;0;1))") == "correct"
    assert check_task("unit-perpendiculars", "((0;0;1);(0;0;1))") == "incorrect"


def test_volume_constraint_has_two_solutions_not_just_the_positive_branch():
    assert check_task("constrained-vector", "((0;1;2);(0;1;-2))") == "correct"


@pytest.mark.parametrize(
    "mode", ["point-collinearity", "parallel-vector", "unit-perpendiculars", "constrained-vector"]
)
@pytest.mark.parametrize("level", [1, 2, 3])
def test_vector_variants_reproduce_and_have_complete_explained_steps(mode, level):
    generator = GeometryPractice(mode)
    params = generator.draw(geometry_seed(level, 7))
    task = generator.build(params)
    assert task == generator.build(generator.draw(geometry_seed(level, 7)))
    assert task.steps and all(step.text_key in generator.step_text for step in task.steps)
    assert task.metadata["difficulty"] == level
    work = generator.work(params)
    assert len(work.steps) == len(task.steps)
    assert all(step.rule and step.explanation for step in work.steps)
    assert generator.input_contract(params) == task.answer.contract


def test_difficulty_adds_reconstruction_before_the_core_vector_method():
    generator = GeometryPractice("parallel-vector")
    assert len(generator.build(fixture(1)).steps) < len(generator.build(fixture(2)).steps)
    assert len(generator.build(fixture(2)).steps) < len(generator.build(fixture(3)).steps)


@pytest.mark.parametrize(
    ("mode", "answer"),
    [
        ("plane-equation", "2*z-6"),
        ("plane-parameterisation", "(s;t;3)"),
        ("line-equation", "(t;t+1;t+2)"),
        ("containing-plane", "z-3"),
        ("perpendicular-line", "(1;2;t)"),
        ("parallel-parameter", "0"),
        ("normal-parameters", "(-3/4;-8)"),
        ("planes-common-point", "(3;4)"),
        ("planes-common-line", "(3;4)"),
        ("planes-three-lines", "(3;4)"),
    ],
)
def test_lines_planes_and_parameter_conditions_against_hand_derived_fixtures(mode, answer):
    assert check_task(mode, answer) == "correct"


@pytest.mark.parametrize(
    "mode",
    [
        "plane-equation",
        "plane-parameterisation",
        "line-equation",
        "containing-plane",
        "perpendicular-line",
        "parallel-parameter",
        "normal-parameters",
        "planes-common-point",
        "planes-common-line",
        "planes-three-lines",
    ],
)
@pytest.mark.parametrize("level", [1, 2, 3])
def test_construction_levels_have_matching_safe_contracts_and_reconstruct_their_data(mode, level):
    generator = GeometryPractice(mode)
    p = generator.draw(geometry_seed(level, 5))
    work = generator.work(p)
    assert work.answer.contract == generator.input_contract(p)
    assert work.steps[-1].key in {"check", "condition"}
    assert all(step.rule and step.explanation for step in work.steps)


@pytest.mark.parametrize(
    ("mode", "answer"),
    [
        ("line-angle", "45"),
        ("plane-angle", "45"),
        ("point-line-distance", "sqrt(2)"),
        ("point-plane-distance", "1"),
        ("parallel-line-distance", "sqrt(2)"),
        ("skew-line-distance", "1"),
        ("parallel-plane-distance", "1"),
        ("line-line-intersection", "(3;2;3)"),
        ("line-plane-intersection", "(1/2;2;3)"),
        ("equidistant-plane", "z-5"),
        ("point-line-projection", "(2;2;3)"),
        ("point-plane-projection", "(2;3;3)"),
        ("line-plane-projection", "(2+2*t;3+t;3)"),
        ("directed-point-line-projection", "(3;2;3)"),
        ("directed-point-plane-projection", "(-1;2;3)"),
        ("directed-line-plane-projection", "(-1-t;2+t;3)"),
        ("line-reflection", "(2;1;2)"),
        ("plane-reflection", "(2;3;2)"),
        ("same-side", "same_side"),
    ],
)
def test_distances_angles_projections_and_reflections_against_exact_coordinates(mode, answer):
    assert check_task(mode, answer) == "correct"


@pytest.mark.parametrize(
    ("mode", "answers"),
    [
        ("line-position", ("intersecting", "parallel", "skew", "coincident")),
        ("line-plane-position", ("crossing", "parallel", "contained")),
    ],
)
def test_relative_position_keeps_distinct_geometric_cases(mode, answers):
    for variation, answer in enumerate(answers):
        assert check_task(mode, answer, variation=variation) == "correct"


@pytest.mark.parametrize(
    "mode",
    [
        "point-line-distance",
        "point-plane-distance",
        "parallel-line-distance",
        "skew-line-distance",
        "parallel-plane-distance",
    ],
)
def test_zero_distance_is_a_valid_case_not_a_generation_error(mode):
    assert check_task(mode, "0", variation=4) == "correct"


def answer_text(answer):
    def scalar(value):
        return sp.sstr(value).replace("**", "^")

    if isinstance(answer, FormulaAnswer):
        return scalar(answer.expected)
    if isinstance(answer, CategoryAnswer):
        return answer.expected
    if isinstance(answer, PlaneEquationAnswer):
        return scalar(
            sum(c * sp.Symbol(n) for c, n in zip(answer.normal, "xyz", strict=False))
            + answer.offset
        )
    if isinstance(answer, ParametricGeometryAnswer):
        symbols = sp.symbols(" ".join(answer.parameters), seq=True)
        return (
            "("
            + ";".join(
                scalar(
                    answer.point[i]
                    + sum(t * d[i] for t, d in zip(symbols, answer.directions, strict=False))
                )
                for i in range(3)
            )
            + ")"
        )
    if isinstance(answer, VectorSetAnswer):
        return (
            "(" + ";".join("(" + ";".join(scalar(x) for x in v) + ")" for v in answer.vectors) + ")"
        )
    assert isinstance(answer, OrderedAnswer)
    return "(" + ";".join(answer_text(x) for x in answer.components) + ")"


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("level", [1, 2, 3])
def test_every_variant_has_an_expressible_exact_answer_and_independent_geometric_checks(
    mode, level
):
    for seed in sweep(8):
        generator = GeometryPractice(mode)
        p = generator.draw(geometry_seed(level, seed))
        work = generator.work(p)
        answer = work.answer
        assert answer.contract == generator.input_contract(p)
        assert answer.check(parse_computational(answer_text(answer), answer.contract)) == "correct"
        point, u, v, w = (sp.Matrix(a) for a in (p.p, p.u, p.v, p.w))
        normal = u.cross(v)
        if mode == "parallel-vector":
            result = sp.Matrix([a.expected for a in answer.components])
            assert result.cross(w) == sp.zeros(3, 1) and result.dot(w) == p.k
        elif mode == "unit-perpendiculars":
            if level == 1:
                u, v = (
                    next(o.vectors[0] for o in work.givens if o.label == name)
                    for name in ("u", "v")
                )
            for result in map(sp.Matrix, answer.vectors):
                assert sp.simplify(result.dot(result)) == 1
                assert sp.simplify(result.dot(u)) == sp.simplify(result.dot(v)) == 0
        elif mode == "constrained-vector":
            for result in map(sp.Matrix, answer.vectors):
                assert sp.simplify(result.dot(u)) == 0
                assert sp.simplify(result.dot(v) - (v.dot(v) - u.dot(v) ** 2 / u.dot(u))) == 0
                assert (
                    sp.simplify(
                        abs(sp.Matrix.hstack(result, u, v).det()) - p.k * normal.dot(normal)
                    )
                    == 0
                )
        elif mode in {"plane-equation", "containing-plane", "plane-parameterisation"}:
            if isinstance(answer, PlaneEquationAnswer):
                n = sp.Matrix(answer.normal)
                assert (
                    n.dot(point) + answer.offset
                    == n.dot(point + u) + answer.offset
                    == n.dot(point + v) + answer.offset
                    == 0
                )
            else:
                assert normal.dot(sp.Matrix(answer.point) - point) == 0
                assert all(normal.dot(sp.Matrix(d)) == 0 for d in answer.directions)
        elif mode in {
            "point-line-distance",
            "parallel-line-distance",
            "point-plane-distance",
            "parallel-plane-distance",
        }:
            source = point + (u if seed % 5 == 4 else w)
            objects = [*work.givens, *(o for s in work.steps for o in s.objects)]
            foot = next(o.point for o in reversed(objects) if o.kind == "point" and o.label == "H")
            delta = source - foot
            assert sp.simplify(delta.dot(delta) - answer.expected**2) == 0
            if mode in {"point-line-distance", "parallel-line-distance"}:
                assert (foot - point).cross(u) == sp.zeros(3, 1) and delta.dot(u) == 0
            else:
                assert normal.dot(foot - point) == 0 and delta.cross(normal) == sp.zeros(3, 1)
        elif mode in {"line-plane-projection", "directed-line-plane-projection"}:
            source = point + w
            direction = u + w if mode == "line-plane-projection" else u + v + w
            projection = normal if mode == "line-plane-projection" else w + p.k * u
            assert normal.dot(sp.Matrix(answer.point) - point) == 0
            assert normal.dot(sp.Matrix(answer.directions[0])) == 0
            for parameter in (0, 1, -2):
                original = source + parameter * direction
                image = sp.Matrix(answer.point) + parameter * sp.Matrix(answer.directions[0])
                assert (original - image).cross(projection) == sp.zeros(3, 1)
