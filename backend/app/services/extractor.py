"""Trích xuất giá đất từ nội dung bài viết VÀ comment."""

import logging
import re

from app.config import OPENAI_API_KEY, GEMINI_API_KEY
from app.models.schemas import PriceItem

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

_PAT_TY = re.compile(
    r"(\d+[.,]?\d*)\s*(?:tỷ|ty|đồng)\s*(?:rưỡi|ruoi|\d{1,3})?",
    re.IGNORECASE,
)

_PAT_TY_PARSE = re.compile(
    r"(\d+[.,]?\d*)\s*(?:tỷ|ty|đồng)\s*(?:(rưỡi|ruoi)|(\d{1,3}))?",
    re.IGNORECASE,
)

_PAT_TR_M2 = re.compile(
    r"(\d+[.,x]?\d*)\s*(?:tr|triệu|trieu)\s*/\s*(?:\d\s*)?m[2²]?",
    re.IGNORECASE,
)

_PAT_TRIEU = re.compile(
    r"(\d+[.,]?\d*)\s*(?:triệu|trieu|tr)\b",
    re.IGNORECASE,
)

_PAT_AREA = re.compile(r"(\d+[.,]?\d*)\s*m[2²]", re.IGNORECASE)

_PAT_PHONE = re.compile(r"(?:\+84|0)\s*(?:\d[\s.-]?){8,9}\d")

_PAT_LOCATION = re.compile(
    r"(?:hòa\s*lạc|hoa\s*lac|thạch\s*thất|thach\s*that|quốc\s*oai|quoc\s*oai"
    r"|tân\s*xã|tan\s*xa|đông\s*xuân|dong\s*xuan|bình\s*yên|binh\s*yen"
    r"|thạch\s*hoà|thach\s*hoa|tiến\s*xuân|tien\s*xuan"
    r"|ngọc\s*liệp|đồng\s*trúc|cổ\s*hoạch|sài\s*sơn|yên\s*bình"
    r"|phú\s*cát|phú\s*mãn|đông\s*yên|hạ\s*bằng"
    r"|cẩm\s*yên|cam\s*yen|lại\s*thượng|lai\s*thuong|phú\s*kim|phu\s*kim"
    r"|hoài\s*đức|sơn\s*tây|xuân\s*mai)",
    re.IGNORECASE,
)

_PAT_BUYER = re.compile(
    r"(?:cần\s*mua|muốn\s*mua|tìm\s*mua|ai\s*bán|ai\s*có\s*(?:đất|lô|mảnh)"
    r"|cần\s*tìm\s*(?:mua|đất|lô|mảnh|nhà)"
    r"|tài\s*chính\s*\d|ngân\s*sách"
    r"|ai\s*(?:để|bán)\s*lại"
    r"|mua\s*(?:đất|lô|mảnh|nhà)"
    r"|quay\s*đầu\s*cần\s*mua"
    r"|để\s*lại\s*(?:tt|thông\s*tin)\s*giúp"
    r"|khách\s*cần\s*mua|khách\s*cần\s*tìm"
    r"|muốn\s*tìm\s*mua"
    r"|có\s*ai\s*bán|có\s*(?:đất|lô|mảnh)\s*nào"
    r"|em\s*cần\s*mua|mình\s*cần\s*mua"
    r"|tìm\s*(?:đất|lô|mảnh|nhà)\s*(?:ở|để)"
    r"|hỏi\s*mua|xin\s*(?:giá|thông\s*tin))",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _first_match(pattern: re.Pattern, text: str) -> str:
    m = pattern.search(text)
    return m.group(0).strip() if m else ""


def _all_phones(text: str) -> str:
    phones = _PAT_PHONE.findall(text)
    cleaned = [re.sub(r"[\s.-]", "", p) for p in phones]
    seen: set[str] = set()
    unique: list[str] = []
    for p in cleaned:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return " | ".join(unique)


def _get_author(data: dict) -> str:
    author = (
        data.get("authorName")
        or data.get("author")
        or data.get("userName")
        or ""
    )
    if not author and isinstance(data.get("user"), dict):
        author = data["user"].get("name", "")
    return str(author)


def is_buyer_post(text: str) -> bool:
    return bool(_PAT_BUYER.search(text))


def estimate_price_ty(text: str) -> float | None:
    m = _PAT_TY_PARSE.search(text)
    if m:
        base = float(m.group(1).replace(",", "."))
        if m.group(2):
            return base + 0.5
        if m.group(3):
            frac = int(m.group(3))
            if frac < 10:
                return base + frac * 0.1
            else:
                return base + frac / 1000
        return base

    m = _PAT_TRIEU.search(text)
    if m:
        val = float(m.group(1).replace(",", "."))
        if val >= 100:
            return val / 1000

    m_price = _PAT_TR_M2.search(text)
    m_area = _PAT_AREA.search(text)
    if m_price and m_area:
        price_str = m_price.group(1).replace(",", ".").replace("x", "5")
        area_str = m_area.group(1).replace(",", ".")
        try:
            total_trieu = float(price_str) * float(area_str)
            return total_trieu / 1000
        except ValueError:
            pass
    return None


# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------

def _extract_from_post(post: dict, post_type: str = "bán") -> PriceItem:
    text: str = post.get("text") or post.get("message") or ""
    post_id: str = str(post.get("postId") or post.get("id") or "")
    post_url: str = post.get("postUrl") or ""

    phone = _all_phones(text)
    if not phone:
        phone = _all_phones(str(post.get("contactPhone") or ""))

    return PriceItem(
        post_id=post_id,
        group_name=post.get("groupName") or "",
        post_type=post_type,
        source="bài viết",
        link=post_url,
        author=_get_author(post),
        phone=phone,
        text_snippet=text[:300],
        price_ty=_first_match(_PAT_TY, text),
        price_tr_m2=_first_match(_PAT_TR_M2, text),
        price_trieu=_first_match(_PAT_TRIEU, text),
        area=_first_match(_PAT_AREA, text),
        location=_first_match(_PAT_LOCATION, text),
        ai_summary="",
    )


def _extract_from_comment(comment: dict, post: dict, post_type: str = "bán") -> PriceItem:
    text = (
        comment.get("text")
        or comment.get("message")
        or comment.get("body")
        or ""
    )
    comment_id = str(comment.get("commentId") or comment.get("id") or "")
    post_url = post.get("postUrl") or ""

    cmt_type = "cmt_bài_mua" if post_type == "mua" else "cmt_bài_bán"
    post_text = (post.get("text") or post.get("message") or "").strip()
    parent_label = "BÀI MUA" if post_type == "mua" else "BÀI BÁN"
    comment_with_context = (
        f"[COMMENT CỦA {parent_label}] {text.strip()}"
        f"\n[BÀI GỐC] {post_text[:180]}"
    )

    comment_url = comment.get("commentUrl") or comment.get("url") or ""
    if not comment_url and post_url and comment_id:
        sep = "&" if "?" in post_url else "?"
        comment_url = f"{post_url}{sep}comment_id={comment_id}"
    if not comment_url:
        comment_url = post_url

    return PriceItem(
        post_id=str(post.get("postId") or post.get("id") or ""),
        group_name=post.get("groupName") or "",
        post_type=cmt_type,
        source="comment",
        link=comment_url,
        author=_get_author(comment),
        phone=_all_phones(text),
        text_snippet=comment_with_context[:300],
        price_ty=_first_match(_PAT_TY, text),
        price_tr_m2=_first_match(_PAT_TR_M2, text),
        price_trieu=_first_match(_PAT_TRIEU, text),
        area=_first_match(_PAT_AREA, text),
        location=_first_match(_PAT_LOCATION, text),
        ai_summary="",
    )


# ---------------------------------------------------------------------------
# AI extractor
# ---------------------------------------------------------------------------

_AI_PROMPT = """Bạn là chuyên gia bất động sản Việt Nam. Phân tích đoạn đăng bán đất sau
và trả về JSON với các trường:
- gia_ty: giá tổng (tỷ VNĐ), null nếu không rõ
- gia_trieu_m2: giá trên m² (triệu/m²), null nếu không rõ
- dien_tich_m2: diện tích (m²), null nếu không rõ
- vi_tri: vị trí cụ thể
- mo_ta_ngan: tóm tắt 1 câu

Nội dung:
{text}
"""


def _ask_openai(text: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": _AI_PROMPT.format(text=text[:1500])}],
        temperature=0,
        max_tokens=300,
    )
    return resp.choices[0].message.content or ""


def _ask_gemini(text: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content(_AI_PROMPT.format(text=text[:1500]))
    return resp.text or ""


def _extract_by_ai(post: dict) -> str:
    text: str = post.get("text") or post.get("message") or ""
    if not text:
        return ""
    try:
        if OPENAI_API_KEY:
            return _ask_openai(text)
        if GEMINI_API_KEY:
            return _ask_gemini(text)
    except Exception as exc:
        logger.warning("AI extraction failed: %s", exc)
    return ""


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def filter_results(
    results: list[PriceItem],
    require_phone: bool = True,
) -> list[PriceItem]:
    if not require_phone:
        return results

    filtered: list[PriceItem] = []
    buyer_post_ids: set[str] = set()

    for r in results:
        if r.post_type == "mua" and r.source == "bài viết":
            buyer_post_ids.add(r.post_id)
            filtered.append(r)

    for r in results:
        if r.post_type == "mua" and r.source == "bài viết":
            continue

        if r.post_type == "cmt_bài_mua":
            if r.post_id in buyer_post_ids and r.phone:
                filtered.append(r)
            continue

        if require_phone and not r.phone:
            continue
        filtered.append(r)

    return filtered


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_all(posts: list[dict], use_ai: bool = False) -> list[PriceItem]:
    results: list[PriceItem] = []
    buyer_count = 0
    seller_count = 0
    comment_count = 0

    for post in posts:
        text = post.get("text") or post.get("message") or ""
        is_buyer = is_buyer_post(text)
        post_type = "mua" if is_buyer else "bán"

        if is_buyer:
            buyer_count += 1
        else:
            seller_count += 1

        info = _extract_from_post(post, post_type=post_type)
        if use_ai and info.text_snippet and (OPENAI_API_KEY or GEMINI_API_KEY):
            info.ai_summary = _extract_by_ai(post)
        results.append(info)

        comments = post.get("comments") or []
        for comment in comments:
            ctext = (
                comment.get("text")
                or comment.get("message")
                or comment.get("body")
                or ""
            )
            if not ctext.strip():
                continue
            cinfo = _extract_from_comment(comment, post, post_type=post_type)
            results.append(cinfo)
            comment_count += 1

    logger.info(
        "Trích xuất xong: %d bài bán + %d bài mua + %d comment = %d mục.",
        seller_count, buyer_count, comment_count, len(results),
    )
    return results
