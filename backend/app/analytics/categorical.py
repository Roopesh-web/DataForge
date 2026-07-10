import polars as pl

from app.core.logging import get_logger

logger = get_logger("analytics.categorical")

DEFAULT_TOP_VALUES = 5


def compute_categorical_statistics(
    dataframe: pl.DataFrame,
    column_name: str,
    top_n: int = DEFAULT_TOP_VALUES,
) -> dict[str, int | list[dict[str, str | int]]]:
    series = dataframe.get_column(column_name)
    unique_count = int(series.n_unique())

    value_counts = (
        series.drop_nulls()
        .value_counts()
        .sort("count", descending=True)
        .head(top_n)
    )

    top_values = [
        {
            "value": str(row[column_name]),
            "frequency": int(row["count"]),
        }
        for row in value_counts.iter_rows(named=True)
    ]

    logger.debug(
        "Computed categorical statistics | column={} | unique_count={}",
        column_name,
        unique_count,
    )

    return {
        "unique_count": unique_count,
        "top_values": top_values,
        "frequencies": top_values,
    }


def compute_categorical_statistics_for_columns(
    dataframe: pl.DataFrame,
    categorical_columns: list[str],
) -> dict[str, dict[str, int | list[dict[str, str | int]]]]:
    return {
        column: compute_categorical_statistics(dataframe, column)
        for column in categorical_columns
    }
