"""Dashboard UI components, styling, and layout helpers."""

from typing import Any

import plotly.graph_objects as go
import streamlit as st

COLORS = {
    "primary": "#3B82F6",
    "primary_dark": "#1D4ED8",
    "accent": "#22D3EE",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "surface": "#111827",
    "surface_alt": "#1F2937",
    "surface_card": "#172033",
    "border": "#334155",
    "text": "#F8FAFC",
    "text_muted": "#94A3B8",
    "chart_bg": "#0F172A",
    "chart_grid": "#1E293B",
}

CHART_COLORWAY = [COLORS["primary"], COLORS["accent"], COLORS["success"], COLORS["warning"], "#A78BFA"]


def inject_custom_css() -> None:
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

            :root {{
                --df-primary: {COLORS["primary"]};
                --df-surface: {COLORS["surface"]};
                --df-card: {COLORS["surface_card"]};
                --df-border: {COLORS["border"]};
                --df-text: {COLORS["text"]};
                --df-muted: {COLORS["text_muted"]};
            }}

            html, body, [class*="css"] {{
                font-family: 'Inter', system-ui, sans-serif;
            }}

            .stApp {{
                background: linear-gradient(180deg, #0B1220 0%, #0F172A 100%);
            }}

            .block-container {{
                padding-top: 1.25rem;
                padding-bottom: 5rem;
                max-width: 1440px;
            }}

            .df-hero {{
                background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 45%, #0EA5E9 100%);
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 18px;
                padding: 2rem 2.25rem;
                margin-bottom: 1.5rem;
                color: white;
                box-shadow: 0 18px 40px rgba(15, 23, 42, 0.35);
            }}

            .df-hero h1 {{
                margin: 0;
                font-size: 2.1rem;
                font-weight: 700;
                letter-spacing: -0.03em;
                color: white !important;
            }}

            .df-hero p {{
                margin: 0.75rem 0 0 0;
                font-size: 1.02rem;
                line-height: 1.65;
                color: rgba(255,255,255,0.92) !important;
            }}

            .df-kpi-card {{
                background: var(--df-card);
                border: 1px solid var(--df-border);
                border-radius: 16px;
                padding: 1.15rem 1.3rem;
                min-height: 118px;
                box-shadow: 0 8px 24px rgba(2, 6, 23, 0.28);
            }}

            .df-kpi-label {{
                color: var(--df-muted);
                font-size: 0.78rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.45rem;
            }}

            .df-kpi-value {{
                color: var(--df-text);
                font-size: 1.8rem;
                font-weight: 700;
                line-height: 1.15;
            }}

            .df-section-title {{
                color: var(--df-text);
                font-size: 1.2rem;
                font-weight: 600;
                margin: 1.75rem 0 0.9rem 0;
                letter-spacing: -0.01em;
            }}

            .df-sidebar-brand {{
                font-size: 1.4rem;
                font-weight: 700;
                color: #E2E8F0;
                margin-bottom: 0.2rem;
            }}

            .df-sidebar-sub {{
                color: var(--df-muted);
                font-size: 0.86rem;
                margin-bottom: 0.75rem;
            }}

            .df-footer {{
                margin-top: 2.5rem;
                padding: 1rem 0 0.5rem 0;
                border-top: 1px solid var(--df-border);
                color: var(--df-muted);
                font-size: 0.85rem;
                text-align: center;
            }}

            .df-timeline-item {{
                background: var(--df-card);
                border: 1px solid var(--df-border);
                border-left: 4px solid var(--df-primary);
                border-radius: 12px;
                padding: 0.95rem 1rem;
                margin-bottom: 0.75rem;
            }}

            .df-timeline-title {{
                color: var(--df-text);
                font-weight: 600;
                font-size: 0.95rem;
            }}

            .df-timeline-meta {{
                color: var(--df-muted);
                font-size: 0.82rem;
                margin-top: 0.25rem;
            }}

            div[data-testid="stSidebar"] {{
                background: linear-gradient(180deg, #0B1220 0%, #111827 100%);
                border-right: 1px solid var(--df-border);
            }}

            div[data-testid="stSidebar"] .stRadio label {{
                padding: 0.45rem 0.2rem;
            }}

            div[data-testid="stMetric"] {{
                background: var(--df-card);
                border: 1px solid var(--df-border);
                border-radius: 14px;
                padding: 0.9rem 1rem;
            }}

            .stTabs [data-baseweb="tab-list"] {{
                gap: 10px;
            }}

            .stTabs [data-baseweb="tab"] {{
                border-radius: 10px 10px 0 0;
                padding: 0.7rem 1rem;
                font-weight: 600;
            }}

            .stDataFrame, [data-testid="stDataFrame"] {{
                border-radius: 14px;
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


def render_footer() -> None:
    st.markdown(
        """
        <div class="df-footer">
            DataForge v1.0 · FastAPI · Streamlit · PostgreSQL
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_timeline(events: list[dict[str, Any]]) -> None:
    if not events:
        render_info_card("No dataset activity recorded yet.", "info")
        return

    for event in events[:12]:
        status = event.get("status", "success")
        border_color = COLORS["success"] if status == "success" else COLORS["danger"]
        st.markdown(
            f"""
            <div class="df-timeline-item" style="border-left-color: {border_color};">
                <div class="df-timeline-title">{event.get('title', 'Event')}</div>
                <div class="df-timeline-meta">{event.get('detail', '')}</div>
                <div class="df-timeline-meta">{event.get('timestamp', '')} · {event.get('category', '')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_plotly_chart(
    figure: go.Figure,
    key: str,
    *,
    use_container_width: bool = True,
) -> None:
    styled = apply_chart_theme(figure)
    st.plotly_chart(
        styled,
        use_container_width=use_container_width,
        key=key,
    )


def apply_chart_theme(figure: go.Figure) -> go.Figure:
    figure.update_layout(
        template="plotly_dark",
        font={"family": "Inter, system-ui, sans-serif", "color": COLORS["text"], "size": 13},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=COLORS["chart_bg"],
        margin={"l": 48, "r": 28, "t": 64, "b": 48},
        title_font_size=17,
        title_x=0.02,
        colorway=CHART_COLORWAY,
        hovermode="closest",
        height=max(figure.layout.height or 430, 380),
    )
    figure.update_xaxes(
        gridcolor=COLORS["chart_grid"],
        linecolor=COLORS["border"],
        zerolinecolor=COLORS["border"],
    )
    figure.update_yaxes(
        gridcolor=COLORS["chart_grid"],
        linecolor=COLORS["border"],
        zerolinecolor=COLORS["border"],
    )
    return figure


def render_info_card(message: str, kind: str = "info") -> None:
    icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
    handlers = {"info": st.info, "success": st.success, "warning": st.warning, "error": st.error}
    handlers.get(kind, st.info)(f"{icons.get(kind, 'ℹ️')} {message}")


def render_column_list(title: str, items: list[str], icon: str) -> None:
    st.markdown(f"**{icon} {title}**")
    if items:
        for item in items:
            st.markdown(f"- `{item}`")
    else:
        st.caption("None detected")
