"""Shared / common Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    """Generic status envelope."""
    status: str = "ok"
    message: str = ""


class ErrorResponse(BaseModel):
    """Standard error body."""
    detail: str


class PaginationParams(BaseModel):
    """Pagination query parameters."""
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=500)


class PaginatedResponse(BaseModel):
    """Wrapper for paginated results."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class JobStatusResponse(BaseModel):
    """Background job status."""
    job_id: int
    type: str
    status: str
    progress: float
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
