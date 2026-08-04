"""Local TF-IDF document classification backed by the validated ML artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from time import perf_counter
from typing import Any

import joblib

from app.core.config import BASE_DIR
from app.core.exceptions import DocumentClassificationError
from app.core.logging import logger
from ml.scripts.preprocessing import TextPreprocessor

_CLASSIFIER_NAME = "Linear SVM"
_MODEL_VERSION = "v1"
_MODELS_DIRECTORY = BASE_DIR / "ml" / "models"


@dataclass(frozen=True)
class ClassificationResult:
    """Category metadata produced by the deployed local ML classifier."""

    category: str
    classifier: str
    model_version: str
    confidence: float | None
    duration_ms: float


class DocumentClassificationService:
    """Load selected ML artifacts once and classify already extracted PDF text."""

    def __init__(self) -> None:
        """Initialize an unloaded, thread-safe classifier service."""
        self._model: Any | None = None
        self._vectorizer: Any | None = None
        self._label_encoder: Any | None = None
        self._preprocessor = TextPreprocessor()
        self._load_lock = Lock()

    def classify_text(self, text: str) -> ClassificationResult:
        """Classify extracted text using the persisted Linear SVM model."""
        started_at = perf_counter()
        try:
            normalized_text = self._preprocessor.transform(text)
            if not normalized_text:
                raise DocumentClassificationError("Document text is empty after preprocessing.")
            self._ensure_loaded()
            if self._model is None or self._vectorizer is None or self._label_encoder is None:
                raise DocumentClassificationError("Classifier artifacts are unavailable.")
            feature_vector = self._vectorizer.transform([normalized_text])
            predicted_index = int(self._model.predict(feature_vector)[0])
            category = str(self._label_encoder.inverse_transform([predicted_index])[0])
        except DocumentClassificationError:
            raise
        except Exception as error:
            raise DocumentClassificationError("Document classification failed.") from error

        duration_ms = (perf_counter() - started_at) * 1_000
        result = ClassificationResult(
            category=category,
            classifier=_CLASSIFIER_NAME,
            model_version=_MODEL_VERSION,
            confidence=None,
            duration_ms=duration_ms,
        )
        logger.info(
            "Document classified: category=%s classifier=%s version=%s duration_ms=%.1f",
            result.category,
            result.classifier,
            result.model_version,
            result.duration_ms,
        )
        return result

    def _ensure_loaded(self) -> None:
        """Load and validate ML artifacts once for the process lifetime."""
        if self._model is not None:
            return
        with self._load_lock:
            if self._model is not None:
                return
            try:
                model_path = _MODELS_DIRECTORY / "best_model.pkl"
                vectorizer_path = _MODELS_DIRECTORY / "tfidf_vectorizer.pkl"
                label_encoder_path = _MODELS_DIRECTORY / "label_encoder.pkl"
                for artifact_path in (model_path, vectorizer_path, label_encoder_path):
                    if not artifact_path.is_file():
                        raise FileNotFoundError(artifact_path)
                model = joblib.load(model_path)
                if type(model).__name__ != "LinearSVC":
                    raise TypeError("The deployed artifact is not the selected Linear SVM model.")
                self._model = model
                self._vectorizer = joblib.load(vectorizer_path)
                self._label_encoder = joblib.load(label_encoder_path)
                logger.info("Loaded document classifier artifacts: %s %s", _CLASSIFIER_NAME, _MODEL_VERSION)
            except Exception as error:
                raise DocumentClassificationError("Unable to load document classifier artifacts.") from error


document_classification_service = DocumentClassificationService()
