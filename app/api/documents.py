"""Document API endpoints."""

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.exceptions import DuplicateDocumentError, InvalidDocumentError
from app.rag.chunker import chunk_text
from app.rag.parser import extract_text_from_pdf
from app.schemas.chunk import Chunk
from app.services.document_service import save_uploaded_document


router = APIRouter(prefix="/documents", tags=["documents"])


def _extract_uploaded_document_text(filename: str) -> str:
    """Extract an uploaded document's text or translate absence to HTTP 404."""
    try:
        return extract_text_from_pdf(filename)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        ) from None


@router.post("/upload")
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF document to upload")],
) -> dict[str, str]:
    """Store an uploaded PDF document and return its filename."""
    try:
        filename = await save_uploaded_document(file)
    except InvalidDocumentError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except DuplicateDocumentError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return {"message": "Document uploaded successfully", "filename": filename}


@router.get("/{filename}/text")
def get_document_text(filename: str) -> dict[str, str]:
    """Return text extracted from every page of an uploaded PDF."""
    text = _extract_uploaded_document_text(filename)

    return {"filename": filename, "text": text}


@router.get("/{filename}/chunks")
def get_document_chunks(filename: str) -> dict[str, str | int | list[Chunk]]:
    """Return overlapping text chunks extracted from an uploaded document."""
    chunks = chunk_text(
        _extract_uploaded_document_text(filename),
        source_document=filename,
    )
    return {
        "filename": filename,
        "total_chunks": len(chunks),
        "chunks": chunks,
    }
