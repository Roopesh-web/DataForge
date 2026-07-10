from pathlib import Path

import polars as pl

from app.etl.profiler import DataProfiler
from app.etl.reader import DatasetReader

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_profile_csv_dataset():
    reader = DatasetReader()
    dataframe, file_format = reader.read(FIXTURES_DIR / "sample.csv")

    profiler = DataProfiler(reader=reader)
    result = profiler.profile(dataframe, file_format.value)

    assert result["row_count"] == 4
    assert result["column_count"] == 5
    assert result["duplicate_rows"] == 1
    assert "amount" in result["numeric_columns"]
    assert "name" in result["categorical_columns"]
    assert result["memory_usage_bytes"] > 0

    amount_profile = next(column for column in result["columns"] if column["name"] == "amount")
    assert amount_profile["null_count"] == 0
    assert amount_profile["statistics"] is not None
    assert amount_profile["statistics"]["max"] == 300.0


def test_profile_json_dataset():
    reader = DatasetReader()
    dataframe, file_format = reader.read(FIXTURES_DIR / "sample.json")

    profiler = DataProfiler()
    result = profiler.profile(dataframe, file_format.value)

    assert result["row_count"] == 3
    assert result["column_count"] == 4
    assert result["duplicate_rows"] == 1
