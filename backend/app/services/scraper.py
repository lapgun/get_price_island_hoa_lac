"""Scrape Facebook Groups — Playwright (local, miễn phí) hoặc Apify (fallback)."""

import json
import logging

from app.config import (
    APIFY_TOKEN,
    APIFY_ACTOR_ID,
    MAX_POSTS_PER_GROUP,
    SCRAPE_COMMENTS,
    DAYS_TO_SCRAPE,
)
from app.database import SessionLocal
from app.services.group_store import get_group_urls
from app.services.runtime_settings import get_runtime_fb_cookie

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Apify helpers (giữ lại làm fallback)
# ---------------------------------------------------------------------------

def _parse_cookie_string(cookie_str: str) -> list[dict]:
    cookies = []
    for pair in cookie_str.split(";"):
        pair = pair.strip()
        if "=" not in pair:
            continue
        name, value = pair.split("=", 1)
        cookies.append({
            "name": name.strip(),
            "value": value.strip(),
            "domain": ".facebook.com",
        })
    return cookies


def _get_cookies(cookie_raw: str) -> list[dict]:
    if not cookie_raw:
        return []
    try:
        parsed = json.loads(cookie_raw)
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    return _parse_cookie_string(cookie_raw)


def _build_input_whoareyouanas(group_urls: list[str], cookie_raw: str) -> dict:
    run_input: dict = {
        "startUrls": [{"url": url} for url in group_urls],
        "maxPosts": MAX_POSTS_PER_GROUP,
        "includeComments": SCRAPE_COMMENTS,
        "onlyPostsNewerThan": f"{DAYS_TO_SCRAPE} days",
        "maxConcurrency": 1,
    }
    cookies = _get_cookies(cookie_raw)
    if cookies:
        run_input["cookies"] = cookies
    return run_input


def _fetch_posts_apify(group_urls: list[str], cookie_raw: str) -> list[dict]:
    """Fallback: dùng Apify Actor."""
    from apify_client import ApifyClient

    if not APIFY_TOKEN:
        raise RuntimeError("APIFY_TOKEN chưa được cấu hình trong .env")

    client = ApifyClient(APIFY_TOKEN)
    run_input = _build_input_whoareyouanas(group_urls, cookie_raw)

    logger.info(
        "Bắt đầu chạy Apify Actor %s cho %d nhóm …",
        APIFY_ACTOR_ID, len(group_urls),
    )
    run = client.actor(APIFY_ACTOR_ID).call(run_input=run_input)
    dataset_items = list(
        client.dataset(run["defaultDatasetId"]).iterate_items()
    )
    logger.info("Lấy được %d bài viết từ Apify.", len(dataset_items))
    return dataset_items


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_posts() -> list[dict]:
    """Scrape FB Groups. Ưu tiên Apify, fallback Playwright nếu lỗi."""
    cookie_raw = ""
    cookie_source = "none"
    db = SessionLocal()
    try:
        group_urls = get_group_urls(db)
        cookie_raw, cookie_source = get_runtime_fb_cookie(db)
    finally:
        db.close()

    if not group_urls:
        raise RuntimeError("Chưa có group trong DB. Hãy thêm group ở /api/groups.")

    # --- Ưu tiên Apify ---
    if APIFY_TOKEN:
        try:
            posts = _fetch_posts_apify(group_urls, cookie_raw)
            if posts:
                return posts
            logger.warning("Apify trả về 0 bài, thử fallback Playwright…")
        except Exception as e:
            logger.error("Apify lỗi: %s — thử fallback Playwright…", e)

    # --- Fallback: Playwright (local, miễn phí, không giới hạn) ---
    if cookie_raw:
        try:
            from app.services.fb_playwright import fetch_posts_playwright
            logger.info("Sử dụng Playwright scraper (local, miễn phí), cookie source=%s…", cookie_source)
            return fetch_posts_playwright()
        except ImportError:
            logger.error("Playwright chưa cài đặt. Chạy: pip install playwright && playwright install chromium")
        except Exception as e:
            logger.error("Playwright lỗi: %s", e)

    raise RuntimeError(
        "Không thể scrape: Apify hết credit và Playwright cũng thất bại. "
        "Kiểm tra APIFY_TOKEN hoặc cập nhật cookie qua /api/settings/fb-cookie."
    )
