from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger
from app.etl.exceptions import ProfilingError, ProfilingFileNotFoundError
from app.etl.reader import DatasetReader
from app.quality.engine import QualityValidationEngine
from app.schemas.quality import (
    QualityCheckResponse,
    ValidationRuleResult,
    ValidationSummary,
)
from app.utils.exceptions import AppException, ErrorCode

logger = get_logger("services.quality")


class QualityService:
    def __init__(
        self,
        upload_dir: Path | None = None,
        reader: DatasetReader | None = None,
        engine: QualityValidationEngine | None = None,
    ) -> None:
        self.upload_dir = upload_dir or settings.upload_path
        self.reader = reader or DatasetReader()
        self.engine = engine or QualityValidationEngine()

    def check_uploaded_file(self, stored_filename: str) -> QualityCheckResponse:
        logger.info("Quality check started | stored_filename={}", stored_filename)

        try:
            file_path = self._resolve_file_path(stored_filename)
            dataframe, _ = self.reader.read(file_path)
            validation_result = self.engine.validate(dataframe)
            response = self._build_response(stored_filename, validation_result)

            logger.info(
                "Quality check completed | stored_filename={} | score={} | failed={}",
                stored_filename,
                response.validation_summary.quality_score,
                response.validation_summary.failed_rules,
            )
            return response

        except AppException as exc:
            logger.warning(
                "Quality check failed | stored_filename={} | error={} | code={}",
                stored_filename,
                exc.message,
                exc.error_code.value,
            )
            raise
        except Exception as exc:
            logger.error(
                "Quality check failed | stored_filename={} | error={}",
                stored_filename,
                str(exc),
            )
            raise ProfilingError(
                message=f"Failed to run quality check: {exc}",
                status_code=500,
                error_code=ErrorCode.INTERNAL_ERROR,
            ) from exc

    def _resolve_file_path(self, stored_filename: str) -> Path:
        safe_name = Path(stored_filename).name
        if safe_name != stored_filename:
            raise ProfilingError(
                message="Invalid stored filename",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
            )

        file_path = self.upload_dir / safe_name
        if not file_path.exists():
            raise ProfilingFileNotFoundError(stored_filename=safe_name)

        return file_path

    def _build_response(
        self,
        stored_filename: str,
        validation_result: dict,
    ) -> QualityCheckResponse:
        summary = validation_result["validation_summary"]

        return QualityCheckResponse(
            stored_filename=stored_filename,
            validation_summary=ValidationSummary(**summary),
            passed_rules=[
                ValidationRuleResult(**rule) for rule in validation_result["passed_rules"]
            ],
            failed_rules=[
                ValidationRuleResult(**rule) for rule in validation_result["failed_rules"]
            ],
            validation_report=validation_result["validation_report"],
        )


def get_quality_service() -> QualityService:
    return QualityService()
