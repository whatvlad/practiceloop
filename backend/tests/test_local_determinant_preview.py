import sympy as sp
from fastapi.testclient import TestClient

from local_determinant_generator import (
    ColoredDeterminantGenerator,
    DetailedDeterminantGenerator,
    ExplainedDeterminantGenerator,
    LocalDeterminantGenerator,
    determinant_seed,
)
from local_matrix_preview import _task, app


def test_determinant_generator_and_preview_flow() -> None:
    client = TestClient(app)
    generator = LocalDeterminantGenerator()
    for level in (1, 2, 3):
        for size in (2, 3, 4, 5):
            for variation in range(4):
                seed = determinant_seed(level, size, variation)
                params = generator.draw(seed)
                task = generator.build(params)
                assert task.answer.expected == sp.Matrix(params.matrix).det()
                assert _task(task.code).answer.expected == task.answer.expected
                answer = str(task.answer.expected)
                assert (
                    client.post("/check", json={"code": task.code, "answer": answer}).json()[
                        "result"
                    ]
                    == "correct"
                )
                assert (
                    client.post(
                        "/check", json={"code": task.code, "answer": str(int(answer) + 1)}
                    ).json()["result"]
                    == "incorrect"
                )
            response = client.post("/generate", json={"level": level, "determinantSize": size})
            assert response.status_code == 200
            body = response.json()
            assert body["answerInput"]["kind"] == "formula"
            assert client.post("/reveal-solution", json={"code": body["code"]}).status_code == 200
    assert client.post("/generate", json={"level": 1, "determinantSize": 6}).status_code == 422


def test_determinant_generator_includes_singular_matrices() -> None:
    generator = LocalDeterminantGenerator()
    assert any(
        generator.build(generator.draw(determinant_seed(1, 2, i))).answer.expected == 0
        for i in range(100)
    )


def test_detailed_solution_shows_diagonals_for_all_three_by_three_minors() -> None:
    generator = DetailedDeterminantGenerator()
    client = TestClient(app)
    for size in (2, 3, 4, 5):
        params = generator.draw(determinant_seed(3, size, 25))
        task = generator.build(params)
        assert task.answer.expected == sp.Matrix(params.matrix).det()
        response = client.post("/reveal-solution", json={"code": task.code})
        assert response.status_code == 200
        steps = response.json()["steps"]
        visuals = [step["determinantMatrix"] for step in steps if "determinantMatrix" in step]
        assert visuals
        assert all(len(matrix) == (2 if size == 2 else 3) for matrix in visuals)
        for matrix in visuals:
            n = len(matrix)
            if n == 2:
                value = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
            else:
                positive = sum(
                    matrix[0][j] * matrix[1][(j + 1) % 3] * matrix[2][(j + 2) % 3] for j in range(3)
                )
                negative = sum(
                    matrix[2][j] * matrix[1][(j + 1) % 3] * matrix[0][(j + 2) % 3] for j in range(3)
                )
                value = positive - negative
            assert value == sp.Matrix(matrix).det()
        if size > 3:
            assert any("Row " in step["latex"] for step in steps)
        assert str(task.answer.expected) in steps[-1]["latex"]


def test_colored_groups_match_diagrams_without_changing_result() -> None:
    client = TestClient(app)
    colored = ColoredDeterminantGenerator()
    original = DetailedDeterminantGenerator()
    for size in (2, 3, 4, 5):
        params = colored.draw(determinant_seed(2, size, 17))
        task = colored.build(params)
        assert task.answer.expected == original.build(params).answer.expected
        response = client.post("/reveal-solution", json={"code": task.code})
        assert response.status_code == 200
        steps = response.json()["steps"]
        visual_steps = [step for step in steps if "determinantMatrix" in step]
        assert visual_steps
        for step in visual_steps:
            assert r"\color{#f17baa}" in step["latex"]
            assert r"\color{#759bff}" in step["latex"]
        evaluation = [step for step in steps if step["say"].startswith("Multiply the entries")]
        assert evaluation and all(r"\color{#f17baa}" in step["latex"] for step in evaluation)


def test_laplace_steps_describe_each_parent_and_selectable_minor() -> None:
    client = TestClient(app)
    generator = ColoredDeterminantGenerator()
    for size in (4, 5):
        params = generator.draw(determinant_seed(3, size, 25))
        task = generator.build(params)
        steps = client.post("/reveal-solution", json={"code": task.code}).json()["steps"]
        expansions = [step["minorExpansion"] for step in steps if "minorExpansion" in step]
        assert expansions and len(expansions[0]["matrix"]) == size
        if size == 5:
            assert any(len(expansion["matrix"]) == 4 for expansion in expansions)
        for expansion in expansions:
            matrix, row = expansion["matrix"], expansion["row"]
            assert expansion["columns"] == [i for i, value in enumerate(matrix[row]) if value]
            for col in expansion["columns"]:
                child = [
                    [value for j, value in enumerate(line) if j != col]
                    for i, line in enumerate(matrix)
                    if i != row
                ]
                assert len(child) == len(matrix) - 1


def test_explanations_include_sign_checkerboard_and_textbook_reasoning() -> None:
    client = TestClient(app)
    generator = ExplainedDeterminantGenerator()
    for size in (2, 3, 4, 5):
        params = generator.draw(determinant_seed(2, size, 25))
        task = generator.build(params)
        steps = client.post("/reveal-solution", json={"code": task.code}).json()["steps"]
        signs = steps[0]
        assert signs["latex"].count(r"\color{#65df91}{+}") == (size * size + 1) // 2
        assert signs["latex"].count(r"\color{#ff829d}{-}") == size * size // 2
        assert signs["say"].startswith("The top-left sign is positive")
        assert steps[-1]["say"].startswith("Simplifying the expression")
        assert task.answer.expected == sp.Matrix(params.matrix).det()
        if size > 3:
            expansions = [step for step in steps if "minorExpansion" in step]
            assert expansions
            for step in expansions:
                assert f"Row {step['minorExpansion']['row'] + 1}" in step["say"]
                assert "cofactor sign" in step["say"]


def test_equivalent_numeric_denominators_are_checked_safely() -> None:
    client = TestClient(app)
    generator = LocalDeterminantGenerator()
    task = next(
        generator.build(generator.draw(determinant_seed(1, 2, i)))
        for i in range(200)
        if generator.build(generator.draw(determinant_seed(1, 2, i))).answer.expected == -1
    )
    for answer in ("-1", "1/(-1)", "1/(0-1)"):
        assert (
            client.post("/check", json={"code": task.code, "answer": answer}).json()["result"]
            == "correct"
        )
    for answer in ("1/(1-1)", "1/(2-2)"):
        assert (
            client.post("/check", json={"code": task.code, "answer": answer}).json()["result"]
            == "invalid"
        )
