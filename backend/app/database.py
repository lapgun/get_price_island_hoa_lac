"""SQLAlchemy database setup."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://hoalac:hoalac@db:5432/hoalac",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency – yield a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    from app.models.price_record import PriceRecord  # noqa: F401
    from app.models.fb_group import FBGroup  # noqa: F401
    from app.models.app_setting import AppSetting  # noqa: F401
    from app.config import FB_GROUP_URLS
    from app.services.group_store import seed_groups_if_empty
    from app.services.runtime_settings import seed_fb_cookie_from_env_if_empty

    Base.metadata.create_all(bind=engine)

    # Seed groups từ ENV đúng 1 lần nếu bảng fb_groups đang trống.
    db = SessionLocal()
    try:
        seed_groups_if_empty(db, FB_GROUP_URLS)
        seed_fb_cookie_from_env_if_empty(db)
    finally:
        db.close()
