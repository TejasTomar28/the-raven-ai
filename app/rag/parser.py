"""PDF text extraction utilities for the RAG pipeline."""

import fitz

from app.core.config import get_uploaded_document_path
from app.core.logging import logger


def extract_text_from_pdf(filename: str) -> str:
    """Extract and combine text from every page of an uploaded PDF.

    Args:
        filename: Name of the PDF stored in the uploads directory.

    Raises:
        FileNotFoundError: If no uploaded file matches ``filename``.

    Returns:
        The document text in page order.
    """
    document_path = get_uploaded_document_path(filename)
    if not document_path.is_file():
        raise FileNotFoundError(filename)

    logger.info("Text extraction started: %s", document_path.name)
    with fitz.open(document_path) as document:
        page_texts = [str(page.get_text()) for page in document]
        text = "\n".join(page_texts)

    logger.info(
        "Text extraction completed: %s (%d characters)",
        document_path.name,
        len(text),
    )
    return text
