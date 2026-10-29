"""Pydantic schemas for experiment APIs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExperimentCreate(BaseModel):
    """Payload to create a new experiment."""
    name: str
    type: str = Field(..., description="tfidf, transformer, or hierarchy")
    config: Dict[str, Any] = Field(default_factory=dict)


class ExperimentResponse(BaseModel):
    """Single experiment record."""
    id: int
    name: str
    type: str
    config: Dict[str, Any] = Field(default_factory=dict)
    status: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_msg: Optional[str] = None


class ExperimentListResponse(BaseModel):
    """List of experiments."""
    experiments: List[ExperimentResponse]
    total: int


class ExperimentRunResponse(BaseModel):
    """Single run record."""
    id: int
    experiment_id: int
    run_id: str
    config: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    predictions_path: Optional[str] = None
    model_path: Optional[str] = None
    figures: List[str] = Field(default_factory=list)
    status: str
    created_at: Optional[datetime] = None


class MetricsResponse(BaseModel):
    """Experiment metrics response."""
    experiment_id: int
    metrics: Dict[str, Any]
    per_class_metrics: Optional[Dict[str, Any]] = None


class PredictionsResponse(BaseModel):
    """Predictions response."""
    experiment_id: int
    predictions: List[Dict[str, Any]]
    total: int


class CompareRequest(BaseModel):
    """Compare multiple experiments."""
    experiment_ids: List[int]


class CompareResponse(BaseModel):
    """Comparison results."""
    experiments: List[Dict[str, Any]]
    metric_comparison: Dict[str, Any]


class RunRequest(BaseModel):
    """Request to launch an experiment run."""
    dev_mode: bool = True
    dev_sample_size: Optional[int] = None
    split_strategy: str = "random"
    config_overrides: Dict[str, Any] = Field(default_factory=dict)
