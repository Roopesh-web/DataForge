from app.api.health import router as health_router
from app.api.router import api_router
from app.api.upload import router as upload_router

__all__ = ["api_router", "health_router", "upload_router"]
