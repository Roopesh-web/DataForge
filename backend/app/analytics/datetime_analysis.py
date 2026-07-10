from datetime import datetime

import polars as pl

from app.core.logging import get_logger

logger = get_logger("analytics.datetime_analysis")


def _parse_datetime_series(series: pl.Series) -> pl.Series:
    if series.dtype in {pl.Date, pl.Datetime, pl.Time, pl.Duration}:
        return series

    if series.dtype in {pl.Utf8, pl.String, pl.Categorical}:
        try:
            return series.str.to_datetime(strict=False)
        except Exception:
            try:
                return series.str.to_date(strict=False)
            except Exception:
                return series

    return series


def _format_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def compute_datetime_statistics(
    dataframe: pl.DataFrame,
    column_name: str,
) -> dict[str, str | int | None]:
    series = _parse_datetime_series(dataframe.get_column(column_name))
    non_null = series.drop_nulls()

    if non_null.len() == 0:
        return {
            "min_date": None,
            "max_date": None,
            "date_range": None,
        }

    min_value = non_null.min()
    max_value = non_null.max()

    min_date = _format_datetime(min_value) if min_value is not None else None
    max_date = _format_datetime(max_value) if max_value is not None else None

    date_range = None
    if min_value is not None and max_value is not None:
        try:
            delta = max_value - min_value
            if hasattr(delta, "days"):
                date_range = int(delta.days)
            else:
                date_range = int(delta.total_seconds() // 86400)
        except Exception:
            date_range = None

    logger.debug(
        "Computed datetime statistics | column={} | date_range={}",
        column_name,
        date_range,
    )

    return {
        "min_date": min_date,
        "max_date": max_date,
        "date_range": date_range,
    }


def compute_datetime_statistics_for_columns(
    dataframe: pl.DataFrame,
    datetime_columns: list[str],
) -> dict[str, dict[str, str | int | None]]:
    return {
        column: compute_datetime_statistics(dataframe, column)
        for column in datetime_columns
    }
