from app.db.base import Base
from app.db.session import engine as default_engine
from app.models.warehouse import DatasetMetadata, UploadHistory, WarehouseLoadHistory

__all__ = [
    "ensure_metadata_tables",
]


def ensure_metadata_tables(db_engine: Engine | None = None) -> None:
    target_engine = db_engine or default_engine
    Base.metadata.create_all(
        bind=target_engine,
        tables=[
            UploadHistory.__table__,
            DatasetMetadata.__table__,
            WarehouseLoadHistory.__table__,
        ],
    )
