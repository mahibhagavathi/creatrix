import numpy as np
import pandas as pd
from datetime import datetime, timezone
from collections import Counter


def calculate_metrics(channel_data: dict, videos_data: list[dict]) -> dict:
    """Calculate comprehensive metrics from channel and video data."""
    metrics = {}

    if not videos_data:
        return _empty_metrics(channel_data)

    df = pd.DataFrame(videos_data)

    # ── Basic Stats ─────────────────────────────────────────────────────────
    metrics["total_videos_analyzed"] = len(df)
    metrics["avg_views_per_video"] = df["view_count"].mean()
    metrics["median_views"] = df["view_count"].median()
    metrics["max_views"] = df["view_count"].max()
    metrics["min_views"] = df["view_count"].min()
    metrics["avg_likes"] = df["like_count"].mean()
    metrics["avg_comments"] = df["comment_count"].mean()

    # ── Engagement Rate ──────────────────────────────────────────────────────
    subs = channel_data.get("subscriber_count", 1)
    if subs > 0:
        engagement = (df["like_count"] + df["comment_count"]) / df["view_count"].replace(0, np.nan)
        metrics["avg_engagement_rate"] = engagement.mean()
    else:
        metrics["avg_engagement_rate"] = 0.0

    # ── Shorts Analysis ──────────────────────────────────────────────────────
    shorts = df["is_short"].sum()
    metrics["shorts_count"] = int(shorts)
    metrics["longform_count"] = len(df) - int(shorts)
    metrics["shorts_ratio"] = shorts / len(df) if len(df) > 0 else 0

    # ── Title Length ────────────────────────────────────────────────────────
    metrics["avg_title_length"] = df["title_length"].mean()

    # ── Upload Cadence ───────────────────────────────────────────────────────
    df_sorted = df[df["published_dt"].notna()].sort_values("published_dt", ascending=False).copy()

    if len(df_sorted) >= 2:
        dates = df_sorted["published_dt"].tolist()
        gaps_days = []
        for i in range(len(dates) - 1):
            try:
                d1 = dates[i]
                d2 = dates[i + 1]
                if d1.tzinfo and d2.tzinfo:
                    gap = (d1 - d2).days
                elif not d1.tzinfo and not d2.tzinfo:
                    gap = (d1 - d2).days
                else:
                    d1 = d1.replace(tzinfo=None) if d1.tzinfo else d1
                    d2 = d2.replace(tzinfo=None) if d2.tzinfo else d2
                    gap = abs((d1 - d2).days)
                if gap >= 0:
                    gaps_days.append(gap)
            except Exception:
                continue

        if gaps_days:
            avg_gap = np.mean(gaps_days)
            metrics["avg_days_between_uploads"] = round(avg_gap, 1)
            metrics["upload_frequency"] = round(7 / avg_gap, 2) if avg_gap > 0 else 7.0
        else:
            metrics["avg_days_between_uploads"] = 7
            metrics["upload_frequency"] = 1.0
    else:
        metrics["avg_days_between_uploads"] = 7
        metrics["upload_frequency"] = 1.0

    # ── Best Upload Day ──────────────────────────────────────────────────────
    if "published_day" in df.columns:
        day_counts = Counter(df["published_day"].dropna().tolist())
        if day_counts:
            metrics["best_upload_day"] = day_counts.most_common(1)[0][0]
            metrics["upload_day_distribution"] = dict(day_counts)
        else:
            metrics["best_upload_day"] = "N/A"
            metrics["upload_day_distribution"] = {}
    else:
        metrics["best_upload_day"] = "N/A"
        metrics["upload_day_distribution"] = {}

    # ── Views Distribution ───────────────────────────────────────────────────
    metrics["views_std"] = df["view_count"].std()
    metrics["views_cv"] = metrics["views_std"] / metrics["avg_views_per_video"] if metrics["avg_views_per_video"] > 0 else 0

    # ── Growth Simulation (for chart) ───────────────────────────────────────
    metrics["subscriber_count"] = channel_data.get("subscriber_count", 0)
    metrics["total_view_count"] = channel_data.get("view_count", 0)
    metrics["video_count"] = channel_data.get("video_count", 0)

    # Simulate monthly subscriber growth (since YouTube API doesn't give historical data)
    metrics["monthly_subscribers"] = _simulate_monthly_growth(
        channel_data.get("subscriber_count", 0),
        channel_data.get("published_at", ""),
        growth_rate=0.03
    )
    metrics["monthly_views"] = _simulate_monthly_views(
        df, channel_data.get("published_at", "")
    )

    # ── Audience Loyalty Estimate ────────────────────────────────────────────
    # Ratio of avg views to subscriber count
    view_to_sub_ratio = metrics["avg_views_per_video"] / max(subs, 1)
    metrics["audience_loyalty"] = min(view_to_sub_ratio * 100, 100)

    # ── Top Performing Videos ────────────────────────────────────────────────
    top_videos = df.nlargest(5, "view_count")[["title", "view_count", "like_count", "comment_count", "is_short"]].to_dict("records")
    metrics["top_videos"] = top_videos

    # ── Content clusters from titles ─────────────────────────────────────────
    all_titles = " ".join(df["title"].tolist()).lower()
    metrics["title_corpus"] = all_titles

    # ── Video views list for charts ──────────────────────────────────────────
    metrics["video_views_list"] = df["view_count"].tolist()[:50]
    metrics["video_titles_short"] = [t[:30] + "..." if len(t) > 30 else t for t in df["title"].tolist()[:50]]

    return metrics


def _simulate_monthly_growth(current_subs: int, published_at: str, growth_rate: float = 0.03) -> list[dict]:
    """Simulate subscriber growth over 12 months working backwards."""
    months = []
    import calendar

    now = datetime.now()
    subs = current_subs

    for i in range(11, -1, -1):
        month = (now.month - i - 1) % 12 + 1
        year = now.year - ((now.month - i - 1) // 12 + (1 if (now.month - i - 1) < 0 else 0))
        # Decay backwards
        subs_at = int(subs * ((1 - growth_rate) ** i))
        months.append({
            "month": f"{calendar.month_abbr[month]} {str(year)[-2:]}",
            "subscribers": max(subs_at, 0)
        })

    return months


def _simulate_monthly_views(df: pd.DataFrame, published_at: str) -> list[dict]:
    """Aggregate actual video views by month where possible."""
    import calendar

    now = datetime.now()
    monthly = {}

    for i in range(12):
        month = (now.month - i - 1) % 12 + 1
        year = now.year - ((now.month - i - 1) // 12 + (1 if (now.month - i - 1) < 0 else 0))
        key = f"{year}-{month:02d}"
        monthly[key] = {"month": f"{calendar.month_abbr[month]} {str(year)[-2:]}", "views": 0}

    # Add actual data from videos
    for _, row in df.iterrows():
        try:
            if row.get("published_dt"):
                dt = row["published_dt"]
                if hasattr(dt, 'year'):
                    key = f"{dt.year}-{dt.month:02d}"
                    if key in monthly:
                        monthly[key]["views"] += row.get("view_count", 0)
        except Exception:
            continue

    return list(monthly.values())


def _empty_metrics(channel_data: dict) -> dict:
    return {
        "total_videos_analyzed": 0,
        "avg_views_per_video": 0,
        "avg_engagement_rate": 0,
        "shorts_ratio": 0,
        "upload_frequency": 0,
        "avg_title_length": 0,
        "avg_comments": 0,
        "avg_likes": 0,
        "subscriber_count": channel_data.get("subscriber_count", 0),
        "total_view_count": channel_data.get("view_count", 0),
        "best_upload_day": "N/A",
        "audience_loyalty": 0,
        "monthly_subscribers": [],
        "monthly_views": [],
        "top_videos": [],
        "shorts_count": 0,
        "longform_count": 0,
        "video_views_list": [],
        "video_titles_short": [],
        "views_cv": 0,
    }
