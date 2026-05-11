import streamlit as st
from utils.youtube import get_channel_data, get_channel_videos
from utils.metrics import calculate_metrics
from utils.scoring import calculate_scores
from utils.groq_analysis import (
    generate_ai_analysis, generate_ai_insights,
    generate_sponsorship_recommendations
)
from components.cards import (
    render_score_cards, render_insight_cards,
    render_brand_safety_card, render_sponsorship_cards
)
from components.charts import render_subscriber_growth_chart

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Creatrix — Creator Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── API KEYS ─────────────────────────────────────────────────────────────────
try:
    YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
    GROQ_API_KEY    = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error(
        "⚠️  API keys not found. Go to **Settings → Secrets** and add:\n\n"
        "```\nYOUTUBE_API_KEY = 'AIza...'\nGROQ_API_KEY = 'gsk_...'\n```"
    )
    st.stop()

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "input"
if "active_stage" not in st.session_state:
    st.session_state.active_stage = 0
if "stage_done" not in st.session_state:
    st.session_state.stage_done = []
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap');

:root {
    --bg:        #070a11;
    --bg2:       #0b0f1c;
    --bg3:       #0f1525;
    --glass:     rgba(15,21,37,0.72);
    --border:    rgba(79,158,255,0.08);
    --border-hi: rgba(79,158,255,0.24);
    --blue:      #4f9eff;
    --cyan:      #00d4ff;
    --purple:    #8b5cf6;
    --green:     #00ff9d;
    --amber:     #ffbe0b;
    --red:       #ff4d6d;
    --t1:        #e8f0fe;
    --t2:        #6b7f96;
    --t3:        #2e3d50;
    --grad:      linear-gradient(135deg,#4f9eff 0%,#00d4ff 100%);
    --grad2:     linear-gradient(135deg,#8b5cf6 0%,#4f9eff 100%);
}

*, *::before, *::after { box-sizing: border-box; }
* { font-family: 'DM Sans', sans-serif; }
h1,h2,h3,h4,h5,h6 { font-family: 'Syne', sans-serif !important; color: var(--t1) !important; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: var(--bg) !important;
    color: var(--t1) !important;
}

/* Ambient background glow */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background:
        radial-gradient(ellipse 900px 600px at 10% 0%, rgba(79,158,255,0.05) 0%, transparent 65%),
        radial-gradient(ellipse 700px 500px at 90% 90%, rgba(139,92,246,0.05) 0%, transparent 65%);
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 260px !important;
    max-width: 260px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1.4rem 1.1rem !important;
}

/* ── INPUTS ── */
.stTextArea textarea, .stTextInput input {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--t1) !important;
    font-size: 0.88rem !important;
    transition: border-color .2s, box-shadow .2s !important;
    padding: 0.7rem 0.95rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 2px rgba(79,158,255,0.18) !important;
    outline: none !important;
}
.stSelectbox > div > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--t1) !important;
}
.stSelectbox > div > div:focus-within {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 2px rgba(79,158,255,0.18) !important;
}

/* ── LABELS ── */
label,
.stTextInput label, .stTextArea label,
.stSelectbox label, .stMultiSelect label, .stSlider label {
    color: var(--t2) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: var(--grad) !important;
    border: none !important;
    border-radius: 14px !important;
    color: #fff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.85rem 2rem !important;
    letter-spacing: 0.03em !important;
    box-shadow: 0 6px 28px rgba(79,158,255,0.3) !important;
    transition: all .22s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 36px rgba(79,158,255,0.45) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── PROGRESS ── */
[data-testid="stProgress"] > div > div {
    background: var(--grad) !important;
    border-radius: 99px !important;
}

/* ── TABS ── */
[data-testid="stTabs"] { border-bottom: 1px solid var(--border) !important; }
[data-testid="stTabs"] button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: var(--t2) !important;
    border: none !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.02em !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--blue) !important;
    border-bottom: 2px solid var(--blue) !important;
    background: transparent !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    backdrop-filter: blur(14px) !important;
}
[data-testid="stExpander"] summary { color: var(--t1) !important; }

/* ── HIDE CHROME ── */
footer, #MainMenu, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"] { display: none !important; }

/* ─────────────────────────────────────
   UTILITY CLASSES
───────────────────────────────────── */

/* Glass card */
.card {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.5rem 1.6rem;
    backdrop-filter: blur(16px);
    margin-bottom: 1rem;
    transition: border-color .22s, box-shadow .22s, transform .22s;
}
.card:hover {
    border-color: var(--border-hi);
    box-shadow: 0 4px 32px rgba(79,158,255,0.08);
}

/* Score card */
.score-hero {
    background: linear-gradient(145deg, rgba(15,21,37,0.9), rgba(11,15,28,0.95));
    border: 1px solid var(--border-hi);
    border-radius: 22px;
    padding: 2.2rem 2rem;
    text-align: center;
    backdrop-filter: blur(20px);
    box-shadow: 0 12px 48px rgba(79,158,255,0.12);
    margin-bottom: 1rem;
}

/* Section heading */
.sec-head {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--t1);
    margin: 2rem 0 0.9rem;
}
.sec-head::before {
    content: '';
    width: 3px; height: 17px;
    background: var(--grad);
    border-radius: 3px;
    flex-shrink: 0;
}

/* KV rows */
.kv { display: flex; justify-content: space-between; align-items: center;
      padding: 0.55rem 0; border-bottom: 1px solid var(--border); }
.kv:last-child { border-bottom: none; }
.kv-k { color: var(--t2); font-size: 0.83rem; }
.kv-v { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.87rem; color: var(--t1); }

/* Pill badge */
.pill {
    display: inline-block;
    background: rgba(79,158,255,0.1);
    border: 1px solid rgba(79,158,255,0.2);
    border-radius: 999px;
    padding: 3px 12px;
    font-size: 0.68rem;
    color: var(--blue);
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    letter-spacing: 0.04em;
}

/* Insight cards */
.insight-card {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.2rem 1.3rem;
    backdrop-filter: blur(14px);
    transition: border-color .2s, box-shadow .2s;
    height: 100%;
}
.insight-card:hover {
    border-color: var(--border-hi);
    box-shadow: 0 4px 24px rgba(79,158,255,0.1);
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — Workflow Tracker
# ═══════════════════════════════════════════════════════════════════════════════

STAGES = [
    ("📋", "Campaign Brief"),
    ("👥", "Audience Understanding"),
    ("🎬", "Creator Analysis"),
    ("🎯", "Match Scoring"),
    ("🧬", "Audience Persona"),
    ("🛡️", "Brand Safety"),
    ("💼", "Sponsorship Readiness"),
    ("🧠", "AI Insights"),
    ("🚀", "Recommendations"),
]

with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding: 0.2rem 0 1.8rem;">
        <div style="font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:800;
            background: linear-gradient(135deg,#4f9eff,#00d4ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; letter-spacing:-0.01em; margin-bottom:3px;">
            ⚡ Creatrix
        </div>
        <div style="font-size:0.6rem; color:#3a4a5c; letter-spacing:0.12em;
            text-transform:uppercase;">Creator Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    # Stage tracker
    st.markdown("""
    <div style="font-size:0.6rem; font-weight:700; letter-spacing:0.12em;
        text-transform:uppercase; color:#3a4a5c; margin-bottom:0.7rem;">
        Analysis Workflow
    </div>
    """, unsafe_allow_html=True)

    done = st.session_state.stage_done
    active = st.session_state.active_stage

    for i, (icon, label) in enumerate(STAGES):
        is_active = (i == active)
        is_done   = (i in done)

        if is_done:
            bg      = "rgba(0,255,157,0.07)"
            border  = "rgba(0,255,157,0.22)"
            num_bg  = "rgba(0,255,157,0.15)"
            num_col = "#00ff9d"
            lbl_col = "#a0e8c8"
            marker  = "✓"
        elif is_active:
            bg      = "rgba(79,158,255,0.1)"
            border  = "rgba(79,158,255,0.32)"
            num_bg  = "rgba(79,158,255,0.2)"
            num_col = "#4f9eff"
            lbl_col = "#e8f0fe"
            marker  = str(i + 1)
        else:
            bg      = "transparent"
            border  = "rgba(79,158,255,0.06)"
            num_bg  = "rgba(79,158,255,0.05)"
            num_col = "#3a4a5c"
            lbl_col = "#3a4a5c"
            marker  = str(i + 1)

        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px;
            background:{bg}; border:1px solid {border}; border-radius:10px;
            padding:0.52rem 0.7rem; margin-bottom:5px;
            transition: all .2s ease; cursor: {'pointer' if is_done else 'default'};">
            <div style="width:22px; height:22px; border-radius:50%;
                background:{num_bg}; display:flex; align-items:center; justify-content:center;
                font-size:0.6rem; font-weight:800; color:{num_col};
                font-family:'Syne',sans-serif; flex-shrink:0;">{marker}</div>
            <div style="font-size:0.72rem; font-weight:{'600' if is_active or is_done else '400'};
                color:{lbl_col}; font-family:'Syne',sans-serif;">{icon} {label}</div>
        </div>
        """, unsafe_allow_html=True)

    # Back button (only on results page)
    if st.session_state.page == "output":
        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="height:1px; background:rgba(79,158,255,0.08); margin-bottom:1rem;"></div>
        """, unsafe_allow_html=True)
        if st.button("← New Analysis", use_container_width=True):
            st.session_state.page = "input"
            st.session_state.active_stage = 0
            st.session_state.stage_done = []
            st.session_state.analysis_data = None
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — USER INPUT
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.page == "input":

    # Center the form in a narrower column
    _, center, _ = st.columns([1, 3, 1])

    with center:
        # Hero header
        st.markdown("""
        <div style="text-align:center; padding:2.5rem 0 2rem;">
            <div style="display:inline-block; background:rgba(79,158,255,0.09);
                border:1px solid rgba(79,158,255,0.22); border-radius:999px;
                padding:4px 16px; font-size:0.62rem; color:#4f9eff;
                font-family:'Syne',sans-serif; font-weight:700;
                letter-spacing:0.12em; text-transform:uppercase; margin-bottom:1rem;">
                ⚡ Step-by-Step Creator Intelligence
            </div>
            <div style="font-family:'Syne',sans-serif; font-size:2.5rem; font-weight:800;
                background:linear-gradient(135deg,#e8f0fe 0%,#4f9eff 50%,#00d4ff 100%);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                background-clip:text; letter-spacing:-0.025em; line-height:1.1;
                margin-bottom:0.75rem;">
                Find Your Perfect<br>Creator Match
            </div>
            <div style="color:#6b7f96; font-size:0.92rem; max-width:420px;
                margin:0 auto; line-height:1.65;">
                Enter your campaign details below. Creatrix's AI engine will analyze
                the creator and surface deep partnership intelligence.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── FORM CARD ──────────────────────────────────────────────────────────
        st.markdown('<div class="card" style="padding:2rem 2.2rem;">', unsafe_allow_html=True)

        # 1. Brand Name
        st.markdown("""
        <div style="font-size:0.68rem; font-weight:700; letter-spacing:0.1em;
            text-transform:uppercase; color:#6b7f96; margin-bottom:0.35rem;">
            Brand Name
        </div>
        """, unsafe_allow_html=True)
        brand_name = st.text_input(
            "brand_name",
            placeholder="e.g. Notion, Linear, Figma …",
            label_visibility="collapsed",
            key="inp_brand"
        )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # 2. Marketing Brief
        st.markdown("""
        <div style="font-size:0.68rem; font-weight:700; letter-spacing:0.1em;
            text-transform:uppercase; color:#6b7f96; margin-bottom:0.35rem;">
            Marketing Brief
        </div>
        """, unsafe_allow_html=True)
        brand_brief = st.text_area(
            "brand_brief",
            placeholder="We want to promote our AI productivity tool to students and young professionals.",
            height=110,
            label_visibility="collapsed",
            key="inp_brief"
        )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # 3. Target Audience — gender + age side by side
        st.markdown("""
        <div style="font-size:0.68rem; font-weight:700; letter-spacing:0.1em;
            text-transform:uppercase; color:#6b7f96; margin-bottom:0.35rem;">
            Target Audience
        </div>
        """, unsafe_allow_html=True)
        col_g, col_a1, col_a2 = st.columns([2, 1, 1])
        with col_g:
            audience_gender = st.selectbox(
                "Gender",
                ["All Genders", "Male", "Female", "Non-binary"],
                key="inp_gender"
            )
        with col_a1:
            age_min = st.number_input("Age Min", min_value=13, max_value=65,
                                       value=18, key="inp_amin")
        with col_a2:
            age_max = st.number_input("Age Max", min_value=13, max_value=65,
                                       value=34, key="inp_amax")

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # 4. Campaign Goal
        st.markdown("""
        <div style="font-size:0.68rem; font-weight:700; letter-spacing:0.1em;
            text-transform:uppercase; color:#6b7f96; margin-bottom:0.35rem;">
            Campaign Goal
        </div>
        """, unsafe_allow_html=True)
        campaign_goal = st.selectbox(
            "Campaign Goal",
            ["Awareness", "Engagement", "App Installs", "Conversions", "Product Launch"],
            label_visibility="collapsed",
            key="inp_goal"
        )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # 5. YouTube Channel URL
        st.markdown("""
        <div style="font-size:0.68rem; font-weight:700; letter-spacing:0.1em;
            text-transform:uppercase; color:#6b7f96; margin-bottom:0.35rem;">
            Creator YouTube Channel URL
        </div>
        """, unsafe_allow_html=True)
        channel_url = st.text_input(
            "channel_url",
            placeholder="https://youtube.com/@channelhandle  or  /channel/UCxxxxxxxxx",
            label_visibility="collapsed",
            key="inp_url"
        )

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        # CTA Button
        analyze_btn = st.button("⚡  Analyze Creator Match", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)  # close .card

        # ── FEATURE TILES ──────────────────────────────────────────────────────
        st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)
        t1, t2, t3 = st.columns(3)
        tiles = [
            ("🎯", "Match Scoring", "5-dimensional AI fit scoring against your campaign brief."),
            ("🧠", "Deep AI Analysis", "Groq LLM surfaces audience persona, content themes & insights."),
            ("🛡️", "Brand Safety", "Risk scoring, sponsorship readiness, integration recommendations."),
        ]
        for col, (icon, ttl, desc) in zip([t1, t2, t3], tiles):
            with col:
                st.markdown(f"""
                <div class="card" style="text-align:center; padding:1.5rem 1rem;">
                    <div style="font-size:1.6rem; margin-bottom:0.6rem;">{icon}</div>
                    <div style="font-family:'Syne',sans-serif; font-weight:700;
                        font-size:0.82rem; color:#e8f0fe; margin-bottom:0.4rem;">{ttl}</div>
                    <div style="font-size:0.77rem; color:#6b7f96; line-height:1.55;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── ANALYSIS TRIGGER ──────────────────────────────────────────────────────
    if analyze_btn:
        if not channel_url.strip():
            st.error("⚠️  Please enter a YouTube channel URL.")
            st.stop()
        if not brand_brief.strip():
            st.error("⚠️  Please enter a marketing brief.")
            st.stop()

        campaign_config = {
            "brand_name":      brand_name,
            "brand_brief":     brand_brief,
            "campaign_goals":  [campaign_goal],
            "age_range":       (age_min, age_max),
            "audience_gender": audience_gender,
        }

        # Progress states mapped to sidebar stages
        PROGRESS_STEPS = [
            (0,  10,  "🔍  Fetching channel metadata …"),
            (1,  24,  "📹  Pulling latest 50 videos …"),
            (2,  38,  "📊  Computing engagement & cadence metrics …"),
            (3,  52,  "⚡  Calculating creator fit scores …"),
            (4,  66,  "🧬  Generating audience persona …"),
            (5,  78,  "🛡️  Running brand safety checks …"),
            (6,  85,  "💼  Evaluating sponsorship readiness …"),
            (7,  91,  "🧠  Surfacing AI insight cards …"),
            (8,  97,  "🚀  Building recommendations …"),
        ]

        _, pcol, _ = st.columns([1, 3, 1])
        with pcol:
            progress_bar = st.progress(0)
            status_slot  = st.empty()

        def _step(stage_idx, pct, msg):
            st.session_state.active_stage = stage_idx
            if stage_idx > 0:
                st.session_state.stage_done = list(range(stage_idx))
            status_slot.markdown(
                f'<div style="font-family:Syne,sans-serif; font-size:0.8rem;'
                f'color:#4f9eff; letter-spacing:0.04em; text-align:center;'
                f'margin-top:0.5rem;">{msg}</div>',
                unsafe_allow_html=True
            )
            progress_bar.progress(pct)

        # Run pipeline
        _step(0, 10, "🔍  Fetching channel metadata …")
        channel_data = get_channel_data(channel_url.strip(), YOUTUBE_API_KEY)
        if not channel_data:
            progress_bar.empty(); status_slot.empty()
            st.error("❌  Could not fetch this channel. Check the URL and ensure YouTube Data API v3 is enabled.")
            st.stop()

        _step(1, 24, "📹  Pulling latest 50 videos …")
        videos_data = get_channel_videos(channel_data["channel_id"], YOUTUBE_API_KEY)

        _step(2, 38, "📊  Computing metrics …")
        metrics = calculate_metrics(channel_data, videos_data)

        _step(3, 52, "⚡  Scoring creator fit …")
        scores = calculate_scores(metrics, campaign_config)

        _step(4, 66, "🧬  Generating audience persona …")
        ai_analysis = generate_ai_analysis(channel_data, metrics, scores, campaign_config, GROQ_API_KEY)

        _step(5, 78, "🛡️  Brand safety check …")
        # Brand safety is part of scores; no extra call needed

        _step(6, 85, "💼  Sponsorship readiness …")
        sponsorship_recs = generate_sponsorship_recommendations(
            channel_data, metrics, scores, campaign_config, GROQ_API_KEY
        )

        _step(7, 91, "🧠  AI insight cards …")
        ai_insights = generate_ai_insights(channel_data, metrics, videos_data, GROQ_API_KEY)

        _step(8, 97, "🚀  Building recommendations …")

        progress_bar.progress(100)
        status_slot.empty()
        progress_bar.empty()

        # Store all results
        st.session_state.analysis_data = {
            "channel_data":     channel_data,
            "videos_data":      videos_data,
            "metrics":          metrics,
            "scores":           scores,
            "ai_analysis":      ai_analysis,
            "ai_insights":      ai_insights,
            "sponsorship_recs": sponsorship_recs,
            "campaign_config":  campaign_config,
        }
        st.session_state.stage_done   = list(range(9))
        st.session_state.active_stage = 8
        st.session_state.page         = "output"
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — AI OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "output":

    d   = st.session_state.analysis_data
    ch  = d["channel_data"]
    m   = d["metrics"]
    s   = d["scores"]
    ai  = d["ai_analysis"]
    ins = d["ai_insights"]
    rec = d["sponsorship_recs"]
    cfg = d["campaign_config"]
    vids = d["videos_data"]

    def _fmt(n):
        try:
            n = int(n)
            if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
            if n >= 1_000:     return f"{n/1_000:.1f}K"
            return str(n)
        except Exception:
            return "—"

    # ── CHANNEL IDENTITY BANNER ───────────────────────────────────────────────
    topics = ch.get("topics", [])
    pills  = " ".join([
        f'<span class="pill">{t}</span>'
        for t in topics[:4]
    ])

    brand_name_display = cfg.get("brand_name") or "Your Brand"

    st.markdown(f"""
    <div class="card" style="display:flex; align-items:center; gap:1.4rem;
        padding:1.4rem 1.8rem; border-top:2px solid rgba(79,158,255,0.2);
        margin-top:0.8rem;">
        <img src="{ch.get('thumbnail','')}"
             style="width:68px; height:68px; border-radius:50%; object-fit:cover;
                    border:2px solid rgba(79,158,255,0.35); flex-shrink:0;"
             onerror="this.style.display='none'"/>
        <div style="flex:1; min-width:0;">
            <div style="font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:800;
                color:#e8f0fe; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                {ch.get('title','Channel')}
            </div>
            <div style="color:#6b7f96; font-size:0.82rem; margin-top:3px;
                white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                {ch.get('description','')[:130]}{'…' if len(ch.get('description','')) > 130 else ''}
            </div>
            <div style="margin-top:8px; display:flex; gap:6px; flex-wrap:wrap;">{pills}</div>
        </div>
        <div style="display:flex; gap:2.2rem; flex-shrink:0; padding-left:1rem;
            border-left:1px solid rgba(79,158,255,0.1);">
            {''.join([
                f'<div style="text-align:center;">'
                f'<div style="font-family:Syne,sans-serif; font-size:1.4rem; font-weight:800; color:{c};">{_fmt(v)}</div>'
                f'<div style="font-size:0.6rem; color:#6b7f96; text-transform:uppercase; letter-spacing:0.08em;">{lbl}</div>'
                f'</div>'
                for v,lbl,c in [
                    (ch.get('subscriber_count',0),'Subscribers','#4f9eff'),
                    (ch.get('video_count',0),'Videos','#00d4ff'),
                    (ch.get('view_count',0),'Total Views','#8b5cf6'),
                ]
            ])}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    #  SECTION 1 — CREATOR-BRAND MATCH SCORE  (hero card)
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-head">🎯 Creator-Brand Match Score</div>', unsafe_allow_html=True)

    overall = s.get("overall_score", s.get("creator_fit_score", 0))
    if overall >= 80:   score_color, score_label = "#00ff9d", "Excellent Match"
    elif overall >= 65: score_color, score_label = "#4f9eff", "Strong Match"
    elif overall >= 50: score_color, score_label = "#ffbe0b", "Moderate Match"
    else:               score_color, score_label = "#ff4d6d", "Weak Match"

    match_exp = ai.get("match_explanation", "Analysis not available.")

    col_hero, col_sub = st.columns([1, 2])
    with col_hero:
        st.markdown(f"""
        <div class="score-hero">
            <div style="font-size:0.65rem; font-weight:700; letter-spacing:0.12em;
                text-transform:uppercase; color:#6b7f96; margin-bottom:0.8rem;">
                {brand_name_display} × {ch.get('title','Creator')}
            </div>
            <div style="font-family:'Syne',sans-serif; font-size:4rem; font-weight:800;
                color:{score_color}; line-height:1; margin-bottom:0.4rem;">
                {overall}
            </div>
            <div style="font-size:0.65rem; color:{score_color}; font-weight:700;
                letter-spacing:0.1em; text-transform:uppercase; margin-bottom:1.2rem;">
                {score_label}
            </div>
            <div style="display:flex; gap:0.7rem; justify-content:center; flex-wrap:wrap;">
                {' '.join([
                    f'<div style="text-align:center; padding:0.4rem 0.8rem;'
                    f'background:rgba(79,158,255,0.07); border:1px solid rgba(79,158,255,0.14);'
                    f'border-radius:10px;">'
                    f'<div style="font-family:Syne,sans-serif; font-weight:800; font-size:0.95rem; color:{c};">{s.get(k,0)}</div>'
                    f'<div style="font-size:0.57rem; color:#6b7f96; text-transform:uppercase; letter-spacing:0.07em;">{lbl}</div>'
                    f'</div>'
                    for k,lbl,c in [
                        ('creator_fit_score','Creator Fit','#4f9eff'),
                        ('audience_match_score','Audience','#8b5cf6'),
                        ('brand_safety_score','Safety','#00ff9d'),
                        ('sponsorship_readiness_score','Readiness','#ffbe0b'),
                    ]
                ])}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_sub:
        st.markdown(f"""
        <div class="card" style="height:100%; border-left:3px solid {score_color};">
            <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.1em;
                text-transform:uppercase; color:{score_color}; margin-bottom:0.9rem;">
                🧠 AI Match Explanation
            </div>
            <div style="color:#e8f0fe; font-size:0.92rem; line-height:1.78;">
                {match_exp}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    #  SECTION 2 — AUDIENCE PERSONA
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-head">🧬 Audience Persona</div>', unsafe_allow_html=True)
    persona_text = ai.get("audience_persona", "Audience data not available.")

    col_p, col_q = st.columns(2)
    with col_p:
        st.markdown(f"""
        <div class="card" style="border-left:3px solid #8b5cf6;">
            <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.1em;
                text-transform:uppercase; color:#8b5cf6; margin-bottom:0.9rem;">
                👥 Audience Profile · Score {s.get('audience_match_score',0)}/100
            </div>
            <div style="color:#e8f0fe; font-size:0.9rem; line-height:1.76;">
                {persona_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_q:
        # Content themes from AI or fallback
        themes_raw = ai.get("content_themes", [])
        if isinstance(themes_raw, list):
            theme_pills = "".join([
                f'<span class="pill" style="margin:3px;">{t}</span>'
                for t in themes_raw[:8]
            ])
        else:
            theme_pills = f'<div style="font-size:0.88rem; color:#e8f0fe; line-height:1.7;">{themes_raw}</div>'

        st.markdown(f"""
        <div class="card" style="border-left:3px solid #00d4ff;">
            <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.1em;
                text-transform:uppercase; color:#00d4ff; margin-bottom:0.9rem;">
                🏷️ Content Themes
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:4px; margin-top:0.2rem;">
                {theme_pills}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    #  SECTION 3 — CHANNEL ANALYTICS
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-head">📊 Channel Analytics</div>', unsafe_allow_html=True)

    ca, cb, cc, cd, ce = st.columns(5)
    analytics_tiles = [
        (ca, "Subscribers",     _fmt(ch.get('subscriber_count',0)), "#4f9eff"),
        (cb, "Avg Views",       _fmt(m.get('avg_views_per_video',0)), "#00d4ff"),
        (cc, "Engagement Rate", f"{m.get('avg_engagement_rate',0):.2%}", "#8b5cf6"),
        (cd, "Uploads / Week",  f"{m.get('upload_frequency',0):.1f}", "#00ff9d"),
        (ce, "Shorts Ratio",    f"{m.get('shorts_ratio',0):.0%}", "#ffbe0b"),
    ]
    for col, label, val, color in analytics_tiles:
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center; padding:1.2rem 0.8rem;">
                <div style="font-family:'Syne',sans-serif; font-size:1.6rem; font-weight:800;
                    color:{color}; line-height:1; margin-bottom:0.4rem;">{val}</div>
                <div style="font-size:0.65rem; color:#6b7f96; text-transform:uppercase;
                    letter-spacing:0.08em;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    #  SECTION 4 — GROWTH TREND CHART
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-head">📈 Growth Trend</div>', unsafe_allow_html=True)
    render_subscriber_growth_chart(m)

    # ══════════════════════════════════════════════════════════════════
    #  SECTION 5 — BRAND SAFETY + SPONSORSHIP READINESS
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-head">🛡️ Brand Safety & Sponsorship Readiness</div>',
                unsafe_allow_html=True)

    bs_score = s.get("brand_safety_score", 0)
    if bs_score >= 80:   bs_col, bs_label = "#00ff9d", "Low Risk"
    elif bs_score >= 60: bs_col, bs_label = "#ffbe0b", "Moderate Risk"
    else:                bs_col, bs_label = "#ff4d6d", "High Risk"

    sp_score = s.get("sponsorship_readiness_score", 0)
    if sp_score >= 75:   sp_col, sp_label = "#00ff9d", "Highly Ready"
    elif sp_score >= 55: sp_col, sp_label = "#4f9eff", "Ready"
    else:                sp_col, sp_label = "#ffbe0b", "Developing"

    col_bs, col_sp = st.columns(2)
    with col_bs:
        st.markdown(f"""
        <div class="card" style="border-left:3px solid {bs_col};">
            <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.1em;
                text-transform:uppercase; color:{bs_col}; margin-bottom:0.4rem;">
                🛡️ Brand Safety Score
            </div>
            <div style="font-family:'Syne',sans-serif; font-size:2.2rem; font-weight:800;
                color:{bs_col}; line-height:1; margin-bottom:0.3rem;">{bs_score}</div>
            <div style="font-size:0.78rem; color:{bs_col}; font-weight:600;
                margin-bottom:0.8rem;">{bs_label}</div>
            <div style="color:#6b7f96; font-size:0.83rem; line-height:1.65;">
                {ai.get('brand_safety_notes', 'No significant brand safety concerns detected.')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_sp:
        st.markdown(f"""
        <div class="card" style="border-left:3px solid {sp_col};">
            <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.1em;
                text-transform:uppercase; color:{sp_col}; margin-bottom:0.4rem;">
                💼 Sponsorship Readiness
            </div>
            <div style="font-family:'Syne',sans-serif; font-size:2.2rem; font-weight:800;
                color:{sp_col}; line-height:1; margin-bottom:0.3rem;">{sp_score}</div>
            <div style="font-size:0.78rem; color:{sp_col}; font-weight:600;
                margin-bottom:0.8rem;">{sp_label}</div>
            <div class="kv">
                <span class="kv-k">Audience Trust</span>
                <span class="kv-v" style="color:{sp_col};">{s.get('audience_trust_score', sp_score)}/100</span>
            </div>
            <div class="kv">
                <span class="kv-k">Engagement Consistency</span>
                <span class="kv-v">{s.get('engagement_consistency', 'N/A')}</span>
            </div>
            <div class="kv">
                <span class="kv-k">Upload Consistency</span>
                <span class="kv-v">{m.get('upload_frequency', 0):.1f}× / week</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    #  SECTION 6 — SPONSORSHIP RECOMMENDATIONS
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-head">🚀 Sponsorship Recommendations</div>', unsafe_allow_html=True)

    recs_list = rec.get("recommendations", [])
    if recs_list and isinstance(recs_list, list):
        rec_cols = st.columns(min(len(recs_list), 3))
        for i, (col, item) in enumerate(zip(rec_cols, recs_list[:3])):
            with col:
                icon_map = ["🎬", "⚡", "📱"]
                st.markdown(f"""
                <div class="card" style="padding:1.3rem;">
                    <div style="font-size:1.4rem; margin-bottom:0.5rem;">{icon_map[i]}</div>
                    <div style="font-family:'Syne',sans-serif; font-size:0.82rem; font-weight:700;
                        color:#e8f0fe; margin-bottom:0.4rem;">
                        {item.get('type', item) if isinstance(item, dict) else item}
                    </div>
                    <div style="font-size:0.78rem; color:#6b7f96; line-height:1.55;">
                        {item.get('description','') if isinstance(item, dict) else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        talking = rec.get("talking_points", "")
        if talking:
            st.markdown(f"""
            <div class="card" style="border-left:3px solid #00ff9d;">
                <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.1em;
                    text-transform:uppercase; color:#00ff9d; margin-bottom:0.9rem;">
                    💰 Sponsorship Talking Points
                </div>
                <div style="color:#e8f0fe; font-size:0.9rem; line-height:1.78; white-space:pre-line;">
                    {talking}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    #  SECTION 7 — AI INSIGHT CARDS
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-head">🧠 AI Insight Cards</div>', unsafe_allow_html=True)

    # Fallback insight structure
    default_insights = [
        {"type": "strength",    "emoji": "🔥", "label": "Strength",    "color": "#00ff9d"},
        {"type": "weakness",    "emoji": "⚠️", "label": "Weakness",    "color": "#ff4d6d"},
        {"type": "opportunity", "emoji": "📈", "label": "Opportunity",  "color": "#4f9eff"},
    ]

    if isinstance(ins, list) and len(ins) > 0:
        ins_cols = st.columns(min(len(ins), 3))
        for col, insight in zip(ins_cols, ins[:3]):
            typ   = insight.get("type", "insight")
            emoji = insight.get("emoji", "💡")
            label = insight.get("label", typ.title())
            text  = insight.get("text", insight.get("content", ""))
            color_map = {"strength":"#00ff9d","weakness":"#ff4d6d","opportunity":"#4f9eff"}
            card_col  = color_map.get(typ.lower(), "#4f9eff")
            with col:
                st.markdown(f"""
                <div class="insight-card" style="border-top:2px solid {card_col};">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.7rem;">
                        <span style="font-size:1.3rem;">{emoji}</span>
                        <span style="font-family:'Syne',sans-serif; font-weight:700;
                            font-size:0.75rem; color:{card_col}; text-transform:uppercase;
                            letter-spacing:0.08em;">{label}</span>
                    </div>
                    <div style="color:#e8f0fe; font-size:0.88rem; line-height:1.65;">{text}</div>
                </div>
                """, unsafe_allow_html=True)
    elif isinstance(ins, dict):
        icols = st.columns(3)
        for col, meta in zip(icols, default_insights):
            text = ins.get(meta["type"], "")
            with col:
                st.markdown(f"""
                <div class="insight-card" style="border-top:2px solid {meta['color']};">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.7rem;">
                        <span style="font-size:1.3rem;">{meta['emoji']}</span>
                        <span style="font-family:'Syne',sans-serif; font-weight:700;
                            font-size:0.75rem; color:{meta['color']}; text-transform:uppercase;
                            letter-spacing:0.08em;">{meta['label']}</span>
                    </div>
                    <div style="color:#e8f0fe; font-size:0.88rem; line-height:1.65;">
                        {text or 'Analysis not available.'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Render whatever the component provides
        render_insight_cards(ins)

    # ══════════════════════════════════════════════════════════════════
    #  FOOTER SPACER
    # ══════════════════════════════════════════════════════════════════
    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; color:#2e3d50; font-size:0.68rem; letter-spacing:0.05em;">
        ⚡ Creatrix — Creator Intelligence Platform · Powered by Groq + YouTube · Built by Mahitha Bhagavathi
    </div>
    """, unsafe_allow_html=True)
