import streamlit as st
from utils.youtube import get_channel_data, get_channel_videos
from utils.metrics import calculate_metrics
from utils.scoring import calculate_scores
from utils.groq_analysis import (
    generate_ai_analysis, generate_ai_insights,
    generate_sponsorship_recommendations
)
from components.cards import (
    render_kpi_cards, render_score_cards, render_insight_cards,
    render_brand_safety_card, render_sponsorship_cards
)
from components.charts import (
    render_subscriber_growth_chart, render_views_growth_chart,
    render_engagement_chart, render_content_distribution_chart
)

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Creatrix — Creator Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── LOAD API KEYS FROM STREAMLIT SECRETS ────────────────────────────────────
try:
    YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
    GROQ_API_KEY    = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error(
        "⚠️  API keys not found. "
        "Go to your Streamlit app **Settings → Secrets** and add:\n\n"
        "```\nYOUTUBE_API_KEY = 'AIza...'\nGROQ_API_KEY = 'gsk_...'\n```"
    )
    st.stop()

# ─── GLOBAL CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

:root {
    --bg-primary:   #07090f;
    --bg-secondary: #0b0f1a;
    --bg-card:      #0e1420;
    --bg-glass:     rgba(14,20,32,0.75);
    --border:       rgba(79,158,255,0.07);
    --border-hi:    rgba(79,158,255,0.22);
    --blue:   #4f9eff;
    --cyan:   #00d4ff;
    --purple: #8b5cf6;
    --green:  #00ff9d;
    --amber:  #ffbe0b;
    --red:    #ff4d6d;
    --t1: #e8f0fe;
    --t2: #6b7f96;
    --t3: #3a4a5c;
    --grad1: linear-gradient(135deg,#4f9eff 0%,#00d4ff 100%);
    --grad2: linear-gradient(135deg,#8b5cf6 0%,#4f9eff 100%);
}

* { font-family:'DM Sans',sans-serif; box-sizing:border-box; }
h1,h2,h3,h4,h5,h6 { font-family:'Syne',sans-serif !important; color:var(--t1) !important; }

html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"] {
    background: var(--bg-primary) !important;
    color: var(--t1) !important;
}
[data-testid="stAppViewContainer"]::before {
    content:'';
    position:fixed;inset:0;
    background:
        radial-gradient(ellipse 800px 500px at 15% 5%, rgba(79,158,255,0.04) 0%, transparent 70%),
        radial-gradient(ellipse 600px 500px at 85% 85%, rgba(139,92,246,0.04) 0%, transparent 70%);
    pointer-events:none;z-index:0;
}

[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 1.2rem 1rem !important; }

.stTextArea textarea, .stTextInput input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--t1) !important;
    font-size: 0.87rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 1px rgba(79,158,255,0.4) !important;
}
.stMultiSelect > div > div, .stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--t1) !important;
}
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background: rgba(79,158,255,0.12) !important;
    border: 1px solid rgba(79,158,255,0.28) !important;
    border-radius: 6px !important;
    color: var(--blue) !important;
    font-size: 0.73rem !important;
}
[data-testid="stSlider"] [role="slider"] {
    background: var(--blue) !important;
    border: 2px solid #fff !important;
}

.stButton > button {
    background: var(--grad1) !important;
    border: none !important;
    border-radius: 12px !important;
    color: #fff !important;
    font-family: 'Syne',sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.68rem 1.4rem !important;
    width: 100% !important;
    letter-spacing: 0.03em !important;
    box-shadow: 0 4px 20px rgba(79,158,255,0.26) !important;
    transition: all 0.22s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(79,158,255,0.40) !important;
}

[data-testid="stTabs"] { border-bottom: 1px solid var(--border) !important; }
[data-testid="stTabs"] button {
    font-family: 'Syne',sans-serif !important;
    font-weight: 600 !important;
    color: var(--t2) !important;
    border: none !important;
    font-size: 0.82rem !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--blue) !important;
    border-bottom: 2px solid var(--blue) !important;
    background: transparent !important;
}

[data-testid="stProgress"] > div > div { background: var(--grad1) !important; }

[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: var(--t1) !important; }

label,.stMultiSelect label,.stSelectbox label,
.stTextInput label,.stTextArea label,.stSlider label {
    color: var(--t2) !important;
    font-size: 0.76rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
}

footer,#MainMenu,header,
[data-testid="stDecoration"],
[data-testid="stToolbar"] { display:none !important; }

.glass-card {
    background: var(--bg-glass);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem;
    backdrop-filter: blur(14px);
    margin-bottom: 1rem;
    transition: border-color .22s, box-shadow .22s;
}
.glass-card:hover {
    border-color: var(--border-hi);
    box-shadow: 0 0 26px rgba(79,158,255,0.09);
}

.sec {
    font-family: 'Syne',sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--t1);
    margin: 2rem 0 0.9rem;
    display: flex;
    align-items: center;
    gap: 9px;
}
.sec::before {
    content:'';
    display:block;
    width:3px; height:18px;
    background: var(--grad1);
    border-radius:2px;
    flex-shrink:0;
}

.sb-label {
    font-family:'Syne',sans-serif;
    font-size:0.6rem;
    font-weight:700;
    letter-spacing:0.12em;
    text-transform:uppercase;
    color: var(--blue);
    margin: 1.1rem 0 0.35rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid var(--border);
}

.kv {
    display:flex;justify-content:space-between;align-items:center;
    padding:0.52rem 0;
    border-bottom:1px solid var(--border);
}
.kv:last-child { border-bottom:none; }
.kv-k { color:var(--t2); font-size:0.82rem; }
.kv-v { font-family:'Syne',sans-serif; font-weight:700; font-size:0.86rem; color:var(--t1); }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR — Campaign Configuration Only
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:0.3rem 0 1.2rem;">
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;
            background:linear-gradient(135deg,#4f9eff,#00d4ff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
            letter-spacing:-0.01em;">⚡ Creatrix</div>
        <div style="font-size:0.62rem;color:#3a4a5c;letter-spacing:0.1em;
            text-transform:uppercase;margin-top:2px;">Campaign Configuration</div>
    </div>
    """, unsafe_allow_html=True)

    # Brand Brief
    st.markdown('<div class="sb-label">📝 Brand Brief</div>', unsafe_allow_html=True)
    brand_brief = st.text_area(
        "brief",
        placeholder="e.g. We're launching an AI productivity app targeting Gen Z professionals "
                    "in India. Drive app installs and build brand awareness among students and young founders.",
        height=100,
        label_visibility="collapsed"
    )

    # Campaign Goals
    st.markdown('<div class="sb-label">🎯 Campaign Goals</div>', unsafe_allow_html=True)
    campaign_goals = st.multiselect(
        "goals",
        ["Awareness", "Consideration", "Conversions", "App Installs",
         "Product Launch", "Community Building", "Engagement", "Education", "Brand Recall"],
        default=["Awareness", "App Installs"],
        label_visibility="collapsed"
    )

    # Target Audience
    st.markdown('<div class="sb-label">👤 Target Audience</div>', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca: age_min = st.number_input("Age min", 13, 65, 18)
    with cb: age_max = st.number_input("Age max", 13, 65, 34)
    audience_gender = st.selectbox("gender", ["All Genders","Male","Female","Non-binary"],
                                   label_visibility="collapsed")
    audience_locations = st.text_input("locations", placeholder="India, US, UK …",
                                       label_visibility="collapsed")
    audience_languages = st.multiselect(
        "languages",
        ["English","Hindi","Hinglish","Telugu","Tamil","Kannada","Malayalam"],
        default=["English","Hindi"],
        label_visibility="collapsed"
    )

    # Creator Genre
    st.markdown('<div class="sb-label">🎬 Creator Genre</div>', unsafe_allow_html=True)
    creator_genres = st.multiselect(
        "genre",
        ["Tech","Lifestyle","Beauty","Finance","Gaming","Productivity",
         "Education","Fitness","Travel","Entertainment","Business","AI","Fashion","Food"],
        default=["Tech","AI"],
        label_visibility="collapsed"
    )

    # Creator Demographics
    st.markdown('<div class="sb-label">📊 Creator Demographics</div>', unsafe_allow_html=True)
    cc, cd = st.columns(2)
    with cc: creator_age_min = st.number_input("Creator age min", 13, 65, 18)
    with cd: creator_age_max = st.number_input("Creator age max", 13, 65, 40)
    creator_gender = st.selectbox("creagender", ["Any","Male","Female","Non-binary"],
                                  label_visibility="collapsed")

    # Content Language
    st.markdown('<div class="sb-label">🌐 Content Language</div>', unsafe_allow_html=True)
    content_languages = st.multiselect(
        "clang",
        ["English","Hindi","Hinglish","Telugu","Tamil","Kannada","Malayalam"],
        default=["English"],
        label_visibility="collapsed"
    )

    # Persona
    st.markdown('<div class="sb-label">🎭 Creator Persona / Archetype</div>', unsafe_allow_html=True)
    creator_persona = st.selectbox(
        "persona",
        ["Educator","Entertainer","Thought Leader","Motivator","Storyteller",
         "Reviewer","Trendsetter","News Analyst","Comedian",
         "Premium Luxury","Relatable Everyday"],
        label_visibility="collapsed"
    )

    # Subscriber slider
    st.markdown('<div class="sb-label">📈 Max Subscriber Count</div>', unsafe_allow_html=True)
    sub_max = st.slider("subs", 0, 2_000_000, 500_000,
                        step=25_000, format="%d",
                        label_visibility="collapsed")
    st.markdown(
        f'<div style="font-size:0.73rem;color:var(--t2);margin-top:-0.3rem;">'
        f'Up to <b style="color:#4f9eff;">{sub_max:,}</b> subscribers</div>',
        unsafe_allow_html=True
    )
    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  MAIN PANEL
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<div style="padding:1.8rem 0 0.6rem;">
    <div style="display:inline-block;background:rgba(79,158,255,0.09);
        border:1px solid rgba(79,158,255,0.2);border-radius:999px;
        padding:3px 13px;font-size:0.65rem;color:#4f9eff;
        font-family:'Syne',sans-serif;font-weight:700;letter-spacing:0.1em;
        text-transform:uppercase;margin-bottom:0.8rem;">⚡ AI-Powered Creator Intelligence</div>
    <div style="font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;
        background:linear-gradient(135deg,#e8f0fe 0%,#4f9eff 52%,#00d4ff 100%);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
        letter-spacing:-0.02em;line-height:1.12;margin-bottom:0.4rem;">
        Creator Intelligence Engine
    </div>
    <div style="color:#6b7f96;font-size:0.9rem;max-width:540px;line-height:1.6;">
        Paste a YouTube channel URL, configure your campaign in the sidebar,
        and Creatrix's AI engine surfaces deep creator intelligence instantly.
    </div>
</div>
""", unsafe_allow_html=True)

# Channel URL + Analyze button
col_u, col_b = st.columns([5, 1])
with col_u:
    channel_url = st.text_input(
        "url",
        placeholder="https://youtube.com/@channelhandle   ·   or   /channel/UCxxxxxxxx",
        label_visibility="collapsed"
    )
with col_b:
    analyze_btn = st.button("⚡ Analyze", use_container_width=True)

st.markdown("<hr style='border:none;border-top:1px solid rgba(79,158,255,0.07);margin:1.4rem 0;'>",
            unsafe_allow_html=True)

# Campaign config bundle
campaign_config = {
    "brand_brief":        brand_brief,
    "campaign_goals":     campaign_goals,
    "age_range":          (age_min, age_max),
    "audience_gender":    audience_gender,
    "audience_locations": audience_locations,
    "audience_languages": audience_languages,
    "creator_genres":     creator_genres,
    "creator_age_range":  (creator_age_min, creator_age_max),
    "creator_gender":     creator_gender,
    "content_languages":  content_languages,
    "creator_persona":    creator_persona,
    "sub_max":            sub_max,
}

# ── Empty state ──────────────────────────────────────────────────────
if not analyze_btn:
    c1, c2, c3 = st.columns(3)
    tiles = [
        ("📊", "Deep Channel Analysis",
         "Subscriber & views time-series (last 12M + YoY), 50-video breakdown, "
         "upload cadence, Shorts ratio, title patterns, thumbnail psychology."),
        ("🎯", "Creator Fit Scoring",
         "5-dimensional scoring: Creator Fit, Audience Match, Brand Safety, "
         "Sponsorship Readiness. AI explanation of WHY this creator matches."),
        ("💰", "Sponsorship Intelligence",
         "Ideal sponsor categories, integration styles, CPM estimates, "
         "AI-generated talking points and campaign brief."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3], tiles):
        with col:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;padding:1.8rem 1.2rem;min-height:175px;">
                <div style="font-size:1.8rem;margin-bottom:0.7rem;">{icon}</div>
                <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.9rem;
                    color:var(--t1);margin-bottom:0.45rem;">{title}</div>
                <div style="font-size:0.8rem;color:var(--t2);line-height:1.55;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    st.stop()

# ── Validation ────────────────────────────────────────────────────────
if not channel_url.strip():
    st.error("⚠️  Please paste a YouTube channel URL above.")
    st.stop()


# ═══════════════════════════════════════════════════════════════════
#  ANALYSIS PIPELINE
# ═══════════════════════════════════════════════════════════════════
progress = st.progress(0)
status   = st.empty()

def _step(msg, pct):
    status.markdown(
        f'<div style="font-family:Syne,sans-serif;font-size:0.8rem;'
        f'color:#4f9eff;letter-spacing:0.04em;">{msg}</div>',
        unsafe_allow_html=True
    )
    progress.progress(pct)

_step("🔍  Fetching channel metadata …", 10)
channel_data = get_channel_data(channel_url.strip(), YOUTUBE_API_KEY)
if not channel_data:
    progress.empty(); status.empty()
    st.error("❌  Could not fetch this channel. Check the URL and ensure your YouTube API key has YouTube Data API v3 enabled.")
    st.stop()

_step("📹  Pulling latest 50 videos …", 26)
videos_data = get_channel_videos(channel_data["channel_id"], YOUTUBE_API_KEY)

_step("📊  Computing engagement & cadence metrics …", 44)
metrics = calculate_metrics(channel_data, videos_data)

_step("⚡  Calculating creator fit & brand safety scores …", 58)
scores = calculate_scores(metrics, campaign_config)

_step("🧠  Running Groq LLM — generating match intelligence …", 72)
ai_analysis = generate_ai_analysis(channel_data, metrics, scores, campaign_config, GROQ_API_KEY)

_step("💡  Surfacing AI insight cards …", 86)
ai_insights = generate_ai_insights(channel_data, metrics, videos_data, GROQ_API_KEY)

_step("💰  Building sponsorship recommendations …", 94)
sponsorship_recs = generate_sponsorship_recommendations(
    channel_data, metrics, scores, campaign_config, GROQ_API_KEY
)

progress.progress(100); status.empty(); progress.empty()


# ═══════════════════════════════════════════════════════════════════
#  CHANNEL IDENTITY BANNER
# ═══════════════════════════════════════════════════════════════════
ch = channel_data

def _fmt(n):
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(int(n))

topic_pills = "".join([
    f'<span style="background:rgba(79,158,255,0.09);border:1px solid rgba(79,158,255,0.18);'
    f'border-radius:999px;padding:2px 10px;font-size:0.68rem;color:#4f9eff;'
    f'font-family:Syne,sans-serif;font-weight:600;">{t}</span>'
    for t in ch.get("topics", [])[:4]
])

stat_block = "".join([
    f'<div style="text-align:center;">'
    f'<div style="font-family:Syne,sans-serif;font-size:1.45rem;font-weight:800;color:{c};">{_fmt(v)}</div>'
    f'<div style="font-size:0.62rem;color:#6b7f96;text-transform:uppercase;letter-spacing:0.08em;">{lbl}</div>'
    f'</div>'
    for v, lbl, c in [
        (ch.get("subscriber_count",0), "Subscribers", "#4f9eff"),
        (ch.get("video_count",0),      "Videos",      "#00d4ff"),
        (ch.get("view_count",0),       "Total Views", "#8b5cf6"),
    ]
])

st.markdown(f"""
<div class="glass-card" style="display:flex;align-items:center;gap:1.4rem;
    padding:1.3rem 1.7rem;border-top:2px solid rgba(79,158,255,0.16);">
    <img src="{ch.get('thumbnail','')}"
         style="width:65px;height:65px;border-radius:50%;
                border:2px solid rgba(79,158,255,0.32);object-fit:cover;flex-shrink:0;"
         onerror="this.style.display='none'"/>
    <div style="flex:1;min-width:0;">
        <div style="font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:800;
            color:#e8f0fe;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
            {ch.get('title','Channel')}
        </div>
        <div style="color:#6b7f96;font-size:0.8rem;margin-top:2px;
            overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
            {ch.get('description','')[:120]}{'…' if len(ch.get('description',''))>120 else ''}
        </div>
        <div style="margin-top:7px;display:flex;gap:8px;flex-wrap:wrap;">{topic_pills}</div>
    </div>
    <div style="display:flex;gap:2rem;flex-shrink:0;">{stat_block}</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Channel Overview",
    "🎬 Video Analysis",
    "🎯 Creator Fit",
    "🧠 AI Intelligence",
    "🛡️ Brand Safety",
    "💰 Sponsorship",
])

# ── TAB 1 — CHANNEL OVERVIEW ─────────────────────────────────────────
with tab1:
    st.markdown('<div class="sec">Channel Performance KPIs</div>', unsafe_allow_html=True)
    render_kpi_cards(metrics)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec">Subscriber Growth — Last 12 Months</div>', unsafe_allow_html=True)
        render_subscriber_growth_chart(metrics)
    with c2:
        st.markdown('<div class="sec">Total Views — Last 12 Months</div>', unsafe_allow_html=True)
        render_views_growth_chart(metrics)

    st.markdown('<div class="sec">Content Format Distribution</div>', unsafe_allow_html=True)
    render_content_distribution_chart(metrics, videos_data)

# ── TAB 2 — VIDEO ANALYSIS ────────────────────────────────────────────
with tab2:
    st.markdown('<div class="sec">Last 50 Videos — Views Performance</div>', unsafe_allow_html=True)
    render_engagement_chart(videos_data, metrics)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec">Upload Patterns</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="glass-card">
            <div class="kv"><span class="kv-k">Upload frequency</span>
                <span class="kv-v" style="color:#4f9eff;">{metrics.get('upload_frequency',0):.1f} / week</span></div>
            <div class="kv"><span class="kv-k">Shorts ratio</span>
                <span class="kv-v" style="color:#8b5cf6;">{metrics.get('shorts_ratio',0):.1%}</span></div>
            <div class="kv"><span class="kv-k">Avg title length</span>
                <span class="kv-v" style="color:#00d4ff;">{metrics.get('avg_title_length',0):.0f} chars</span></div>
            <div class="kv"><span class="kv-k">Best upload day</span>
                <span class="kv-v" style="color:#00ff9d;">{metrics.get('best_upload_day','N/A')}</span></div>
            <div class="kv"><span class="kv-k">Avg days between uploads</span>
                <span class="kv-v">{metrics.get('avg_days_between_uploads',0):.1f} days</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="sec">Engagement Snapshot</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="glass-card">
            <div class="kv"><span class="kv-k">Avg views / video</span>
                <span class="kv-v" style="color:#4f9eff;">{metrics.get('avg_views_per_video',0):,.0f}</span></div>
            <div class="kv"><span class="kv-k">Median views</span>
                <span class="kv-v">{metrics.get('median_views',0):,.0f}</span></div>
            <div class="kv"><span class="kv-k">Avg likes</span>
                <span class="kv-v" style="color:#00d4ff;">{metrics.get('avg_likes',0):,.0f}</span></div>
            <div class="kv"><span class="kv-k">Avg comments</span>
                <span class="kv-v" style="color:#8b5cf6;">{metrics.get('avg_comments',0):,.0f}</span></div>
            <div class="kv"><span class="kv-k">Engagement rate</span>
                <span class="kv-v" style="color:#00ff9d;">{metrics.get('avg_engagement_rate',0):.2%}</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sec">AI Content Analysis</div>', unsafe_allow_html=True)
    content_ai = ai_analysis.get("content_strategy", "")
    st.markdown(f"""
    <div class="glass-card" style="border-left:3px solid #00d4ff;">
        <div style="font-family:'Syne',sans-serif;font-size:0.62rem;font-weight:700;
            letter-spacing:0.1em;text-transform:uppercase;color:#00d4ff;margin-bottom:0.8rem;">
            🧠 Title Patterns · Thumbnail Psychology · Content Clusters · Viral Signals
        </div>
        <div style="color:#e8f0fe;font-size:0.88rem;line-height:1.72;">
            {content_ai or 'Analysis not available.'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 Full Video Table — Last 50 Videos"):
        if videos_data:
            import pandas as pd
            df = pd.DataFrame(videos_data)
            show = [c for c in ["title","published_at","view_count","like_count",
                                 "comment_count","is_short","duration_seconds"] if c in df.columns]
            df_d = df[show].copy()
            df_d.columns = [c.replace("_"," ").title() for c in show]
            st.dataframe(df_d, use_container_width=True)

# ── TAB 3 — CREATOR FIT ───────────────────────────────────────────────
with tab3:
    st.markdown('<div class="sec">Creator Fit Scores</div>', unsafe_allow_html=True)
    render_score_cards(scores)

    st.markdown('<div class="sec">Why This Creator Matches Your Campaign</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="glass-card" style="border-left:3px solid #4f9eff;">
        <div style="font-family:'Syne',sans-serif;font-size:0.62rem;font-weight:700;
            letter-spacing:0.1em;text-transform:uppercase;color:#4f9eff;margin-bottom:0.9rem;">
            🧠 Groq AI — Match Explanation
        </div>
        <div style="color:#e8f0fe;font-size:0.9rem;line-height:1.75;">
            {ai_analysis.get('match_explanation','Analysis not available.')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">Audience Persona</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="glass-card" style="border-left:3px solid #8b5cf6;">
        <div style="font-family:'Syne',sans-serif;font-size:0.62rem;font-weight:700;
            letter-spacing:0.1em;text-transform:uppercase;color:#8b5cf6;margin-bottom:0.9rem;">
            👥 Audience Match Score · {scores.get('audience_match_score',0)}/100
        </div>
        <div style="color:#e8f0fe;font-size:0.9rem;line-height:1.75;">
            {ai_analysis.get('audience_persona','Audience data not available.')}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── TAB 4 — AI INTELLIGENCE ───────────────────────────────────────────
with tab4:
    st.markdown('<div class="sec">AI Insight Cards</div>', unsafe_allow_html=True)
    render_insight_cards(ai_insights)

# ── TAB 5 — BRAND SAFETY ──────────────────────────────────────────────
with tab5:
    st.markdown('<div class="sec">Brand Safety Assessment</div>', unsafe_allow_html=True)
    render_brand_safety_card(scores, metrics)

# ── TAB 6 — SPONSORSHIP ───────────────────────────────────────────────
with tab6:
    st.markdown('<div class="sec">Sponsorship Intelligence</div>', unsafe_allow_html=True)
    render_sponsorship_cards(sponsorship_recs)

    st.markdown('<div class="sec">AI-Generated Campaign Brief</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="glass-card" style="border-left:3px solid #00ff9d;">
        <div style="font-family:'Syne',sans-serif;font-size:0.62rem;font-weight:700;
            letter-spacing:0.1em;text-transform:uppercase;color:#00ff9d;margin-bottom:0.9rem;">
            💰 Sponsorship Talking Points
        </div>
        <div style="color:#e8f0fe;font-size:0.9rem;line-height:1.8;white-space:pre-line;">
            {sponsorship_recs.get('talking_points','Recommendations not available.')}
        </div>
    </div>
    """, unsafe_allow_html=True)
