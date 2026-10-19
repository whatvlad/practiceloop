"""The single error envelope from docs/api/README.md."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    """A learner-safe failure; the message never carries answers or internals."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        *,
        retryable: bool = False,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(code)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.retryable = retryable
        self.headers = headers or {}


async def _api_error_response(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, ApiError)  # noqa: S101 - registered for ApiError only
    body = {"error": {"code": exc.code, "message": exc.message, "retryable": exc.retryable}}
    return JSONResponse(body, status_code=exc.status_code, headers=exc.headers)


def install_error_handlers(app: FastAPI) -> None:
    """Call once on the application that serves the /api routes."""
    app.add_exception_handler(ApiError, _api_error_response)
