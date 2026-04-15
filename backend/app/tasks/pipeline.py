"""Pipeline: scrape → extract → filter → sync DB."""

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.price_record import PriceRecord
from app.models.schemas import PriceItem
from app.services.scraper import fetch_posts
from app.services.extractor import extract_all, filter_results, estimate_price_ty

logger = logging.getLogger(__name__)


def run_pipeline(
    db: Session,
    use_ai: bool = False,
) -> tuple[list[PriceItem], int, int, int]:
    """Chạy pipeline scrape → extract → sync DB (không lọc, lọc ở client).
    Returns (all_items_in_db, raw_count, new_count, skipped_count).
    """
    # --- 1. Thu thập bài viết ---
    posts = fetch_posts()

    if not posts:
        all_records = db.query(PriceRecord).order_by(PriceRecord.id.desc()).all()
        return [PriceItem.model_validate(r) for r in all_records], 0, 0, 0

    # --- 1b. Bổ sung comments bằng Playwright nếu Apify không trả về ---
    has_comments = any(p.get("comments") for p in posts)
    if not has_comments:
        try:
            from app.services.fb_playwright import enrich_posts_with_comments
            posts = enrich_posts_with_comments(posts)
        except ImportError:
            logger.warning("Playwright chưa cài — bỏ qua bổ sung comments.")
        except Exception as e:
            logger.warning("Lỗi bổ sung comments: %s", e)

    posts_with_text = [
        p for p in posts if (p.get("text") or p.get("message") or "").strip()
    ]
    logger.info("Có %d/%d bài có nội dung text.", len(posts_with_text), len(posts))
    if not posts_with_text:
        all_records = db.query(PriceRecord).order_by(PriceRecord.id.desc()).all()
        return [PriceItem.model_validate(r) for r in all_records], 0, 0, 0

    # --- 2. Trích xuất ---
    all_results = extract_all(posts_with_text, use_ai=use_ai)
    raw_count = len(all_results)

    # --- Log chi tiết trước khi lọc ---
    for i, r in enumerate(all_results, 1):
        est = estimate_price_ty(r.text_snippet)
        logger.info(
            "[PRE-FILTER %d/%d] type=%s source=%s author=%s phone=%s "
            "price_ty=%s price_tr_m2=%s area=%s est=%.2f tỷ | text=%s",
            i, raw_count, r.post_type, r.source, r.author,
            r.phone or "(không)", r.price_ty or "-", r.price_tr_m2 or "-",
            r.area or "-", est if est else 0,
            r.text_snippet[:120].replace("\n", " "),
        )

    # --- 3. Không lọc ở backend (lọc hoàn toàn ở client) ---
    results = filter_results(all_results, require_phone=False)
    logger.info("Sau lọc (không theo giá): %d/%d mục.", len(results), raw_count)

    # Thêm estimated_price_ty
    for r in results:
        r.estimated_price_ty = estimate_price_ty(r.text_snippet)

    # --- 4. Lưu vào DB (chỉ insert bản ghi chưa tồn tại) ---
    session_id = datetime.now().isoformat()

    # Lấy tất cả post_id + source + post_type + link đã có trong DB
    # Thêm `link` để không gộp nhầm nhiều comment của cùng 1 post.
    existing_keys: set[tuple[str, str, str, str]] = set()
    existing_rows = db.query(
        PriceRecord.post_id, PriceRecord.source, PriceRecord.post_type, PriceRecord.link,
    ).all()
    for row in existing_rows:
        existing_keys.add((row.post_id, row.source, row.post_type, row.link or ""))

    new_records = []
    skipped = 0
    for r in results:
        key = (r.post_id, r.source, r.post_type, r.link or "")
        if key in existing_keys:
            skipped += 1
            continue

        rec = PriceRecord(
            scrape_session=session_id,
            post_id=r.post_id,
            group_name=r.group_name,
            post_type=r.post_type,
            source=r.source,
            link=r.link,
            author=r.author,
            phone=r.phone,
            text_snippet=r.text_snippet,
            price_ty=r.price_ty,
            price_tr_m2=r.price_tr_m2,
            price_trieu=r.price_trieu,
            area=r.area,
            location=r.location,
            ai_summary=r.ai_summary,
            estimated_price_ty=r.estimated_price_ty,
        )
        new_records.append(rec)
        existing_keys.add(key)

    if new_records:
        db.add_all(new_records)
        db.commit()

    logger.info(
        "Đồng bộ xong: %d mới, %d trùng bỏ qua, %d tổng trước lọc (session %s).",
        len(new_records), skipped, raw_count, session_id,
    )

    # Trả về TOÀN BỘ dữ liệu trong DB
    all_records = db.query(PriceRecord).order_by(PriceRecord.id.desc()).all()
    return (
        [PriceItem.model_validate(rec) for rec in all_records],
        raw_count,
        len(new_records),
        skipped,
    )
