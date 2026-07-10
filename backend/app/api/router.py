from fastapi import APIRouter

from app.api import health, profiling, upload

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(upload.router)
api_router.include_router(profiling.router)
