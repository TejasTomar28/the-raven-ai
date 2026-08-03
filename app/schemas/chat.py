"""Schemas for retrieval-augmented chat responses."""

from pydantic import BaseModel, Field

from app.schemas.search import SearchResult


class ChatRequest(BaseModel):
    """A user question to answer from indexed document context."""

    question: str = Field(description="Natural-language question about uploaded documents.")


class ChatResponse(BaseModel):
    """A grounded answer and its relevance-filtered supporting passages."""

    question: str = Field(description="Original user question.")
    answer: str = Field(description="Grounded final answer generated from the knowledge archive.")
    supported: bool = Field(description="Whether relevant passages supported the answer.")
    sources: list[SearchResult] = Field(description="Relevant retrieved passages that support the answer.")
    retrieved_chunks: int = Field(description="Number of supporting chunks supplied to the answer chain.")
