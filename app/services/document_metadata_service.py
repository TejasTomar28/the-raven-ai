"""Persistent metadata storage for uploaded RAVEN AI documents."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from app.core.config import DOCUMENT_METADATA_PATH
from app.core.exceptions import DocumentMetadataError


class DocumentMetadataService:
    """Read and atomically update document metadata stored in a JSON file."""

    def get(self, filename: str) -> dict[str, Any] | None:
        """Return one document metadata record when available."""
        return self._read_all().get(Path(filename).name)

    def list(self) -> dict[str, dict[str, Any]]:
        """Return all persisted metadata keyed by safe filename."""
        return self._read_all()

    def upsert(
        self,
        *,
        filename: str,
        category: str,
        classifier: str,
        model_version: str,
        classification_confidence: float | None,
        uploaded_at: datetime,
        file_size: int,
        chunk_count: int,
    ) -> None:
        """Persist a complete metadata record for one uploaded document."""
        records = self._read_all()
        records[Path(filename).name] = {
            "filename": Path(filename).name,
            "category": category,
            "classifier": classifier,
            "model_version": model_version,
            "classification_confidence": classification_confidence,
            "uploaded_at": uploaded_at.astimezone(timezone.utc).isoformat(),
            "file_size": file_size,
            "chunk_count": chunk_count,
        }
        self._write_all(records)

    def delete(self, filename: str) -> None:
        """Remove a document metadata record, if one exists."""
        records = self._read_all()
        records.pop(Path(filename).name, None)
        self._write_all(records)

    def _read_all(self) -> dict[str, dict[str, Any]]:
        """Read validated JSON metadata, treating a missing file as empty storage."""
        if not DOCUMENT_METADATA_PATH.is_file():
            return {}
        try:
            payload = json.loads(DOCUMENT_METADATA_PATH.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Metadata root must be an object.")
            return {str(key): value for key, value in payload.items() if isinstance(value, dict)}
        except Exception as error:
            raise DocumentMetadataError("Unable to read document metadata.") from error

    def _write_all(self, records: dict[str, dict[str, Any]]) -> None:
        """Atomically replace the JSON metadata file."""
        try:
            DOCUMENT_METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
            temporary_path = DOCUMENT_METADATA_PATH.with_suffix(".tmp")
            temporary_path.write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")
            temporary_path.replace(DOCUMENT_METADATA_PATH)
        except Exception as error:
            raise DocumentMetadataError("Unable to persist document metadata.") from error


document_metadata_service = DocumentMetadataService()
