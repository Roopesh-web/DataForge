from __future__ import annotations

from enum import Enum

import polars as pl
from pydantic import BaseModel, Field


class SemanticDataType(str, Enum):
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    UNKNOWN = "unknown"


class ColumnSchema(BaseModel):
    name: str = Field(..., description="Column name")
    raw_dtype: str = Field(..., description="Native Polars data type")
    semantic_type: SemanticDataType = Field(..., description="Inferred semantic type")


class InferredSchema(BaseModel):
    columns: list[ColumnSchema] = Field(default_factory=list, description="Inferred column schema")


POLARS_NUMERIC_TYPES: frozenset[pl.DataType] = frozenset(
    {
        pl.Int8,
        pl.Int16,
        pl.Int32,
        pl.Int64,
        pl.UInt8,
        pl.UInt16,
        pl.UInt32,
        pl.UInt64,
        pl.Float32,
        pl.Float64,
        pl.Decimal,
    }
)

POLARS_DATETIME_TYPES: frozenset[pl.DataType] = frozenset(
    {
        pl.Date,
        pl.Datetime,
        pl.Time,
        pl.Duration,
    }
)


def _resolve_polars_type(dtype: pl.DataType) -> pl.DataType:
    if hasattr(dtype, "base_type"):
        base = dtype.base_type()
        if base != dtype:
            return _resolve_polars_type(base)
    return dtype


def infer_semantic_type(dtype: pl.DataType) -> SemanticDataType:
    resolved = _resolve_polars_type(dtype)

    if resolved in POLARS_NUMERIC_TYPES:
        return SemanticDataType.NUMERIC
    if resolved in POLARS_DATETIME_TYPES:
        return SemanticDataType.DATETIME
    if resolved == pl.Boolean:
        return SemanticDataType.BOOLEAN
    if resolved in {pl.Utf8, pl.Categorical, pl.Enum}:
        return SemanticDataType.CATEGORICAL
    return SemanticDataType.UNKNOWN


def infer_schema(df: pl.DataFrame) -> InferredSchema:
    columns = [
        ColumnSchema(
            name=name,
            raw_dtype=str(dtype),
            semantic_type=infer_semantic_type(dtype),
        )
        for name, dtype in df.schema.items()
    ]
    return InferredSchema(columns=columns)
