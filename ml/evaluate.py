"""Evaluate the final persisted ML model once on the untouched test set."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from ml.scripts.config import BEST_MODEL_PATH, LABEL_ENCODER_PATH, TEST_DIRECTORY, TFIDF_VECTORIZER_PATH
from ml.scripts.dataset import load_labeled_pdfs
from ml.scripts.metrics import print_evaluation_report
from ml.scripts.preprocessing import TextPreprocessor


def evaluate_model(dataset_directory: str | None = None) -> None:
    """Evaluate saved artifacts once on test, retaining any unseen test class in the report."""
    test_directory = TEST_DIRECTORY if dataset_directory is None else Path(dataset_directory)
    _ensure_artifacts_exist()
    dataset = load_labeled_pdfs(test_directory, TextPreprocessor())
    model: Any = joblib.load(BEST_MODEL_PATH)
    vectorizer: Any = joblib.load(TFIDF_VECTORIZER_PATH)
    label_encoder: Any = joblib.load(LABEL_ENCODER_PATH)
    training_classes = [str(name) for name in label_encoder.classes_]
    class_names = sorted(set(training_classes).union(dataset.labels))
    unseen_test_classes = sorted(set(dataset.labels).difference(training_classes))
    if unseen_test_classes:
        print(
            "Warning: no usable training PDFs were available for test-only classes: "
            + ", ".join(unseen_test_classes)
        )

    predicted_indices = np.asarray(model.predict(vectorizer.transform(dataset.texts)), dtype=int).tolist()
    predicted_labels = [str(label_encoder.inverse_transform([index])[0]) for index in predicted_indices]
    label_indices = {label: index for index, label in enumerate(class_names)}
    y_true = [label_indices[label] for label in dataset.labels]
    y_predicted = [label_indices[label] for label in predicted_labels]
    print(f"Final test evaluation on {len(dataset.texts)} usable PDFs")
    print_evaluation_report("Final Test Metrics", y_true, y_predicted, class_names)


def _ensure_artifacts_exist() -> None:
    """Raise an actionable error when final training artifacts are unavailable."""
    missing = [
        path for path in (BEST_MODEL_PATH, TFIDF_VECTORIZER_PATH, LABEL_ENCODER_PATH) if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError("Train the model before evaluation. Missing: " + ", ".join(map(str, missing)))


def main() -> None:
    """Parse the optional test-directory override and run final evaluation."""
    parser = argparse.ArgumentParser(description="Evaluate RAVEN AI's final offline ML model.")
    parser.add_argument("--dataset", help="Optional class-directory test dataset path.")
    arguments = parser.parse_args()
    evaluate_model(arguments.dataset)


if __name__ == "__main__":
    main()
