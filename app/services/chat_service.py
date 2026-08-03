"""Framework-independent retrieval-augmented chat orchestration."""

from langchain_core.documents import Document

from app.core.exceptions import InvalidSearchQueryError
from app.core.logging import logger
from app.langchain.rag_chain import LangChainRAG, langchain_rag
from app.schemas.chat import ChatResponse
from app.schemas.search import SearchResult

_MAX_CITATION_DOCUMENTS = 3
_DOMINANCE_SCORE_MARGIN = 0.50
_DOMINANCE_SCORE_RATIO = 2.0
_UNSUPPORTED_ANSWER_MARKERS = (
    "i could not find this information in the uploaded documents",
    "not contained in the uploaded documents",
    "not present in the uploaded documents",
    "not available in the uploaded documents",
    "not found in the uploaded documents",
    "not in the uploaded documents",
)


class ChatService:
    """Retrieve document context, generate an answer, and select concise citations."""

    def __init__(self, rag_chain: LangChainRAG) -> None:
        """Create a chat service backed by one LangChain RAG chain."""
        self._rag_chain = rag_chain

    def answer_question(self, question: str) -> ChatResponse:
        """Answer a question and return concise document-level citations."""
        if not question.strip():
            raise InvalidSearchQueryError("Question must not be empty.")

        logger.info("Incoming chat request")
        result = self._rag_chain.answer(question)
        supported = not _answer_indicates_unsupported(result.answer)
        selected_matches = _select_citation_matches(result.matches) if supported else []
        sources = [
            _to_search_result(document, score)
            for document, score in selected_matches
        ]

        logger.info(
            "Chat completed: supported=%s, retrieved chunks=%d, returned citations=%d",
            supported,
            len(result.matches),
            len(sources),
        )
        return ChatResponse(
            question=question,
            answer=result.answer,
            supported=supported,
            sources=sources,
            retrieved_chunks=len(result.matches),
        )


def _select_citation_matches(
    matches: list[tuple[Document, float]],
) -> list[tuple[Document, float]]:
    """Keep one highest-scoring chunk per document for concise citations."""
    best_by_filename: dict[str, tuple[Document, float]] = {}

    for document, score in matches:
        filename = str(document.metadata["filename"])
        current_best = best_by_filename.get(filename)
        if current_best is None or score > current_best[1]:
            best_by_filename[filename] = (document, score)

    ranked_documents = sorted(
        best_by_filename.values(),
        key=lambda match: match[1],
        reverse=True,
    )
    if _has_dominant_document(ranked_documents):
        return ranked_documents[:1]

    return ranked_documents[:_MAX_CITATION_DOCUMENTS]


def _has_dominant_document(matches: list[tuple[Document, float]]) -> bool:
    """Return whether the top document clearly outweighs all alternatives."""
    if len(matches) < 2:
        return False

    top_score = matches[0][1]
    next_score = matches[1][1]
    return (
        top_score - next_score >= _DOMINANCE_SCORE_MARGIN
        and top_score >= next_score * _DOMINANCE_SCORE_RATIO
    )


def _answer_indicates_unsupported(answer: str) -> bool:
    """Return whether the LLM explicitly says the archive lacks the requested answer."""
    normalized_answer = " ".join(answer.lower().split())
    return any(marker in normalized_answer for marker in _UNSUPPORTED_ANSWER_MARKERS)


def _to_search_result(document: Document, score: float) -> SearchResult:
    """Convert one LangChain document and relevance score into an API citation."""
    page_number = document.metadata.get("page_number")
    return SearchResult(
        score=score,
        filename=str(document.metadata["filename"]),
        chunk_id=int(document.metadata["chunk_id"]),
        page_number=page_number if isinstance(page_number, int) and page_number >= 0 else None,
        text=document.page_content,
    )


chat_service = ChatService(rag_chain=langchain_rag)
