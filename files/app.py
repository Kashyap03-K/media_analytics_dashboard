"""
app.py — TAM EIKONA Dashboard
Light gradient theme | Fixed sidebar | Multi-medium Analytics
"""
import os, io
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import base64

from config import (APP_TITLE, APP_ICON, COOKIE_NAME, COOKIE_KEY, COOKIE_EXPIRY,
                    FALLBACK_CREDENTIALS, ROLE_ACCESS, ROLE_ADMIN, ROLE_CLIENT, ROLE_PARTNER)
import data_loader as dl
from platform_dashboard import render_platform_dashboard, init_platform_db, PLATFORMS, table_has_data, get_platform_df, build_chart_data

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root {
    --bg:         #F0F4FF;
    --bg-card:    #FFFFFF;
    --bg-card2:   #F8FAFF;
    --accent:     #4F46E5;
    --accent2:    #6366F1;
    --teal:       #0891B2;
    --green:      #059669;
    --gold:       #D97706;
    --danger:     #DC2626;
    --text:       #1E293B;
    --muted:      #64748B;
    --dim:        #94A3B8;
    --border:     #E2E8F0;
    --radius:     10px;
    --sidebar-w:  240px;
}

html, body, [class*="css"] { font-family:'Plus Jakarta Sans',sans-serif!important; }

/* ══ LIGHT GRADIENT BACKGROUND ══ */
.stApp {
    background: linear-gradient(135deg, #EEF2FF 0%, #F0F9FF 40%, #F0FDF4 100%) !important;
    min-height: 100vh;
    color: var(--text);
}

#MainMenu, footer, header { display:none!important; }
.block-container { padding-top:.6rem!important; padding-bottom:2rem!important; }

/* ══ WHITE SIDEBAR — always visible ══ */
section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid var(--border) !important;
    min-width: var(--sidebar-w) !important;
    max-width: var(--sidebar-w) !important;
    width: var(--sidebar-w) !important;
    box-shadow: 2px 0 8px rgba(0,0,0,0.06) !important;
    transform: none !important;
    visibility: visible !important;
    display: block !important;
}
/* Keep sidebar visible even when Streamlit marks it collapsed */
section[data-testid="stSidebar"][aria-expanded="false"] {
    transform: none !important;
    margin-left: 0 !important;
    display: block !important;
    width: var(--sidebar-w) !important;
    min-width: var(--sidebar-w) !important;
}
/* Hide the collapse/expand toggle button AND keyboard_double text — sidebar stays locked open */
button[data-testid="collapsedControl"],
button[title="Close sidebar"],
button[title="Open sidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
div[class*="stSidebarCollapse"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}
/* Hide the keyboard_double_arrow icon that leaks through at the top */
section[data-testid="stSidebar"] > div:first-child > div:first-child > div[style*="position: absolute"],
button[aria-label*="sidebar"], button[aria-label*="Sidebar"] {
    display: none !important;
}

/* Hide radio widget's own label ("nav" text) */
section[data-testid="stSidebar"] [data-testid="stRadio"] > label,
section[data-testid="stSidebar"] [data-testid="stRadio"] > div[class*="label"],
section[data-testid="stSidebar"] .stRadio > label {
    display: none !important;
    height: 0 !important;
    overflow: hidden !important;
}

/* ══ SIDEBAR NAV — no bullets ══ */
section[data-testid="stSidebar"] * {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    display:flex!important; flex-direction:column!important; gap:2px!important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    display:flex!important; align-items:center!important; gap:9px!important;
    padding:9px 14px!important; border-radius:8px!important; cursor:pointer!important;
    transition:background .12s!important; font-size:0.875rem!important;
    font-weight:500!important; color:#111827!important; margin:0!important;
    border:none!important; background:transparent!important; width:100%!important;
    list-style:none!important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background:#F5F3FF!important; color:#4F46E5!important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background:#EEF2FF!important; color:#4338CA!important; font-weight:600!important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"] {
    display:none!important;
    width:0!important; height:0!important; opacity:0!important;
    position:absolute!important; pointer-events:none!important;
}
/* Kill ONLY the circular radio dot — not the text */
/* Target the SVG/circle element that Streamlit renders as the radio indicator */
section[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child:has(> div > div) {
    display:none!important;
}
/* Fallback: hide the first child div only if it contains an SVG (the radio circle) */
section[data-testid="stSidebar"] [data-testid="stRadio"] label svg {
    display:none!important;
}
/* Hide the outer wrapper div that holds the radio circle (width ~20px) */
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label > div:first-child {
    width:0!important; overflow:hidden!important; flex-shrink:0!important;
    margin:0!important; padding:0!important;
}
/* Nuke any ::before circle pseudo-elements */
section[data-testid="stSidebar"] [data-testid="stRadio"] label::before,
section[data-testid="stSidebar"] [data-testid="stRadio"] label > div::before {
    display:none!important; content:none!important;
}
/* Make sure text (stMarkdownContainer) is always visible */
section[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stMarkdownContainer"] {
    display:block!important; visibility:visible!important; opacity:1!important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
    display:block!important; visibility:visible!important; opacity:1!important;
    color:#111827!important; font-size:.875rem!important; font-weight:500!important;
}
/* Make the label itself flex so icon+text align */
section[data-testid="stSidebar"] [data-testid="stRadio"] label > div:last-child {
    display:flex!important; align-items:center!important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] div { color:#111827!important; }

section[data-testid="stSidebar"] hr {
    border-color:#F3F4F6!important; margin:8px 0!important;
}
section[data-testid="stSidebar"] .stButton>button {
    background:#F9FAFB!important; color:#374151!important;
    border:1px solid #E5E7EB!important; border-radius:8px!important;
    font-size:0.84rem!important; width:100%!important;
    padding:8px 14px!important; transition:background .15s!important;
}
section[data-testid="stSidebar"] .stButton>button:hover {
    background:#FEF2F2!important; color:#DC2626!important; border-color:#FECACA!important;
}
section[data-testid="stSidebar"] .stSelectbox>div>div,
section[data-testid="stSidebar"] .stTextInput>div>input {
    background:#F9FAFB!important; color:#111827!important;
    border:1px solid #E5E7EB!important; border-radius:6px!important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextInput label {
    color:#6B7280!important; font-size:0.74rem!important; font-weight:600!important;
}

/* ══ MAIN AREA ══ */
h1 { color:var(--accent)!important; font-size:1.4rem!important; font-weight:700!important; letter-spacing:-.02em; }
h2 { color:var(--text)!important; font-size:1.15rem!important; font-weight:600!important; }
h3 { color:var(--gold)!important; font-size:.9rem!important; font-weight:600!important; }

div[data-testid="metric-container"] {
    background: #FFFFFF!important;
    border: 1px solid var(--border)!important;
    border-radius: var(--radius)!important;
    padding: 14px 18px!important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05)!important;
}
div[data-testid="metric-container"] label { color:var(--muted)!important; font-size:.76rem!important; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color:var(--accent)!important; font-size:1.65rem!important; font-weight:700!important;
}

.stDataFrame { border:1px solid var(--border)!important; border-radius:var(--radius)!important; }

.stButton>button {
    background:var(--accent)!important; color:#fff!important;
    border:none!important; border-radius:7px!important;
    padding:7px 18px!important; font-size:.85rem!important; font-weight:500!important;
    transition:background .2s!important;
}
.stButton>button:hover { background:var(--accent2)!important; }

.stDownloadButton>button {
    background:#EFF6FF!important; color:var(--accent)!important;
    border:1px solid #BFDBFE!important; border-radius:7px!important;
    padding:7px 18px!important; font-weight:500!important;
}
.stDownloadButton>button:hover { background:var(--accent)!important; color:#fff!important; }

.stTabs [data-baseweb="tab-list"] {
    background:#FFFFFF!important; border-radius:var(--radius)!important;
    border:1px solid var(--border)!important; padding:4px!important;
}
.stTabs [data-baseweb="tab"] { color:var(--muted)!important; border-radius:7px!important; }
.stTabs [aria-selected="true"] {
    color:var(--accent)!important; background:#EEF2FF!important;
    border-bottom:none!important; font-weight:600!important;
}
.streamlit-expanderHeader { background:#FFFFFF!important; color:var(--text)!important; border-radius:var(--radius)!important; }
.stSelectbox>div, .stTextInput>div>input {
    background:#FFFFFF!important; color:var(--text)!important; border:1px solid var(--border)!important;
}
.stAlert { border-radius:var(--radius)!important; }
.stCheckbox label { color:var(--text)!important; font-size:.9rem!important; }

/* Banner */
.banner {
    background: linear-gradient(90deg, #FBCFE8 0%, #A21CAF 50%, #3B0764 100%);
    border-radius:12px; padding:16px 24px 12px;
    margin-bottom:18px; display:flex; align-items:center; gap:14px;
    box-shadow:0 4px 14px rgba(79,70,229,0.25);
}
.banner-title { font-size:1.2rem; font-weight:700; color:#fff; letter-spacing:-.01em; }
.banner-sub   { font-size:.78rem; color:rgba(255,255,255,0.75); margin-top:3px; }

/* Badges */
.badge { display:inline-block; padding:2px 9px; border-radius:20px; font-size:.72rem; font-weight:600; }
.badge-admin   { background:#EDE9FE; color:#5B21B6; }
.badge-client  { background:#DBEAFE; color:#1D4ED8; }
.badge-partner { background:#D1FAE5; color:#065F46; }
.badge-clear   { background:#D1FAE5; color:#065F46; }
.badge-review  { background:#FEF3C7; color:#92400E; }

.sidebar-section-label {
    font-size:0.68rem; font-weight:700; letter-spacing:.08em;
    text-transform:uppercase; color:#9CA3AF;
    padding:10px 14px 3px; display:block;
}
</style>
<script>
// Force sidebar open on every Streamlit rerun
// Also nuke the keyboard_double_arrow button that leaks through
(function keepSidebarOpen() {
    function expand() {
        // Hide keyboard_double arrow button and any stale collapse controls
        var killSelectors = [
            'button[data-testid="collapsedControl"]',
            '[data-testid="stSidebarCollapseButton"]',
            '[data-testid="stSidebarCollapsedControl"]',
            'button[title="Open sidebar"]',
            'button[title="Close sidebar"]',
            'button[aria-label*="sidebar"]'
        ];
        killSelectors.forEach(function(sel) {
            var els = window.parent.document.querySelectorAll(sel);
            els.forEach(function(el) {
                el.style.setProperty('display', 'none', 'important');
                el.style.setProperty('visibility', 'hidden', 'important');
            });
        });

        // Also force the sidebar element to be visible via style
        var sb = window.parent.document.querySelector('section[data-testid="stSidebar"]');
        if (sb) {
            sb.style.setProperty('display',    'block',   'important');
            sb.style.setProperty('visibility', 'visible', 'important');
            sb.style.setProperty('width',      '240px',   'important');
            sb.style.setProperty('min-width',  '240px',   'important');
            sb.style.setProperty('transform',  'none',    'important');
        }
    }
    // Run immediately and after short delays for Streamlit's rerun cycle
    expand();
    setTimeout(expand, 100);
    setTimeout(expand, 400);
    setTimeout(expand, 1000);

    // Re-run on any DOM mutations (Streamlit reruns change the DOM)
    var observer = new MutationObserver(function() { expand(); });
    observer.observe(window.parent.document.body, {
        childList: true, subtree: true, attributes: true,
        attributeFilter: ['aria-expanded', 'class', 'style']
    });
})();
</script>
""", unsafe_allow_html=True)

@st.cache_resource
def _init_db():
    dl.bootstrap()
    init_platform_db()
    return True
_init_db()

def _load_credentials():
    import yaml
    yaml_path = os.path.join(os.path.dirname(__file__), "users.yaml")
    if os.path.exists(yaml_path):
        with open(yaml_path, "r") as f:
            raw = yaml.safe_load(f)
        return raw.get("credentials", FALLBACK_CREDENTIALS)
    return FALLBACK_CREDENTIALS


creds = _load_credentials()

import inspect as _inspect
_auth_params = set(_inspect.signature(stauth.Authenticate.__init__).parameters.keys())
_cookie_kwarg = "key" if "key" in _auth_params else "cookie_key"

authenticator = stauth.Authenticate(
    credentials=creds, cookie_name=COOKIE_NAME, cookie_expiry_days=COOKIE_EXPIRY,
    **{_cookie_kwarg: COOKIE_KEY},
)
# 1. Function to encode the image
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 2. Convert your specific logo
# Resolve logo relative to this file's directory so it works on any machine
_IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
_LOGO_BIG  = os.path.join(_IMG_DIR, "NewBig.png")
_LOGO_SMALL = os.path.join(_IMG_DIR, "TAM_logo.png")
logo_base64 = get_base64_of_bin_file(_LOGO_BIG) if os.path.exists(_LOGO_BIG) else ""
logo_small_base64 = get_base64_of_bin_file(_LOGO_SMALL) if os.path.exists(_LOGO_SMALL) else ""
def show_login():
    # Logo card rendered first so it appears ABOVE the login form
    _, mid, _ = st.columns([1, 1.6, 1])
    with mid:
        st.markdown(f"""
        <div style="text-align:center;padding:36px 32px 24px;
                    border-radius:16px;margin-bottom:18px">
            <div style="margin-bottom:14px">
                <img src="data:image/png;base64,{logo_base64}" width="220">
            </div>
            <div style="font-size:1.7rem;font-weight:800;color:#4F46E5;margin-bottom:4px;
                        letter-spacing:-.02em">
                TAM — EIKONA Dashboard
            </div>
            <div style="font-size:.78rem;color:#64748B;line-height:1.6">
                Internal Media Intelligence Portal<br>
                <span style="color:#DC2626;font-weight:600">
                    🔒 Restricted — Authorised Personnel Only
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    # Login form renders below this card automatically

def _get_role(username):
    return creds.get("usernames", {}).get(username, {}).get("role", ROLE_CLIENT)

def _can(username, panel):
    return panel in ROLE_ACCESS.get(_get_role(username), [])

def _badge(role):
    return f'<span class="badge badge-{role}">{role.upper()}</span>'

def _df_to_csv(df):
    buf = io.StringIO(); df.to_csv(buf, index=False); return buf.getvalue().encode()

def _sidebar_filters_channels():
    st.sidebar.markdown('<span class="sidebar-section-label">Filters</span>', unsafe_allow_html=True)
    regions   = [""] + sorted(dl.query_df("SELECT DISTINCT region FROM channels ORDER BY region")["region"].tolist())
    languages = [""] + sorted(dl.query_df("SELECT DISTINCT language FROM channels ORDER BY language")["language"].tolist())
    cats      = [""] + sorted(dl.query_df("SELECT DISTINCT category FROM channels ORDER BY category")["category"].tolist())
    return {"region": st.sidebar.selectbox("Region", regions),
            "language": st.sidebar.selectbox("Language", languages),
            "category": st.sidebar.selectbox("Category", cats),
            "search": st.sidebar.text_input("Search name")}

def _sidebar_filters_shows():
    st.sidebar.markdown('<span class="sidebar-section-label">Filters</span>', unsafe_allow_html=True)
    genres    = [""] + sorted(dl.query_df("SELECT DISTINCT genre FROM shows ORDER BY genre")["genre"].tolist())
    languages = [""] + sorted(dl.query_df("SELECT DISTINCT language FROM shows ORDER BY language")["language"].tolist())
    return {"genre": st.sidebar.selectbox("Genre", genres),
            "platform": st.sidebar.selectbox("Platform", ["","DTH","Cable","DTH+Cable"]),
            "language": st.sidebar.selectbox("Language", languages),
            "status": st.sidebar.selectbox("Status", ["","Active","Archived"]),
            "search": st.sidebar.text_input("Search title")}


# ── Panel renderers ──────────────────────────────────────────────────────────
def render_overview(username):
    m = dl.get_metrics()
    st.markdown("## 📊 Overview — Key Metrics")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Channels",m["total_channels"]); c2.metric("Empaneled",m["empaneled"])
    c3.metric("Total Shows",m["total_shows"]);       c4.metric("Active Shows",m["active_shows"])
    c5,c6,c7,c8 = st.columns(4)
    c5.metric("Avg Runtime",m["avg_runtime"]); c6.metric("Avg Rating",m["avg_rating"])
    c7.metric("Avg Compliance %",m["avg_compliance"])
    c8.metric("Flagged",m["compliance_flags"], delta=f"-{m['compliance_flags']} need review" if m["compliance_flags"] else None, delta_color="inverse")

def render_channels(username):
    st.markdown("## 📡 Empaneled Channel List")
    f  = _sidebar_filters_channels()
    df = dl.get_channels(**{k:v or None for k,v in f.items()})
    st.caption(f"**{len(df)}** channels")
    def cs(v):
        if pd.isna(v): return ""
        return "color:#4F46E5" if v>=90 else "color:#D97706" if v>=80 else "color:#DC2626"
    st.dataframe(df.style.applymap(cs,subset=["compliance_score"])
                 .format({"compliance_score":"{:.1f}%"},na_rep="—")
                 .set_properties(**{"background-color":"#fff","color":"#1E293B"}),
                 use_container_width=True, height=440)
    if _can(username,"downloads"):
        st.download_button("⬇ Export CSV",_df_to_csv(df),"channels.csv","text/csv",key="dl_ch")

def render_shows(username):
    st.markdown("## 🎬 Programme Register")
    f  = _sidebar_filters_shows()
    df = dl.get_shows(**{k:v or None for k,v in f.items()})
    st.caption(f"**{len(df)}** shows")
    st.dataframe(df.style
                 .applymap(lambda v:"color:#4F46E5" if v=="Clear" else "color:#D97706",subset=["compliance_flag"])
                 .applymap(lambda v:"color:#D97706" if v=="Yes" else "",subset=["prime_time"])
                 .format({"avg_rating":"{:.2f}","runtime_mins":"{} min"},na_rep="—")
                 .set_properties(**{"background-color":"#fff","color":"#1E293B"}),
                 use_container_width=True, height=480)
    if _can(username,"downloads"):
        st.download_button("⬇ Export CSV",_df_to_csv(df),"shows.csv","text/csv",key="dl_sh")


# ── Analytics — multi-medium comparison ─────────────────────────────────────
def render_analytics(username):
    import plotly.graph_objects as go

    st.markdown("## ◈ Analytics — Cross-Platform Intelligence")

    # Medium selector checkboxes
    st.markdown("#### Select Mediums to Compare")
    available = {"Print":"print","Online":"online","TV":"tv","Social Media":"social"}
    cols = st.columns(len(available))
    selected = []
    for i,(label,key) in enumerate(available.items()):
        has = table_has_data(key)
        with cols[i]:
            checked = st.checkbox(label, value=has, disabled=not has,
                                  help="No data loaded" if not has else f"{label} data available")
            if checked and has:
                selected.append((label, key))

    if not selected:
        st.info("No medium data loaded. Upload data from the Print / Online / TV / Social panels first.")
        return

    if len(selected) == 1:
        st.caption(f"Showing single medium: **{selected[0][0]}**")
    else:
        st.caption(f"Comparing: **{' vs '.join(l for l,_ in selected)}**")

    st.markdown("---")

    # Load dataframes for selected mediums
    PCOLORS = {"Print":"#2563EB","Online":"#059669","TV":"#7C3AED","Social Media":"#DB2777"}
    BG = "rgba(0,0,0,0)"
    FONT = "Plus Jakarta Sans, sans-serif"
    GC = "rgba(203,213,225,0.4)"; TC = "#64748B"

    def base(title="", h=340):
        return dict(paper_bgcolor=BG, plot_bgcolor=BG,
                    font=dict(family=FONT, color=TC, size=11),
                    margin=dict(l=40,r=20,t=44,b=40),
                    title=dict(text=title, font=dict(color="#1E293B",size=13,family=FONT)),
                    height=h)

    dfs = {}
    for label, key in selected:
        df = get_platform_df(key)
        dfs[label] = df

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Platform Comparison","🧭 Sentiment Overview","📅 Trend Analysis","🏆 SOV Breakdown"
    ])

    # ── TAB 1: Articles & Volume comparison ──────────────────────────────
    with tab1:
        st.markdown("##### Volume Comparison across Selected Mediums")
        rows = []
        for label, key in selected:
            df_ = dfs[label]
            rows.append({
                "Medium":     label,
                "Articles":   int(pd.to_numeric(df_.get("total_articles", pd.Series([0])), errors="coerce").fillna(0).sum()) if not df_.empty else 0,
                "Volume":     int(pd.to_numeric(df_.get("total_vol",      pd.Series([0])), errors="coerce").fillna(0).sum()) if not df_.empty else 0,
                "Beneficial": int(pd.to_numeric(df_.get("beneficial_art", pd.Series([0])), errors="coerce").fillna(0).sum()) if not df_.empty else 0,
                "Neutral":    int(pd.to_numeric(df_.get("neutral_art",    pd.Series([0])), errors="coerce").fillna(0).sum()) if not df_.empty else 0,
                "Adverse":    int(pd.to_numeric(df_.get("adverse_art",    pd.Series([0])), errors="coerce").fillna(0).sum()) if not df_.empty else 0,
            })
        cdf = pd.DataFrame(rows)

        c1, c2 = st.columns(2)
        for col, metric, key_suffix in [(c1,"Articles","art"),(c2,"Volume","vol")]:
            with col:
                fig = go.Figure()
                for _, r in cdf.iterrows():
                    fig.add_bar(name=r["Medium"], x=[r["Medium"]], y=[r[metric]],
                                marker_color=PCOLORS.get(r["Medium"],"#888"),
                                marker_line_width=0, width=0.5)
                fig.update_layout(**base(f"Total {metric}"),
                    xaxis=dict(showgrid=False, tickfont=dict(color=TC)),
                    yaxis=dict(showgrid=True, gridcolor=GC, tickfont=dict(color=TC)),
                    showlegend=False, bargap=0.3)
                st.plotly_chart(fig, use_container_width=True, key=f"an_cmp_{key_suffix}")

        if not cdf.empty:
            st.dataframe(cdf.set_index("Medium").style
                .set_properties(**{"background-color":"#fff","color":"#1E293B"})
                .format("{:,}"), use_container_width=True)

    # ── TAB 2: Sentiment comparison ──────────────────────────────────────
    with tab2:
        st.markdown("##### Sentiment Split per Medium")
        sent_rows = []
        for label, key in selected:
            df_ = dfs[label]
            if df_.empty: continue
            def safesum(col):
                return float(pd.to_numeric(df_.get(col, pd.Series([0])), errors="coerce").fillna(0).sum())
            tb = safesum("beneficial_art"); tn = safesum("neutral_art"); ta = safesum("adverse_art")
            tot = tb+tn+ta or 1
            sent_rows.append({"Medium":label,
                               "Beneficial %":round(tb/tot*100,1),
                               "Neutral %":round(tn/tot*100,1),
                               "Adverse %":round(ta/tot*100,1)})
        if sent_rows:
            sdf = pd.DataFrame(sent_rows)
            fig = go.Figure()
            fig.add_bar(name="Beneficial", x=sdf["Medium"], y=sdf["Beneficial %"],
                        marker_color="#16A34A", marker_line_width=0)
            fig.add_bar(name="Neutral",    x=sdf["Medium"], y=sdf["Neutral %"],
                        marker_color="#6B7280", marker_line_width=0)
            fig.add_bar(name="Adverse",    x=sdf["Medium"], y=sdf["Adverse %"],
                        marker_color="#DC2626", marker_line_width=0)
            fig.update_layout(**base("Sentiment Distribution — 100% stacked", h=380),
                barmode="stack",
                xaxis=dict(showgrid=False, tickfont=dict(color=TC)),
                yaxis=dict(showgrid=True, gridcolor=GC, ticksuffix="%",
                           tickfont=dict(color=TC), range=[0,100]),
                legend=dict(font=dict(color=TC,size=11), bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig, use_container_width=True, key="an_sent")
        else:
            st.info("No sentiment data available for the selected mediums.")

    # ── TAB 3: Trend comparison ───────────────────────────────────────────
    with tab3:
        st.markdown("##### Article/Clip Count Over Time per Medium")
        fig = go.Figure()
        for label, key in selected:
            df_ = dfs[label]
            if df_.empty or "publication_date" not in df_.columns: continue
            df_["publication_date"] = df_["publication_date"].astype(str)
            trend = df_.groupby("publication_date")["total_articles"].sum().reset_index()
            trend = trend.sort_values("publication_date")
            fig.add_scatter(name=label, x=trend["publication_date"], y=trend["total_articles"],
                            mode="lines+markers", line=dict(color=PCOLORS.get(label,"#888"),width=2),
                            marker=dict(size=4))
        fig.update_layout(**base("Daily Volume Trend", h=380),
            xaxis=dict(showgrid=False, tickfont=dict(color=TC)),
            yaxis=dict(showgrid=True, gridcolor=GC, tickfont=dict(color=TC)),
            legend=dict(font=dict(color=TC,size=11), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True, key="an_trend")

    # ── TAB 4: SOV per medium ─────────────────────────────────────────────
    with tab4:
        st.markdown("##### Share of Voice — Articles per Medium")
        sov_rows = []
        for label, key in selected:
            df_ = dfs[label]
            if df_.empty or "company" not in df_.columns: continue
            for co, sub in df_.groupby("company"):
                arts = int(pd.to_numeric(sub.get("total_articles",pd.Series([1])),errors="coerce").fillna(1).sum())
                sov_rows.append({"Medium":label,"Company":co,"Articles":arts})
        if sov_rows:
            sovdf = pd.DataFrame(sov_rows)
            fig = go.Figure()
            companies = sorted(sovdf["Company"].unique())
            for co in companies:
                sub = sovdf[sovdf["Company"]==co]
                fig.add_bar(name=co, x=sub["Medium"], y=sub["Articles"],
                            marker_line_width=0)
            fig.update_layout(**base("SOV by Company across Mediums", h=400),
                barmode="group",
                xaxis=dict(showgrid=False, tickfont=dict(color=TC)),
                yaxis=dict(showgrid=True, gridcolor=GC, tickfont=dict(color=TC)),
                legend=dict(font=dict(color=TC,size=11), bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig, use_container_width=True, key="an_sov")
            st.dataframe(sovdf.pivot_table(index="Company",columns="Medium",values="Articles",aggfunc="sum",fill_value=0)
                         .style.set_properties(**{"background-color":"#fff","color":"#1E293B"}),
                         use_container_width=True)
        else:
            st.info("No company data available for the selected mediums.")


def render_downloads(username):
    st.markdown("## ⬇ Secure Data Downloads")
    st.info("All exports are session-scoped. No permanent logs.")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("### Channels"); df=dl.get_channels()
        st.download_button("Download Channels",_df_to_csv(df),"channels.csv","text/csv",key="dl_ch_m")
    with c2:
        st.markdown("### Shows"); df=dl.get_shows()
        st.download_button("Download Shows",_df_to_csv(df),"shows.csv","text/csv",key="dl_sh_m")
    st.markdown("---")
    st.markdown("### Compliance Summary")
    df_comp=dl.query_df("""
        SELECT c.channel_name, c.region, c.category, c.compliance_score,
               COUNT(s.show_id) AS total_shows,
               SUM(CASE WHEN s.compliance_flag!='Clear' THEN 1 ELSE 0 END) AS flagged_shows
        FROM channels c LEFT JOIN shows s ON c.channel_id=s.channel_id
        GROUP BY c.channel_id ORDER BY c.compliance_score DESC
    """)
    st.dataframe(df_comp, use_container_width=True)
    st.download_button("Download Compliance Report",_df_to_csv(df_comp),"compliance.csv","text/csv",key="dl_comp")
    dl.write_audit(username,"bulk_download")

def render_admin(username):
    st.markdown("## ⚙️ Admin Panel")
    t1,t2,t3=st.tabs(["DB Stats","Audit Log","Reload Data"])
    with t1:
        st.markdown("### Database Statistics")
        stats=dl.query_df("""
            SELECT 'channels' AS tbl, COUNT(*) AS rows FROM channels
            UNION ALL SELECT 'shows', COUNT(*) FROM shows
            UNION ALL SELECT 'audit_log', COUNT(*) FROM audit_log
        """)
        st.dataframe(stats, use_container_width=True)
        st.metric("DB size", f"{os.path.getsize(dl.DB_PATH)/1024:.1f} KB")
    with t2:
        st.markdown("### Audit Log")
        st.dataframe(dl.query_df("SELECT ts, username, action FROM audit_log ORDER BY id DESC LIMIT 100"),
                     use_container_width=True, height=380)
    with t3:
        st.markdown("### Reload Data"); st.warning("This REPLACES all channel/show data.")
        if st.button("🔄 Reload"):
            with st.spinner("Reloading…"):
                n_ch=dl.load_channels(); n_sh=dl.load_shows()
                dl.write_audit(username,"data_reload")
            st.success(f"Reloaded {n_ch} channels, {n_sh} shows")


# ── Banner ────────────────────────────────────────────────────────────────────
def render_banner(name, username):
    role=_get_role(username)
    st.markdown(f"""
    <div class="banner">
        <div><img src="data:image/png;base64,{logo_small_base64}" width="110"></div>
        <div>
            <div class="banner-title">TAM — EIKONA Dashboard</div>
            <div class="banner-sub">
                Good Day, <strong>{name}</strong> 👋 &nbsp;·&nbsp;
                Here's the latest update on your media analytics
                &nbsp;·&nbsp; {_badge(role)}
                &nbsp;·&nbsp; <span style="font-size:.7rem;opacity:.7">🔒 Secure Session</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar(username):
    role  = _get_role(username)
    access = ROLE_ACCESS.get(role,[])
    name  = st.session_state.get("name", username)

    nav_items = {
        "analytics": ("📈","Analytics"),
        "print":     ("🗞️","Print"),
        "online":    ("🌐","Online"),
        "tv":        ("📺","TV"),
        "social":    ("📱","Social Media"),
        "admin":     ("⚙️","Admin"),
    }

    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="padding:20px 16px 12px;border-bottom:1px solid #F3F4F6;margin-bottom:6px;">
            <div style="font-size:1rem;font-weight:700;color:#111827;letter-spacing:-.01em;">EIKONA</div>
            <div style="font-size:0.67rem;color:#9CA3AF;margin-top:1px;font-weight:600;
                        text-transform:uppercase;letter-spacing:.06em;">Media Intelligence</div>
        </div>
        """, unsafe_allow_html=True)

        # User pill
        initials="".join(w[0].upper() for w in name.split()[:2]) if name else "U"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:9px 14px;
                    background:#F5F3FF;border-radius:9px;margin:0 6px 6px;">
            <div style="width:34px;height:34px;border-radius:50%;
                        background:linear-gradient(135deg,#4F46E5,#6366F1);
                        display:flex;align-items:center;justify-content:center;
                        font-size:.85rem;color:#fff;font-weight:700;flex-shrink:0">{initials}</div>
            <div>
                <div style="font-size:.84rem;font-weight:600;color:#111827;">{name}</div>
                <div style="font-size:.68rem;color:#6B7280;text-transform:capitalize;">{role}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<span class="sidebar-section-label">Navigation</span>', unsafe_allow_html=True)

        choices=[(k,f"{icon}  {label}") for k,(icon,label) in nav_items.items() if k in access]
        labels=[c[1] for c in choices]; keys=[c[0] for c in choices]
        sel=st.radio("", labels, label_visibility="collapsed")
        selected_key=keys[labels.index(sel)]

        st.markdown("<hr>", unsafe_allow_html=True)
        try:
            authenticator.logout("↪  Logout", location="sidebar")
        except Exception:
            if st.button("↪  Logout"):
                for k in ["name","authentication_status","username"]:
                    st.session_state.pop(k,None)
                st.rerun()

    return selected_key


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # Check if already authenticated (from session_state cookie)
    pre_auth = st.session_state.get("authentication_status")
    pre_user = st.session_state.get("username")

    # If not yet logged in, show logo card FIRST, then render login form below it
    if not pre_auth:
        show_login()

    try:
        result=authenticator.login(location="main")
        if result is not None:
            name,auth_status,username=result
        else:
            name=st.session_state.get("name")
            auth_status=st.session_state.get("authentication_status")
            username=st.session_state.get("username")
    except Exception:
        name=st.session_state.get("name")
        auth_status=st.session_state.get("authentication_status")
        username=st.session_state.get("username")

    if auth_status is False:
        st.error("❌ Invalid credentials.")
        st.markdown(
            "<p style='text-align:center;color:#64748B;font-size:.8rem;margin-top:4px'>",
            unsafe_allow_html=True); return
    if auth_status is None:
        st.markdown(
            "<p style='text-align:center;color:#64748B;font-size:.8rem;margin-top:4px'>"
            ,
            unsafe_allow_html=True); return
    if not username:
        st.warning("⚠️ Session lost — refresh and log in again."); return

    # Sidebar MUST be rendered before banner so Streamlit keeps it expanded
    panel = render_sidebar(username)
    render_banner(name, username)
    dl.write_audit(username, "login")

    dispatch={
        "analytics": render_analytics,
        "print":     lambda u: render_platform_dashboard(u,_get_role(u),"print"),
        "online":    lambda u: render_platform_dashboard(u,_get_role(u),"online"),
        "tv":        lambda u: render_platform_dashboard(u,_get_role(u),"tv"),
        "social":    lambda u: render_platform_dashboard(u,_get_role(u),"social"),
        "admin":     render_admin,
    }
    if panel in dispatch and _can(username,panel):
        dispatch[panel](username)
    else:
        st.error("🚫 Access denied for your role.")

if __name__=="__main__":
    main()
