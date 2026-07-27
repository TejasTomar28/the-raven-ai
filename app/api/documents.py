"""Document API endpoints."""

from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from app.services.documents import save_uploaded_document


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF document to upload")],
) -> dict[str, str]:
    """Store an uploaded PDF document and return its filename."""
    filename = await save_uploaded_document(file)
    return {"message": "Document uploaded successfully", "filename": filename}
