"""Dashboard session state helpers and aggregated metrics."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import streamlit as st

from dashboard.api_client import APIError, get_warehouse_history


def ensure_app_state() -> None:
    defaults = {
        "upload_result": None,
        "profile_result": None,
        "analytics_result": None,
        "quality_result": None,
        "warehouse_result": None,
        "stored_filename": None,
        "current_page": "home",
        "upload_history": [],
        "activity_timeline": [],
        "settings_api_url": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def record_upload(result: dict[str, Any]) -> None:
    entry = {
        "original_filename": result.get("original_filename"),
        "stored_filename": result.get("stored_filename"),
        "file_type": result.get("file_type"),
        "size": result.get("size"),
        "timestamp": result.get("timestamp") or datetime.now(timezone.utc).isoformat(),
    }
    history = list(st.session_state.upload_history)
    history.insert(0, entry)
    st.session_state.upload_history = history[:25]
    _append_timeline(
        title="File Uploaded",
        detail=entry["original_filename"],
        status="success",
        timestamp=entry["timestamp"],
        category="upload",
    )


def record_activity(title: str, detail: str, status: str = "success", category: str = "action") -> None:
    _append_timeline(
        title=title,
        detail=detail,
        status=status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        category=category,
    )


def _append_timeline(
    title: str,
    detail: str,
    status: str,
    timestamp: str,
    category: str,
) -> None:
    timeline = list(st.session_state.activity_timeline)
    timeline.insert(
        0,
        {
            "title": title,
            "detail": detail,
            "status": status,
            "timestamp": timestamp,
            "category": category,
        },
    )
    st.session_state.activity_timeline = timeline[:30]


def _safe_rows_from_profile(profile: dict[str, Any] | None) -> int:
    if not profile:
        return 0
    return int(profile.get("row_count") or 0)


def _safe_rows_from_analytics(analytics: dict[str, Any] | None) -> int:
    if not analytics:
        return 0
    return int(analytics.get("dataset_summary", {}).get("rows") or 0)


def fetch_warehouse_loads() -> list[dict[str, Any]]:
    try:
        payload = get_warehouse_history(limit=50)
        return payload.get("loads", [])
    except (APIError, Exception):
        return []


def build_dashboard_metrics() -> dict[str, Any]:
    upload_history = st.session_state.upload_history
    warehouse_loads = fetch_warehouse_loads()

    total_datasets = len(upload_history)
    if st.session_state.upload_result and not any(
        item.get("stored_filename") == st.session_state.upload_result.get("stored_filename")
        for item in upload_history
    ):
        total_datasets += 1

    rows_processed = 0
    if st.session_state.profile_result:
        rows_processed = max(rows_processed, _safe_rows_from_profile(st.session_state.profile_result))
    if st.session_state.analytics_result:
        rows_processed = max(rows_processed, _safe_rows_from_analytics(st.session_state.analytics_result))
    rows_processed += sum(int(item.get("rows_loaded") or 0) for item in warehouse_loads if item.get("status") == "success")

    quality_scores: list[float] = []
    if st.session_state.quality_result:
        score = st.session_state.quality_result.get("validation_summary", {}).get("quality_score")
        if score is not None:
            quality_scores.append(float(score))

    avg_quality = round(sum(quality_scores) / len(quality_scores), 1) if quality_scores else None
    warehouse_tables = len({item.get("table_name") for item in warehouse_loads if item.get("status") == "success"})

    return {
        "total_datasets": total_datasets,
        "rows_processed": rows_processed,
        "average_quality_score": avg_quality,
        "warehouse_tables": warehouse_tables,
        "warehouse_loads": warehouse_loads,
        "upload_history": upload_history,
        "timeline": st.session_state.activity_timeline,
    }


def build_recent_uploads_table() -> list[dict[str, Any]]:
    rows = list(st.session_state.upload_history)
    current = st.session_state.upload_result
    if current and not any(item.get("stored_filename") == current.get("stored_filename") for item in rows):
        rows.insert(
            0,
            {
                "original_filename": current.get("original_filename"),
                "stored_filename": current.get("stored_filename"),
                "file_type": current.get("file_type"),
                "size": current.get("size"),
                "timestamp": current.get("timestamp"),
            },
        )
    return rows
