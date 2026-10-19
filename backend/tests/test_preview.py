import json
from itertools import product

import pytest
import sympy as sp
from fastapi.testclient import TestClient

from app.api import preview
from app.generators.basic import X
from app.generators.core import catalogue, replay
from app.main import app
from app.services.answer_check import check_tree, replay_problem
from app.services.math_parser import parse_math_input
from app.services.math_worker import MathCheckInconclusive, MathWorkerError
from app.services.preview_check import check_answer

CELLS = tuple(product(("basic-integrals", "substitution"), (1, 2)))


@pytest.fixture
def client():
    preview._sessions.clear()
    preview._requests.clear()
    with TestClient(app) as client:
        yield client


def headers(client):
    response = client.post("/preview/sessions")
    assert response.status_code == 201
    return {"Authorization": "Bearer " + response.json()["token"]}


@pytest.mark.parametrize("topic,level", CELLS)
def test_entire_catalogue_has_valid_replay_domain_clean_values_and_answers(topic, level):
    exercises = catalogue(topic, level)
    assert len(exercises) >= 36
    assert len({item.statement for item in exercises}) == len(exercises)
    for exercise in exercises:
        assert sp.simplify(sp.diff(exercise.primitive, X) - exercise.integrand) == 0
        assert exercise.primitive.is_real is True
        assert exercise.integrand.is_real is True
        assert not exercise.primitive.atoms(sp.Float)
        assert (
            max((abs(number.p) for number in exercise.primitive.atoms(sp.Rational)), default=0) <= 4
        )
        assert replay(json.loads(json.dumps(exercise.record))) == exercise
        source = str(exercise.primitive).replace("**", "^") + " + C"
        assert check_tree(parse_math_input(source), replay_problem(exercise.record)) == "correct"
        assert exercise.steps[-1]["latex"].endswith(" + C")


@pytest.mark.parametrize("topic,level", CELLS)
def test_no_repeats_until_pool_exhausted_and_no_adjacent_repeat_across_cycle(client, topic, level):
    auth = headers(client)
    statements = []
    for _ in range(len(catalogue(topic, level)) + 1):
        response = client.post(
            "/preview/problems", json={"topic": topic, "difficulty": level}, headers=auth
        )
        assert response.status_code == 201
        assert response.headers["cache-control"] == "no-store"
        problem = response.json()
        assert set(problem) == {
            "id",
            "topic",
            "difficulty",
            "problemLatex",
            "createdAt",
            "answerRevealed",
            "solutionRevealed",
            "lastResult",
            "lastAnswer",
        }
        statements.append(problem["problemLatex"])
    assert len(set(statements[:-1])) == len(statements) - 1
    assert statements[-1] != statements[-2]


def test_reveal_is_scoped_and_check_does_not_leak(client):
    auth = headers(client)
    problem = client.post(
        "/preview/problems", json={"topic": "basic-integrals", "difficulty": 1}, headers=auth
    ).json()
    path = f"/preview/problems/{problem['id']}"
    for suffix in ("reveal-answer", "reveal-solution", "attempts"):
        body = {"answer": "x+C"} if suffix == "attempts" else {}
        assert client.post(f"{path}/{suffix}", json=body).status_code == 401
        assert (
            client.post(f"{path}/{suffix}", json=body, headers=headers(client)).status_code == 404
        )
    assert set(client.post(f"{path}/reveal-answer", headers=auth).json()) == {"answerLatex"}
    assert set(client.post(f"{path}/reveal-solution", headers=auth).json()) == {"steps"}
    response = client.post(f"{path}/attempts", headers=auth, json={"answer": "__import__(x)"})
    assert response.json() == {"result": "invalid", "feedbackCode": None}
    assert "__import__" not in response.text


@pytest.mark.parametrize("topic,level", CELLS)
def test_generate_check_and_reveal_through_shared_worker(client, topic, level):
    auth = headers(client)
    public = client.post(
        "/preview/problems", headers=auth, json={"topic": topic, "difficulty": level}
    ).json()
    private = next(iter(preview._sessions.values())).problems[public["id"]]
    source = str(private.primitive).replace("**", "^")
    path = f"/preview/problems/{public['id']}"
    checked = client.post(f"{path}/attempts", headers=auth, json={"answer": source + "+C"})
    assert checked.status_code == 200
    assert checked.json() == {"result": "correct", "feedbackCode": None}
    missing = client.post(f"{path}/attempts", headers=auth, json={"answer": source})
    assert missing.json() == {"result": "incorrect", "feedbackCode": "missing_constant"}
    answer = client.post(f"{path}/reveal-answer", headers=auth).json()
    steps = client.post(f"{path}/reveal-solution", headers=auth).json()
    assert answer["answerLatex"] == steps["steps"][-1]["latex"]


@pytest.mark.parametrize(
    "answer,expected",
    [
        ("x^2/2+C", "correct"),
        ("2*x^2/4+2k+7", "correct"),
        ("x^2/2", "missing_constant"),
        ("x^2/2+7", "missing_constant"),
        ("x^3+C", "incorrect"),
        ("x^2/2+C*x", "incorrect"),
        ("x^2/2+C^2", "incorrect"),
        ("x^2/2+sin(C)", "incorrect"),
        ("x^2/2+C+0/(C-1)", "invalid"),
        ("x^2/2+(x/x-1)+C", "invalid"),
        ("x^2/2+ln(x)-ln(x)+C", "invalid"),
        ("x^2/2+sqrt(-1)+C", "invalid"),
    ],
)
def test_worker_equivalence_and_original_domains(answer, expected):
    record = {"generator_version": "basic-v1", "template": "power", "coefficient": 1}
    assert check_answer(answer, record) == expected


def test_request_bounds_expiry_rate_and_unsupported_cells(client, monkeypatch):
    auth = headers(client)
    for body in (
        {"topic": "substitution", "difficulty": 3},
        {"topic": "basic-integrals", "difficulty": True},
        {"topic": "basic-integrals", "difficulty": 1, "answer": "PRIVATE"},
    ):
        response = client.post("/preview/problems", headers=auth, json=body)
        assert response.status_code == 422
        assert "PRIVATE" not in response.text
    assert client.post("/preview/problems", content=b"x" * 4097).status_code == 413
    session = next(iter(preview._sessions.values()))
    session.expires = 0
    assert (
        client.post(
            "/preview/problems", headers=auth, json={"topic": "basic-integrals", "difficulty": 1}
        ).status_code
        == 401
    )
    monkeypatch.setattr(preview, "MAX_SESSIONS", 0)
    assert client.post("/preview/sessions").status_code == 503
    preview._requests.extend([preview.time.monotonic()] * 120)
    response = client.post("/preview/sessions")
    assert response.status_code == 429
    assert response.headers["retry-after"] == "60"


def test_check_failure_is_retryable_not_a_verdict(client, monkeypatch):
    auth = headers(client)
    problem = client.post(
        "/preview/problems", headers=auth, json={"topic": "basic-integrals", "difficulty": 1}
    ).json()

    def fail(*_args):
        raise MathWorkerError("private worker detail")

    monkeypatch.setattr(preview, "check_answer", fail)
    response = client.post(
        f"/preview/problems/{problem['id']}/attempts", headers=auth, json={"answer": "x+C"}
    )
    assert response.status_code == 503
    assert response.headers["retry-after"] == "3"
    assert "private" not in response.text
    assert "result" not in response.json()


def test_worker_saturation_does_not_queue_and_slot_is_released(monkeypatch):
    from app.services import preview_check

    record = {"generator_version": "basic-v1", "template": "power", "coefficient": 1}
    assert preview_check._SLOTS.acquire(blocking=False)
    try:
        with pytest.raises(MathWorkerError, match="busy"):
            check_answer("x+C", record)
    finally:
        preview_check._SLOTS.release()

    def inconclusive(*_args):
        raise MathCheckInconclusive("undecided")

    monkeypatch.setattr(preview_check, "shared_check", inconclusive)
    with pytest.raises(MathWorkerError, match="inconclusive"):
        check_answer("x+C", record)
    assert preview_check._SLOTS.acquire(blocking=False)
    preview_check._SLOTS.release()
