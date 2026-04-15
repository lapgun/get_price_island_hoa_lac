"""Cấu hình đọc từ biến môi trường (.env)."""

import os
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN: str = os.getenv("APIFY_TOKEN", "")
FB_COOKIE: str = os.getenv("FB_COOKIE", "")
FB_GROUP_URLS: list[str] = [
    u.strip() for u in os.getenv("FB_GROUP_URLS", "").split(",") if u.strip()
]
APIFY_ACTOR_ID: str = os.getenv("APIFY_ACTOR_ID", "apify/facebook-groups-scraper")
MAX_POSTS_PER_GROUP: int = int(os.getenv("MAX_POSTS_PER_GROUP", "200"))
SCRAPE_COMMENTS: bool = os.getenv("SCRAPE_COMMENTS", "true").lower() == "true"
DAYS_TO_SCRAPE: int = int(os.getenv("DAYS_TO_SCRAPE", "10"))
PRICE_MIN_TY: float = float(os.getenv("PRICE_MIN_TY", "1.0"))
PRICE_MAX_TY: float = float(os.getenv("PRICE_MAX_TY", "2.0"))

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
