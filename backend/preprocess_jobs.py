"""
Preprocessing step: Rank news once and store top 10, create transcription jobs for YouTube videos.

This runs before workers start to create all transcription jobs.
Workers will pull these jobs when they start.

This is the ONLY place where Gemini ranking happens.
"""

from datetime import date
from news.combine_news import combine_news
from ranking.rank_news import rank_news_with_gemini, prepare_news_for_ranking
from transcription.transcription_jobs import create_transcription_job
from core.utils import load_json_file, get_news_from_json
from core.database import insert_daily_ranked_news
from config import TOP_NEWS_COUNT


def preprocess_and_create_jobs():
    """
    Preprocessing step: Ranks all news once, stores top 10 in daily_ranked_news,
    and creates transcription jobs only for top-10 YouTube videos.
    
    This should run before workers start (e.g., 8:00 AM if workers start at 8:30 AM).
    """
    print("\n" + "="*60)
    print("PREPROCESSING: RANKING NEWS & CREATING TRANSCRIPTION JOBS")
    print("="*60)
    
    try:
        # Step 1: Fetch + combine news
        print("\n[1/5] Fetching and combining news from all sources...")
        rss_news = combine_news()  # This combines RSS and YouTube
        
        # Count by source
        website_count = sum(1 for item in rss_news if item.get("source") == "website")
        youtube_count = sum(1 for item in rss_news if item.get("source") == "youtube")
        print(f"✓ Combined {len(rss_news)} total news items")
        print(f"  - Website news: {website_count}")
        print(f"  - YouTube videos: {youtube_count}")
        
        # Step 2: Rank ALL news once (this is the ONLY ranking step)
        print("\n[2/5] Ranking all content with Gemini...")
        prepared_news = prepare_news_for_ranking(rss_news)
        if not prepared_news:
            print("✗ No valid news items to rank")
            return False
        
        ranked_news, _ = rank_news_with_gemini(prepared_news, top_n=TOP_NEWS_COUNT)
        if not ranked_news:
            print("✗ Failed to rank news")
            return False
        
        # Count YouTube videos in ranked results
        ranked_youtube_count = sum(1 for item in ranked_news if item.get("source") == "youtube")
        ranked_website_count = sum(1 for item in ranked_news if item.get("source") == "website")
        print(f"✓ Ranked {len(ranked_news)} top news items")
        print(f"  - Website news in top {TOP_NEWS_COUNT}: {ranked_website_count}")
        print(f"  - YouTube videos in top {TOP_NEWS_COUNT}: {ranked_youtube_count}")
        
        # Step 3: Use in-memory news data (don't rely on JSON file on ephemeral filesystem)
        print("\n[3/5] Loading full news metadata...")
        # Use the rss_news data we already have in memory instead of loading from file
        # This avoids issues with ephemeral filesystem on Render
        news_by_id = {item.get("id"): item for item in rss_news}
        
        # Step 4: Store top 10 ranked items in daily_ranked_news
        print("\n[4/5] Storing top 10 ranked items in database...")
        today = date.today()
        top_ranked = ranked_news[:TOP_NEWS_COUNT]
        top_items_for_db = []
        
        for idx, ranked_item in enumerate(top_ranked, start=1):
            news_id = ranked_item.get("id")
            source = ranked_item.get("source", "unknown")
            news_item = news_by_id.get(news_id)
            
            if not news_item:
                print(f"   ⚠ Skipping ranked item {news_id} - not found in combined news")
                continue
            
            source_link = news_item.get("source_link") if source == "website" else news_item.get("video_link", "")
            video_id = news_item.get("video_id") if source == "youtube" else None
            
            item_data = {
                "rank": idx,
                "source": source,
                "news_id": news_id,
                "title": news_item.get("title", ""),
                "published_at": news_item.get("published_at"),
                "source_link": source_link,
                "video_id": video_id,
                "summary": news_item.get("summary") if source == "website" else None,
            }
            
            top_items_for_db.append(item_data)
        
        rows_inserted = insert_daily_ranked_news(today, top_items_for_db)
        if rows_inserted:
            print(f"✓ Stored {rows_inserted} ranked items in daily_ranked_news for {today}")
        else:
            print("✗ Failed to store ranked items in database")
            return False
        
        # Step 5: Create transcription jobs only for top-10 YouTube videos
        print("\n[5/5] Creating transcription jobs for top YouTube videos...")
        top_youtube_videos = [
            item for item in top_items_for_db
            if item["source"] == "youtube" and item["video_id"]
        ]
        
        print(f"✓ Found {len(top_youtube_videos)} YouTube videos in top 10")
        
        jobs_created = 0
        for idx, item in enumerate(top_youtube_videos):
            video_id = item["video_id"]
            video_url = item["source_link"]
            video_title = item["title"]
            
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
