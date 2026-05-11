import requests
import re
from datetime import datetime
import streamlit as st


def extract_channel_id(url: str, api_key: str) -> str | None:
    """Extract channel ID from various YouTube URL formats."""
    url = url.strip()

    # Handle @handle format
    handle_match = re.search(r'youtube\.com/@([^/?&]+)', url)
    if handle_match:
        handle = handle_match.group(1)
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={"part": "id", "forHandle": handle, "key": api_key}
        )
        data = resp.json()
        items = data.get("items", [])
        if items:
            return items[0]["id"]

    # Handle /channel/ID format
    channel_match = re.search(r'youtube\.com/channel/([^/?&]+)', url)
    if channel_match:
        return channel_match.group(1)

    # Handle /c/name or /user/name format
    custom_match = re.search(r'youtube\.com/(?:c|user)/([^/?&]+)', url)
    if custom_match:
        name = custom_match.group(1)
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={"part": "id", "forUsername": name, "key": api_key}
        )
        data = resp.json()
        items = data.get("items", [])
        if items:
            return items[0]["id"]

    return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_channel_data(channel_url: str, api_key: str) -> dict | None:
    """Fetch comprehensive channel metadata from YouTube API."""
    try:
        channel_id = extract_channel_id(channel_url, api_key)
        if not channel_id:
            return None

        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={
                "part": "snippet,statistics,contentDetails,brandingSettings,topicDetails",
                "id": channel_id,
                "key": api_key
            }
        )
        data = resp.json()
        items = data.get("items", [])
        if not items:
            return None

        item = items[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        branding = item.get("brandingSettings", {}).get("channel", {})
        topics = item.get("topicDetails", {}).get("topicCategories", [])

        # Parse topic categories
        topic_names = []
        for t in topics:
            parts = t.split("/")
            if parts:
                topic_names.append(parts[-1].replace("_", " "))

        return {
            "channel_id": channel_id,
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "country": snippet.get("country", "N/A"),
            "published_at": snippet.get("publishedAt", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "view_count": int(stats.get("viewCount", 0)),
            "keywords": branding.get("keywords", ""),
            "topics": topic_names,
            "uploads_playlist_id": item.get("contentDetails", {})
                                       .get("relatedPlaylists", {})
                                       .get("uploads", ""),
        }
    except Exception as e:
        st.error(f"Channel fetch error: {e}")
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_channel_videos(channel_id: str, api_key: str, max_results: int = 50) -> list[dict]:
    """Fetch latest videos from a channel with full statistics."""
    try:
        # Step 1: Get uploads playlist ID
        ch_resp = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={"part": "contentDetails", "id": channel_id, "key": api_key}
        )
        ch_data = ch_resp.json()
        ch_items = ch_data.get("items", [])
        if not ch_items:
            return []

        playlist_id = ch_items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Step 2: Get video IDs from playlist
        video_ids = []
        next_page_token = None

        while len(video_ids) < max_results:
            params = {
                "part": "contentDetails,snippet",
                "playlistId": playlist_id,
                "maxResults": min(50, max_results - len(video_ids)),
                "key": api_key
            }
            if next_page_token:
                params["pageToken"] = next_page_token

            pl_resp = requests.get(
                "https://www.googleapis.com/youtube/v3/playlistItems",
                params=params
            )
            pl_data = pl_resp.json()
            pl_items = pl_data.get("items", [])

            for item in pl_items:
                vid_id = item.get("contentDetails", {}).get("videoId")
                if vid_id:
                    video_ids.append(vid_id)

            next_page_token = pl_data.get("nextPageToken")
            if not next_page_token:
                break

        if not video_ids:
            return []

        # Step 3: Fetch video statistics in batches of 50
        videos = []
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            vid_resp = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "part": "snippet,statistics,contentDetails",
                    "id": ",".join(batch),
                    "key": api_key
                }
            )
            vid_data = vid_resp.json()

            for item in vid_data.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                content = item.get("contentDetails", {})

                # Parse duration to detect Shorts (≤60s)
                duration_str = content.get("duration", "PT0S")
                duration_seconds = _parse_duration(duration_str)
                is_short = duration_seconds <= 60

                pub_date = snippet.get("publishedAt", "")
                try:
                    pub_dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                    pub_day = pub_dt.strftime("%A")
                except Exception:
                    pub_dt = None
                    pub_day = "Unknown"

                videos.append({
                    "video_id": item["id"],
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", "")[:500],
                    "published_at": pub_date,
                    "published_day": pub_day,
                    "published_dt": pub_dt,
                    "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                    "tags": snippet.get("tags", []),
                    "view_count": int(stats.get("viewCount", 0)),
                    "like_count": int(stats.get("likeCount", 0)),
                    "comment_count": int(stats.get("commentCount", 0)),
                    "duration_seconds": duration_seconds,
                    "is_short": is_short,
                    "title_length": len(snippet.get("title", "")),
                })

        return videos

    except Exception as e:
        st.error(f"Video fetch error: {e}")
        return []


def _parse_duration(duration: str) -> int:
    """Parse ISO 8601 duration (e.g. PT4M13S) to seconds."""
    pattern = re.compile(
        r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    )
    match = pattern.match(duration)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds
