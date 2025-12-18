"""Main pipeline orchestrator: builds and sends newsletter from stored ranking.

This script does NOT re-rank news. It reads the top 10 ranked items from
daily_ranked_news (created by preprocess_jobs.py), joins with transcripts,
generates summaries, and sends the newsletter.
"""

import sys
import traceback
from datetime import date

from core.database import get_daily_ranked_news
from process_top_news import build_issue_from_ranked_news, save_top_news
from send_email import send_news_to_all_subscribers


def main():
    """Build and send newsletter from stored ranking (no re-ranking)."""
    print("\n" + "="*60)
    print("BUILDING & SENDING NEWSLETTER FROM STORED RANKING")
    print("="*60)
    
    try:
        # Step 1: Load ranked items from database (no ranking here!)
        print("\n[1/4] Loading ranked news from database...")
        today = date.today()
        ranked_items = get_daily_ranked_news(today)
        
        if not ranked_items:
            print(f"✗ No ranked news found for {today}")
            print("   Run preprocess_jobs.py first to rank and store top 10 items")
            return False
        
        print(f"✓ Loaded {len(ranked_items)} ranked items from daily_ranked_news")
        
        # Step 2: Build processed news (join with transcripts, generate summaries)
        print("\n[2/4] Processing ranked items (joining transcripts, generating summaries)...")
        processed_news = build_issue_from_ranked_news(ranked_items)
        
        if not processed_news:
            print("✗ Failed to process ranked news")
            return False
        
        print(f"✓ Processed {len(processed_news)} news items")
        
        # Step 3: Save final issue to database
        print("\n[3/4] Saving final issue to database...")
        save_top_news(processed_news)
        print("✓ Issue saved to daily_top_news")
        
        # Step 4: Send emails to all subscribers
        print("\n[4/4] Sending emails to subscribers...")
        success = send_news_to_all_subscribers(processed_news)
        
        if success:
            print("\n" + "="*60)
            print("✓ PIPELINE COMPLETED SUCCESSFULLY")
            print("="*60)
            return True
        else:
            print("\n" + "="*60)
            print("⚠ PIPELINE COMPLETED WITH WARNINGS")
            print("="*60)
            return False
            
    except Exception as e:
        print("\n" + "="*60)
        print("✗ PIPELINE FAILED")
        print("="*60)
        print(f"Error: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
