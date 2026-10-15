from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_liveness() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unimplemented_math_api_is_not_exposed() -> None:
    assert client.post("/api/problems", json={"topic": "basic-integrals"}).status_code == 404
