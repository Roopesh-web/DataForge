from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.quality_service import QualityService, get_quality_service

client = TestClient(app)
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def quality_upload_dir(tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    sample_file = FIXTURES_DIR / "sample.csv"
    (upload_dir / "stored_sample.csv").write_bytes(sample_file.read_bytes())

    service = QualityService(upload_dir=upload_dir)
    app.dependency_overrides[get_quality_service] = lambda: service
    yield upload_dir
    app.dependency_overrides.clear()


def test_quality_check_api_success(quality_upload_dir):
    response = client.post(
        "/quality-check",
        json={"stored_filename": "stored_sample.csv"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stored_filename"] == "stored_sample.csv"
    assert body["validation_summary"]["total_rules"] > 0
    assert "quality_score" in body["validation_summary"]
    assert isinstance(body["failed_rules"], list)
    assert isinstance(body["passed_rules"], list)
    assert "validation_report" in body


def test_quality_check_api_file_not_found(quality_upload_dir):
    response = client.post(
        "/quality-check",
        json={"stored_filename": "missing.csv"},
    )

    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"
