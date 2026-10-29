"""Security utilities – path validation and input sanitisation."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from fastapi import HTTPException


def validate_path(user_path: str, allowed_root: str) -> Path:
    """Resolve *user_path* and verify it resides under *allowed_root*.

    Args:
        user_path: Untrusted path received from the client.
        allowed_root: The directory tree the path must reside in.

    Returns:
        Resolved ``pathlib.Path``.

    Raises:
        HTTPException: 403 if the path escapes *allowed_root*, 404 if it does not exist.
    """
    root = Path(allowed_root).resolve()
    resolved = Path(user_path).resolve()
    if not str(resolved).startswith(str(root)):
        raise HTTPException(status_code=403, detail="Access denied – path outside allowed root.")
    if not resolved.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {resolved}")
    return resolved


def sanitize_filename(name: str) -> str:
    """Strip dangerous characters from a filename.

    Args:
        name: Raw filename string.

    Returns:
        Sanitised filename safe for filesystem use.
    """
    # Keep alphanumeric, dashes, underscores, dots
    sanitized = re.sub(r"[^\w\-.]", "_", name)
    # Collapse consecutive underscores
    sanitized = re.sub(r"_+", "_", sanitized)
    # Remove leading dots to prevent hidden files
    sanitized = sanitized.lstrip(".")
    return sanitized or "unnamed"


def sanitize_text_input(text: str, max_length: int = 10000) -> str:
    """Basic sanitisation of free-text input.

    Args:
        text: Raw user text.
        max_length: Maximum allowed character count.

    Returns:
        Cleaned text string.

    Raises:
        HTTPException: 400 if *text* is empty or exceeds *max_length*.
    """
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text input must not be empty.")
    text = text.strip()
    if len(text) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Text too long ({len(text)} chars). Maximum is {max_length}.",
        )
    return text
