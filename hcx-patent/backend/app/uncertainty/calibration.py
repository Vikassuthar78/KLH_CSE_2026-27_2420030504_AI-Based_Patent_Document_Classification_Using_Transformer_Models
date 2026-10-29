"""Probability calibration assessment and reliability diagram metrics."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


def compute_calibration_curve(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
) -> Dict[str, Any]:
    """Compute reliability diagram coordinates and Expected Calibration Error (ECE).

    Args:
        y_true: Ground truth binary array or matrix
        y_prob: Predicted probability array or matrix
        n_bins: Number of equal-width bins

    Returns:
        Dict with bin centers, true fractions, counts, and ECE score.
    """
    y_t = np.asarray(y_true).ravel()
    y_p = np.asarray(y_prob).ravel()

    # Filter out any NaNs
    valid = ~(np.isnan(y_t) | np.isnan(y_p))
    y_t = y_t[valid]
    y_p = y_p[valid]

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    bin_accs = []
    bin_confs = []
    bin_counts = []
    total_samples = len(y_t)

    ece = 0.0

    for i in range(n_bins):
        low, high = bin_edges[i], bin_edges[i + 1]
        if i == n_bins - 1:
            mask = (y_p >= low) & (y_p <= high)
        else:
            mask = (y_p >= low) & (y_p < high)

        count = int(np.sum(mask))
        bin_counts.append(count)

        if count > 0:
            acc = float(np.mean(y_t[mask]))
            conf = float(np.mean(y_p[mask]))
            bin_accs.append(round(acc, 4))
            bin_confs.append(round(conf, 4))
            ece += (count / total_samples) * abs(acc - conf)
        else:
            bin_accs.append(0.0)
            bin_confs.append(round(bin_centers[i], 4))

    return {
        "bin_centers": [round(float(c), 4) for c in bin_centers],
        "bin_accuracies": bin_accs,
        "bin_confidences": bin_confs,
        "bin_counts": bin_counts,
        "expected_calibration_error": float(round(ece, 4)),
    }

