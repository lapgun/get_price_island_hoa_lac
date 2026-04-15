"""Router: runtime settings (FB cookie)."""

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.app_setting import AppSetting
from app.services.runtime_settings import (
    FB_COOKIE_KEY,
    delete_setting,
    get_runtime_fb_cookie,
    set_fb_cookie,
)

router = APIRouter(prefix="/api/settings", tags=["settings"])


class FBCookieUpdateRequest(BaseModel):
    cookie: str


class FBCookieStatusResponse(BaseModel):
    has_cookie: bool
    source: str
    updated_at: str | None = None


@router.get("/fb-cookie", response_model=FBCookieStatusResponse)
def get_fb_cookie_status(db: Session = Depends(get_db)):
    cookie, source = get_runtime_fb_cookie(db)
    row = db.query(AppSetting).filter(AppSetting.key == FB_COOKIE_KEY).first()
    return FBCookieStatusResponse(
        has_cookie=bool(cookie),
        source=source,
        updated_at=row.updated_at.isoformat() if row else None,
    )


@router.put("/fb-cookie", response_model=FBCookieStatusResponse)
def update_fb_cookie(payload: FBCookieUpdateRequest, db: Session = Depends(get_db)):
    try:
        set_fb_cookie(db, payload.cookie)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    row = db.query(AppSetting).filter(AppSetting.key == FB_COOKIE_KEY).first()
    return FBCookieStatusResponse(
        has_cookie=True,
        source="db",
        updated_at=row.updated_at.isoformat() if row else None,
    )


@router.delete("/fb-cookie", response_model=FBCookieStatusResponse)
def clear_fb_cookie(db: Session = Depends(get_db)):
    delete_setting(db, FB_COOKIE_KEY)
    cookie, source = get_runtime_fb_cookie(db)
    row = db.query(AppSetting).filter(AppSetting.key == FB_COOKIE_KEY).first()
    return FBCookieStatusResponse(
        has_cookie=bool(cookie),
        source=source,
        updated_at=row.updated_at.isoformat() if row else None,
    )
