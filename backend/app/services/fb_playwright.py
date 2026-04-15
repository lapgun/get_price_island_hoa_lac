"""Self-hosted Facebook Group scraper using Playwright (thay thế Apify)."""

import json
import logging
import re
from datetime import datetime, timedelta, timezone

from playwright.sync_api import sync_playwright, Page, BrowserContext

from app.config import (
    MAX_POSTS_PER_GROUP,
    SCRAPE_COMMENTS,
    DAYS_TO_SCRAPE,
)
from app.database import SessionLocal
from app.services.group_store import get_group_urls
from app.services.runtime_settings import get_runtime_fb_cookie

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cookie helpers
# ---------------------------------------------------------------------------

def _parse_cookies(cookie_str: str) -> list[dict]:
    """Parse FB_COOKIE string hoặc JSON thành list dùng cho Playwright."""
    if not cookie_str:
        return []
    # Try JSON array first
    try:
        parsed = json.loads(cookie_str)
        if isinstance(parsed, list):
            cookies = []
            for c in parsed:
                cookies.append({
                    "name": c.get("name", ""),
                    "value": c.get("value", ""),
                    "domain": c.get("domain", ".facebook.com"),
                    "path": c.get("path", "/"),
                })
            return cookies
    except (json.JSONDecodeError, TypeError):
        pass
    # Parse key=value; pairs
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
            "path": "/",
        })
    return cookies


# ---------------------------------------------------------------------------
# Post extraction from DOM
# ---------------------------------------------------------------------------

def _extract_post_id(el_html: str, permalink: str) -> str:
    """Trích post ID từ permalink hoặc HTML."""
    # From permalink: /groups/123/posts/456/ or /permalink/456/
    m = re.search(r"/(?:posts|permalink)/(\d+)", permalink)
    if m:
        return m.group(1)
    # From data attributes
    m = re.search(r'data-ft="[^"]*story_fbid["\s:]+(\d+)', el_html)
    if m:
        return m.group(1)
    # Fallback: any long number in permalink
    m = re.search(r"/(\d{10,})", permalink)
    if m:
        return m.group(1)
    return ""


def _extract_posts_from_page(page: Page, group_url: str, max_posts: int,
                              cutoff: datetime, scrape_comments: bool) -> list[dict]:
    """Scroll group page và extract bài viết."""
    posts: list[dict] = []
    seen_ids: set[str] = set()
    no_new_count = 0
    max_no_new = 8  # Stop sau 8 scroll liên tiếp không có bài mới

    # Lấy tên nhóm
    group_name = ""
    try:
        name_el = page.query_selector("h1")
        if name_el:
            group_name = name_el.inner_text().strip()
    except Exception:
        pass
    if not group_name:
        group_name = group_url.split("/groups/")[-1].rstrip("/")

    logger.info("Đang scrape nhóm: %s (%s)", group_name, group_url)

    for scroll_i in range(60):  # max 60 scrolls
        if len(posts) >= max_posts:
            break

        # Tìm tất cả post containers
        post_elements = page.query_selector_all(
            'div[role="article"][aria-label], '
            'div[role="article"][data-ad-preview], '
            'div[class*="userContentWrapper"], '
            'div[data-ad-comet-preview-index]'
        )

        # Fallback selector nếu không tìm thấy
        if not post_elements:
            post_elements = page.query_selector_all('div[role="article"]')

        new_in_scroll = 0
        for el in post_elements:
            if len(posts) >= max_posts:
                break

            try:
                # Lấy permalink
                permalink = ""
                link_els = el.query_selector_all('a[href*="/posts/"], a[href*="/permalink/"]')
                for link_el in link_els:
                    href = link_el.get_attribute("href") or ""
                    if "/posts/" in href or "/permalink/" in href:
                        permalink = href.split("?")[0]
                        break

                post_id = _extract_post_id("", permalink)
                if not post_id or post_id in seen_ids:
                    continue

                # Lấy text content
                text = ""
                # Thử nhiều selector cho nội dung
                for sel in [
                    'div[data-ad-comet-preview="message"]',
                    'div[data-ad-preview="message"]',
                    'div[dir="auto"]',
                ]:
                    text_els = el.query_selector_all(sel)
                    if text_els:
                        parts = [t.inner_text() for t in text_els if t.inner_text().strip()]
                        if parts:
                            text = "\n".join(parts)
                            break

                if not text:
                    # Fallback: lấy toàn bộ text trong article
                    text = el.inner_text()

                if not text.strip():
                    continue

                # Lấy tác giả
                author = ""
                # Tìm link profile trong phần header
                author_links = el.query_selector_all(
                    'a[role="link"][href*="facebook.com"]'
                )
                for a_el in author_links:
                    a_text = a_el.inner_text().strip()
                    href = a_el.get_attribute("href") or ""
                    # Bỏ qua link "Xem thêm", link nhóm, link bình luận
                    if (a_text and len(a_text) > 1 and len(a_text) < 50
                            and "/groups/" not in href
                            and "comment" not in href.lower()):
                        author = a_text
                        break

                # Build post URL
                post_url = permalink
                if not post_url and post_id:
                    # Reconstruct from group URL
                    gid = re.search(r"/groups/(\d+)", group_url)
                    if gid:
                        post_url = f"https://www.facebook.com/groups/{gid.group(1)}/posts/{post_id}/"

                # Lấy comments
                comments: list[dict] = []
                if scrape_comments:
                    comments = _extract_comments(el)

                post_data = {
                    "postId": post_id,
                    "postUrl": post_url,
                    "text": text.strip(),
                    "authorName": author,
                    "groupName": group_name,
                    "comments": comments,
                }

                posts.append(post_data)
                seen_ids.add(post_id)
                new_in_scroll += 1

            except Exception as e:
                logger.debug("Lỗi extract post: %s", e)
                continue

        if new_in_scroll == 0:
            no_new_count += 1
            if no_new_count >= max_no_new:
                logger.info(
                    "Dừng scroll sau %d lần không có bài mới. Tổng: %d bài.",
                    max_no_new, len(posts),
                )
                break
        else:
            no_new_count = 0

        # Scroll xuống
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000 + (scroll_i % 3) * 500)  # 2-3.5s delay

        # Click "Xem thêm" buttons if present
        try:
            see_more = page.query_selector_all(
                'div[role="button"]:has-text("Xem thêm"), '
                'span:has-text("Xem thêm")'
            )
            for btn in see_more[:3]:
                try:
                    btn.click(timeout=1000)
                    page.wait_for_timeout(500)
                except Exception:
                    pass
        except Exception:
            pass

        logger.debug(
            "Scroll %d: %d bài mới, tổng %d/%d",
            scroll_i + 1, new_in_scroll, len(posts), max_posts,
        )

    logger.info("Hoàn thành nhóm %s: %d bài viết.", group_name, len(posts))
    return posts


def _extract_comments(post_el) -> list[dict]:
    """Trích xuất comments từ một bài viết."""
    comments: list[dict] = []
    try:
        # Tìm comment containers
        comment_els = post_el.query_selector_all(
            'div[role="article"] div[role="article"], '
            'ul li div[dir="auto"]'
        )
        seen_texts: set[str] = set()
        for i, cel in enumerate(comment_els[:20]):  # max 20 comments
            try:
                ctext = cel.inner_text().strip()
                if not ctext or len(ctext) < 5 or ctext in seen_texts:
                    continue
                seen_texts.add(ctext)

                cauthor = ""
                cauthor_el = cel.query_selector('a[role="link"]')
                if cauthor_el:
                    cauthor = cauthor_el.inner_text().strip()

                comments.append({
                    "text": ctext,
                    "authorName": cauthor or "Unknown",
                    "commentId": f"cmt_{i}",
                })
            except Exception:
                continue
    except Exception:
        pass
    return comments


# ---------------------------------------------------------------------------
# Public API — drop-in replacement for Apify fetch_posts()
# ---------------------------------------------------------------------------

def fetch_posts_playwright() -> list[dict]:
    """Scrape Facebook Groups bằng Playwright. Trả về format giống Apify."""
    cookie_raw = ""
    cookie_source = "none"
    db = SessionLocal()
    try:
        group_urls = get_group_urls(db)
        cookie_raw, cookie_source = get_runtime_fb_cookie(db)
    finally:
        db.close()

    if not cookie_raw:
        raise RuntimeError(
            "Chưa có cookie Facebook runtime. "
            "Cập nhật qua API /api/settings/fb-cookie."
        )

    if not group_urls:
        raise RuntimeError("Chưa có group trong DB. Hãy thêm group ở /api/groups.")

    cookies = _parse_cookies(cookie_raw)
    if not cookies:
        raise RuntimeError("Không thể parse FB_COOKIE. Kiểm tra lại format.")

    logger.info("Playwright dùng cookie source=%s", cookie_source)

    cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_TO_SCRAPE)
    all_posts: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="vi-VN",
        )

        # Add cookies
        context.add_cookies(cookies)

        for group_url in group_urls:
            try:
                page = context.new_page()

                # Block heavy resources to speed up
                page.route(
                    re.compile(r"\.(woff2?|ttf|otf)(\?|$)"),
                    lambda route: route.abort(),
                )

                logger.info("Đang mở nhóm: %s", group_url)
                page.goto(group_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)

                # Kiểm tra xem có bị redirect về login không
                current_url = page.url
                if "login" in current_url or "checkpoint" in current_url:
                    logger.warning(
                        "Bị redirect về trang login. Cookie có thể đã hết hạn. URL: %s",
                        current_url,
                    )
                    page.close()
                    continue

                # Đóng popup nếu có
                try:
                    close_btns = page.query_selector_all(
                        'div[aria-label="Đóng"], div[aria-label="Close"]'
                    )
                    for btn in close_btns:
                        btn.click(timeout=1000)
                        page.wait_for_timeout(500)
                except Exception:
                    pass

                group_posts = _extract_posts_from_page(
                    page=page,
                    group_url=group_url,
                    max_posts=MAX_POSTS_PER_GROUP,
                    cutoff=cutoff,
                    scrape_comments=SCRAPE_COMMENTS,
                )
                all_posts.extend(group_posts)
                page.close()

            except Exception as e:
                logger.error("Lỗi scrape nhóm %s: %s", group_url, e)
                continue

        browser.close()

    logger.info("Tổng cộng lấy được %d bài viết từ %d nhóm.",
                len(all_posts), len(group_urls))
    return all_posts


# ---------------------------------------------------------------------------
# Comment enrichment — bổ sung comments cho posts từ Apify
# ---------------------------------------------------------------------------

def _extract_comments_from_post_page(page: Page) -> list[dict]:
    """Trích xuất comments từ trang chi tiết bài viết."""
    comments: list[dict] = []
    seen_texts: set[str] = set()

    # Mở rộng tất cả comments nếu có
    for _ in range(8):
        try:
            expand_btns = page.query_selector_all(
                'div[role="button"]:has-text("Xem thêm bình luận"), '
                'div[role="button"]:has-text("View more comments"), '
                'div[role="button"]:has-text("bình luận trước"), '
                'div[role="button"]:has-text("Tất cả bình luận"), '
                'div[role="button"]:has-text("All comments")'
            )
            if not expand_btns:
                break
            for btn in expand_btns[:2]:
                btn.click(timeout=2000)
                page.wait_for_timeout(1500)
        except Exception:
            break

    # Click "Xem thêm" in individual comments
    try:
        see_more_btns = page.query_selector_all(
            'div[role="button"]:has-text("Xem thêm")'
        )
        for btn in see_more_btns[:10]:
            try:
                btn.click(timeout=1000)
                page.wait_for_timeout(300)
            except Exception:
                pass
    except Exception:
        pass

    # Scroll nhẹ để nạp thêm comments
    try:
        for _ in range(3):
            page.mouse.wheel(0, 1500)
            page.wait_for_timeout(500)
    except Exception:
        pass

    # Extract comment elements (ưu tiên selector hẹp cho comment list)
    selectors = [
        'div[aria-label*="Bình luận"] ul li',
        'div[aria-label*="Comment"] ul li',
        'ul[role="list"] > li',
    ]
    comment_containers = []
    for sel in selectors:
        comment_containers = page.query_selector_all(sel)
        if comment_containers:
            break

    for i, container in enumerate(comment_containers[:120]):
        try:
            # Lấy text
            text_parts = []
            text_els = container.query_selector_all('div[dir="auto"]')
            for te in text_els:
                t = te.inner_text().strip()
                if t and len(t) > 2 and len(t) < 500:
                    text_parts.append(t)

            if not text_parts:
                continue

            ctext = " ".join(text_parts)

            # Bỏ qua text trùng hoặc quá ngắn
            if len(ctext) < 5 or ctext in seen_texts:
                continue

            # Bỏ qua text nhiều dòng UI không phải comment thực
            if "Thích" in ctext and "Phản hồi" in ctext and len(ctext) > 220:
                continue

            seen_texts.add(ctext)

            # Lấy tác giả
            cauthor = ""
            author_el = container.query_selector('h3 a, a[role="link"] > span, a[role="link"]')
            if author_el:
                cauthor = author_el.inner_text().strip()[:50]

            comments.append({
                "text": ctext,
                "authorName": cauthor or "Unknown",
                "commentId": f"cmt_{len(comments)}",
            })
        except Exception:
            continue

    return comments


def enrich_posts_with_comments(posts: list[dict], max_enrich: int = 30) -> list[dict]:
    """Dùng Playwright mở từng bài viết có comments để lấy nội dung comment.

    Args:
        posts: Danh sách bài từ Apify (có postUrl, commentsCount).
        max_enrich: Số bài tối đa để mở (tránh quá lâu).

    Returns:
        Cùng danh sách posts, với key 'comments' được bổ sung.
    """
    db = SessionLocal()
    try:
        cookie_raw, _ = get_runtime_fb_cookie(db)
    finally:
        db.close()

    if not cookie_raw:
        return posts

    cookies = _parse_cookies(cookie_raw)
    if not cookies:
        return posts

    # Lọc bài cần enrich (có commentsCount > 0 và có postUrl)
    to_enrich = [
        (i, p) for i, p in enumerate(posts)
        if p.get("commentsCount", 0) > 0
        and p.get("postUrl", "").startswith("http")
        and not p.get("comments")  # chưa có comments
    ]

    if not to_enrich:
        logger.info("Không có bài nào cần bổ sung comments.")
        return posts

    to_enrich = to_enrich[:max_enrich]
    logger.info(
        "Bổ sung comments cho %d/%d bài bằng Playwright…",
        len(to_enrich), len(posts),
    )

    total_comments = 0

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ],
            )

            context = browser.new_context(
                viewport={"width": 1280, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="vi-VN",
            )
            context.add_cookies(cookies)

            page = context.new_page()

            # Block heavy resources
            page.route(
                re.compile(r"\.(woff2?|ttf|otf)(\?|$)"),
                lambda route: route.abort(),
            )

            for idx, post in to_enrich:
                post_url = post["postUrl"]
                try:
                    page.goto(post_url, wait_until="domcontentloaded", timeout=20000)
                    page.wait_for_timeout(2500)

                    # Kiểm tra login redirect
                    if "login" in page.url:
                        logger.warning("Cookie hết hạn khi bổ sung comments.")
                        break

                    comments = _extract_comments_from_post_page(page)
                    if comments:
                        posts[idx]["comments"] = comments
                        total_comments += len(comments)
                        logger.debug(
                            "Post %s: %d comments",
                            post.get("postId", "?"), len(comments),
                        )
                except Exception as e:
                    logger.debug("Lỗi enrich post %s: %s", post_url, e)
                    continue

            browser.close()

    except Exception as e:
        logger.error("Lỗi Playwright khi bổ sung comments: %s", e)

    logger.info("Bổ sung xong: %d comments từ %d bài.", total_comments, len(to_enrich))
    return posts
