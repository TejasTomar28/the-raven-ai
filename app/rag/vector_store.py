"""Persistent ChromaDB storage for embedded document chunks."""

from collections.abc import Mapping
from typing import cast

import chromadb
from chromadb.api.types import Embeddings

from app.core.config import CHROMA_DIRECTORY
from app.core.constants import CHROMA_COLLECTION_NAME
from app.core.exceptions import NoIndexedDocumentsError, VectorStoreError
from app.core.logging import logger
from app.schemas.chunk import Chunk
from app.schemas.search import SearchResult


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

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Return the most similar indexed chunks for a query embedding.

        Scores are normalized from ChromaDB's non-negative distance values so that
        larger scores indicate closer matches.
        """
        if self._collection.count() == 0:
            raise NoIndexedDocumentsError("No indexed documents are available.")

        try:
            logger.info("ChromaDB search started: top_k=%d", top_k)
            response = self._collection.query(
                query_embeddings=cast(Embeddings, [query_embedding]),
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )
            raw_documents = response["documents"]
            raw_metadatas = response["metadatas"]
            raw_distances = response["distances"]
            if raw_documents is None or raw_metadatas is None or raw_distances is None:
                raise VectorStoreError("ChromaDB did not return complete search data.")

            documents = cast(list[str], raw_documents[0] or [])
            metadatas = cast(
                list[Mapping[str, object]],
                raw_metadatas[0] or [],
            )
            distances = cast(list[float], raw_distances[0] or [])

            results = [
                SearchResult(
                    score=1.0 / (1.0 + distance),
                    filename=str(metadata["filename"]),
                    chunk_id=_chunk_id_from_metadata(metadata),
                    page_number=_page_number_from_metadata(metadata),
                    text=document,
                )
                for document, metadata, distance in zip(documents, metadatas, distances)
            ]
            logger.info("ChromaDB search retrieved %d chunks", len(results))
            return results
        except NoIndexedDocumentsError:
            raise
        except Exception as error:
            raise VectorStoreError("Unable to search document vectors.") from error


def _page_number_from_metadata(metadata: Mapping[str, object]) -> int | None:
    """Convert ChromaDB's unavailable-page sentinel back to ``None``."""
    page_number = metadata.get("page_number")
    if isinstance(page_number, int) and page_number >= 0:
        return page_number
    return None


def _chunk_id_from_metadata(metadata: Mapping[str, object]) -> int:
    """Return the required integer chunk ID from persisted ChromaDB metadata."""
    chunk_id = metadata.get("chunk_id")
    if isinstance(chunk_id, int):
        return chunk_id
    if isinstance(chunk_id, str):
        return int(chunk_id)
    raise VectorStoreError("ChromaDB result is missing a valid chunk ID.")
