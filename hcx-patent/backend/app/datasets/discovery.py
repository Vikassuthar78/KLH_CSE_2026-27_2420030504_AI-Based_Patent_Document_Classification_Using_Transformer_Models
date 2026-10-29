"""Auto-discover dataset files in the configured DATASET_ROOT."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from app.schemas.dataset import DatasetFileInfo

logger = logging.getLogger(__name__)

# Supported extensions
SUPPORTED_EXTENSIONS = {".parquet", ".csv", ".tsv", ".json", ".jsonl"}


def discover_datasets(root_dir: str) -> List[DatasetFileInfo]:
    """Scan *root_dir* recursively for supported dataset files.

    Args:
        root_dir: Filesystem directory to scan.

    Returns:
        List of ``DatasetFileInfo`` objects.
    """
    root = Path(root_dir)
    if not root.exists():
        logger.warning("Dataset root does not exist: %s", root_dir)
        return []

    files: List[DatasetFileInfo] = []

    for entry in sorted(root.rglob("*")):
        if entry.is_file() and entry.suffix.lower() in SUPPORTED_EXTENSIONS:
            stat = entry.stat()
            modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            fmt = entry.suffix.lstrip(".").lower()
            if fmt == "tsv":
                fmt = "csv"  # treat TSV as CSV variant

            files.append(
                DatasetFileInfo(
                    path=str(entry),
                    name=entry.name,
                    size_bytes=stat.st_size,
                    format=fmt,
                    modified_at=modified,
                )
            )

    logger.info("Discovered %d dataset files in %s", len(files), root_dir)
    return files


discover_dataset_files = discover_datasets


def get_default_dataset_path(root_dir: str) -> str | None:
    """Return the path to the first parquet file in *root_dir*, or None.

    Args:
        root_dir: Filesystem directory to scan.

    Returns:
        Path string or None.
    """
    root = Path(root_dir)
    if not root.exists():
        return None
    parquets = sorted(root.glob("*.parquet"))
    if parquets:
        return str(parquets[0])
    # Fallback to any supported file
    for ext in SUPPORTED_EXTENSIONS:
        found = sorted(root.glob(f"*{ext}"))
        if found:
            return str(found[0])
    return None


def list_parquet_files(root_dir: str) -> List[str]:
    """Return sorted list of parquet file paths under *root_dir*.

    Args:
        root_dir: Directory to scan.

    Returns:
        List of absolute path strings.
    """
    root = Path(root_dir)
    if not root.exists():
        return []
    return [str(p) for p in sorted(root.glob("*.parquet"))]
