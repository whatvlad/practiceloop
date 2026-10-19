"""Verified Supabase identity: the only source of a user ID in the API.

Supabase signs access tokens with an asymmetric key and publishes the public
keys as a JWKS. Only asymmetric algorithms are accepted, so a token signed with
a shared secret, or with no signature, can never pass. Keys are cached and the
set is refetched when a token names an unknown `kid`, which covers rotation;
PyJWKClient rate-limits those refetches.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errors import ApiError

# Supabase's asymmetric signing keys: ECC P-256 and RSA. Never HS*/none.
ALLOWED_ALGORITHMS = ("ES256", "RS256")
AUDIENCE = "authenticated"
CLOCK_SKEW_SECONDS = 10
JWKS_CACHE_SECONDS = 600
JWKS_TIMEOUT_SECONDS = 5.0
_REQUIRED_CLAIMS = ["exp", "iat", "iss", "aud", "sub"]
_CHALLENGE = {"WWW-Authenticate": "Bearer"}


@dataclass(frozen=True)
class VerifiedUser:
    id: UUID
    email: str | None


class AuthUnavailableError(RuntimeError):
    """Keys could not be fetched or configuration is missing; not the caller's fault."""


def _invalid_token() -> ApiError:
    return ApiError(
        401, "invalid_token", "Your session is not valid. Sign in again.", headers=_CHALLENGE
    )


class TokenVerifier:
    def __init__(self, issuer: str, jwks_client: jwt.PyJWKClient) -> None:
        self.issuer = issuer
        self._jwks = jwks_client

    def verify(self, token: str) -> VerifiedUser:
        try:
            header = jwt.get_unverified_header(token)
        except jwt.PyJWTError:
            raise _invalid_token() from None
        if header.get("alg") not in ALLOWED_ALGORITHMS or not isinstance(header.get("kid"), str):
            raise _invalid_token()
        try:
            key = self._jwks.get_signing_key(header["kid"])
        except jwt.PyJWKClientConnectionError as exc:
            raise AuthUnavailableError("signing keys unavailable") from exc
        except jwt.PyJWKClientError:
            # Unknown kid even after a refetch: a foreign or forged token.
            raise _invalid_token() from None
        try:
            claims: dict[str, Any] = jwt.decode(
                token,
                key,
                algorithms=list(ALLOWED_ALGORITHMS),
                audience=AUDIENCE,
                issuer=self.issuer,
                leeway=CLOCK_SKEW_SECONDS,
                options={"require": _REQUIRED_CLAIMS},
            )
        except jwt.PyJWTError:
            raise _invalid_token() from None
        return _user_from_claims(claims)


def _user_from_claims(claims: dict[str, Any]) -> VerifiedUser:
    # Signed but not a signed-in learner: anon/service keys, anonymous sign-ins.
    if claims.get("role") != "authenticated" or claims.get("is_anonymous") is True:
        raise _invalid_token()
    try:
        user_id = UUID(str(claims["sub"]))
    except ValueError:
        raise _invalid_token() from None
    email = claims.get("email")
    return VerifiedUser(id=user_id, email=email if isinstance(email, str) and email else None)


@lru_cache(maxsize=1)
def get_token_verifier() -> TokenVerifier:
    """Built from the host's SUPABASE_URL and SUPABASE_JWT_ISSUER."""
    base = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    if not base.startswith("https://"):
        raise AuthUnavailableError("SUPABASE_URL is not configured")
    issuer = os.environ.get("SUPABASE_JWT_ISSUER", "").strip() or f"{base}/auth/v1"
    client = jwt.PyJWKClient(
        f"{base}/auth/v1/.well-known/jwks.json",
        lifespan=JWKS_CACHE_SECONDS,
        timeout=JWKS_TIMEOUT_SECONDS,
    )
    return TokenVerifier(issuer, client)


def token_verifier() -> TokenVerifier:
    """Dependency; tests replace it through app.dependency_overrides."""
    try:
        return get_token_verifier()
    except AuthUnavailableError:
        raise _auth_unavailable() from None


def _auth_unavailable() -> ApiError:
    return ApiError(
        503,
        "authentication_unavailable",
        "Sign-in cannot be checked right now. Try again shortly.",
        retryable=True,
        headers={"Retry-After": "5"},
    )


_bearer = HTTPBearer(auto_error=False, description="Supabase access token")


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    verifier: Annotated[TokenVerifier, Depends(token_verifier)],
) -> VerifiedUser:
    """FastAPI dependency for every /api route; the request body never names the user."""
    if credentials is None or not credentials.credentials:
        raise ApiError(401, "authentication_required", "Sign in to continue.", headers=_CHALLENGE)
    try:
        return verifier.verify(credentials.credentials)
    except AuthUnavailableError:
        raise _auth_unavailable() from None
