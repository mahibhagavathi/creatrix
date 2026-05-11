import streamlit as st
import textwrap
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
from components.charts import (
    render_subscriber_growth_chart,
    render_views_growth_chart,
    render_engagement_chart,
    render_content_distribution_chart
)

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Creatrix — Creator Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── API KEYS ─────────────────────────────────────────────────────────────────
# BUG FIX 1: bare `except:` swallowed the error silently AND st.stop() was
# outside the except block so the app always stopped regardless of success.
try:
    YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
    GROQ_API_KEY    = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error(
        "⚠️ API keys not found. Go to **Settings → Secrets** and add:\n\n"
        "```\nYOUTUBE_API_KEY = 'AIza...'\nGROQ_API_KEY = 'gsk_...'\n```"
    )
    st.stop()   # ← now correctly INSIDE the except block

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
st.markdown(textwrap.dedent("""
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

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background:
        radial-gradient(ellipse 900px 600px at 10% 0%, rgba(79,158,255,0.05) 0%, transparent 65%),
        radial-gradient(ellipse 700px 500px at 90% 90%, rgba(139,92,246,0.05) 0%, transparent 65%);
}

[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 260px !important;
    max-width: 260px !important;
}

.stTextArea textarea, .stTextInput input {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--t1) !important;
}

.stButton > button {
    background: var(--grad) !important;
    border: none !important;
    border-radius: 14px !important;
    color: #fff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    width: 100% !important;
}

.card {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.5rem 1.6rem;
    backdrop-filter: blur(16px);
    margin-bottom: 1rem;
}

.score-hero {
    background: linear-gradient(145deg, rgba(15,21,37,0.9), rgba(11,15,28,0.95));
    border: 1px solid var(--border-hi);
    border-radius: 22px;
    padding: 2.2rem 2rem;
    text-align: center;
}

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

.pill {
    display: inline-block;
    background: rgba(79,158,255,0.1);
    border: 1px solid rgba(79,158,255,0.2);
    border-radius: 999px;
    padding: 3px 12px;
    font-size: 0.68rem;
    color: var(--blue);
    font-family: 'Syne', sans-serif;
}

.insight-card {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.3rem 1.4rem;
    backdrop-filter: blur(14px);
    margin-bottom: 1rem;
}

.kv {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border);
}
.kv:last-child { border-bottom: none; }
.kv-k { color: var(--t2); font-size: 0.82rem; }
.kv-v { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.85rem; color: var(--t1); }

footer, #MainMenu, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"] { display: none !important; }
</style>
"""), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — Workflow Tracker + Campaign Inputs
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
    st.markdown(textwrap.dedent("""
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
    """), unsafe_allow_html=True)

    done   = st.session_state.stage_done
    active = st.session_state.active_stage

    for i, (icon, label) in enumerate(STAGES):
        is_active = (i == active)
        is_done   = (i in done)
        bg      = "rgba(79,158,255,0.1)" if is_active else "transparent"
        lbl_col = "#e8f0fe" if (is_active or is_done) else "#3a4a5c"
        st.markdown(textwrap.dedent(f"""
        <div style="display:flex; align-items:center; gap:10px; background:{bg};
            border-radius:10px; padding:0.52rem 0.7rem; margin-bottom:5px;">
            <div style="font-size:0.72rem; font-weight:600; color:{lbl_col};
                font-family:'Syne',sans-serif;">
                {icon} {label}
            </div>
        </div>
        """), unsafe_allow_html=True)

    if st.session_state.page == "output":
        if st.button("← New Analysis", use_container_width=True):
            st.session_state.page = "input"
            st.session_state.active_stage = 0
            st.session_state.stage_done = []
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — USER INPUT
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.page == "input":
    _, center, _ = st.columns([1, 3, 1])
    with center:
        st.markdown(textwrap.dedent("""
        <div style="text-align:center; padding:2.5rem 0 2rem;">
            <div style="font-family:'Syne',sans-serif; font-size:2.5rem; font-weight:800; color:#e8f0fe;">
                Find Your Perfect<br>Creator Match
            </div>
            <div style="color:#6b7f96; font-size:0.95rem; margin-top:0.6rem;">
                Fill in your campaign details and paste a YouTube channel URL to begin.
            </div>
        </div>
        """), unsafe_allow_html=True)

        brand_name  = st.text_input("Brand Name", placeholder="e.g. Notion")
        brand_brief = st.text_area(
            "Marketing Brief",
            placeholder="Describe your brand, product, campaign goals, and target outcome …",
            height=100
        )

        # Campaign Goals — multi-select
        campaign_goals = st.multiselect(
            "Campaign Goals",
            ["Awareness", "Consideration", "Conversions", "App Installs",
             "Product Launch", "Community Building", "Engagement", "Education", "Brand Recall"],
            default=["Awareness"]
        )

        # Target Audience
        st.markdown(
            '<div style="font-size:0.75rem;font-weight:600;color:#6b7f96;'
            'text-transform:uppercase;letter-spacing:0.06em;margin:1rem 0 0.4rem;">Target Audience</div>',
            unsafe_allow_html=True
        )
        col_g, col_a1, col_a2 = st.columns([2, 1, 1])
        with col_g:
            audience_gender = st.selectbox("Gender", ["All Genders", "Male", "Female", "Non-binary"])
        with col_a1:
            age_min = st.number_input("Age Min", 13, 65, 18)
        with col_a2:
            age_max = st.number_input("Age Max", 13, 65, 34)

        audience_locations = st.text_input("Locations", placeholder="India, US, UK …")
        audience_languages = st.multiselect(
            "Languages",
            ["English", "Hindi", "Hinglish", "Telugu", "Tamil", "Kannada", "Malayalam"],
            default=["English"]
        )

        # Creator filters
        st.markdown(
            '<div style="font-size:0.75rem;font-weight:600;color:#6b7f96;'
            'text-transform:uppercase;letter-spacing:0.06em;margin:1rem 0 0.4rem;">Creator Filters</div>',
            unsafe_allow_html=True
        )
        creator_genres = st.multiselect(
            "Creator Genre",
            ["Tech", "Lifestyle", "Beauty", "Finance", "Gaming", "Productivity",
             "Education", "Fitness", "Travel", "Entertainment", "Business", "AI", "Fashion", "Food"],
            default=["Tech"]
        )
        content_languages = st.multiselect(
            "Content Language",
            ["English", "Hindi", "Hinglish", "Telugu", "Tamil", "Kannada", "Malayalam"],
            default=["English"]
        )
        creator_persona = st.selectbox(
            "Creator Persona / Archetype",
            ["Educator", "Entertainer", "Thought Leader", "Motivator", "Storyteller",
             "Reviewer", "Trendsetter", "News Analyst", "Comedian",
             "Premium Luxury", "Relatable Everyday"]
        )
        sub_max = st.slider(
            "Max Subscriber Count", 0, 2_000_000, 500_000,
            step=25_000, format="%d"
        )
        st.caption(f"Up to **{sub_max:,}** subscribers")

        channel_url = st.text_input(
            "YouTube Channel URL",
            placeholder="https://youtube.com/@channelname"
        )

        analyze_btn = st.button("⚡  Analyze Creator Match")

    # ── Run Analysis ──────────────────────────────────────────────────────────
    if analyze_btn:
        if not channel_url.strip():
            st.error("⚠️ Please enter a YouTube channel URL.")
        else:
            progress = st.progress(0)
            status   = st.empty()

            def _step(msg, pct):
                status.markdown(
                    f'<div style="font-family:Syne,sans-serif;font-size:0.8rem;'
                    f'color:#4f9eff;letter-spacing:0.04em;text-align:center;">{msg}</div>',
                    unsafe_allow_html=True
                )
                progress.progress(pct)
                st.session_state.active_stage = pct // 12

            _step("🔍 Fetching channel metadata …", 10)
            channel_data = get_channel_data(channel_url.strip(), YOUTUBE_API_KEY)

            if not channel_data:
                progress.empty(); status.empty()
                st.error("❌ Could not fetch channel. Check the URL and your YouTube API key.")
            else:
                _step("📹 Pulling latest 50 videos …", 24)
                videos_data = get_channel_videos(channel_data["channel_id"], YOUTUBE_API_KEY)

                _step("📊 Computing metrics …", 40)
                metrics = calculate_metrics(channel_data, videos_data)

                cfg = {
                    "brand_name":        brand_name,
                    "brand_brief":       brand_brief,
                    "campaign_goals":    campaign_goals,
                    "age_range":         (age_min, age_max),
                    "audience_gender":   audience_gender,
                    "audience_locations": audience_locations,
                    "audience_languages": audience_languages,
                    "creator_genres":    creator_genres,
                    "content_languages": content_languages,
                    "creator_persona":   creator_persona,
                    "sub_max":           sub_max,
                }

                _step("⚡ Scoring creator fit …", 55)
                scores = calculate_scores(metrics, cfg)

                _step("🧠 Generating AI match intelligence …", 70)
                ai_analysis = generate_ai_analysis(channel_data, metrics, scores, cfg, GROQ_API_KEY)

                _step("💡 Building insight cards …", 84)
                ai_insights = generate_ai_insights(channel_data, metrics, videos_data, GROQ_API_KEY)

                _step("💰 Building sponsorship recommendations …", 94)
                # BUG FIX 2: variable was named `sponsorship_recs` in pipeline but
                # referenced as `rec` and `recs` in the output page — unified to sponsorship_recs
                sponsorship_recs = generate_sponsorship_recommendations(
                    channel_data, metrics, scores, cfg, GROQ_API_KEY
                )

                progress.progress(100)
                status.empty()
                progress.empty()

                st.session_state.active_stage  = len(STAGES) - 1
                st.session_state.stage_done    = list(range(len(STAGES)))
                st.session_state.analysis_data = {
                    "channel_data":    channel_data,
                    "metrics":         metrics,
                    "scores":          scores,
                    "ai_analysis":     ai_analysis,
                    "ai_insights":     ai_insights,
                    "sponsorship_recs": sponsorship_recs,
                    "campaign_config": cfg,
                    "videos_data":     videos_data,
                }
                st.session_state.page = "output"
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — AI OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "output":
    # BUG FIX 3: `ins` and `rec` were never defined — they should unpack from analysis_data
    d    = st.session_state.analysis_data
    ch   = d["channel_data"]
    m    = d["metrics"]
    s    = d["scores"]
    ai   = d["ai_analysis"]
    ins  = d["ai_insights"]          # ← was referenced as `ins` but never assigned
    rec  = d["sponsorship_recs"]     # ← was referenced as `rec` but never assigned
    cfg  = d["campaign_config"]
    videos_data = d["videos_data"]

    def _fmt(n):
        try:
            n = int(n)
            if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
            if n >= 1_000:     return f"{n/1_000:.1f}K"
            return str(n)
        except:
            return "—"

    # ── CHANNEL IDENTITY BANNER ───────────────────────────────────────────────
    topics = ch.get("topics", [])
    pills  = "".join([
        f'<span class="pill" style="margin-right:4px;">{t}</span>'
        for t in topics[:4]
    ])

    stats_html = "".join([
        f'<div style="text-align:center;">'
        f'<div style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:{c};">{_fmt(v)}</div>'
        f'<div style="font-size:0.6rem;color:#6b7f96;text-transform:uppercase;">{lbl}</div>'
        f'</div>'
        for v, lbl, c in [
            (ch.get('subscriber_count', 0), 'Subscribers', '#4f9eff'),
            (ch.get('video_count', 0),      'Videos',      '#00d4ff'),
            (ch.get('view_count', 0),       'Total Views', '#8b5cf6'),
        ]
    ])

    st.markdown(textwrap.dedent(f"""
    <div class="card" style="display:flex; align-items:center; gap:1.4rem; border-top:2px solid #4f9eff;">
        <img src="{ch.get('thumbnail','')}"
             style="width:68px; height:68px; border-radius:50%; border:2px solid #4f9eff;
                    object-fit:cover; flex-shrink:0;"
             onerror="this.style.display='none'"/>
        <div style="flex:1; min-width:0;">
            <div style="font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:800;
                color:#e8f0fe; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                {ch.get('title', 'Channel')}
            </div>
            <div style="margin-top:8px;">{pills}</div>
        </div>
        <div style="display:flex; gap:2.2rem; padding-left:1rem;
            border-left:1px solid rgba(79,158,255,0.1); flex-shrink:0;">
            {stats_html}
        </div>
    </div>
    """), unsafe_allow_html=True)

    # ── SECTION 1 — MATCH SCORE ───────────────────────────────────────────────
    st.markdown('<div class="sec-head">🎯 Creator-Brand Match Score</div>', unsafe_allow_html=True)

    overall     = s.get("overall_score", 0)
    score_color = "#00ff9d" if overall >= 75 else "#ffbe0b" if overall >= 50 else "#ff4d6d"

    col_hero, col_sub = st.columns([1, 2])
    with col_hero:
        st.markdown(textwrap.dedent(f"""
        <div class="score-hero">
            <div style="font-family:'Syne',sans-serif; font-size:4rem; font-weight:800;
                color:{score_color}; line-height:1;">{overall}</div>
            <div style="font-size:0.65rem; color:{score_color}; font-weight:700;
                text-transform:uppercase; letter-spacing:0.1em; margin-top:0.5rem;">
                Overall Match Score
            </div>
            <div style="margin-top:1rem; display:flex; flex-direction:column; gap:0.5rem;">
                <div style="display:flex; justify-content:space-between; font-size:0.78rem;">
                    <span style="color:#6b7f96;">Creator Fit</span>
                    <span style="color:#4f9eff; font-weight:700;">{s.get('creator_fit_score',0)}</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.78rem;">
                    <span style="color:#6b7f96;">Audience Match</span>
                    <span style="color:#00d4ff; font-weight:700;">{s.get('audience_match_score',0)}</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.78rem;">
                    <span style="color:#6b7f96;">Sponsorship Ready</span>
                    <span style="color:#00ff9d; font-weight:700;">{s.get('sponsorship_readiness_score',0)}</span>
                </div>
            </div>
        </div>
        """), unsafe_allow_html=True)

    with col_sub:
        st.markdown(textwrap.dedent(f"""
        <div class="card" style="height:100%; border-left:3px solid {score_color};">
            <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.1em;
                text-transform:uppercase; color:{score_color}; margin-bottom:0.9rem;">
                🧠 AI MATCH EXPLANATION
            </div>
            <div style="color:#e8f0fe; font-size:0.92rem; line-height:1.7;">
                {ai.get('match_explanation', 'No analysis available.')}
            </div>
        </div>
        """), unsafe_allow_html=True)

    # ── SECTION 2 — AUDIENCE PERSONA ─────────────────────────────────────────
    st.markdown('<div class="sec-head">🧬 Audience Persona</div>', unsafe_allow_html=True)

    col_p, col_q = st.columns(2)
    with col_p:
        st.markdown(textwrap.dedent(f"""
        <div class="card" style="border-left:3px solid #8b5cf6;">
            <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.1em;
                text-transform:uppercase; color:#8b5cf6; margin-bottom:0.8rem;">
                👥 Audience Persona
            </div>
            <div style="color:#e8f0fe; font-size:0.9rem; line-height:1.7;">
                {ai.get('audience_persona', 'N/A')}
            </div>
        </div>
        """), unsafe_allow_html=True)

    with col_q:
        # BUG FIX 4: `ai.get("content_themes")` returns a string from groq_analysis,
        # not a list — handle both types safely
        themes_raw = ai.get("content_strategy", "")
        if isinstance(themes_raw, list):
            theme_pills = "".join([
                f'<span class="pill" style="margin:3px;">{t}</span>'
                for t in themes_raw[:8]
            ])
        else:
            theme_pills = (
                f'<div style="font-size:0.88rem; color:#e8f0fe; line-height:1.7;">'
                f'{themes_raw}</div>'
            )

        st.markdown(f"""
        <div class="card" style="border-left:3px solid #00d4ff;">
            <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.1em;
                text-transform:uppercase; color:#00d4ff; margin-bottom:0.9rem;">
                📹 Content Strategy & Themes
            </div>
            <div>{theme_pills}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── SECTION 3 — CHANNEL ANALYTICS ────────────────────────────────────────
    st.markdown('<div class="sec-head">📊 Channel Analytics</div>', unsafe_allow_html=True)

    ca, cb, cc, cd, ce = st.columns(5)
    analytics_tiles = [
        (ca, "Subscribers",     _fmt(ch.get('subscriber_count', 0)), "#4f9eff"),
        (cb, "Avg Views",       _fmt(m.get('avg_views_per_video', 0)), "#00d4ff"),
        (cc, "Engagement Rate", f"{m.get('avg_engagement_rate', 0):.2%}", "#8b5cf6"),
        (cd, "Uploads / Week",  f"{m.get('upload_frequency', 0):.1f}", "#00ff9d"),
        (ce, "Shorts Ratio",    f"{m.get('shorts_ratio', 0):.0%}", "#ffbe0b"),
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

    # ── SECTION 4 — GROWTH CHARTS ─────────────────────────────────────────────
    st.markdown('<div class="sec-head">📈 Growth Trends</div>', unsafe_allow_html=True)

    gc1, gc2 = st.columns(2)
    with gc1:
        st.caption("Subscriber Growth — Last 12 Months")
        render_subscriber_growth_chart(m)
    with gc2:
        st.caption("Views Growth — Last 12 Months")
        render_views_growth_chart(m)

    # ── VIDEO ANALYSIS ────────────────────────────────────────────────────────
    st.markdown('<div class="sec-head">🎬 Video Performance</div>', unsafe_allow_html=True)
    render_engagement_chart(videos_data, m)
    render_content_distribution_chart(m, videos_data)

    with st.expander("📋 Full Video Table — Last 50 Videos"):
        if videos_data:
            import pandas as pd
            df = pd.DataFrame(videos_data)
            show = [c for c in ["title", "published_at", "view_count", "like_count",
                                 "comment_count", "is_short", "duration_seconds"]
                    if c in df.columns]
            df_d = df[show].copy()
            df_d.columns = [c.replace("_", " ").title() for c in show]
            st.dataframe(df_d, use_container_width=True)

    # ── SECTION 5 — BRAND SAFETY + SPONSORSHIP READINESS ─────────────────────
    st.markdown('<div class="sec-head">🛡️ Brand Safety & Sponsorship Readiness</div>',
                unsafe_allow_html=True)

    bs_score = s.get("brand_safety_score", 0)
    if   bs_score >= 80: bs_col, bs_label = "#00ff9d", "Low Risk"
    elif bs_score >= 60: bs_col, bs_label = "#ffbe0b", "Moderate Risk"
    else:                bs_col, bs_label = "#ff4d6d", "High Risk"

    sp_score = s.get("sponsorship_readiness_score", 0)
    if   sp_score >= 75: sp_col, sp_label = "#00ff9d", "Highly Ready"
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
                <span class="kv-k">Upload Consistency</span>
                <span class="kv-v">{m.get('upload_frequency', 0):.1f}× / week</span>
            </div>
            <div class="kv">
                <span class="kv-k">Avg Engagement Rate</span>
                <span class="kv-v" style="color:{sp_col};">{m.get('avg_engagement_rate',0):.2%}</span>
            </div>
            <div class="kv">
                <span class="kv-k">Audience Loyalty</span>
                <span class="kv-v">{m.get('audience_loyalty', 0):.0f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── SECTION 6 — SPONSORSHIP RECOMMENDATIONS ───────────────────────────────
    st.markdown('<div class="sec-head">🚀 Sponsorship Recommendations</div>', unsafe_allow_html=True)
    render_sponsorship_cards(rec)

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

    # ── SECTION 7 — AI INSIGHT CARDS ─────────────────────────────────────────
    st.markdown('<div class="sec-head">🧠 AI Insight Cards</div>', unsafe_allow_html=True)

    # BUG FIX 5: insight rendering used undefined `.insight-card` CSS class —
    # now defined in the CSS block above; also fixed color_map key lookup
    if isinstance(ins, list) and len(ins) > 0:
        # Show all insights in rows of 3
        for row_start in range(0, len(ins), 3):
            row = ins[row_start:row_start + 3]
            ins_cols = st.columns(len(row))
            for col, insight in zip(ins_cols, row):
                icon  = insight.get("icon",  insight.get("emoji", "💡"))
                label = insight.get("label", insight.get("type", "Insight").title())
                text  = insight.get("text",  insight.get("content", ""))
                color_map = {
                    "strength": "#00ff9d", "weakness": "#ff4d6d",
                    "opportunity": "#4f9eff", "viral pattern": "#ffbe0b",
                    "monetization opportunity": "#00d4ff",
                    "audience behavior": "#8b5cf6", "campaign fit signal": "#4f9eff",
                }
                # BUG FIX 6: .get() on color_map used wrong key — use label.lower() as fallback
                card_col = color_map.get(
                    insight.get("type", "").lower(),
                    color_map.get(label.lower(), "#4f9eff")
                )
                with col:
                    st.markdown(f"""
                    <div class="insight-card" style="border-top:2px solid {card_col};">
                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.7rem;">
                            <span style="font-size:1.3rem;">{icon}</span>
                            <span style="font-family:'Syne',sans-serif; font-weight:700;
                                font-size:0.75rem; color:{card_col}; text-transform:uppercase;
                                letter-spacing:0.08em;">{label}</span>
                        </div>
                        <div style="color:#e8f0fe; font-size:0.88rem; line-height:1.65;">{text}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        # Fallback to component renderer
        render_insight_cards(ins)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; color:#2e3d50; font-size:0.68rem; letter-spacing:0.05em;">
        ⚡ Creatrix — Creator Intelligence Platform · Powered by Groq + YouTube
    </div>
    """, unsafe_allow_html=True)
