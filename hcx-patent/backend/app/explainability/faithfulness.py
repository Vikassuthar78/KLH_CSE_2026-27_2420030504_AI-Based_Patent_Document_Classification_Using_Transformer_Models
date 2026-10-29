"""Faithfulness metrics: Comprehensiveness and Sufficiency for model attributions."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List

import numpy as np

logger = logging.getLogger(__name__)


def compute_faithfulness_metrics(
    text: str,
    tokens: List[str],
    scores: List[float],
    predict_fn: Callable[[List[str]], np.ndarray],
    target_class_idx: int,
    top_k_pct: float = 0.2,
) -> Dict[str, float]:
    """Evaluate Comprehensiveness and Sufficiency of explanations.

    Comprehensiveness: Measure how much prediction confidence drops when the most important
    features are removed. High comprehensiveness indicates that removed features were genuinely crucial.
    Comprehensiveness = P(original) - P(without_important_tokens)

    Sufficiency: Measure whether keeping ONLY the most important features retains the prediction confidence.
    Sufficiency = P(original) - P(only_important_tokens)

    Returns:
        Dict containing comprehensiveness, sufficiency, and baseline probability.
    """
    orig_prob = float(predict_fn([text])[0, target_class_idx])

    # Rank tokens by attribution score
    sorted_pairs = sorted(zip(tokens, scores), key=lambda x: abs(x[1]), reverse=True)
    num_to_select = max(1, int(len(sorted_pairs) * top_k_pct))
    top_tokens = set([p[0] for p in sorted_pairs[:num_to_select]])

    # Text without important tokens
    words = text.split()
    text_without = " ".join([w for w in words if w.lower() not in top_tokens])
    if not text_without.strip():
        text_without = "empty"

    prob_without = float(predict_fn([text_without])[0, target_class_idx])
    comprehensiveness = orig_prob - prob_without

    # Text with ONLY important tokens
    text_only = " ".join([w for w in words if w.lower() in top_tokens])
    if not text_only.strip():
        text_only = "empty"

    prob_only = float(predict_fn([text_only])[0, target_class_idx])
    sufficiency = orig_prob - prob_only

    return {
        "original_probability": round(orig_prob, 4),
        "comprehensiveness": round(float(comprehensiveness), 4),
        "sufficiency": round(float(sufficiency), 4),
        "tokens_evaluated": len(sorted_pairs),
        "top_tokens_count": num_to_select,
    }

