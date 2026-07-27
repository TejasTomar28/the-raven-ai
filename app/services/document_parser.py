"""Services for extracting text from uploaded PDF documents."""

from pathlib import Path

import fitz

from app.services.document_service import UPLOADS_DIRECTORY


def extract_text_from_pdf(filename: str) -> str:
    """Extract and combine text from every page of an uploaded PDF.

    Args:
        filename: Name of the PDF stored in the uploads directory.

    Raises:
        FileNotFoundError: If no uploaded file matches ``filename``.

    Returns:
        The document text in page order.
    """
    document_path = UPLOADS_DIRECTORY / Path(filename).name
    if not document_path.is_file():
        raise FileNotFoundError(filename)

    with fitz.open(document_path) as document:
        return "\n".join(page.get_text() for page in document)
