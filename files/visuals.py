"""
visuals.py — All Plotly chart builders.
Each function returns a go.Figure ready for st.plotly_chart().
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from data_loader import query_df

# ── Shared palette ────────────────────────────────────────────
PALETTE   = ["#1A3C5E", "#2E6DA4", "#4FAAD7", "#7DC8E8",
             "#F4A300", "#E07B00", "#C45200", "#8B1A1A"]
BG        = "rgba(0,0,0,0)"
FONT_FAM  = "Inter, sans-serif"


def _base_layout(**kwargs) -> dict:
    return dict(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family=FONT_FAM, color="#E8EDF2", size=12),
        margin=dict(l=40, r=20, t=50, b=40),
        **kwargs
    )


# ─────────────────────────────────────────────────────────────────────────────
# 1. Compliance Heatmap — channels × compliance score
# ─────────────────────────────────────────────────────────────────────────────

def compliance_heatmap() -> go.Figure:
    df = query_df("""
        SELECT channel_name, category, compliance_score
        FROM   channels
        ORDER BY compliance_score DESC
    """)
    pivot = df.pivot_table(index="category", columns="channel_name",
                           values="compliance_score", aggfunc="mean")
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[
            [0.0, "#8B1A1A"], [0.5, "#F4A300"], [1.0, "#2E6DA4"]
        ],
        zmin=60, zmax=100,
        text=pivot.values.round(1),
        texttemplate="%{text}",
        hoverongaps=False,
        colorbar=dict(
            title=dict(text="Score", font=dict(color="#E8EDF2")),
            ticksuffix="%",
            tickfont=dict(color="#E8EDF2")),
    ))
    fig.update_layout(
        **_base_layout(title="Compliance Score — Category × Channel"),
        xaxis=dict(tickangle=-40, showgrid=False,
                   tickfont=dict(size=10, color="#9DBDD5")),
        yaxis=dict(showgrid=False, tickfont=dict(size=10, color="#9DBDD5")),
        height=400,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 2. Top Genres by Average Rating
# ─────────────────────────────────────────────────────────────────────────────

def top_genres_bar() -> go.Figure:
    df = query_df("""
        SELECT genre,
               ROUND(AVG(avg_rating),2) AS avg_r,
               COUNT(*) AS count
        FROM   shows
        GROUP BY genre
        HAVING count >= 1
        ORDER BY avg_r DESC
        LIMIT 15
    """)
    fig = go.Figure(go.Bar(
        x=df["avg_r"],
        y=df["genre"],
        orientation="h",
        marker=dict(
            color=df["avg_r"],
            colorscale=[[0, "#1A3C5E"], [0.5, "#2E6DA4"], [1, "#4FAAD7"]],
            showscale=False,
            line=dict(width=0),
        ),
        text=df["avg_r"].apply(lambda v: f"{v:.2f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Avg Rating: %{x:.2f}<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(title="Average Rating by Genre"),
        xaxis=dict(range=[0, 10.5], showgrid=True,
                   gridcolor="rgba(255,255,255,0.08)",
                   tickfont=dict(color="#9DBDD5")),
        yaxis=dict(autorange="reversed", showgrid=False,
                   tickfont=dict(color="#9DBDD5")),
        height=460,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 3. Shows by Platform (Pie / Donut)
# ─────────────────────────────────────────────────────────────────────────────

def platform_donut() -> go.Figure:
    df = query_df("""
        SELECT platform, COUNT(*) AS cnt
        FROM   shows
        GROUP BY platform
        ORDER BY cnt DESC
    """)
    fig = go.Figure(go.Pie(
        labels=df["platform"],
        values=df["cnt"],
        hole=0.52,
        marker=dict(colors=PALETTE,
                    line=dict(color="#0D1B2A", width=2)),
        textinfo="percent+label",
        textfont=dict(color="#E8EDF2", size=11),
        hovertemplate="<b>%{label}</b><br>Shows: %{value}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(title="Show Distribution by Platform"),
        showlegend=False,
        height=380,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 4. Ratings Distribution Histogram
# ─────────────────────────────────────────────────────────────────────────────

def ratings_histogram() -> go.Figure:
    df = query_df("SELECT avg_rating FROM shows WHERE avg_rating IS NOT NULL")
    fig = go.Figure(go.Histogram(
        x=df["avg_rating"],
        nbinsx=18,
        marker=dict(
            color="#2E6DA4",
            line=dict(color="#0D1B2A", width=1),
        ),
        hovertemplate="Rating: %{x:.1f}<br>Count: %{y}<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(title="Distribution of Show Ratings"),
        xaxis=dict(title="Avg Rating", range=[0, 10],
                   showgrid=True, gridcolor="rgba(255,255,255,0.08)",
                   tickfont=dict(color="#9DBDD5")),
        yaxis=dict(title="Count", showgrid=True,
                   gridcolor="rgba(255,255,255,0.08)",
                   tickfont=dict(color="#9DBDD5")),
        height=340,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 5. Channels by Region (Horizontal Bar)
# ─────────────────────────────────────────────────────────────────────────────

def channels_by_region() -> go.Figure:
    df = query_df("""
        SELECT region, COUNT(*) AS cnt
        FROM   channels
        GROUP BY region
        ORDER BY cnt DESC
    """)
    fig = go.Figure(go.Bar(
        y=df["region"],
        x=df["cnt"],
        orientation="h",
        marker=dict(color=PALETTE[:len(df)],
                    line=dict(width=0)),
        text=df["cnt"],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Channels: %{x}<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(title="Empaneled Channels by Region"),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)",
                   tickfont=dict(color="#9DBDD5")),
        yaxis=dict(autorange="reversed", showgrid=False,
                   tickfont=dict(color="#9DBDD5")),
        height=380,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 6. Runtime vs Rating Scatter
# ─────────────────────────────────────────────────────────────────────────────

def runtime_vs_rating_scatter() -> go.Figure:
    df = query_df("""
        SELECT s.title, s.runtime_mins, s.avg_rating,
               s.genre, c.channel_name, s.weekly_slots
        FROM   shows s
        JOIN   channels c ON s.channel_id = c.channel_id
        WHERE  s.avg_rating IS NOT NULL AND s.runtime_mins IS NOT NULL
    """)
    genres = df["genre"].unique().tolist()
    colour_map = {g: PALETTE[i % len(PALETTE)] for i, g in enumerate(genres)}
    traces = []
    for genre in genres:
        sub = df[df["genre"] == genre]
        traces.append(go.Scatter(
            x=sub["runtime_mins"], y=sub["avg_rating"],
            mode="markers", name=genre,
            marker=dict(
                size=sub["weekly_slots"].clip(3, 20),
                color=colour_map[genre],
                opacity=0.8,
                line=dict(width=0.5, color="#0D1B2A"),
            ),
            customdata=sub[["title", "channel_name", "weekly_slots"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Channel: %{customdata[1]}<br>"
                "Runtime: %{x} min<br>"
                "Rating: %{y:.1f}<br>"
                "Weekly Slots: %{customdata[2]}<extra></extra>"
            ),
        ))
    fig = go.Figure(traces)
    fig.update_layout(
        **_base_layout(title="Runtime vs Rating (bubble = weekly slots)"),
        xaxis=dict(title="Runtime (mins)",
                   showgrid=True, gridcolor="rgba(255,255,255,0.08)",
                   tickfont=dict(color="#9DBDD5")),
        yaxis=dict(title="Avg Rating", range=[0, 11],
                   showgrid=True, gridcolor="rgba(255,255,255,0.08)",
                   tickfont=dict(color="#9DBDD5")),
        legend=dict(font=dict(color="#9DBDD5", size=10),
                    bgcolor="rgba(0,0,0,0.3)"),
        height=440,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 7. Compliance trend bar (channels sorted by score)
# ─────────────────────────────────────────────────────────────────────────────

def compliance_bars() -> go.Figure:
    df = query_df("""
        SELECT channel_name, compliance_score, category
        FROM   channels
        ORDER BY compliance_score DESC
    """)
    colors = df["compliance_score"].apply(
        lambda v: "#2E6DA4" if v >= 90 else ("#F4A300" if v >= 80 else "#8B1A1A")
    )
    fig = go.Figure(go.Bar(
        x=df["channel_name"],
        y=df["compliance_score"],
        marker=dict(color=colors, line=dict(width=0)),
        text=df["compliance_score"].apply(lambda v: f"{v:.1f}"),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Score: %{y}%<extra></extra>",
    ))
    fig.add_hline(y=90, line_dash="dot", line_color="#4FAAD7",
                  annotation_text="Target 90%",
                  annotation_font_color="#4FAAD7")
    fig.update_layout(
        **_base_layout(title="Compliance Score per Channel"),
        xaxis=dict(tickangle=-40, showgrid=False,
                   tickfont=dict(color="#9DBDD5", size=9)),
        yaxis=dict(range=[60, 105], showgrid=True,
                   gridcolor="rgba(255,255,255,0.08)",
                   ticksuffix="%", tickfont=dict(color="#9DBDD5")),
        height=420,
    )
    return fig