import requests
import os
from dotenv import load_dotenv
import argparse
import sys

load_dotenv()


def transcribe_youtube_video(video_id: str):
    """
    Transcribe a YouTube video using SerpAPI.
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        tuple: (transcript_text, error_message) or (None, error_message) if failed
    """
    try:
        print(f"   📝 Transcribing video {video_id}...")
        
        serp_api_key = os.getenv("SERP_API_KEY")
        if not serp_api_key:
            raise Exception("SERP_API_KEY not found in environment variables")
        
        params = {
            "api_key": serp_api_key,
            "engine": "youtube_video_transcript",
            "v": video_id,
            # "type": "asr"
        }
        
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        
        data = response.json()
        transcript_items = data.get("transcript", [])
        
        if not transcript_items:
            raise Exception("No transcript found for this video")
        
        whole_transcript = " ".join(item.get("snippet", "") for item in transcript_items)
        
        if not whole_transcript.strip():
            raise Exception("Transcript is empty")
        
        print(f"   ✓ Transcript retrieved ({len(whole_transcript)} characters, {len(whole_transcript.split())} words)")
        return whole_transcript, None
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ✗ Transcription failed: {error_msg}")
        return None, error_msg


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transcribe a YouTube video by video ID",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python youtube_transcribe.py dQw4w9WgXcQ
  python youtube_transcribe.py --video-id dQw4w9WgXcQ
  python youtube_transcribe.py --video-id dQw4w9WgXcQ --output transcript.txt
        """
    )
    parser.add_argument(
        "video_id",
        nargs="?",
        help="YouTube video ID (e.g., 'dQw4w9WgXcQ' from URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
    )
    parser.add_argument(
        "--video-id",
        dest="video_id_flag",
        help="YouTube video ID (alternative to positional argument)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Optional: Save transcript to a file (default: print to stdout)"
    )
    
    args = parser.parse_args()
    
    # Get video_id from either positional argument or --video-id flag
    video_id = args.video_id or args.video_id_flag
    
    if not video_id:
        parser.error("Video ID is required. Provide it as a positional argument or use --video-id")
    
    # Extract video ID from full URL if provided
    if "youtube.com" in video_id or "youtu.be" in video_id:
        if "v=" in video_id:
            video_id = video_id.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_id:
            video_id = video_id.split("youtu.be/")[1].split("?")[0]
    
    # Transcribe the video
    transcript, error = transcribe_youtube_video(video_id)
    
    if error:
        print(f"\n❌ Error: {error}")
        sys.exit(1)
    
    if transcript:
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(transcript)
            print(f"\n✓ Transcript saved to: {args.output}")
        else:
            print("\n" + "="*80)
            print("TRANSCRIPT:")
            print("="*80)
            print(transcript)
            print("="*80)
    else:
        print("\n❌ Failed to retrieve transcript")
        sys.exit(1)
