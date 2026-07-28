"""Services for storing uploaded documents."""

from pathlib import Path

from fastapi import UploadFile

from app.core.config import UPLOADS_DIRECTORY, get_uploaded_document_path
from app.core.constants import UPLOAD_CHUNK_SIZE
from app.core.exceptions import DuplicateDocumentError, InvalidDocumentError
from app.core.logging import logger

async def save_uploaded_document(file: UploadFile) -> str:
    """Validate and save a PDF upload, returning its sanitized filename.

    Args:
        file: The uploaded document.

    Raises:
        InvalidDocumentError: If the upload does not have a PDF extension.
        DuplicateDocumentError: If the upload would overwrite a document.
    """
    try:
        if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
            raise InvalidDocumentError("Only PDF files are allowed.")

        filename = Path(file.filename).name
        destination = get_uploaded_document_path(filename)
        UPLOADS_DIRECTORY.mkdir(parents=True, exist_ok=True)
        logger.info("Uploading document: %s", filename)

        if destination.exists():
            raise DuplicateDocumentError("A document with this filename already exists.")

        with destination.open("wb") as uploaded_file:
            while chunk := await file.read(UPLOAD_CHUNK_SIZE):
                uploaded_file.write(chunk)

        logger.info("Upload completed: %s", filename)
        return filename
    finally:
        await file.close()
