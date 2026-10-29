"""
Tests for dataset adapter, discovery, and profiling
"""
import os
import sys
import json
import tempfile
from pathlib import Path

import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


class TestDatasetDiscovery:
    """Tests for dataset file discovery."""

    def test_discover_parquet_files(self, dataset_root):
        """Test that parquet files are discovered."""
        from app.datasets.discovery import discover_dataset_files
        files = discover_dataset_files(str(dataset_root))
        assert len(files) == 7
        assert all(f["format"] == "parquet" for f in files)

    def test_discover_empty_directory(self, temp_dir):
        """Test discovery with empty directory."""
        from app.datasets.discovery import discover_dataset_files
        files = discover_dataset_files(str(temp_dir))
        assert len(files) == 0

    def test_discover_nonexistent_directory(self):
        """Test discovery with nonexistent directory."""
        from app.datasets.discovery import discover_dataset_files
        files = discover_dataset_files(r"C:\nonexistent\path")
        assert len(files) == 0


class TestDatasetProfiler:
    """Tests for dataset profiling."""

    def test_profile_parquet_file(self, sample_parquet_file):
        """Test profiling a real parquet file."""
        from app.datasets.profiler import profile_dataset_file
        profile = profile_dataset_file(str(sample_parquet_file), max_rows=1000)
        assert profile["num_rows"] > 0
        assert "columns" in profile
        assert len(profile["columns"]) == 4
        col_names = [c["name"] for c in profile["columns"]]
        assert "id" in col_names
        assert "text" in col_names
        assert "cpc_ids" in col_names
        assert "date" in col_names

    def test_profile_sample_dataframe(self, sample_dataframe, temp_dir):
        """Test profiling from a DataFrame."""
        path = temp_dir / "test.parquet"
        sample_dataframe.to_parquet(path)
        from app.datasets.profiler import profile_dataset_file
        profile = profile_dataset_file(str(path))
        assert profile["num_rows"] == 100
        assert profile["num_columns"] == 4


class TestDatasetAdapter:
    """Tests for dataset adapter and column mapping."""

    def test_load_with_column_mapping(self, sample_dataframe):
        """Test loading data with column mapping."""
        from app.datasets.adapter import DatasetAdapter
        mapping = {
            "patent_id": "id",
            "text": "text",
            "cpc_codes": "cpc_ids",
            "date": "date"
        }
        adapter = DatasetAdapter(column_mapping=mapping)
        result = adapter.apply_mapping(sample_dataframe)
        assert "patent_id" in result.columns
        assert "cpc_codes" in result.columns

    def test_missing_column_raises_error(self, sample_dataframe):
        """Test that mapping to nonexistent column raises error."""
        from app.datasets.adapter import DatasetAdapter
        mapping = {
            "patent_id": "nonexistent_column",
            "text": "text",
        }
        adapter = DatasetAdapter(column_mapping=mapping)
        with pytest.raises((KeyError, ValueError)):
            adapter.apply_mapping(sample_dataframe)

    def test_null_detection(self, sample_dataframe):
        """Test null value detection."""
        from app.datasets.adapter import DatasetAdapter
        # Introduce nulls
        df = sample_dataframe.copy()
        df.loc[0, "text"] = None
        adapter = DatasetAdapter()
        report = adapter.check_nulls(df)
        assert report["text"] >= 1


class TestDatasetValidator:
    """Tests for data validation."""

    def test_validate_good_data(self, sample_dataframe):
        """Test validation on well-formed data."""
        from app.datasets.validator import validate_dataset
        issues = validate_dataset(sample_dataframe, id_col="id", text_col="text", label_col="cpc_ids")
        # Should find no critical issues
        critical = [i for i in issues if i.get("severity") == "critical"]
        assert len(critical) == 0

    def test_detect_duplicates(self, sample_dataframe):
        """Test duplicate detection."""
        from app.datasets.validator import validate_dataset
        df = pd.concat([sample_dataframe, sample_dataframe.head(5)], ignore_index=True)
        issues = validate_dataset(df, id_col="id", text_col="text", label_col="cpc_ids")
        dup_issues = [i for i in issues if "duplicate" in i.get("type", "").lower()]
        assert len(dup_issues) > 0

    def test_detect_missing_labels(self):
        """Test detection of empty labels."""
        from app.datasets.validator import validate_dataset
        df = pd.DataFrame({
            "id": ["1", "2", "3"],
            "text": ["text a", "text b", "text c"],
            "cpc_ids": ["A01H", "", "G06F"],
            "date": ["2020-01-01"] * 3
        })
        issues = validate_dataset(df, id_col="id", text_col="text", label_col="cpc_ids")
        label_issues = [i for i in issues if "label" in i.get("type", "").lower() or "empty" in i.get("type", "").lower()]
        assert len(label_issues) > 0


class TestDatasetSplitter:
    """Tests for train/val/cal/test splitting."""

    def test_random_split_ratios(self, sample_dataframe):
        """Test that random split produces correct approximate ratios."""
        from app.datasets.splitter import create_splits
        splits = create_splits(
            sample_dataframe, 
            strategy="random",
            train_ratio=0.7, val_ratio=0.1, cal_ratio=0.1, test_ratio=0.1,
            random_seed=42
        )
        total = sum(len(s) for s in splits.values())
        assert total == len(sample_dataframe)
        assert len(splits["train"]) > len(splits["test"])

    def test_temporal_split(self, sample_dataframe):
        """Test temporal split by date."""
        from app.datasets.splitter import create_splits
        splits = create_splits(
            sample_dataframe,
            strategy="temporal",
            date_col="date",
            temporal_cutoff="2010-01-01",
            train_ratio=0.7, val_ratio=0.1, cal_ratio=0.1, test_ratio=0.1,
            random_seed=42
        )
        assert "train" in splits
        assert "test" in splits

    def test_no_leakage_between_splits(self, sample_dataframe):
        """Test that no patent ID appears in multiple splits."""
        from app.datasets.splitter import create_splits
        splits = create_splits(
            sample_dataframe,
            strategy="random",
            train_ratio=0.7, val_ratio=0.1, cal_ratio=0.1, test_ratio=0.1,
            random_seed=42,
            id_col="id"
        )
        train_ids = set(splits["train"]["id"])
        val_ids = set(splits["val"]["id"])
        cal_ids = set(splits["cal"]["id"])
        test_ids = set(splits["test"]["id"])
        
        assert len(train_ids & val_ids) == 0
        assert len(train_ids & test_ids) == 0
        assert len(train_ids & cal_ids) == 0
        assert len(val_ids & test_ids) == 0
        assert len(val_ids & cal_ids) == 0
        assert len(cal_ids & test_ids) == 0

