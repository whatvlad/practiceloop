from itertools import product

import pytest
from engine_fixtures import native_record
from fastapi.testclient import TestClient

from app.api import preview
from app.engine import practice as engine
from app.main import app
from app.services.math_worker import MathCheckInconclusive, MathWorkerError
from app.services.preview_check import check_answer


def test_fixed_demo_picks_rendered_data_without_symbolic_work() -> None:
    import sys

    preview._sessions.clear()
    preview._requests.clear()
    token = preview.start_session()["token"]
    calls = []

    def profile(frame, event, _):
        if event == "call" and frame.f_globals.get("__name__", "").startswith("sympy"):
            calls.append(frame.f_code.co_name)

    previous = sys.getprofile()
    engine._registry.cache_clear()
    sys.setprofile(profile)
    try:
        public = preview.generate(
            preview.Generate(topic="basic-integrals", difficulty=1), authorization=f"Bearer {token}"
        )
    finally:
        sys.setprofile(previous)
    assert not calls
    assert "answerLatex" not in public and "solution" not in public


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


def test_one_fixed_demo_requires_login_for_more_and_never_saves_outcomes(client):
    body = {"topic": "basic-integrals", "difficulty": 1}
    auth = headers(client)
    first = client.post("/preview/problems", json=body, headers=auth)
    assert first.status_code == 201
    assert client.post("/preview/problems", json=body, headers=auth).status_code == 403
    assert (
        client.post(
            "/preview/problems",
            json={"topic": "substitution", "difficulty": 1},
            headers=headers(client),
        ).status_code
        == 403
    )
    again = client.post("/preview/problems", json=body, headers=headers(client))
    assert again.json()["problemLatex"] == first.json()["problemLatex"]
    assert first.json()["lastAnswer"] is None
    assert first.json()["lastResult"] is None
    assert len(next(iter(preview._sessions.values())).problems) == 1


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
    solution = client.post(f"{path}/reveal-solution", headers=auth).json()
    assert set(solution) == {"steps", "visual"}
    assert solution["visual"]["kind"] == "indefinite"
    response = client.post(f"{path}/attempts", headers=auth, json={"answer": "__import__(x)"})
    assert response.json() == {"result": "invalid", "feedbackCode": None}
    assert "__import__" not in response.text


@pytest.mark.parametrize("topic,level", (("basic-integrals", 1),))
def test_generate_check_and_reveal_through_shared_worker(client, topic, level):
    auth = headers(client)
    public = client.post(
        "/preview/problems", headers=auth, json={"topic": topic, "difficulty": level}
    ).json()
    private = next(iter(preview._sessions.values())).problems[public["id"]]
    source = str(engine.replay(private.record).answer.primitive).replace("**", "^")
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
    record = native_record("basic", "power")
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

    record = native_record("basic", "power")
    assert preview_check.CHECK_SLOTS.acquire(blocking=False)
    try:
        with pytest.raises(MathWorkerError, match="busy"):
            check_answer("x+C", record)
    finally:
        preview_check.CHECK_SLOTS.release()

    def inconclusive(*_args):
        raise MathCheckInconclusive("undecided")

    monkeypatch.setattr(preview_check, "shared_check", inconclusive)
    with pytest.raises(MathWorkerError, match="inconclusive"):
        check_answer("x+C", record)
    assert preview_check.CHECK_SLOTS.acquire(blocking=False)
    preview_check.CHECK_SLOTS.release()
