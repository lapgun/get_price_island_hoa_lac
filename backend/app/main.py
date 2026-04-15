"""FastAPI backend – API giá đất Hoà Lạc."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import scrape_router, data_router, groups_router, settings_router
from app.tasks.scheduler import start_scheduler, get_scheduler_status

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("app")

app = FastAPI(title="Giá đất Hoà Lạc API", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scrape_router)
app.include_router(data_router)
app.include_router(groups_router)
app.include_router(settings_router)


@app.get("/api/scheduler")
def scheduler_status():
    """Trả về trạng thái scheduler."""
    return get_scheduler_status()


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Database tables created / verified.")
    start_scheduler()
    logger.info("Background scheduler started.")
