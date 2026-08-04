"""Metrics and report helpers for classifier evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)


@dataclass(frozen=True)
class ModelMetrics:
    """Accuracy plus macro and weighted classification metrics."""

    accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    weighted_precision: float
    weighted_recall: float
    weighted_f1: float


def calculate_metrics(y_true: list[int], y_pred: list[int]) -> ModelMetrics:
    """Calculate the requested macro and weighted classification metrics."""
    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=cast(Any, 0)
    )
    weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=cast(Any, 0)
    )
    return ModelMetrics(
        accuracy=float(accuracy_score(y_true, y_pred)),
        macro_precision=float(macro_precision),
        macro_recall=float(macro_recall),
        macro_f1=float(macro_f1),
        weighted_precision=float(weighted_precision),
        weighted_recall=float(weighted_recall),
        weighted_f1=float(weighted_f1),
    )


def print_evaluation_report(
    title: str,
    y_true: list[int],
    y_pred: list[int],
    class_names: list[str],
) -> ModelMetrics:
    """Print a complete metric, matrix, and per-class report and return its metrics."""
    metrics = calculate_metrics(y_true, y_pred)
    print(f"\n{title}")
    print(f"Accuracy:           {metrics.accuracy:.3f}")
    print(f"Macro Precision:    {metrics.macro_precision:.3f}")
    print(f"Macro Recall:       {metrics.macro_recall:.3f}")
    print(f"Macro F1:           {metrics.macro_f1:.3f}")
    print(f"Weighted Precision: {metrics.weighted_precision:.3f}")
    print(f"Weighted Recall:    {metrics.weighted_recall:.3f}")
    print(f"Weighted F1:        {metrics.weighted_f1:.3f}")
    print("Confusion Matrix:")
    print(confusion_matrix(y_true, y_pred, labels=list(range(len(class_names)))))
    print("Classification Report:")
    print(classification_report(
        y_true,
        y_pred,
        labels=list(range(len(class_names))),
        target_names=class_names,
        zero_division=cast(Any, 0),
    ))
    return metrics


def format_comparison_table(metrics_by_model: dict[str, ModelMetrics]) -> str:
    """Return a concise model-comparison table."""
    header = "Model                    Accuracy  Macro F1  Weighted F1"
    rows = [header, "-" * len(header)]
    for name, metrics in metrics_by_model.items():
        rows.append(
            f"{name:<24} {metrics.accuracy:>8.3f}  {metrics.macro_f1:>8.3f}  "
            f"{metrics.weighted_f1:>11.3f}"
        )
    return "\n".join(rows)
