"""Temporal and taxonomy drift evaluation across publication cohorts."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

from app.evaluation.metrics import compute_all_metrics

logger = logging.getLogger(__name__)


def evaluate_temporal_drift(
    df_test: pd.DataFrame,
    y_test: np.ndarray,
    y_pred: np.ndarray,
    date_col: str = "date",
    yearly_window: int = 2,
) -> Dict[str, Any]:
    """Evaluate classification performance degradation over chronological cohorts.

    Args:
        df_test: Test DataFrame with date column
        y_test: Ground truth binary matrix (N, C)
        y_pred: Predicted binary matrix (N, C)
        date_col: Name of date column
        yearly_window: Cohort window size in years

    Returns:
        Dict with performance metrics per year cohort and drift magnitude.
    """
    if date_col not in df_test.columns:
        return {"error": f"Date column '{date_col}' not found in test dataset."}

    dates = pd.to_datetime(df_test[date_col], errors="coerce")
    years = dates.dt.year

    valid_mask = ~years.isna()
    if not valid_mask.any():
        return {"error": "No valid dates found in test dataset."}

    years_valid = years[valid_mask].astype(int)
    unique_years = sorted(years_valid.unique())

    cohort_results = []
    f1_by_year = {}

    for yr in unique_years:
        idx = np.where(years == yr)[0]
        if len(idx) < 5:
            continue

        yt_cohort = y_test[idx]
        yp_cohort = y_pred[idx]

        macro_f1 = float(f1_score(yt_cohort, yp_cohort, average="macro", zero_division=0))
        micro_f1 = float(f1_score(yt_cohort, yp_cohort, average="micro", zero_division=0))

        cohort_results.append({
            "year": int(yr),
            "sample_count": len(idx),
            "macro_f1": round(macro_f1, 4),
            "micro_f1": round(micro_f1, 4),
        })
        f1_by_year[str(yr)] = round(macro_f1, 4)

    # Compute drift delta (first cohort vs last cohort)
    drift_delta = 0.0
    if len(cohort_results) >= 2:
        drift_delta = cohort_results[-1]["macro_f1"] - cohort_results[0]["macro_f1"]

    return {
        "cohorts": cohort_results,
        "f1_by_year": f1_by_year,
        "drift_delta_macro_f1": round(drift_delta, 4),
        "total_cohorts": len(cohort_results),
    }

