import json
import re
import hashlib

from news.check_rss import fetch_rss_news
from news.youtube_fetch import fetch_videos_from_channels
from core.utils import save_json_file, load_json_file, get_news_from_json


def generate_news_id(title: str, source_link: str) -> str:
    """Generate a unique ID for website news based on title and source link."""
    unique_string = f"{title}|{source_link}"
    return hashlib.md5(unique_string.encode("utf-8")).hexdigest()[:12]


def combine_news():
    """Combine news from RSS feed and YouTube channels."""
    print("\n" + "=" * 50)
    print("COMBINING NEWS FROM ALL SOURCES")
    print("=" * 50)

    # Fetch RSS news
    print("\n📰 Fetching RSS news...")
    rss_news = fetch_rss_news()

    # Add source field and news_id to RSS news
    for news in rss_news:
        news["source"] = "website"
        if "news_id" not in news:
            news["news_id"] = generate_news_id(news.get("title", ""), news.get("source_link", ""))

    print(f"✓ Found {len(rss_news)} news from website")

    # Fetch YouTube videos
    print("\n📺 Fetching YouTube videos...")
    from config import YOUTUBE_CHANNELS
    youtube_videos = fetch_videos_from_channels(YOUTUBE_CHANNELS)

    for video in youtube_videos:
        video["source"] = "youtube"

    print(f"✓ Found {len(youtube_videos)} videos from YouTube")

    # Combine all news
    all_combined = rss_news + youtube_videos

    # Add sequential ID
    for idx, item in enumerate(all_combined, start=1):
        item["id"] = idx

    combined_data = {
        "metadata": {
            "total_news": len(all_combined),
            "website_count": len(rss_news),
            "youtube_count": len(youtube_videos),
        },
        "news": all_combined,
    }

    save_json_file("combined_news.json", combined_data)

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Website news: {len(rss_news)}")
    print(f"YouTube videos: {len(youtube_videos)}")
    print(f"Total combined: {len(all_combined)}")
    print("✓ Saved to: combined_news.json")
    print("=" * 50)

    return all_combined


def get_news_items(json_file: str = "combined_news.json"):
    """Helper to get news items from combined JSON."""
    data = load_json_file(json_file)
    return get_news_from_json(data) if data else []


if __name__ == "__main__":
    try:
        combine_news()
    except Exception as e:
        print(f"Error: {e}")
