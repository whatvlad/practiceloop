"""PracticeLoop backend."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local Vite dev server only; deployed origins come from ALLOWED_ORIGINS on the host.
DEFAULT_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")


def allowed_origins() -> list[str]:
    """Comma-separated exact origins; wildcards are never accepted."""
    raw = os.environ.get("ALLOWED_ORIGINS", "")
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    return [origin for origin in origins if origin != "*"] or list(DEFAULT_ORIGINS)


app = FastAPI(title="PracticeLoop API", version="0.0.0")
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
