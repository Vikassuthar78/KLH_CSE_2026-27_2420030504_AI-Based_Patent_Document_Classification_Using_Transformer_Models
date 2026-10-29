"""Text preprocessing and tokenization utilities."""

from __future__ import annotations

import logging
import re
from typing import List, Optional, Set

import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Basic text cleaning for patent text.

    Args:
        text: Raw patent text.

    Returns:
        Cleaned text.
    """
    if not isinstance(text, str):
        return ""
    # Normalise whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Remove very long sequences of digits (patent reference numbers)
    text = re.sub(r"\b\d{8,}\b", "", text)
    # Remove excessive punctuation
    text = re.sub(r"[^\w\s.,;:!?()\-/']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_cpc_codes(cpc_string: str) -> List[str]:
    """Parse a comma-separated CPC code string into a list.

    Args:
        cpc_string: e.g. "A01H,C11D,Y10S"

    Returns:
        List of cleaned CPC codes.
    """
    if not isinstance(cpc_string, str) or not cpc_string.strip():
        return []
    return [c.strip() for c in cpc_string.split(",") if c.strip()]


def build_label_encoder(
    df: pd.DataFrame,
    cpc_col: str = "cpc_ids",
    min_samples: int = 1,
    top_n: Optional[int] = None,
) -> tuple[MultiLabelBinarizer, List[str]]:
    """Build a MultiLabelBinarizer from the dataset.

    Args:
        df: DataFrame with CPC column.
        cpc_col: Column name containing CPC codes.
        min_samples: Minimum sample count to include a label.
        top_n: Keep only the top-N most frequent labels.

    Returns:
        Tuple of (fitted MLB, list of selected classes).
    """
    all_labels: List[List[str]] = []
    for val in df[cpc_col].dropna():
        codes = parse_cpc_codes(str(val))
        all_labels.append(codes)

    # Count label frequencies
    from collections import Counter
    freq: Counter = Counter()
    for labels in all_labels:
        freq.update(labels)

    # Filter by min_samples
    eligible = {code for code, count in freq.items() if count >= min_samples}

    # Apply top_n
    if top_n is not None:
        top_codes = [code for code, _ in freq.most_common(top_n)]
        eligible = eligible & set(top_codes)

    selected_classes = sorted(eligible)
    logger.info(
        "Label encoder: %d classes selected (min_samples=%d, top_n=%s)",
        len(selected_classes),
        min_samples,
        top_n,
    )

    mlb = MultiLabelBinarizer(classes=selected_classes)
    mlb.fit([selected_classes])  # fit on the full class list

    return mlb, selected_classes


def binarize_labels(
    df: pd.DataFrame,
    mlb: MultiLabelBinarizer,
    cpc_col: str = "cpc_ids",
) -> np.ndarray:
    """Convert CPC codes column to binary matrix.

    Args:
        df: DataFrame with CPC column.
        mlb: Fitted MultiLabelBinarizer.
        cpc_col: Column name.

    Returns:
        Binary label matrix of shape (n_samples, n_classes).
    """
    all_labels = [parse_cpc_codes(str(val)) for val in df[cpc_col].fillna("")]
    return mlb.transform(all_labels)


def preprocess_dataframe(
    df: pd.DataFrame,
    text_col: str = "text",
    clean: bool = True,
    max_length: Optional[int] = None,
) -> pd.DataFrame:
    """Preprocess a DataFrame for model consumption.

    Args:
        df: Raw DataFrame.
        text_col: Text column to clean.
        clean: Whether to apply text cleaning.
        max_length: Truncate text to this character length.

    Returns:
        Preprocessed DataFrame (copy).
    """
    result = df.copy()

    if clean and text_col in result.columns:
        result[text_col] = result[text_col].apply(clean_text)

    if max_length and text_col in result.columns:
        result[text_col] = result[text_col].str[:max_length]

    # Drop rows with empty text
    if text_col in result.columns:
        result = result[result[text_col].str.len() > 0].reset_index(drop=True)

    return result
