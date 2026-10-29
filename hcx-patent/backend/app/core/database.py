"""SQLite database setup with SQLAlchemy."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


# ---------------------------------------------------------------------------
# ORM Models
# ---------------------------------------------------------------------------

class DatasetProfile(Base):
    """Persisted dataset profiling result."""

    __tablename__ = "dataset_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(1024), nullable=False, unique=True)
    name = Column(String(256), nullable=False)
    file_hash = Column(String(64), nullable=True)
    num_rows = Column(Integer, nullable=False, default=0)
    num_cols = Column(Integer, nullable=False, default=0)
    columns_json = Column(Text, nullable=False, default="{}")
    stats_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def set_columns(self, data: dict) -> None:
        self.columns_json = json.dumps(data, default=str)

    def get_columns(self) -> dict:
        return json.loads(self.columns_json) if self.columns_json else {}

    def set_stats(self, data: dict) -> None:
        self.stats_json = json.dumps(data, default=str)

    def get_stats(self) -> dict:
        return json.loads(self.stats_json) if self.stats_json else {}


class Experiment(Base):
    """Top-level experiment record."""

    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    type = Column(String(64), nullable=False)  # tfidf, transformer, hierarchy
    config_json = Column(Text, nullable=False, default="{}")
    status = Column(String(32), nullable=False, default="created")
    metrics_json = Column(Text, nullable=False, default="{}")
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_msg = Column(Text, nullable=True)

    def set_config(self, data: dict) -> None:
        self.config_json = json.dumps(data, default=str)

    def get_config(self) -> dict:
        return json.loads(self.config_json) if self.config_json else {}

    def set_metrics(self, data: dict) -> None:
        self.metrics_json = json.dumps(data, default=str)

    def get_metrics(self) -> dict:
        return json.loads(self.metrics_json) if self.metrics_json else {}


class ExperimentRun(Base):
    """Individual run within an experiment."""

    __tablename__ = "experiment_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(Integer, nullable=False, index=True)
    run_id = Column(String(64), nullable=False, unique=True)
    config_json = Column(Text, nullable=False, default="{}")
    metrics_json = Column(Text, nullable=False, default="{}")
    predictions_path = Column(String(1024), nullable=True)
    model_path = Column(String(1024), nullable=True)
    figures_json = Column(Text, nullable=False, default="[]")
    status = Column(String(32), nullable=False, default="created")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def set_config(self, data: dict) -> None:
        self.config_json = json.dumps(data, default=str)

    def get_config(self) -> dict:
        return json.loads(self.config_json) if self.config_json else {}

    def set_metrics(self, data: dict) -> None:
        self.metrics_json = json.dumps(data, default=str)

    def get_metrics(self) -> dict:
        return json.loads(self.metrics_json) if self.metrics_json else {}

    def set_figures(self, data: list) -> None:
        self.figures_json = json.dumps(data, default=str)

    def get_figures(self) -> list:
        return json.loads(self.figures_json) if self.figures_json else []


class Job(Base):
    """Background job record."""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    progress = Column(Float, nullable=False, default=0.0)
    result_json = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    def set_result(self, data: dict) -> None:
        self.result_json = json.dumps(data, default=str)

    def get_result(self) -> Optional[dict]:
        return json.loads(self.result_json) if self.result_json else None


# ---------------------------------------------------------------------------
# Engine / Session helpers
# ---------------------------------------------------------------------------

_engine = None
_SessionLocal = None


def _set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable WAL mode and foreign keys for SQLite."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_engine():
    """Return (and lazily create) the global SQLAlchemy engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.SQLITE_URL,
            echo=False,
            connect_args={"check_same_thread": False},
        )
        event.listen(_engine, "connect", _set_sqlite_pragma)
    return _engine


def get_session_factory():
    """Return (and lazily create) the global sessionmaker."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)
    return _SessionLocal


def SessionLocal() -> Session:
    """Convenience callable returning a new Session instance."""
    return get_session_factory()()


def get_db() -> Session:
    """FastAPI dependency – yields a DB session and closes it after the request."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Create all tables if they do not exist."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
