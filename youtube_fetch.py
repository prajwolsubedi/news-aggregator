import os
import json
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

youtube = build(
    "youtube",
    "v3",
    developerKey=os.getenv("YOUTUBE_API_KEY")
)

def fetch_latest_videos(username: str):
    """
    Fetch latest videos from a YouTube channel using username/handle.
    
    Args:
        username: Channel username/handle (e.g., "google" or "@google")
    """
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    
    # Remove @ if present
    username_clean = username.lstrip("@")
    
    # Search for the channel by username/handle (works for all channels)
    search_response = youtube.search().list(
        part="snippet",
        q=username_clean,
        type="channel",
        maxResults=1
    ).execute()
    
    if not search_response.get("items"):
        raise ValueError(f"Channel not found for username/handle: {username}")
    
    channel_id = search_response["items"][0]["id"]["channelId"]

    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        order="date",
        publishedAfter=since.isoformat(),
        type="video",
        maxResults=50
    )

    response = request.execute()

    videos = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        videos.append({
            "title": item["snippet"]["title"],
            "published_at": item["snippet"]["publishedAt"],
            "video_id": video_id,
            "video_link": f"https://www.youtube.com/watch?v={video_id}",
            "summary": None  # Will be populated later with transcription/summary
        })

    return videos

def fetch_videos_from_channels(channel_names: list):
    """
    Fetch latest videos from multiple YouTube channels and save to JSON.
    
    Args:
        channel_names: List of channel usernames/handles
    """
    all_videos = []
    
    for channel_name in channel_names:
        try:
            videos = fetch_latest_videos(channel_name)
            # Add channel name to each video
            for video in videos:
                video["channel_name"] = channel_name
            all_videos.extend(videos)
            print(f"✓ Found {len(videos)} video(s) from {channel_name}")
        except Exception as e:
            print(f"✗ Error fetching from {channel_name}: {e}")
    
    return all_videos

if __name__ == "__main__":
    # List of channel names/handles to fetch videos from
    channels = [
        "@matthew_berman",
        "@aiDotEngineer",
        "@aiadvantage",
        "@aiexplained-official",
        "@mreflow",
        "@Fireship",
        "@IshanSharma7390",
        "@OpenAI",
        "@anthropic-ai",
        "@google"
    ]
    
    print("\n" + "="*50)
    print("FETCHING VIDEOS FROM CHANNELS")
    print("="*50)
    print(f"Channels: {len(channels)}\n")
    
    try:
        all_videos = fetch_videos_from_channels(channels)
        
        # Save to JSON file
        with open("youtube_videos.json", "w", encoding="utf-8") as f:
            json.dump(all_videos, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        print(f"Total videos found: {len(all_videos)}")
        print(f"✓ Saved to: youtube_videos.json")
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}")
