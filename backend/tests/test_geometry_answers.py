"""Geometric answers compare objects, including their complete affine spans."""

import pytest
import sympy as sp

from app.engine.answers.geometry import (
    ParametricGeometryAnswer,
    PlaneEquationAnswer,
    VectorSetAnswer,
)
from app.math_input.computational import parse_computational


def verdict(answer, text):
    return answer.check(parse_computational(text, answer.contract))


@pytest.mark.parametrize("text", ["x+2*y-z-3", "-2*x-4*y+2*z+6", "(x+2*y-z-3)/3"])
def test_plane_accepts_every_nonzero_constant_multiple(text):
    assert verdict(PlaneEquationAnswer((1, 2, -1), -3), text) == "correct"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("x+2*y-z+3", "incorrect"),
        ("0", "invalid"),
        ("(x+2*y-z-3)^2", "invalid"),
        ("(x+2*y-z-3)*x/x", "invalid"),
        ("sqrt(x^2)+2*y-z-3", "invalid"),
    ],
)
def test_plane_rejects_wrong_objects_or_undefined_and_nonaffine_equations(text, expected):
    assert verdict(PlaneEquationAnswer((1, 2, -1), -3), text) == expected


@pytest.mark.parametrize("text", ["(1+t;2+2*t;3-t)", "(3-2*t;6-4*t;1+2*t)"])
def test_line_accepts_shift_and_nonzero_change_of_parameter(text):
    line = ParametricGeometryAnswer((1, 2, 3), ((1, 2, -1),))
    assert verdict(line, text) == "correct"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("(1;2;3)", "incorrect"),
        ("(1+t;2+2*t;4-t)", "incorrect"),
        ("(1+t^2;2+2*t^2;3-t^2)", "invalid"),
        ("(1+t/t;2+2*t;3-t)", "invalid"),
    ],
)
def test_line_requires_the_whole_correct_line(text, expected):
    assert verdict(ParametricGeometryAnswer((1, 2, 3), ((1, 2, -1),)), text) == expected


def test_plane_parameterisation_accepts_another_origin_and_basis():
    plane = ParametricGeometryAnswer((0, 0, 3), ((1, 0, 1), (0, 1, 2)))
    assert verdict(plane, "(1+s+t;2+s-t;8+3*s-t)") == "correct"
    assert verdict(plane, "(s;2*s;3+5*s)") == "incorrect"
    assert verdict(plane, "(s;t;4+s+2*t)") == "incorrect"


def test_unordered_vectors_require_both_solutions_and_accept_equivalent_radicals():
    a = sp.sqrt(2) / 2
    pair = VectorSetAnswer(((a, -a, 0), (-a, a, 0)))
    assert verdict(pair, "((-1/sqrt(2);1/sqrt(2);0);(1/sqrt(2);-1/sqrt(2);0))") == "correct"
    assert verdict(pair, "((1/sqrt(2);-1/sqrt(2);0);(1/sqrt(2);-1/sqrt(2);0))") == "incorrect"


def test_trusted_geometries_reject_zero_normal_rank_loss_and_duplicate_solutions():
    with pytest.raises(ValueError):
        PlaneEquationAnswer((0, 0, 0), 3)
    with pytest.raises(ValueError):
        ParametricGeometryAnswer((0, 0, 0), ((1, 2, 3), (2, 4, 6)))
    with pytest.raises(ValueError):
        VectorSetAnswer(((1, 0, 0), (1, 0, 0)))
