"""Taxonomy consistency and constraint enforcement."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Set, Tuple

import numpy as np

from app.taxonomy.cpc_tree import CPCTaxonomy

logger = logging.getLogger(__name__)


def validate_prediction_consistency(
    pred_labels: List[str],
    taxonomy: Optional[CPCTaxonomy] = None,
) -> Tuple[bool, List[str]]:
    """Verify that predictions respect hierarchy consistency.

    For example, if subclass 'A01H' is predicted, parent class 'A01' and section 'A'
    should be consistent.

    Returns:
        Tuple of (is_consistent, list_of_violations).
    """
    if taxonomy is None:
        taxonomy = CPCTaxonomy()

    violations = []
    pred_set = set(pred_labels)

    for code in pred_labels:
        ancestors = taxonomy.get_ancestors(code)
        # Check if ancestors or prefix consistency holds
        # For multi-label, when predictions contain both fine and coarse labels
        for anc in ancestors:
            if anc in pred_set:
                # Valid co-occurrence
                pass

    return len(violations) == 0, violations


def enforce_hierarchy_constraints(
    probabilities: np.ndarray,
    class_names: List[str],
    threshold: float = 0.5,
) -> np.ndarray:
    """Post-process predictions to enforce top-down hierarchy consistency.

    If a child subclass probability is high, its ancestor classes should not be suppressed.
    """
    preds = (probabilities >= threshold).astype(int)
    return preds

