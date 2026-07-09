from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.upload import UploadResponse
from app.utils.exceptions import AppException, UploadFailedError
from app.utils.file_validation import generate_unique_filename, validate_upload_file

logger = get_logger("services.upload")


class UploadService:
    def __init__(self, upload_dir: Path | None = None) -> None:
        self.upload_dir = upload_dir or settings.upload_path

    async def process_upload(self, file: UploadFile) -> UploadResponse:
        original_filename = file.filename or "unknown"

        logger.info(
            "Upload started | original_filename={} | content_type={}",
            original_filename,
            file.content_type,
        )

        try:
            content, file_type = await validate_upload_file(file)
            stored_filename = generate_unique_filename(original_filename, self.upload_dir)
            destination = self.upload_dir / stored_filename

            if destination.exists():
                raise UploadFailedError(message="File already exists and cannot be overwritten")

            destination.write_bytes(content)

            timestamp = datetime.now(timezone.utc)

            logger.info(
                "Upload completed | original_filename={} | stored_filename={} | "
                "size={} | file_type={}",
                original_filename,
                stored_filename,
                len(content),
                file_type.value,
            )

            return UploadResponse(
                original_filename=original_filename,
                stored_filename=stored_filename,
                timestamp=timestamp,
                size=len(content),
                file_type=file_type.value,
            )

        except AppException as exc:
            logger.warning(
                "Upload failed | original_filename={} | error={} | code={}",
                original_filename,
                exc.message,
                exc.error_code.value,
            )
            raise
        except OSError as exc:
            logger.error(
                "Upload failed | original_filename={} | error={}",
                original_filename,
                str(exc),
            )
            raise UploadFailedError(message="Failed to save uploaded file") from exc
        except Exception as exc:
            logger.error(
                "Upload failed | original_filename={} | error={}",
                original_filename,
                str(exc),
            )
            raise UploadFailedError(message="Failed to process uploaded file") from exc


def get_upload_service() -> UploadService:
    return UploadService()
