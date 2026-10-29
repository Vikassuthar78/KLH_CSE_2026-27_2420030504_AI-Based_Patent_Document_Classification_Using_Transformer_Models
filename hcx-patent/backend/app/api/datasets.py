"""Dataset discovery, profiling, validation, and preview endpoints."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.datasets.discovery import discover_datasets
from app.datasets.profiler import profile_dataset_file
from app.datasets.validator import validate_dataset
from app.schemas.dataset import ProfileRequest

router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.get("/discover")
def discover_endpoint() -> List[Dict[str, Any]]:
    """Discover dataset files in configured DATASET_ROOT."""
    settings = get_settings()
    files = discover_datasets(settings.DATASET_ROOT)
    return [
        {
            "path": f.path,
            "name": f.name,
            "size_bytes": f.size_bytes,
            "format": f.format,
            "modified_at": f.modified_at,
        }
        for f in files
    ]


@router.get("/preview")
def preview_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    file_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Return paginated preview records from dataset."""
    settings = get_settings()
    target_path = file_path
    if not target_path:
        files = discover_datasets(settings.DATASET_ROOT)
        parquets = [f.path for f in files if f.format == "parquet"]
        if not parquets:
            raise HTTPException(status_code=404, detail="No dataset files found.")
        target_path = parquets[0]

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"File not found: {target_path}")

    import pyarrow.parquet as pq

    pf = pq.ParquetFile(target_path)
    total_rows = pf.metadata.num_rows

    start_idx = (page - 1) * page_size
    # Read row group containing the rows
    table = pf.read_row_group(0)
    df = table.to_pandas()

    if start_idx >= len(df):
        records = []
    else:
        page_df = df.iloc[start_idx : start_idx + page_size]
        records = page_df.to_dict(orient="records")

    return {
        "page": page,
        "page_size": page_size,
        "total_rows": total_rows,
        "records": records,
        "columns": list(df.columns),
    }


@router.get("/stats")
def stats_endpoint() -> Dict[str, Any]:
    """Retrieve summarized dataset statistics."""
    settings = get_settings()
    files = discover_datasets(settings.DATASET_ROOT)
    parquets = [f.path for f in files if f.format == "parquet"]
    if not parquets:
        raise HTTPException(status_code=404, detail="No dataset files found.")

    import pyarrow.parquet as pq

    total_rows = 0
    for p in parquets:
        pf = pq.ParquetFile(p)
        total_rows += pf.metadata.num_rows

    # Quick profile from first file
    sample_profile = profile_dataset_file(parquets[0], max_rows=1000)

    return {
        "file_count": len(parquets),
        "total_rows": total_rows,
        "sample_profile": sample_profile,
    }


@router.post("/profile")
def profile_endpoint(req: ProfileRequest) -> Dict[str, Any]:
    """Run profiling on a specific file or default."""
    settings = get_settings()
    path = req.path
    if not path:
        files = discover_datasets(settings.DATASET_ROOT)
        parquets = [f.path for f in files if f.format == "parquet"]
        if not parquets:
            raise HTTPException(status_code=404, detail="No dataset files found.")
        path = parquets[0]

    return profile_dataset_file(path)


@router.post("/validate")
def validate_endpoint(file_path: Optional[str] = None) -> Dict[str, Any]:
    """Run data quality validation on dataset."""
    settings = get_settings()
    target = file_path
    if not target:
        files = discover_datasets(settings.DATASET_ROOT)
        parquets = [f.path for f in files if f.format == "parquet"]
        if not parquets:
            raise HTTPException(status_code=404, detail="No dataset files found.")
        target = parquets[0]

    import pyarrow.parquet as pq

    pf = pq.ParquetFile(target)
    df = pf.read_row_group(0).to_pandas().head(1000)

    issues = validate_dataset(df)
    return {
        "path": target,
        "samples_checked": len(df),
        "issues": issues,
        "is_valid": len([i for i in issues if i.get("severity") == "critical"]) == 0,
    }

