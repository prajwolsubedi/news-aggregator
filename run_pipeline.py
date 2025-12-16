"""Main pipeline orchestrator that runs all news processing steps sequentially."""

import sys
import traceback
from combine_news import combine_news
from rank_news import rank_news_with_gemini, prepare_news_for_ranking
from process_top_news import process_top_news, save_top_news
from send_email import send_news_to_all_subscribers
from config import TOP_NEWS_COUNT


def main():
    """Run the complete news pipeline: fetch, combine, rank, process, and send emails."""
    print("\n" + "="*60)
    print("AI NEWS PIPELINE - STARTING")
    print("="*60)
    
    try:
        # Step 1: Combine news (fetches RSS and YouTube internally)
        print("\n[1/5] Fetching and combining news from all sources...")
        combined_news = combine_news()
        print(f"✓ Combined {len(combined_news)} total news items")
        
        # Step 2: Rank news
        print("\n[2/5] Ranking news by importance...")
        prepared_news = prepare_news_for_ranking(combined_news)
        if not prepared_news:
            print("✗ No valid news items to rank")
            return False
        ranked_news, ranked_output = rank_news_with_gemini(prepared_news, top_n=TOP_NEWS_COUNT)
        if not ranked_news:
            print("✗ Failed to rank news")
            return False
        print(f"✓ Ranked {len(ranked_news)} top news items")
        
        # Step 3: Process top news (transcribe YouTube, summarize)
        print("\n[3/5] Processing top news (transcribing & summarizing)...")
        processed_news = process_top_news(top_n=TOP_NEWS_COUNT)
        if processed_news:
            save_top_news(processed_news)
            print(f"✓ Processed {len(processed_news)} news items")
        else:
            print("✗ No news items processed")
            return False
        
        # Step 4: Send emails to all subscribers
        print("\n[4/5] Sending emails to subscribers...")
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
