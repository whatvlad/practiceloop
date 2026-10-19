"""PracticeLoop backend."""

import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app.api.preview import router as preview_router

# Local Vite dev server only; deployed origins come from ALLOWED_ORIGINS on the host.
DEFAULT_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")


def allowed_origins() -> list[str]:
    """Comma-separated exact origins; wildcards are never accepted."""
    raw = os.environ.get("ALLOWED_ORIGINS", "")
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    return [origin for origin in origins if origin != "*"] or list(DEFAULT_ORIGINS)


app = FastAPI(title="PracticeLoop API", version="0.0.0")
app.include_router(preview_router)


@app.exception_handler(RequestValidationError)
async def invalid_request(_request: Request, _error: RequestValidationError) -> JSONResponse:
    # Do not reflect submitted answers or unexpected private fields in errors.
    return JSONResponse({"detail": "invalid_request"}, status_code=422)


@app.middleware("http")
async def preview_boundary(request: Request, call_next: RequestResponseEndpoint) -> Response:
    if request.url.path.startswith("/preview"):
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
    if request.url.path.startswith("/preview"):
        response.headers["Cache-Control"] = "no-store"
    return response


# Bearer tokens travel in the Authorization header, so no cookies or credentials mode.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    """Liveness only; does not claim authentication or database readiness."""
    return {"status": "ok"}
