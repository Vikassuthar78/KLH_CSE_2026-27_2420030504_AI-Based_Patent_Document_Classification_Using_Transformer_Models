"""Application configuration using pydantic-settings with .env support."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application settings loaded from environment / .env file."""

    APP_NAME: str = "HCX-Patent"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Paths
    DATASET_ROOT: str = r"D:\ALT-PROJECT\DATA"
    PROJECT_ROOT: str = r"D:\ALT-PROJECT\hcx-patent"
    DATA_DIR: str = r"D:\ALT-PROJECT\hcx-patent\data"
    ARTIFACTS_DIR: str = r"D:\ALT-PROJECT\hcx-patent\artifacts"

    # Database
    SQLITE_URL: str = "sqlite:///D:/ALT-PROJECT/hcx-patent/hcx_patent.db"
    MLFLOW_TRACKING_URI: str = "sqlite:///D:/ALT-PROJECT/hcx-patent/mlflow.db"

    # Dataset
    MAX_PREVIEW_ROWS: int = 100
    DEV_SAMPLE_SIZE: int = 10000
    RANDOM_SEED: int = 42

    # Training
    BATCH_SIZE: int = 64
    MAX_TEXT_LENGTH: int = 512
    NUM_WORKERS: int = 0
    DEVICE: str = "cpu"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        return Settings(_env_file=env_path)
    return Settings()
