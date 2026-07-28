"""Filesystem configuration for the RAVEN AI application."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
"""Root directory of the application project."""

UPLOADS_DIRECTORY = BASE_DIR / "uploads"
"""Directory where uploaded documents are stored."""

DATA_DIRECTORY = BASE_DIR / "data"
"""Directory containing persistent application data."""

CHROMA_DIRECTORY = DATA_DIRECTORY / "chroma"
"""Directory used by the persistent ChromaDB client."""


def get_uploaded_document_path(filename: str) -> Path:
    """Return the safe uploads-directory path for a document filename."""
    return UPLOADS_DIRECTORY / Path(filename).name
