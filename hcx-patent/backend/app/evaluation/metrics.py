"""Comprehensive evaluation metrics for multi-label patent classification."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Union

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    hamming_loss,
    precision_score,
    recall_score,
)

logger = logging.getLogger(__name__)


def compute_all_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
    class_names: Optional[List[str]] = None,
    training_time_seconds: float = 0.0,
    inference_latency_ms: float = 0.0,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Compute complete suite of multi-label evaluation metrics.

    Args:
        y_true: Binary ground truth matrix (N, C)
        y_pred: Binary predicted matrix (N, C)
        y_prob: Predicted probability matrix (N, C), optional
        class_names: Names for each class column
        training_time_seconds: Training duration
        inference_latency_ms: Inference latency per sample

    Returns:
        Dict containing global and per-class metrics.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if y_true.ndim == 1:
        y_true = y_true.reshape(-1, 1)
    if y_pred.ndim == 1:
        y_pred = y_pred.reshape(-1, 1)

    # Subset accuracy (exact match ratio)
    acc = float(accuracy_score(y_true, y_pred))

    # Macro metrics
    macro_p = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    macro_r = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))

    # Micro metrics
    micro_p = float(precision_score(y_true, y_pred, average="micro", zero_division=0))
    micro_r = float(recall_score(y_true, y_pred, average="micro", zero_division=0))
    micro_f1 = float(f1_score(y_true, y_pred, average="micro", zero_division=0))

    # Hamming loss
    h_loss = float(hamming_loss(y_true, y_pred))

    metrics: Dict[str, Any] = {
        "accuracy": acc,
        "macro_precision": macro_p,
        "macro_recall": macro_r,
        "macro_f1": macro_f1,
        "micro_precision": micro_p,
        "micro_recall": micro_r,
        "micro_f1": micro_f1,
        "hamming_loss": h_loss,
        "training_time_seconds": float(training_time_seconds),
        "inference_latency_ms": float(inference_latency_ms),
    }

    # Per-class breakdown
    n_classes = y_true.shape[1]
    per_class: Dict[str, Dict[str, float]] = {}

    for i in range(n_classes):
        name = class_names[i] if class_names and i < len(class_names) else f"class_{i}"
        yt_col = y_true[:, i]
        yp_col = y_pred[:, i]
        support = int(np.sum(yt_col))

        per_class[name] = {
            "precision": float(precision_score(yt_col, yp_col, zero_division=0)),
            "recall": float(recall_score(yt_col, yp_col, zero_division=0)),
            "f1": float(f1_score(yt_col, yp_col, zero_division=0)),
            "support": support,
        }

    metrics["per_class"] = per_class
    return metrics

