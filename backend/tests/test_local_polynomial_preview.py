import sympy as sp
from fastapi.testclient import TestClient

from local_matrix_preview import _task, app
from local_polynomial_generator import (
    MODES,
    VARIATIONS,
    LocalPolynomialGenerator,
    LocalPolynomialScalarGenerator,
    X,
)


def test_polynomial_tasks_check_and_explain() -> None:
    client = TestClient(app)
    for level in (1, 2, 3):
        for index, mode in enumerate(MODES):
            generator = (
                LocalPolynomialGenerator()
                if mode == "division"
                else LocalPolynomialScalarGenerator()
            )
            for variation in range(8):
                params = generator.draw(((level - 1) * 3 + index) * VARIATIONS + variation)
                task = generator.build(params)
                assert _task(task.code).answer == task.answer
                assert task.steps[0].text_key == "rewrite"
                if mode == "division":
                    q, r = task.answer.components
                    divisor = sum(coef * X**i for i, coef in enumerate(params.divisor))
                    expected_q = sum(coef * X**i for i, coef in enumerate(params.quotient))
                    expected_r = sum(coef * X**i for i, coef in enumerate(params.remainder))
                    dividend = sp.expand(divisor * expected_q + expected_r)
                    quotient_check, remainder_check = sp.div(dividend, divisor, X)
                    assert sp.expand(q.expected - quotient_check) == 0
                    assert sp.expand(r.expected - remainder_check) == 0
                    quotient = sp.sstr(q.expected).replace("**", "^")
                    remainder = sp.sstr(r.expected).replace("**", "^")
                    answer = f"({quotient};{remainder})"
                    wrong = "(999;999)"
                    assert any(step.text_key == "subtract" for step in task.steps)
                else:
                    answer, wrong = str(task.answer.expected), "999"
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
            response = client.post("/generate", json={"level": level, "polynomialMode": mode})
            assert response.status_code == 200
            public = response.json()
            assert ("answerInput" in public) == (mode == "division")
            steps = client.post("/reveal-solution", json={"code": public["code"]}).json()["steps"]
            assert steps[0]["say"] == "Write the original problem."
            assert all(step["say"] and step["latex"] for step in steps)


def test_used_rules_are_attached_only_to_relevant_steps() -> None:
    client = TestClient(app)
    expected = {
        "division": {"Polynomial division theorem"},
        "remainder": set(),
        "divisibility": set(),
    }
    for mode, titles in expected.items():
        task = client.post("/generate", json={"level": 2, "polynomialMode": mode}).json()
        steps = client.post("/reveal-solution", json={"code": task["code"]}).json()["steps"]
        assert "rules" not in steps[0]
        rules = [rule for step in steps for rule in step.get("rules", [])]
        assert titles == {rule["title"] for rule in rules}
        assert all(rule["latex"] and rule["explanation"] for rule in rules)
