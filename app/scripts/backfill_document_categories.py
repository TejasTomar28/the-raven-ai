"""Backfill ML classification metadata for already uploaded documents."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from app.core.config import UPLOADS_DIRECTORY
from app.core.exceptions import DocumentClassificationError, DocumentMetadataError, VectorStoreError
from app.core.logging import logger
from app.langchain.vector_store import LangChainVectorStore, get_vector_store
from app.rag.parser import extract_text_from_pdf
from app.services.document_classification_service import ClassificationResult, document_classification_service
from app.services.document_metadata_service import document_metadata_service


def backfill_document_categories(force: bool = False) -> tuple[int, int]:
    """Classify uploaded PDFs missing metadata without reindexing ChromaDB."""
    processed = 0
    skipped = 0
    vector_store = get_vector_store()
    if not UPLOADS_DIRECTORY.exists():
        return processed, skipped
    for path in sorted(UPLOADS_DIRECTORY.glob("*.pdf"), key=lambda item: item.name.casefold()):
        existing = document_metadata_service.get(path.name)
        if not force and existing and existing.get("category"):
            skipped += 1
            continue
        try:
            text = extract_text_from_pdf(path.name)
            classification = document_classification_service.classify_text(text)
        except (DocumentClassificationError, FileNotFoundError):
            logger.exception("Category backfill failed for %s; using general fallback", path.name)
            classification = ClassificationResult("general", "fallback", "v1", None, 0.0)
        try:
            document_metadata_service.upsert(
                filename=path.name,
                category=classification.category,
                classifier=classification.classifier,
                model_version=classification.model_version,
                classification_confidence=classification.confidence,
                uploaded_at=datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc),
                file_size=path.stat().st_size,
                chunk_count=_existing_chunk_count(vector_store, path.name, existing),
            )
            processed += 1
        except DocumentMetadataError:
            logger.exception("Metadata backfill failed for %s", path.name)
    return processed, skipped


def _existing_chunk_count(
    vector_store: LangChainVectorStore, filename: str, existing: dict[str, object] | None
) -> int:
    """Read existing vector count without indexing or changing ChromaDB records."""
    try:
        return vector_store.count_chunks(filename)
    except VectorStoreError:
        logger.exception("Unable to count vectors for %s during backfill", filename)
        value = existing.get("chunk_count") if existing else None
        return value if isinstance(value, int) else 0


def main() -> None:
    """Run document-category backfill from the repository root."""
    parser = argparse.ArgumentParser(description="Backfill RAVEN AI document categories.")
    parser.add_argument("--force", action="store_true", help="Reclassify documents with existing metadata.")
    arguments = parser.parse_args()
    processed, skipped = backfill_document_categories(force=arguments.force)
    print(f"Backfill complete: processed={processed}, skipped={skipped}")


if __name__ == "__main__":
    main()
