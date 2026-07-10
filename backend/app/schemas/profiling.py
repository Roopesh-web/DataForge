from pydantic import BaseModel, Field


class NumericStatistics(BaseModel):
    min: float | None = Field(default=None, description="Minimum value")
    max: float | None = Field(default=None, description="Maximum value")
    mean: float | None = Field(default=None, description="Mean value")
    median: float | None = Field(default=None, description="Median value")
    std: float | None = Field(default=None, description="Standard deviation")


class ColumnProfile(BaseModel):
    name: str = Field(..., description="Column name")
    datatype: str = Field(..., description="Inferred semantic data type")
    raw_dtype: str = Field(..., description="Native engine data type")
    null_count: int = Field(..., ge=0, description="Number of null values")
    null_percentage: float = Field(..., ge=0, description="Percentage of null values")
    unique_values: int = Field(..., ge=0, description="Count of distinct values")
    statistics: NumericStatistics | None = Field(
        default=None,
        description="Summary statistics for numeric columns",
    )


class SchemaColumn(BaseModel):
    name: str
    raw_dtype: str
    semantic_type: str


class InferredSchemaResponse(BaseModel):
    columns: list[SchemaColumn] = Field(default_factory=list)


class ProfilingResponse(BaseModel):
    stored_filename: str = Field(..., description="Stored upload filename")
    file_format: str = Field(..., description="Detected file format")
    row_count: int = Field(..., ge=0, description="Total number of rows")
    column_count: int = Field(..., ge=0, description="Total number of columns")
    column_names: list[str] = Field(default_factory=list, description="Column names")
    inferred_schema: InferredSchemaResponse = Field(
        ...,
        description="Inferred dataset schema",
        serialization_alias="schema",
    )
    columns: list[ColumnProfile] = Field(default_factory=list, description="Column-level profiles")
    duplicate_rows: int = Field(..., ge=0, description="Number of duplicate rows")
    memory_usage_bytes: int = Field(..., ge=0, description="Estimated memory usage in bytes")
    numeric_columns: list[str] = Field(default_factory=list, description="Numeric column names")
    categorical_columns: list[str] = Field(
        default_factory=list,
        description="Categorical column names",
    )
    datetime_columns: list[str] = Field(default_factory=list, description="Datetime column names")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "stored_filename": "a1b2c3d4-e5f6-7890-abcd-ef1234567890.csv",
                "file_format": "csv",
                "row_count": 1000,
                "column_count": 5,
                "column_names": ["id", "name", "amount", "category", "created_at"],
                "inferred_schema": {
                    "columns": [
                        {
                            "name": "id",
                            "raw_dtype": "Int64",
                            "semantic_type": "numeric",
                        }
                    ]
                },
                "columns": [],
                "duplicate_rows": 3,
                "memory_usage_bytes": 40960,
                "numeric_columns": ["id", "amount"],
                "categorical_columns": ["name", "category"],
                "datetime_columns": ["created_at"],
            }
        }
    }


class ProfilingRequest(BaseModel):
    stored_filename: str = Field(
        ...,
        min_length=1,
        description="Stored filename returned by the upload API",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890.csv"],
    )
