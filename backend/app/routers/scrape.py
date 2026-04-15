"""Router: scrape / đồng bộ dữ liệu."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import ScrapeResponse
from app.tasks.pipeline import run_pipeline
from app.tasks.scrape_job import start_scrape_job, get_scrape_job

router = APIRouter(prefix="/api", tags=["scrape"])


@router.post("/scrape", response_model=ScrapeResponse)
def scrape(
    use_ai: bool = Query(default=False, description="Dùng AI trích xuất"),
    db: Session = Depends(get_db),
):
    """Đồng bộ dữ liệu từ Apify vào DB (không lọc, lọc ở client)."""
    items, raw_count, new_count, skipped = run_pipeline(
        db, use_ai=use_ai,
    )
    return ScrapeResponse(
        status="ok",
        count=len(items),
        raw_count=raw_count,
        new_count=new_count,
        skipped=skipped,
        scraped_at=datetime.now().isoformat(),
        data=items,
    )


@router.post("/scrape/start")
def scrape_start(
    use_ai: bool = Query(default=False, description="Dùng AI trích xuất"),
):
    """Bắt đầu job scrape chạy nền để tránh request timeout/504."""
    job_id = start_scrape_job(use_ai=use_ai)
    return {"status": "accepted", "job_id": job_id}


@router.get("/scrape/status/{job_id}")
def scrape_status(job_id: str):
    """Kiểm tra trạng thái job scrape chạy nền."""
    job = get_scrape_job(job_id)
    if not job:
        return {"status": "not_found", "job_id": job_id}
    return job

