from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import check_database_connection, engine
from app.utils.error_handlers import RequestIDMiddleware, register_exception_handlers
from app.warehouse.db_init import ensure_metadata_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(
        "Starting {} v{} | env={}",
        settings.app_name,
        settings.app_version,
        settings.app_env,
    )

    settings.upload_path.mkdir(parents=True, exist_ok=True)

    if check_database_connection():
        logger.info("Database connection verified")
        if ensure_metadata_tables(engine):
            logger.info("Warehouse metadata tables verified")
        else:
            logger.warning("Warehouse metadata tables could not be created at startup")
    else:
        logger.warning("Database connection could not be verified at startup")

    yield

    engine.dispose()
    logger.info("Shutting down {}", settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description=(
            "DataForge is an enterprise-grade data platform. "
            "Phase 1 provides the core API foundation with health checks and file uploads."
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    register_exception_handlers(app)

    app.include_router(api_router)

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app()
