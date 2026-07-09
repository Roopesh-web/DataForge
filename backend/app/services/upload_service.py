from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.upload import UploadResponse
from app.utils.exceptions import UploadFailedError
from app.utils.file_validation import (
    generate_safe_filename,
    validate_upload_file,
)

logger = get_logger("services.upload")


class UploadService:
    def __init__(self, upload_dir: Path | None = None) -> None:
        self.upload_dir = upload_dir or settings.upload_path

    async def process_upload(self, file) -> UploadResponse:
        content, file_type = await validate_upload_file(file)
        safe_filename = generate_safe_filename(file.filename)
        destination = self.upload_dir / safe_filename

        try:
            destination.write_bytes(content)
        except OSError as exc:
            logger.error("Failed to write upload to disk: {}", exc)
            raise UploadFailedError(message="Failed to save uploaded file") from exc

        timestamp = datetime.now(timezone.utc)
        logger.info(
            "File uploaded | filename={} | size={} | type={}",
            safe_filename,
            len(content),
            file_type.value,
        )

        return UploadResponse(
            filename=safe_filename,
            size=len(content),
            type=file_type.value,
            timestamp=timestamp,
        )


def get_upload_service() -> UploadService:
    return UploadService()
