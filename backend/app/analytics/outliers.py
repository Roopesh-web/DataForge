import math
from typing import Any

import polars as pl

from app.core.logging import get_logger

logger = get_logger("analytics.outliers")

IQR_MULTIPLIER = 1.5


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


def detect_outliers_iqr(
    dataframe: pl.DataFrame,
    column_name: str,
) -> dict[str, str | float | int | None]:
    series = dataframe.get_column(column_name).cast(pl.Float64, strict=False)
    non_null = series.drop_nulls()

    if non_null.len() == 0:
        return {
            "method": "IQR",
            "lower_bound": None,
            "upper_bound": None,
            "outlier_count": 0,
        }

    q1 = _safe_float(non_null.quantile(0.25))
    q3 = _safe_float(non_null.quantile(0.75))

    if q1 is None or q3 is None:
        return {
            "method": "IQR",
            "lower_bound": None,
            "upper_bound": None,
            "outlier_count": 0,
        }

    iqr = q3 - q1
    lower_bound = _safe_float(q1 - IQR_MULTIPLIER * iqr)
    upper_bound = _safe_float(q3 + IQR_MULTIPLIER * iqr)

    outlier_count = 0
    if lower_bound is not None and upper_bound is not None:
        outlier_count = sum(
            1
            for value in non_null.to_list()
            if value is not None and (float(value) < lower_bound or float(value) > upper_bound)
        )

    logger.debug(
        "Detected outliers | column={} | outlier_count={}",
        column_name,
        outlier_count,
    )

    return {
        "method": "IQR",
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "outlier_count": outlier_count,
    }


def detect_outliers_for_columns(
    dataframe: pl.DataFrame,
    numeric_columns: list[str],
) -> dict[str, dict[str, str | float | int | None]]:
    return {
        column: detect_outliers_iqr(dataframe, column)
        for column in numeric_columns
    }
