import pytest

from app.warehouse.exceptions import build_warehouse_table_name, sanitize_identifier


def test_sanitize_identifier_replaces_invalid_characters():
    assert sanitize_identifier("Sales Data!") == "sales_data"


def test_build_warehouse_table_name_is_stable_and_prefixed():
    first = build_warehouse_table_name("abc-123.csv")
    second = build_warehouse_table_name("abc-123.csv")

    assert first == second
    assert first.startswith("wh_")
