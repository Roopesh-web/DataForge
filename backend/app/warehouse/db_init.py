from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import get_logger
from app.db.base import Base
from app.db.session import engine as default_engine
from app.models.warehouse import DatasetMetadata, UploadHistory, WarehouseLoadHistory

logger = get_logger("warehouse.db_init")

__all__ = [
    "ensure_metadata_tables",
]


def ensure_metadata_tables(db_engine: Engine | None = None) -> bool:
    target_engine = db_engine or default_engine
    try:
        Base.metadata.create_all(
            bind=target_engine,
            tables=[
                UploadHistory.__table__,
                DatasetMetadata.__table__,
                WarehouseLoadHistory.__table__,
            ],
        )
        return True
    except SQLAlchemyError as exc:
        logger.warning("Could not ensure warehouse metadata tables: {}", exc)
        return False
