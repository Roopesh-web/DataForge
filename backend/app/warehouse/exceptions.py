import re
import uuid


class WarehouseError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class WarehouseLoadError(WarehouseError):
    pass


class WarehouseTableError(WarehouseError):
    pass


def sanitize_identifier(value: str, max_length: int = 63) -> str:
    cleaned = re.sub(r"[^\w]+", "_", value.lower()).strip("_")
    if not cleaned:
        cleaned = "dataset"
    if cleaned in {"id", "index"}:
        cleaned = f"col_{cleaned}"
    if cleaned[0].isdigit():
        cleaned = f"ds_{cleaned}"
    return cleaned[:max_length]


def build_warehouse_table_name(stored_filename: str) -> str:
    stem = stored_filename.rsplit(".", 1)[0]
    safe_stem = sanitize_identifier(stem)
    suffix = uuid.uuid5(uuid.NAMESPACE_DNS, stored_filename).hex[:8]
    table_name = f"wh_{safe_stem}_{suffix}"
    return sanitize_identifier(table_name, max_length=63)
