"""Background scheduler — tự động đồng bộ dữ liệu theo lịch."""

import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.database import SessionLocal
from app.tasks.pipeline import run_pipeline

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(daemon=True)

SYNC_INTERVAL_HOURS = 1


def _scheduled_sync():
    """Job chạy mỗi giờ — gọi pipeline đồng bộ."""
    logger.info("⏰ [Scheduled] Bắt đầu đồng bộ tự động...")
    db = SessionLocal()
    try:
        items, raw_count, new_count, skipped = run_pipeline(db)
        logger.info(
            "⏰ [Scheduled] Xong: %d mới, %d trùng, tổng DB %d.",
            new_count, skipped, len(items),
        )
    except Exception as e:
        logger.error("⏰ [Scheduled] Lỗi đồng bộ: %s", e, exc_info=True)
    finally:
        db.close()


def start_scheduler():
    """Khởi động scheduler với job đồng bộ mỗi SYNC_INTERVAL_HOURS giờ."""
    if scheduler.running:
        return

    scheduler.add_job(
        _scheduled_sync,
        trigger=IntervalTrigger(hours=SYNC_INTERVAL_HOURS),
        id="auto_sync",
        name="Tự động đồng bộ dữ liệu",
        replace_existing=True,
        next_run_time=None,  # Không chạy ngay, đợi đến interval tiếp theo
    )
    scheduler.start()
    logger.info(
        "Scheduler đã khởi động — đồng bộ tự động mỗi %d giờ.",
        SYNC_INTERVAL_HOURS,
    )


def get_scheduler_status() -> dict:
    """Trả về trạng thái scheduler."""
    job = scheduler.get_job("auto_sync")
    if not job:
        return {"running": False, "next_run": None, "interval_hours": SYNC_INTERVAL_HOURS}

    next_run = job.next_run_time
    return {
        "running": scheduler.running,
        "next_run": next_run.isoformat() if next_run else None,
        "interval_hours": SYNC_INTERVAL_HOURS,
    }
