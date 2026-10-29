"""Experiment configuration dataclasses and schemas."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExperimentConfig(BaseModel):
    """Configuration for an experiment execution."""
    name: str = "Baseline Experiment"
    type: str = "baseline"  # baseline, transformer, hierarchy, conformal, temporal, ablation
    sample_size: int = 10000
    random_seed: int = 42
    split_strategy: str = "random"  # random, temporal
    temporal_cutoff_year: int = 2012
    min_samples_per_class: int = 10
    max_features: int = 50000
    target_coverage: float = 0.90
    model_name: str = "bert-base-uncased"
    batch_size: int = 16
    epochs: int = 3
    hierarchy_penalty: float = 0.1
    enforce_constraints: bool = True

