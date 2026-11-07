from fastapi.testclient import TestClient

from local_matrix_preview import _task, app


def test_preview_uses_real_generator_and_does_not_reveal_answer_until_requested() -> None:
    client = TestClient(app)
    generated = client.post(
        "/generate", json={"level": 1, "matrixOptions": {"operation": "add", "size": "2x2"}}
    )
    assert generated.status_code == 200
    problem = generated.json()
    assert problem["generatorVersion"] == "matrix-sum-v2"
    assert "answer" not in problem and "solution" not in problem
    assert problem["answerInput"]["kind"] == "tuple"
    code = problem["code"]
    expected = _task(code).answer.expected
    answer = "(" + ";".join("(" + ";".join(map(str, row)) + ")" for row in expected) + ")"
    assert (
        client.post("/check", json={"code": code, "answer": answer}).json()["result"] == "correct"
    )
    answer_reveal = client.post("/reveal-answer", json={"code": code})
    assert answer_reveal.status_code == 200
    assert "answerLatex" in answer_reveal.json() and "steps" not in answer_reveal.json()
    solution_reveal = client.post("/reveal-solution", json={"code": code})
    assert solution_reveal.status_code == 200 and solution_reveal.json()["steps"]
    assert (
        client.post("/check", json={"code": code, "answer": "(1;2)"}).json()["result"] == "invalid"
    )
    assert (
        client.post("/check", json={"code": code, "answer": "x^99999"}).json()["result"]
        == "invalid"
    )


def test_preview_rejects_other_problem_codes() -> None:
    client = TestClient(app)
    assert client.post("/reveal-answer", json={"code": "invalid"}).status_code == 404


def test_preview_honours_multiplication_and_size() -> None:
    from app.engine.practice import matrix_classification

    client = TestClient(app)
    response = client.post(
        "/generate", json={"level": 1, "matrixOptions": {"operation": "multiply", "size": "3x3"}}
    )
    assert response.status_code == 200
    body = response.json()
    assert matrix_classification(
        {"code": body["code"], "generator_version": body["generatorVersion"]}
    ) == ("multiply", "3x3")
    invalid = client.post(
        "/generate", json={"level": 1, "matrixOptions": {"operation": "add", "size": "rectangular"}}
    )
    assert invalid.status_code == 422


def test_preview_checks_bounded_trigonometric_matrix_answers() -> None:
    from app.engine.generators.matrix_full import DetailedMatrixTrig

    generator = DetailedMatrixTrig()
    task = generator.build(generator.draw(8))
    answer = (
        "("
        + ";".join(
            "(" + ";".join(str(value).replace("**", "^") for value in row) + ")"
            for row in task.answer.expected
        )
        + ")"
    )
    client = TestClient(app)
    assert (
        client.post("/check", json={"code": task.code, "answer": answer}).json()["result"]
        == "correct"
    )
    assert (
        client.post("/check", json={"code": task.code, "answer": "((2^999;0);(0;1))"}).json()[
            "result"
        ]
        == "invalid"
    )


def test_custom_dimensions_generate_and_check_rectangular_and_large_matrices() -> None:
    client = TestClient(app)
    for operation, dimensions in (
        ("add", (2, 3, 2, 3)),
        ("multiply", (5, 3, 3, 5)),
        ("subtract", (5, 5, 5, 5)),
    ):
        a, b, c, d = dimensions
        payload = {
            "level": 2,
            "dimensions": {"operation": operation, "rowsA": a, "colsA": b, "rowsB": c, "colsB": d},
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 200
        task = _task(response.json()["code"])
        assert len(task.answer.expected) == a and len(task.answer.expected[0]) == d
        answer = (
            "("
            + ";".join("(" + ";".join(map(str, row)) + ")" for row in task.answer.expected)
            + ")"
        )
        assert (
            client.post("/check", json={"code": task.code, "answer": answer}).json()["result"]
            == "correct"
        )
        assert client.post("/reveal-solution", json={"code": task.code}).status_code == 200
    invalid = {
        "level": 1,
        "dimensions": {"operation": "multiply", "rowsA": 2, "colsA": 3, "rowsB": 2, "colsB": 2},
    }
    assert client.post("/generate", json=invalid).status_code == 422


def test_division_generates_invertible_b_and_checks_a_times_inverse() -> None:
    import sympy as sp

    from local_matrix_generator import LocalMatrixGenerator, make_seed

    generator = LocalMatrixGenerator()
    client = TestClient(app)
    response = client.post(
        "/generate",
        json={
            "level": 2,
            "dimensions": {"operation": "divide", "rowsA": 2, "colsA": 3, "rowsB": 3, "colsB": 3},
        },
    )
    assert response.status_code == 200
    assert response.json()["generatorVersion"] == "local-matrix-division-v3"
    assert r"\end{pmatrix}:\begin{pmatrix}" in response.json()["statement"]
    assert r"^{-1}" not in response.json()["statement"]
    for size in (1, 2, 3, 4, 5):
        for variation in range(5):
            seed = make_seed("divide", 3, (2, size, size, size), variation)
            params = generator.draw(seed)
            first, second = sp.Matrix(params.first), sp.Matrix(params.second)
            assert second.det() in (-1, 1)
            task = generator.build(params)
            assert sp.Matrix(task.answer.expected) == first * second.inv()
            assert _task(task.code).answer.expected == task.answer.expected
            answer = (
                "("
                + ";".join("(" + ";".join(map(str, row)) + ")" for row in task.answer.expected)
                + ")"
            )
            assert (
                client.post("/check", json={"code": task.code, "answer": answer}).json()["result"]
                == "correct"
            )
            steps = client.post("/reveal-solution", json={"code": task.code}).json()["steps"]
            assert any(r"\begin{array}" in step["latex"] for step in steps)
            assert any(r"A:B=A\cdot B^{-1}" in step["latex"] for step in steps)
    for dimensions in ((2, 3, 2, 2), (2, 3, 3, 2)):
        a, b, c, d = dimensions
        response = client.post(
            "/generate",
            json={
                "level": 1,
                "dimensions": {
                    "operation": "divide",
                    "rowsA": a,
                    "colsA": b,
                    "rowsB": c,
                    "colsB": d,
                },
            },
        )
        assert response.status_code == 422


def test_inverse_steps_show_row_operations_and_correct_inverse() -> None:
    import sympy as sp

    from local_matrix_generator import inverse_steps

    matrix = sp.Matrix([[0, 2], [1, 3]])
    steps = inverse_steps(matrix)
    assert [step.text_key for step in steps] == [
        "augment",
        "row_swap",
        "row_scale",
        "row_eliminate",
        "inverse",
    ]
    assert r"\begin{array}{cc|cc}" in steps[0].latex
    assert r"\frac{1}{2}" in steps[-1].latex


def test_division_generator_produces_nontriangular_invertible_matrices() -> None:
    import sympy as sp

    from local_matrix_generator import LocalMatrixDivisionGenerator, make_seed

    generator = LocalMatrixDivisionGenerator()
    client = TestClient(app)
    for size in range(2, 6):
        matrices = set()
        for variation in range(12):
            seed = make_seed("divide", 3, (size, size, size, size), variation)
            params = generator.draw(seed)
            matrices.add(params.second)
            assert params.second[1][0] != 0
            second = sp.Matrix(params.second)
            assert second.det() == 1
            task = generator.build(params)
            assert sp.Matrix(task.answer.expected) == sp.Matrix(params.first) * second.inv()
            assert _task(task.code).answer.expected == task.answer.expected
            answer = (
                "("
                + ";".join("(" + ";".join(map(str, row)) + ")" for row in task.answer.expected)
                + ")"
            )
            assert (
                client.post("/check", json={"code": task.code, "answer": answer}).json()["result"]
                == "correct"
            )
        assert len(matrices) > 1


def test_division_difficulty_controls_matrix_structure() -> None:
    import sympy as sp

    from local_matrix_generator import LeveledMatrixDivisionGenerator, make_seed

    client = TestClient(app)
    counts = {2: 0, 3: 0}
    for level in (1, 2, 3):
        response = client.post(
            "/generate",
            json={
                "level": level,
                "dimensions": {
                    "operation": "divide",
                    "rowsA": 4,
                    "colsA": 4,
                    "rowsB": 4,
                    "colsB": 4,
                },
            },
        )
        assert response.status_code == 200
        version = response.json()["generatorVersion"]
        assert version == ("local-matrix-sized-v1" if level == 1 else "local-matrix-division-v3")
        for variation in range(20):
            seed = make_seed("divide", level, (4, 4, 4, 4), variation)
            generator = _task_generator(version)
            params = generator.draw(seed)
            matrix = sp.Matrix(params.second)
            assert matrix.det() in (-1, 1)
            if level == 1:
                assert all(matrix[i, j] == 0 for i in range(4) for j in range(i))
            else:
                assert params.second[1][0] != 0
                counts[level] += sum(matrix[i, j] != 0 for i in range(4) for j in range(i))
                task = generator.build(params)
                assert sp.Matrix(task.answer.expected) == sp.Matrix(params.first) * matrix.inv()
                assert _task(task.code).answer.expected == task.answer.expected
    assert counts[3] > counts[2]
    generator = LeveledMatrixDivisionGenerator()
    for variation in range(10):
        params = generator.draw(make_seed("divide", 3, (5, 5, 5, 5), variation))
        task = generator.build(params)
        assert (
            sp.Matrix(task.answer.expected)
            == sp.Matrix(params.first) * sp.Matrix(params.second).inv()
        )
        answer = (
            "("
            + ";".join("(" + ";".join(map(str, row)) + ")" for row in task.answer.expected)
            + ")"
        )
        assert (
            client.post("/check", json={"code": task.code, "answer": answer}).json()["result"]
            == "correct"
        )


def _task_generator(version: str):
    from local_matrix_preview import _registry

    return _registry().get(version)
