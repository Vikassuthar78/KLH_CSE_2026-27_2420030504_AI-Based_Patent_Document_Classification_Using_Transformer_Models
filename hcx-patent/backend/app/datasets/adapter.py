"""Configurable dataset adapter with column mapping.

Maps actual dataset columns to canonical names expected by the pipeline.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Default column mapping for the HCX-Patent dataset
DEFAULT_COLUMN_MAP: Dict[str, str] = {
    "patent_id": "id",
    "text": "text",
    "cpc_codes": "cpc_ids",
    "date": "date",
}

# Reverse: canonical -> actual
CANONICAL_COLUMNS = {"patent_id", "text", "cpc_codes", "date", "title", "abstract", "claims"}


class DatasetAdapter:
    """Adapts a raw DataFrame to canonical column names.

    Args:
        column_map: Mapping from canonical name to actual column name.
        column_mapping: Alias for column_map.
    """

    def __init__(
        self,
        column_map: Optional[Dict[str, str]] = None,
        column_mapping: Optional[Dict[str, str]] = None,
    ) -> None:
        self.column_map = column_mapping or column_map or dict(DEFAULT_COLUMN_MAP)

    def apply_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply mapping to DataFrame, raising KeyError if required mapped columns are missing."""
        for canonical, actual in self.column_map.items():
            if actual not in df.columns:
                raise KeyError(f"Mapped actual column '{actual}' not found in DataFrame columns: {list(df.columns)}")
        return self.adapt(df)

    def check_nulls(self, df: pd.DataFrame) -> Dict[str, int]:
        """Return null counts for each column in df."""
        return {str(col): int(df[col].isna().sum()) for col in df.columns}

    def detect_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """Auto-detect column mapping based on column names.

        Args:
            df: Raw DataFrame.

        Returns:
            Detected mapping from canonical name to actual column name.
        """
        actual_cols = set(df.columns)
        detected: Dict[str, str] = {}

        # Direct matches
        direct_map = {
            "id": "patent_id",
            "patent_id": "patent_id",
            "text": "text",
            "cpc_ids": "cpc_codes",
            "cpc_codes": "cpc_codes",
            "cpc_id": "cpc_codes",
            "labels": "cpc_codes",
            "date": "date",
            "filing_date": "date",
            "title": "title",
            "abstract": "abstract",
            "claims": "claims",
        }

        for actual_col in actual_cols:
            col_lower = actual_col.lower().strip()
            if col_lower in direct_map:
                canonical = direct_map[col_lower]
                detected[canonical] = actual_col

        self.column_map = detected
        logger.info("Auto-detected column mapping: %s", detected)
        return detected

    def adapt(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename columns in *df* to canonical names.

        Args:
            df: Raw DataFrame.

        Returns:
            DataFrame with canonical column names.
        """
        rename_map: Dict[str, str] = {}
        for canonical, actual in self.column_map.items():
            if actual in df.columns:
                rename_map[actual] = canonical

        adapted = df.rename(columns=rename_map)
        logger.debug("Adapted columns: %s", list(adapted.columns))
        return adapted

    def get_canonical_column(self, canonical_name: str) -> Optional[str]:
        """Get the actual column name for a canonical name.

        Args:
            canonical_name: One of the canonical column names.

        Returns:
            Actual column name or None.
        """
        return self.column_map.get(canonical_name)

    def validate_required_columns(self, df: pd.DataFrame) -> List[str]:
        """Check that required canonical columns are present (or mappable).

        Args:
            df: DataFrame to validate.

        Returns:
            List of missing canonical columns.
        """
        required = {"patent_id", "text", "cpc_codes"}
        available_canonical = set()

        for canonical, actual in self.column_map.items():
            if actual in df.columns:
                available_canonical.add(canonical)

        # Also check direct column names
        for col in df.columns:
            if col in required:
                available_canonical.add(col)

        missing = required - available_canonical
        return list(missing)
