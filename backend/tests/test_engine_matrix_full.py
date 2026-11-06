"""Full-matrix answers preserve the earlier scalar generator versions."""

import pytest

from app.engine.generators.matrix_full import generators
from app.engine.opening import rebuild
from app.engine.practice import input_contract, input_projection, replay
from app.math_input.parser import MathInputError
from app.math_input.structured import parse_answer_input


@pytest.mark.parametrize("generator", generators(), ids=lambda generator: generator.version)
def test_full_matrix_is_replayable_and_checked_per_entry(generator) -> None:
    for seed in range(12):
        task = generator.build(generator.draw(seed))
        record = {"generator_version": generator.version, "code": task.code}
        assert replay(record) == task
        assert rebuild(task.code).problem.code == task.code
        contract = input_contract(record)
        assert contract == task.answer.contract
        projection = input_projection(record)["answerInput"]
        assert projection == contract.public()
        assert "expected" not in str(projection)
        matrix = task.answer.expected
        text = (
            "("
            + ";".join(
                "(" + ";".join(str(value).replace("**", "^") for value in row) + ")"
                for row in matrix
            )
            + ")"
        )
        assert task.answer.check(parse_answer_input(text, "tuple", contract=contract)) == "correct"
        altered = [list(row) for row in matrix]
        altered[0][0] += 1
        wrong = (
            "("
            + ";".join(
                "(" + ";".join(str(value).replace("**", "^") for value in row) + ")"
                for row in altered
            )
            + ")"
        )
        assert (
            task.answer.check(parse_answer_input(wrong, "tuple", contract=contract)) == "incorrect"
        )
        with pytest.raises(MathInputError):
            parse_answer_input("(1;2)", "tuple", contract=contract)


def test_original_scalar_code_still_opens() -> None:
    from app.engine.generators.matrix_operations import MatrixProduct

    old = MatrixProduct().build(MatrixProduct().draw(42))
    assert rebuild(old.code).problem.code == old.code
    assert replay({"generator_version": old.generator_version, "code": old.code}) == old


def test_basic_matrix_operations_cover_two_and_three_dimensions() -> None:
    from app.engine.generators.matrix_full import FullMatrixSum

    generator = FullMatrixSum()
    dimensions = set()
    operations = set()
    for seed in range(100):
        params = generator.draw(seed)
        task = generator.build(params)
        dimensions.add(len(params.first))
        operations.add(params.sign)
        assert task.statement.startswith(
            "Add the matrices:" if params.sign == 1 else "Subtract the matrices:"
        )
        assert task.answer.expected == tuple(
            tuple(a + params.sign * b for a, b in zip(first, second, strict=True))
            for first, second in zip(params.first, params.second, strict=True)
        )
    assert dimensions == {2, 3}
    assert operations == {-1, 1}


def test_trigonometric_matrix_checks_exact_symbolic_values() -> None:
    from app.engine.generators.matrix_full import FullMatrixTrig

    generator = FullMatrixTrig()
    for seed in range(6):
        task = generator.build(generator.draw(seed))
        assert task.answer.contract.components[0].components[0].symbols == (("theta", "real"),)
        text = (
            "("
            + ";".join(
                "(" + ";".join(str(value).replace("**", "^") for value in row) + ")"
                for row in task.answer.expected
            )
            + ")"
        )
        assert (
            task.answer.check(parse_answer_input(text, "tuple", contract=task.answer.contract))
            == "correct"
        )
        assert "theta" in text
        params = generator.draw(seed)
        alternate = [list(row) for row in task.answer.expected]
        alternate[0][0] = f"{params.first}+({params.second}-{params.first})*sin(theta)^2"
        equivalent = (
            "("
            + ";".join(
                "(" + ";".join(str(value).replace("**", "^") for value in row) + ")"
                for row in alternate
            )
            + ")"
        )
        assert (
            task.answer.check(
                parse_answer_input(equivalent, "tuple", contract=task.answer.contract)
            )
            == "correct"
        )


def test_five_by_five_matrix_contract_checks_every_entry() -> None:
    from app.engine.generators.matrix_full import MatrixAnswer
    from app.math_input.contracts import InputContract

    matrix = tuple(tuple(row * 5 + column for column in range(5)) for row in range(5))
    answer = MatrixAnswer(matrix)
    text = "(" + ";".join("(" + ";".join(map(str, row)) + ")" for row in matrix) + ")"
    assert answer.check(parse_answer_input(text, "tuple", contract=answer.contract)) == "correct"
    formula = InputContract("formula")
    row = InputContract("tuple", components=(formula,) * 5, labels=("Entry",) * 5)
    with pytest.raises(ValueError):
        InputContract("tuple", components=(row,) * 5, labels=("Other",) * 5)
