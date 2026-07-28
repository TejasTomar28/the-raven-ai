"""Text chunking utilities for the RAG pipeline."""

from app.core.logging import logger
from app.core.constants import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE
from app.core.exceptions import InvalidChunkConfigurationError
from app.schemas.chunk import Chunk


def chunk_text(
    text: str,
    source_document: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Chunk]:
    """Split text into fixed-size chunks with overlap between neighbours.

    Args:
        text: Source text to split.
        source_document: Filename of the document that produced ``text``.
        chunk_size: Maximum number of characters in a chunk.
        chunk_overlap: Number of characters shared by adjacent chunks.

    Raises:
        InvalidChunkConfigurationError: If the parameters cannot make forward progress.

    Returns:
        Non-empty chunks in their original order.
    """
    if chunk_size <= 0:
        raise InvalidChunkConfigurationError("chunk_size must be greater than zero")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise InvalidChunkConfigurationError(
            "chunk_overlap must be zero or greater and less than chunk_size"
        )
    if not text:
        logger.info("Chunk generation completed: 0 chunks (average length: 0.00 characters)")
        return []

    step_size = chunk_size - chunk_overlap
    chunks: list[Chunk] = []
    start = 0

    while start < len(text):
        chunk_text_value = text[start : start + chunk_size]
        if chunk_text_value:
            chunks.append(
                Chunk(
                    id=len(chunks) + 1,
                    text=chunk_text_value,
                    source_document=source_document,
                    page_number=None,
                    start_char=start,
                    end_char=start + len(chunk_text_value),
                )
            )

        if start + chunk_size >= len(text):
            break
        start += step_size

    average_chunk_length = sum(len(chunk.text) for chunk in chunks) / len(chunks)
    logger.info(
        "Chunk generation completed: %d chunks (average length: %.2f characters)",
        len(chunks),
        average_chunk_length,
    )
    return chunks
