"""Helpers for runtime settings stored in DB."""

import json

from sqlalchemy.orm import Session

from app.config import FB_COOKIE
from app.models.app_setting import AppSetting

FB_COOKIE_KEY = "fb_cookie"


def get_setting(db: Session, key: str) -> str:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    return row.value if row and row.value else ""


def set_setting(db: Session, key: str, value: str) -> None:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    if row:
        row.value = value
    else:
        db.add(AppSetting(key=key, value=value))
    db.commit()


def delete_setting(db: Session, key: str) -> bool:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


def _normalize_cookie(raw_cookie: str) -> str:
    raw_cookie = (raw_cookie or "").strip()
    if not raw_cookie:
        return ""

    try:
        parsed = json.loads(raw_cookie)
        if isinstance(parsed, list):
            return json.dumps(parsed, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        pass

    return raw_cookie


def set_fb_cookie(db: Session, raw_cookie: str) -> str:
    cookie = _normalize_cookie(raw_cookie)
    if not cookie:
        raise ValueError("Cookie rỗng")
    set_setting(db, FB_COOKIE_KEY, cookie)
    return cookie


def get_runtime_fb_cookie(db: Session) -> tuple[str, str]:
    cookie_db = get_setting(db, FB_COOKIE_KEY)
    if cookie_db:
        return cookie_db, "db"
    if FB_COOKIE:
        return FB_COOKIE, "env"
    return "", "none"


def seed_fb_cookie_from_env_if_empty(db: Session) -> bool:
    existing = get_setting(db, FB_COOKIE_KEY)
    if existing or not FB_COOKIE:
        return False
    set_setting(db, FB_COOKIE_KEY, _normalize_cookie(FB_COOKIE))
    return True
