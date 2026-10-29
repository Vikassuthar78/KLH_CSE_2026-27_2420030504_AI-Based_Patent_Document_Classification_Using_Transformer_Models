"""Transformer-based patent classification model (BERT / PatentBERT architecture)."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

from app.models.base import BasePatentClassifier

logger = logging.getLogger(__name__)


class PatentTextDataset(Dataset):
    """PyTorch Dataset for tokenized patent texts and binary multi-labels."""

    def __init__(self, encodings: Dict[str, torch.Tensor], labels: Optional[torch.Tensor] = None) -> None:
        self.encodings = encodings
        self.labels = labels

    def __len__(self) -> int:
        return len(self.encodings["input_ids"])

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        item = {key: val[idx] for key, val in self.encodings.items()}
        if self.labels is not None:
            item["labels"] = self.labels[idx]
        return item


class TransformerPatentClassifier(BasePatentClassifier):
    """PyTorch / HuggingFace multi-label patent classifier with section chunking."""

    def __init__(
        self,
        model_name: str = "bert-base-uncased",
        num_labels: int = 10,
        max_length: int = 512,
        device: str = "cpu",
        learning_rate: float = 2e-5,
        batch_size: int = 16,
        epochs: int = 3,
    ) -> None:
        self.model_name = model_name
        self.num_labels = num_labels
        self.max_length = max_length
        self.device = torch.device(device if torch.cuda.is_available() and device != "cpu" else "cpu")
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs

        self.tokenizer = None
        self.model = None

    def _init_model(self) -> None:
        """Lazy initialization of tokenizer and model."""
        if self.tokenizer is None or self.model is None:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=self.num_labels,
                problem_type="multi_label_classification",
            )
            self.model.to(self.device)

    def train(
        self,
        texts: List[str],
        labels: np.ndarray,
        val_texts: Optional[List[str]] = None,
        val_labels: Optional[np.ndarray] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Train transformer classifier using BCEWithLogitsLoss."""
        t0 = time.time()
        self.num_labels = labels.shape[1]
        self._init_model()

        encodings = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        tensor_labels = torch.tensor(labels, dtype=torch.float32)
        dataset = PatentTextDataset(encodings, tensor_labels)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        optimizer = torch.optim.AdamW(self.model.parameters(), lr=self.learning_rate)
        criterion = nn.BCEWithLogitsLoss()

        self.model.train()
        epoch_losses = []

        for epoch in range(self.epochs):
            total_loss = 0.0
            for batch in loader:
                optimizer.zero_grad()
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                targets = batch["labels"].to(self.device)

                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                loss = criterion(outputs.logits, targets)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            avg_loss = total_loss / max(1, len(loader))
            epoch_losses.append(avg_loss)
            logger.info("Epoch %d/%d - Loss: %.4f", epoch + 1, self.epochs, avg_loss)

        train_time = time.time() - t0
        return {
            "training_time_seconds": train_time,
            "epoch_losses": epoch_losses,
            "device": str(self.device),
        }

    def predict(
        self,
        texts: List[str],
        threshold: float = 0.5,
        **kwargs: Any,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Inference with sigmoid multi-label probabilities."""
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model is not initialized or trained.")

        self.model.eval()
        encodings = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        dataset = PatentTextDataset(encodings)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)

        all_probs = []
        with torch.no_grad():
            for batch in loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                logits = self.model(input_ids=input_ids, attention_mask=attention_mask).logits
                probs = torch.sigmoid(logits).cpu().numpy()
                all_probs.append(probs)

        probabilities = np.vstack(all_probs)
        predictions = (probabilities >= threshold).astype(int)
        return predictions, probabilities

    def save(self, path: str) -> None:
        """Save model and tokenizer weights."""
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        if self.model is not None:
            self.model.save_pretrained(str(p))
        if self.tokenizer is not None:
            self.tokenizer.save_pretrained(str(p))

    @classmethod
    def load(cls, path: str, device: str = "cpu") -> "TransformerPatentClassifier":
        """Load from directory."""
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        p = Path(path)
        tokenizer = AutoTokenizer.from_pretrained(str(p))
        model = AutoModelForSequenceClassification.from_pretrained(str(p))
        instance = cls(model_name=str(p), device=device)
        instance.tokenizer = tokenizer
        instance.model = model
        instance.model.to(instance.device)
        return instance

