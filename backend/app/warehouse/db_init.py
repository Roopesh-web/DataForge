from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import get_logger
from app.db.base import Base
from app.db.session import engine as default_engine
from app.models.warehouse import DatasetMetadata, UploadHistory, WarehouseLoadHistory
from app.db.schema_setup import (
    APPLICATION_SCHEMA,
    ensure_application_schema,
    uses_application_schema,
)

logger = get_logger("warehouse.db_init")

METADATA_TABLES = (
    UploadHistory.__table__,
    DatasetMetadata.__table__,
    WarehouseLoadHistory.__table__,
)

__all__ = [
    "ensure_metadata_tables",
]


def _metadata_tables_exist(db_engine: Engine) -> bool:
    inspector = inspect(db_engine)
    schema = APPLICATION_SCHEMA if uses_application_schema(db_engine) else None
    for table in METADATA_TABLES:
        if not inspector.has_table(table.name, schema=schema):
            # Fallback: honor search_path / default schema lookups.
            if schema and inspector.has_table(table.name):
                continue
            return False
    return True


def ensure_metadata_tables(db_engine: Engine | None = None) -> bool:
    """Create warehouse metadata tables if they do not already exist."""
    target_engine = db_engine or default_engine
    try:
        ensure_application_schema(target_engine)

        if uses_application_schema(target_engine):
            # Create tables inside the application schema explicitly so DDL does
            # not attempt CREATE in the restricted ``public`` schema.
            with target_engine.begin() as connection:
                connection.execute(
                    text(f'SET LOCAL search_path TO "{APPLICATION_SCHEMA}", public')
                )
                Base.metadata.create_all(
                    bind=connection,
                    tables=list(METADATA_TABLES),
                )
        else:
            Base.metadata.create_all(
                bind=target_engine,
                tables=list(METADATA_TABLES),
            )

        if not _metadata_tables_exist(target_engine):
            logger.warning(
                "Warehouse metadata tables are still missing after create_all | schema={}",
                APPLICATION_SCHEMA if uses_application_schema(target_engine) else "default",
            )
            return False

        logger.info(
            "Warehouse metadata tables verified | tables={}",
            ", ".join(table.name for table in METADATA_TABLES),
        )
        return True
    except SQLAlchemyError as exc:
        logger.warning("Could not ensure warehouse metadata tables: {}", exc)
        return False
