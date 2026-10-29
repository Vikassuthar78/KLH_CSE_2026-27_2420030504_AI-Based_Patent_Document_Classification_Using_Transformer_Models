"""Background job manager with SQLite persistence and progress tracking."""

from __future__ import annotations

import concurrent.futures
import json
import logging
import threading
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from app.core.database import Job, SessionLocal

logger = logging.getLogger(__name__)


class JobManager:
    """Thread-pool background job executor."""

    _instance: Optional["JobManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "JobManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_manager()
            return cls._instance

    def _init_manager(self) -> None:
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="HCXJobWorker")
        self.active_futures: Dict[int, concurrent.futures.Future] = {}

    def create_job(self, job_type: str) -> int:
        """Create a new job record in SQLite."""
        db = SessionLocal()
        try:
            job = Job(
                type=job_type,
                status="pending",
                progress=0.0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            return job.id
        finally:
            db.close()

    def update_job(
        self,
        job_id: int,
        status: Optional[str] = None,
        progress: Optional[float] = None,
        result: Optional[Any] = None,
        error: Optional[str] = None,
    ) -> None:
        """Update job status, progress, and result in SQLite."""
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                if status is not None:
                    job.status = status
                if progress is not None:
                    job.progress = float(progress)
                if result is not None:
                    job.result_json = json.dumps(result)
                if error is not None:
                    job.error = str(error)
                job.updated_at = datetime.now(timezone.utc)
                db.commit()
        except Exception as e:
            logger.error("Failed to update job %d: %s", job_id, e)
        finally:
            db.close()

    def submit_job(
        self,
        job_id: int,
        task_fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> concurrent.futures.Future:
        """Submit a task to run in the background thread pool."""
        def wrapper():
            self.update_job(job_id, status="running", progress=0.0)
            try:
                def progress_cb(pct: float, msg: str):
                    self.update_job(job_id, progress=pct)

                kwargs["progress_callback"] = progress_cb
                res = task_fn(*args, **kwargs)
                self.update_job(job_id, status="completed", progress=1.0, result=res)
                return res
            except Exception as e:
                logger.exception("Job %d failed: %s", job_id, e)
                self.update_job(job_id, status="failed", error=str(e))
                raise

        future = self.executor.submit(wrapper)
        self.active_futures[job_id] = future
        return future

    def get_job_status(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve job status and result from SQLite."""
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return None
            return {
                "id": job.id,
                "type": job.type,
                "status": job.status,
                "progress": job.progress,
                "result": json.loads(job.result_json) if job.result_json else None,
                "error": job.error,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "updated_at": job.updated_at.isoformat() if job.updated_at else None,
            }
        finally:
            db.close()

