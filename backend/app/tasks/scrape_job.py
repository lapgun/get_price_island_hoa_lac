"""In-memory background scrape job manager."""

import logging
import threading
import uuid
from datetime import datetime

from app.database import SessionLocal
from app.tasks.pipeline import run_pipeline

logger = logging.getLogger(__name__)

_jobs: dict[str, dict] = {}
_jobs_lock = threading.Lock()


def _run_job(job_id: str, use_ai: bool = False):
    db = SessionLocal()
    try:
        with _jobs_lock:
            _jobs[job_id]["status"] = "running"
            _jobs[job_id]["started_at"] = datetime.now().isoformat()

        items, raw_count, new_count, skipped = run_pipeline(db, use_ai=use_ai)

        with _jobs_lock:
            _jobs[job_id].update({
                "status": "done",
                "finished_at": datetime.now().isoformat(),
                "result": {
                    "count": len(items),
                    "raw_count": raw_count,
                    "new_count": new_count,
                    "skipped": skipped,
                },
            })
    except Exception as exc:
        logger.error("Background scrape job failed: %s", exc, exc_info=True)
        with _jobs_lock:
            _jobs[job_id].update({
                "status": "failed",
                "finished_at": datetime.now().isoformat(),
                "error": str(exc),
            })
    finally:
        db.close()


def start_scrape_job(use_ai: bool = False) -> str:
    job_id = str(uuid.uuid4())
    with _jobs_lock:
        _jobs[job_id] = {
            "id": job_id,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "finished_at": None,
            "result": None,
            "error": None,
        }

    thread = threading.Thread(
        target=_run_job,
        kwargs={"job_id": job_id, "use_ai": use_ai},
        daemon=True,
    )
    thread.start()
    return job_id


def get_scrape_job(job_id: str) -> dict | None:
    with _jobs_lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None
