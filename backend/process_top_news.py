import json
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

from core.utils import load_json_file, get_news_from_json
from core.database import create_daily_top_news
from transcription.transcription_jobs import create_transcription_job, get_transcript_by_video_id

load_dotenv()

# Initialize Gemini API client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) if os.getenv("GEMINI_API_KEY") else genai.Client()


def load_ranked_news(json_file: str = "ranked_news.json"):
    """Load ranked news from JSON file.

    Expects the JSON file (written by ranking/rank_news.py) to be in the
    server working directory when this script is run.

    This is primarily for standalone runs of this script; the main
    pipeline passes ranked news in-memory instead.
    """
    data = load_json_file(json_file)
    return get_news_from_json(data) if data else []


def load_combined_news(json_file: str = "combined_news.json"):
    """Load combined news from JSON file.

    Expects the JSON file (written by news/combine_news.py) to be in the
    server working directory when this script is run.

    This is primarily for standalone runs of this script; the main
    pipeline passes combined news in-memory instead.
    """
    data = load_json_file(json_file)
    return get_news_from_json(data) if data else []

def get_news_by_id(news_items: list, news_id: int):
    """Get news item by sequential ID."""
    for item in news_items:
        if item.get("id") == news_id:
            return item
    return None

def summarize_with_gemini(transcript: str, model_name: str = "gemini-2.5-flash-lite"):
    """
    Summarize transcript using Google Gemini.
    Only sends 200-400 words of the transcript to keep it concise.
    
    Args:
        transcript: Video transcript text
        model_name: Gemini model to use
    
    Returns:
        str: Summary text or None if failed
    """
    try:
        print(f"   🤖 Summarizing with {model_name}...")
        
        # Split transcript into words and limit to 200-400 words
        words = transcript.split()
        word_count = len(words)
        
        # Use 300 words as target (middle of 200-400 range)
        target_words = min(300, word_count)
        limited_transcript = " ".join(words[:target_words])
        
        print(f"   📊 Using {target_words} words from transcript (total: {word_count} words)")
        
        prompt = f"""Summarize the following video transcript in 2-3 concise paragraphs. Focus on key points, main topics, and important information.

Transcript:
{limited_transcript}"""
        
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        summary = response.text.strip() if hasattr(response, 'text') else str(response)
        print(f"   ✓ Summary generated ({len(summary)} characters)")
        return summary
        
    except Exception as e:
        print(f"   ✗ Error summarizing with Gemini: {e}")
        return None

def build_issue_from_ranked_news(ranked_items):
    """Build processed news list from daily_ranked_news records.

    This function reads ranked items from the database (already ranked by Gemini)
    and processes them:
    - For websites: uses stored summary
    - For YouTube: looks up transcript and generates summary if available

    Args:
        ranked_items: list of dicts from get_daily_ranked_news(), each with:
            rank, source, news_id, title, published_at, source_link, video_id, summary

    Returns:
        list: Processed news items ready for email
    """
    from transcription.transcription_jobs import get_transcript_by_video_id

    print("\n" + "="*50)
    print("BUILDING ISSUE FROM STORED RANKING")
    print("="*50)

    processed_news = []

    print(f"\n🔄 Processing {len(ranked_items)} ranked items...")
    print("="*50)

    for idx, item in enumerate(ranked_items, 1):
        rank = item.get("rank", idx)
        source = item.get("source", "unknown")
        news_id = item.get("news_id")
        title = item.get("title", "")
        published_at = item.get("published_at", "")
        source_link = item.get("source_link", "")

        print(f"\n[{rank}/10] Processing {source.upper()}: {title[:50]}...")

        processed_item = {
            "id": news_id,
            "source": source,
            "title": title,
            "published_at": published_at,
            "source_link": source_link,
            "summary": None,
        }

        if source == "website":
            # Use stored summary from daily_ranked_news
            summary = item.get("summary") or ""
            processed_item["summary"] = summary
            if summary:
                print(f"   ✓ Using stored summary ({len(summary)} characters)")
            else:
                print(f"   ⚠ No summary available for this news item")

        elif source == "youtube":
            # Get video ID and look up transcript
            video_id = item.get("video_id")

            if not video_id:
                print(f"   ✗ No video_id found for news item {news_id}")
                processed_item["summary"] = "Video transcription unavailable"
            else:
                # Check if transcript exists in database
                transcript_data = get_transcript_by_video_id(video_id)

                if transcript_data and transcript_data.get("transcript"):
                    # Transcript exists, summarize it
                    transcript = transcript_data["transcript"]
                    print(f"   ✓ Found transcript ({len(transcript)} characters)")

                    summary = summarize_with_gemini(transcript)

                    if summary:
                        processed_item["summary"] = summary
                    else:
                        processed_item["summary"] = "Summary generation failed"
                else:
                    # No transcript yet - job may be pending or not created
                    print(f"   ⏳ No transcript found for video {video_id} (may be pending)")
                    processed_item["summary"] = "Transcription pending - waiting for worker"

        processed_news.append(processed_item)

    return processed_news


def process_top_news(top_n: int = 10, ranked_news: list | None = None, combined_news: list | None = None):
    """
    Process top N ranked news items:
    - For websites: use existing summary
    - For YouTube: transcribe and summarize
    
    Args:
        top_n: Number of top news items to process
    
    Returns:
        list: Processed news items
    """
    print("\n" + "="*50)
    print("PROCESSING TOP NEWS")
    print("="*50)
    
    # Load ranked news (from memory if provided, otherwise from JSON artifact)
    print("\n📊 Loading ranked news...")
    if ranked_news is None:
        ranked_news = load_ranked_news()
    
    if not ranked_news:
        print("✗ No ranked news found")
        return []
    
    # Get top N from the ranked list provided by Gemini
    top_ranked = ranked_news[:top_n]
    print(f"✓ Found {len(top_ranked)} top ranked news items")
    
    # Load combined news for full data (from memory if provided, otherwise from JSON)
    print("\n📰 Loading combined news data...")
    if combined_news is None:
        combined_news = load_combined_news()
    
    if not combined_news:
        print("✗ No combined news found")
        return []
    
    # Create a mapping by ID for quick lookup
    news_by_id = {item.get("id"): item for item in combined_news}
    
    print(f"✓ Loaded {len(combined_news)} news items")
    
    # Process each top news item
    processed_news = []
    
    print(f"\n🔄 Processing top {len(top_ranked)} news items...")
    print("="*50)
    
    for idx, ranked_item in enumerate(top_ranked, 1):
        news_id = ranked_item.get("id")
        source = ranked_item.get("source", "unknown")
        
        print(f"\n[{idx}/{len(top_ranked)}] Processing ID {news_id} ({source})...")
        
        # Get full news data
        news_item = news_by_id.get(news_id)
        
        if not news_item:
            print(f"   ✗ News item with ID {news_id} not found in combined news")
            continue
        
        # Prepare base data
        processed_item = {
            "id": news_id,
            "source": source,
            "title": news_item.get("title", ""),
            "published_at": news_item.get("published_at", ""),
            "source_link": news_item.get("source_link") if source == "website" else news_item.get("video_link", ""),
            "summary": None
        }
        
        if source == "website":
            # Use existing summary
            summary = news_item.get("summary") or ""
            processed_item["summary"] = summary
            if summary:
                print(f"   ✓ Using existing summary ({len(summary)} characters)")
            else:
                print(f"   ⚠ No summary available for this news item")
            
        elif source == "youtube":
            # Get video ID
            video_id = news_item.get("video_id")
            
            if not video_id:
                print(f"   ✗ No video_id found for news item {news_id}")
                processed_item["summary"] = "Video transcription unavailable"
            else:
                # Check if transcript exists in database
                transcript_data = get_transcript_by_video_id(video_id)
                
                if transcript_data and transcript_data.get("transcript"):
                    # Transcript exists, summarize it
                    transcript = transcript_data["transcript"]
                    print(f"   ✓ Found transcript ({len(transcript)} characters)")
                    
                    summary = summarize_with_gemini(transcript)
                    
                    if summary:
                        processed_item["summary"] = summary
                    else:
                        processed_item["summary"] = "Summary generation failed"
                else:
                    # No transcript yet - job may be pending or not created
                    print(f"   ⏳ No transcript found for video {video_id} (may be pending)")
                    processed_item["summary"] = "Transcription pending - waiting for worker"
        
        processed_news.append(processed_item)
    
    return processed_news

def save_top_news(processed_news: list, output_file: str = "top_news.json"):
    """Save processed top news to JSON file and daily_top_news table."""
    from datetime import datetime
    from core.utils import save_json_file

    output_data = {
        "total_items": len(processed_news),
        "news": processed_news
    }

    # Write JSON artifact (kept for debugging / backward compatibility)
    success = save_json_file(output_file, output_data)
    if success:
        print(f"\n✓ Saved top news to: {output_file}")

    # Also persist to database as the new source of truth
    try:
        today_utc = datetime.utcnow().date()
        db_id = create_daily_top_news(today_utc, processed_news)
        if db_id is not None:
            print(f"✓ Saved daily top news in database with id={db_id} for {today_utc}")
        else:
            print("✗ Failed to save daily top news in database")
    except Exception as e:
        print(f"✗ Error saving daily top news in database: {e}")

    return success

if __name__ == "__main__":
    try:
        # Check if API key is set
        if not os.getenv("GEMINI_API_KEY"):
            print("✗ Error: GEMINI_API_KEY not found in environment variables")
            print("   Please set GEMINI_API_KEY in your .env file")
            exit(1)
        
        # Process top 10 news
        processed_news = process_top_news(top_n=10)
        
        if processed_news:
            # Save to file
            save_top_news(processed_news)
            
            # Print summary
            print("\n" + "="*50)
            print("SUMMARY")
            print("="*50)
            website_count = sum(1 for item in processed_news if item["source"] == "website")
            youtube_count = sum(1 for item in processed_news if item["source"] == "youtube")
            
            print(f"Total processed: {len(processed_news)}")
            print(f"Website news: {website_count}")
            print(f"YouTube videos: {youtube_count}")
            print("="*50)
        else:
            print("\n✗ No news items processed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
