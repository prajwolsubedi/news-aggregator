"""Common utility functions used across the application."""

import json
from typing import Any, Dict, List, Optional


def load_json_file(filepath: str) -> Any:
    """Load JSON file and return parsed data.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Parsed JSON data (dict, list, etc.) or None if file not found
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in {filepath}: {e}")
        return None
    except Exception as e:
        print(f"✗ Error loading {filepath}: {e}")
        return None


def save_json_file(filepath: str, data: Any, indent: int = 2) -> bool:
    """Save data to JSON file.
    
    Args:
        filepath: Path to save JSON file
        data: Data to save (must be JSON serializable)
        indent: JSON indentation level
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"✗ Error saving {filepath}: {e}")
        return False


def get_news_from_json(data: Any) -> List[Dict]:
    """Extract news items from JSON data, handling different formats.
    
    Handles formats:
    - {"news": [...]}
    - {"ranked_news": [...]}
    - [...]
    
    Args:
        data: JSON data (dict or list)
        
    Returns:
        List of news items
    """
    if not data:
        return []
    
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        if "news" in data:
            return data["news"]
        elif "ranked_news" in data:
            return data["ranked_news"]
        else:
            return []
    else:
        return []


def extract_video_id(video_link: str) -> Optional[str]:
    """Extract YouTube video ID from URL.
    
    Args:
        video_link: YouTube URL (full or short)
        
    Returns:
        Video ID or None if not found
    """
    if not video_link:
        return None
    
    # Handle full YouTube URL
    if "youtube.com" in video_link and "v=" in video_link:
        return video_link.split("v=")[1].split("&")[0]
    
    # Handle short YouTube URL
    if "youtu.be/" in video_link:
        return video_link.split("youtu.be/")[1].split("?")[0]
    
    # Assume it's already a video ID if it's 11 characters
    if len(video_link) == 11:
        return video_link
    
    return None
