import sympy as sp
from fastapi.testclient import TestClient

from local_matrix_preview import _task, app
from local_rank_generator import LocalRankGenerator, rank_seed


def test_rank_generation_and_checking() -> None:
    client = TestClient(app)
    generator = LocalRankGenerator()
    observed = set()
    for level in (1, 2, 3):
        for rows, columns in ((2, 2), (2, 5), (5, 2), (5, 5)):
            for variation in range(5):
                params = generator.draw(rank_seed(level, rows, columns, variation))
                task = generator.build(params)
                expected = sp.Matrix(params.matrix).rank()
                observed.add(expected)
                assert task.answer.expected == expected
                assert _task(task.code).answer.expected == expected
                assert (
                    client.post("/check", json={"code": task.code, "answer": str(expected)}).json()[
                        "result"
                    ]
                    == "correct"
                )
                assert (
                    client.post(
                        "/check", json={"code": task.code, "answer": str(expected + 1)}
                    ).json()["result"]
                    == "incorrect"
                )
    assert 0 in observed and len(observed) >= 3
    response = client.post(
        "/generate", json={"level": 2, "rankDimensions": {"rows": 3, "columns": 5}}
    )
    assert response.status_code == 200
    solution = client.post("/reveal-solution", json={"code": response.json()["code"]}).json()[
        "steps"
    ]
    assert "rank" in solution[-1]["latex"]
