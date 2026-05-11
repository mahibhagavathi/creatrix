import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# ── Shared Plotly Theme ──────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#7b8fa6"),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.06)",
        tickfont=dict(size=11, color="#4a5568"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.06)",
        tickfont=dict(size=11, color="#4a5568"),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(255,255,255,0.06)",
        font=dict(color="#7b8fa6"),
    ),
)


def render_subscriber_growth_chart(metrics: dict):
    """Render animated subscriber growth line chart."""
    monthly = metrics.get("monthly_subscribers", [])
    if not monthly:
        st.info("Subscriber growth data not available.")
        return

    months = [m["month"] for m in monthly]
    subs = [m["subscribers"] for m in monthly]

    fig = go.Figure()

    # Area fill
    fig.add_trace(go.Scatter(
        x=months, y=subs,
        fill="tozeroy",
        fillcolor="rgba(79,158,255,0.06)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False,
        hoverinfo="skip"
    ))

    # Main line
    fig.add_trace(go.Scatter(
        x=months, y=subs,
        mode="lines+markers",
        name="Subscribers",
        line=dict(color="#4f9eff", width=2.5, shape="spline"),
        marker=dict(
            color="#4f9eff", size=5,
            line=dict(color="#0d1117", width=2)
        ),
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} subscribers<extra></extra>"
    ))

    # YoY growth annotation
    if len(subs) >= 12:
        yoy = ((subs[-1] - subs[0]) / subs[0] * 100) if subs[0] > 0 else 0
        sign = "+" if yoy >= 0 else ""
        color = "#00ff9d" if yoy >= 0 else "#ff4d6d"
        fig.add_annotation(
            x=months[-1], y=subs[-1],
            text=f"YoY {sign}{yoy:.1f}%",
            showarrow=False,
            xanchor="right",
            font=dict(color=color, size=12, family="Syne"),
            bgcolor="rgba(0,0,0,0.5)",
            borderpad=4,
            yshift=20
        )

    layout = dict(**PLOT_LAYOUT)
    layout["height"] = 300
    layout["yaxis"]["tickformat"] = ".2s"
    fig.update_layout(**layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_views_growth_chart(metrics: dict):
    """Render views growth line chart."""
    monthly = metrics.get("monthly_views", [])
    if not monthly:
        st.info("Views growth data not available.")
        return

    months = [m["month"] for m in monthly]
    views = [m["views"] for m in monthly]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=months, y=views,
        fill="tozeroy",
        fillcolor="rgba(0,212,255,0.06)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=months, y=views,
        mode="lines+markers",
        name="Views",
        line=dict(color="#00d4ff", width=2.5, shape="spline"),
        marker=dict(
            color="#00d4ff", size=5,
            line=dict(color="#0d1117", width=2)
        ),
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} views<extra></extra>"
    ))

    layout = dict(**PLOT_LAYOUT)
    layout["height"] = 300
    layout["yaxis"]["tickformat"] = ".2s"
    fig.update_layout(**layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_engagement_chart(videos_data: list, metrics: dict):
    """Render per-video engagement bar chart for last 50 videos."""
    if not videos_data:
        st.info("Video data not available.")
        return

    df = pd.DataFrame(videos_data).head(50)
    df = df.sort_values("view_count", ascending=False).reset_index(drop=True)
    df["title_short"] = df["title"].apply(lambda t: t[:25] + "…" if len(t) > 25 else t)
    df["color"] = df["is_short"].apply(lambda x: "#8b5cf6" if x else "#4f9eff")

    fig = go.Figure()

    # Long-form videos
    lf = df[~df["is_short"]]
    fig.add_trace(go.Bar(
        x=lf.index,
        y=lf["view_count"],
        name="Long-form",
        marker_color="#4f9eff",
        marker_opacity=0.8,
        hovertemplate="<b>%{customdata}</b><br>Views: %{y:,.0f}<extra></extra>",
        customdata=lf["title_short"]
    ))

    # Shorts
    sh = df[df["is_short"]]
    fig.add_trace(go.Bar(
        x=sh.index,
        y=sh["view_count"],
        name="Shorts",
        marker_color="#8b5cf6",
        marker_opacity=0.8,
        hovertemplate="<b>%{customdata}</b><br>Views: %{y:,.0f}<extra></extra>",
        customdata=sh["title_short"]
    ))

    layout = dict(**PLOT_LAYOUT)
    layout["height"] = 350
    layout["barmode"] = "overlay"
    layout["yaxis"]["tickformat"] = ".2s"
    layout["xaxis"]["title"] = "Video Rank (by views)"
    layout["yaxis"]["title"] = "Views"
    layout["title"] = dict(
        text="Video Performance Distribution",
        font=dict(family="Syne", size=14, color="#e8f0fe"),
        x=0
    )
    fig.update_layout(**layout)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_content_distribution_chart(metrics: dict, videos_data: list):
    """Render content type donut + upload day distribution."""
    col1, col2 = st.columns(2)

    with col1:
        # Shorts vs Long-form donut
        shorts = metrics.get("shorts_count", 0)
        longform = metrics.get("longform_count", 0)
        total = shorts + longform

        if total > 0:
            fig = go.Figure(go.Pie(
                labels=["Long-form", "Shorts"],
                values=[longform, shorts],
                hole=0.65,
                marker=dict(
                    colors=["#4f9eff", "#8b5cf6"],
                    line=dict(color="#080b14", width=2)
                ),
                textinfo="label+percent",
                textfont=dict(family="Syne", size=12, color="#e8f0fe"),
                hovertemplate="%{label}: %{value} videos (%{percent})<extra></extra>"
            ))

            fig.add_annotation(
                text=f"<b>{total}</b><br>videos",
                x=0.5, y=0.5,
                font=dict(family="Syne", size=16, color="#e8f0fe"),
                showarrow=False,
                align="center"
            )

            layout = dict(**PLOT_LAYOUT)
            layout["height"] = 300
            layout["title"] = dict(
                text="Content Type Split",
                font=dict(family="Syne", size=14, color="#e8f0fe"),
                x=0
            )
            layout["showlegend"] = True
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Content distribution data not available.")

    with col2:
        # Upload day bar chart
        day_dist = metrics.get("upload_day_distribution", {})
        if day_dist:
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            days = [d for d in day_order if d in day_dist]
            counts = [day_dist[d] for d in days]

            colors = ["#00d4ff" if d == metrics.get("best_upload_day") else "#4f9eff40"
                      for d in days]

            fig = go.Figure(go.Bar(
                x=days,
                y=counts,
                marker_color=colors,
                hovertemplate="%{x}: %{y} uploads<extra></extra>"
            ))

            layout = dict(**PLOT_LAYOUT)
            layout["height"] = 300
            layout["title"] = dict(
                text="Upload Day Distribution",
                font=dict(family="Syne", size=14, color="#e8f0fe"),
                x=0
            )
            layout["yaxis"]["title"] = "Upload Count"
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Upload day data not available.")
