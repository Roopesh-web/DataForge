from typing import Any

import httpx

from dashboard.config import (
    ANALYTICS_ENDPOINT,
    HEALTH_ENDPOINT,
    PROFILE_ENDPOINT,
    QUALITY_ENDPOINT,
    REQUEST_TIMEOUT,
    UPLOAD_ENDPOINT,
    SUPPORTED_FILE_TYPES,
)


class APIError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _parse_error(response: httpx.Response) -> str:
    try:
        payload = response.json()
        return payload.get("message") or payload.get("error") or response.text
    except Exception:
        return response.text or f"Request failed with status {response.status_code}"


def check_health() -> dict[str, Any]:
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.get(HEALTH_ENDPOINT)
        if response.status_code != 200:
            raise APIError(_parse_error(response), response.status_code)
        return response.json()


def upload_file(filename: str, file_bytes: bytes, content_type: str) -> dict[str, Any]:
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.post(
            UPLOAD_ENDPOINT,
            files={"file": (filename, file_bytes, content_type)},
        )
        if response.status_code not in {200, 201}:
            raise APIError(_parse_error(response), response.status_code)
        return response.json()


def profile_dataset(stored_filename: str) -> dict[str, Any]:
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.post(
            PROFILE_ENDPOINT,
            json={"stored_filename": stored_filename},
        )
        if response.status_code != 200:
            raise APIError(_parse_error(response), response.status_code)
        return response.json()


def analyze_dataset(stored_filename: str) -> dict[str, Any]:
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.post(
            ANALYTICS_ENDPOINT,
            json={"stored_filename": stored_filename},
        )
        if response.status_code != 200:
            raise APIError(_parse_error(response), response.status_code)
        return response.json()


def quality_check(stored_filename: str) -> dict[str, Any]:
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.post(
            QUALITY_ENDPOINT,
            json={"stored_filename": stored_filename},
        )
        if response.status_code != 200:
            raise APIError(_parse_error(response), response.status_code)
        return response.json()


def resolve_content_type(filename: str) -> str:
    extension = filename.rsplit(".", 1)[-1].lower()
    return SUPPORTED_FILE_TYPES.get(extension, "application/octet-stream")
