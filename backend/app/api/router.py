from fastapi import APIRouter

from app.api import analytics, health, profiling, quality, upload, warehouse

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(upload.router)
api_router.include_router(profiling.router)
api_router.include_router(analytics.router)
api_router.include_router(quality.router)
api_router.include_router(warehouse.router)
