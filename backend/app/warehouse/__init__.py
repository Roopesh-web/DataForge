"""Warehouse package for enterprise dataset loading."""

__all__ = [
    "ensure_metadata_tables",
    "batch_insert_dataframe",
    "build_warehouse_table_name",
]


def __getattr__(name: str):
    if name == "ensure_metadata_tables":
        from app.warehouse.db_init import ensure_metadata_tables

        return ensure_metadata_tables
    if name == "batch_insert_dataframe":
        from app.warehouse.loader import batch_insert_dataframe

        return batch_insert_dataframe
    if name == "build_warehouse_table_name":
        from app.warehouse.exceptions import build_warehouse_table_name

        return build_warehouse_table_name
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
