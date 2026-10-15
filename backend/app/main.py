from fastapi import FastAPI

app = FastAPI(title="PracticeLoop API", version="0.0.0")


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    """Liveness only; does not claim authentication or database readiness."""
    return {"status": "ok"}
