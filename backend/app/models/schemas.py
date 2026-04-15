"""Pydantic schemas (API request / response)."""

from datetime import datetime

from pydantic import BaseModel


class PriceItem(BaseModel):
    id: int | None = None
    post_id: str = ""
    group_name: str = ""
    post_type: str = ""
    source: str = ""
    link: str = ""
    author: str = ""
    phone: str = ""
    text_snippet: str = ""
    price_ty: str = ""
    price_tr_m2: str = ""
    price_trieu: str = ""
    area: str = ""
    location: str = ""
    ai_summary: str = ""
    estimated_price_ty: float | None = None
    scrape_session: str | None = None
    created_at: datetime | str | None = None

    model_config = {"from_attributes": True}


class ScrapeResponse(BaseModel):
    status: str = "ok"
    count: int = 0
    raw_count: int = 0
    new_count: int = 0
    skipped: int = 0
    scraped_at: str | None = None
    data: list[PriceItem] = []


class DataResponse(BaseModel):
    count: int = 0
    scraped_at: str | None = None
    data: list[PriceItem] = []


class StatsResponse(BaseModel):
    scraped_at: str | None = None
    total: int = 0
    raw_count: int = 0
    by_type: dict[str, int] = {}
    by_location: dict[str, int] = {}
    sessions: list[str] = []
