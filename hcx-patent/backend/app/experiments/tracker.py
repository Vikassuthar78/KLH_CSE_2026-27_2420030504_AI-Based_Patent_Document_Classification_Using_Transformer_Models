"""Experiment tracking with SQLite metadata persistence and artifact management."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.core.database import SessionLocal, ExperimentRun, Experiment

logger = logging.getLogger(__name__)


class ExperimentTracker:
    """Manages experiment runs, metrics logging, and artifact persistence."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.artifacts_dir = Path(self.settings.ARTIFACTS_DIR)
        for sub in ["metrics", "checkpoints", "predictions", "figures", "reports"]:
            (self.artifacts_dir / sub).mkdir(parents=True, exist_ok=True)

    def log_run(
        self,
        experiment_id: int,
        run_id: str,
        config: Dict[str, Any],
        metrics: Dict[str, Any],
        model_path: Optional[str] = None,
        predictions_path: Optional[str] = None,
        figures: Optional[List[Dict[str, Any]]] = None,
        status: str = "completed",
        error: Optional[str] = None,
    ) -> int:
        """Persist experiment run record to SQLite and JSON artifact."""
        # 1. Save metrics JSON
        metrics_file = self.artifacts_dir / "metrics" / f"{run_id}_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)

        # 2. Save SQLite record
        db = SessionLocal()
        try:
            run = ExperimentRun(
                experiment_id=experiment_id,
                run_id=run_id,
                config_json=json.dumps(config),
                metrics_json=json.dumps(metrics),
                predictions_path=predictions_path,
                model_path=model_path,
                figures_json=json.dumps(figures or []),
                status=status,
                created_at=datetime.now(timezone.utc),
            )
            db.add(run)

            # Update parent experiment status
            exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
            if exp:
                exp.status = status
                exp.metrics_json = json.dumps(metrics)
                exp.completed_at = datetime.now(timezone.utc)
                if error:
                    exp.error_msg = error

            db.commit()
            db.refresh(run)
            return run.id
        except Exception as e:
            db.rollback()
            logger.error("Failed to persist experiment run to database: %s", e)
            return -1
        finally:
            db.close()

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve run metadata by run_id."""
        db = SessionLocal()
        try:
            run = db.query(ExperimentRun).filter(ExperimentRun.run_id == run_id).first()
            if not run:
                return None
            return {
                "id": run.id,
                "run_id": run.run_id,
                "experiment_id": run.experiment_id,
                "config": json.loads(run.config_json or "{}"),
                "metrics": json.loads(run.metrics_json or "{}"),
                "status": run.status,
                "figures": json.loads(run.figures_json or "[]"),
                "model_path": run.model_path,
                "predictions_path": run.predictions_path,
                "created_at": run.created_at.isoformat() if run.created_at else None,
            }
        finally:
            db.close()

    def list_all_runs(self) -> List[Dict[str, Any]]:
        """List all completed or active runs."""
        db = SessionLocal()
        try:
            runs = db.query(ExperimentRun).order_by(ExperimentRun.id.desc()).all()
            result = []
            for r in runs:
                result.append({
                    "id": r.id,
                    "run_id": r.run_id,
                    "experiment_id": r.experiment_id,
                    "metrics": json.loads(r.metrics_json or "{}"),
                    "status": r.status,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                })
            return result
        finally:
            db.close()

