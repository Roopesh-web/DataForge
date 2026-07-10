"""Dashboard UI components, styling, and layout helpers."""

from typing import Any

import plotly.graph_objects as go
import streamlit as st

# Professional color palette
COLORS = {
    "primary": "#1E3A5F",
    "accent": "#3B82F6",
    "accent_light": "#60A5FA",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "surface": "#F8FAFC",
    "surface_alt": "#EEF2FF",
    "border": "#E2E8F0",
    "text": "#1E293B",
    "text_muted": "#64748B",
}

CHART_TEMPLATE = {
    "layout": {
        "font": {"family": "Inter, system-ui, sans-serif", "color": COLORS["text"]},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": COLORS["surface"],
        "colorway": [COLORS["accent"], COLORS["primary"], COLORS["success"], COLORS["warning"]],
        "margin": {"l": 40, "r": 24, "t": 56, "b": 40},
    }
}


def inject_custom_css() -> None:
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

            html, body, [class*="css"] {{
                font-family: 'Inter', system-ui, sans-serif;
            }}

            .block-container {{
                padding-top: 1.5rem;
                padding-bottom: 2rem;
                max-width: 1400px;
            }}

            .df-hero {{
                background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["accent"]} 100%);
                border-radius: 16px;
                padding: 2rem 2.25rem;
                margin-bottom: 1.75rem;
                color: white;
                box-shadow: 0 10px 30px rgba(30, 58, 95, 0.18);
            }}

            .df-hero h1 {{
                margin: 0;
                font-size: 2rem;
                font-weight: 700;
                letter-spacing: -0.02em;
                color: white !important;
            }}

            .df-hero p {{
                margin: 0.65rem 0 0 0;
                font-size: 1rem;
                opacity: 0.92;
                line-height: 1.6;
                color: rgba(255,255,255,0.95) !important;
            }}

            .df-kpi-card {{
                background: {COLORS["surface"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 14px;
                padding: 1.1rem 1.25rem;
                min-height: 108px;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
            }}

            .df-kpi-label {{
                color: {COLORS["text_muted"]};
                font-size: 0.82rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.04em;
                margin-bottom: 0.35rem;
            }}

            .df-kpi-value {{
                color: {COLORS["text"]};
                font-size: 1.65rem;
                font-weight: 700;
                line-height: 1.2;
            }}

            .df-section-title {{
                color: {COLORS["text"]};
                font-size: 1.15rem;
                font-weight: 600;
                margin: 1.5rem 0 0.75rem 0;
            }}

            .df-sidebar-brand {{
                font-size: 1.35rem;
                font-weight: 700;
                color: {COLORS["primary"]};
                margin-bottom: 0.15rem;
            }}

            .df-sidebar-sub {{
                color: {COLORS["text_muted"]};
                font-size: 0.85rem;
                margin-bottom: 0.5rem;
            }}

            div[data-testid="stSidebar"] {{
                background-color: #FBFDFF;
                border-right: 1px solid {COLORS["border"]};
            }}

            div[data-testid="stMetric"] {{
                background: {COLORS["surface"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 12px;
                padding: 0.85rem 1rem;
            }}

            .stTabs [data-baseweb="tab-list"] {{
                gap: 8px;
            }}

            .stTabs [data-baseweb="tab"] {{
                border-radius: 8px 8px 0 0;
                padding: 0.65rem 1rem;
                font-weight: 600;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str, icon: str = "📊") -> None:
    st.markdown(
        f"""
        <div class="df-hero">
            <h1>{icon} {title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_cards(metrics: list[tuple[str, str, str, str]]) -> None:
    """Render KPI cards. Each metric: (icon, label, value, help_text)."""
    columns = st.columns(len(metrics), gap="medium")
    for column, (icon, label, value, help_text) in zip(columns, metrics):
        with column:
            st.markdown(
                f"""
                <div class="df-kpi-card" title="{help_text}">
                    <div class="df-kpi-label">{icon} {label}</div>
                    <div class="df-kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_section_title(title: str) -> None:
    st.markdown(f'<div class="df-section-title">{title}</div>', unsafe_allow_html=True)


def render_plotly_chart(
    figure: go.Figure,
    key: str,
    *,
    use_container_width: bool = True,
) -> None:
    """Render a plotly chart with a guaranteed unique Streamlit key."""
    styled = apply_chart_theme(figure)
    st.plotly_chart(
        styled,
        use_container_width=use_container_width,
        key=key,
    )


def apply_chart_theme(figure: go.Figure) -> go.Figure:
    figure.update_layout(
        template="plotly_white",
        font=CHART_TEMPLATE["layout"]["font"],
        paper_bgcolor=CHART_TEMPLATE["layout"]["paper_bgcolor"],
        plot_bgcolor=CHART_TEMPLATE["layout"]["plot_bgcolor"],
        margin=CHART_TEMPLATE["layout"]["margin"],
        title_font_size=16,
        title_x=0.02,
    )
    return figure


def render_info_card(message: str, kind: str = "info") -> None:
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
    }
    handlers = {
        "info": st.info,
        "success": st.success,
        "warning": st.warning,
        "error": st.error,
    }
    handlers.get(kind, st.info)(f"{icons.get(kind, 'ℹ️')} {message}")


def render_column_list(title: str, items: list[str], icon: str) -> None:
    st.markdown(f"**{icon} {title}**")
    if items:
        for item in items:
            st.markdown(f"- `{item}`")
    else:
        st.caption("None detected")
