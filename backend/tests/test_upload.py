import json
from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.upload_service import UploadService, get_upload_service

client = TestClient(app)


@pytest.fixture
def upload_dir(tmp_path):
    path = tmp_path / "uploads"
    path.mkdir(parents=True, exist_ok=True)
    service = UploadService(upload_dir=path)
    app.dependency_overrides[get_upload_service] = lambda: service
    yield path
    app.dependency_overrides.clear()


def test_upload_csv_file(upload_dir):
    content = b"col1,col2\nvalue1,value2\n"
    response = client.post(
        "/upload",
        files={"file": ("test_data.csv", BytesIO(content), "text/csv")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["size"] == len(content)
    assert body["type"] == "csv"
    assert body["filename"].endswith(".csv")
    assert "timestamp" in body
    assert (upload_dir / body["filename"]).exists()


def test_upload_json_file(upload_dir):
    content = json.dumps({"key": "value"}).encode()
    response = client.post(
        "/upload",
        files={"file": ("test_data.json", BytesIO(content), "application/json")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["type"] == "json"
    assert body["size"] == len(content)


def test_upload_rejects_unsupported_file_type():
    content = b"plain text content"
    response = client.post(
        "/upload",
        files={"file": ("test_data.txt", BytesIO(content), "text/plain")},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "INVALID_FILE_TYPE"


def test_upload_rejects_empty_file():
    response = client.post(
        "/upload",
        files={"file": ("empty.csv", BytesIO(b""), "text/csv")},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "EMPTY_FILE"


def test_upload_rejects_oversized_file(upload_dir):
    content = b"x" * (2 * 1024 * 1024)
    with patch("app.utils.file_validation.settings") as mock_settings:
        mock_settings.max_upload_size_bytes = 1024 * 1024
        response = client.post(
            "/upload",
            files={"file": ("large.csv", BytesIO(content), "text/csv")},
        )

    assert response.status_code == 413
    body = response.json()
    assert body["error"] == "FILE_TOO_LARGE"
