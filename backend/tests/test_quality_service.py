from pathlib import Path

import pytest

from app.services.quality_service import QualityService
from app.utils.exceptions import ErrorCode

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def quality_service(tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    sample_file = FIXTURES_DIR / "sample.csv"
    (upload_dir / "sample.csv").write_bytes(sample_file.read_bytes())
    return QualityService(upload_dir=upload_dir)


def test_quality_check_success(quality_service):
    response = quality_service.check_uploaded_file("sample.csv")

    assert response.stored_filename == "sample.csv"
    assert response.validation_summary.total_rules > 0
    assert 0 <= response.validation_summary.quality_score <= 100
    assert response.validation_report["dataset_rows"] == 4
    assert len(response.failed_rules) >= 1


def test_quality_check_file_not_found(quality_service):
    with pytest.raises(Exception) as exc_info:
        quality_service.check_uploaded_file("missing.csv")

    assert exc_info.value.status_code == 404
    assert exc_info.value.error_code == ErrorCode.NOT_FOUND


def test_quality_check_rejects_path_traversal(quality_service):
    with pytest.raises(Exception) as exc_info:
        quality_service.check_uploaded_file("../sample.csv")

    assert exc_info.value.status_code == 400
