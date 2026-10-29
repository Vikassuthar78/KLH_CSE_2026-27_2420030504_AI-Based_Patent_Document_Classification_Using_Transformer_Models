"""Figure serving and retrieval endpoints."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import get_settings

router = APIRouter(prefix="/figures", tags=["Figures"])


@router.get("")
@router.get("/")
def list_figures() -> List[Dict[str, Any]]:
    """List all generated publication figures."""
    settings = get_settings()
    fig_dir = Path(settings.ARTIFACTS_DIR) / "figures"
    if not fig_dir.exists():
        return []

    pngs = sorted(fig_dir.glob("*.png"))
    return [
        {
            "name": p.stem,
            "filename": p.name,
            "url": f"/api/v1/figures/image/{p.name}",
            "size_bytes": p.stat().st_size,
        }
        for p in pngs
    ]


@router.get("/image/{filename}")
def get_figure_image(filename: str):
    """Serve a specific figure image file."""
    settings = get_settings()
    file_path = Path(settings.ARTIFACTS_DIR) / "figures" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Figure not found.")

    return FileResponse(str(file_path), media_type="image/png")

