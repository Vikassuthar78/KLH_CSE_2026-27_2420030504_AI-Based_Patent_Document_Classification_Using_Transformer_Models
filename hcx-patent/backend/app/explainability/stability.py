"""Explanation stability evaluation across seeds and minor text perturbations."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List

import numpy as np
from scipy.stats import spearmanr

logger = logging.getLogger(__name__)


def compute_explanation_stability(
    text: str,
    explain_fn: Callable[[str], List[float]],
    num_perturbations: int = 5,
) -> Dict[str, float]:
    """Measure explanation stability under minor input perturbations.

    Computes rank correlation between explanations of original and slightly perturbed inputs.
    """
    orig_scores = np.asarray(explain_fn(text))
    words = text.split()

    if len(words) < 5:
        return {"stability_score": 1.0, "mean_rank_correlation": 1.0}

    correlations = []
    for _ in range(num_perturbations):
        # Drop 1 random non-essential word
        drop_idx = np.random.randint(0, len(words))
        perturbed_text = " ".join([w for i, w in enumerate(words) if i != drop_idx])

        perturbed_scores = np.asarray(explain_fn(perturbed_text))
        min_len = min(len(orig_scores), len(perturbed_scores))
        if min_len > 1:
            corr, _ = spearmanr(orig_scores[:min_len], perturbed_scores[:min_len])
            if not np.isnan(corr):
                correlations.append(corr)

    mean_corr = float(np.mean(correlations)) if correlations else 1.0
    return {
        "mean_rank_correlation": round(mean_corr, 4),
        "stability_score": round(max(0.0, mean_corr), 4),
        "perturbations_tested": len(correlations),
    }

