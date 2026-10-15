import pytest
from sympy import diff, simplify

from app.generators.basic import X, generate_basic


@pytest.mark.parametrize("coefficient", [-20, -7, -1, 1, 3, 20])
@pytest.mark.parametrize("power", range(9))
def test_all_fixture_parameters_have_correct_antiderivative(coefficient: int, power: int) -> None:
    problem = generate_basic(coefficient, power)
    assert simplify(diff(problem.antiderivative, X) - problem.integrand) == 0
    assert problem.answer_latex.endswith(" + C")
    assert problem.solution_steps[-1] == problem.answer_latex


def test_deterministic() -> None:
    assert generate_basic(3, 4) == generate_basic(3, 4)


def test_public_projection_never_contains_solution_or_parameters() -> None:
    public = generate_basic(3, 4).public().model_dump()
    assert set(public) == {"topic", "problem_latex"}


@pytest.mark.parametrize("coefficient,power", [(0, 1), (21, 1), (1, -1), (1, 9), (True, 1)])
def test_invalid_parameters(coefficient: int, power: int) -> None:
    with pytest.raises(ValueError):
        generate_basic(coefficient, power)


@pytest.mark.parametrize("payload", ["__import__('os')", "x**(9**9)", "sin(x)", "3"])
def test_no_string_parameter_evaluation(payload: str) -> None:
    with pytest.raises(ValueError):
        generate_basic(payload, 2)  # type: ignore[arg-type]
