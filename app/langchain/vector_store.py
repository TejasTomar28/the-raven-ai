"""LangChain Chroma integration backed by the existing persistent collection."""

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.core.config import CHROMA_DIRECTORY
from app.core.constants import CHROMA_COLLECTION_NAME
from app.core.exceptions import NoIndexedDocumentsError, VectorStoreError
from app.core.logging import logger
from app.langchain.embeddings import RavenEmbeddings
from app.rag.embedding import EmbeddingService
from app.schemas.chunk import Chunk
from app.schemas.search import SearchResult


class LangChainVectorStore:
    """Store and retrieve chunks through one LangChain Chroma wrapper."""

    def __init__(self, embedding_service: EmbeddingService) -> None:
        """Open the existing persistent Chroma ``documents`` collection."""
        try:
            CHROMA_DIRECTORY.mkdir(parents=True, exist_ok=True)
            self._store = Chroma(
                collection_name=CHROMA_COLLECTION_NAME,
                persist_directory=str(CHROMA_DIRECTORY),
                embedding_function=RavenEmbeddings(embedding_service),
                relevance_score_fn=_distance_to_similarity,
            )
        except Exception as error:
            raise VectorStoreError("Unable to initialize the ChromaDB collection.") from error

    def store_chunks(self, filename: str, chunks: list[Chunk]) -> None:
        """Replace one document's existing chunks without recreating the collection."""
        if not chunks:
            logger.info("Saving vectors skipped for %s because it has no chunks", filename)
            return

        try:
            existing = self._store.get(where={"filename": filename})
            existing_ids = existing["ids"]
            if existing_ids:
                self._store.delete(ids=existing_ids)

            documents = [
                Document(
                    page_content=chunk.text,
                    metadata={
                        "filename": filename,
                        "chunk_id": chunk.id,
                        "start_char": chunk.start_char,
                        "end_char": chunk.end_char,
                        # ChromaDB omits null metadata; -1 represents an unavailable page.
                        "page_number": chunk.page_number if chunk.page_number is not None else -1,
                    },
                )
                for chunk in chunks
            ]
            logger.info("Saving vectors for %s: %d chunks", filename, len(chunks))
            self._store.add_documents(
                documents,
                ids=[f"{filename}_{chunk.id}" for chunk in chunks],
            )
        except Exception as error:
            raise VectorStoreError("Unable to save document vectors.") from error

    def as_retriever(self, top_k: int = 5):
        """Return the LangChain retriever configured for the requested result count."""
        self._ensure_indexed_documents()
        return self._store.as_retriever(search_kwargs={"k": top_k})

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Return ranked results through LangChain's Chroma similarity search."""
        self._ensure_indexed_documents()
        try:
            logger.info("ChromaDB search started: top_k=%d", top_k)
            matches = self._store.similarity_search_with_relevance_scores(query, k=top_k)
            results = [
                SearchResult(
                    score=score,
                    filename=str(document.metadata["filename"]),
                    chunk_id=int(document.metadata["chunk_id"]),
                    page_number=_page_number(document),
                    text=document.page_content,
                )
                for document, score in matches
            ]
            logger.info("ChromaDB search retrieved %d chunks", len(results))
            return results
        except NoIndexedDocumentsError:
            raise
        except Exception as error:
            raise VectorStoreError("Unable to search document vectors.") from error

    def _ensure_indexed_documents(self) -> None:
        """Raise the domain not-found error when the shared collection is empty."""
        if self._store._collection.count() == 0:
            raise NoIndexedDocumentsError("No indexed documents are available.")


def _distance_to_similarity(distance: float) -> float:
    """Normalize Chroma's non-negative distance so larger scores are better."""
    return 1.0 / (1.0 + distance)


def _page_number(document: Document) -> int | None:
    """Convert Chroma's unavailable-page sentinel back to ``None``."""
    page_number = document.metadata.get("page_number")
    if isinstance(page_number, int) and page_number >= 0:
        return page_number
    return None


_vector_store: LangChainVectorStore | None = None


def get_vector_store() -> LangChainVectorStore:
    """Return the application-wide LangChain wrapper for the existing collection."""
    global _vector_store
    if _vector_store is None:
        _vector_store = LangChainVectorStore(EmbeddingService())
    return _vector_store
