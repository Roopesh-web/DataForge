from pydantic import BaseModel, Field


class AnalyticsRequest(BaseModel):
    stored_filename: str = Field(
        ...,
        min_length=1,
        description="Stored filename returned by the upload API",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890.csv"],
    )


class DatasetSummary(BaseModel):
    rows: int = Field(..., ge=0)
    columns: int = Field(..., ge=0)
    numeric_columns: list[str] = Field(default_factory=list)
    categorical_columns: list[str] = Field(default_factory=list)
    datetime_columns: list[str] = Field(default_factory=list)


class MissingValuesSummary(BaseModel):
    count: int = Field(..., ge=0)
    percentage: float = Field(..., ge=0)


class CorrelationMatrix(BaseModel):
    columns: list[str] = Field(default_factory=list)
    values: list[list[float | None]] = Field(default_factory=list)


class NumericColumnStatistics(BaseModel):
    mean: float | None = None
    median: float | None = None
    mode: float | None = None
    variance: float | None = None
    standard_deviation: float | None = None
    min: float | None = None
    max: float | None = None
    skewness: float | None = None
    kurtosis: float | None = None


class OutlierDetectionResult(BaseModel):
    method: str = Field(default="IQR")
    lower_bound: float | None = None
    upper_bound: float | None = None
    outlier_count: int = Field(default=0, ge=0)


class CategoricalValueFrequency(BaseModel):
    value: str
    frequency: int = Field(..., ge=0)


class CategoricalColumnStatistics(BaseModel):
    unique_count: int = Field(..., ge=0)
    top_values: list[CategoricalValueFrequency] = Field(default_factory=list)
    frequencies: list[CategoricalValueFrequency] = Field(default_factory=list)


class DatetimeColumnStatistics(BaseModel):
    min_date: str | None = None
    max_date: str | None = None
    date_range: int | None = Field(
        default=None,
        description="Date range in days between min and max date",
    )


class AnalyticsResponse(BaseModel):
    stored_filename: str
    dataset_summary: DatasetSummary
    missing_values: MissingValuesSummary
    correlation_matrix: CorrelationMatrix
    numeric_statistics: dict[str, NumericColumnStatistics] = Field(default_factory=dict)
    outlier_detection: dict[str, OutlierDetectionResult] = Field(default_factory=dict)
    categorical_statistics: dict[str, CategoricalColumnStatistics] = Field(default_factory=dict)
    datetime_statistics: dict[str, DatetimeColumnStatistics] = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "example": {
                "stored_filename": "a1b2c3d4-e5f6-7890-abcd-ef1234567890.csv",
                "dataset_summary": {
                    "rows": 1000,
                    "columns": 5,
                    "numeric_columns": ["id", "amount"],
                    "categorical_columns": ["name", "category"],
                    "datetime_columns": ["created_at"],
                },
                "missing_values": {"count": 12, "percentage": 0.24},
                "correlation_matrix": {
                    "columns": ["id", "amount"],
                    "values": [[1.0, 0.42], [0.42, 1.0]],
                },
                "numeric_statistics": {},
                "outlier_detection": {},
                "categorical_statistics": {},
                "datetime_statistics": {},
            }
        }
    }
