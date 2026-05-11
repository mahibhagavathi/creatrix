import streamlit as st


def render_kpi_cards(metrics: dict):
    """Render the top KPI cards row."""
    subs = metrics.get("subscriber_count", 0)
    avg_views = metrics.get("avg_views_per_video", 0)
    eng_rate = metrics.get("avg_engagement_rate", 0)
    upload_freq = metrics.get("upload_frequency", 0)
    shorts_ratio = metrics.get("shorts_ratio", 0)
    loyalty = metrics.get("audience_loyalty", 0)

    def _fmt_num(n):
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        elif n >= 1_000:
            return f"{n/1_000:.1f}K"
        return str(int(n))

    cards = [
        ("📹", "Avg Views / Video", _fmt_num(avg_views), "#4f9eff"),
        ("💬", "Engagement Rate", f"{eng_rate:.2%}", "#00d4ff"),
        ("📅", "Upload Frequency", f"{upload_freq:.1f}/wk", "#8b5cf6"),
        ("⚡", "Shorts Ratio", f"{shorts_ratio:.0%}", "#ffbe0b"),
        ("❤️", "Audience Loyalty", f"{loyalty:.0f}%", "#00ff9d"),
        ("👥", "Subscribers", _fmt_num(subs), "#ff4d6d"),
    ]

    cols = st.columns(6)
    for col, (icon, label, value, color) in zip(cols, cards):
        with col:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;padding:1.2rem 0.8rem;
                border-top:2px solid {color}20;min-height:110px;">
                <div style="font-size:1.5rem;margin-bottom:0.4rem;">{icon}</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;
                    color:{color};line-height:1;">{value}</div>
                <div style="font-size:0.72rem;color:var(--text-secondary);margin-top:0.4rem;
                    text-transform:uppercase;letter-spacing:0.06em;">{label}</div>
            </div>
            """, unsafe_allow_html=True)


def render_score_cards(scores: dict):
    """Render animated score gauge cards."""
    score_items = [
        ("creator_fit_score", "Creator Fit", "🎯", "#4f9eff"),
        ("audience_match_score", "Audience Match", "👥", "#00d4ff"),
        ("brand_safety_score", "Brand Safety", "🛡️", "#00ff9d"),
        ("sponsorship_readiness_score", "Sponsorship Ready", "💰", "#ffbe0b"),
        ("overall_score", "Overall Score", "⚡", "#8b5cf6"),
    ]

    cols = st.columns(5)
    for col, (key, label, icon, color) in zip(cols, score_items):
        score = scores.get(key, 0)
        # Gauge arc approximation via conic-gradient
        with col:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;padding:1.5rem 1rem;
                border-top:2px solid {color}30;">
                <div style="position:relative;width:90px;height:90px;margin:0 auto 1rem;">
                    <svg viewBox="0 0 100 100" style="width:90px;height:90px;transform:rotate(-90deg)">
                        <circle cx="50" cy="50" r="40" fill="none"
                            stroke="rgba(255,255,255,0.05)" stroke-width="8"/>
                        <circle cx="50" cy="50" r="40" fill="none"
                            stroke="{color}" stroke-width="8"
                            stroke-dasharray="{score * 2.51:.0f} 251"
                            stroke-linecap="round"
                            style="filter:drop-shadow(0 0 6px {color}66)"/>
                    </svg>
                    <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                        font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:800;color:{color};">
                        {score}
                    </div>
                </div>
                <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;
                    color:var(--text-secondary);font-family:'Syne',sans-serif;font-weight:600;">
                    {icon} {label}
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_brand_safety_card(scores: dict, metrics: dict):
    """Render brand safety analysis card."""
    safety_score = scores.get("brand_safety_score", 0)
    safety_label = scores.get("brand_safety_label", "N/A")
    risk_emoji = scores.get("brand_safety_risk", "")

    color_map = {
        "Low Risk": "#00ff9d",
        "Moderate Risk": "#ffbe0b",
        "High Risk": "#ff4d6d"
    }
    color = color_map.get(safety_label, "#4f9eff")

    factors = [
        ("Content Volatility", "Low" if metrics.get("views_cv", 1) < 1 else "Moderate", metrics.get("views_cv", 1) < 1),
        ("Audience Engagement", "Strong" if metrics.get("avg_engagement_rate", 0) > 0.02 else "Weak", metrics.get("avg_engagement_rate", 0) > 0.02),
        ("Upload Consistency", "Consistent" if metrics.get("upload_frequency", 0) > 1 else "Irregular", metrics.get("upload_frequency", 0) > 1),
        ("Content Format", "Balanced" if 0.2 <= metrics.get("shorts_ratio", 0) <= 0.7 else "Skewed", 0.2 <= metrics.get("shorts_ratio", 0) <= 0.7),
    ]

    factors_html = ""
    for factor_name, factor_val, is_good in factors:
        dot_color = "#00ff9d" if is_good else "#ffbe0b"
        factors_html += f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
            padding:0.6rem 0;border-bottom:1px solid var(--border);">
            <span style="color:var(--text-secondary);font-size:0.85rem;">{factor_name}</span>
            <span style="display:flex;align-items:center;gap:6px;font-size:0.85rem;font-weight:600;color:var(--text-primary);">
                <span style="width:8px;height:8px;border-radius:50%;background:{dot_color};
                    display:inline-block;box-shadow:0 0 6px {dot_color}80;"></span>
                {factor_val}
            </span>
        </div>
        """

    st.markdown(f"""
    <div class="glass-card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1.2rem;">
            <div>
                <div style="font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;
                    letter-spacing:0.1em;text-transform:uppercase;color:var(--text-secondary);margin-bottom:6px;">
                    Brand Safety Assessment
                </div>
                <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:{color};">
                    {risk_emoji} {safety_label}
                </div>
            </div>
            <div style="text-align:center;">
                <div style="font-family:'Syne',sans-serif;font-size:2.5rem;font-weight:800;color:{color};">
                    {safety_score}
                </div>
                <div style="font-size:0.7rem;color:var(--text-secondary);text-transform:uppercase;letter-spacing:0.08em;">
                    / 100
                </div>
            </div>
        </div>
        {factors_html}
    </div>
    """, unsafe_allow_html=True)


def render_insight_cards(insights: list):
    """Render AI insight cards in a 2-column grid."""
    if not insights:
        st.warning("No AI insights available.")
        return

    col1, col2 = st.columns(2)
    cols = [col1, col2]

    insight_colors = ["#4f9eff", "#00d4ff", "#8b5cf6", "#ffbe0b", "#00ff9d", "#ff4d6d"]

    for i, insight in enumerate(insights):
        color = insight_colors[i % len(insight_colors)]
        with cols[i % 2]:
            st.markdown(f"""
            <div class="glass-card" style="border-left:3px solid {color};padding:1.2rem 1.5rem;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.6rem;">
                    <span style="font-size:1.3rem;">{insight.get('icon','💡')}</span>
                    <span style="font-family:'Syne',sans-serif;font-size:0.72rem;font-weight:700;
                        letter-spacing:0.1em;text-transform:uppercase;color:{color};">
                        {insight.get('label','Insight')}
                    </span>
                </div>
                <div style="color:var(--text-primary);font-size:0.9rem;line-height:1.6;">
                    {insight.get('text','No data.')}
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_sponsorship_cards(recs: dict):
    """Render sponsorship recommendation cards."""
    col1, col2, col3 = st.columns(3)

    with col1:
        categories = recs.get("ideal_categories", [])
        cats_html = "".join([
            f'<div style="background:rgba(79,158,255,0.1);border:1px solid rgba(79,158,255,0.2);'
            f'border-radius:8px;padding:6px 12px;font-size:0.82rem;color:var(--accent-blue);'
            f'margin-bottom:6px;font-weight:500;">{c}</div>'
            for c in categories
        ])
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;
                letter-spacing:0.1em;text-transform:uppercase;color:var(--accent-blue);margin-bottom:1rem;">
                🏷️ Ideal Sponsor Categories
            </div>
            {cats_html}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        styles = recs.get("integration_styles", [])
        ctas = recs.get("cta_styles", [])
        styles_html = "".join([
            f'<div style="color:var(--text-primary);font-size:0.85rem;padding:0.5rem 0;'
            f'border-bottom:1px solid var(--border);">📌 {s}</div>'
            for s in styles
        ])
        ctas_html = "".join([
            f'<div style="color:var(--accent-green);font-size:0.85rem;padding:0.5rem 0;'
            f'border-bottom:1px solid var(--border);">→ {c}</div>'
            for c in ctas
        ])
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;
                letter-spacing:0.1em;text-transform:uppercase;color:var(--accent-purple);margin-bottom:0.8rem;">
                🎬 Integration Styles
            </div>
            {styles_html}
            <div style="font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;
                letter-spacing:0.1em;text-transform:uppercase;color:var(--accent-green);
                margin:1rem 0 0.8rem;">
                📣 CTA Styles
            </div>
            {ctas_html}
        </div>
        """, unsafe_allow_html=True)

    with col3:
        cpm = recs.get("estimated_cpm_range", "N/A")
        fmt = recs.get("recommended_format", "")
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;
                letter-spacing:0.1em;text-transform:uppercase;color:var(--accent-amber);margin-bottom:1rem;">
                💰 Deal Intelligence
            </div>
            <div style="margin-bottom:1.2rem;">
                <div style="color:var(--text-secondary);font-size:0.78rem;margin-bottom:4px;">Estimated CPM Range</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;
                    color:var(--accent-amber);">{cpm}</div>
            </div>
            <div>
                <div style="font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;
                    letter-spacing:0.1em;text-transform:uppercase;color:var(--text-secondary);margin-bottom:0.6rem;">
                    Recommended Format
                </div>
                <div style="color:var(--text-primary);font-size:0.88rem;line-height:1.6;">{fmt}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
