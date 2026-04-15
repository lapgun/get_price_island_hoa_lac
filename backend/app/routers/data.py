"""Router: truy vấn dữ liệu từ DB."""

from fastapi import APIRouter, Query, Depends
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.price_record import PriceRecord
from app.models.schemas import PriceItem, DataResponse, StatsResponse

router = APIRouter(prefix="/api", tags=["data"])


@router.get("/data", response_model=DataResponse)
def get_data(
    post_type: str = Query(default=None),
    has_phone: bool = Query(default=None),
    location: str = Query(default=None),
    session: str = Query(default=None, description="Lọc theo scrape session"),
    db: Session = Depends(get_db),
):
    """Trả toàn bộ dữ liệu từ DB."""
    q = db.query(PriceRecord)

    if session:
        q = q.filter(PriceRecord.scrape_session == session)
    if post_type:
        q = q.filter(PriceRecord.post_type == post_type)
    if has_phone is True:
        q = q.filter(PriceRecord.phone != "")
    if location:
        q = q.filter(PriceRecord.location.ilike(f"%{location}%"))

    q = q.order_by(PriceRecord.id.desc())
    records = q.all()

    latest = db.query(func.max(PriceRecord.scrape_session)).scalar()

    return DataResponse(
        count=len(records),
        scraped_at=latest,
        data=[PriceItem.model_validate(r) for r in records],
    )


@router.get("/stats", response_model=StatsResponse)
def stats(db: Session = Depends(get_db)):
    """Thống kê nhanh."""
    total = db.query(func.count(PriceRecord.id)).scalar() or 0
    if total == 0:
        return StatsResponse()

    latest = db.query(func.max(PriceRecord.scrape_session)).scalar()

    type_rows = (
        db.query(PriceRecord.post_type, func.count(PriceRecord.id))
        .group_by(PriceRecord.post_type)
        .all()
    )
    by_type = {t: c for t, c in type_rows}

    loc_rows = (
        db.query(PriceRecord.location, func.count(PriceRecord.id))
        .group_by(PriceRecord.location)
        .all()
    )
    by_location = {(loc or "không rõ"): c for loc, c in loc_rows}

    sessions = [
        s[0]
        for s in db.query(distinct(PriceRecord.scrape_session))
        .order_by(PriceRecord.scrape_session.desc())
        .limit(20)
        .all()
    ]

    return StatsResponse(
        scraped_at=latest,
        total=total,
        raw_count=total,
        by_type=by_type,
        by_location=by_location,
        sessions=sessions,
    )
