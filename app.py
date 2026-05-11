import streamlit as st
import time
from utils.youtube import get_channel_data, get_channel_videos
from utils.metrics import calculate_metrics
from utils.scoring import calculate_scores
from utils.groq_analysis import generate_ai_analysis, generate_ai_insights, generate_sponsorship_recommendations
from components.cards import (
    render_kpi_cards, render_score_cards, render_insight_cards,
    render_brand_safety_card, render_sponsorship_cards
)
from components.charts import (
    render_subscriber_growth_chart, render_views_growth_chart,
    render_engagement_chart, render_content_distribution_chart
)

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Creatrix — Creator Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

:root {
    --bg-primary: #080b14;
    --bg-secondary: #0d1117;
    --bg-card: #0f1520;
    --bg-glass: rgba(15, 21, 32, 0.7);
    --border: rgba(99, 179, 237, 0.08);
    --border-bright: rgba(99, 179, 237, 0.2);
    --accent-blue: #4f9eff;
    --accent-cyan: #00d4ff;
    --accent-purple: #8b5cf6;
    --accent-green: #00ff9d;
    --accent-amber: #ffbe0b;
    --accent-red: #ff4d6d;
    --text-primary: #e8f0fe;
    --text-secondary: #7b8fa6;
    --text-muted: #4a5568;
    --gradient-1: linear-gradient(135deg, #4f9eff 0%, #00d4ff 100%);
    --gradient-2: linear-gradient(135deg, #8b5cf6 0%, #4f9eff 100%);
    --gradient-hero: linear-gradient(135deg, #080b14 0%, #0d1a2e 50%, #080b14 100%);
    --shadow-glow: 0 0 30px rgba(79, 158, 255, 0.15);
    --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.4);
}

* { font-family: 'DM Sans', sans-serif; }

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

[data-testid="stAppViewContainer"] {
    background: var(--bg-primary) !important;
}

[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] > div:first-child {
    background: var(--bg-secondary) !important;
    padding: 1.5rem 1rem !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text-primary) !important;
}

.stTextArea textarea, .stTextInput input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 1px var(--accent-blue) !important;
}

.stMultiSelect > div, .stSelectbox > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

.stSlider > div > div > div {
    background: var(--accent-blue) !important;
}

.stButton > button {
    background: var(--gradient-1) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
    letter-spacing: 0.02em !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(79, 158, 255, 0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(79, 158, 255, 0.45) !important;
}

[data-testid="stTabs"] {
    border-bottom: 1px solid var(--border) !important;
}

[data-testid="stTabs"] button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    border: none !important;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent-blue) !important;
    border-bottom: 2px solid var(--accent-blue) !important;
}

.hero-header {
    background: var(--gradient-hero);
    border-bottom: 1px solid var(--border);
    padding: 2.5rem 3rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
    position: relative;
    overflow: hidden;
}

.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -20%;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(79,158,255,0.06) 0%, transparent 70%);
    pointer-events: none;
}

.hero-header::after {
    content: '';
    position: absolute;
    bottom: -60%;
    right: -10%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(139,92,246,0.06) 0%, transparent 70%);
    pointer-events: none;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #e8f0fe 0%, #4f9eff 50%, #00d4ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -0.02em;
    line-height: 1.1;
}

.hero-sub {
    font-size: 1rem;
    color: var(--text-secondary);
    margin-top: 0.6rem;
    font-weight: 400;
    letter-spacing: 0.01em;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(79, 158, 255, 0.1);
    border: 1px solid rgba(79, 158, 255, 0.25);
    border-radius: 999px;
    padding: 4px 14px;
    font-size: 0.72rem;
    color: var(--accent-blue);
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.sidebar-section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent-blue);
    margin: 1.4rem 0 0.5rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}

.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 2.5rem 0 1.2rem 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.section-header::before {
    content: '';
    display: block;
    width: 4px;
    height: 22px;
    background: var(--gradient-1);
    border-radius: 2px;
}

.glass-card {
    background: var(--bg-glass);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(12px);
    margin-bottom: 1.2rem;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.glass-card:hover {
    border-color: var(--border-bright);
    box-shadow: var(--shadow-glow);
}

.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
}

.stSpinner > div {
    border-top-color: var(--accent-blue) !important;
}

.stExpander {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

.stExpander summary {
    color: var(--text-primary) !important;
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'Syne', sans-serif !important;
}

.empty-state {
    text-align: center;
    padding: 5rem 2rem;
}

.empty-state-icon {
    font-size: 4rem;
    margin-bottom: 1.2rem;
    opacity: 0.6;
}

.empty-state-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.6rem;
}

.empty-state-sub {
    color: var(--text-secondary);
    font-size: 0.95rem;
    max-width: 450px;
    margin: 0 auto;
    line-height: 1.6;
}

.loading-text {
    font-family: 'Syne', sans-serif;
    color: var(--accent-blue);
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}

label, .stMultiSelect span, .stSelectbox span {
    color: var(--text-secondary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
}

.stMarkdown p { color: var(--text-secondary); }

div[data-testid="stDecoration"] { display: none !important; }

footer { display: none !important; }
#MainMenu { display: none !important; }
header { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ─── HERO HEADER ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-badge">⚡ AI-Powered Creator Intelligence</div>
    <div class="hero-title">Creatrix</div>
    <div class="hero-sub">Discover, evaluate, and activate the world's best YouTube creators — powered by AI</div>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:1.5rem;">
        <div style="font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:800;
            background:linear-gradient(135deg,#4f9eff,#00d4ff);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
            ⚡ Creatrix
        </div>
        <div style="font-size:0.72rem; color:#4a5568; letter-spacing:0.08em; text-transform:uppercase; margin-top:2px;">
            Creator Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    # API Keys
    st.markdown('<div class="sidebar-section-label">🔑 API Configuration</div>', unsafe_allow_html=True)
    youtube_api_key = st.text_input("YouTube API Key", type="password", placeholder="AIza...")
    groq_api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")

    # Brand Brief
    st.markdown('<div class="sidebar-section-label">📝 Brand Brief</div>', unsafe_allow_html=True)
    brand_brief = st.text_area(
        "Campaign Description",
        placeholder="Describe the brand, product, campaign, and target outcome...",
        height=110
    )

    # Campaign Goals
    st.markdown('<div class="sidebar-section-label">🎯 Campaign Goals</div>', unsafe_allow_html=True)
    campaign_goals = st.multiselect(
        "Select Goals",
        ["Awareness", "Consideration", "Conversions", "App Installs",
         "Product Launch", "Community Building", "Engagement", "Education", "Brand Recall"],
        default=["Awareness"]
    )

    # Target Audience
    st.markdown('<div class="sidebar-section-label">👥 Target Audience</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        age_min = st.number_input("Age Min", min_value=13, max_value=65, value=18)
    with col2:
        age_max = st.number_input("Age Max", min_value=13, max_value=65, value=35)
    gender = st.selectbox("Gender", ["All", "Male", "Female", "Non-binary"])
    locations = st.text_input("Locations", placeholder="India, US, UK...")
    languages = st.multiselect("Languages", ["English", "Hindi", "Hinglish", "Telugu", "Tamil", "Kannada", "Malayalam"], default=["English"])

    # Creator Genre
    st.markdown('<div class="sidebar-section-label">🎬 Creator Genre</div>', unsafe_allow_html=True)
    creator_genres = st.multiselect(
        "Select Genres",
        ["Tech", "Lifestyle", "Beauty", "Finance", "Gaming", "Productivity",
         "Education", "Fitness", "Travel", "Entertainment", "Business", "AI", "Fashion", "Food"],
        default=["Tech"]
    )

    # Creator Persona
    st.markdown('<div class="sidebar-section-label">🎭 Creator Persona</div>', unsafe_allow_html=True)
    creator_persona = st.selectbox(
        "Archetype",
        ["Educator", "Entertainer", "Thought Leader", "Motivator", "Storyteller",
         "Reviewer", "Trendsetter", "News Analyst", "Comedian", "Premium Luxury", "Relatable Everyday"]
    )

    # Subscriber Count
    st.markdown('<div class="sidebar-section-label">📊 Subscriber Range</div>', unsafe_allow_html=True)
    sub_range = st.slider("Max Subscribers", 0, 2_000_000, 500_000, step=50_000,
                          format="%d")
    st.caption(f"Up to **{sub_range:,}** subscribers")

    # Channel URL
    st.markdown('<div class="sidebar-section-label">🔗 YouTube Channel</div>', unsafe_allow_html=True)
    channel_url = st.text_input("Channel URL", placeholder="https://youtube.com/@channelname")

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    analyze_btn = st.button("⚡ Run Creator Analysis", use_container_width=True)

# ─── CAMPAIGN CONFIG CONTEXT ─────────────────────────────────────────────────
campaign_config = {
    "brand_brief": brand_brief,
    "campaign_goals": campaign_goals,
    "age_range": (age_min, age_max),
    "gender": gender,
    "locations": locations,
    "languages": languages,
    "creator_genres": creator_genres,
    "creator_persona": creator_persona,
    "sub_range": sub_range,
    "channel_url": channel_url
}

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
if not analyze_btn:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">⚡</div>
        <div class="empty-state-title">Creator Intelligence Awaits</div>
        <div class="empty-state-sub">
            Configure your campaign brief in the sidebar, paste a YouTube channel URL,
            and let Creatrix's AI engine surface deep creator intelligence for your brand.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature highlights
    col1, col2, col3 = st.columns(3)
    features = [
        ("🧠", "AI-Powered Analysis", "Deep LLM insights on creator persona, content patterns, and audience psychology"),
        ("📊", "Creator Fit Engine", "Multi-dimensional scoring across brand safety, audience match, and sponsorship readiness"),
        ("🎯", "Campaign Intelligence", "Tailored sponsorship recommendations, CTA styles, and integration strategies"),
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3], features):
        with col:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; padding:2rem 1.5rem;">
                <div style="font-size:2rem; margin-bottom:1rem;">{icon}</div>
                <div style="font-family:'Syne',sans-serif; font-weight:700; font-size:1rem;
                    color:var(--text-primary); margin-bottom:0.6rem;">{title}</div>
                <div style="font-size:0.85rem; color:var(--text-secondary); line-height:1.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

else:
    # ─── VALIDATION ────────────────────────────────────────────────────────
    if not youtube_api_key:
        st.error("⚠️ YouTube API Key is required. Add it in the sidebar.")
        st.stop()
    if not groq_api_key:
        st.error("⚠️ Groq API Key is required. Add it in the sidebar.")
        st.stop()
    if not channel_url:
        st.error("⚠️ Please provide a YouTube channel URL.")
        st.stop()

    # ─── ANALYSIS PIPELINE ─────────────────────────────────────────────────
    progress_bar = st.progress(0)
    status = st.empty()

    with st.spinner(""):
        status.markdown('<div class="loading-text">🔍 Fetching channel data from YouTube API...</div>', unsafe_allow_html=True)
        channel_data = get_channel_data(channel_url, youtube_api_key)
        progress_bar.progress(15)

        if not channel_data:
            st.error("❌ Could not fetch channel data. Check your URL and API key.")
            st.stop()

        status.markdown('<div class="loading-text">📹 Analyzing latest 50 videos...</div>', unsafe_allow_html=True)
        videos_data = get_channel_videos(channel_data["channel_id"], youtube_api_key)
        progress_bar.progress(35)

        status.markdown('<div class="loading-text">📊 Computing engagement metrics...</div>', unsafe_allow_html=True)
        metrics = calculate_metrics(channel_data, videos_data)
        progress_bar.progress(55)

        status.markdown('<div class="loading-text">⚡ Calculating AI creator scores...</div>', unsafe_allow_html=True)
        scores = calculate_scores(metrics, campaign_config)
        progress_bar.progress(70)

        status.markdown('<div class="loading-text">🧠 Generating Groq AI intelligence report...</div>', unsafe_allow_html=True)
        ai_analysis = generate_ai_analysis(channel_data, metrics, scores, campaign_config, groq_api_key)
        progress_bar.progress(85)

        status.markdown('<div class="loading-text">💡 Surfacing AI insights and recommendations...</div>', unsafe_allow_html=True)
        ai_insights = generate_ai_insights(channel_data, metrics, videos_data, groq_api_key)
        sponsorship_recs = generate_sponsorship_recommendations(channel_data, metrics, scores, campaign_config, groq_api_key)
        progress_bar.progress(100)

    status.empty()
    progress_bar.empty()

    # ─── CHANNEL META BANNER ────────────────────────────────────────────────
    ch = channel_data
    st.markdown(f"""
    <div class="glass-card" style="display:flex; align-items:center; gap:1.5rem; padding:1.5rem 2rem;">
        <img src="{ch.get('thumbnail','')}" style="width:72px;height:72px;border-radius:50%;
            border:2px solid rgba(79,158,255,0.4);object-fit:cover;" onerror="this.style.display='none'"/>
        <div style="flex:1;">
            <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;
                color:var(--text-primary);">{ch.get('title','Channel')}</div>
            <div style="color:var(--text-secondary);font-size:0.85rem;margin-top:3px;">
                {ch.get('description','')[:120]}{'...' if len(ch.get('description','')) > 120 else ''}
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;
                background:linear-gradient(135deg,#4f9eff,#00d4ff);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
                {int(ch.get('subscriber_count',0)):,}
            </div>
            <div style="color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;
                letter-spacing:0.08em;">Subscribers</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── TABS ───────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", "🎬 Video Analysis", "🎯 Creator Fit", "🧠 AI Intelligence", "💰 Sponsorship"
    ])

    # TAB 1 — OVERVIEW
    with tab1:
        st.markdown('<div class="section-header">Channel Performance Overview</div>', unsafe_allow_html=True)
        render_kpi_cards(metrics)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-header">Subscriber Growth</div>', unsafe_allow_html=True)
            render_subscriber_growth_chart(metrics)
        with col2:
            st.markdown('<div class="section-header">Views Growth</div>', unsafe_allow_html=True)
            render_views_growth_chart(metrics)

        st.markdown('<div class="section-header">Content Distribution</div>', unsafe_allow_html=True)
        render_content_distribution_chart(metrics, videos_data)

    # TAB 2 — VIDEO ANALYSIS
    with tab2:
        st.markdown('<div class="section-header">Last 50 Videos — Deep Dive</div>', unsafe_allow_html=True)
        render_engagement_chart(videos_data, metrics)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-header">Upload Patterns</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:grid;gap:1rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:0.8rem;border-bottom:1px solid var(--border);">
                        <span style="color:var(--text-secondary);font-size:0.85rem;">Upload Frequency</span>
                        <span style="font-family:'Syne',sans-serif;font-weight:700;color:var(--accent-blue);">
                            {metrics.get('upload_frequency','N/A')} / week
                        </span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:0.8rem;border-bottom:1px solid var(--border);">
                        <span style="color:var(--text-secondary);font-size:0.85rem;">Shorts Ratio</span>
                        <span style="font-family:'Syne',sans-serif;font-weight:700;color:var(--accent-purple);">
                            {metrics.get('shorts_ratio',0):.1%}
                        </span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:0.8rem;border-bottom:1px solid var(--border);">
                        <span style="color:var(--text-secondary);font-size:0.85rem;">Avg Title Length</span>
                        <span style="font-family:'Syne',sans-serif;font-weight:700;color:var(--accent-cyan);">
                            {metrics.get('avg_title_length',0):.0f} chars
                        </span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="color:var(--text-secondary);font-size:0.85rem;">Best Upload Day</span>
                        <span style="font-family:'Syne',sans-serif;font-weight:700;color:var(--accent-green);">
                            {metrics.get('best_upload_day','N/A')}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="section-header">Engagement Snapshot</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:grid;gap:1rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:0.8rem;border-bottom:1px solid var(--border);">
                        <span style="color:var(--text-secondary);font-size:0.85rem;">Avg Views / Video</span>
                        <span style="font-family:'Syne',sans-serif;font-weight:700;color:var(--accent-blue);">
                            {metrics.get('avg_views_per_video',0):,.0f}
                        </span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:0.8rem;border-bottom:1px solid var(--border);">
                        <span style="color:var(--text-secondary);font-size:0.85rem;">Avg Comments</span>
                        <span style="font-family:'Syne',sans-serif;font-weight:700;color:var(--accent-purple);">
                            {metrics.get('avg_comments',0):,.0f}
                        </span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:0.8rem;border-bottom:1px solid var(--border);">
                        <span style="color:var(--text-secondary);font-size:0.85rem;">Avg Likes</span>
                        <span style="font-family:'Syne',sans-serif;font-weight:700;color:var(--accent-cyan);">
                            {metrics.get('avg_likes',0):,.0f}
                        </span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="color:var(--text-secondary);font-size:0.85rem;">Engagement Rate</span>
                        <span style="font-family:'Syne',sans-serif;font-weight:700;color:var(--accent-green);">
                            {metrics.get('avg_engagement_rate',0):.2%}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("📋 Video Performance Table — Last 50 Videos"):
            if videos_data:
                import pandas as pd
                df = pd.DataFrame(videos_data)
                display_cols = [c for c in ["title", "published_at", "view_count", "like_count",
                                             "comment_count", "is_short"] if c in df.columns]
                if display_cols:
                    df_display = df[display_cols].copy()
                    df_display.columns = [c.replace("_", " ").title() for c in display_cols]
                    st.dataframe(df_display, use_container_width=True)

    # TAB 3 — CREATOR FIT
    with tab3:
        st.markdown('<div class="section-header">Creator Fit Intelligence</div>', unsafe_allow_html=True)
        render_score_cards(scores)

        st.markdown('<div class="section-header">Brand Safety Analysis</div>', unsafe_allow_html=True)
        render_brand_safety_card(scores, metrics)

        st.markdown('<div class="section-header">AI Match Explanation</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="glass-card" style="border-left:3px solid var(--accent-blue);">
            <div style="font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;
                letter-spacing:0.1em;text-transform:uppercase;color:var(--accent-blue);margin-bottom:1rem;">
                🧠 Groq AI — Why This Creator Matches
            </div>
            <div style="color:var(--text-primary);font-size:0.95rem;line-height:1.75;">
                {ai_analysis.get('match_explanation','Analysis not available.')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # TAB 4 — AI INTELLIGENCE
    with tab4:
        st.markdown('<div class="section-header">AI Insight Cards</div>', unsafe_allow_html=True)
        render_insight_cards(ai_insights)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-header">Audience Persona</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-size:0.7rem;font-family:'Syne',sans-serif;font-weight:700;
                    letter-spacing:0.1em;text-transform:uppercase;color:var(--accent-purple);margin-bottom:0.8rem;">
                    👥 Audience Intelligence
                </div>
                <div style="color:var(--text-primary);font-size:0.9rem;line-height:1.7;">
                    {ai_analysis.get('audience_persona','Audience data not available.')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="section-header">Content Strategy</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-size:0.7rem;font-family:'Syne',sans-serif;font-weight:700;
                    letter-spacing:0.1em;text-transform:uppercase;color:var(--accent-cyan);margin-bottom:0.8rem;">
                    📹 Content Intelligence
                </div>
                <div style="color:var(--text-primary);font-size:0.9rem;line-height:1.7;">
                    {ai_analysis.get('content_strategy','Content data not available.')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # TAB 5 — SPONSORSHIP
    with tab5:
        st.markdown('<div class="section-header">Sponsorship Intelligence</div>', unsafe_allow_html=True)
        render_sponsorship_cards(sponsorship_recs)

        st.markdown('<div class="section-header">Campaign Talking Points</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="glass-card" style="border-left:3px solid var(--accent-green);">
            <div style="font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;
                letter-spacing:0.1em;text-transform:uppercase;color:var(--accent-green);margin-bottom:1rem;">
                💰 AI-Generated Sponsorship Brief
            </div>
            <div style="color:var(--text-primary);font-size:0.95rem;line-height:1.75;white-space:pre-line;">
                {sponsorship_recs.get('talking_points','Recommendations not available.')}
            </div>
        </div>
        """, unsafe_allow_html=True)
