from pathlib import Path

import polars as pl
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.warehouse import DatasetMetadata, UploadHistory, WarehouseLoadHistory
from app.services.warehouse_service import WarehouseService
from app.utils.exceptions import ErrorCode

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def warehouse_service(tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    sample_file = FIXTURES_DIR / "sample.csv"
    (upload_dir / "sample.csv").write_bytes(sample_file.read_bytes())

    db_path = tmp_path / "warehouse_test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    return WarehouseService(
        upload_dir=upload_dir,
        session_factory=session_factory,
        db_engine=engine,
    )


def test_load_uploaded_file_success(warehouse_service):
    response = warehouse_service.load_uploaded_file("sample.csv")

    assert response.status == "success"
    assert response.rows_loaded == 4
    assert response.table_name.startswith("wh_")
    assert response.duration_ms >= 0


def test_load_uploaded_file_persists_metadata(warehouse_service):
    warehouse_service.load_uploaded_file("sample.csv")

    with warehouse_service.session_factory() as session:
        metadata = session.scalar(
            select(DatasetMetadata).where(DatasetMetadata.stored_filename == "sample.csv")
        )
        upload = session.scalar(
            select(UploadHistory).where(UploadHistory.stored_filename == "sample.csv")
        )
        history = session.scalars(select(WarehouseLoadHistory)).all()

    assert metadata is not None
    assert metadata.row_count == 4
    assert metadata.column_count == 5
    assert metadata.quality_score is not None
    assert upload is not None
    assert len(history) == 1
    assert history[0].status == "success"


def test_get_load_history(warehouse_service):
    warehouse_service.load_uploaded_file("sample.csv")
    history = warehouse_service.get_load_history()

    assert len(history.loads) == 1
    assert history.loads[0].table_name.startswith("wh_")
    assert history.loads[0].rows_loaded == 4


def test_get_load_history_empty(warehouse_service):
    history = warehouse_service.get_load_history()

    assert history.loads == []


def test_load_uploaded_file_not_found(warehouse_service):
    with pytest.raises(Exception) as exc_info:
        warehouse_service.load_uploaded_file("missing.csv")

    assert exc_info.value.status_code == 404
    assert exc_info.value.error_code == ErrorCode.NOT_FOUND
