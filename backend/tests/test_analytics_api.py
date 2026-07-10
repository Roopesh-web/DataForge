from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.analytics_service import AnalyticsService, get_analytics_service

client = TestClient(app)
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def analytics_upload_dir(tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    sample_file = FIXTURES_DIR / "sample.csv"
    (upload_dir / "stored_sample.csv").write_bytes(sample_file.read_bytes())

    service = AnalyticsService(upload_dir=upload_dir)
    app.dependency_overrides[get_analytics_service] = lambda: service
    yield upload_dir
    app.dependency_overrides.clear()


def test_analytics_api_success(analytics_upload_dir):
    response = client.post(
        "/analytics",
        json={"stored_filename": "stored_sample.csv"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stored_filename"] == "stored_sample.csv"
    assert body["dataset_summary"]["rows"] == 4
    assert body["dataset_summary"]["columns"] == 5
    assert "amount" in body["dataset_summary"]["numeric_columns"]
    assert "amount" in body["numeric_statistics"]
    assert body["numeric_statistics"]["amount"]["max"] == 300.0
    assert body["outlier_detection"]["amount"]["method"] == "IQR"
    assert body["correlation_matrix"]["columns"] == ["id", "amount"]
    assert "name" in body["categorical_statistics"]
    assert body["missing_values"]["count"] >= 0


def test_analytics_api_file_not_found(analytics_upload_dir):
    response = client.post(
        "/analytics",
        json={"stored_filename": "missing.csv"},
    )

    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"
