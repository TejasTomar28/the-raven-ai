"""Framework-independent semantic search orchestration."""

from app.core.exceptions import InvalidSearchQueryError
from app.core.logging import logger
from app.rag.embedding import EmbeddingService
from app.rag.vector_store import ChromaVectorStore
from app.schemas.search import SearchResponse


class SearchService:
    """Generate query embeddings and retrieve ranked document chunks."""

    def __init__(self, embedding_service: EmbeddingService) -> None:
        """Create a search service with a shared embedding service."""
        self._embedding_service = embedding_service
        self._vector_store: ChromaVectorStore | None = None

    @property
    def vector_store(self) -> ChromaVectorStore:
        """Initialize the persistent vector store when search is first requested."""
        if self._vector_store is None:
            self._vector_store = ChromaVectorStore()
        return self._vector_store

    def search(self, query: str, top_k: int = 5) -> SearchResponse:
        """Return ranked semantic matches for a natural-language query."""
        normalized_query = query.strip()
        if not normalized_query:
            raise InvalidSearchQueryError("Query must not be empty.")

        logger.info("Incoming search query: %s", normalized_query)
        query_embedding = self._embedding_service.embed_text(normalized_query)
        logger.info("Query embedding generated")
        results = self.vector_store.search(query_embedding, top_k=top_k)
        logger.info("Search completed: %d results", len(results))
        return SearchResponse(query=query, results=results)


search_service = SearchService(embedding_service=EmbeddingService())
