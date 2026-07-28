"""Retrieval-augmented chat API endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import (
    EmbeddingGenerationError,
    InvalidSearchQueryError,
    LLMGenerationError,
    NoIndexedDocumentsError,
    OllamaUnavailableError,
    VectorStoreError,
)
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service


router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Generate a grounded answer from retrieved uploaded-document context."""
    try:
        return chat_service.answer_question(request.question)
    except InvalidSearchQueryError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except NoIndexedDocumentsError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except OllamaUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama is unavailable.",
        ) from error
    except (EmbeddingGenerationError, VectorStoreError, LLMGenerationError) as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat generation failed.",
        ) from error
