"""Health check and system status endpoints."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from app.config import get_settings

router = APIRouter(tags=["Health & Status"])


@router.get("/health")
def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy"}


@router.get("/status")
def app_status() -> Dict[str, Any]:
    """Application status, configured dataset path, and hardware info."""
    settings = get_settings()
    import torch
    import os

    has_data = os.path.exists(settings.DATASET_ROOT)

    return {
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "debug": settings.DEBUG,
        "dataset_root": settings.DATASET_ROOT,
        "dataset_available": has_data,
        "device": settings.DEVICE,
        "cuda_available": torch.cuda.is_available(),
    }

