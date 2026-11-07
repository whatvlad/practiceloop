import sympy as sp
from fastapi.testclient import TestClient

from local_matrix_preview import _task, app
from local_polynomial_extras import KINDS, VARIATIONS, PartialFractionsExtras, PolynomialExtras, X


def test_polynomial_extras_with_independent_algebra() -> None:
    client = TestClient(app)
    for level in (1, 2, 3):
        for index, kind in enumerate(KINDS):
            generator = PartialFractionsExtras() if kind == "fractions" else PolynomialExtras()
            for variation in range(6):
                params = generator.draw(((level - 1) * len(KINDS) + index) * VARIATIONS + variation)
                task = generator.build(params)
                assert task == _task(task.code)
                if kind == "fractions":
                    a, b = params.roots
                    A, B, C = params.coefficients
                    if level == 1:
                        numerator = sp.expand(A * (X - b) + B * (X - a))
                        identity = A / (X - a) + B / (X - b)
                        divisor = (X - a) * (X - b)
                    elif level == 2:
                        numerator = sp.expand(
                            A * (X - a) * (X - b) + B * (X - b) + C * (X - a) ** 2
                        )
                        identity = A / (X - a) + B / (X - a) ** 2 + C / (X - b)
                        divisor = (X - a) ** 2 * (X - b)
                    else:
                        numerator = sp.expand(A * (X**2 + abs(b)) + (B * X + C) * (X - a))
                        identity = A / (X - a) + (B * X + C) / (X**2 + abs(b))
                        divisor = (X - a) * (X**2 + abs(b))
                    assert sp.cancel(identity - numerator / divisor) == 0
                    answer = "(" + ";".join(str(v.expected) for v in task.answer.components) + ")"
                else:
                    answer = str(task.answer.expected).replace("**", "^")
                    if kind == "fundamental":
                        a, b = params.roots
                        assert task.answer.expected == sp.degree(
                            (X - a) ** level * (X - b) * (X**2 + 1), X
                        )
                check = client.post("/check", json={"code": task.code, "answer": answer}).json()
                assert check["result"] == "correct", (kind, answer, check)
            response = client.post("/generate", json={"level": level, "polynomialExtra": kind})
            assert response.status_code == 200
            task = response.json()
            assert ("answerInput" in task) == (kind == "fractions")
            solution = client.post("/reveal-solution", json={"code": task["code"]}).json()
            assert solution["steps"][0]["say"] == "Write the original problem."
            if kind in ("fundamental", "fractions"):
                assert any(step.get("rules") for step in solution["steps"])
