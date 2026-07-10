from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboard.ui import CHART_COLORWAY, COLORS, apply_chart_theme


def _base_layout_kwargs(height: int = 430) -> dict[str, Any]:
    return {
        "height": height,
        "margin": {"l": 48, "r": 28, "t": 64, "b": 48},
    }


def dataset_timeline_chart(events: list[dict[str, Any]]) -> go.Figure:
    if not events:
        return go.Figure()

    frame = pd.DataFrame(events[:10]).copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
    frame = frame.dropna(subset=["timestamp"]).sort_values("timestamp")

    if frame.empty:
        return go.Figure()

    figure = px.scatter(
        frame,
        x="timestamp",
        y="title",
        color="category",
        size_max=12,
        title="Dataset Activity Timeline",
        labels={"timestamp": "Time", "title": "Event", "category": "Category"},
        color_discrete_sequence=CHART_COLORWAY,
    )
    figure.update_traces(marker={"size": 14, "line": {"width": 1, "color": COLORS["border"]}})
    figure.update_layout(**_base_layout_kwargs(460), showlegend=True, legend_title_text="")
    return apply_chart_theme(figure)


def missing_values_bar_chart(profile: dict[str, Any]) -> go.Figure:
    columns = profile.get("columns", [])
    if not columns:
        return go.Figure()

    frame = pd.DataFrame(
        {
            "column": [column["name"] for column in columns],
            "missing_count": [column["null_count"] for column in columns],
            "missing_percentage": [column["null_percentage"] for column in columns],
        }
    )

    figure = px.bar(
        frame,
        x="column",
        y="missing_count",
        color="missing_percentage",
        title="Missing Values by Column",
        labels={"column": "Column", "missing_count": "Missing Count", "missing_percentage": "Missing %"},
        color_continuous_scale=["#1E293B", COLORS["danger"]],
    )
    figure.update_layout(**_base_layout_kwargs(), coloraxis_showscale=True)
    return apply_chart_theme(figure)


def correlation_heatmap(analytics: dict[str, Any]) -> go.Figure:
    matrix = analytics.get("correlation_matrix", {})
    column_names = matrix.get("columns", [])
    values = matrix.get("values", [])

    if len(column_names) < 2 or not values:
        return go.Figure()

    frame = pd.DataFrame(values, columns=column_names, index=column_names)
    figure = px.imshow(
        frame,
        text_auto=".2f",
        color_continuous_scale=[COLORS["danger"], COLORS["chart_bg"], COLORS["primary"]],
        zmin=-1,
        zmax=1,
        title="Pearson Correlation Heatmap",
        aspect="auto",
    )
    figure.update_layout(**_base_layout_kwargs(500))
    return apply_chart_theme(figure)


def numeric_histogram(analytics: dict[str, Any], column_name: str) -> go.Figure:
    stats = analytics.get("numeric_statistics", {}).get(column_name)
    if not stats:
        return go.Figure()

    mean = stats.get("mean")
    std = stats.get("standard_deviation")
    minimum = stats.get("min")
    maximum = stats.get("max")

    if mean is None or std in (None, 0):
        frame = pd.DataFrame(
            {
                "metric": ["Min", "Median", "Mean", "Max"],
                "value": [stats.get("min"), stats.get("median"), stats.get("mean"), stats.get("max")],
            }
        )
        figure = px.bar(
            frame,
            x="metric",
            y="value",
            title=f"Numeric Summary — {column_name}",
            color="metric",
            color_discrete_sequence=CHART_COLORWAY,
        )
        figure.update_layout(**_base_layout_kwargs(), showlegend=False)
        return apply_chart_theme(figure)

    samples = np.random.default_rng(42).normal(loc=mean, scale=std, size=1000)
    if minimum is not None:
        samples = samples[samples >= minimum]
    if maximum is not None:
        samples = samples[samples <= maximum]
    if samples.size == 0:
        samples = np.array([mean])

    figure = px.histogram(
        pd.DataFrame({"value": samples}),
        x="value",
        nbins=30,
        title=f"Approximate Distribution — {column_name}",
        labels={"value": column_name},
        color_discrete_sequence=[COLORS["primary"]],
    )
    figure.update_layout(**_base_layout_kwargs(), showlegend=False, bargap=0.05)
    figure.update_traces(marker_line_color=COLORS["accent"], marker_line_width=0.8)
    return apply_chart_theme(figure)


def numeric_box_plot(analytics: dict[str, Any], column_name: str) -> go.Figure:
    stats = analytics.get("numeric_statistics", {}).get(column_name, {})
    outliers = analytics.get("outlier_detection", {}).get(column_name, {})

    figure = go.Figure()
    figure.add_trace(
        go.Box(
            name=column_name,
            q1=[outliers.get("lower_bound") or stats.get("min")],
            median=[stats.get("median")],
            q3=[outliers.get("upper_bound") or stats.get("max")],
            lowerfence=[stats.get("min")],
            upperfence=[stats.get("max")],
            mean=[stats.get("mean")],
            boxpoints="outliers",
            marker_color=COLORS["accent"],
            line_color=COLORS["primary"],
            fillcolor="rgba(59, 130, 246, 0.25)",
        )
    )
    figure.update_layout(**_base_layout_kwargs(), title=f"Box Plot — {column_name}", showlegend=False)
    return apply_chart_theme(figure)


def category_distribution_chart(analytics: dict[str, Any], column_name: str) -> go.Figure:
    stats = analytics.get("categorical_statistics", {}).get(column_name)
    if not stats:
        return go.Figure()

    frequencies = stats.get("frequencies") or stats.get("top_values") or []
    frame = pd.DataFrame(frequencies)
    if frame.empty:
        return go.Figure()

    figure = px.bar(
        frame,
        x="value",
        y="frequency",
        title=f"Category Distribution — {column_name}",
        color="frequency",
        color_continuous_scale=["#1E3A8A", COLORS["accent"]],
        labels={"value": "Category", "frequency": "Count"},
    )
    figure.update_layout(**_base_layout_kwargs(), showlegend=False)
    return apply_chart_theme(figure)


def outlier_summary_chart(analytics: dict[str, Any]) -> go.Figure:
    outlier_data = analytics.get("outlier_detection", {})
    if not outlier_data:
        return go.Figure()

    frame = pd.DataFrame(
        [{"column": column, "outlier_count": result.get("outlier_count", 0)} for column, result in outlier_data.items()]
    )

    figure = px.bar(
        frame,
        x="column",
        y="outlier_count",
        title="Outlier Count by Numeric Column (IQR)",
        color="outlier_count",
        color_continuous_scale=["#422006", COLORS["warning"]],
    )
    figure.update_layout(**_base_layout_kwargs(), showlegend=False)
    return apply_chart_theme(figure)
