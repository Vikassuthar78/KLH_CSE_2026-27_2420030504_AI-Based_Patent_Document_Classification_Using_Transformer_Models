"""Dataset splitting with strict data leakage prevention and reproducible manifests."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


def create_splits(
    df: pd.DataFrame,
    strategy: str = "random",
    train_ratio: float = 0.7,
    val_ratio: float = 0.1,
    cal_ratio: float = 0.1,
    test_ratio: float = 0.1,
    random_seed: int = 42,
    date_col: str = "date",
    id_col: str = "id",
    temporal_cutoff: Optional[str] = None,
    temporal_cutoff_year: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, pd.DataFrame]:
    """Create train, validation, calibration, and test splits.

    Ensures no document ID leakage across splits.

    Args:
        df: Input patent DataFrame.
        strategy: 'random' or 'temporal'.
        train_ratio: Ratio for training set.
        val_ratio: Ratio for validation set.
        cal_ratio: Ratio for conformal calibration set.
        test_ratio: Ratio for held-out test set.
        random_seed: Seed for reproducibility.
        date_col: Column containing publication/filing dates.
        id_col: Column containing unique patent identifier.
        temporal_cutoff: Date cutoff string (e.g. '2012-01-01') for temporal splits.
        temporal_cutoff_year: Year cutoff int (e.g. 2012).

    Returns:
        Dict mapping split names ('train', 'val', 'cal', 'test') to DataFrames.
    """
    total = len(df)
    if total == 0:
        empty = pd.DataFrame(columns=df.columns)
        return {"train": empty, "val": empty, "cal": empty, "test": empty}

    # Dedup by id if id_col present to prevent document leakage
    if id_col in df.columns:
        df_clean = df.drop_duplicates(subset=[id_col]).reset_index(drop=True)
    else:
        df_clean = df.copy().reset_index(drop=True)

    if strategy == "temporal" and date_col in df_clean.columns:
        dates = pd.to_datetime(df_clean[date_col], errors="coerce")

        if temporal_cutoff is not None:
            cutoff = pd.to_datetime(temporal_cutoff)
            is_train = dates < cutoff
        elif temporal_cutoff_year is not None:
            is_train = dates.dt.year < temporal_cutoff_year
        else:
            # Default cutoff at the 70th percentile of dates
            cutoff = dates.quantile(train_ratio)
            is_train = dates <= cutoff

        train_pool = df_clean[is_train].copy().reset_index(drop=True)
        eval_pool = df_clean[~is_train].copy().reset_index(drop=True)

        if len(eval_pool) < 3:
            # Fallback if evaluation pool too small
            logger.warning("Temporal evaluation pool too small; falling back to random split.")
            return _random_split(df_clean, train_ratio, val_ratio, cal_ratio, test_ratio, random_seed)

        # Split train pool into train (e.g. 90%) and val (10%)
        t_val_ratio = val_ratio / (train_ratio + val_ratio) if (train_ratio + val_ratio) > 0 else 0.1
        train_df, val_df = train_test_split(train_pool, test_size=t_val_ratio, random_state=random_seed)

        # Split eval pool into calibration and test
        eval_cal_ratio = cal_ratio / (cal_ratio + test_ratio) if (cal_ratio + test_ratio) > 0 else 0.5
        cal_df, test_df = train_test_split(eval_pool, test_size=(1.0 - eval_cal_ratio), random_state=random_seed)

        return {
            "train": train_df.reset_index(drop=True),
            "val": val_df.reset_index(drop=True),
            "cal": cal_df.reset_index(drop=True),
            "test": test_df.reset_index(drop=True),
        }
    else:
        return _random_split(df_clean, train_ratio, val_ratio, cal_ratio, test_ratio, random_seed)


def _random_split(
    df: pd.DataFrame,
    train_ratio: float,
    val_ratio: float,
    cal_ratio: float,
    test_ratio: float,
    random_seed: int,
) -> Dict[str, pd.DataFrame]:
    """Helper for random partition."""
    # Normalize ratios
    total_ratio = train_ratio + val_ratio + cal_ratio + test_ratio
    r_train = train_ratio / total_ratio
    r_val = val_ratio / total_ratio
    r_cal = cal_ratio / total_ratio
    r_test = test_ratio / total_ratio

    n = len(df)
    indices = np.random.RandomState(random_seed).permutation(n)

    n_train = int(np.round(n * r_train))
    n_val = int(np.round(n * r_val))
    n_cal = int(np.round(n * r_cal))

    # Ensure train gets at least 1 if n > 0
    n_train = max(1, min(n - 3, n_train)) if n >= 4 else max(1, n - 1)

    train_idx = indices[:n_train]
    val_idx = indices[n_train : n_train + n_val]
    cal_idx = indices[n_train + n_val : n_train + n_val + n_cal]
    test_idx = indices[n_train + n_val + n_cal :]

    return {
        "train": df.iloc[train_idx].reset_index(drop=True),
        "val": df.iloc[val_idx].reset_index(drop=True),
        "cal": df.iloc[cal_idx].reset_index(drop=True),
        "test": df.iloc[test_idx].reset_index(drop=True),
    }

