"""Base class and interface for patent classification models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np


class BasePatentClassifier(ABC):
    """Abstract base class for all patent classification models."""

    @abstractmethod
    def train(
        self,
        texts: List[str],
        labels: np.ndarray,
        val_texts: Optional[List[str]] = None,
        val_labels: Optional[np.ndarray] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Train the model on the provided texts and binary label matrix."""
        pass

    @abstractmethod
    def predict(
        self,
        texts: List[str],
        threshold: float = 0.5,
        **kwargs: Any,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Predict binary labels and class probabilities for input texts.

        Returns:
            Tuple of (binary_predictions_matrix, probability_matrix).
        """
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        """Persist model artifacts to disk."""
        pass

    @classmethod
    @abstractmethod
    def load(cls, path: str) -> "BasePatentClassifier":
        """Load model artifacts from disk."""
        pass

