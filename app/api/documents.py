"""Document API endpoints."""

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import UPLOADS_DIRECTORY
from app.core.exceptions import (
    DocumentMetadataError,
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
from app.services.document_metadata_service import document_metadata_service
from app.services.document_processing_service import document_processing_service
from app.services.document_service import delete_uploaded_document, save_uploaded_document
from app.services.search_service import search_service

router = APIRouter(prefix="/documents", tags=["documents"])


def _extract_uploaded_document_text(filename: str) -> str:
    """Extract an uploaded document's text or translate absence to HTTP 404."""
    try:
        return extract_text_from_pdf(filename)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.") from None


@router.get("", response_model=DocumentListResponse)
def list_documents() -> DocumentListResponse:
    """Return uploaded PDFs with persisted classification metadata."""
    if not UPLOADS_DIRECTORY.exists():
        return DocumentListResponse(documents=[])
    try:
        metadata_by_filename = document_metadata_service.list()
    except DocumentMetadataError:
        metadata_by_filename = {}

    documents = [
        _document_summary(document_path, metadata_by_filename.get(document_path.name, {}))
        for document_path in sorted(UPLOADS_DIRECTORY.glob("*.pdf"), key=lambda path: path.name.casefold())
        if document_path.is_file()
    ]
    return DocumentListResponse(documents=documents)


def _document_summary(document_path: Any, metadata: dict[str, Any]) -> DocumentSummary:
    """Merge filesystem facts with persisted metadata and legacy archive fields."""
    archived_at = datetime.fromtimestamp(document_path.stat().st_mtime, tz=timezone.utc)
    uploaded_at = _metadata_datetime(metadata.get("uploaded_at"), archived_at)
    file_size = document_path.stat().st_size
    return DocumentSummary(
        filename=document_path.name,
        size_bytes=file_size,
        file_size=file_size,
        updated_at=uploaded_at,
        uploaded_at=uploaded_at,
        chunk_count=int(metadata.get("chunk_count", 0)),
        category=str(metadata.get("category", "general")),
        classifier=str(metadata.get("classifier", "fallback")),
        model_version=str(metadata.get("model_version", "v1")),
        classification_confidence=metadata.get("classification_confidence"),
    )


def _metadata_datetime(value: object, fallback: datetime) -> datetime:
    """Parse stored timestamps while retaining backward compatibility for old PDFs."""
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass
    return fallback


@router.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest) -> SearchResponse:
    """Return ranked document chunks that are semantically similar to a query."""
    try:
        return search_service.search(request.query)
    except InvalidSearchQueryError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except NoIndexedDocumentsError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except (EmbeddingGenerationError, VectorStoreError) as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Semantic search failed.") from error


@router.post("/upload")
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF document to upload")],
) -> dict[str, str | int]:
    """Store, classify, embed, and index an uploaded PDF document."""
    try:
        filename = await save_uploaded_document(file)
    except InvalidDocumentError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except DuplicateDocumentError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error

    try:
        result = document_processing_service.process_document(filename)
    except (EmbeddingGenerationError, VectorStoreError) as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Document processing failed.") from error

    return {
        "message": "Document processed successfully",
        "filename": filename,
        "chunks": result.chunk_count,
        "category": result.classification.category,
    }


@router.delete("/{filename}")
def delete_document(filename: str) -> dict[str, str]:
    """Remove an uploaded PDF, its vectors, and persisted metadata."""
    try:
        delete_uploaded_document(filename, document_processing_service.vector_store)
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except (VectorStoreError, DocumentMetadataError) as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Document deletion failed.") from error
    return {"message": "Document deleted successfully", "filename": filename}


@router.get("/{filename}/text")
def get_document_text(filename: str) -> dict[str, str]:
    """Return text extracted from every page of an uploaded PDF."""
    return {"filename": filename, "text": _extract_uploaded_document_text(filename)}


@router.get("/{filename}/chunks")
def get_document_chunks(filename: str) -> dict[str, str | int | list[Chunk]]:
    """Return overlapping text chunks extracted from an uploaded document."""
    chunks = chunk_text(_extract_uploaded_document_text(filename), source_document=filename)
    return {"filename": filename, "total_chunks": len(chunks), "chunks": chunks}
