"""Framework-independent retrieval-augmented chat orchestration."""

from app.core.exceptions import InvalidSearchQueryError
from app.core.logging import logger
from app.rag.llm import LLMService
from app.schemas.chat import ChatResponse
from app.services.search_service import SearchService, search_service


class ChatService:
    """Retrieve document context and generate a grounded local LLM answer."""

    def __init__(self, search: SearchService, llm_service: LLMService) -> None:
        """Create a chat service with semantic-search and LLM dependencies."""
        self._search = search
        self._llm_service = llm_service

    def answer_question(self, question: str) -> ChatResponse:
        """Answer a question using the top five semantically retrieved chunks."""
        if not question.strip():
            raise InvalidSearchQueryError("Question must not be empty.")

        logger.info("Incoming chat request")
        search_response = self._search.search(question, top_k=5)
        logger.info("Semantic search completed: %d chunks", len(search_response.results))

        context = [result.text for result in search_response.results]
        answer = self._llm_service.generate_answer(question, context)
        sources = list(dict.fromkeys(result.filename for result in search_response.results))

        logger.info("Chat completed")
        return ChatResponse(
            question=question,
            answer=answer,
            sources=sources,
            retrieved_chunks=len(search_response.results),
        )


chat_service = ChatService(search=search_service, llm_service=LLMService())
