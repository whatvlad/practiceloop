import json
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api import practice
from app.core.auth import VerifiedUser, current_user, token_verifier
from app.core.errors import ApiError
from app.main import app
from app.services import account


@pytest.mark.parametrize("status", [200, 404, 302, 401, 429, 500])
def test_hard_delete_uses_server_key_and_no_redirects(monkeypatch, status):
    monkeypatch.setenv("SUPABASE_URL", "https://project.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "synthetic-server-only-key")
    connection = Mock()
    connection.getresponse.return_value = SimpleNamespace(status=status)
    factory = Mock(return_value=connection)
    monkeypatch.setattr(account, "HTTPSConnection", factory)
    user = uuid4()
    if status in (200, 404):
        account.delete_user(user)
    else:
        with pytest.raises(ApiError) as error:
            account.delete_user(user)
        assert error.value.status_code == 503
    args, kwargs = connection.request.call_args
    assert args == ("DELETE", f"/auth/v1/admin/users/{user}")
    assert json.loads(kwargs["body"]) == {"should_soft_delete": False}
    assert kwargs["headers"]["apikey"] == "synthetic-server-only-key"
    assert connection.request.call_count == 1
    connection.close.assert_called_once()


def test_missing_deletion_config_never_contacts_auth(monkeypatch):
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    factory = Mock()
    monkeypatch.setattr(account, "HTTPSConnection", factory)
    with pytest.raises(ApiError):
        account.delete_user(uuid4())
    factory.assert_not_called()


def test_uncertain_auth_failure_is_safe_and_closes_connection(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://project.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "synthetic-server-only-key")
    connection = Mock()
    connection.request.side_effect = TimeoutError("private upstream detail")
    monkeypatch.setattr(account, "HTTPSConnection", Mock(return_value=connection))
    with pytest.raises(ApiError) as error:
        account.delete_user(uuid4())
    assert error.value.status_code == 503 and error.value.retryable
    assert "private" not in error.value.message
    connection.close.assert_called_once()


def test_delete_requires_exact_confirmation_and_uses_only_verified_identity(monkeypatch):
    user = VerifiedUser(uuid4(), None)
    app.dependency_overrides[current_user] = lambda: user
    delete = Mock()
    monkeypatch.setattr(practice, "delete_user", delete)
    try:
        with TestClient(app) as client:
            for body in (
                {},
                {"confirmation": "delete"},
                {"confirmation": "DELETE", "userId": str(uuid4())},
            ):
                assert client.post("/account/delete", json=body).status_code == 422
            delete.assert_not_called()
            assert client.post("/account/delete", json={"confirmation": "DELETE"}).json() == {
                "deleted": True
            }
            delete.assert_called_once_with(user.id)
    finally:
        app.dependency_overrides.clear()


def test_new_account_routes_require_auth_before_any_data_access(monkeypatch):
    app.dependency_overrides[token_verifier] = lambda: object()
    delete = Mock(side_effect=AssertionError("unauthenticated delete"))
    monkeypatch.setattr(practice, "delete_user", delete)
    try:
        with TestClient(app) as client:
            assert client.get("/statistics").status_code == 401
            assert client.post("/profile", json={"name": "test"}).status_code == 401
            assert (
                client.post("/account/delete", json={"confirmation": "DELETE"}).status_code == 401
            )
        delete.assert_not_called()
    finally:
        app.dependency_overrides.clear()
