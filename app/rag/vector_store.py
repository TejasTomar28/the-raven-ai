"""Persistent ChromaDB storage for embedded document chunks."""

from typing import cast

import chromadb
from chromadb.api.types import Embeddings

from app.core.config import CHROMA_DIRECTORY
from app.core.constants import CHROMA_COLLECTION_NAME
from app.core.exceptions import VectorStoreError
from app.core.logging import logger
from app.schemas.chunk import Chunk


class ChromaVectorStore:
    """Persist document chunk embeddings in a local ChromaDB collection."""

    def __init__(self) -> None:
        """Initialize the persistent ChromaDB client and document collection."""
        try:
            CHROMA_DIRECTORY.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(CHROMA_DIRECTORY))
            self._collection = client.get_or_create_collection(CHROMA_COLLECTION_NAME)
        except Exception as error:
            raise VectorStoreError("Unable to initialize the ChromaDB collection.") from error

    def store_chunks(
        self,
        filename: str,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        """Replace a document's vectors with the supplied chunk embeddings.

        Args:
            filename: Filename shared by the supplied chunks.
            chunks: Chunk metadata and source text to persist.
            embeddings: Embedding vectors aligned with ``chunks``.

        Raises:
            VectorStoreError: If the vectors cannot be saved.
        """
        if len(chunks) != len(embeddings):
            raise VectorStoreError("Chunk and embedding counts must match.")
        if not chunks:
            logger.info("Saving vectors skipped for %s because it has no chunks", filename)
            return

        try:
            logger.info("Saving vectors for %s: %d chunks", filename, len(chunks))
            self._collection.delete(where={"filename": filename})
            self._collection.upsert(
                ids=[f"{filename}_{chunk.id}" for chunk in chunks],
                documents=[chunk.text for chunk in chunks],
                metadatas=[
                    {
                        "filename": filename,
                        "chunk_id": chunk.id,
                        "start_char": chunk.start_char,
                        "end_char": chunk.end_char,
                        # ChromaDB omits metadata keys with null values; -1 means unavailable.
                        "page_number": chunk.page_number if chunk.page_number is not None else -1,
                    }
                    for chunk in chunks
                ],
                embeddings=cast(Embeddings, embeddings),
            )
        except VectorStoreError:
            raise
        except Exception as error:
            raise VectorStoreError("Unable to save document vectors.") from error
