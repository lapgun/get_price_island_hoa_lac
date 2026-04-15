"""Group store helpers (DB-backed)."""

import re

from sqlalchemy.orm import Session

from app.models.fb_group import FBGroup


def normalize_group_url(url: str) -> str:
    """Chuẩn hóa URL group Facebook."""
    url = (url or "").strip()
    url = re.sub(r"[?#].*$", "", url).rstrip("/")
    return url


def extract_group_name(url: str) -> str:
    """Trích slug/ID group từ URL."""
    m = re.search(r"facebook\.com/groups/([^/?]+)", url)
    return m.group(1) if m else url


def is_valid_group_url(url: str) -> bool:
    return bool(re.match(r"https?://.*facebook\.com/groups/", url or ""))


def list_groups(db: Session) -> list[FBGroup]:
    return db.query(FBGroup).order_by(FBGroup.id.asc()).all()


def get_group_urls(db: Session) -> list[str]:
    return [g.url for g in list_groups(db)]


def add_group(db: Session, url: str) -> FBGroup:
    url = normalize_group_url(url)
    group = FBGroup(url=url, name=extract_group_name(url))
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def remove_group(db: Session, url: str) -> bool:
    url = normalize_group_url(url)
    row = db.query(FBGroup).filter(FBGroup.url == url).first()
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


def seed_groups_if_empty(db: Session, urls: list[str]) -> int:
    """Seed initial groups from ENV only when table is empty."""
    if db.query(FBGroup).count() > 0:
        return 0

    added = 0
    seen: set[str] = set()
    for raw_url in urls:
        url = normalize_group_url(raw_url)
        if not url or url in seen or not is_valid_group_url(url):
            continue
        seen.add(url)
        db.add(FBGroup(url=url, name=extract_group_name(url)))
        added += 1

    if added:
        db.commit()
    return added
