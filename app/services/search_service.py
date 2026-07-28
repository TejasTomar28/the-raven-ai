"""Framework-independent semantic search orchestration."""

from app.core.exceptions import InvalidSearchQueryError
from app.core.logging import logger
from app.langchain.vector_store import LangChainVectorStore, get_vector_store
from app.schemas.search import SearchResponse


class SearchService:
    """Generate query embeddings and retrieve ranked document chunks."""

    def __init__(self) -> None:
        """Create a search service that uses the shared LangChain vector store."""
        self._vector_store: LangChainVectorStore | None = None

    @property
    def vector_store(self) -> LangChainVectorStore:
        """Return the shared LangChain wrapper when search is first requested."""
        if self._vector_store is None:
            self._vector_store = get_vector_store()
        return self._vector_store

    def search(self, query: str, top_k: int = 5) -> SearchResponse:
        """Return ranked semantic matches for a natural-language query."""
        normalized_query = query.strip()
        if not normalized_query:
            raise InvalidSearchQueryError("Query must not be empty.")

        logger.info("Incoming search query: %s", normalized_query)
        results = self.vector_store.search(normalized_query, top_k=top_k)
        logger.info("Search completed: %d results", len(results))
        return SearchResponse(query=query, results=results)


search_service = SearchService()
