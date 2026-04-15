"""SQLAlchemy ORM model – bảng price_records."""

from datetime import datetime

from sqlalchemy import Integer, Float, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PriceRecord(Base):
    __tablename__ = "price_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scrape_session: Mapped[str] = mapped_column(String(50), index=True)
    post_id: Mapped[str] = mapped_column(String(100), default="")
    group_name: Mapped[str] = mapped_column(String(300), default="")
    post_type: Mapped[str] = mapped_column(String(30), default="", index=True)
    source: Mapped[str] = mapped_column(String(20), default="")
    link: Mapped[str] = mapped_column(Text, default="")
    author: Mapped[str] = mapped_column(String(200), default="")
    phone: Mapped[str] = mapped_column(String(100), default="", index=True)
    text_snippet: Mapped[str] = mapped_column(Text, default="")
    price_ty: Mapped[str] = mapped_column(String(50), default="")
    price_tr_m2: Mapped[str] = mapped_column(String(50), default="")
    price_trieu: Mapped[str] = mapped_column(String(50), default="")
    area: Mapped[str] = mapped_column(String(50), default="")
    location: Mapped[str] = mapped_column(String(100), default="", index=True)
    ai_summary: Mapped[str] = mapped_column(Text, default="")
    estimated_price_ty: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
