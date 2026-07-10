import math
from typing import Any

import polars as pl

from app.core.logging import get_logger

logger = get_logger("analytics.correlation")


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


def compute_pearson_correlation_matrix(
    dataframe: pl.DataFrame,
    numeric_columns: list[str],
) -> dict[str, list[str] | list[list[float | None]]]:
    if len(numeric_columns) < 2:
        logger.debug(
            "Skipping correlation matrix | numeric_columns={}",
            len(numeric_columns),
        )
        return {"columns": numeric_columns, "values": []}

    numeric_frame = dataframe.select(numeric_columns).cast(pl.Float64, strict=False)
    correlation = numeric_frame.to_pandas().corr(method="pearson")

    values = [
        [_safe_float(correlation.loc[row, col]) for col in numeric_columns]
        for row in numeric_columns
    ]

    logger.debug(
        "Computed Pearson correlation matrix | columns={}",
        len(numeric_columns),
    )

    return {
        "columns": numeric_columns,
        "values": values,
    }
