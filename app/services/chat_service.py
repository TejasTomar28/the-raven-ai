"""Framework-independent retrieval-augmented chat orchestration."""

from app.core.exceptions import InvalidSearchQueryError
from app.core.logging import logger
from app.langchain.rag_chain import LangChainRAG, langchain_rag
from app.schemas.chat import ChatResponse


class ChatService:
    """Retrieve document context and generate a grounded local LLM answer."""

    def __init__(self, rag_chain: LangChainRAG) -> None:
        """Create a chat service backed by one LangChain RAG chain."""
        self._rag_chain = rag_chain

    def answer_question(self, question: str) -> ChatResponse:
        """Answer a question using the top five semantically retrieved chunks."""
        if not question.strip():
            raise InvalidSearchQueryError("Question must not be empty.")

        logger.info("Incoming chat request")
        answer, documents = self._rag_chain.answer(question)
        sources = list(dict.fromkeys(str(document.metadata["filename"]) for document in documents))

        logger.info("Chat completed")
        return ChatResponse(
            question=question,
            answer=answer,
            sources=sources,
            retrieved_chunks=len(documents),
        )


chat_service = ChatService(rag_chain=langchain_rag)
