"""PracticeLoop backend."""

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app.api.practice import router as practice_router
from app.api.preview import router as preview_router
from app.api.shares import router as shares_router
from app.core.database import close_pool
from app.core.errors import install_error_handlers

logger = logging.getLogger("practiceloop.api")

# Local Vite dev server only; deployed origins come from ALLOWED_ORIGINS on the host.
DEFAULT_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")


def allowed_origins() -> list[str]:
    """Comma-separated exact origins; wildcards are never accepted."""
    raw = os.environ.get("ALLOWED_ORIGINS", "")
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    return [origin for origin in origins if origin != "*"] or list(DEFAULT_ORIGINS)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield
    close_pool()


app = FastAPI(title="PracticeLoop API", version="0.0.0", lifespan=lifespan)
app.include_router(preview_router)
app.include_router(practice_router)
app.include_router(shares_router)
install_error_handlers(app)


def _error(status: int, code: str, message: str, **extra: str) -> JSONResponse:
    body = {"error": {"code": code, "message": message, "retryable": False, **extra}}
    return JSONResponse(body, status_code=status)


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, _error_: RequestValidationError) -> JSONResponse:
    # Do not reflect submitted answers or unexpected private fields in errors.
    if request.url.path.startswith("/preview"):
        return JSONResponse({"detail": "invalid_request"}, status_code=422)
    return _error(422, "invalid_request", "Check your request and try again.")


@app.exception_handler(Exception)
async def internal_error(_request: Request, exc: Exception) -> JSONResponse:
    # The correlation ID ties the learner's report to the log line; no exception text leaks.
    correlation = str(uuid4())
    logger.error("Unhandled error %s", correlation, exc_info=exc)
    return _error(
        500, "internal_error", "Something went wrong. Try again.", correlationId=correlation
    )


@app.middleware("http")
async def request_boundary(request: Request, call_next: RequestResponseEndpoint) -> Response:
    if request.method == "POST":
        size = 0
        chunks: list[bytes] = []
        async for chunk in request.stream():
            size += len(chunk)
            if size > 4096:
                return JSONResponse({"detail": "request_too_large"}, status_code=413)
            chunks.append(chunk)
        # Starlette BaseHTTPMiddleware replays the cached bounded body to the route.
        request._body = b"".join(chunks)
    response = await call_next(request)
    if request.url.path != "/health":
        response.headers["Cache-Control"] = "no-store"
    return response


# Bearer tokens travel in the Authorization header, so no cookies or credentials mode.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
    expose_headers=["Idempotency-Replayed", "Retry-After"],
)


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    """Liveness only; does not claim authentication or database readiness."""
    return {"status": "ok"}
