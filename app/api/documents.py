"""Document API endpoints."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import UPLOADS_DIRECTORY
from app.core.exceptions import (
    DocumentNotFoundError,
    DuplicateDocumentError,
    EmbeddingGenerationError,
    InvalidDocumentError,
    InvalidSearchQueryError,
    NoIndexedDocumentsError,
    VectorStoreError,
)
from app.rag.chunker import chunk_text
from app.rag.parser import extract_text_from_pdf
from app.schemas.chunk import Chunk
from app.schemas.document import DocumentListResponse, DocumentSummary
from app.schemas.search import SearchRequest, SearchResponse
from app.services.document_processing_service import document_processing_service
from app.services.document_service import delete_uploaded_document, save_uploaded_document
from app.services.search_service import search_service


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


@router.get("", response_model=DocumentListResponse)
def list_documents() -> DocumentListResponse:
    """Return uploaded PDF metadata for the knowledge archive."""
    if not UPLOADS_DIRECTORY.exists():
        return DocumentListResponse(documents=[])

    documents = [
        DocumentSummary(
            filename=document_path.name,
            size_bytes=document_path.stat().st_size,
            updated_at=datetime.fromtimestamp(document_path.stat().st_mtime, tz=timezone.utc),
        )
        for document_path in sorted(
            UPLOADS_DIRECTORY.glob("*.pdf"), key=lambda path: path.name.casefold()
        )
        if document_path.is_file()
    ]
    return DocumentListResponse(documents=documents)


@router.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest) -> SearchResponse:
    """Return ranked document chunks that are semantically similar to a query."""
    try:
        return search_service.search(request.query)
    except InvalidSearchQueryError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except NoIndexedDocumentsError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except (EmbeddingGenerationError, VectorStoreError) as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Semantic search failed.",
        ) from error


@router.post("/upload")
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF document to upload")],
) -> dict[str, str | int]:
    """Store, parse, embed, and index an uploaded PDF document."""
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

    try:
        chunk_count = document_processing_service.process_document(filename)
    except (EmbeddingGenerationError, VectorStoreError) as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document processing failed.",
        ) from error

    return {
        "message": "Document processed successfully",
        "filename": filename,
        "chunks": chunk_count,
    }


@router.delete("/{filename}")
def delete_document(filename: str) -> dict[str, str]:
    """Remove an uploaded PDF and all of its indexed knowledge records."""
    try:
        delete_uploaded_document(filename, document_processing_service.vector_store)
    except DocumentNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except VectorStoreError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document deletion failed.",
        ) from error

    return {"message": "Document deleted successfully", "filename": filename}


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
