from pathlib import Path

from app.analytics.analyzer import DatasetAnalyzer
from app.core.config import settings
from app.core.logging import get_logger
from app.etl.exceptions import ProfilingError, ProfilingFileNotFoundError
from app.etl.reader import DatasetReader
from app.schemas.analytics import (
    AnalyticsResponse,
    CategoricalColumnStatistics,
    CategoricalValueFrequency,
    CorrelationMatrix,
    DatasetSummary,
    DatetimeColumnStatistics,
    MissingValuesSummary,
    NumericColumnStatistics,
    OutlierDetectionResult,
)
from app.utils.exceptions import AppException, ErrorCode

logger = get_logger("services.analytics")


class AnalyticsService:
    def __init__(
        self,
        upload_dir: Path | None = None,
        reader: DatasetReader | None = None,
        analyzer: DatasetAnalyzer | None = None,
    ) -> None:
        self.upload_dir = upload_dir or settings.upload_path
        self.reader = reader or DatasetReader()
        self.analyzer = analyzer or DatasetAnalyzer()

    def analyze_uploaded_file(self, stored_filename: str) -> AnalyticsResponse:
        logger.info("Analytics started | stored_filename={}", stored_filename)

        try:
            file_path = self._resolve_file_path(stored_filename)
            dataframe, _ = self.reader.read(file_path)
            analysis_result = self.analyzer.analyze(dataframe)
            response = self._build_response(stored_filename, analysis_result)

            logger.info(
                "Analytics completed | stored_filename={} | rows={} | columns={}",
                stored_filename,
                response.dataset_summary.rows,
                response.dataset_summary.columns,
            )
            return response

        except AppException as exc:
            logger.warning(
                "Analytics failed | stored_filename={} | error={} | code={}",
                stored_filename,
                exc.message,
                exc.error_code.value,
            )
            raise
        except Exception as exc:
            logger.error(
                "Analytics failed | stored_filename={} | error={}",
                stored_filename,
                str(exc),
            )
            raise ProfilingError(
                message=f"Failed to analyze dataset: {exc}",
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
        analysis_result: dict,
    ) -> AnalyticsResponse:
        summary_data = analysis_result["dataset_summary"]
        missing_data = analysis_result["missing_values"]
        correlation_data = analysis_result["correlation_matrix"]

        numeric_statistics = {
            column: NumericColumnStatistics(**stats)
            for column, stats in analysis_result["numeric_statistics"].items()
        }

        outlier_detection = {
            column: OutlierDetectionResult(**stats)
            for column, stats in analysis_result["outlier_detection"].items()
        }

        categorical_statistics = {
            column: CategoricalColumnStatistics(
                unique_count=stats["unique_count"],
                top_values=[
                    CategoricalValueFrequency(**item) for item in stats["top_values"]
                ],
                frequencies=[
                    CategoricalValueFrequency(**item) for item in stats["frequencies"]
                ],
            )
            for column, stats in analysis_result["categorical_statistics"].items()
        }

        datetime_statistics = {
            column: DatetimeColumnStatistics(**stats)
            for column, stats in analysis_result["datetime_statistics"].items()
        }

        return AnalyticsResponse(
            stored_filename=stored_filename,
            dataset_summary=DatasetSummary(**summary_data),
            missing_values=MissingValuesSummary(**missing_data),
            correlation_matrix=CorrelationMatrix(**correlation_data),
            numeric_statistics=numeric_statistics,
            outlier_detection=outlier_detection,
            categorical_statistics=categorical_statistics,
            datetime_statistics=datetime_statistics,
        )


def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()
