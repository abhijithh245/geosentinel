import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# -------------------------------
# 📌 Page Config
# -------------------------------
st.set_page_config(layout="wide", page_title="Chennai Risk Dashboard", page_icon="🌡️")

# -------------------------------
# 🎨 Dark Mode CSS
# -------------------------------
st.markdown("""
<style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');

    /* ── Root dark palette ── */
    :root {
        --bg-primary:    #0a0e14;
        --bg-surface:    #111720;
        --bg-card:       #161d28;
        --border:        #1e2d40;
        --accent-red:    #ff4b4b;
        --accent-yellow: #f5a623;
        --accent-green:  #2ecc71;
        --accent-blue:   #3b9eff;
        --text-primary:  #e8edf5;
        --text-muted:    #6b7a91;
        --font-display:  'Rajdhani', sans-serif;
        --font-body:     'Inter', sans-serif;
    }

    /* ── App background ── */
    .stApp {
        background: var(--bg-primary);
        color: var(--text-primary);
        font-family: var(--font-body);
    }

    /* ── Hide default header decoration ── */
    header[data-testid="stHeader"] { background: transparent; }

    /* ── Main title ── */
    h1 {
        font-family: var(--font-display) !important;
        font-size: 2.4rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em !important;
        background: linear-gradient(135deg, #3b9eff 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem !important;
    }

    /* ── Section subheadings ── */
    h2, h3 {
        font-family: var(--font-display) !important;
        font-weight: 600 !important;
        letter-spacing: 0.04em !important;
        color: var(--text-primary) !important;
    }

    /* ── Stat/metric cards ── */
    .risk-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 0.6rem;
    }
    .risk-card-label {
        font-family: var(--font-display);
        font-size: 0.75rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.15rem;
    }
    .risk-card-value {
        font-family: var(--font-display);
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
    }
    .risk-high   { color: var(--accent-red); }
    .risk-medium { color: var(--accent-yellow); }
    .risk-low    { color: var(--accent-green); }

    /* ── Selectbox ── */
    .stSelectbox label { color: var(--text-muted) !important; font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; }
    div[data-baseweb="select"] > div {
        background: var(--bg-card) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
    }

    /* ── Alert / info boxes ── */
    .stAlert {
        border-radius: 10px !important;
        border-left-width: 4px !important;
        font-family: var(--font-body) !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--bg-surface) !important;
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] h2 {
        font-family: var(--font-display) !important;
        font-size: 1.1rem !important;
        letter-spacing: 0.1em !important;
        color: var(--accent-blue) !important;
    }
    .sidebar-zone {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.55rem 0.9rem;
        margin-bottom: 0.45rem;
        font-family: var(--font-body);
        font-size: 0.82rem;
    }
    .sidebar-zone-name { color: var(--text-primary); font-weight: 500; }
    .sidebar-zone-score { color: var(--accent-red); font-weight: 700; font-size: 1rem; float: right; }

    /* ── Divider ── */
    .section-divider {
        border: none;
        border-top: 1px solid var(--border);
        margin: 1.6rem 0;
    }

    /* ── Plot backgrounds match theme ── */
    .stPlotlyChart, .stPyplot { background: transparent !important; }

    /* ── Remove Streamlit branding from footer ── */
    footer { visibility: hidden; }

    /* ── Top title bar accent ── */
    .title-bar {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 1.4rem;
        border-bottom: 1px solid var(--border);
        padding-bottom: 1rem;
    }
    .title-dot {
        width: 10px; height: 10px;
        border-radius: 50%;
        background: var(--accent-blue);
        box-shadow: 0 0 10px var(--accent-blue);
    }
    .live-badge {
        background: rgba(59,158,255,0.12);
        border: 1px solid rgba(59,158,255,0.35);
        color: var(--accent-blue);
        font-size: 0.65rem;
        font-family: var(--font-display);
        letter-spacing: 0.14em;
        text-transform: uppercase;
        padding: 0.18rem 0.6rem;
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Dark matplotlib style ───────────────────────────────────────────────────
DARK_BG     = "#0a0e14"
CARD_BG     = "#111720"
BORDER_CLR  = "#1e2d40"
TEXT_CLR    = "#e8edf5"
MUTED_CLR   = "#6b7a91"
ACCENT_BLUE = "#3b9eff"
ACCENT_RED  = "#ff4b4b"
ACCENT_YEL  = "#f5a623"
ACCENT_GRN  = "#2ecc71"

plt.rcParams.update({
    "figure.facecolor":  DARK_BG,
    "axes.facecolor":    CARD_BG,
    "axes.edgecolor":    BORDER_CLR,
    "axes.labelcolor":   MUTED_CLR,
    "axes.titlecolor":   TEXT_CLR,
    "xtick.color":       MUTED_CLR,
    "ytick.color":       MUTED_CLR,
    "text.color":        TEXT_CLR,
    "grid.color":        BORDER_CLR,
    "grid.linewidth":    0.6,
    "font.family":       "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

# -------------------------------
# 📂 Load Data
# -------------------------------
gdf = gpd.read_file("final_risk.geojson")
gdf = gdf.to_crs(epsg=4326)

# -------------------------------
# 🎨 Color helpers
# -------------------------------
def get_color(score):
    if score > 70:   return "red"
    elif score >= 40: return "yellow"
    else:             return "green"

def score_class(score):
    if score > 70:   return "risk-high"
    elif score >= 40: return "risk-medium"
    else:             return "risk-low"

# ─── Title bar ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="title-bar">
    <div class="title-dot"></div>
    <h1 style="margin:0">Chennai Compound Risk Early Warning</h1>
    <span class="live-badge">Live</span>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🏆 Top 5 High-Risk Zones")
top5 = gdf.sort_values(by="compound_score", ascending=False).head(5)
for rank, (_, row) in enumerate(top5.iterrows(), 1):
    st.sidebar.markdown(f"""
    <div class="sidebar-zone">
        <span class="sidebar-zone-name">#{rank} &nbsp; {row['name']}</span>
        <span class="sidebar-zone-score">{row['compound_score']:.1f}</span>
    </div>""", unsafe_allow_html=True)

st.sidebar.markdown("<hr style='border-color:#1e2d40; margin:1.2rem 0'>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='font-size:0.7rem;color:#6b7a91;letter-spacing:0.08em;text-transform:uppercase;'>Score thresholds</div>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='margin-top:0.5rem;font-size:0.8rem;line-height:2'>
    <span style='color:#ff4b4b'>●</span>&nbsp;High &nbsp;&gt; 70<br>
    <span style='color:#f5a623'>●</span>&nbsp;Medium &nbsp;40–70<br>
    <span style='color:#2ecc71'>●</span>&nbsp;Low &nbsp;&lt; 40
</div>""", unsafe_allow_html=True)

# ─── Map ─────────────────────────────────────────────────────────────────────
st.subheader("🗺️ Risk Map")

m = folium.Map(
    location=[13.08, 80.27],
    zoom_start=10,
    tiles="CartoDB dark_matter"
)

for _, row in gdf.iterrows():
    folium.GeoJson(
        row["geometry"],
        style_function=lambda x, score=row["compound_score"]: {
            "fillColor": get_color(score),
            "color": "#1e2d40",
            "weight": 1,
            "fillOpacity": 0.65,
        },
        tooltip=folium.Tooltip(
            f"<b style='font-family:sans-serif'>{row['name']}</b><br>"
            f"<span style='color:#aaa'>Score:</span> <b>{row['compound_score']:.2f}</b>",
            sticky=True
        )
    ).add_to(m)

st_folium(m, width="100%", height=480)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ─── Zone selector ───────────────────────────────────────────────────────────
col_sel, col_stats = st.columns([2, 3])
with col_sel:
    zone = st.selectbox("Select Zone", gdf["name"])

selected = gdf[gdf["name"] == zone].iloc[0]
score    = selected["compound_score"]
sc       = score_class(score)

with col_stats:
    c1, c2, c3, c4 = st.columns(4)
    def metric_card(col, label, value, cls):
        col.markdown(f"""
        <div class="risk-card">
            <div class="risk-card-label">{label}</div>
            <div class="risk-card-value {cls}">{value:.1f}</div>
        </div>""", unsafe_allow_html=True)

    metric_card(c1, "Compound",  score,                    sc)
    metric_card(c2, "Heat",      selected["heat_score"],   score_class(selected["heat_score"]))
    metric_card(c3, "Flood",     selected["flood_score"],  score_class(selected["flood_score"]))
    metric_card(c4, "AQI",       selected["aqi_score"],    score_class(selected["aqi_score"]))

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ─── Charts side by side ─────────────────────────────────────────────────────
chart_col1, chart_col2 = st.columns(2)

# Bar chart
with chart_col1:
    st.subheader("📊 Component Risk Scores")

    categories = ["Heat", "Flood", "AQI"]
    values     = [selected["heat_score"], selected["flood_score"], selected["aqi_score"]]
    bar_colors = [
        ACCENT_RED if v > 70 else (ACCENT_YEL if v >= 40 else ACCENT_GRN)
        for v in values
    ]

    fig1, ax1 = plt.subplots(figsize=(5, 3.4))
    bars = ax1.bar(categories, values, color=bar_colors, width=0.45,
                   zorder=3, linewidth=0)

    # value labels on bars
    for bar, val in zip(bars, values):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.2,
            f"{val:.1f}",
            ha="center", va="bottom",
            fontsize=9, fontweight="bold", color=TEXT_CLR
        )

    ax1.set_ylim(0, 110)
    ax1.set_ylabel("Score", fontsize=8)
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(20))
    ax1.grid(axis="y", zorder=0)
    ax1.set_title(f"{zone} — Risk Components", fontsize=10, pad=10)
    fig1.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

# Line chart
with chart_col2:
    st.subheader("📈 30-Day Risk Prediction")

    prediction_cols  = [f"day{i}_predicted" for i in range(1, 31)]
    available_cols   = [c for c in prediction_cols if c in gdf.columns]

    if not available_cols:
        st.error("❌ No prediction data found. Run ML script first.")
    else:
        predictions = [selected[c] for c in available_cols]
        days        = list(range(1, len(predictions) + 1))
        pred_arr    = np.array(predictions, dtype=float)

        fig2, ax2 = plt.subplots(figsize=(5, 3.4))

        # Gradient-like fill under the line
        ax2.fill_between(days, pred_arr, alpha=0.15, color=ACCENT_BLUE, zorder=2)

        # Colour the line segments by severity
        for i in range(len(days) - 1):
            seg_color = (
                ACCENT_RED if pred_arr[i] > 70
                else ACCENT_YEL if pred_arr[i] >= 40
                else ACCENT_GRN
            )
            ax2.plot(days[i:i+2], pred_arr[i:i+2],
                     color=seg_color, linewidth=2, zorder=3)

        # Dots
        ax2.scatter(days, pred_arr,
                    color=[
                        ACCENT_RED if v > 70 else (ACCENT_YEL if v >= 40 else ACCENT_GRN)
                        for v in pred_arr
                    ],
                    s=34, zorder=4, linewidths=0)

        # Danger threshold line
        ax2.axhline(70, color=ACCENT_RED,  linewidth=0.8,
                    linestyle="--", alpha=0.5, label="High threshold")
        ax2.axhline(40, color=ACCENT_YEL, linewidth=0.8,
                    linestyle="--", alpha=0.5, label="Med threshold")

        ax2.set_xlabel("Day", fontsize=8)
        ax2.set_ylabel("Risk Score", fontsize=8)
        ax2.set_title(f"{zone} — 30-Day Forecast", fontsize=10, pad=10)
        ax2.legend(fontsize=7, framealpha=0.15, edgecolor=BORDER_CLR)
        ax2.grid(True, zorder=0)
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ─── AI Risk Briefing ─────────────────────────────────────────────────────────
st.subheader("🧠 AI Risk Briefing")

briefing = selected.get("ai_briefing", "")

if isinstance(briefing, str) and briefing.strip():
    if score > 70:
        st.error(briefing)
    elif score >= 40:
        st.warning(briefing)
    else:
        st.success(briefing)
else:
    st.info("⚠️ AI briefing not available for this zone.")
