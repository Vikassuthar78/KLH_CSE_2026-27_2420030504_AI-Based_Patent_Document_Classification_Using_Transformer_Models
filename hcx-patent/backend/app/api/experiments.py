"""Experiment management and execution endpoints."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.database import Experiment, ExperimentRun, SessionLocal
from app.evaluation.comparison import compare_runs
from app.experiments.runner import run_experiment_pipeline
from app.experiments.tracker import ExperimentTracker
from app.jobs.manager import JobManager

router = APIRouter(prefix="/experiments", tags=["Experiments"])


class CreateExperimentRequest(BaseModel):
    name: str = "Baseline Experiment"
    type: str = "baseline"
    config: Dict[str, Any] = {}


@router.get("")
@router.get("/")
def list_experiments() -> List[Dict[str, Any]]:
    """List all configured experiments with latest status and metrics."""
    db = SessionLocal()
    try:
        exps = db.query(Experiment).order_by(Experiment.id.desc()).all()
        result = []
        for e in exps:
            result.append({
                "id": e.id,
                "name": e.name,
                "type": e.type,
                "status": e.status,
                "config": json.loads(e.config_json or "{}"),
                "metrics": json.loads(e.metrics_json) if e.metrics_json else None,
                "started_at": e.started_at.isoformat() if e.started_at else None,
                "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                "error": e.error_msg,
            })
        return result
    finally:
        db.close()


@router.post("/create")
def create_experiment(req: CreateExperimentRequest) -> Dict[str, Any]:
    """Create a new experiment configuration."""
    db = SessionLocal()
    try:
        exp = Experiment(
            name=req.name,
            type=req.type,
            config_json=json.dumps(req.config),
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        db.add(exp)
        db.commit()
        db.refresh(exp)
        return {"id": exp.id, "name": exp.name, "type": exp.type, "status": exp.status}
    finally:
        db.close()


@router.post("/{exp_id}/run")
def run_experiment(exp_id: int) -> Dict[str, Any]:
    """Launch experiment execution in background."""
    db = SessionLocal()
    try:
        exp = db.query(Experiment).filter(Experiment.id == exp_id).first()
        if not exp:
            raise HTTPException(status_code=404, detail="Experiment not found.")

        exp.status = "running"
        exp.started_at = datetime.now(timezone.utc)
        db.commit()

        config = json.loads(exp.config_json or "{}")
        config["type"] = exp.type
        config["name"] = exp.name
    finally:
        db.close()

    job_mgr = JobManager()
    job_id = job_mgr.create_job(job_type=f"run_experiment_{exp.type}")

    def task_wrapper(**kwargs):
        progress_cb = kwargs.get("progress_callback")
        res = run_experiment_pipeline(config, exp_id, progress_callback=progress_cb)
        tracker = ExperimentTracker()
        tracker.log_run(
            experiment_id=exp_id,
            run_id=res["run_id"],
            config=config,
            metrics=res["metrics"],
            model_path=res.get("model_path"),
            predictions_path=res.get("predictions_path"),
            figures=res.get("figures"),
            status="completed",
        )
        return res

    job_mgr.submit_job(job_id, task_wrapper)

    return {"job_id": job_id, "experiment_id": exp_id, "status": "running"}


@router.get("/jobs/{job_id}")
def get_job_status(job_id: int) -> Dict[str, Any]:
    """Retrieve background job progress and status."""
    job_mgr = JobManager()
    status = job_mgr.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found.")
    return status


@router.get("/{exp_id}")
def get_experiment_details(exp_id: int) -> Dict[str, Any]:
    """Get detailed experiment metadata and runs."""
    db = SessionLocal()
    try:
        exp = db.query(Experiment).filter(Experiment.id == exp_id).first()
        if not exp:
            raise HTTPException(status_code=404, detail="Experiment not found.")

        runs = db.query(ExperimentRun).filter(ExperimentRun.experiment_id == exp_id).all()
        run_items = []
        for r in runs:
            run_items.append({
                "run_id": r.run_id,
                "metrics": json.loads(r.metrics_json or "{}"),
                "status": r.status,
                "figures": json.loads(r.figures_json or "[]"),
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })

        return {
            "id": exp.id,
            "name": exp.name,
            "type": exp.type,
            "status": exp.status,
            "config": json.loads(exp.config_json or "{}"),
            "metrics": json.loads(exp.metrics_json) if exp.metrics_json else None,
            "runs": run_items,
        }
    finally:
        db.close()


@router.get("/compare/all")
def compare_all_runs() -> Dict[str, Any]:
    """Compare recent runs across models."""
    tracker = ExperimentTracker()
    runs = tracker.list_all_runs()
    return compare_runs(runs)

