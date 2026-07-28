"""Schemas describing RAG text chunks."""

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """A text segment prepared for future embedding and retrieval operations."""

    id: int = Field(description="One-based identifier for the chunk within its document.")
    text: str = Field(description="The text content of the chunk.")
    source_document: str = Field(description="Filename of the document that produced the chunk.")
    page_number: int | None = Field(
        default=None,
        description="Source PDF page number when page-aware parsing is available.",
    )
    start_char: int = Field(description="Zero-based inclusive character offset in the source text.")
    end_char: int = Field(description="Zero-based exclusive character offset in the source text.")
