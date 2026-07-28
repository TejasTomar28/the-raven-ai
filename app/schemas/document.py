"""Schemas for uploaded-document metadata."""

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentSummary(BaseModel):
    """Metadata for one PDF available in the knowledge archive."""

    filename: str = Field(description="Stored PDF filename.")
    size_bytes: int = Field(description="Size of the uploaded PDF in bytes.")
    updated_at: datetime = Field(description="Timestamp when the PDF was last modified.")


class DocumentListResponse(BaseModel):
    """Collection of uploaded documents available to the frontend."""

    documents: list[DocumentSummary] = Field(description="Uploaded PDF documents.")
