from typing import Any

import polars as pl

from app.analytics.categorical import compute_categorical_statistics_for_columns
from app.analytics.correlation import compute_pearson_correlation_matrix
from app.analytics.datetime_analysis import compute_datetime_statistics_for_columns
from app.analytics.outliers import detect_outliers_for_columns
from app.analytics.statistics import compute_numeric_statistics_for_columns
from app.core.logging import get_logger
from app.etl.schema import SemanticDataType, infer_schema

logger = get_logger("analytics.analyzer")


class DatasetAnalyzer:
    def analyze(self, dataframe: pl.DataFrame) -> dict[str, Any]:
        row_count = dataframe.height
        column_count = dataframe.width

        logger.info(
            "Dataset analysis started | rows={} | columns={}",
            row_count,
            column_count,
        )

        inferred_schema = infer_schema(dataframe)

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

        total_cells = row_count * column_count
        missing_count = int(dataframe.null_count().sum_horizontal().item())
        missing_percentage = round((missing_count / total_cells) * 100, 4) if total_cells else 0.0

        logger.info("Computing correlation matrix")
        correlation_matrix = compute_pearson_correlation_matrix(dataframe, numeric_columns)

        logger.info("Computing numeric statistics")
        numeric_statistics = compute_numeric_statistics_for_columns(dataframe, numeric_columns)

        logger.info("Detecting outliers")
        outlier_detection = detect_outliers_for_columns(dataframe, numeric_columns)

        logger.info("Computing categorical statistics")
        categorical_statistics = compute_categorical_statistics_for_columns(
            dataframe,
            categorical_columns,
        )

        logger.info("Computing datetime statistics")
        datetime_statistics = compute_datetime_statistics_for_columns(
            dataframe,
            datetime_columns,
        )

        result = {
            "dataset_summary": {
                "rows": row_count,
                "columns": column_count,
                "numeric_columns": numeric_columns,
                "categorical_columns": categorical_columns,
                "datetime_columns": datetime_columns,
            },
            "missing_values": {
                "count": missing_count,
                "percentage": missing_percentage,
            },
            "correlation_matrix": correlation_matrix,
            "numeric_statistics": numeric_statistics,
            "outlier_detection": outlier_detection,
            "categorical_statistics": categorical_statistics,
            "datetime_statistics": datetime_statistics,
        }

        logger.info("Dataset analysis completed | rows={} | columns={}", row_count, column_count)
        return result
