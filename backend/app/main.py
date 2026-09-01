"""Market Zone Intelligence API."""

from fastapi import FastAPI

app = FastAPI(
    title="Market Zone Intelligence",
    description="Impulse-based zone detection and intelligence platform",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok"}
