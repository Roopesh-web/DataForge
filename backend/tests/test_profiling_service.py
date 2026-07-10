from pathlib import Path

import pytest

from app.services.profiling_service import ProfilingService
from app.utils.exceptions import ErrorCode

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def profiling_service(tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    sample_file = FIXTURES_DIR / "sample.csv"
    (upload_dir / "sample.csv").write_bytes(sample_file.read_bytes())
    return ProfilingService(upload_dir=upload_dir)


def test_profile_uploaded_file_success(profiling_service):
    response = profiling_service.profile_uploaded_file("sample.csv")

    assert response.stored_filename == "sample.csv"
    assert response.file_format == "csv"
    assert response.row_count == 4
    assert response.column_count == 5
    assert response.duplicate_rows == 1
    assert "amount" in response.numeric_columns


def test_profile_uploaded_file_not_found(profiling_service):
    with pytest.raises(Exception) as exc_info:
        profiling_service.profile_uploaded_file("missing.csv")

    assert exc_info.value.status_code == 404
    assert exc_info.value.error_code == ErrorCode.NOT_FOUND


def test_profile_rejects_path_traversal(profiling_service):
    with pytest.raises(Exception) as exc_info:
        profiling_service.profile_uploaded_file("../sample.csv")

    assert exc_info.value.status_code == 400
