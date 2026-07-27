"""Services for storing uploaded documents."""

from pathlib import Path

from fastapi import HTTPException, UploadFile, status


UPLOADS_DIRECTORY = Path(__file__).resolve().parents[2] / "uploads"
CHUNK_SIZE = 1024 * 1024


async def save_uploaded_document(file: UploadFile) -> str:
    """Validate and save a PDF upload, returning its sanitized filename.

    Args:
        file: The uploaded document.

    Raises:
        HTTPException: If the upload does not have a PDF extension.
    """
    try:
        if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed.",
            )

        filename = Path(file.filename).name
        destination = UPLOADS_DIRECTORY / filename
        UPLOADS_DIRECTORY.mkdir(parents=True, exist_ok=True)

        if destination.exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A document with this filename already exists.",
            )

        with destination.open("wb") as uploaded_file:
            while chunk := await file.read(CHUNK_SIZE):
                uploaded_file.write(chunk)

        return filename
    finally:
        await file.close()
