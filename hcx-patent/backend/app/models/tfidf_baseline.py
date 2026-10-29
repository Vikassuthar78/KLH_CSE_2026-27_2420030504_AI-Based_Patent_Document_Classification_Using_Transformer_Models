"""Classical TF-IDF + OneVsRest Logistic Regression baseline model."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier

from app.models.base import BasePatentClassifier

logger = logging.getLogger(__name__)


class TFIDFBaseline(BasePatentClassifier):
    """TF-IDF vectorization with One-vs-Rest Logistic Regression for multi-label classification."""

    def __init__(
        self,
        max_features: int = 50000,
        ngram_range: Tuple[int, int] = (1, 2),
        C: float = 1.0,
        max_iter: int = 1000,
        sublinear_tf: bool = True,
        min_df: int = 1,
        random_seed: int = 42,
    ) -> None:
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.C = C
        self.max_iter = max_iter
        self.sublinear_tf = sublinear_tf
        self.min_df = min_df
        self.random_seed = random_seed

        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            sublinear_tf=self.sublinear_tf,
            strip_accents="unicode",
            min_df=self.min_df,
        )
        self.classifier: Optional[OneVsRestClassifier] = None
        self.classes_: Optional[np.ndarray] = None
        self.n_classes_: int = 0

    def _sanitize_texts(self, texts: List[str]) -> List[str]:
        """Ensure texts are non-empty strings."""
        return [str(t) if t and str(t).strip() else "empty_patent_document" for t in texts]

    def train(
        self,
        texts: List[str],
        labels: np.ndarray,
        val_texts: Optional[List[str]] = None,
        val_labels: Optional[np.ndarray] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Fit vectorizer and OneVsRest Logistic Regression classifier."""
        t0 = time.time()
        clean_texts = self._sanitize_texts(texts)
        y = np.asarray(labels)

        if y.ndim == 1:
            y = y.reshape(-1, 1)

        self.n_classes_ = y.shape[1]

        logger.info("Fitting TF-IDF vectorizer on %d documents...", len(clean_texts))
        X = self.vectorizer.fit_transform(clean_texts)

        base_lr = LogisticRegression(
            C=self.C,
            max_iter=self.max_iter,
            solver="liblinear" if self.n_classes_ < 10 else "saga",
            random_state=self.random_seed,
        )
        self.classifier = OneVsRestClassifier(base_lr, n_jobs=-1)

        logger.info("Fitting OneVsRestClassifier for %d classes...", self.n_classes_)
        self.classifier.fit(X, y)
        train_time = time.time() - t0

        return {
            "training_time_seconds": train_time,
            "vocab_size": len(self.vectorizer.vocabulary_),
            "n_classes": self.n_classes_,
        }

    def predict(
        self,
        texts: List[str],
        threshold: float = 0.5,
        **kwargs: Any,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Predict binary classification and calibrated probability matrix."""
        if self.classifier is None:
            raise RuntimeError("Model has not been trained yet.")

        clean_texts = self._sanitize_texts(texts)
        X = self.vectorizer.transform(clean_texts)

        # Probabilities
        n_samples = len(clean_texts)
        probabilities = np.zeros((n_samples, self.n_classes_), dtype=float)

        for i, estimator in enumerate(self.classifier.estimators_):
            if hasattr(estimator, "predict_proba"):
                probs = estimator.predict_proba(X)
                if probs.shape[1] == 2:
                    probabilities[:, i] = probs[:, 1]
                elif probs.shape[1] == 1:
                    probabilities[:, i] = probs[:, 0]
            elif hasattr(estimator, "decision_function"):
                decision = estimator.decision_function(X)
                probabilities[:, i] = 1.0 / (1.0 + np.exp(-decision))

        predictions = (probabilities >= threshold).astype(int)
        return predictions, probabilities

    def save(self, path: str) -> None:
        """Save model artifacts to a file or directory."""
        p = Path(path)
        if p.is_dir() or not p.suffix:
            p.mkdir(parents=True, exist_ok=True)
            save_file = p / "model.joblib"
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            save_file = p

        data = {
            "vectorizer": self.vectorizer,
            "classifier": self.classifier,
            "n_classes_": self.n_classes_,
            "config": {
                "max_features": self.max_features,
                "ngram_range": self.ngram_range,
                "C": self.C,
                "max_iter": self.max_iter,
                "sublinear_tf": self.sublinear_tf,
                "min_df": self.min_df,
                "random_seed": self.random_seed,
            },
        }
        joblib.dump(data, str(save_file))
        logger.info("Saved TFIDFBaseline model to %s", save_file)

    @classmethod
    def load(cls, path: str) -> "TFIDFBaseline":
        """Load model from file or directory."""
        p = Path(path)
        if p.is_dir():
            load_file = p / "model.joblib"
        else:
            load_file = p

        if not load_file.exists():
            raise FileNotFoundError(f"Model file not found: {load_file}")

        data = joblib.load(str(load_file))
        cfg = data.get("config", {})
        instance = cls(**cfg)
        instance.vectorizer = data["vectorizer"]
        instance.classifier = data["classifier"]
        instance.n_classes_ = data.get("n_classes_", 0)
        return instance

