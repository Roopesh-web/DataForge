import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from typing import Any

import pandas as pd
import streamlit as st

from dashboard import charts
from dashboard.api_client import (
    APIError,
    analyze_dataset,
    check_health,
    profile_dataset,
    quality_check,
    resolve_content_type,
    upload_file,
)
from dashboard.config import API_BASE_URL, LAYOUT, PAGE_ICON, PAGE_TITLE
from dashboard.ui import (
    inject_custom_css,
    render_column_list,
    render_hero,
    render_info_card,
    render_kpi_cards,
    render_plotly_chart,
    render_section_title,
)

NAV_OPTIONS = {
    "📤 File Upload": "upload",
    "📋 Dataset Overview": "overview",
    "📈 Analytics Explorer": "analytics",
    "✅ Data Quality": "quality",
}
NAV_LABELS = list(NAV_OPTIONS.keys())
NAV_BY_VALUE = {value: label for label, value in NAV_OPTIONS.items()}


def init_session_state() -> None:
    defaults = {
        "upload_result": None,
        "profile_result": None,
        "analytics_result": None,
        "quality_result": None,
        "stored_filename": None,
        "current_page": "upload",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar() -> str:
    st.sidebar.markdown('<div class="df-sidebar-brand">DataForge</div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        '<div class="df-sidebar-sub">Enterprise Data Engineering</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.divider()

    current_label = NAV_BY_VALUE.get(st.session_state.current_page, NAV_LABELS[0])
    page_label = st.sidebar.radio(
        "Navigation",
        options=NAV_LABELS,
        index=NAV_LABELS.index(current_label),
        label_visibility="collapsed",
    )
    st.session_state.current_page = NAV_OPTIONS[page_label]

    st.sidebar.divider()
    st.sidebar.markdown("##### 🌐 API Connection")
    st.sidebar.code(API_BASE_URL, language="text")

    try:
        health = check_health()
        st.sidebar.success(f"🟢 Online — {health.get('status', 'healthy')}")
    except APIError as exc:
        st.sidebar.error(f"🔴 Offline — {exc.message}")
    except Exception as exc:
        st.sidebar.error(f"🔴 Offline — {exc}")

    if st.session_state.stored_filename:
        st.sidebar.divider()
        st.sidebar.markdown("##### 📁 Active Dataset")
        st.sidebar.markdown(f"`{st.session_state.stored_filename}`")
        if st.session_state.upload_result:
            upload = st.session_state.upload_result
            st.sidebar.caption(
                f"**{upload.get('original_filename')}** · "
                f"{str(upload.get('file_type', '')).upper()}"
            )

    return st.session_state.current_page


def render_upload_page() -> None:
    render_hero(
        "File Upload",
        "Upload CSV, Excel (.xlsx), or JSON datasets and process them through the DataForge API.",
        "📤",
    )

    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
        render_section_title("Upload Dataset")
        uploaded_file = st.file_uploader(
            "Choose a dataset file",
            type=["csv", "xlsx", "json"],
            help="Supported formats: CSV, Excel (.xlsx), JSON",
            key="upload_file_input",
        )

        if uploaded_file is not None:
            with st.expander("📄 File Details", expanded=True):
                detail_cols = st.columns(3)
                detail_cols[0].metric("Filename", uploaded_file.name)
                detail_cols[1].metric("Size", f"{uploaded_file.size:,} B")
                detail_cols[2].metric("MIME", resolve_content_type(uploaded_file.name))

            if st.button(
                "🚀 Upload to DataForge",
                type="primary",
                use_container_width=True,
                key="btn_upload",
            ):
                with st.spinner("Uploading file to backend..."):
                    try:
                        content_type = resolve_content_type(uploaded_file.name)
                        result = upload_file(
                            filename=uploaded_file.name,
                            file_bytes=uploaded_file.getvalue(),
                            content_type=content_type,
                        )
                        st.session_state.upload_result = result
                        st.session_state.stored_filename = result["stored_filename"]
                        st.session_state.profile_result = None
                        st.session_state.analytics_result = None
                        st.session_state.quality_result = None
                        st.success("✅ File uploaded successfully.")
                    except APIError as exc:
                        st.error(f"❌ Upload failed: {exc.message}")
                    except Exception as exc:
                        st.error(f"❌ Upload failed: {exc}")

    with right:
        render_section_title("Quick Actions")
        st.markdown(
            "After uploading, profile the dataset for schema insights or run full analytics."
        )
        action_cols = st.columns(3)
        with action_cols[0]:
            if st.button("🔍 Profile Dataset", use_container_width=True, key="btn_profile_upload"):
                _run_profile()
        with action_cols[1]:
            if st.button("📊 Run Analytics", use_container_width=True, key="btn_analytics_upload"):
                _run_analytics()
        with action_cols[2]:
            if st.button("✅ Quality Check", use_container_width=True, key="btn_quality_upload"):
                _run_quality()

    if st.session_state.upload_result:
        upload = st.session_state.upload_result
        stored_name = upload.get("stored_filename", "—")
        stored_display = stored_name if len(stored_name) <= 24 else f"{stored_name[:21]}..."
        st.markdown("---")
        render_section_title("Upload Summary")
        render_kpi_cards(
            [
                ("📎", "Original File", upload.get("original_filename", "—"), "Client filename"),
                ("💾", "Stored File", stored_display, stored_name),
                ("📦", "File Size", f"{upload.get('size', 0):,} B", "Uploaded bytes"),
                ("🏷️", "File Type", str(upload.get("file_type", "—")).upper(), "Detected type"),
            ]
        )


def _run_profile() -> None:
    if not st.session_state.stored_filename:
        render_info_card("Upload a file before profiling.", "warning")
        return

    with st.spinner("Profiling dataset..."):
        try:
            st.session_state.profile_result = profile_dataset(st.session_state.stored_filename)
            st.success("✅ Dataset profiled successfully.")
        except APIError as exc:
            st.error(f"❌ Profiling failed: {exc.message}")
        except Exception as exc:
            st.error(f"❌ Profiling failed: {exc}")


def _run_analytics() -> None:
    if not st.session_state.stored_filename:
        render_info_card("Upload a file before running analytics.", "warning")
        return

    with st.spinner("Running analytics..."):
        try:
            st.session_state.analytics_result = analyze_dataset(
                st.session_state.stored_filename
            )
            st.success("✅ Analytics completed successfully.")
        except APIError as exc:
            st.error(f"❌ Analytics failed: {exc.message}")
        except Exception as exc:
            st.error(f"❌ Analytics failed: {exc}")


def _run_quality() -> None:
    if not st.session_state.stored_filename:
        render_info_card("Upload a file before running quality checks.", "warning")
        return

    with st.spinner("Running data quality checks..."):
        try:
            st.session_state.quality_result = quality_check(st.session_state.stored_filename)
            st.success("✅ Quality check completed successfully.")
        except APIError as exc:
            st.error(f"❌ Quality check failed: {exc.message}")
        except Exception as exc:
            st.error(f"❌ Quality check failed: {exc}")


def render_overview_page() -> None:
    render_hero(
        "Dataset Overview",
        "Explore dataset structure, schema inference, missing values, and column-level profiles.",
        "📋",
    )

    if not st.session_state.stored_filename:
        render_info_card("Upload a dataset on the File Upload page to get started.", "info")
        return

    action_cols = st.columns(2, gap="medium")
    with action_cols[0]:
        if st.button("🔄 Refresh Profile", use_container_width=True, key="btn_refresh_profile"):
            _run_profile()
    with action_cols[1]:
        if st.button("🔄 Refresh Analytics", use_container_width=True, key="btn_refresh_analytics"):
            _run_analytics()

    profile = st.session_state.profile_result
    analytics = st.session_state.analytics_result

    if not profile and not analytics:
        render_info_card("Run Profile or Analytics from the File Upload page.", "warning")
        return

    dataset_summary = (
        analytics.get("dataset_summary", {}) if analytics else _profile_summary(profile)
    )

    render_kpi_cards(
        [
            ("📏", "Rows", f"{dataset_summary.get('rows', profile.get('row_count', 0) if profile else 0):,}", "Total rows"),
            ("🧩", "Columns", f"{dataset_summary.get('columns', profile.get('column_count', 0) if profile else 0):,}", "Total columns"),
            (
                "🔢",
                "Numeric",
                str(len(dataset_summary.get("numeric_columns", profile.get("numeric_columns", []) if profile else []))),
                "Numeric fields",
            ),
            (
                "🕳️",
                "Missing",
                str(analytics.get("missing_values", {}).get("count", "—") if analytics else "—"),
                "Total null values",
            ),
        ]
    )

    tabs = st.tabs(["📌 Summary", "🗂️ Schema", "🕳️ Missing Values", "📑 Column Profiles"])

    with tabs[0]:
        _render_dataset_summary(profile, analytics)

    with tabs[1]:
        _render_schema(profile)

    with tabs[2]:
        _render_missing_values(profile, analytics)

    with tabs[3]:
        _render_column_profiles(profile)


def _profile_summary(profile: dict[str, Any] | None) -> dict[str, Any]:
    if not profile:
        return {}
    return {
        "rows": profile.get("row_count", 0),
        "columns": profile.get("column_count", 0),
        "numeric_columns": profile.get("numeric_columns", []),
        "categorical_columns": profile.get("categorical_columns", []),
        "datetime_columns": profile.get("datetime_columns", []),
    }


def _render_dataset_summary(
    profile: dict[str, Any] | None,
    analytics: dict[str, Any] | None,
) -> None:
    summary = analytics.get("dataset_summary", {}) if analytics else _profile_summary(profile)

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        render_column_list("Numeric Columns", summary.get("numeric_columns", []), "🔢")
        st.markdown("")
        render_column_list("Categorical Columns", summary.get("categorical_columns", []), "🏷️")

    with col_right:
        render_column_list("Datetime Columns", summary.get("datetime_columns", []), "📅")
        if profile:
            with st.expander("📎 Profiling Metadata", expanded=False):
                st.json(
                    {
                        "stored_filename": profile.get("stored_filename"),
                        "file_format": profile.get("file_format"),
                        "duplicate_rows": profile.get("duplicate_rows"),
                        "memory_usage_bytes": profile.get("memory_usage_bytes"),
                        "column_names": profile.get("column_names"),
                    }
                )


def _render_schema(profile: dict[str, Any] | None) -> None:
    if not profile:
        render_info_card("Run profiling to view schema details.", "info")
        return

    schema = profile.get("schema") or profile.get("inferred_schema") or {}
    schema_columns = schema.get("columns", [])
    if not schema_columns:
        render_info_card("No schema information available.", "warning")
        return

    st.dataframe(pd.DataFrame(schema_columns), use_container_width=True, hide_index=True)


def _render_missing_values(
    profile: dict[str, Any] | None,
    analytics: dict[str, Any] | None,
) -> None:
    top_left, top_right = st.columns(2, gap="medium")

    if analytics:
        missing = analytics.get("missing_values", {})
        with top_left:
            st.metric("Missing Count", f"{missing.get('count', 0):,}")
        with top_right:
            st.metric("Missing %", f"{missing.get('percentage', 0):.2f}%")

    if profile:
        render_plotly_chart(
            charts.missing_values_bar_chart(profile),
            key="overview_missing_values_chart",
        )
    elif not analytics:
        render_info_card("Run profiling or analytics to view missing values.", "info")


def _render_column_profiles(profile: dict[str, Any] | None) -> None:
    if not profile:
        render_info_card("Run profiling to view column profiles.", "info")
        return

    columns = profile.get("columns", [])
    if not columns:
        render_info_card("No column profiles available.", "warning")
        return

    for index, column in enumerate(columns):
        with st.expander(f"📊 {column['name']} · {column['datatype']}", expanded=index == 0):
            metric_cols = st.columns(3)
            metric_cols[0].metric("Null Count", column.get("null_count", 0))
            metric_cols[1].metric("Null %", f"{column.get('null_percentage', 0)}%")
            metric_cols[2].metric("Unique Values", column.get("unique_values", 0))
            st.caption(f"Raw dtype: `{column.get('raw_dtype')}`")
            if column.get("statistics"):
                st.json(column["statistics"])


def render_analytics_page() -> None:
    render_hero(
        "Analytics Explorer",
        "Deep statistical analysis with correlations, outliers, distributions, and interactive charts.",
        "📈",
    )

    if not st.session_state.stored_filename:
        render_info_card("Upload a dataset on the File Upload page to get started.", "info")
        return

    if not st.session_state.analytics_result:
        render_info_card("Run Analytics to explore charts and statistics.", "warning")
        if st.button("📊 Run Analytics", type="primary", key="btn_run_analytics_page"):
            _run_analytics()
        return

    analytics = st.session_state.analytics_result
    summary = analytics.get("dataset_summary", {})
    numeric_columns = summary.get("numeric_columns", [])
    categorical_columns = summary.get("categorical_columns", [])

    render_kpi_cards(
        [
            ("🔢", "Numeric Columns", str(len(numeric_columns)), "Columns analyzed numerically"),
            ("🏷️", "Categorical Columns", str(len(categorical_columns)), "Columns analyzed categorically"),
            ("📅", "Datetime Columns", str(len(summary.get("datetime_columns", []))), "Datetime fields"),
            ("🕳️", "Missing Cells", f"{analytics.get('missing_values', {}).get('count', 0):,}", "Total null values"),
        ]
    )

    tabs = st.tabs(
        [
            "📊 Statistics",
            "🔗 Correlations",
            "⚠️ Outliers",
            "🏷️ Categorical",
            "📅 Datetime",
            "📈 Charts",
        ]
    )

    with tabs[0]:
        _render_numeric_statistics(analytics)

    with tabs[1]:
        _render_correlations(analytics)

    with tabs[2]:
        _render_outlier_summary(analytics)

    with tabs[3]:
        _render_categorical_statistics(analytics)

    with tabs[4]:
        _render_datetime_statistics(analytics)

    with tabs[5]:
        _render_charts(analytics, numeric_columns, categorical_columns)


def _render_correlations(analytics: dict[str, Any]) -> None:
    chart_col, table_col = st.columns([1.2, 0.8], gap="large")

    with chart_col:
        render_plotly_chart(
            charts.correlation_heatmap(analytics),
            key="analytics_correlation_heatmap",
        )

    with table_col:
        with st.expander("📋 Correlation Matrix Data", expanded=True):
            matrix = analytics.get("correlation_matrix", {})
            if matrix.get("columns"):
                st.dataframe(
                    pd.DataFrame(
                        matrix.get("values", []),
                        columns=matrix.get("columns", []),
                        index=matrix.get("columns", []),
                    ),
                    use_container_width=True,
                )
            else:
                st.caption("Not enough numeric columns for correlation.")


def _render_numeric_statistics(analytics: dict[str, Any]) -> None:
    numeric_stats = analytics.get("numeric_statistics", {})
    if not numeric_stats:
        render_info_card("No numeric statistics available.", "info")
        return

    rows = [{"column": column, **stats} for column, stats in numeric_stats.items()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_outlier_summary(analytics: dict[str, Any]) -> None:
    outlier_data = analytics.get("outlier_detection", {})
    if not outlier_data:
        render_info_card("No outlier results available.", "info")
        return

    chart_col, table_col = st.columns([1.1, 0.9], gap="large")

    with chart_col:
        render_plotly_chart(
            charts.outlier_summary_chart(analytics),
            key="analytics_outlier_summary_chart",
        )

    with table_col:
        rows = [{"column": column, **result} for column, result in outlier_data.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_categorical_statistics(analytics: dict[str, Any]) -> None:
    categorical_stats = analytics.get("categorical_statistics", {})
    if not categorical_stats:
        render_info_card("No categorical statistics available.", "info")
        return

    for column, stats in categorical_stats.items():
        with st.expander(
            f"🏷️ {column} — {stats.get('unique_count', 0)} unique values",
            expanded=False,
        ):
            table_col, chart_col = st.columns([0.9, 1.1], gap="medium")
            frequencies = stats.get("frequencies") or stats.get("top_values") or []

            with table_col:
                if frequencies:
                    st.dataframe(
                        pd.DataFrame(frequencies),
                        use_container_width=True,
                        hide_index=True,
                    )

            with chart_col:
                if frequencies:
                    render_plotly_chart(
                        charts.category_distribution_chart(analytics, column),
                        key=f"analytics_categorical_chart_{column}",
                    )


def _render_datetime_statistics(analytics: dict[str, Any]) -> None:
    datetime_stats = analytics.get("datetime_statistics", {})
    if not datetime_stats:
        render_info_card("No datetime statistics available.", "info")
        return

    rows = [{"column": column, **stats} for column, stats in datetime_stats.items()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_charts(
    analytics: dict[str, Any],
    numeric_columns: list[str],
    categorical_columns: list[str],
) -> None:
    chart_tabs = st.tabs(
        [
            "📊 Histogram",
            "📦 Box Plot",
            "🔗 Correlation",
            "🕳️ Missing Values",
            "🏷️ Categories",
        ]
    )

    profile = st.session_state.profile_result

    with chart_tabs[0]:
        if numeric_columns:
            selected = st.selectbox("Numeric column", numeric_columns, key="hist_col_select")
            render_plotly_chart(
                charts.numeric_histogram(analytics, selected),
                key=f"charts_histogram_{selected}",
            )
            st.caption(
                "Histogram approximated from backend summary statistics when raw values "
                "are not exposed by the API."
            )
        else:
            render_info_card("No numeric columns available.", "info")

    with chart_tabs[1]:
        if numeric_columns:
            selected = st.selectbox("Numeric column", numeric_columns, key="box_col_select")
            render_plotly_chart(
                charts.numeric_box_plot(analytics, selected),
                key=f"charts_boxplot_{selected}",
            )
        else:
            render_info_card("No numeric columns available.", "info")

    with chart_tabs[2]:
        render_plotly_chart(
            charts.correlation_heatmap(analytics),
            key="charts_correlation_heatmap",
        )

    with chart_tabs[3]:
        if profile:
            render_plotly_chart(
                charts.missing_values_bar_chart(profile),
                key="charts_missing_values_bar",
            )
        else:
            render_info_card("Run profiling to render missing values chart.", "info")

    with chart_tabs[4]:
        if categorical_columns:
            selected = st.selectbox(
                "Categorical column",
                categorical_columns,
                key="cat_col_select",
            )
            render_plotly_chart(
                charts.category_distribution_chart(analytics, selected),
                key=f"charts_category_{selected}",
            )
        else:
            render_info_card("No categorical columns available.", "info")


def render_quality_page() -> None:
    render_hero(
        "Data Quality",
        "Enterprise validation checks for nulls, duplicates, types, ranges, regex, and categorical rules.",
        "✅",
    )

    if not st.session_state.stored_filename:
        render_info_card("Upload a dataset on the File Upload page to get started.", "info")
        return

    if st.button("✅ Run Quality Check", type="primary", key="btn_run_quality_page"):
        _run_quality()

    quality = st.session_state.quality_result
    if not quality:
        render_info_card("Run a quality check to view validation results.", "warning")
        return

    summary = quality.get("validation_summary", {})
    render_kpi_cards(
        [
            ("⭐", "Quality Score", f"{summary.get('quality_score', 0):.1f}", "Weighted score out of 100"),
            ("✅", "Passed Rules", str(summary.get("passed_rules", 0)), "Rules that passed validation"),
            ("❌", "Failed Rules", str(summary.get("failed_rules", 0)), "Rules that failed validation"),
            ("📋", "Total Rules", str(summary.get("total_rules", 0)), "Rules evaluated"),
        ]
    )

    tabs = st.tabs(["📌 Summary", "✅ Passed Rules", "❌ Failed Rules", "📄 Report"])

    with tabs[0]:
        col_left, col_right = st.columns(2, gap="large")
        with col_left:
            st.metric("Quality Score", f"{summary.get('quality_score', 0):.2f}")
            st.metric("Passed Rules", summary.get("passed_rules", 0))
        with col_right:
            st.metric("Failed Rules", summary.get("failed_rules", 0))
            st.metric("Total Rules", summary.get("total_rules", 0))

        with st.expander("📎 Validation Summary Details", expanded=False):
            st.json(summary)

    with tabs[1]:
        passed_rules = quality.get("passed_rules", [])
        if passed_rules:
            st.dataframe(pd.DataFrame(passed_rules), use_container_width=True, hide_index=True)
        else:
            render_info_card("No passed rules to display.", "info")

    with tabs[2]:
        failed_rules = quality.get("failed_rules", [])
        if failed_rules:
            st.dataframe(pd.DataFrame(failed_rules), use_container_width=True, hide_index=True)
        else:
            render_info_card("No failed rules. Dataset passed all quality checks.", "success")

    with tabs[3]:
        with st.expander("📄 Validation Report", expanded=True):
            st.json(quality.get("validation_report", {}))


def main() -> None:
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state="expanded",
    )

    inject_custom_css()
    init_session_state()
    page = render_sidebar()

    if page == "upload":
        render_upload_page()
    elif page == "overview":
        render_overview_page()
    elif page == "analytics":
        render_analytics_page()
    else:
        render_quality_page()


if __name__ == "__main__":
    main()
