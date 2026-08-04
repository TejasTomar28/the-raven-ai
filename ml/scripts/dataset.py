"""Dataset loading, auditing, and duplicate-safe splitting utilities."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
from pathlib import Path

import numpy as np
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold, train_test_split

from ml.scripts.pdf_extraction import extract_pdf_text
from ml.scripts.preprocessing import TextPreprocessor


@dataclass(frozen=True)
class DocumentDataset:
    """In-memory labelled documents prepared for training or evaluation."""

    texts: list[str]
    labels: list[str]
    paths: list[Path]
    text_hashes: list[str]
    skipped_empty_pdfs: int


@dataclass(frozen=True)
class DatasetSplit:
    """Deterministic split indices and whether exact duplicate groups were preserved."""

    train_indices: list[int]
    validation_indices: list[int]
    grouped_duplicates: bool


@dataclass(frozen=True)
class DuplicateGroup:
    """Exact duplicate normalized-text documents grouped by SHA-256 hash."""

    text_hash: str
    paths: list[Path]
    labels: list[str]


class DatasetAuditError(ValueError):
    """Raised when data quality would make model selection invalid."""


def load_labeled_pdfs(dataset_directory: Path, preprocessor: TextPreprocessor) -> DocumentDataset:
    """Extract and normalize PDFs arranged in class-named subdirectories."""
    if not dataset_directory.is_dir():
        raise FileNotFoundError(dataset_directory)

    texts: list[str] = []
    labels: list[str] = []
    paths: list[Path] = []
    text_hashes: list[str] = []
    skipped_empty_pdfs = 0
    for category_directory in sorted(path for path in dataset_directory.iterdir() if path.is_dir()):
        for pdf_path in sorted(category_directory.glob("*.pdf")):
            processed_text = preprocessor.transform(extract_pdf_text(pdf_path))
            if not processed_text:
                skipped_empty_pdfs += 1
                continue
            texts.append(processed_text)
            labels.append(category_directory.name)
            paths.append(pdf_path)
            text_hashes.append(hashlib.sha256(processed_text.encode("utf-8")).hexdigest())

    if not texts:
        raise ValueError(f"No non-empty PDF text found in {dataset_directory}")
    return DocumentDataset(texts, labels, paths, text_hashes, skipped_empty_pdfs)


def find_exact_duplicate_groups(dataset: DocumentDataset) -> list[DuplicateGroup]:
    """Return exact normalized-text duplicate groups for an audit."""
    grouped_indices: dict[str, list[int]] = defaultdict(list)
    for index, text_hash in enumerate(dataset.text_hashes):
        grouped_indices[text_hash].append(index)
    return [
        DuplicateGroup(
            text_hash=text_hash,
            paths=[dataset.paths[index] for index in indices],
            labels=[dataset.labels[index] for index in indices],
        )
        for text_hash, indices in sorted(grouped_indices.items())
        if len(indices) > 1
    ]


def find_conflicting_label_groups(*datasets: DocumentDataset) -> list[DuplicateGroup]:
    """Return exact text groups that are assigned more than one class label."""
    grouped_entries: dict[str, list[tuple[Path, str]]] = defaultdict(list)
    for dataset in datasets:
        for path, label, text_hash in zip(
            dataset.paths, dataset.labels, dataset.text_hashes, strict=True
        ):
            grouped_entries[text_hash].append((path, label))
    return [
        DuplicateGroup(
            text_hash=text_hash,
            paths=[path for path, _ in entries],
            labels=[label for _, label in entries],
        )
        for text_hash, entries in sorted(grouped_entries.items())
        if len({label for _, label in entries}) > 1
    ]


def assert_dataset_audit_passes(train: DocumentDataset, test: DocumentDataset) -> None:
    """Fail before fitting when labels conflict or train/test text leakage exists."""
    missing_train_classes = sorted(set(test.labels).difference(train.labels))
    conflicts = find_conflicting_label_groups(train, test)
    leaked_hashes = shared_text_hashes(train, test)
    failures: list[str] = []
    if missing_train_classes:
        failures.append(
            "test classes with no usable training PDFs: " + ", ".join(missing_train_classes)
        )
    if conflicts:
        details = "; ".join(
            f"{group.text_hash}: " + ", ".join(
                f"{label} ({path})" for path, label in zip(group.paths, group.labels, strict=True)
            )
            for group in conflicts
        )
        failures.append("conflicting labels for identical normalized text: " + details)
    if leaked_hashes:
        failures.append(
            "exact normalized-text leakage between train and test: " + ", ".join(sorted(leaked_hashes))
        )
    if failures:
        raise DatasetAuditError("Dataset audit failed. " + " | ".join(failures))


def repeated_filenames_across_classes(dataset: DocumentDataset) -> dict[str, list[Path]]:
    """Return filenames reused by more than one class in one dataset split."""
    grouped_paths: dict[str, list[int]] = defaultdict(list)
    for index, path in enumerate(dataset.paths):
        grouped_paths[path.name.casefold()].append(index)
    return {
        filename: [dataset.paths[index] for index in indices]
        for filename, indices in grouped_paths.items()
        if len({dataset.labels[index] for index in indices}) > 1
    }


def shared_text_hashes(first: DocumentDataset, second: DocumentDataset) -> set[str]:
    """Return normalized text hashes present in both datasets."""
    return set(first.text_hashes).intersection(second.text_hashes)


def class_distribution(dataset: DocumentDataset, indices: list[int] | None = None) -> dict[str, int]:
    """Return a sorted class-count mapping for all or selected documents."""
    selected = range(len(dataset.labels)) if indices is None else indices
    return dict(sorted(Counter(dataset.labels[index] for index in selected).items()))


def split_dataset(dataset: DocumentDataset, validation_size: float, random_state: int) -> DatasetSplit:
    """Create a validation split without allowing exact-text leakage."""
    indices = list(range(len(dataset.texts)))
    if not find_exact_duplicate_groups(dataset):
        train_indices, validation_indices = train_test_split(
            indices, test_size=validation_size, random_state=random_state, stratify=dataset.labels
        )
        return DatasetSplit(list(train_indices), list(validation_indices), False)
    return _grouped_split(dataset, validation_size, random_state)


def create_test_split_if_empty(
    train_directory: Path,
    test_directory: Path,
    preprocessor: TextPreprocessor,
    test_size: float,
    random_state: int,
) -> bool:
    """Create a deterministic duplicate-safe physical test split only when test is empty."""
    if any(test_directory.rglob("*.pdf")):
        return False
    dataset = load_labeled_pdfs(train_directory, preprocessor)
    split = split_dataset(dataset, test_size, random_state)
    for index in split.validation_indices:
        source = dataset.paths[index]
        destination = test_directory / dataset.labels[index] / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing test document: {destination}")
        source.replace(destination)
    return True


def _grouped_split(dataset: DocumentDataset, validation_size: float, random_state: int) -> DatasetSplit:
    """Use stratified groups when possible, preserving duplicate-text groups."""
    labels = np.asarray(dataset.labels)
    groups = np.asarray(dataset.text_hashes)
    group_counts = Counter(zip(dataset.labels, dataset.text_hashes, strict=True))
    distinct_groups = Counter(label for label, _ in group_counts)
    minimum_groups = min(distinct_groups.values())
    if minimum_groups >= 2:
        splitter = StratifiedGroupKFold(
            n_splits=min(5, minimum_groups), shuffle=True, random_state=random_state
        )
        target_size = len(dataset.texts) * validation_size
        candidates = list(splitter.split(np.zeros(len(labels)), labels, groups))
        train_indices, validation_indices = min(
            candidates, key=lambda candidate: abs(len(candidate[1]) - target_size)
        )
    else:
        splitter = GroupShuffleSplit(n_splits=1, test_size=validation_size, random_state=random_state)
        train_indices, validation_indices = next(splitter.split(np.zeros(len(labels)), labels, groups))
    return DatasetSplit(
        [int(index) for index in train_indices],
        [int(index) for index in validation_indices],
        True,
    )
