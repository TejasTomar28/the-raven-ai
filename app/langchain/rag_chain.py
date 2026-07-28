"""Reusable LangChain retrieval-and-generation chain."""

import httpx
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from ollama import ResponseError

from app.core.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.core.constants import OLLAMA_REQUEST_TIMEOUT_SECONDS
from app.core.exceptions import LLMGenerationError, OllamaUnavailableError
from app.core.logging import logger
from app.langchain.vector_store import get_vector_store


class LangChainRAG:
    """Retrieve relevant chunks and answer with a local LangChain ChatOllama chain."""

    def __init__(self) -> None:
        """Create the reusable prompt and local Ollama answer chain."""
        self._prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an enterprise knowledge assistant.

Answer ONLY from the retrieved context. Never hallucinate. If the information
is unavailable, clearly state that it is not contained in the uploaded documents.
Keep responses concise and professional.

Retrieved context:
{context}""",
                ),
                ("human", "{question}"),
            ]
        )
        self._llm = ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL,
            temperature=0,
            client_kwargs={"timeout": OLLAMA_REQUEST_TIMEOUT_SECONDS},
        )
        self._answer_chain = self._prompt | self._llm | StrOutputParser()

    def answer(self, question: str) -> tuple[str, list[Document]]:
        """Retrieve top chunks once and generate a grounded answer from them."""
        retriever = get_vector_store().as_retriever(top_k=5)
        try:
            documents = retriever.invoke(question)
            logger.info("LangChain retrieval completed: %d chunks", len(documents))
            answer = self._answer_chain.invoke(
                {
                    "question": question,
                    "context": _format_documents(documents),
                }
            )
            logger.info("LangChain RAG chain completed")
            return answer, documents
        except (httpx.ConnectError, httpx.ConnectTimeout) as error:
            raise OllamaUnavailableError("Ollama is unavailable.") from error
        except (httpx.TimeoutException, ResponseError) as error:
            raise LLMGenerationError("Ollama could not generate an answer.") from error
        except (OllamaUnavailableError, LLMGenerationError):
            raise
        except Exception as error:
            raise LLMGenerationError("LangChain RAG generation failed.") from error


def _format_documents(documents: list[Document]) -> str:
    """Format retrieved document text for the reusable prompt template."""
    return "\n\n---\n\n".join(document.page_content for document in documents)


langchain_rag = LangChainRAG()
