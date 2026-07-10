from pathlib import Path

import polars as pl
import pytest

from app.analytics.analyzer import DatasetAnalyzer
from app.analytics.categorical import compute_categorical_statistics
from app.analytics.correlation import compute_pearson_correlation_matrix
from app.analytics.datetime_analysis import compute_datetime_statistics
from app.analytics.outliers import detect_outliers_iqr
from app.analytics.statistics import compute_numeric_statistics
from app.etl.reader import DatasetReader

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_dataframe():
    reader = DatasetReader()
    dataframe, _ = reader.read(FIXTURES_DIR / "sample.csv")
    return dataframe


def test_compute_numeric_statistics(sample_dataframe):
    stats = compute_numeric_statistics(sample_dataframe, "amount")

    assert stats["mean"] is not None
    assert stats["median"] is not None
    assert stats["max"] == 300.0
    assert stats["standard_deviation"] is not None
    assert stats["variance"] is not None


def test_compute_pearson_correlation_matrix(sample_dataframe):
    matrix = compute_pearson_correlation_matrix(sample_dataframe, ["id", "amount"])

    assert matrix["columns"] == ["id", "amount"]
    assert len(matrix["values"]) == 2
    assert matrix["values"][0][0] == 1.0


def test_detect_outliers_iqr(sample_dataframe):
    result = detect_outliers_iqr(sample_dataframe, "amount")

    assert result["method"] == "IQR"
    assert result["lower_bound"] is not None
    assert result["upper_bound"] is not None
    assert result["outlier_count"] >= 0


def test_compute_categorical_statistics(sample_dataframe):
    result = compute_categorical_statistics(sample_dataframe, "name")

    assert result["unique_count"] == 3
    assert len(result["top_values"]) > 0
    assert result["top_values"][0]["frequency"] >= 1


def test_compute_datetime_statistics(sample_dataframe):
    result = compute_datetime_statistics(sample_dataframe, "created_at")

    assert result["min_date"] is not None
    assert result["max_date"] is not None
    assert result["date_range"] is not None
    assert result["date_range"] >= 0


def test_dataset_analyzer(sample_dataframe):
    analyzer = DatasetAnalyzer()
    result = analyzer.analyze(sample_dataframe)

    assert result["dataset_summary"]["rows"] == 4
    assert result["dataset_summary"]["columns"] == 5
    assert "amount" in result["dataset_summary"]["numeric_columns"]
    assert result["missing_values"]["count"] >= 0
    assert "amount" in result["numeric_statistics"]
    assert "name" in result["categorical_statistics"]
    assert result["correlation_matrix"]["columns"] == ["id", "amount"]
