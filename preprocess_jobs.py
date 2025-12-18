"""
Preprocessing step: Create transcription jobs for YouTube videos.

This runs before workers start to create all transcription jobs.
Workers will pull these jobs when they start.
"""

from combine_news import combine_news
from rank_news import rank_news_with_gemini, prepare_news_for_ranking
from transcription_jobs import create_transcription_job
from config import TOP_NEWS_COUNT


def preprocess_and_create_jobs():
    """
    Preprocessing step: Creates transcription jobs for top YouTube videos.
    
    This should run before workers start (e.g., 8:00 AM if workers start at 8:30 AM).
    """
    print("\n" + "="*60)
    print("PREPROCESSING: CREATING TRANSCRIPTION JOBS")
    print("="*60)
    
    try:
        # Step 1: Fetch RSS news
        print("\n[1/4] Fetching RSS news...")
        rss_news = combine_news()  # This combines RSS and YouTube
        print(f"✓ Combined {len(rss_news)} total news items")
        
        # Step 2: Rank news
        print("\n[2/4] Ranking all content...")
        prepared_news = prepare_news_for_ranking(rss_news)
        if not prepared_news:
            print("✗ No valid news items to rank")
            return False
        
        ranked_news, _ = rank_news_with_gemini(prepared_news, top_n=TOP_NEWS_COUNT)
        if not ranked_news:
            print("✗ Failed to rank news")
            return False
        print(f"✓ Ranked {len(ranked_news)} top news items")
        
        # Step 3: Select top YouTube videos
        print("\n[3/4] Selecting top YouTube videos...")
        from utils import load_json_file, get_news_from_json
        data = load_json_file("combined_news.json")
        all_news = get_news_from_json(data) if data else []
        news_by_id = {item.get("id"): item for item in all_news}
        
        top_youtube_videos = []
        for ranked_item in ranked_news:
            if ranked_item.get("source") == "youtube":
                news_id = ranked_item.get("id")
                news_item = news_by_id.get(news_id)
                if news_item and news_item.get("video_id"):
                    top_youtube_videos.append(news_item)
        
        print(f"✓ Found {len(top_youtube_videos)} YouTube videos in top news")
        
        # Step 4: Create transcription jobs
        print("\n[4/4] Creating transcription jobs...")
        jobs_created = 0
        for idx, video in enumerate(top_youtube_videos):
            video_id = video.get("video_id")
            video_url = video.get("video_link", f"https://www.youtube.com/watch?v={video_id}" if video_id else "")
            video_title = video.get("title", "")
            
            if video_id:
                try:
                    job_id = create_transcription_job(
                        video_id=video_id,
                        video_url=video_url,
                        video_title=video_title,
                        priority=idx  # Lower index = higher priority
                    )
                    jobs_created += 1
                    print(f"   ✓ Created job for: {video_title[:50]}...")
                except Exception as e:
                    print(f"   ✗ Error creating job for {video_id}: {e}")
        
        print(f"\n✓ Created {jobs_created} transcription job(s)")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n✗ Preprocessing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = preprocess_and_create_jobs()
    exit(0 if success else 1)
