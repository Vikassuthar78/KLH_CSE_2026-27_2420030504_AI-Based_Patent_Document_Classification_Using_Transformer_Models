"""Dataset profiling – statistics, distributions, quality metrics."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.schemas.dataset import ColumnInfo, DatasetProfileResponse

logger = logging.getLogger(__name__)


def compute_file_hash(path: str, algorithm: str = "sha256") -> str:
    """Compute hash of a file for change detection.

    Args:
        path: Path to the file.
        algorithm: Hash algorithm name.

    Returns:
        Hex-digest string.
    """
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def load_dataframe(path: str, nrows: Optional[int] = None) -> pd.DataFrame:
    """Load a dataset file into a DataFrame.

    Args:
        path: File path (parquet, csv, json, jsonl).
        nrows: Optional row limit.

    Returns:
        Loaded DataFrame.
    """
    p = Path(path)
    ext = p.suffix.lower()

    if ext == ".parquet":
        df = pd.read_parquet(path)
        if nrows is not None:
            df = df.head(nrows)
    elif ext in (".csv", ".tsv"):
        sep = "\t" if ext == ".tsv" else ","
        df = pd.read_csv(path, sep=sep, nrows=nrows)
    elif ext == ".json":
        df = pd.read_json(path)
        if nrows is not None:
            df = df.head(nrows)
    elif ext == ".jsonl":
        df = pd.read_json(path, lines=True, nrows=nrows)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return df


def load_all_parquets(paths: List[str], nrows: Optional[int] = None) -> pd.DataFrame:
    """Concatenate multiple parquet files into one DataFrame.

    Args:
        paths: List of parquet file paths.
        nrows: Optional total row limit.

    Returns:
        Combined DataFrame.
    """
    frames: List[pd.DataFrame] = []
    total = 0
    for p in sorted(paths):
        df = pd.read_parquet(p)
        if nrows is not None:
            remaining = nrows - total
            if remaining <= 0:
                break
            df = df.head(remaining)
            total += len(df)
        frames.append(df)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def profile_column(series: pd.Series) -> ColumnInfo:
    """Compute profiling statistics for a single column.

    Args:
        series: Pandas Series.

    Returns:
        ``ColumnInfo`` with statistics.
    """
    null_count = int(series.isna().sum())
    total = len(series)
    null_pct = round(null_count / total * 100, 2) if total > 0 else 0.0
    unique_count = int(series.nunique())

    min_val = None
    max_val = None
    mean_val = None

    if pd.api.types.is_numeric_dtype(series):
        non_null = series.dropna()
        if len(non_null) > 0:
            min_val = float(non_null.min())
            max_val = float(non_null.max())
            mean_val = float(non_null.mean())
    elif pd.api.types.is_string_dtype(series):
        non_null = series.dropna()
        if len(non_null) > 0:
            lengths = non_null.str.len()
            min_val = int(lengths.min())
            max_val = int(lengths.max())
            mean_val = float(lengths.mean())

    # Sample values (up to 5)
    sample_values = series.dropna().head(5).tolist()

    return ColumnInfo(
        name=series.name,
        dtype=str(series.dtype),
        null_count=null_count,
        null_pct=null_pct,
        unique_count=unique_count,
        min_val=min_val,
        max_val=max_val,
        mean_val=mean_val,
        sample_values=sample_values,
    )


def compute_cpc_distribution(df: pd.DataFrame, cpc_col: str = "cpc_ids") -> Dict[str, int]:
    """Compute frequency of each CPC code in the dataset.

    Args:
        df: DataFrame with CPC column.
        cpc_col: Name of the CPC column.

    Returns:
        Dict mapping CPC code to count, sorted descending.
    """
    if cpc_col not in df.columns:
        return {}

    all_codes: List[str] = []
    for val in df[cpc_col].dropna():
        codes = [c.strip() for c in str(val).split(",") if c.strip()]
        all_codes.extend(codes)

    code_series = pd.Series(all_codes)
    counts = code_series.value_counts().to_dict()
    # Sort descending
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def compute_date_distribution(df: pd.DataFrame, date_col: str = "date") -> Dict[str, Any]:
    """Compute date range and yearly distribution.

    Args:
        df: DataFrame.
        date_col: Name of the date column.

    Returns:
        Dict with date statistics.
    """
    if date_col not in df.columns:
        return {}

    dates = pd.to_datetime(df[date_col], errors="coerce")
    valid_dates = dates.dropna()

    if len(valid_dates) == 0:
        return {"min_date": None, "max_date": None, "yearly_counts": {}}

    yearly = valid_dates.dt.year.value_counts().sort_index()

    return {
        "min_date": str(valid_dates.min().date()),
        "max_date": str(valid_dates.max().date()),
        "total_valid": int(len(valid_dates)),
        "total_invalid": int(len(dates) - len(valid_dates)),
        "yearly_counts": {str(k): int(v) for k, v in yearly.items()},
    }


def compute_text_length_stats(df: pd.DataFrame, text_col: str = "text") -> Dict[str, float]:
    """Compute text length statistics.

    Args:
        df: DataFrame.
        text_col: Name of the text column.

    Returns:
        Dict with text length stats.
    """
    if text_col not in df.columns:
        return {}

    lengths = df[text_col].dropna().str.len()
    if len(lengths) == 0:
        return {}

    return {
        "min_length": int(lengths.min()),
        "max_length": int(lengths.max()),
        "mean_length": round(float(lengths.mean()), 1),
        "median_length": round(float(lengths.median()), 1),
        "std_length": round(float(lengths.std()), 1),
        "p25_length": round(float(lengths.quantile(0.25)), 1),
        "p75_length": round(float(lengths.quantile(0.75)), 1),
        "p95_length": round(float(lengths.quantile(0.95)), 1),
    }


def compute_labels_per_sample(df: pd.DataFrame, cpc_col: str = "cpc_ids") -> Dict[str, float]:
    """Compute statistics on number of labels per sample.

    Args:
        df: DataFrame.
        cpc_col: CPC column name.

    Returns:
        Dict with label count statistics.
    """
    if cpc_col not in df.columns:
        return {}

    label_counts = df[cpc_col].dropna().apply(
        lambda x: len([c for c in str(x).split(",") if c.strip()])
    )

    if len(label_counts) == 0:
        return {}

    return {
        "min_labels": int(label_counts.min()),
        "max_labels": int(label_counts.max()),
        "mean_labels": round(float(label_counts.mean()), 2),
        "median_labels": round(float(label_counts.median()), 1),
    }


def profile_dataset(path: str, compute_hash: bool = True) -> DatasetProfileResponse:
    """Run full profiling on a dataset file or directory of parquets.

    Args:
        path: Path to a single file or directory containing parquet files.
        compute_hash: Whether to compute SHA-256 hash (slow for large files).

    Returns:
        ``DatasetProfileResponse`` with all profiling data.
    """
    p = Path(path)
    file_hash = None

    if p.is_dir():
        parquet_files = sorted(p.glob("*.parquet"))
        if not parquet_files:
            raise FileNotFoundError(f"No parquet files found in {path}")
        df = load_all_parquets([str(f) for f in parquet_files])
        name = p.name
    else:
        df = load_dataframe(path)
        name = p.name
        if compute_hash:
            file_hash = compute_file_hash(path)

    columns = [profile_column(df[col]) for col in df.columns]

    cpc_dist = compute_cpc_distribution(df)
    date_dist = compute_date_distribution(df)
    text_stats = compute_text_length_stats(df)
    label_stats = compute_labels_per_sample(df)

    top_n = 30
    top_cpc = [{"code": k, "count": v} for k, v in list(cpc_dist.items())[:top_n]]

    stats = {
        "cpc_distribution_top30": top_cpc,
        "total_unique_cpc": len(cpc_dist),
        "date_distribution": date_dist,
        "text_length_stats": text_stats,
        "labels_per_sample": label_stats,
    }

    return DatasetProfileResponse(
        path=str(path),
        name=name,
        file_hash=file_hash,
        num_rows=len(df),
        num_cols=len(df.columns),
        columns=columns,
        stats=stats,
    )


def profile_dataset_file(path: str, max_rows: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]:
    """Profile a single dataset file and return a dictionary of results."""
    p = Path(path)
    if p.suffix.lower() == ".parquet":
        import pyarrow.parquet as pq
        pf = pq.ParquetFile(path)
        actual_total_rows = pf.metadata.num_rows
        df = pf.read_row_group(0).to_pandas()
        if max_rows and len(df) > max_rows:
            df = df.head(max_rows)
        # Use actual total rows if not limited
        total_rows = actual_total_rows if max_rows is None else len(df)
    else:
        df = load_dataframe(path, nrows=max_rows)
        total_rows = len(df)

    cols = []
    for col in df.columns:
        c_info = profile_column(df[col])
        cols.append({
            "name": col,
            "dtype": str(df[col].dtype),
            "null_count": int(df[col].isna().sum()),
            "unique_count": int(df[col].nunique()),
            "sample_values": df[col].dropna().head(5).astype(str).tolist(),
        })

    cpc_dist = compute_cpc_distribution(df)
    date_dist = compute_date_distribution(df)
    text_stats = compute_text_length_stats(df)
    label_stats = compute_labels_per_sample(df)

    return {
        "path": str(path),
        "name": p.name,
        "num_rows": total_rows,
        "num_columns": len(df.columns),
        "columns": cols,
        "stats": {
            "cpc_distribution": cpc_dist,
            "date_distribution": date_dist,
            "text_length_stats": text_stats,
            "multi_label_stats": label_stats,
        }
    }
