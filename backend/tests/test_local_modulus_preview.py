import sympy as sp
from fastapi.testclient import TestClient

from local_matrix_preview import _task, app
from local_modulus_generator import VARIATIONS, LocalModulusGenerator


def test_modulus_generation_replay_and_answers() -> None:
    client = TestClient(app)
    generator = LocalModulusGenerator()
    for level in (1, 2, 3):
        for variation in range(30):
            params = generator.draw((level - 1) * VARIATIONS + variation)
            task = generator.build(params)
            expected = sp.sqrt(params.real**2 + params.imaginary**2)
            assert task.answer.expected == expected
            assert _task(task.code).answer == task.answer
            answer = str(expected).replace("**", "^")
            assert (
                client.post("/check", json={"code": task.code, "answer": answer}).json()["result"]
                == "correct"
            )
            assert task.steps[0].text_key == "rewrite"
            assert all(generator.step_text[step.text_key] for step in task.steps)
    response = client.post("/generate", json={"level": 2, "complexModulus": True})
    assert response.status_code == 200
    assert (
        len(client.post("/reveal-solution", json={"code": response.json()["code"]}).json()["steps"])
        == 6
    )


def test_equivalent_radical_denominator_is_accepted() -> None:
    from local_modulus_generator import LocalModulusGenerator

    client = TestClient(app)
    generator = LocalModulusGenerator()
    task = next(
        generator.build(generator.draw(i))
        for i in range(100)
        if generator.build(generator.draw(i)).answer.expected == sp.sqrt(2)
    )
    assert (
        client.post("/check", json={"code": task.code, "answer": "2/sqrt(2)"}).json()["result"]
        == "correct"
    )
    assert (
        client.post("/check", json={"code": task.code, "answer": "1/sqrt(0)"}).json()["result"]
        == "invalid"
    )


def test_rationalized_radical_denominator_is_accepted() -> None:
    from local_modulus_generator import LocalModulusGenerator

    client = TestClient(app)
    generator = LocalModulusGenerator()
    task = next(
        generator.build(generator.draw(i))
        for i in range(100)
        if generator.build(generator.draw(i)).answer.expected == 1
    )
    answer = "(1+sqrt(2))/(1+sqrt(2))"
    assert (
        client.post("/check", json={"code": task.code, "answer": answer}).json()["result"]
        == "correct"
    )
    assert (
        client.post("/check", json={"code": task.code, "answer": "1/(sqrt(2)-sqrt(2))"}).json()[
            "result"
        ]
        == "invalid"
    )
