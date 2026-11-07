import sympy as sp
from fastapi.testclient import TestClient

from app.engine.codes import parse_code
from local_matrix_preview import _registry, _task, app
from local_modulus_generator import (
    VARIATIONS,
    CircleParameters,
    LocalModulusCircle,
    LocalModulusPractice,
    ModulusPracticeParameters,
)


def test_modulus_modes_generate_replay_and_check() -> None:
    client = TestClient(app)
    for mode in ("expression", "properties", "geometry"):
        for level in (1, 2, 3):
            response = client.post(
                "/generate", json={"level": level, "complexModulus": True, "modulusMode": mode}
            )
            assert response.status_code == 200, response.text
            problem = response.json()
            task = _task(problem["code"])
            parsed = parse_code(problem["code"], _registry())
            generator = _registry().get_code(parsed.prefix, parsed.version)
            params = generator.draw(parsed.seed)
            if mode == "geometry":
                answer = f"({params.center_x};{params.center_y};{params.radius})"
                assert problem["answerInput"]["kind"] == "tuple"
            else:
                answer = str(task.answer.expected).replace("**", "^")
            result = client.post("/check", json={"code": task.code, "answer": answer})
            assert result.json()["result"] == "correct", (mode, answer, result.json())
            solution = client.post("/reveal-solution", json={"code": task.code}).json()
            assert len(solution["steps"]) >= 4
            assert solution["steps"][0]["say"] == "Write the original expression."
            assert all(step["say"] and step["latex"] for step in solution["steps"])
            if mode == "geometry":
                visual = solution["visual"]
                assert visual["mode"] == "circle"
                assert visual["first"] == [float(params.center_x), float(params.center_y)]
                assert visual["radius"] == float(params.radius)
            if mode == "properties":
                rules = [rule for step in solution["steps"] for rule in step.get("rules", [])]
                assert any("modulus" in rule["title"].lower() for rule in rules)


def test_geometry_rejects_wrong_radius() -> None:
    client = TestClient(app)
    problem = client.post(
        "/generate", json={"level": 2, "complexModulus": True, "modulusMode": "geometry"}
    ).json()
    parsed = parse_code(problem["code"], _registry())
    params = _registry().get_code(parsed.prefix, parsed.version).draw(parsed.seed)
    wrong = f"({params.center_x};{params.center_y};{sp.simplify(params.radius + 1)})"
    assert (
        client.post("/check", json={"code": problem["code"], "answer": wrong}).json()["result"]
        == "incorrect"
    )


def test_known_values_and_circle_coordinates() -> None:
    generator = LocalModulusPractice()
    examples = (
        ("expression", 1, sp.sqrt(26)),
        ("expression", 2, sp.sqrt(5) * sp.sqrt(17)),
        ("expression", 3, sp.sqrt(5) / sp.sqrt(17)),
        ("properties", 1, sp.sqrt(5) * sp.sqrt(17)),
        ("properties", 2, 5 * sp.sqrt(17)),
        ("properties", 3, 5 * sp.sqrt(5) / sp.sqrt(17)),
    )
    for mode, level, expected in examples:
        params = ModulusPracticeParameters(seed=0, mode=mode, level=level, a=1, b=2, c=4, d=-1)
        assert sp.simplify(generator.build(params).answer.expected - expected) == 0

    circle = CircleParameters(seed=0, level=3, a=2, b=-3, c=3, d=4, scale=2)
    task = LocalModulusCircle().build(circle)
    assert tuple(part.expected for part in task.answer.components) == (
        sp.Integer(1),
        sp.Rational(-3, 2),
        sp.Rational(5, 2),
    )


def test_generated_results_against_modulus_identities() -> None:
    generator = LocalModulusPractice()
    for index in range(6):
        for variation in range(12):
            params = generator.draw(index * VARIATIONS + variation)
            z = params.a + params.b * sp.I
            w = params.c + params.d * sp.I
            expected = (
                (sp.Abs(z + w), sp.Abs(z) * sp.Abs(w), sp.Abs(z) / sp.Abs(w))
                if params.mode == "expression"
                else (sp.Abs(z) * sp.Abs(w), sp.Abs(z) ** 2 * sp.Abs(w), sp.Abs(z) ** 3 / sp.Abs(w))
            )[params.level - 1]
            assert sp.simplify(generator.build(params).answer.expected - expected) == 0
