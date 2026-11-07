import sympy as sp
from fastapi.testclient import TestClient

from local_matrix_preview import _task, app
from local_polynomial_roots_generator import VARIATIONS, LocalPolynomialRootsGenerator, X


def test_real_roots_generation_replay_and_check() -> None:
    client = TestClient(app)
    generator = LocalPolynomialRootsGenerator()
    repeated = set()
    for level in (1, 2, 3):
        for variation in range(20):
            params = generator.draw((level - 1) * VARIATIONS + variation)
            task = generator.build(params)
            residual = X**2 + params.extra if params.extra else 1
            polynomial = sp.expand(residual * sp.prod(X - root for root in params.roots))
            actual = set(sp.polys.polytools.real_roots(polynomial))
            assert actual == set(task.answer.expected)
            assert _task(task.code).answer == task.answer
            answer = "{" + ",".join(map(str, reversed(task.answer.expected))) + "}"
            assert (
                client.post("/check", json={"code": task.code, "answer": answer}).json()["result"]
                == "correct"
            )
            assert (
                client.post("/check", json={"code": task.code, "answer": "{99}"}).json()["result"]
                == "incorrect"
            )
            assert task.steps[0].text_key == "rewrite"
            assert any(step.text_key == "factorization" for step in task.steps)
            repeated.add(len(set(params.roots)) < len(params.roots))
            if params.extra:
                assert any(step.text_key == "nonreal" for step in task.steps)
    assert repeated == {True, False}
    generated = client.post("/generate", json={"level": 2, "polynomialRoots": True})
    assert generated.status_code == 200
    assert generated.json()["answerInput"]["kind"] == "finite_set"
    steps = client.post("/reveal-solution", json={"code": generated.json()["code"]}).json()["steps"]
    assert any(
        rule["title"] == "Rational root theorem" for step in steps for rule in step.get("rules", [])
    )
    assert (
        client.post(
            "/generate", json={"level": 2, "polynomialRoots": True, "polynomialMode": "division"}
        ).status_code
        == 422
    )


def test_zero_root_is_factored_before_nonzero_candidates() -> None:
    from local_polynomial_roots_generator import RootParameters

    params = RootParameters(seed=0, level=1, roots=(1, 0), extra=0)
    task = LocalPolynomialRootsGenerator().build(params)
    keys = [step.text_key for step in task.steps]
    assert keys[:4] == ["rewrite", "evaluate", "factor", "candidates"]
    assert "0" in task.steps[1].latex
    assert set(task.answer.expected) == {0, 1}
