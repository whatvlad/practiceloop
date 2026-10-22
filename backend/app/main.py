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
from app.api.reports import router as reports_router
from app.api.shares import router as shares_router
from app.api.worksheets import router as worksheets_router
from app.core.database import close_pool
from app.core.errors import install_error_handlers

logger = logging.getLogger("practiceloop.api")

# JSON never needs to run or embed anything. The interactive docs load Swagger
# from a CDN, so they only get the framing rules.
API_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
DOCS_CSP = "frame-ancestors 'none'"
DOCS_PATHS = ("/docs", "/redoc")
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cross-Origin-Resource-Policy": "same-site",
}

# Local Vite dev server only; deployed origins come from ALLOWED_ORIGINS on the host.
DEFAULT_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")


def _known_origin(origin: str) -> bool:
    # HTTPS everywhere except the local dev server.
    if origin.startswith("https://"):
        return "*" not in origin
    return origin in DEFAULT_ORIGINS


def allowed_origins() -> list[str]:
    """Comma-separated exact origins; wildcards and non-local HTTP are never accepted."""
    raw = os.environ.get("ALLOWED_ORIGINS", "")
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    return [origin for origin in origins if _known_origin(origin)] or list(DEFAULT_ORIGINS)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield
    close_pool()


app = FastAPI(title="PracticeLoop API", version="0.0.0", lifespan=lifespan)
app.include_router(preview_router)
app.include_router(practice_router)
app.include_router(shares_router)
app.include_router(reports_router)
app.include_router(worksheets_router)
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
                too_large = JSONResponse({"detail": "request_too_large"}, status_code=413)
                _secure(request.url.path, too_large)
                return too_large
            chunks.append(chunk)
        # Starlette BaseHTTPMiddleware replays the cached bounded body to the route.
        request._body = b"".join(chunks)
    response = await call_next(request)
    if request.url.path != "/health":
        response.headers["Cache-Control"] = "no-store"
    _secure(request.url.path, response)
    return response


def _secure(path: str, response: Response) -> None:
    response.headers.update(SECURITY_HEADERS)
    docs = path.startswith(DOCS_PATHS)
    response.headers["Content-Security-Policy"] = DOCS_CSP if docs else API_CSP


# Bearer tokens travel in the Authorization header, so no cookies or credentials mode.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
    expose_headers=["Idempotency-Replayed", "Retry-After", "Content-Disposition"],
)


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    """Liveness only; does not claim authentication or database readiness."""
    return {"status": "ok"}
