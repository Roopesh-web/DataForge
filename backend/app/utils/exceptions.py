from enum import Enum


class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    EMPTY_FILE = "EMPTY_FILE"
    UPLOAD_FAILED = "UPLOAD_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NOT_FOUND = "NOT_FOUND"
    DATABASE_ERROR = "DATABASE_ERROR"


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: ErrorCode = ErrorCode.VALIDATION_ERROR,
        details: list[dict[str, str | None]] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or []
        super().__init__(message)


class FileValidationError(AppException):
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INVALID_FILE_TYPE,
        field: str = "file",
    ) -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_code=error_code,
            details=[{"field": field, "message": message, "code": error_code.value}],
        )


class FileSizeExceededError(AppException):
    def __init__(self, max_size_mb: int) -> None:
        message = f"File size exceeds maximum allowed size of {max_size_mb} MB"
        super().__init__(
            message=message,
            status_code=413,
            error_code=ErrorCode.FILE_TOO_LARGE,
            details=[
                {
                    "field": "file",
                    "message": message,
                    "code": ErrorCode.FILE_TOO_LARGE.value,
                }
            ],
        )


class UploadFailedError(AppException):
    def __init__(self, message: str = "Failed to save uploaded file") -> None:
        super().__init__(
            message=message,
            status_code=500,
            error_code=ErrorCode.UPLOAD_FAILED,
            details=[
                {
                    "field": "file",
                    "message": message,
                    "code": ErrorCode.UPLOAD_FAILED.value,
                }
            ],
        )
