"""Sentence-transformer embedding service for the RAG pipeline."""

from typing import ClassVar

from sentence_transformers import SentenceTransformer

from app.core.constants import EMBEDDING_MODEL_NAME
from app.core.exceptions import EmbeddingGenerationError
from app.core.logging import logger
from app.schemas.chunk import Chunk


class EmbeddingService:
    """Generate embeddings with a lazily loaded shared sentence-transformer model."""

    _instance: ClassVar["EmbeddingService | None"] = None
    _model: ClassVar[SentenceTransformer | None] = None

    def __new__(cls) -> "EmbeddingService":
        """Return the single application-wide embedding service instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def model(self) -> SentenceTransformer:
        """Load the configured embedding model once, on first use."""
        service_class = type(self)
        if service_class._model is None:
            try:
                logger.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)
                service_class._model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            except Exception as error:
                raise EmbeddingGenerationError("Unable to load the embedding model.") from error
        return service_class._model

    def embed_text(self, text: str) -> list[float]:
        """Generate an embedding vector for one text value."""
        try:
            embedding = self.model.encode(text)
            return [float(value) for value in embedding]
        except EmbeddingGenerationError:
            raise
        except Exception as error:
            raise EmbeddingGenerationError("Unable to generate a text embedding.") from error

    def embed_chunks(self, chunks: list[Chunk]) -> list[list[float]]:
        """Generate embedding vectors for a collection of document chunks."""
        logger.info("Generating embeddings for %d chunks", len(chunks))
        return [self.embed_text(chunk.text) for chunk in chunks]
