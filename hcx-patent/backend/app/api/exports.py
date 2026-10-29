"""Data, prediction, and metric exports in CSV/JSON formats."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response

from app.config import get_settings

router = APIRouter(prefix="/exports", tags=["Exports"])


@router.get("/{run_id}/csv")
def export_predictions_csv(run_id: str):
    """Download predictions CSV for a specific run."""
    settings = get_settings()
    pred_file = Path(settings.ARTIFACTS_DIR) / "predictions" / f"{run_id}_predictions.csv"
    if not pred_file.exists():
        raise HTTPException(status_code=404, detail="Predictions CSV file not found.")

    return FileResponse(
        str(pred_file),
        media_type="text/csv",
        filename=f"{run_id}_predictions.csv",
    )


@router.get("/{run_id}/json")
def export_metrics_json(run_id: str):
    """Download metrics JSON for a specific run."""
    settings = get_settings()
    metrics_file = Path(settings.ARTIFACTS_DIR) / "metrics" / f"{run_id}_metrics.json"
    if not metrics_file.exists():
        raise HTTPException(status_code=404, detail="Metrics JSON file not found.")

    return FileResponse(
        str(metrics_file),
        media_type="application/json",
        filename=f"{run_id}_metrics.json",
    )

