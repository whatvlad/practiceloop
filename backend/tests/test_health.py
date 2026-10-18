import pytest
from fastapi.testclient import TestClient

from app.main import DEFAULT_ORIGINS, allowed_origins, app

client = TestClient(app)


def test_liveness() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unimplemented_math_api_is_not_exposed() -> None:
    assert client.post("/api/problems", json={"topic": "basic-integrals"}).status_code == 404


def test_cors_allows_local_dev_origin_by_default() -> None:
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_ignores_unlisted_origin() -> None:
    response = client.get("/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in response.headers


def test_allowed_origins_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "ALLOWED_ORIGINS", " https://practiceloop.pages.dev/ ,*, http://localhost:5173"
    )
    assert allowed_origins() == ["https://practiceloop.pages.dev", "http://localhost:5173"]
    monkeypatch.setenv("ALLOWED_ORIGINS", "*")
    assert allowed_origins() == list(DEFAULT_ORIGINS)
