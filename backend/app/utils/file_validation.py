import uuid
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
    ".json": SupportedFileType.JSON,
}

ALLOWED_MIME_TYPES: dict[str, SupportedFileType] = {
    "text/csv": SupportedFileType.CSV,
    "application/csv": SupportedFileType.CSV,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": SupportedFileType.EXCEL,
    "application/json": SupportedFileType.JSON,
    "text/json": SupportedFileType.JSON,
}


def get_file_extension(filename: str | None) -> str:
    if not filename:
        return ""
    return Path(filename).suffix.lower()


def validate_extension(filename: str) -> SupportedFileType:
    extension = get_file_extension(filename)

    if extension not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            message=(
                "Unsupported file extension. Allowed extensions: "
                ".csv, .xlsx, .json"
            ),
        )

    return ALLOWED_EXTENSIONS[extension]


def validate_mime_type(content_type: str | None) -> SupportedFileType:
    if not content_type:
        raise FileValidationError(
            message="Content-Type header is required",
            error_code=ErrorCode.VALIDATION_ERROR,
        )

    normalized_content_type = content_type.split(";")[0].strip().lower()

    if normalized_content_type in ALLOWED_MIME_TYPES:
        return ALLOWED_MIME_TYPES[normalized_content_type]

    raise FileValidationError(
        message=(
            "Unsupported MIME type. Allowed types: text/csv, application/csv, "
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, "
            "application/json"
        ),
    )


def validate_file_type(filename: str, content_type: str | None) -> SupportedFileType:
    extension_type = validate_extension(filename)
    mime_type = validate_mime_type(content_type)

    if extension_type != mime_type:
        raise FileValidationError(
            message=(
                f"File extension and MIME type mismatch: "
                f"extension indicates '{extension_type.value}', "
                f"MIME type indicates '{mime_type.value}'"
            ),
        )

    return extension_type


def generate_unique_filename(original_filename: str, upload_dir: Path) -> str:
    extension = get_file_extension(original_filename)

    while True:
        stored_filename = f"{uuid.uuid4()}{extension}"
        if not (upload_dir / stored_filename).exists():
            return stored_filename


async def validate_upload_file(file: UploadFile) -> tuple[bytes, SupportedFileType]:
    if not file.filename:
        raise FileValidationError(
            message="Filename is required",
            error_code=ErrorCode.VALIDATION_ERROR,
        )

    file_type = validate_file_type(file.filename, file.content_type)
    content = await file.read()

    if not content:
        raise FileValidationError(
            message="Uploaded file is empty",
            error_code=ErrorCode.EMPTY_FILE,
        )

    if len(content) > settings.max_upload_size_bytes:
        raise FileSizeExceededError(max_size_mb=settings.max_upload_size_mb)

    return content, file_type
