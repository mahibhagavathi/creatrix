import numpy as np


def calculate_scores(metrics: dict, campaign_config: dict) -> dict:
    """Calculate all creator and campaign fit scores (0–100)."""

    scores = {}

    # ── 1. Creator Fit Score ─────────────────────────────────────────────────
    genre_match = _genre_match_score(campaign_config)
    persona_match = _persona_match_score(metrics, campaign_config)
    sub_fit = _subscriber_fit_score(metrics, campaign_config)

    scores["creator_fit_score"] = int(np.clip(
        (genre_match * 0.4 + persona_match * 0.35 + sub_fit * 0.25), 0, 100
    ))

    # ── 2. Audience Match Score ──────────────────────────────────────────────
    engagement_score = _engagement_to_score(metrics.get("avg_engagement_rate", 0))
    loyalty_score = min(metrics.get("audience_loyalty", 0) * 3, 100)
    consistency_score = _upload_consistency_score(metrics)

    scores["audience_match_score"] = int(np.clip(
        (engagement_score * 0.45 + loyalty_score * 0.35 + consistency_score * 0.20), 0, 100
    ))

    # ── 3. Brand Safety Score ────────────────────────────────────────────────
    brand_safety = _brand_safety_score(metrics)
    scores["brand_safety_score"] = int(np.clip(brand_safety, 0, 100))
    scores["brand_safety_label"] = _brand_safety_label(scores["brand_safety_score"])
    scores["brand_safety_risk"] = _brand_safety_risk(scores["brand_safety_score"])

    # ── 4. Sponsorship Readiness Score ──────────────────────────────────────
    spon_score = _sponsorship_readiness(metrics)
    scores["sponsorship_readiness_score"] = int(np.clip(spon_score, 0, 100))

    # ── 5. Overall Intelligence Score ───────────────────────────────────────
    scores["overall_score"] = int(np.clip(
        scores["creator_fit_score"] * 0.30
        + scores["audience_match_score"] * 0.25
        + scores["brand_safety_score"] * 0.25
        + scores["sponsorship_readiness_score"] * 0.20,
        0, 100
    ))

    # ── 6. Growth Momentum ──────────────────────────────────────────────────
    scores["growth_momentum"] = _growth_momentum(metrics)

    # ── 7. Content Consistency ──────────────────────────────────────────────
    cv = metrics.get("views_cv", 1.0)
    scores["content_consistency"] = int(np.clip(100 - (cv * 40), 10, 100))

    return scores


def _genre_match_score(campaign_config: dict) -> float:
    """Score based on how well creator genres match campaign."""
    goals = campaign_config.get("campaign_goals", [])
    genres = campaign_config.get("creator_genres", [])

    if not genres:
        return 60.0

    # High-value genre-goal combos
    power_combos = {
        ("Tech", "Awareness"): 95,
        ("Tech", "Product Launch"): 90,
        ("Finance", "Conversions"): 88,
        ("AI", "Education"): 92,
        ("Productivity", "App Installs"): 90,
        ("Gaming", "App Installs"): 88,
        ("Beauty", "Conversions"): 86,
        ("Lifestyle", "Brand Recall"): 82,
        ("Education", "Consideration"): 85,
        ("Fitness", "Community Building"): 80,
    }

    scores = []
    for genre in genres:
        for goal in goals:
            scores.append(power_combos.get((genre, goal), 65))

    return np.mean(scores) if scores else 65.0


def _persona_match_score(metrics: dict, campaign_config: dict) -> float:
    """Score based on creator persona matching."""
    persona = campaign_config.get("creator_persona", "")
    goals = campaign_config.get("campaign_goals", [])

    persona_goal_fit = {
        "Educator": {"Education": 95, "Consideration": 88, "Awareness": 80},
        "Thought Leader": {"Awareness": 92, "Consideration": 90, "Brand Recall": 88},
        "Reviewer": {"Conversions": 92, "Consideration": 90, "Product Launch": 88},
        "Entertainer": {"Awareness": 88, "Community Building": 90, "Brand Recall": 85},
        "Motivator": {"Community Building": 90, "Brand Recall": 88, "Engagement": 92},
        "Storyteller": {"Brand Recall": 92, "Engagement": 88, "Awareness": 85},
        "Trendsetter": {"Product Launch": 92, "Awareness": 90, "Fashion": 88},
        "Comedian": {"Engagement": 92, "Awareness": 88, "Community Building": 85},
        "News Analyst": {"Awareness": 90, "Education": 88, "Consideration": 85},
        "Premium Luxury": {"Brand Recall": 90, "Awareness": 88, "Consideration": 85},
        "Relatable Everyday": {"Community Building": 92, "Engagement": 90, "Conversions": 82},
    }

    if persona not in persona_goal_fit:
        return 70.0

    fit_map = persona_goal_fit[persona]
    scores = [fit_map.get(g, 65) for g in goals]
    return np.mean(scores) if scores else 70.0


def _subscriber_fit_score(metrics: dict, campaign_config: dict) -> float:
    """Score based on subscriber count vs campaign range."""
    subs = metrics.get("subscriber_count", 0)
    max_subs = campaign_config.get("sub_range", 2_000_000)

    if subs <= 0:
        return 50.0

    # Perfect fit: within 80% of max
    if subs <= max_subs:
        ratio = subs / max_subs
        if ratio >= 0.1:
            return 85 + (ratio * 15)
        return 60.0
    else:
        # Over-limit penalty
        over_ratio = max_subs / subs
        return max(over_ratio * 100, 30)


def _engagement_to_score(engagement_rate: float) -> float:
    """Convert engagement rate (0-1) to score (0-100)."""
    # Industry benchmarks:
    # < 1% = poor, 1-3% = average, 3-6% = good, > 6% = excellent
    if engagement_rate <= 0:
        return 20.0
    pct = engagement_rate * 100
    if pct >= 6:
        return 95.0
    elif pct >= 3:
        return 75 + ((pct - 3) / 3) * 20
    elif pct >= 1:
        return 40 + ((pct - 1) / 2) * 35
    else:
        return max(pct * 40, 10)


def _upload_consistency_score(metrics: dict) -> float:
    """Score based on upload frequency and consistency."""
    freq = metrics.get("upload_frequency", 0)
    if freq >= 3:
        return 95.0
    elif freq >= 2:
        return 85.0
    elif freq >= 1:
        return 70.0
    elif freq >= 0.5:
        return 50.0
    return 30.0


def _brand_safety_score(metrics: dict) -> float:
    """Calculate brand safety score from content signals."""
    base_score = 85.0

    # Penalize high volatility (unpredictable content)
    cv = metrics.get("views_cv", 0)
    if cv > 2:
        base_score -= 10
    elif cv > 1.5:
        base_score -= 5

    # Penalize very low engagement (bot/dead audience signal)
    eng = metrics.get("avg_engagement_rate", 0)
    if eng < 0.005:
        base_score -= 15
    elif eng < 0.01:
        base_score -= 5

    # Penalize irregular uploads
    freq = metrics.get("upload_frequency", 1)
    if freq < 0.25:
        base_score -= 8

    # Penalize high shorts ratio (unstable audience)
    shorts_ratio = metrics.get("shorts_ratio", 0)
    if shorts_ratio > 0.8:
        base_score -= 7

    return max(base_score, 10)


def _brand_safety_label(score: int) -> str:
    if score >= 80:
        return "Low Risk"
    elif score >= 60:
        return "Moderate Risk"
    return "High Risk"


def _brand_safety_risk(score: int) -> str:
    if score >= 80:
        return "✅"
    elif score >= 60:
        return "⚠️"
    return "🚨"


def _sponsorship_readiness(metrics: dict) -> float:
    """Score sponsorship readiness based on channel maturity."""
    score = 50.0

    subs = metrics.get("subscriber_count", 0)
    avg_views = metrics.get("avg_views_per_video", 0)
    engagement = metrics.get("avg_engagement_rate", 0)
    freq = metrics.get("upload_frequency", 0)

    # Subscriber tier bonus
    if subs >= 500_000:
        score += 20
    elif subs >= 100_000:
        score += 15
    elif subs >= 50_000:
        score += 10
    elif subs >= 10_000:
        score += 5

    # Average views bonus
    if avg_views >= 100_000:
        score += 15
    elif avg_views >= 50_000:
        score += 10
    elif avg_views >= 10_000:
        score += 5

    # Engagement bonus
    if engagement >= 0.04:
        score += 15
    elif engagement >= 0.02:
        score += 8

    # Frequency bonus
    if freq >= 2:
        score += 10
    elif freq >= 1:
        score += 5

    return min(score, 100)


def _growth_momentum(metrics: dict) -> int:
    """Estimate growth momentum from monthly data."""
    monthly = metrics.get("monthly_subscribers", [])
    if len(monthly) < 3:
        return 50

    recent = monthly[-3:]
    older = monthly[-6:-3] if len(monthly) >= 6 else monthly[:3]

    recent_avg = np.mean([m.get("subscribers", 0) for m in recent])
    older_avg = np.mean([m.get("subscribers", 0) for m in older])

    if older_avg == 0:
        return 50

    growth_pct = (recent_avg - older_avg) / older_avg * 100

    if growth_pct >= 20:
        return 95
    elif growth_pct >= 10:
        return 80
    elif growth_pct >= 5:
        return 65
    elif growth_pct >= 0:
        return 50
    return max(30, 50 + int(growth_pct))
