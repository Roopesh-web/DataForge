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
    assert body["original_filename"] == "test_data.csv"
    assert body["stored_filename"].endswith(".csv")
    assert body["size"] == len(content)
    assert body["file_type"] == "csv"
    assert "timestamp" in body
    assert (upload_dir / body["stored_filename"]).exists()


def test_upload_xlsx_file(upload_dir):
    content = b"PK\x03\x04fake-xlsx-content"
    response = client.post(
        "/upload",
        files={
            "file": (
                "report.xlsx",
                BytesIO(content),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["original_filename"] == "report.xlsx"
    assert body["stored_filename"].endswith(".xlsx")
    assert body["file_type"] == "excel"


def test_upload_json_file(upload_dir):
    content = json.dumps({"key": "value"}).encode()
    response = client.post(
        "/upload",
        files={"file": ("test_data.json", BytesIO(content), "application/json")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["original_filename"] == "test_data.json"
    assert body["file_type"] == "json"
    assert body["size"] == len(content)


def test_upload_generates_unique_filenames(upload_dir):
    content = b"col1,col2\nvalue1,value2\n"

    first = client.post(
        "/upload",
        files={"file": ("test_data.csv", BytesIO(content), "text/csv")},
    )
    second = client.post(
        "/upload",
        files={"file": ("test_data.csv", BytesIO(content), "text/csv")},
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["stored_filename"] != second.json()["stored_filename"]


def test_upload_rejects_unsupported_extension():
    content = b"plain text content"
    response = client.post(
        "/upload",
        files={"file": ("test_data.txt", BytesIO(content), "text/plain")},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "INVALID_FILE_TYPE"


def test_upload_rejects_unsupported_mime_type():
    content = b"col1,col2\nvalue1,value2\n"
    response = client.post(
        "/upload",
        files={"file": ("test_data.csv", BytesIO(content), "text/plain")},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "INVALID_FILE_TYPE"


def test_upload_rejects_extension_mime_mismatch():
    content = b"col1,col2\nvalue1,value2\n"
    response = client.post(
        "/upload",
        files={"file": ("test_data.csv", BytesIO(content), "application/json")},
    )

    assert response.status_code == 400
    body = response.json()
    assert "mismatch" in body["message"].lower()


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
