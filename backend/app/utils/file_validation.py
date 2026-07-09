import mimetypes
from enum import Enum
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.utils.exceptions import ErrorCode, FileSizeExceededError, FileValidationError


class SupportedFileType(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"


ALLOWED_EXTENSIONS: dict[str, SupportedFileType] = {
    ".csv": SupportedFileType.CSV,
    ".xlsx": SupportedFileType.EXCEL,
    ".xls": SupportedFileType.EXCEL,
    ".json": SupportedFileType.JSON,
}

ALLOWED_MIME_TYPES: dict[str, SupportedFileType] = {
    "text/csv": SupportedFileType.CSV,
    "application/csv": SupportedFileType.CSV,
    "application/vnd.ms-excel": SupportedFileType.EXCEL,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": SupportedFileType.EXCEL,
    "application/json": SupportedFileType.JSON,
    "text/json": SupportedFileType.JSON,
}


def get_file_extension(filename: str | None) -> str:
    if not filename:
        return ""
    return Path(filename).suffix.lower()


def detect_file_type(filename: str, content_type: str | None) -> SupportedFileType:
    extension = get_file_extension(filename)

    if extension in ALLOWED_EXTENSIONS:
        return ALLOWED_EXTENSIONS[extension]

    if content_type:
        normalized_content_type = content_type.split(";")[0].strip().lower()
        if normalized_content_type in ALLOWED_MIME_TYPES:
            return ALLOWED_MIME_TYPES[normalized_content_type]

    guessed_type, _ = mimetypes.guess_type(filename)
    if guessed_type and guessed_type in ALLOWED_MIME_TYPES:
        return ALLOWED_MIME_TYPES[guessed_type]

    raise FileValidationError(
        message=(
            "Unsupported file type. Allowed types: CSV (.csv), "
            "Excel (.xlsx, .xls), JSON (.json)"
        ),
    )


async def validate_upload_file(file: UploadFile) -> tuple[bytes, SupportedFileType]:
    if not file.filename:
        raise FileValidationError(message="Filename is required")

    file_type = detect_file_type(file.filename, file.content_type)
    content = await file.read()

    if not content:
        raise FileValidationError(
            message="Uploaded file is empty",
            error_code=ErrorCode.EMPTY_FILE,
        )

    if len(content) > settings.max_upload_size_bytes:
        raise FileSizeExceededError(max_size_mb=settings.max_upload_size_mb)

    return content, file_type


def generate_safe_filename(original_filename: str) -> str:
    from datetime import datetime, timezone
    import re
    import uuid

    extension = get_file_extension(original_filename)
    stem = Path(original_filename).stem
    safe_stem = re.sub(r"[^\w\-]+", "_", stem).strip("_") or "upload"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{safe_stem}_{timestamp}_{unique_id}{extension}"
