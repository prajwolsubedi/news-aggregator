"""Main pipeline orchestrator: builds and sends newsletter from stored ranking.

This script does NOT re-rank news. It reads the top 10 ranked items from
daily_ranked_news (created by preprocess_jobs.py), joins with transcripts,
generates summaries, and sends the newsletter.
"""

import sys
import traceback
import logging
from datetime import date

from core.database import get_daily_ranked_news
from process_top_news import build_issue_from_ranked_news, save_top_news
from send_email import send_news_to_all_subscribers

logger = logging.getLogger(__name__)
# Also use root logger to ensure visibility in Render logs
root_logger = logging.getLogger()


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
        logger.info("[4/4] Starting email sending step")
        root_logger.info("[PIPELINE] Step 4/4: Sending emails to subscribers")
        
        try:
            success = send_news_to_all_subscribers(processed_news)
            
            if success:
                print("\n" + "="*60)
                print("✓ PIPELINE COMPLETED SUCCESSFULLY")
                print("="*60)
                logger.info("Pipeline completed successfully - emails sent")
                root_logger.info("[PIPELINE] ✓ Completed successfully - emails sent")
                return True
            else:
                error_msg = "Email sending failed - no emails were sent successfully"
                print("\n" + "="*60)
                print("⚠ PIPELINE COMPLETED WITH WARNINGS")
                print("="*60)
                print(f"Error: {error_msg}")
                # Log to both module logger and root logger for visibility
                logger.error("="*60)
                logger.error("PIPELINE EMAIL SENDING FAILED")
                logger.error("="*60)
                logger.error(error_msg)
                root_logger.error("="*60)
                root_logger.error("[PIPELINE] EMAIL SENDING FAILED")
                root_logger.error("="*60)
                root_logger.error(f"[PIPELINE] {error_msg}")
                root_logger.error("[PIPELINE] Check send_email module logs above for detailed error messages")
                root_logger.error("[PIPELINE] Common issues:")
                root_logger.error("[PIPELINE]   1. SMTP authentication failed (check SENDER_PASSWORD is Gmail App Password)")
                root_logger.error("[PIPELINE]   2. SMTP server connection timeout")
                root_logger.error("[PIPELINE]   3. No active subscribers in database")
                root_logger.error("[PIPELINE]   4. Invalid email addresses in subscriber list")
                root_logger.error("="*60)
                return False
        except Exception as e:
            error_msg = f"Exception during email sending: {e}"
            print(f"\n✗ Error sending emails: {e}")
            logger.error(error_msg, exc_info=True)
            root_logger.error(f"[PIPELINE] Exception during email sending: {e}", exc_info=True)
            traceback.print_exc()
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
