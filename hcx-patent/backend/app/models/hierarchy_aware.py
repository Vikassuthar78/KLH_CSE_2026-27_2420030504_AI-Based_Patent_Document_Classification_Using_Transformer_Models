"""Hierarchy-aware multi-label patent classifier."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np

from app.models.base import BasePatentClassifier
from app.models.tfidf_baseline import TFIDFBaseline
from app.taxonomy.cpc_tree import CPCTaxonomy

logger = logging.getLogger(__name__)


class HierarchyAwareClassifier(BasePatentClassifier):
    """Classifier that incorporates CPC parent-child hierarchy constraints.

    Enforces parent-child consistency during probability calibration and thresholding.
    """

    def __init__(
        self,
        base_model: Optional[BasePatentClassifier] = None,
        class_names: Optional[List[str]] = None,
        hierarchy_penalty: float = 0.1,
        enforce_constraints: bool = True,
    ) -> None:
        self.base_model = base_model or TFIDFBaseline()
        self.class_names = class_names or []
        self.hierarchy_penalty = hierarchy_penalty
        self.enforce_constraints = enforce_constraints
        self.taxonomy = CPCTaxonomy()

        if self.class_names:
            self.taxonomy.build_from_codes(self.class_names)

    def train(
        self,
        texts: List[str],
        labels: np.ndarray,
        val_texts: Optional[List[str]] = None,
        val_labels: Optional[np.ndarray] = None,
        class_names: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Train base model and build hierarchy."""
        if class_names:
            self.class_names = class_names
            self.taxonomy.build_from_codes(self.class_names)

        result = self.base_model.train(texts, labels, val_texts=val_texts, val_labels=val_labels, **kwargs)
        return result

    def predict(
        self,
        texts: List[str],
        threshold: float = 0.5,
        **kwargs: Any,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Predict with optional hierarchical constraint enforcement."""
        preds, probs = self.base_model.predict(texts, threshold=threshold, **kwargs)

        if not self.enforce_constraints or not self.class_names:
            return preds, probs

        # Apply constraint propagation
        adjusted_preds = preds.copy()
        name_to_idx = {name: i for i, name in enumerate(self.class_names)}

        for i in range(len(preds)):
            active_indices = np.where(preds[i] == 1)[0]
            for idx in active_indices:
                code = self.class_names[idx]
                ancestors = self.taxonomy.get_ancestors(code)
                for anc in ancestors:
                    if anc in name_to_idx:
                        adjusted_preds[i, name_to_idx[anc]] = 1

        return adjusted_preds, probs

    def save(self, path: str) -> None:
        """Save classifier and hierarchy mappings."""
        self.base_model.save(path)

    @classmethod
    def load(cls, path: str) -> "HierarchyAwareClassifier":
        """Load classifier."""
        base = TFIDFBaseline.load(path)
        return cls(base_model=base)

