"""Split conformal prediction with distribution-free coverage guarantees."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union

import numpy as np

logger = logging.getLogger(__name__)


class SplitConformalPredictor:
    """Split Conformal Predictor for classification tasks.

    Provides finite-sample coverage guarantees under exchangeability.

    Args:
        target_coverage: Desired marginal coverage 1 - alpha (e.g. 0.90 for 90%).
    """

    def __init__(self, target_coverage: float = 0.90) -> None:
        self.target_coverage = float(target_coverage)
        self.alpha = 1.0 - self.target_coverage
        self.q_hat: Optional[float] = None
        self.is_calibrated: bool = False
        self.cal_size: int = 0

    def calibrate(
        self,
        cal_probs: np.ndarray,
        cal_labels: np.ndarray,
    ) -> float:
        """Calibrate the conformal threshold on held-out calibration data.

        Args:
            cal_probs: Model predicted probabilities (N_cal, C)
            cal_labels: Ground truth binary matrix (N_cal, C) or class indices (N_cal,)

        Returns:
            The empirical conformal quantile threshold q_hat.
        """
        cal_probs = np.asarray(cal_probs, dtype=float)
        cal_labels = np.asarray(cal_labels)

        n = len(cal_probs)
        self.cal_size = n
        if n == 0:
            raise ValueError("Calibration set cannot be empty.")

        # Compute nonconformity scores for true labels
        scores = []
        if cal_labels.ndim == 2:
            # Multi-label or one-hot
            for i in range(n):
                true_classes = np.where(cal_labels[i] == 1)[0]
                if len(true_classes) == 0:
                    continue
                # For each true class, nonconformity score is 1 - p(y)
                for c in true_classes:
                    scores.append(1.0 - cal_probs[i, c])
        else:
            # 1D class indices
            for i in range(n):
                c = int(cal_labels[i])
                scores.append(1.0 - cal_probs[i, c])

        scores = np.array(scores)
        if len(scores) == 0:
            self.q_hat = 1.0
            self.is_calibrated = True
            return self.q_hat

        # Quantile level: ceil((N + 1) * (1 - alpha)) / N
        N = len(scores)
        quantile_level = min(1.0, np.ceil((N + 1) * (1.0 - self.alpha)) / N)
        self.q_hat = float(np.quantile(scores, quantile_level, method="higher" if hasattr(np, 'quantile') else "linear"))
        self.is_calibrated = True

        logger.info(
            "Conformal predictor calibrated: n=%d, alpha=%.3f, q_hat=%.4f (min score prob: %.4f)",
            N,
            self.alpha,
            self.q_hat,
            1.0 - self.q_hat,
        )
        return self.q_hat

    def predict(
        self,
        test_probs: np.ndarray,
    ) -> List[List[int]]:
        """Form prediction sets for each test sample.

        Args:
            test_probs: Predicted probabilities (N_test, C)

        Returns:
            List of prediction sets (list of class indices).
        """
        if not self.is_calibrated or self.q_hat is None:
            raise RuntimeError("Predictor must be calibrated before calling predict().")

        test_probs = np.asarray(test_probs, dtype=float)
        pred_sets: List[List[int]] = []

        prob_threshold = 1.0 - self.q_hat

        for i in range(len(test_probs)):
            probs_i = test_probs[i]
            # Classes with prob >= 1 - q_hat
            included = np.where(probs_i >= prob_threshold)[0].tolist()

            # If empty, include top-1 candidate to guarantee non-empty set
            if len(included) == 0:
                included = [int(np.argmax(probs_i))]

            pred_sets.append(included)

        return pred_sets

    def evaluate_coverage(
        self,
        pred_sets: List[List[int]],
        true_labels: np.ndarray,
    ) -> Dict[str, Any]:
        """Empirically evaluate conformal prediction coverage and efficiency.

        Args:
            pred_sets: Prediction sets from predict()
            true_labels: Binary matrix or 1D class indices

        Returns:
            Dict containing empirical coverage and average set size.
        """
        true_labels = np.asarray(true_labels)
        n = len(pred_sets)
        covered_count = 0
        set_sizes = [len(ps) for ps in pred_sets]

        for i in range(n):
            ps_set = set(pred_sets[i])
            if true_labels.ndim == 2:
                true_classes = set(np.where(true_labels[i] == 1)[0])
                if len(true_classes) == 0:
                    covered_count += 1
                elif len(true_classes & ps_set) > 0:
                    covered_count += 1
            else:
                if int(true_labels[i]) in ps_set:
                    covered_count += 1

        empirical_coverage = covered_count / n if n > 0 else 0.0
        avg_set_size = float(np.mean(set_sizes)) if set_sizes else 0.0

        return {
            "target_coverage": self.target_coverage,
            "empirical_coverage": float(empirical_coverage),
            "avg_set_size": float(avg_set_size),
            "min_set_size": int(np.min(set_sizes)) if set_sizes else 0,
            "max_set_size": int(np.max(set_sizes)) if set_sizes else 0,
            "q_hat": float(self.q_hat) if self.q_hat is not None else 0.0,
            "cal_size": self.cal_size,
        }

