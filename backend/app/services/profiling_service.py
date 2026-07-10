from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger
from app.etl.exceptions import ProfilingError, ProfilingFileNotFoundError
from app.etl.profiler import DataProfiler
from app.etl.reader import DatasetReader
from app.schemas.profiling import (
    ColumnProfile,
    InferredSchemaResponse,
    NumericStatistics,
    ProfilingResponse,
    SchemaColumn,
)
from app.utils.exceptions import AppException, ErrorCode

logger = get_logger("services.profiling")


class ProfilingService:
    def __init__(
        self,
        upload_dir: Path | None = None,
        reader: DatasetReader | None = None,
        profiler: DataProfiler | None = None,
    ) -> None:
        self.upload_dir = upload_dir or settings.upload_path
        self.reader = reader or DatasetReader()
        self.profiler = profiler or DataProfiler(reader=self.reader)

    def profile_uploaded_file(self, stored_filename: str) -> ProfilingResponse:
        logger.info("Profiling started | stored_filename={}", stored_filename)

        try:
            file_path = self._resolve_file_path(stored_filename)
            dataframe, file_format = self.reader.read(file_path)
            profile_result = self.profiler.profile(dataframe, file_format.value)
            response = self._build_response(stored_filename, profile_result)

            logger.info(
                "Profiling completed | stored_filename={} | rows={} | columns={}",
                stored_filename,
                response.row_count,
                response.column_count,
            )
            return response

        except AppException as exc:
            logger.warning(
                "Profiling failed | stored_filename={} | error={} | code={}",
                stored_filename,
                exc.message,
                exc.error_code.value,
            )
            raise
        except Exception as exc:
            logger.error(
                "Profiling failed | stored_filename={} | error={}",
                stored_filename,
                str(exc),
            )
            raise ProfilingError(
                message=f"Failed to profile dataset: {exc}",
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
        profile_result: dict,
    ) -> ProfilingResponse:
        schema_data = profile_result["schema"]
        schema_columns = [
            SchemaColumn(**column) for column in schema_data.get("columns", [])
        ]

        column_profiles = []
        for column in profile_result["columns"]:
            statistics = column.get("statistics")
            column_profiles.append(
                ColumnProfile(
                    name=column["name"],
                    datatype=column["datatype"],
                    raw_dtype=column["raw_dtype"],
                    null_count=column["null_count"],
                    null_percentage=column["null_percentage"],
                    unique_values=column["unique_values"],
                    statistics=NumericStatistics(**statistics) if statistics else None,
                )
            )

        return ProfilingResponse(
            stored_filename=stored_filename,
            file_format=profile_result["file_format"],
            row_count=profile_result["row_count"],
            column_count=profile_result["column_count"],
            column_names=profile_result["column_names"],
            inferred_schema=InferredSchemaResponse(columns=schema_columns),
            columns=column_profiles,
            duplicate_rows=profile_result["duplicate_rows"],
            memory_usage_bytes=profile_result["memory_usage_bytes"],
            numeric_columns=profile_result["numeric_columns"],
            categorical_columns=profile_result["categorical_columns"],
            datetime_columns=profile_result["datetime_columns"],
        )


def get_profiling_service() -> ProfilingService:
    return ProfilingService()
