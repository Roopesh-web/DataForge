import math
from typing import Any

import polars as pl

from app.core.logging import get_logger
from app.etl.reader import DatasetReader
from app.etl.schema import InferredSchema, SemanticDataType, infer_schema

logger = get_logger("etl.profiler")


class DataProfiler:
    def __init__(self, reader: DatasetReader | None = None) -> None:
        self.reader = reader or DatasetReader()

    def profile(self, dataframe: pl.DataFrame, file_format: str) -> dict[str, Any]:
        row_count = dataframe.height

        logger.info("Schema inference started | rows={} | columns={}", row_count, dataframe.width)
        inferred_schema = infer_schema(dataframe)
        logger.info("Schema inference completed | columns={}", len(inferred_schema.columns))

        logger.info("Column profiling started")
        column_profiles = self._profile_columns(dataframe, inferred_schema, row_count)
        logger.info("Column profiling completed | columns={}", len(column_profiles))

        numeric_columns = [
            column.name
            for column in inferred_schema.columns
            if column.semantic_type == SemanticDataType.NUMERIC
        ]
        categorical_columns = [
            column.name
            for column in inferred_schema.columns
            if column.semantic_type == SemanticDataType.CATEGORICAL
        ]
        datetime_columns = [
            column.name
            for column in inferred_schema.columns
            if column.semantic_type == SemanticDataType.DATETIME
        ]

        unique_row_count = dataframe.unique(maintain_order=True).height
        duplicate_rows = int(max(row_count - unique_row_count, 0))
        memory_usage = self.reader.memory_usage_bytes(dataframe)

        logger.info(
            "Dataset statistics computed | duplicates={} | memory_bytes={}",
            duplicate_rows,
            memory_usage,
        )

        return {
            "file_format": file_format,
            "row_count": row_count,
            "column_count": dataframe.width,
            "column_names": dataframe.columns,
            "schema": inferred_schema.model_dump(),
            "columns": column_profiles,
            "duplicate_rows": duplicate_rows,
            "memory_usage_bytes": memory_usage,
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "datetime_columns": datetime_columns,
        }

    def _profile_columns(
        self,
        dataframe: pl.DataFrame,
        inferred_schema: InferredSchema,
        row_count: int,
    ) -> list[dict[str, Any]]:
        profiles: list[dict[str, Any]] = []

        for column_schema in inferred_schema.columns:
            column_name = column_schema.name
            series = dataframe.get_column(column_name)
            null_count = int(series.null_count())
            null_percentage = round((null_count / row_count) * 100, 4) if row_count else 0.0
            unique_values = int(series.n_unique())

            profile: dict[str, Any] = {
                "name": column_name,
                "datatype": column_schema.semantic_type.value,
                "raw_dtype": column_schema.raw_dtype,
                "null_count": null_count,
                "null_percentage": null_percentage,
                "unique_values": unique_values,
                "statistics": None,
            }

            if column_schema.semantic_type == SemanticDataType.NUMERIC:
                profile["statistics"] = self._numeric_statistics(dataframe, column_name)

            profiles.append(profile)

        return profiles

    def _numeric_statistics(self, dataframe: pl.DataFrame, column_name: str) -> dict[str, float | None]:
        series = dataframe.get_column(column_name).cast(pl.Float64, strict=False).drop_nulls()

        if series.len() == 0:
            return {
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
                "std": None,
            }

        return {
            "min": self._safe_float(series.min()),
            "max": self._safe_float(series.max()),
            "mean": self._safe_float(series.mean()),
            "median": self._safe_float(series.median()),
            "std": self._safe_float(series.std()),
        }

    @staticmethod
    def _safe_float(value: Any) -> float | None:
        if value is None:
            return None
        try:
            result = float(value)
        except (TypeError, ValueError):
            return None
        if math.isnan(result) or math.isinf(result):
            return None
        return round(result, 6)
