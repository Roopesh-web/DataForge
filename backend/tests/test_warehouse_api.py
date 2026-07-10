from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.main import app
from app.services.warehouse_service import WarehouseService, get_warehouse_service

client = TestClient(app)
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def warehouse_upload_dir(tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    sample_file = FIXTURES_DIR / "sample.csv"
    (upload_dir / "stored_sample.csv").write_bytes(sample_file.read_bytes())

    db_path = tmp_path / "warehouse_api_test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    service = WarehouseService(
        upload_dir=upload_dir,
        session_factory=session_factory,
        db_engine=engine,
    )
    app.dependency_overrides[get_warehouse_service] = lambda: service
    yield upload_dir
    app.dependency_overrides.clear()


def test_warehouse_load_api_success(warehouse_upload_dir):
    response = client.post(
        "/warehouse/load",
        json={"stored_filename": "stored_sample.csv"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["rows_loaded"] == 4
    assert body["table_name"].startswith("wh_")
    assert body["duration_ms"] >= 0


def test_warehouse_history_api(warehouse_upload_dir):
    client.post("/warehouse/load", json={"stored_filename": "stored_sample.csv"})
    response = client.get("/warehouse/history")

    assert response.status_code == 200
    body = response.json()
    assert len(body["loads"]) == 1
    assert body["loads"][0]["status"] == "success"
    assert body["loads"][0]["rows_loaded"] == 4


def test_warehouse_load_api_file_not_found(warehouse_upload_dir):
    response = client.post(
        "/warehouse/load",
        json={"stored_filename": "missing.csv"},
    )

    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"
