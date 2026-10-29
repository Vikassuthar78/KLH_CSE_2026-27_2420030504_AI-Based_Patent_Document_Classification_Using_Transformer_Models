"""Pydantic schemas for patent APIs."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ClassifyRequest(BaseModel):
    """Request to classify patent text."""
    text: str = Field(..., min_length=10, max_length=10000)
    model_type: str = Field("tfidf", description="tfidf, transformer, or hierarchy")
    experiment_id: Optional[int] = None
    top_k: int = Field(5, ge=1, le=50)
    include_confidence: bool = True


class ClassifyResult(BaseModel):
    """Single classification prediction."""
    cpc_code: str
    probability: float
    label_name: Optional[str] = None


class ClassifyResponse(BaseModel):
    """Classification response."""
    predictions: List[ClassifyResult]
    model_type: str
    experiment_id: Optional[int] = None
    inference_time_ms: float


class PatentRecord(BaseModel):
    """A patent record from the dataset."""
    id: str
    date: Optional[str] = None
    text: str
    cpc_ids: str
    text_length: int


class PatentSearchRequest(BaseModel):
    """Patent search query."""
    query: Optional[str] = None
    cpc_code: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PatentSearchResponse(BaseModel):
    """Patent search results."""
    patents: List[PatentRecord]
    total: int
    page: int
    page_size: int


class PatentUploadResponse(BaseModel):
    """Response after uploading a patent file."""
    filename: str
    num_records: int
    message: str
