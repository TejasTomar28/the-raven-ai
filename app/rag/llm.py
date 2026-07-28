"""Local Ollama client for grounded RAG answer generation."""

import json
from urllib import error, request

from app.core.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.core.constants import OLLAMA_REQUEST_TIMEOUT_SECONDS
from app.core.exceptions import LLMGenerationError, OllamaUnavailableError
from app.core.logging import logger


class LLMService:
    """Generate grounded answers through a locally running Ollama server."""

    def generate_answer(self, question: str, context: list[str]) -> str:
        """Return an answer based only on the provided retrieved document context."""
        prompt = _build_prompt(question, context)
        logger.info("Prompt generated")
        payload = json.dumps(
            {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            }
        ).encode("utf-8")
        endpoint = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
        ollama_request = request.Request(
            endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            logger.info("LLM request started: url=%s model=%s", endpoint, OLLAMA_MODEL)
            with request.urlopen(ollama_request, timeout=OLLAMA_REQUEST_TIMEOUT_SECONDS) as response:
                status_code = response.status
                response_body = _read_response_body(response)
        except error.HTTPError as error_response:
            response_body = _read_response_body(error_response)
            _log_ollama_failure(
                endpoint,
                error_response.code,
                response_body,
                error_response,
            )
            raise LLMGenerationError(
                f"Ollama returned HTTP status {error_response.code}."
            ) from error_response
        except error.URLError as error_response:
            _log_ollama_failure(endpoint, None, "", error_response)
            if isinstance(error_response.reason, TimeoutError):
                raise LLMGenerationError("Ollama request timed out.") from error_response
            raise OllamaUnavailableError("Ollama is unavailable.") from error_response
        except TimeoutError as error_response:
            _log_ollama_failure(endpoint, None, "", error_response)
            raise LLMGenerationError("Ollama request timed out.") from error_response

        logger.info(
            "Ollama HTTP response: url=%s model=%s status=%d body=%s",
            endpoint,
            OLLAMA_MODEL,
            status_code,
            response_body[:500],
        )
        if not 200 <= status_code < 300:
            generation_error = LLMGenerationError(
                f"Ollama returned HTTP status {status_code}."
            )
            _log_ollama_failure(endpoint, status_code, response_body, generation_error)
            raise generation_error

        try:
            response_payload = json.loads(response_body)
        except json.JSONDecodeError as error_response:
            _log_ollama_failure(endpoint, status_code, response_body, error_response)
            raise LLMGenerationError("Ollama returned an invalid response.") from error_response

        answer = response_payload.get("response") if isinstance(response_payload, dict) else None
        if not isinstance(answer, str) or not answer.strip():
            generation_error = LLMGenerationError("Ollama returned an empty answer.")
            _log_ollama_failure(endpoint, status_code, response_body, generation_error)
            raise generation_error

        logger.info("LLM response received")
        return answer.strip()


def _build_prompt(question: str, context: list[str]) -> str:
    """Build the constrained enterprise knowledge-answering prompt."""
    context_text = "\n\n---\n\n".join(context)
    return f"""You are an enterprise knowledge assistant.

Answer ONLY using the provided context.

If the answer is not present in the context,
reply:

\"I could not find this information in the uploaded documents.\"

Context:

{context_text}

Question:

{question}

Answer:

Do not include chain-of-thought.

Return only the final answer."""


def _read_response_body(response: object) -> str:
    """Read and decode an Ollama HTTP response body for parsing and diagnostics."""
    try:
        return response.read().decode("utf-8", errors="replace")  # type: ignore[union-attr]
    except Exception as error_response:
        return f"<unable to read response body: {error_response!r}>"


def _log_ollama_failure(
    endpoint: str,
    status_code: int | None,
    response_body: str,
    error_response: BaseException,
) -> None:
    """Log complete Ollama diagnostics before raising a domain exception."""
    logger.error(
        "Ollama request failed: url=%s model=%s status=%s body=%s exception=%r",
        endpoint,
        OLLAMA_MODEL,
        status_code,
        response_body[:500],
        error_response,
    )
