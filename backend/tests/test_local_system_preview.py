import sympy as sp
from fastapi.testclient import TestClient

from local_matrix_preview import _task, app
from local_system_generator import LocalSystemGenerator, system_seed


def test_system_generation_and_checking() -> None:
    client = TestClient(app)
    generator = LocalSystemGenerator()
    for level in (1, 2, 3):
        for size in range(2, 6):
            for variation in range(3):
                params = generator.draw(system_seed(level, size, variation))
                task = generator.build(params)
                assert sp.Matrix(params.matrix).det() != 0
                assert _task(task.code).answer == task.answer
                answer = "(" + ";".join(map(str, params.solution)) + ")"
                wrong = (
                    "(" + ";".join(map(str, (params.solution[0] + 1, *params.solution[1:]))) + ")"
                )
                assert (
                    client.post("/check", json={"code": task.code, "answer": answer}).json()[
                        "result"
                    ]
                    == "correct"
                )
                assert (
                    client.post("/check", json={"code": task.code, "answer": wrong}).json()[
                        "result"
                    ]
                    == "incorrect"
                )
    response = client.post("/generate", json={"level": 2, "systemSize": 3})
    assert response.status_code == 200
    task = response.json()
    assert task["answerInput"]["kind"] == "tuple"
    steps = client.post("/reveal-solution", json={"code": task["code"]}).json()["steps"]
    assert len(steps) >= 3
    assert "x_1" in steps[-1]["latex"]
