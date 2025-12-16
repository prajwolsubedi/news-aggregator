#!/usr/bin/env python3
"""
Hybrid YouTube transcription that tries multiple methods:
1. Direct YouTube API (youtube-transcript-api) - works for new videos
2. SerpAPI - more reliable for older videos, provides additional features

This ensures maximum compatibility with both new and old videos.
"""
import argparse
import sys
import os
from dotenv import load_dotenv

load_dotenv()


def try_direct_method(video_id, language='en'):
    """Try youtube-transcript-api first (works for new videos)"""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
        
        print("   🔄 Method 1: Trying direct YouTube API...")
        
        transcript_data = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=[language, 'en']
        )
        
        transcript_text = " ".join(item['text'] for item in transcript_data)
        word_count = len(transcript_text.split())
        
        print(f"   ✅ Success with direct method!")
        print(f"      Words: {word_count}, Segments: {len(transcript_data)}")
        
        return transcript_text, None
        
    except ImportError:
        return None, "youtube-transcript-api not installed (pip install youtube-transcript-api)"
    except TranscriptsDisabled:
        return None, "Transcripts disabled by creator"
    except NoTranscriptFound:
        return None, "No transcript found"
    except VideoUnavailable:
        return None, "Video unavailable"
    except Exception as e:
        return None, str(e)


def try_serpapi_method(video_id):
    """Try SerpAPI method (more reliable for older videos)"""
    try:
        import requests
        
        serp_api_key = os.getenv("SERP_API_KEY")
        if not serp_api_key:
            return None, "SERP_API_KEY not found"
        
        print("   🔄 Method 2: Trying SerpAPI...")
        
        params = {
            "api_key": serp_api_key,
            "engine": "youtube_video_transcript",
            "v": video_id,
        }
        
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            return None, data["error"]
        
        transcript_items = data.get("transcript", [])
        if not transcript_items:
            # Try with type="asr"
            params["type"] = "asr"
            response = requests.get("https://serpapi.com/search", params=params)
            data = response.json()
            transcript_items = data.get("transcript", [])
        
        if not transcript_items:
            return None, "No transcript found via SerpAPI"
        
        transcript_text = " ".join(item.get("snippet", "") for item in transcript_items)
        word_count = len(transcript_text.split())
        
        print(f"   ✅ Success with SerpAPI!")
        print(f"      Words: {word_count}, Segments: {len(transcript_items)}")
        
        return transcript_text, None
        
    except Exception as e:
        return None, str(e)


def transcribe_youtube_video(video_id: str, language='en', prefer_serpapi=False):
    """
    Transcribe a YouTube video using the best available method.
    
    Args:
        video_id: YouTube video ID
        language: Language code (default: 'en')
        prefer_serpapi: Try SerpAPI first instead of direct method
    
    Returns:
        tuple: (transcript_text, method_used, error_message)
    """
    print(f"\n   📝 Transcribing video: {video_id}")
    print(f"   🔗 https://www.youtube.com/watch?v={video_id}\n")
    
    methods = [
        ("Direct YouTube API", try_direct_method),
        ("SerpAPI", try_serpapi_method)
    ]
    
    # Reverse order if SerpAPI is preferred
    if prefer_serpapi:
        methods.reverse()
    
    errors = []
    
    for method_name, method_func in methods:
        if method_func == try_direct_method:
            transcript, error = method_func(video_id, language)
        else:
            transcript, error = method_func(video_id)
        
        if transcript:
            return transcript, method_name, None
        else:
            errors.append(f"{method_name}: {error}")
            print(f"   ❌ {method_name} failed: {error}")
    
    # Both methods failed
    combined_error = "\n   ".join(errors)
    return None, None, f"All methods failed:\n   {combined_error}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transcribe YouTube videos using multiple methods for maximum compatibility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python youtube_transcribe_hybrid.py tHN44yJoeS8
  python youtube_transcribe_hybrid.py tHN44yJoeS8 --output transcript.txt
  python youtube_transcribe_hybrid.py tHN44yJoeS8 --prefer-serpapi
  python youtube_transcribe_hybrid.py https://youtube.com/watch?v=tHN44yJoeS8
  
This script tries multiple methods to get transcripts:
1. Direct YouTube API (youtube-transcript-api) - works for very new videos
2. SerpAPI - more robust for older videos, requires API key

Install requirements:
  pip install youtube-transcript-api requests python-dotenv
        """
    )
    parser.add_argument(
        "video_id",
        nargs="?",
        help="YouTube video ID or URL"
    )
    parser.add_argument(
        "--video-id",
        dest="video_id_flag",
        help="YouTube video ID (alternative)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Save transcript to a file"
    )
    parser.add_argument(
        "--language",
        "-l",
        default="en",
        help="Language code for direct method (default: en)"
    )
    parser.add_argument(
        "--prefer-serpapi",
        action="store_true",
        help="Try SerpAPI method first instead of direct method"
    )
    
    args = parser.parse_args()
    
    # Get video_id
    video_id = args.video_id or args.video_id_flag
    
    if not video_id:
        parser.error("Video ID is required")
    
    # Extract video ID from URL if provided
    if "youtube.com" in video_id or "youtu.be" in video_id:
        if "v=" in video_id:
            video_id = video_id.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_id:
            video_id = video_id.split("youtu.be/")[1].split("?")[0]
    
    print("="*80)
    
    # Transcribe
    transcript, method_used, error = transcribe_youtube_video(
        video_id,
        language=args.language,
        prefer_serpapi=args.prefer_serpapi
    )
    
    if error:
        print("\n" + "="*80)
        print(f"❌ Transcription failed:\n{error}")
        print("\n💡 TROUBLESHOOTING:")
        print("   • Install youtube-transcript-api: pip install youtube-transcript-api")
        print("   • Add SERP_API_KEY to .env file for SerpAPI support")
        print("   • If video is very new, try again in a few hours")
        print("   • Check if video is accessible on YouTube")
        print("="*80 + "\n")
        sys.exit(1)
    
    print(f"\n   🎉 Successfully transcribed using: {method_used}\n")
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"✅ Transcript saved to: {args.output}")
    else:
        print("="*80)
        print("TRANSCRIPT:")
        print("="*80)
        print(transcript)
        print("="*80)
    
    print()