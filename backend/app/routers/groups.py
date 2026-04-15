"""Router: quản lý danh sách Facebook Groups."""

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.fb_group import FBGroup
from app.services.group_store import (
    add_group as add_group_db,
    list_groups as list_groups_db,
    normalize_group_url,
    is_valid_group_url,
    remove_group as remove_group_db,
)

router = APIRouter(prefix="/api", tags=["groups"])


class GroupItem(BaseModel):
    url: str
    name: str | None = None


class GroupListResponse(BaseModel):
    groups: list[GroupItem]
    count: int


def _to_response(rows: list[FBGroup]) -> GroupListResponse:
    groups = [GroupItem(url=row.url, name=row.name or None) for row in rows]
    return GroupListResponse(groups=groups, count=len(groups))


@router.get("/groups", response_model=GroupListResponse)
def list_groups(db: Session = Depends(get_db)):
    """Trả về danh sách groups hiện tại."""
    rows = list_groups_db(db)
    return _to_response(rows)


@router.post("/groups", response_model=GroupListResponse)
def add_group(url: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """Thêm group mới vào danh sách."""
    url = normalize_group_url(url)
    if not is_valid_group_url(url):
        raise HTTPException(400, "URL không hợp lệ. Cần URL Facebook Group.")

    existed = db.query(FBGroup).filter(FBGroup.url == url).first()
    if existed:
        raise HTTPException(409, "Group đã tồn tại trong danh sách.")

    add_group_db(db, url)
    return _to_response(list_groups_db(db))


@router.delete("/groups", response_model=GroupListResponse)
def remove_group(url: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """Xoá group khỏi danh sách."""
    url = normalize_group_url(url)
    ok = remove_group_db(db, url)
    if not ok:
        raise HTTPException(404, "Group không tồn tại trong danh sách.")

    return _to_response(list_groups_db(db))
