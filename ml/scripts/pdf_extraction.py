"""Reusable PDF text extraction for offline document classification."""

from pathlib import Path

import fitz


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract plain text from non-empty pages of a PDF."""
    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, received: {pdf_path.name}")

    with fitz.open(pdf_path) as document:
        pages = [str(page.get_text("text")).strip() for page in document]

    return "\n".join(page for page in pages if page)
