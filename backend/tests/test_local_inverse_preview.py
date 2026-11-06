import sympy as sp
from fastapi.testclient import TestClient

from local_inverse_generator import LocalInverseGenerator, inverse_seed
from local_matrix_preview import _task, app


def test_inverse_generation_and_answer_flow() -> None:
    generator = LocalInverseGenerator()
    client = TestClient(app)
    for level in (1, 2, 3):
        for size in (2, 3, 4, 5):
            seed = inverse_seed(level, size, 16)
            params = generator.draw(seed)
            task = generator.build(params)
            matrix = sp.Matrix(params.matrix)
            assert matrix.det() != 0
            assert matrix * sp.Matrix(task.answer.expected) == sp.eye(size)
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
            solution = client.post("/reveal-solution", json={"code": task.code}).json()["steps"]
            assert r"\det A=" in solution[0]["latex"]
            assert any(r"\begin{array}" in step["latex"] for step in solution)
            assert r"A^{-1}=" in solution[-1]["latex"]
            generated = client.post("/generate", json={"level": level, "inverseSize": size})
            assert generated.status_code == 200
            assert generated.json()["answerInput"]["kind"] == "tuple"
    assert client.post("/generate", json={"level": 1, "inverseSize": 6}).status_code == 422
