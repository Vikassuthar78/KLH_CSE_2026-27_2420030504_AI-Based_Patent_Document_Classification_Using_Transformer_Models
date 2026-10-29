"""Side-by-side comparison of experiment runs."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def compare_runs(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare multiple experiment runs across key metrics.

    Args:
        runs: List of experiment run dicts containing 'run_id', 'type', 'metrics'

    Returns:
        Structured comparison table dictionary.
    """
    if not runs:
        return {"columns": [], "rows": []}

    metric_keys = [
        "macro_f1",
        "micro_f1",
        "macro_precision",
        "macro_recall",
        "accuracy",
        "hamming_loss",
        "training_time_seconds",
        "inference_latency_ms",
    ]

    columns = ["Metric"] + [r.get("run_id", f"Run {i+1}") for i, r in enumerate(runs)]
    rows = []

    for key in metric_keys:
        row = {"metric": key}
        for r in runs:
            run_id = r.get("run_id", "")
            metrics = r.get("metrics", {})
            val = metrics.get(key)
            row[run_id] = round(val, 4) if isinstance(val, (int, float)) else "N/A"
        rows.append(row)

    return {
        "columns": columns,
        "rows": rows,
        "run_count": len(runs),
    }

