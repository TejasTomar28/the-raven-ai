"""Document API endpoints."""

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.services.document_parser import extract_text_from_pdf
from app.services.document_service import save_uploaded_document


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF document to upload")],
) -> dict[str, str]:
    """Store an uploaded PDF document and return its filename."""
    filename = await save_uploaded_document(file)
    return {"message": "Document uploaded successfully", "filename": filename}


@router.get("/{filename}/text")
def get_document_text(filename: str) -> dict[str, str]:
    """Return text extracted from every page of an uploaded PDF."""
    try:
        text = extract_text_from_pdf(filename)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        ) from None

    return {"filename": filename, "text": text}
