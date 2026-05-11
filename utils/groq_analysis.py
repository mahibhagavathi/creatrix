import requests
import json
import streamlit as st


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


def _call_groq(prompt: str, api_key: str, max_tokens: int = 800, system: str = None) -> str:
    """Call Groq LLM API and return response text."""
    if not api_key:
        return "Groq API key not configured."

    system_msg = system or (
        "You are Creatrix AI — an elite creator intelligence analyst for premium brand partnerships. "
        "You provide sharp, precise, data-backed insights in a premium SaaS tone. "
        "Be concise, specific, and insightful. No fluff. No generic advice."
    )

    try:
        resp = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            },
            timeout=30
        )
        data = resp.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"].strip()
        elif "error" in data:
            return f"Groq API error: {data['error'].get('message', 'Unknown error')}"
        return "Analysis not available."
    except Exception as e:
        return f"Connection error: {str(e)}"


@st.cache_data(ttl=3600, show_spinner=False)
def generate_ai_analysis(
    channel_data: dict,
    metrics: dict,
    scores: dict,
    campaign_config: dict,
    api_key: str
) -> dict:
    """Generate comprehensive AI analysis using Groq."""

    channel_ctx = f"""
CHANNEL: {channel_data.get('title', 'Unknown')}
Subscribers: {metrics.get('subscriber_count', 0):,}
Total Views: {metrics.get('total_view_count', 0):,}
Avg Views/Video: {metrics.get('avg_views_per_video', 0):,.0f}
Avg Engagement Rate: {metrics.get('avg_engagement_rate', 0):.2%}
Upload Frequency: {metrics.get('upload_frequency', 0):.1f}/week
Shorts Ratio: {metrics.get('shorts_ratio', 0):.1%}
Best Upload Day: {metrics.get('best_upload_day', 'N/A')}
Creator Fit Score: {scores.get('creator_fit_score', 0)}/100
Brand Safety Score: {scores.get('brand_safety_score', 0)}/100
"""

    campaign_ctx = f"""
BRAND BRIEF: {campaign_config.get('brand_brief', 'Not specified')}
GOALS: {', '.join(campaign_config.get('campaign_goals', []))}
CREATOR PERSONA: {campaign_config.get('creator_persona', 'Not specified')}
GENRES: {', '.join(campaign_config.get('creator_genres', []))}
TARGET AGE: {campaign_config.get('age_range', (18, 35))}
"""

    # Match Explanation
    match_prompt = f"""
{channel_ctx}
{campaign_ctx}

Write a 3-paragraph AI creator match explanation for this brand-creator pairing.

Paragraph 1: Why this creator is a strong match for this campaign (specific, data-backed).
Paragraph 2: Audience overlap analysis and niche alignment.
Paragraph 3: Sponsorship naturalness and authenticity assessment.

Be specific. Reference actual metrics. Premium SaaS tone.
"""

    # Audience Persona
    persona_prompt = f"""
{channel_ctx}

Based on this YouTube channel's metrics, describe the likely audience persona in 2 paragraphs:
- Demographics, psychographics, interests, behaviors
- What drives their engagement, what content resonates
Reference the engagement rate of {metrics.get('avg_engagement_rate', 0):.2%} and upload frequency.
Be specific and insightful.
"""

    # Content Strategy
    content_prompt = f"""
{channel_ctx}

Analyze the content strategy of this creator:
- Shorts ratio: {metrics.get('shorts_ratio', 0):.1%}
- Upload frequency: {metrics.get('upload_frequency', 0):.1f}/week
- Best day: {metrics.get('best_upload_day', 'N/A')}
- Avg title length: {metrics.get('avg_title_length', 0):.0f} chars

In 2 paragraphs, explain their content strategy strengths and weaknesses for brand partnerships.
"""

    match_explanation = _call_groq(match_prompt, api_key, max_tokens=600)
    audience_persona = _call_groq(persona_prompt, api_key, max_tokens=400)
    content_strategy = _call_groq(content_prompt, api_key, max_tokens=400)

    return {
        "match_explanation": match_explanation,
        "audience_persona": audience_persona,
        "content_strategy": content_strategy,
    }


@st.cache_data(ttl=3600, show_spinner=False)
def generate_ai_insights(
    channel_data: dict,
    metrics: dict,
    videos_data: list,
    api_key: str
) -> list[dict]:
    """Generate AI insight cards using Groq."""

    channel_ctx = f"""
Channel: {channel_data.get('title', 'Unknown')}
Subscribers: {metrics.get('subscriber_count', 0):,}
Avg Views: {metrics.get('avg_views_per_video', 0):,.0f}
Engagement Rate: {metrics.get('avg_engagement_rate', 0):.2%}
Shorts Ratio: {metrics.get('shorts_ratio', 0):.1%}
Upload Freq: {metrics.get('upload_frequency', 0):.1f}/week
Views CV (volatility): {metrics.get('views_cv', 0):.2f}
Best Upload Day: {metrics.get('best_upload_day', 'N/A')}
"""

    prompt = f"""
{channel_ctx}

Generate exactly 6 AI insight cards for this YouTube creator's brand partnership potential.

Return ONLY valid JSON (no markdown, no explanation), structured as:
[
  {{"icon": "🔥", "label": "Growth Strength", "text": "..."}},
  {{"icon": "⚠️", "label": "Weakness", "text": "..."}},
  {{"icon": "📈", "label": "Viral Pattern", "text": "..."}},
  {{"icon": "💰", "label": "Monetization Opportunity", "text": "..."}},
  {{"icon": "👥", "label": "Audience Behavior", "text": "..."}},
  {{"icon": "🎯", "label": "Campaign Fit Signal", "text": "..."}}
]

Each "text" must be 1-2 sharp, specific sentences. Reference actual metrics. No generic advice.
"""

    raw = _call_groq(prompt, api_key, max_tokens=800)

    # Try to parse JSON
    try:
        # Clean up potential markdown code blocks
        raw_clean = raw.strip()
        if raw_clean.startswith("```"):
            raw_clean = raw_clean.split("```")[1]
            if raw_clean.startswith("json"):
                raw_clean = raw_clean[4:]
        raw_clean = raw_clean.strip()
        insights = json.loads(raw_clean)
        return insights
    except Exception:
        # Fallback insights
        return [
            {"icon": "🔥", "label": "Growth Strength", "text": f"Channel maintains {metrics.get('avg_views_per_video',0):,.0f} average views per video with consistent upload cadence."},
            {"icon": "⚠️", "label": "Weakness", "text": f"Views coefficient of variation at {metrics.get('views_cv',0):.1f} suggests inconsistent viral performance."},
            {"icon": "📈", "label": "Viral Pattern", "text": f"Best performing upload day is {metrics.get('best_upload_day','N/A')}, signaling strong algorithmic timing intelligence."},
            {"icon": "💰", "label": "Monetization Opportunity", "text": f"With {metrics.get('avg_engagement_rate',0):.2%} engagement, this audience shows strong conversion signal for premium brands."},
            {"icon": "👥", "label": "Audience Behavior", "text": f"Shorts ratio of {metrics.get('shorts_ratio',0):.1%} indicates a mixed audience comfortable with both quick and deep content."},
            {"icon": "🎯", "label": "Campaign Fit Signal", "text": "Creator's upload consistency and audience loyalty make them a reliable long-term brand partner."},
        ]


@st.cache_data(ttl=3600, show_spinner=False)
def generate_sponsorship_recommendations(
    channel_data: dict,
    metrics: dict,
    scores: dict,
    campaign_config: dict,
    api_key: str
) -> dict:
    """Generate detailed sponsorship recommendations."""

    channel_ctx = f"""
Channel: {channel_data.get('title', 'Unknown')}
Subscribers: {metrics.get('subscriber_count', 0):,}
Avg Views: {metrics.get('avg_views_per_video', 0):,.0f}
Engagement: {metrics.get('avg_engagement_rate', 0):.2%}
Sponsorship Readiness: {scores.get('sponsorship_readiness_score', 0)}/100
Brand Safety: {scores.get('brand_safety_score', 0)}/100 ({scores.get('brand_safety_label', 'N/A')})
"""

    campaign_ctx = f"""
Brand Brief: {campaign_config.get('brand_brief', 'Not specified')}
Campaign Goals: {', '.join(campaign_config.get('campaign_goals', []))}
Target Audience Age: {campaign_config.get('age_range', (18, 35))}
"""

    # Categories
    categories_prompt = f"""
{channel_ctx}
{campaign_ctx}

Return ONLY valid JSON (no markdown):
{{
  "ideal_categories": ["category1", "category2", "category3", "category4", "category5"],
  "integration_styles": ["style1", "style2", "style3"],
  "cta_styles": ["cta1", "cta2", "cta3"],
  "estimated_cpm_range": "$X - $Y",
  "recommended_format": "..."
}}

ideal_categories: best sponsor product categories for this creator
integration_styles: how the brand should integrate (dedicated video, mid-roll, etc.)
cta_styles: best CTA approaches for this audience
estimated_cpm_range: realistic CPM range based on engagement
recommended_format: 1 sentence on best sponsorship format
"""

    # Talking Points
    talking_prompt = f"""
{channel_ctx}
{campaign_ctx}

Write a comprehensive sponsorship talking points brief in 4 bullet points.
Each bullet point should be specific, actionable, and reference actual channel metrics.
Format: • [Point]
Topics: audience overlap, content authenticity, timing, measurement approach.
"""

    raw_cats = _call_groq(categories_prompt, api_key, max_tokens=500)
    talking_points = _call_groq(talking_prompt, api_key, max_tokens=600)

    try:
        raw_clean = raw_cats.strip()
        if raw_clean.startswith("```"):
            raw_clean = raw_clean.split("```")[1]
            if raw_clean.startswith("json"):
                raw_clean = raw_clean[4:]
        raw_clean = raw_clean.strip()
        cats_data = json.loads(raw_clean)
    except Exception:
        cats_data = {
            "ideal_categories": ["SaaS Tools", "AI Products", "Productivity Apps", "Tech Hardware", "Online Courses"],
            "integration_styles": ["Dedicated Sponsored Video", "Mid-Roll Integration", "End-Card CTA"],
            "cta_styles": ["Link in Description", "Promo Code", "Free Trial Offer"],
            "estimated_cpm_range": "$15 - $45",
            "recommended_format": "Dedicated 60-90 second mid-roll with authentic demo walkthrough."
        }

    return {
        "ideal_categories": cats_data.get("ideal_categories", []),
        "integration_styles": cats_data.get("integration_styles", []),
        "cta_styles": cats_data.get("cta_styles", []),
        "estimated_cpm_range": cats_data.get("estimated_cpm_range", "N/A"),
        "recommended_format": cats_data.get("recommended_format", ""),
        "talking_points": talking_points,
    }
