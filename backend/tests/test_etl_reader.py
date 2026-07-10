import json
from pathlib import Path

import polars as pl
import pytest

from app.etl.reader import DatasetFormat, DatasetReader, detect_file_format
from app.etl.schema import SemanticDataType, infer_schema

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_detect_file_format_csv():
    assert detect_file_format(FIXTURES_DIR / "sample.csv") == DatasetFormat.CSV


def test_detect_file_format_json():
    assert detect_file_format(FIXTURES_DIR / "sample.json") == DatasetFormat.JSON


def test_detect_file_format_xlsx():
    assert detect_file_format(FIXTURES_DIR / "sample.xlsx") == DatasetFormat.EXCEL


def test_read_csv_dataset():
    reader = DatasetReader()
    dataframe, file_format = reader.read(FIXTURES_DIR / "sample.csv")

    assert file_format == DatasetFormat.CSV
    assert dataframe.height == 4
    assert dataframe.width == 5
    assert "amount" in dataframe.columns


def test_read_json_dataset():
    reader = DatasetReader()
    dataframe, file_format = reader.read(FIXTURES_DIR / "sample.json")

    assert file_format == DatasetFormat.JSON
    assert dataframe.height == 3
    assert "amount" in dataframe.columns


def test_read_xlsx_dataset():
    reader = DatasetReader()
    dataframe, file_format = reader.read(FIXTURES_DIR / "sample.xlsx")

    assert file_format == DatasetFormat.EXCEL
    assert dataframe.height == 3
    assert "amount" in dataframe.columns


def test_infer_schema_from_csv():
    reader = DatasetReader()
    dataframe, _ = reader.read(FIXTURES_DIR / "sample.csv")
    schema = infer_schema(dataframe)

    semantic_types = {column.name: column.semantic_type for column in schema.columns}
    assert semantic_types["amount"] == SemanticDataType.NUMERIC
    assert semantic_types["name"] == SemanticDataType.CATEGORICAL


def test_memory_usage_bytes():
    reader = DatasetReader()
    dataframe, _ = reader.read(FIXTURES_DIR / "sample.csv")

    memory_usage = reader.memory_usage_bytes(dataframe)

    assert memory_usage > 0
