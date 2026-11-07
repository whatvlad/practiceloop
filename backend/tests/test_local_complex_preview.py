import sympy as sp
from fastapi.testclient import TestClient

from local_complex_generator import (
    OPERATIONS,
    ComplexParameters,
    LocalComplexGenerator,
    colored_complex,
    complex_seed,
)
from local_matrix_preview import _task, app


def test_complex_operations_replay_and_check() -> None:
    client = TestClient(app)
    generator = LocalComplexGenerator()
    for operation in OPERATIONS:
        for level in (1, 2, 3):
            for variation in range(12):
                params = generator.draw(complex_seed(level, operation, variation))
                task = generator.build(params)
                a, b = params.first
                c, d = params.second
                z, w = a + b * sp.I, c + d * sp.I
                expected = {
                    "add": z + w,
                    "subtract": z - w,
                    "multiply": z * w,
                    "divide": z / w,
                }[operation]
                assert sp.simplify(task.answer.expected - expected) == 0
                assert r"\color" not in task.statement
                assert any(r"\color" in step.latex for step in task.steps)
                assert _task(task.code).answer == task.answer
                real, imag = map(sp.simplify, sp.expand_complex(expected).as_real_imag())
                answer = f"({real})+({imag})*i"
                assert (
                    client.post("/check", json={"code": task.code, "answer": answer}).json()[
                        "result"
                    ]
                    == "correct"
                )
                assert (
                    client.post("/check", json={"code": task.code, "answer": "999"}).json()[
                        "result"
                    ]
                    == "incorrect"
                )
    response = client.post("/generate", json={"level": 2, "complexOperation": "divide"})
    assert response.status_code == 200
    task = response.json()
    steps = client.post("/reveal-solution", json={"code": task["code"]}).json()["steps"]
    assert any("conjugate" in step["say"] for step in steps)
    assert "Write the answer" not in task["statement"]
    assert r"\color{" not in task["statement"]
    assert r"\color{#65adff}" in colored_complex(1 + 2 * sp.I)
    assert r"\color{#ffb65c}" in colored_complex(1 + 2 * sp.I)
    assert any(r"\color{" in step["latex"] for step in steps)
    assert (
        client.post(
            "/generate", json={"level": 1, "complexOperation": "divide", "systemSize": 2}
        ).status_code
        == 422
    )


def test_division_explains_numerator_denominator_and_fraction() -> None:
    params = ComplexParameters(
        seed=complex_seed(1, "divide", 0),
        level=1,
        operation="divide",
        first=(1, 2),
        second=(2, 2),
    )
    task = LocalComplexGenerator().build(params)
    assert task.answer.expected == sp.Rational(3, 4) + sp.Rational(1, 4) * sp.I
    assert [step.text_key for step in task.steps] == [
        "rewrite",
        "conjugate",
        "numerator_expand",
        "numerator_square",
        "denominator_expand",
        "denominator_square",
        "fraction",
        "split",
        "result",
    ]
    assert r"\dfrac" in task.steps[1].latex
    assert task.steps[1].latex.count(r"\left(") == 4
    assert r"\color{#65adff}{\left(1 + 2 i\right)}" in task.steps[1].latex
    assert r"\color{#ffb65c}{\left(2 - 2 i\right)}" in task.steps[1].latex
    assert "i^2" in task.steps[2].latex and "i^2" in task.steps[4].latex
    assert "8" in task.steps[5].latex
    assert all(LocalComplexGenerator.step_text[step.text_key] for step in task.steps)


def test_missing_parts_are_explicit_in_the_solution() -> None:
    generator = LocalComplexGenerator()
    for operation in OPERATIONS:
        params = ComplexParameters(
            seed=complex_seed(1, operation, 0),
            level=1,
            operation=operation,
            first=(0, 3),
            second=(2, 0),
        )
        task = generator.build(params)
        assert task.steps[0].text_key == "rewrite"
        assert task.steps[1].text_key == "standard"
        assert r"\color{#65adff}{0}" in task.steps[1].latex
        assert r"\color{#ffb65c}{3i}" in task.steps[1].latex
        assert r"\color{#ffb65c}{0i}" in task.steps[1].latex
        assert r"\color" not in task.statement
