import sympy as sp
from fastapi.testclient import TestClient

from app.engine.generators.complex_numbers import NICE, _principal, _rectangular
from local_conversion_generator import (
    DIRECTIONS,
    VARIATIONS,
    LocalConversionGenerator,
    LocalConversionToPolarGenerator,
)
from local_matrix_preview import _task, app


def test_all_conversions_and_answer_checks() -> None:
    client = TestClient(app)
    for level in (1, 2, 3):
        for index, direction in enumerate(DIRECTIONS):
            generator = (
                LocalConversionGenerator()
                if direction.endswith("-alg")
                else LocalConversionToPolarGenerator()
            )
            for variation in range(4):
                seed = ((level - 1) * len(DIRECTIONS) + index) * VARIATIONS + variation
                params = generator.draw(seed)
                task = generator.build(params)
                assert _task(task.code).answer == task.answer
                assert task.steps[0].text_key == "rewrite"
                assert all(generator.step_text[step.text_key] for step in task.steps)
                phi = _principal(NICE[params.angle])
                z = _rectangular(params.modulus, phi)
                answer = (
                    sp.sstr(z).replace("**", "^").replace("I", "i")
                    if direction.endswith("-alg")
                    else f"({params.modulus};{phi})"
                )
                result = client.post("/check", json={"code": task.code, "answer": answer}).json()
                assert result["result"] == "correct", (direction, answer, result)
                wrong = "999" if direction.endswith("-alg") else f"(999;{phi})"
                assert (
                    client.post("/check", json={"code": task.code, "answer": wrong}).json()[
                        "result"
                    ]
                    == "incorrect"
                )
    for direction in DIRECTIONS:
        response = client.post("/generate", json={"level": 2, "conversion": direction})
        assert response.status_code == 200
        task = response.json()
        assert ("answerInput" in task) == (not direction.endswith("-alg"))
        if not direction.endswith("-alg"):
            answer_latex = client.post("/reveal-answer", json={"code": task["code"]}).json()
            assert answer_latex["answerLatex"].startswith("z=")
        solution = client.post("/reveal-solution", json={"code": task["code"]}).json()
        assert solution["visual"]["kind"] == "complex-plane"
        assert solution["steps"][0]["say"] == "Write the original expression."
