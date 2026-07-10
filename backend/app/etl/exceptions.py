from app.utils.exceptions import AppException, ErrorCode


class ProfilingError(AppException):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status_code,
            error_code=error_code,
            details=[
                {
                    "field": "stored_filename",
                    "message": message,
                    "code": error_code.value,
                }
            ],
        )


class ProfilingFileNotFoundError(ProfilingError):
    def __init__(self, stored_filename: str) -> None:
        super().__init__(
            message=f"Uploaded file not found: {stored_filename}",
            status_code=404,
            error_code=ErrorCode.NOT_FOUND,
        )


class UnsupportedDatasetFormatError(ProfilingError):
    def __init__(self, stored_filename: str) -> None:
        super().__init__(
            message=(
                f"Unsupported dataset format for file: {stored_filename}. "
                "Supported formats: CSV, Excel (.xlsx), JSON"
            ),
            status_code=400,
            error_code=ErrorCode.INVALID_FILE_TYPE,
        )
