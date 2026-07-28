"""LangChain adapter for the application's sentence-transformer model."""

from langchain_core.embeddings import Embeddings

from app.core.logging import logger
from app.rag.embedding import EmbeddingService


class RavenEmbeddings(Embeddings):
    """Expose the existing embedding service through LangChain's interface."""

    def __init__(self, embedding_service: EmbeddingService) -> None:
        """Create an adapter around the shared embedding service."""
        self._embedding_service = embedding_service

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate vectors for document texts using the existing model."""
        logger.info("Generating embeddings for %d chunks", len(texts))
        return [self._embedding_service.embed_text(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        """Generate a vector for a user query using the existing model."""
        return self._embedding_service.embed_text(text)
