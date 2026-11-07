import sympy as sp
from fastapi.testclient import TestClient

from local_matrix_preview import _task, app


def test_polar_preview_modes_check_answers_and_replay() -> None:
    client = TestClient(app)
    for mode in ("argument", "power", "root"):
        for _ in range(10):
            response = client.post("/generate", json={"level": 1, "polarMode": mode})
            assert response.status_code == 200
            problem = response.json()
            task = _task(problem["code"])
            answer = sp.sstr(task.answer.expected).replace("**", "^").replace("I", "i")
            checked = client.post("/check", json={"code": problem["code"], "answer": answer})
            assert checked.json()["result"] == "correct", (mode, answer, checked.json())
            steps = client.post("/reveal-solution", json={"code": problem["code"]}).json()["steps"]
            assert len(steps) >= 4
            assert steps[0]["say"] == "Write the original expression."
        assert (
            client.post(
                "/generate", json={"level": 1, "polarMode": mode, "complexModulus": True}
            ).status_code
            == 422
        )


def test_de_moivre_shows_conversion_formula_and_angle_reduction() -> None:
    from app.engine.generators.complex_numbers import DeMoivreParams
    from local_polar_steps import de_moivre_steps

    steps = de_moivre_steps(DeMoivreParams(seed=0, base=0, power=10))
    assert len(steps) == 12
    assert all(step["say"] and step["latex"] for step in steps)
    assert r"a=1" in steps[1]["latex"] and r"b=1" in steps[1]["latex"]
    assert r"\sqrt{2}" in steps[2]["latex"]
    assert r"\frac{\pi}{4}" in steps[4]["latex"]
    assert r"r^n" in steps[6]["latex"]
    assert r"\frac{5 \pi}{2}" in steps[9]["latex"]
    assert r"\frac{\pi}{2}" in steps[9]["latex"]
    assert steps[-1]["latex"].endswith("32 i")


def test_complex_visual_is_returned_only_with_solution() -> None:
    client = TestClient(app)
    cases = [
        ({"level": 1, "complexOperation": "add"}, "add"),
        ({"level": 1, "complexModulus": True}, "modulus"),
        ({"level": 1, "polarMode": "argument"}, "argument"),
        ({"level": 1, "polarMode": "power"}, "power"),
        ({"level": 1, "polarMode": "root"}, "root"),
    ]
    for request, mode in cases:
        generated = client.post("/generate", json=request).json()
        assert "visual" not in generated
        data = client.post("/reveal-solution", json={"code": generated["code"]}).json()
        visual = data["visual"]
        assert visual["kind"] == "complex-plane" and visual["mode"] == mode
        assert len(visual["first"]) == 2
        task = _task(generated["code"])
        if visual["result"] is not None:
            actual = complex(*visual["result"])
            assert abs(actual - complex(task.answer.expected.evalf())) < 1e-6
        if mode == "power":
            assert 5 <= visual["power"] <= 20


def test_complex_solutions_explain_topic_specific_formulas() -> None:
    client = TestClient(app)
    cases = [
        ({"level": 1, "complexOperation": "divide"}, "Division by a complex number"),
        ({"level": 1, "complexModulus": True}, "Modulus of a complex number"),
        ({"level": 1, "conversion": "trig-exp"}, "Euler's formula"),
        ({"level": 1, "polarMode": "power"}, "De Moivre's formula"),
        ({"level": 1, "polarMode": "root"}, "Roots of a nonzero complex number"),
    ]
    for request, title in cases:
        problem = client.post("/generate", json=request).json()
        steps = client.post("/reveal-solution", json={"code": problem["code"]}).json()["steps"]
        assert "rules" not in steps[0]
        rules = [rule for step in steps for rule in step.get("rules", [])]
        assert title in {rule["title"] for rule in rules}
        assert all(rule["latex"] and rule["explanation"] for rule in rules)
