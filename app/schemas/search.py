"""Schemas for semantic document retrieval."""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """A natural-language query for indexed document chunks."""

    query: str = Field(description="Natural-language question used for semantic retrieval.")


class SearchResult(BaseModel):
    """One ranked document chunk returned by semantic search."""

    score: float = Field(description="Normalized similarity score, where higher is better.")
    filename: str = Field(description="Filename of the document containing the chunk.")
    chunk_id: int = Field(description="One-based identifier of the matching chunk.")
    page_number: int | None = Field(description="Source PDF page number when available.")
    text: str = Field(description="Matching chunk text.")


class SearchResponse(BaseModel):
    """Semantic search results for the supplied query."""

    query: str = Field(description="Original natural-language query.")
    results: list[SearchResult] = Field(description="Ranked matching document chunks.")
