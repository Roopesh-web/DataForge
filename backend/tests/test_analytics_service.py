from pathlib import Path

import pytest

from app.services.analytics_service import AnalyticsService
from app.utils.exceptions import ErrorCode

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def analytics_service(tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    sample_file = FIXTURES_DIR / "sample.csv"
    (upload_dir / "sample.csv").write_bytes(sample_file.read_bytes())
    return AnalyticsService(upload_dir=upload_dir)


def test_analyze_uploaded_file_success(analytics_service):
    response = analytics_service.analyze_uploaded_file("sample.csv")

    assert response.stored_filename == "sample.csv"
    assert response.dataset_summary.rows == 4
    assert response.dataset_summary.columns == 5
    assert "amount" in response.dataset_summary.numeric_columns
    assert "name" in response.categorical_statistics
    assert response.missing_values.count >= 0
    assert "amount" in response.numeric_statistics
    assert response.numeric_statistics["amount"].max == 300.0
    assert response.outlier_detection["amount"].method == "IQR"
    assert response.correlation_matrix.columns == ["id", "amount"]


def test_analyze_uploaded_file_not_found(analytics_service):
    with pytest.raises(Exception) as exc_info:
        analytics_service.analyze_uploaded_file("missing.csv")

    assert exc_info.value.status_code == 404
    assert exc_info.value.error_code == ErrorCode.NOT_FOUND


def test_analyze_rejects_path_traversal(analytics_service):
    with pytest.raises(Exception) as exc_info:
        analytics_service.analyze_uploaded_file("../sample.csv")

    assert exc_info.value.status_code == 400
