"""Application entry point for the RAVEN AI API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router


app = FastAPI(
    title="RAVEN AI",
    description="Enterprise Knowledge Platform using Retrieval-Augmented Generation (RAG)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/")
def read_root() -> dict[str, str]:
    """Return a welcome message for the RAVEN AI service."""
    return {"message": "Welcome to RAVEN AI"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Report the health status of the RAVEN AI service."""
    return {"status": "healthy", "service": "RAVEN AI"}
