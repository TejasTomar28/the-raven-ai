"""Application entry point for the RAVEN AI API."""

from fastapi import FastAPI

from app.api.documents import router as documents_router


app = FastAPI(
    title="RAVEN AI",
    description="Enterprise Knowledge Platform using Retrieval-Augmented Generation (RAG)",
    version="1.0.0",
)

app.include_router(documents_router)


@app.get("/")
def read_root() -> dict[str, str]:
    """Return a welcome message for the RAVEN AI service."""
    return {"message": "Welcome to RAVEN AI"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Report the health status of the RAVEN AI service."""
    return {"status": "healthy", "service": "RAVEN AI"}
