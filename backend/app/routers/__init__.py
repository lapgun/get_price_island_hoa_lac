from app.routers.scrape import router as scrape_router
from app.routers.data import router as data_router
from app.routers.groups import router as groups_router
from app.routers.settings import router as settings_router

__all__ = ["scrape_router", "data_router", "groups_router", "settings_router"]

