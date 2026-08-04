"""Train and persist RAVEN AI's offline PDF document classifier."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC
from xgboost import XGBClassifier

from ml.scripts.config import (
    BEST_MODEL_PATH,
    LABEL_ENCODER_PATH,
    MAX_FEATURES,
    MODELS_DIRECTORY,
    RANDOM_STATE,
    TEST_DIRECTORY,
    TEST_SIZE,
    TFIDF_VECTORIZER_PATH,
    TRAIN_DIRECTORY,
    VALIDATION_SIZE,
)
from ml.scripts.dataset import (
    DocumentDataset,
    assert_dataset_audit_passes,
    class_distribution,
    create_test_split_if_empty,
    find_conflicting_label_groups,
    find_exact_duplicate_groups,
    load_labeled_pdfs,
    repeated_filenames_across_classes,
    shared_text_hashes,
    split_dataset,
)
from ml.scripts.metrics import ModelMetrics, format_comparison_table, print_evaluation_report
from ml.scripts.preprocessing import TextPreprocessor


def _build_vectorizer() -> TfidfVectorizer:
    """Create the shared TF-IDF configuration for every model run."""
    return TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        max_features=MAX_FEATURES,
        sublinear_tf=True,
    )


def _build_models(category_count: int) -> dict[str, Any]:
    """Create fresh candidate estimators for a fair model comparison."""
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=2_000, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "Linear SVM": LinearSVC(class_weight="balanced", random_state=RANDOM_STATE),
        "XGBoost": XGBClassifier(
            objective="multi:softprob",
            num_class=category_count,
            n_estimators=250,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="mlogloss",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }


def train_models(dataset_directory: str | None = None) -> None:
    """Select a model on validation data, then fit and save it on all training data."""
    train_directory = TRAIN_DIRECTORY if dataset_directory is None else Path(dataset_directory)
    preprocessor = TextPreprocessor()
    created_test_split = create_test_split_if_empty(
        train_directory, TEST_DIRECTORY, preprocessor, TEST_SIZE, RANDOM_STATE
    )
    if created_test_split:
        print("Created a deterministic duplicate-safe test split because test was empty.")

    train_dataset = load_labeled_pdfs(train_directory, preprocessor)
    test_dataset = load_labeled_pdfs(TEST_DIRECTORY, preprocessor)
    _print_dataset_audit(train_dataset, test_dataset)
    assert_dataset_audit_passes(train_dataset, test_dataset)

    label_encoder = LabelEncoder()
    encoded_labels = np.asarray(label_encoder.fit_transform(train_dataset.labels), dtype=int)
    split = split_dataset(train_dataset, VALIDATION_SIZE, RANDOM_STATE)
    x_development = [train_dataset.texts[index] for index in split.train_indices]
    x_validation = [train_dataset.texts[index] for index in split.validation_indices]
    y_development = encoded_labels[split.train_indices]
    y_validation = encoded_labels[split.validation_indices].tolist()
    class_names = sorted(set(train_dataset.labels))

    print(f"Validation split: {'group-aware stratified' if split.grouped_duplicates else 'stratified'}")
    print(f"Development distribution: {class_distribution(train_dataset, split.train_indices)}")
    print(f"Validation distribution: {class_distribution(train_dataset, split.validation_indices)}")

    development_vectorizer = _build_vectorizer()
    x_development_vectors = development_vectorizer.fit_transform(x_development)
    x_validation_vectors = development_vectorizer.transform(x_validation)
    metrics_by_model: dict[str, ModelMetrics] = {}

    for name, model in _build_models(len(class_names)).items():
        model.fit(x_development_vectors, y_development)
        predictions = np.asarray(model.predict(x_validation_vectors), dtype=int).tolist()
        metrics_by_model[name] = print_evaluation_report(
            f"Validation — {name}", y_validation, predictions, class_names
        )

    print("\n" + format_comparison_table(metrics_by_model))
    best_name = max(
        metrics_by_model,
        key=lambda name: (metrics_by_model[name].weighted_f1, metrics_by_model[name].macro_f1),
    )
    best_validation = metrics_by_model[best_name]

    final_vectorizer = _build_vectorizer()
    x_full_vectors = final_vectorizer.fit_transform(train_dataset.texts)
    final_labels = np.asarray(label_encoder.transform(train_dataset.labels), dtype=int)
    final_model = _build_models(len(class_names))[best_name]
    final_model.fit(x_full_vectors, final_labels)

    MODELS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, BEST_MODEL_PATH)
    joblib.dump(final_vectorizer, TFIDF_VECTORIZER_PATH)
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)
    print(
        f"\nSelected model: {best_name} (weighted F1: {best_validation.weighted_f1:.3f}, "
        f"macro F1: {best_validation.macro_f1:.3f})"
    )
    print(f"Retrained selected model on all {len(train_dataset.texts)} usable training PDFs.")
    print(f"Saved artifacts to {MODELS_DIRECTORY}")


def _print_dataset_audit(train_dataset: DocumentDataset, test_dataset: DocumentDataset) -> None:
    """Print the requested train/test audit without using test data for fitting."""
    duplicate_groups = find_exact_duplicate_groups(train_dataset)
    conflicting_groups = find_conflicting_label_groups(train_dataset, test_dataset)
    shared_hashes = shared_text_hashes(train_dataset, test_dataset)
    repeated_names = repeated_filenames_across_classes(train_dataset)
    repeated_names.update(repeated_filenames_across_classes(test_dataset))
    print("Dataset audit")
    print(
        f"Train PDFs: {len(train_dataset.paths) + train_dataset.skipped_empty_pdfs} "
        f"| usable: {len(train_dataset.texts)} | excluded: {train_dataset.skipped_empty_pdfs}"
    )
    print(
        f"Test PDFs: {len(test_dataset.paths) + test_dataset.skipped_empty_pdfs} "
        f"| usable: {len(test_dataset.texts)} | excluded: {test_dataset.skipped_empty_pdfs}"
    )
    print(f"Train class distribution: {class_distribution(train_dataset)}")
    print(f"Test class distribution: {class_distribution(test_dataset)}")
    print(f"Exact normalized-text duplicate groups in training: {len(duplicate_groups)}")
    for group in duplicate_groups:
        print(f"  SHA-256 {group.text_hash} | " + " | ".join(map(str, group.paths)))
    print(f"Conflicting-label exact duplicate groups: {len(conflicting_groups)}")
    for group in conflicting_groups:
        print(f"  CONFLICT SHA-256 {group.text_hash} | " + " | ".join(
            f"{label}: {path}" for path, label in zip(group.paths, group.labels, strict=True)
        ))
    print(f"Exact normalized-text hashes shared by train and test: {len(shared_hashes)}")
    print(f"Repeated filenames across classes: {len(repeated_names)}")
    for filename, paths in sorted(repeated_names.items()):
        print(f"  {filename}: " + " | ".join(map(str, paths)))


def main() -> None:
    """Parse CLI arguments and train the offline PDF classifier."""
    parser = argparse.ArgumentParser(description="Train RAVEN AI's offline PDF classifier.")
    parser.add_argument("--dataset", help="Optional class-directory training dataset path.")
    arguments = parser.parse_args()
    train_models(arguments.dataset)


if __name__ == "__main__":
    main()
