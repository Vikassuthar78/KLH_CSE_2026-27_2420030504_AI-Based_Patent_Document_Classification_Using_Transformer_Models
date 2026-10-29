"""Data quality validation for patent datasets."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd

logger = logging.getLogger(__name__)


class ValidationIssueDict(dict):
    """Dictionary representing a validation issue with dict and attribute access."""
    def __init__(self, severity: str, type: str, message: str, column: Optional[str] = None, count: int = 0):
        super().__init__(
            severity=severity,
            type=type,
            message=message,
            column=column,
            count=count,
        )
        self.severity = severity
        self.type = type
        self.message = message
        self.column = column
        self.count = count


def validate_dataset(
    df: pd.DataFrame,
    id_col: str = "id",
    text_col: str = "text",
    label_col: str = "cpc_ids",
    date_col: str = "date",
    **kwargs: Any,
) -> List[Dict[str, Any]]:
    """Run data quality checks on patent dataset DataFrame.

    Returns:
        List of validation issues with 'severity', 'type', 'message', 'column', 'count'.
    """
    issues: List[ValidationIssueDict] = []

    # 1. Check required columns exist
    for col_name, col_role in [(id_col, "identifier"), (text_col, "text"), (label_col, "label")]:
        if col_name not in df.columns:
            issues.append(
                ValidationIssueDict(
                    severity="critical",
                    type="missing_column",
                    column=col_name,
                    message=f"Required {col_role} column '{col_name}' is missing.",
                    count=1,
                )
            )

    if any(i.severity == "critical" and i.type == "missing_column" for i in issues):
        return issues

    # 2. Check for duplicate identifiers
    if id_col in df.columns:
        duplicate_count = int(df.duplicated(subset=[id_col]).sum())
        if duplicate_count > 0:
            issues.append(
                ValidationIssueDict(
                    severity="warning",
                    type="duplicate_identifiers",
                    column=id_col,
                    message=f"Found {duplicate_count} duplicate patent identifiers in '{id_col}'.",
                    count=duplicate_count,
                )
            )

    # 3. Check for null or empty text
    if text_col in df.columns:
        null_texts = int(df[text_col].isna().sum())
        empty_texts = int((df[text_col].fillna("").astype(str).str.strip() == "").sum())
        if null_texts > 0:
            issues.append(
                ValidationIssueDict(
                    severity="critical",
                    type="null_text",
                    column=text_col,
                    message=f"Found {null_texts} null text records in '{text_col}'.",
                    count=null_texts,
                )
            )
        if empty_texts > 0:
            issues.append(
                ValidationIssueDict(
                    severity="warning",
                    type="empty_text",
                    column=text_col,
                    message=f"Found {empty_texts} empty string text records in '{text_col}'.",
                    count=empty_texts,
                )
            )

    # 4. Check for null or empty labels
    if label_col in df.columns:
        null_labels = int(df[label_col].isna().sum())
        empty_labels = int((df[label_col].fillna("").astype(str).str.strip() == "").sum())
        if null_labels > 0:
            issues.append(
                ValidationIssueDict(
                    severity="critical",
                    type="missing_labels",
                    column=label_col,
                    message=f"Found {null_labels} null label entries in '{label_col}'.",
                    count=null_labels,
                )
            )
        if empty_labels > 0:
            issues.append(
                ValidationIssueDict(
                    severity="warning",
                    type="empty_labels",
                    column=label_col,
                    message=f"Found {empty_labels} empty string label records in '{label_col}'.",
                    count=empty_labels,
                )
            )

    # 5. Check date validity if date column present
    if date_col in df.columns:
        null_dates = int(df[date_col].isna().sum())
        if null_dates > 0:
            issues.append(
                ValidationIssueDict(
                    severity="info",
                    type="missing_dates",
                    column=date_col,
                    message=f"Found {null_dates} missing dates in '{date_col}'.",
                    count=null_dates,
                )
            )

    return issues
