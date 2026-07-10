from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.profiling_service import ProfilingService, get_profiling_service

client = TestClient(app)
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def profiling_upload_dir(tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    sample_file = FIXTURES_DIR / "sample.csv"
    (upload_dir / "stored_sample.csv").write_bytes(sample_file.read_bytes())

    service = ProfilingService(upload_dir=upload_dir)
    app.dependency_overrides[get_profiling_service] = lambda: service
    yield upload_dir
    app.dependency_overrides.clear()


def test_profile_api_success(profiling_upload_dir):
    response = client.post(
        "/profile",
        json={"stored_filename": "stored_sample.csv"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stored_filename"] == "stored_sample.csv"
    assert body["file_format"] == "csv"
    assert body["row_count"] == 4
    assert body["column_count"] == 5
    assert len(body["columns"]) == 5
    assert body["duplicate_rows"] == 1


def test_profile_api_file_not_found(profiling_upload_dir):
    response = client.post(
        "/profile",
        json={"stored_filename": "missing.csv"},
    )

    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"
