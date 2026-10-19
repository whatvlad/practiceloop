import json
import time
from typing import Any
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jwt.algorithms import ECAlgorithm, RSAAlgorithm
from jwt.utils import base64url_encode

from app.core import auth
from app.core.auth import TokenVerifier, VerifiedUser, current_user, token_verifier
from app.core.errors import install_error_handlers

ISSUER = "https://project-a.supabase.co/auth/v1"
EC_KEY = ec.generate_private_key(ec.SECP256R1())
RSA_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
NEXT_KEY = ec.generate_private_key(ec.SECP256R1())


def jwk(private_key: Any, kid: str) -> dict[str, Any]:
    if isinstance(private_key, ec.EllipticCurvePrivateKey):
        data = ECAlgorithm.to_jwk(private_key.public_key(), as_dict=True)
        data["alg"] = "ES256"
    else:
        data = RSAAlgorithm.to_jwk(private_key.public_key(), as_dict=True)
        data["alg"] = "RS256"
    return {**data, "kid": kid, "use": "sig"}


class FakeJwksClient(jwt.PyJWKClient):
    """The real client's caching and refetch logic over an in-memory endpoint."""

    def __init__(self, keys: list[dict[str, Any]], cooldown: float = 30) -> None:
        super().__init__("https://project-a.supabase.co/jwks", cooldown_duration=cooldown)
        self.keys = keys
        self.fetches = 0
        self.down = False

    def fetch_data(self) -> Any:
        self.fetches += 1
        if self.down:
            raise jwt.PyJWKClientConnectionError("unreachable")
        data = {"keys": self.keys}
        assert self.jwk_set_cache is not None
        self.jwk_set_cache.put(data)
        self._last_successful_fetch = time.monotonic()
        return data


def claims(**overrides: Any) -> dict[str, Any]:
    now = int(time.time())
    base = {
        "sub": str(uuid4()),
        "iss": ISSUER,
        "aud": "authenticated",
        "role": "authenticated",
        "email": "learner@example.test",
        "iat": now,
        "exp": now + 3600,
        "is_anonymous": False,
    }
    base.update(overrides)
    return {key: value for key, value in base.items() if value is not None}


def sign(payload: dict[str, Any], key: Any = EC_KEY, kid: str = "ec-1", alg: str = "ES256") -> str:
    return jwt.encode(payload, key, algorithm=alg, headers={"kid": kid})


def make_client(jwks: FakeJwksClient) -> TestClient:
    app = FastAPI()
    install_error_handlers(app)

    @app.get("/whoami")
    def whoami(user: VerifiedUser = Depends(current_user)) -> dict[str, Any]:  # noqa: B008
        return {"id": str(user.id), "email": user.email}

    app.dependency_overrides[token_verifier] = lambda: TokenVerifier(ISSUER, jwks)
    return TestClient(app)


@pytest.fixture
def jwks() -> FakeJwksClient:
    return FakeJwksClient([jwk(EC_KEY, "ec-1"), jwk(RSA_KEY, "rsa-1")])


@pytest.fixture
def client(jwks: FakeJwksClient) -> TestClient:
    return make_client(jwks)


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def assert_rejected(response: Any, code: str = "invalid_token") -> None:
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {
        "error": {"code": code, "message": response.json()["error"]["message"], "retryable": False}
    }


@pytest.mark.parametrize(
    ("key", "kid", "alg"), [(EC_KEY, "ec-1", "ES256"), (RSA_KEY, "rsa-1", "RS256")]
)
def test_valid_token_yields_user_from_sub(client: TestClient, key: Any, kid: str, alg: str) -> None:
    payload = claims()
    response = client.get("/whoami", headers=bearer(sign(payload, key, kid, alg)))
    assert response.status_code == 200
    assert response.json() == {"id": payload["sub"], "email": "learner@example.test"}


@pytest.mark.parametrize(
    "headers", [{}, {"Authorization": "Basic abc"}, {"Authorization": "Bearer "}]
)
def test_missing_token_requires_authentication(client: TestClient, headers: dict[str, str]) -> None:
    assert_rejected(client.get("/whoami", headers=headers), "authentication_required")


@pytest.mark.parametrize(
    "payload",
    [
        claims(exp=int(time.time()) - 60),
        claims(iss="https://project-b.supabase.co/auth/v1"),
        claims(aud="anon"),
        claims(role="anon"),
        claims(role="service_role"),
        claims(is_anonymous=True),
        claims(sub="not-a-uuid"),
        claims(exp=None),
        claims(sub=None),
        claims(iss=None),
        claims(aud=None),
    ],
    ids=[
        "expired",
        "other-project",
        "wrong-audience",
        "anon-role",
        "service-role",
        "anonymous-user",
        "bad-sub",
        "no-exp",
        "no-sub",
        "no-iss",
        "no-aud",
    ],
)
def test_rejects_bad_claims(client: TestClient, payload: dict[str, Any]) -> None:
    assert_rejected(client.get("/whoami", headers=bearer(sign(payload))))


def test_rejects_tampered_payload(client: TestClient) -> None:
    header, _, signature = sign(claims()).split(".")
    forged = base64url_encode(json.dumps(claims()).encode()).decode()
    assert_rejected(client.get("/whoami", headers=bearer(f"{header}.{forged}.{signature}")))


def test_rejects_signature_from_unknown_key(client: TestClient) -> None:
    other = ec.generate_private_key(ec.SECP256R1())
    assert_rejected(client.get("/whoami", headers=bearer(sign(claims(), other))))


def test_rejects_shared_secret_and_unsigned_tokens(client: TestClient) -> None:
    public_pem = jwk(EC_KEY, "ec-1")["x"]
    hs = jwt.encode(claims(), public_pem, algorithm="HS256", headers={"kid": "ec-1"})
    unsigned = jwt.encode(claims(), None, algorithm="none", headers={"kid": "ec-1"})
    for token in (hs, unsigned, "not.a.jwt", "garbage"):
        assert_rejected(client.get("/whoami", headers=bearer(token)))


def test_rejects_key_algorithm_mismatch(client: TestClient) -> None:
    # Header says RS256 but names the EC key: the key's own algorithm wins.
    token = sign(claims(), RSA_KEY, kid="ec-1", alg="RS256")
    assert_rejected(client.get("/whoami", headers=bearer(token)))


def test_rotated_key_is_fetched_on_unknown_kid() -> None:
    jwks = FakeJwksClient([jwk(EC_KEY, "ec-1")], cooldown=0)
    client = make_client(jwks)
    assert client.get("/whoami", headers=bearer(sign(claims()))).status_code == 200
    jwks.keys = [jwk(EC_KEY, "ec-1"), jwk(NEXT_KEY, "ec-2")]
    response = client.get("/whoami", headers=bearer(sign(claims(), NEXT_KEY, "ec-2")))
    assert response.status_code == 200
    assert jwks.fetches == 2


def test_unknown_kid_floods_do_not_refetch_every_time(jwks: FakeJwksClient) -> None:
    client = make_client(jwks)
    assert client.get("/whoami", headers=bearer(sign(claims()))).status_code == 200
    for _ in range(5):
        token = sign(claims(), NEXT_KEY, kid=str(uuid4()))
        assert_rejected(client.get("/whoami", headers=bearer(token)))
    assert jwks.fetches == 1


def test_unreachable_keys_are_retryable_service_errors(jwks: FakeJwksClient) -> None:
    jwks.down = True
    response = make_client(jwks).get("/whoami", headers=bearer(sign(claims())))
    assert response.status_code == 503
    assert response.headers["retry-after"] == "5"
    assert response.json()["error"]["code"] == "authentication_unavailable"
    assert response.json()["error"]["retryable"] is True


def test_unconfigured_host_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    auth.get_token_verifier.cache_clear()
    app = FastAPI()
    install_error_handlers(app)

    @app.get("/whoami")
    def whoami(user: VerifiedUser = Depends(current_user)) -> str:  # noqa: B008
        return str(user.id)

    response = TestClient(app).get("/whoami", headers=bearer(sign(claims())))
    assert response.status_code == 503
    auth.get_token_verifier.cache_clear()


def test_verifier_reads_host_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://project-a.supabase.co/")
    monkeypatch.delenv("SUPABASE_JWT_ISSUER", raising=False)
    auth.get_token_verifier.cache_clear()
    verifier = auth.get_token_verifier()
    assert verifier.issuer == ISSUER
    assert verifier._jwks.uri == "https://project-a.supabase.co/auth/v1/.well-known/jwks.json"
    auth.get_token_verifier.cache_clear()
