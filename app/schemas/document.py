"""Schemas for uploaded-document metadata."""

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentSummary(BaseModel):
    """Persisted archive metadata for one uploaded PDF."""

    filename: str = Field(description="Stored PDF filename.")
    size_bytes: int = Field(description="Legacy size field used by the existing frontend.")
    file_size: int = Field(description="PDF size in bytes.")
    updated_at: datetime = Field(description="Legacy archive timestamp field.")
    uploaded_at: datetime = Field(description="Timestamp at which the PDF was archived.")
    chunk_count: int = Field(description="Number of indexed RAG chunks.")
    category: str = Field(description="ML-predicted document category or general fallback.")
    classifier: str = Field(description="Classifier that produced the category.")
    model_version: str = Field(description="Version of the document-classification model.")
    classification_confidence: float | None = Field(
        default=None, description="Native classifier confidence when available."
    )


class DocumentListResponse(BaseModel):
    """Collection of uploaded documents available to the frontend."""

    documents: list[DocumentSummary] = Field(description="Uploaded PDF documents.")
