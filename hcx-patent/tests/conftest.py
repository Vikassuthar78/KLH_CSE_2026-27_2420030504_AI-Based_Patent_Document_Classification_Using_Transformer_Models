"""
HCX-Patent Test Suite - conftest.py
Shared fixtures for all tests
"""
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

import pytest
import numpy as np
import pandas as pd

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def dataset_root():
    """Return the dataset root directory."""
    root = Path(r"D:\ALT-PROJECT\DATA")
    if not root.exists():
        pytest.skip("Dataset root not found")
    return root


@pytest.fixture(scope="session")
def sample_parquet_file(dataset_root):
    """Return path to first parquet file."""
    files = sorted(dataset_root.glob("train-*.parquet"))
    if not files:
        pytest.skip("No parquet files found")
    return files[0]


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    d = tempfile.mkdtemp(prefix="hcx_test_")
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def sample_dataframe():
    """Create a small sample DataFrame mimicking the USPTO-3M schema."""
    np.random.seed(42)
    n = 100
    cpc_options = ["A01H", "B01D", "C07K", "G06F", "H01L", "Y10T", "H04L", "A61K"]
    
    records = []
    for i in range(n):
        num_labels = np.random.randint(1, 4)
        cpcs = ",".join(np.random.choice(cpc_options, num_labels, replace=False))
        records.append({
            "id": str(6000000 + i),
            "date": f"20{np.random.randint(0, 16):02d}-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}",
            "cpc_ids": cpcs,
            "text": f"Patent {i}: This invention relates to a method and apparatus for processing materials "
                    f"with improved efficiency and reduced cost. The method comprises steps of preparing, "
                    f"treating, and finalizing the product according to specified parameters."
        })
    return pd.DataFrame(records)


@pytest.fixture
def sample_texts():
    """Return sample patent texts."""
    return [
        "A method of encoding digital media data comprising applying a transform to blocks of data.",
        "A pharmaceutical composition comprising an effective amount of a therapeutic agent.",
        "An apparatus for processing semiconductor wafers with improved throughput.",
        "A computer-implemented method for analyzing network traffic patterns.",
        "A hard surface cleaning composition comprising a surfactant and solvent."
    ]


@pytest.fixture
def sample_labels():
    """Return sample CPC label arrays for multi-label classification."""
    return [
        ["H04N", "H03M"],
        ["A61K", "A61P"],
        ["H01L"],
        ["G06F", "H04L"],
        ["C11D"]
    ]


@pytest.fixture
def binary_labels(sample_labels):
    """Return binarized label arrays."""
    from sklearn.preprocessing import MultiLabelBinarizer
    mlb = MultiLabelBinarizer()
    return mlb.fit_transform(sample_labels), mlb


@pytest.fixture
def mock_metrics():
    """Return a mock metrics dictionary matching the expected schema."""
    return {
        "accuracy": 0.0,
        "macro_precision": 0.0,
        "macro_recall": 0.0,
        "macro_f1": 0.0,
        "micro_precision": 0.0,
        "micro_recall": 0.0,
        "micro_f1": 0.0,
        "hamming_loss": 0.0,
        "training_time_seconds": 0.0,
        "inference_latency_ms": 0.0,
    }

