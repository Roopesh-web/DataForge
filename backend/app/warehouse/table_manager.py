from __future__ import annotations

import polars as pl
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    inspect,
)
from sqlalchemy.engine import Engine

from app.warehouse.exceptions import WarehouseTableError, sanitize_identifier
from app.db.schema_setup import (
    APPLICATION_SCHEMA,
    ensure_application_schema,
    uses_application_schema,
)

WAREHOUSE_METADATA = MetaData()
DEFAULT_BATCH_SIZE = 1000


def map_polars_type_to_sqlalchemy(dtype: pl.DataType):
    while hasattr(dtype, "base_type"):
        base = dtype.base_type()
        if base == dtype:
            break
        dtype = base

    if dtype in {pl.Int8, pl.Int16, pl.Int32, pl.UInt8, pl.UInt16, pl.UInt32}:
        return Integer
    if dtype in {pl.Int64, pl.UInt64}:
        return BigInteger
    if dtype in {pl.Float32, pl.Float64, pl.Decimal}:
        return Float
    if dtype == pl.Boolean:
        return Boolean
    if dtype in {pl.Date}:
        return Date
    if dtype in {pl.Datetime, pl.Time, pl.Duration}:
        return DateTime
    return Text


def _warehouse_schema(engine: Engine) -> str | None:
    if not uses_application_schema(engine):
        return None
    ensure_application_schema(engine)
    return APPLICATION_SCHEMA


def build_warehouse_table(
    table_name: str,
    dataframe: pl.DataFrame,
    schema: str | None = None,
) -> Table:
    columns = [
        Column("wh_row_id", Integer, primary_key=True, autoincrement=True),
    ]

    for name, dtype in dataframe.schema.items():
        sql_type = map_polars_type_to_sqlalchemy(dtype)
        columns.append(
            Column(
                sanitize_identifier(name),
                sql_type(),
                nullable=True,
            )
        )

    return Table(table_name, WAREHOUSE_METADATA, *columns, schema=schema)


def ensure_warehouse_table(engine: Engine, table_name: str, dataframe: pl.DataFrame) -> Table:
    schema = _warehouse_schema(engine)
    inspector = inspect(engine)

    if inspector.has_table(table_name, schema=schema) or (
        schema is not None and inspector.has_table(table_name)
    ):
        key = f"{schema}.{table_name}" if schema else table_name
        if key in WAREHOUSE_METADATA.tables:
            return WAREHOUSE_METADATA.tables[key]
        if table_name in WAREHOUSE_METADATA.tables:
            return WAREHOUSE_METADATA.tables[table_name]
        return Table(table_name, WAREHOUSE_METADATA, schema=schema, autoload_with=engine)

    key = f"{schema}.{table_name}" if schema else table_name
    if key in WAREHOUSE_METADATA.tables:
        WAREHOUSE_METADATA.remove(WAREHOUSE_METADATA.tables[key])
    elif table_name in WAREHOUSE_METADATA.tables:
        WAREHOUSE_METADATA.remove(WAREHOUSE_METADATA.tables[table_name])

    table = build_warehouse_table(table_name, dataframe, schema=schema)
    try:
        table.create(bind=engine, checkfirst=True)
    except Exception as exc:
        raise WarehouseTableError(f"Failed to create warehouse table '{table_name}': {exc}") from exc
    return table
