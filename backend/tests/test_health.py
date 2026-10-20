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


def test_allowed_origins_refuse_plain_http_outside_local_dev(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "ALLOWED_ORIGINS",
        "http://practiceloop.pages.dev, https://*.pages.dev, http://localhost:5173",
    )
    assert allowed_origins() == ["http://localhost:5173"]


@pytest.mark.parametrize("path", ["/health", "/nope", "/problems"])
def test_api_responses_carry_security_headers(path: str) -> None:
    response = client.get(path)
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["content-security-policy"].startswith("default-src 'none'")


def test_oversized_and_invalid_requests_fail_safely() -> None:
    big = client.post("/preview/check", content=b"x" * 5000)
    assert big.status_code == 413
    assert big.headers["content-security-policy"].startswith("default-src 'none'")
    private_text = "do-not-echo-this-answer"
    invalid = client.post(
        "/problems/00000000-0000-0000-0000-000000000000/report",
        json={"category": "nope", "comment": private_text},
        headers={"Authorization": "Bearer x"},
    )
    assert invalid.status_code >= 400
    assert private_text not in invalid.text


def test_docs_keep_only_framing_rules() -> None:
    assert client.get("/docs").headers["content-security-policy"] == "frame-ancestors 'none'"
