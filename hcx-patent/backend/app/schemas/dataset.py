"""Pydantic schemas for dataset APIs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

class DatasetFileInfo(BaseModel):
    """Metadata about a single discovered dataset file."""
    path: str
    name: str
    size_bytes: int
    format: str
    modified_at: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)


class DiscoverResponse(BaseModel):
    """Result of dataset discovery scan."""
    root: str
    files: List[DatasetFileInfo]
    total_files: int


# ---------------------------------------------------------------------------
# Profiling
# ---------------------------------------------------------------------------

class ProfileRequest(BaseModel):
    """Request to profile a dataset."""
    path: Optional[str] = None
    name: Optional[str] = None


class ColumnInfo(BaseModel):
    """Information about a single column."""
    name: str
    dtype: str
    null_count: int = 0
    null_pct: float = 0.0
    unique_count: int = 0
    min_val: Optional[Any] = None
    max_val: Optional[Any] = None
    mean_val: Optional[float] = None
    sample_values: List[Any] = Field(default_factory=list)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)


class DatasetProfileResponse(BaseModel):
    """Full profiling result."""
    id: Optional[int] = None
    path: str
    name: str
    file_hash: Optional[str] = None
    num_rows: int
    num_cols: int
    columns: List[ColumnInfo]
    stats: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

    def __getitem__(self, item: str) -> Any:
        if item == "num_columns":
            return self.num_cols
        return getattr(self, item)


# ---------------------------------------------------------------------------
# Preview
# ---------------------------------------------------------------------------

class PreviewRequest(BaseModel):
    """Preview query params (as body or query)."""
    path: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=500)


class PreviewResponse(BaseModel):
    """Paginated records preview."""
    records: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class ValidationIssue(BaseModel):
    """A single data-quality issue."""
    severity: str  # error, warning, info
    column: Optional[str] = None
    message: str
    count: Optional[int] = None


class ValidateRequest(BaseModel):
    """Request body for dataset validation."""
    path: Optional[str] = None


class ValidateResponse(BaseModel):
    """Validation result."""
    valid: bool
    issues: List[ValidationIssue]
    summary: str


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

class DatasetStatsResponse(BaseModel):
    """Aggregate dataset statistics."""
    num_rows: int
    num_cols: int
    cpc_distribution: Dict[str, int] = Field(default_factory=dict)
    date_range: Optional[Dict[str, str]] = None
    text_length_stats: Optional[Dict[str, float]] = None
    labels_per_sample: Optional[Dict[str, float]] = None
    top_cpc_codes: List[Dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Splitting
# ---------------------------------------------------------------------------

class SplitRequest(BaseModel):
    """Dataset split configuration."""
    strategy: str = Field("random", description="random or temporal")
    train_ratio: float = Field(0.70, ge=0.1, le=0.95)
    val_ratio: float = Field(0.10, ge=0.0, le=0.3)
    cal_ratio: float = Field(0.10, ge=0.0, le=0.3)
    test_ratio: float = Field(0.10, ge=0.05, le=0.5)
    temporal_cutoff: Optional[str] = None
    stratify: bool = False
    dev_sample: bool = True
    dev_sample_size: Optional[int] = None
    seed: int = 42


class SplitResponse(BaseModel):
    """Split result summary."""
    strategy: str
    splits: Dict[str, int]
    manifest_path: str
    dev_sample_size: Optional[int] = None
    message: str
