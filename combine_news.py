import json
import re
import hashlib
from check_rss import fetch_rss_news
from youtube_fetch import fetch_videos_from_channels

def generate_news_id(title: str, source_link: str) -> str:
    """
    Generate a unique ID for website news based on title and source link.
    
    Args:
        title: News title
        source_link: Source URL
    
    Returns:
        str: Unique hash-based ID
    """
    # Create a unique identifier from title and source link
    unique_string = f"{title}|{source_link}"
    return hashlib.md5(unique_string.encode('utf-8')).hexdigest()[:12]

def combine_news():
    """
    Combine news from RSS feed and YouTube channels.
    Adds 'source' field: 'website' for RSS, 'youtube' for YouTube videos.
    Adds 'news_id' for website news and uses 'video_id' for YouTube videos.
    Adds sequential 'id' field (1, 2, 3, ...) to each news item.
    """
    print("\n" + "="*50)
    print("COMBINING NEWS FROM ALL SOURCES")
    print("="*50)
    
    # Fetch RSS news
    print("\n📰 Fetching RSS news...")
    rss_news = fetch_rss_news()
    
    # Add source field and news_id to RSS news
    for news in rss_news:
        news["source"] = "website"
        # Generate unique ID for website news
        if "news_id" not in news:
            news["news_id"] = generate_news_id(news.get("title", ""), news.get("source_link", ""))
    
    print(f"✓ Found {len(rss_news)} news from website")
    
    # Fetch YouTube videos
    print("\n📺 Fetching YouTube videos...")
    from config import YOUTUBE_CHANNELS
    youtube_videos = fetch_videos_from_channels(YOUTUBE_CHANNELS)
    
    # Add source field to YouTube videos (video_id already exists)
    for video in youtube_videos:
        video["source"] = "youtube"
        # video_id already exists, which serves as the ID
    
    print(f"✓ Found {len(youtube_videos)} videos from YouTube")
    
    # Combine all news
    all_combined = rss_news + youtube_videos
    
    # Add sequential ID to each news item (1, 2, 3, ...)
    for idx, item in enumerate(all_combined, start=1):
        item["id"] = idx
    
    # Create structure with metadata
    combined_data = {
        "metadata": {
            "total_news": len(all_combined),
            "website_count": len(rss_news),
            "youtube_count": len(youtube_videos)
        },
        "news": all_combined
    }
    
    # Save to JSON file
    from utils import save_json_file
    save_json_file("combined_news.json", combined_data)
    
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Website news: {len(rss_news)}")
    print(f"YouTube videos: {len(youtube_videos)}")
    print(f"Total combined: {len(all_combined)}")
    print(f"✓ Saved to: combined_news.json")
    print("="*50)
    
    return all_combined

def update_video_summary(video_identifier: str, summary: str, json_file: str = "combined_news.json"):
    """
    Update the summary field for a YouTube video in the combined news JSON file.
    
    Args:
        video_identifier: Can be video_id (e.g., "IHwt6UxiKOw") or video_link (full URL)
        summary: The transcription/summary text to add
        json_file: Path to the combined news JSON file (default: "combined_news.json")
    
    Returns:
        bool: True if video was found and updated, False otherwise
    """
    try:
        # Load existing data
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Handle both old format (list) and new format (dict with metadata)
        if isinstance(data, dict) and "news" in data:
            news_items = data["news"]
        else:
            news_items = data
        
        # Extract video_id from identifier (handle both video_id and video_link)
        video_id = None
        if "youtube.com" in video_identifier or "youtu.be" in video_identifier:
            # Extract video_id from URL
            match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', video_identifier)
            if match:
                video_id = match.group(1)
        else:
            # Assume it's already a video_id
            video_id = video_identifier
        
        if not video_id:
            print(f"✗ Could not extract video_id from: {video_identifier}")
            return False
        
        # Find and update the video
        updated = False
        for item in news_items:
            if item.get("source") == "youtube":
                # Check by video_id or video_link
                if item.get("video_id") == video_id or video_id in item.get("video_link", ""):
                    item["summary"] = summary
                    updated = True
                    print(f"✓ Updated summary for video: {item.get('title', 'Unknown')}")
                    break
        
        if not updated:
            print(f"✗ Video not found with identifier: {video_identifier}")
            return False
        
        # Save updated data (preserve structure)
        if isinstance(data, dict) and "news" in data:
            data["news"] = news_items
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(news_items, f, indent=2, ensure_ascii=False)
        
        return True
        
    except FileNotFoundError:
        print(f"✗ File not found: {json_file}")
        return False
    except Exception as e:
        print(f"✗ Error updating summary: {e}")
        return False

def update_multiple_video_summaries(summaries_dict: dict, json_file: str = "combined_news.json"):
    """
    Update summaries for multiple videos at once.
    
    Args:
        summaries_dict: Dictionary mapping video_id or video_link to summary text
                        Example: {"IHwt6UxiKOw": "Summary text", "https://youtube.com/...": "Another summary"}
        json_file: Path to the combined news JSON file
    
    Returns:
        int: Number of videos successfully updated
    """
    updated_count = 0
    for video_identifier, summary in summaries_dict.items():
        if update_video_summary(video_identifier, summary, json_file):
            updated_count += 1
    return updated_count

def get_news_items(json_file: str = "combined_news.json"):
    """
    Helper function to get news items from JSON file, handling both formats.
    
    Args:
        json_file: Path to the combined news JSON file
    
    Returns:
        list: List of news items
    """
    from utils import load_json_file, get_news_from_json
    data = load_json_file(json_file)
    return get_news_from_json(data) if data else []

if __name__ == "__main__":
    try:
        combine_news()
    except Exception as e:
        print(f"Error: {e}")

