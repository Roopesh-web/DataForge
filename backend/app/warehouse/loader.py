from typing import Any

import polars as pl
from sqlalchemy import Table, insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.warehouse.exceptions import WarehouseLoadError, sanitize_identifier
from app.warehouse.table_manager import DEFAULT_BATCH_SIZE, ensure_warehouse_table


def _prepare_records(dataframe: pl.DataFrame) -> list[dict[str, Any]]:
    column_map = {name: sanitize_identifier(name) for name in dataframe.columns}
    renamed = dataframe.rename(column_map)
    return renamed.to_dicts()


def batch_insert_dataframe(
    session: Session,
    engine: Engine,
    table_name: str,
    dataframe: pl.DataFrame,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> int:
    if dataframe.height == 0:
        return 0

    table = ensure_warehouse_table(engine, table_name, dataframe)
    records = _prepare_records(dataframe)
    total_inserted = 0

    try:
        for offset in range(0, len(records), batch_size):
            batch = records[offset : offset + batch_size]
            session.execute(insert(table), batch)
            total_inserted += len(batch)
    except Exception as exc:
        raise WarehouseLoadError(f"Batch insert failed for table '{table_name}': {exc}") from exc

    return total_inserted
