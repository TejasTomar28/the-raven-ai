"""Service for indexing and classifying uploaded documents."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.exceptions import DocumentClassificationError, DocumentMetadataError
from app.core.logging import logger
from app.langchain.vector_store import LangChainVectorStore, get_vector_store
from app.rag.chunker import chunk_text
from app.rag.parser import extract_text_from_pdf
from app.services.document_classification_service import (
    ClassificationResult,
    document_classification_service,
)
from app.services.document_metadata_service import document_metadata_service
from app.core.config import get_uploaded_document_path


@dataclass(frozen=True)
class DocumentProcessingResult:
    """Indexing and classification details produced for one uploaded document."""

    chunk_count: int
    classification: ClassificationResult


class DocumentProcessingService:
    """Coordinate parsing, classification, indexing, and metadata persistence."""

    def __init__(self) -> None:
        """Create a document processor with lazy vector-store initialization."""
        self._vector_store: LangChainVectorStore | None = None

    @property
    def vector_store(self) -> LangChainVectorStore:
        """Return the shared LangChain wrapper for persistent vector storage."""
        if self._vector_store is None:
            self._vector_store = get_vector_store()
        return self._vector_store

    def process_document(self, filename: str) -> DocumentProcessingResult:
        """Extract, classify, chunk, and persist vectors and metadata for one PDF."""
        logger.info("Extracting text for %s", filename)
        text = extract_text_from_pdf(filename)
        classification = self._classify_or_fallback(filename, text)

        logger.info("Creating chunks for %s", filename)
        chunks = chunk_text(text, source_document=filename)
        self.vector_store.store_chunks(filename, chunks)
        self._persist_metadata(filename, classification, len(chunks))

        logger.info("Processing completed for %s: %d chunks", filename, len(chunks))
        return DocumentProcessingResult(chunk_count=len(chunks), classification=classification)

    def _classify_or_fallback(self, filename: str, text: str) -> ClassificationResult:
        """Classify text while preserving indexing availability on classifier failure."""
        try:
            return document_classification_service.classify_text(text)
        except DocumentClassificationError:
            logger.exception("Document classification failed for %s; using general fallback", filename)
            return ClassificationResult(
                category="general",
                classifier="fallback",
                model_version="v1",
                confidence=None,
                duration_ms=0.0,
            )

    def _persist_metadata(
        self, filename: str, classification: ClassificationResult, chunk_count: int
    ) -> None:
        """Persist classification without allowing metadata outages to block indexing."""
        try:
            path = get_uploaded_document_path(filename)
            document_metadata_service.upsert(
                filename=filename,
                category=classification.category,
                classifier=classification.classifier,
                model_version=classification.model_version,
                classification_confidence=classification.confidence,
                uploaded_at=datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc),
                file_size=path.stat().st_size,
                chunk_count=chunk_count,
            )
        except (DocumentMetadataError, OSError):
            logger.exception("Document metadata persistence failed for %s", filename)


document_processing_service = DocumentProcessingService()
