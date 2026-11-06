import pytest

from app.engine import practice
from app.engine.generators.matrix_full import FullMatrixMultiply


def test_multiplication_generator_covers_square_and_rectangular_inputs():
    generator = FullMatrixMultiply()
    shapes = set()
    for seed in range(150):
        params = generator.draw(seed)
        task = generator.build(params)
        shapes.add((len(params.first), len(params.first[0]), len(params.second[0])))
        expected = tuple(
            tuple(
                sum(params.first[i][k] * params.second[k][j] for k in range(len(params.second)))
                for j in range(len(params.second[0]))
            )
            for i in range(len(params.first))
        )
        assert task.answer.expected == expected
        expanded = next(step.latex for step in task.steps if step.text_key == "expand")
        assert expanded.count(r"\cdot") == len(params.first) * len(params.second[0]) * len(
            params.second
        )
    assert shapes == {(2, 2, 2), (3, 3, 3), (2, 3, 2)}


@pytest.mark.parametrize(
    ("operation", "size"),
    [
        ("add", "2x2"),
        ("add", "3x3"),
        ("subtract", "2x2"),
        ("subtract", "3x3"),
        ("multiply", "2x2"),
        ("multiply", "3x3"),
        ("multiply", "rectangular"),
    ],
)
def test_basic_selection_respects_both_settings(operation, size):
    issued = practice.issue(
        "matrix-operations", 1, seed=3, matrix_options={"operation": operation, "size": size}
    )
    assert practice.matrix_classification(issued.record) == (operation, size)


def test_unavailable_combination_does_not_fall_back():
    with pytest.raises(ValueError):
        practice.issue(
            "matrix-operations", 1, matrix_options={"operation": "add", "size": "rectangular"}
        )


@pytest.mark.parametrize(
    ("level", "operation", "size"),
    [
        (2, "multiply", "rectangular"),
        (2, "mixed", "rectangular"),
        (3, "multiply", "2x2"),
        (3, "mixed", "2x2"),
    ],
)
def test_higher_levels_respect_settings(level, operation, size):
    issued = practice.issue(
        "matrix-operations",
        level,
        seed=3,
        matrix_options={"operation": operation, "size": size},
    )
    assert practice.matrix_classification(issued.record) == (operation, size)


def test_saved_generation_passes_settings_and_keeps_answer_private(monkeypatch):
    import json
    from contextlib import nullcontext
    from datetime import UTC, datetime
    from types import SimpleNamespace
    from uuid import uuid4

    from app.api import practice as api
    from app.core.auth import VerifiedUser

    monkeypatch.setattr(api, "transaction", lambda _user: nullcontext(object()))
    monkeypatch.setattr(api.generation_limit, "check", lambda _user: None)
    monkeypatch.setattr(api.records, "ensure_profile", lambda *_args: None)
    monkeypatch.setattr(api.idempotency, "claim", lambda *_args: None)
    monkeypatch.setattr(api.idempotency, "store", lambda *_args: None)
    monkeypatch.setattr(api.records, "recent_generator_data", lambda *_args: [])

    captured = []

    def insert(_conn, _user, topic, difficulty, statement, solution):
        captured.append(solution.generator_data)
        return SimpleNamespace(
            id=uuid4(),
            topic=topic,
            difficulty=difficulty,
            problem_latex=statement,
            created_at=datetime.now(UTC),
            answer_revealed=False,
            solution_revealed=False,
            generator_data=solution.generator_data,
        )

    monkeypatch.setattr(api.records, "insert_problem", insert)
    settings = api.MatrixOptions(operation="multiply", size="3x3")
    body = api.GenerateBody(topic="matrix-operations", difficulty=1, matrixOptions=settings)
    response = api.generate(body, VerifiedUser(uuid4(), None), str(uuid4()))
    problem = json.loads(response.body)["problem"]
    assert response.status_code == 201
    assert problem["answerInput"]["kind"] == "tuple"
    assert "answerLatex" not in problem and "solution" not in problem
    assert practice.matrix_classification(captured[0]) == ("multiply", "3x3")
