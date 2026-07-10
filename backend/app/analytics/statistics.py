import math
from typing import Any

import polars as pl

from app.core.logging import get_logger

logger = get_logger("analytics.statistics")


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


def compute_mode(series: pl.Series) -> float | None:
    non_null = series.drop_nulls()
    if non_null.len() == 0:
        return None

    counts = non_null.value_counts().sort("count", descending=True)
    if counts.height == 0:
        return None

    column_name = series.name
    return _safe_float(counts[column_name][0])


def compute_numeric_statistics(
    dataframe: pl.DataFrame,
    column_name: str,
) -> dict[str, float | None]:
    series = dataframe.get_column(column_name).cast(pl.Float64, strict=False)
    non_null = series.drop_nulls()

    if non_null.len() == 0:
        return {
            "mean": None,
            "median": None,
            "mode": None,
            "variance": None,
            "standard_deviation": None,
            "min": None,
            "max": None,
            "skewness": None,
            "kurtosis": None,
        }

    pandas_series = non_null.to_pandas()

    logger.debug("Computed numeric statistics | column={}", column_name)

    return {
        "mean": _safe_float(non_null.mean()),
        "median": _safe_float(non_null.median()),
        "mode": compute_mode(series),
        "variance": _safe_float(non_null.var()),
        "standard_deviation": _safe_float(non_null.std()),
        "min": _safe_float(non_null.min()),
        "max": _safe_float(non_null.max()),
        "skewness": _safe_float(pandas_series.skew()),
        "kurtosis": _safe_float(pandas_series.kurtosis()),
    }


def compute_numeric_statistics_for_columns(
    dataframe: pl.DataFrame,
    numeric_columns: list[str],
) -> dict[str, dict[str, float | None]]:
    return {
        column: compute_numeric_statistics(dataframe, column)
        for column in numeric_columns
    }
