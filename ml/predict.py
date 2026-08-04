"""Predict one PDF category using the saved offline ML artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import joblib

from ml.scripts.config import BEST_MODEL_PATH, LABEL_ENCODER_PATH, TFIDF_VECTORIZER_PATH
from ml.scripts.pdf_extraction import extract_pdf_text
from ml.scripts.preprocessing import TextPreprocessor


def predict_pdf(pdf_path: Path) -> tuple[str, float | None]:
    """Return a PDF category and native model confidence, when available."""
    _ensure_artifacts_exist()
    processed_text = TextPreprocessor().transform(extract_pdf_text(pdf_path))
    if not processed_text:
        raise ValueError("The PDF does not contain enough extractable text to classify.")
    model: Any = joblib.load(BEST_MODEL_PATH)
    vectorizer: Any = joblib.load(TFIDF_VECTORIZER_PATH)
    label_encoder: Any = joblib.load(LABEL_ENCODER_PATH)
    features = vectorizer.transform([processed_text])
    predicted_index = int(model.predict(features)[0])
    category = str(label_encoder.inverse_transform([predicted_index])[0])
    confidence = _native_confidence(model, features, predicted_index)
    return category, confidence


def _native_confidence(model: Any, features: Any, predicted_index: int) -> float | None:
    """Return only a model-provided probability; never fabricate LinearSVC confidence."""
    if not hasattr(model, "predict_proba"):
        return None
    probabilities = model.predict_proba(features)
    return float(probabilities[0][predicted_index])


def _ensure_artifacts_exist() -> None:
    """Raise an actionable error when training artifacts are unavailable."""
    missing = [
        path for path in (BEST_MODEL_PATH, TFIDF_VECTORIZER_PATH, LABEL_ENCODER_PATH) if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError("Train the model before prediction. Missing: " + ", ".join(map(str, missing)))


def main() -> None:
    """Parse a PDF path and print its persisted-model prediction."""
    parser = argparse.ArgumentParser(description="Predict a PDF category with RAVEN AI's ML model.")
    parser.add_argument("pdf_path", type=Path, help="Path to the PDF to classify.")
    arguments = parser.parse_args()
    category, confidence = predict_pdf(arguments.pdf_path)
    print(f"Predicted Category: {category}")
    if confidence is None:
        print("Prediction Confidence: unavailable (model has no native probabilities)")
    else:
        print(f"Prediction Confidence: {confidence:.1%}")


if __name__ == "__main__":
    main()
