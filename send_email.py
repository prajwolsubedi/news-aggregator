import json
import os
import re
import smtplib
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from core import models
from core.utils import load_json_file, get_news_from_json
from core.database import get_latest_daily_top_news

logger = logging.getLogger(__name__)
# Also use root logger to ensure visibility in Render logs
root_logger = logging.getLogger()

load_dotenv()

def load_top_news(json_file: str = "top_news.json"):
    """Load top news, preferring the latest entry from daily_top_news table.

    Falls back to top_news.json for backward compatibility if no DB row exists.
    """
    # First try database-backed daily_top_news
    latest = get_latest_daily_top_news()
    if latest and latest.get("top_items"):
        print("✓ Loaded top news from daily_top_news table")
        return latest["top_items"]

    # Fallback to JSON artifact
    print("⚠ No daily_top_news found in DB, falling back to top_news.json")
    data = load_json_file(json_file)
    return get_news_from_json(data) if data else []

def get_youtube_thumbnail(video_id: str):
    """Get YouTube thumbnail URL from video ID."""
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

def create_html_email(news_items: list, unsubscribe_url: str | None = None):
    """Create styled HTML email with animations and optional unsubscribe link."""
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Top AI News - """ + current_date + """</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                line-height: 1.6;
            }
            
            .email-container {
                max-width: 700px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 32px;
                font-weight: 700;
                margin-bottom: 10px;
                animation: fadeInDown 0.6s ease-out;
            }
            
            .header p {
                font-size: 16px;
                opacity: 0.9;
                animation: fadeInUp 0.6s ease-out 0.2s both;
            }
            
            .content {
                padding: 40px 30px;
            }
            
            .news-item {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 25px;
                border-left: 4px solid #667eea;
                transition: all 0.3s ease;
                animation: slideInLeft 0.5s ease-out;
                animation-fill-mode: both;
            }
            
            .news-item:nth-child(1) { animation-delay: 0.1s; }
            .news-item:nth-child(2) { animation-delay: 0.2s; }
            .news-item:nth-child(3) { animation-delay: 0.3s; }
            .news-item:nth-child(4) { animation-delay: 0.4s; }
            .news-item:nth-child(5) { animation-delay: 0.5s; }
            .news-item:nth-child(6) { animation-delay: 0.6s; }
            .news-item:nth-child(7) { animation-delay: 0.7s; }
            .news-item:nth-child(8) { animation-delay: 0.8s; }
            .news-item:nth-child(9) { animation-delay: 0.9s; }
            .news-item:nth-child(10) { animation-delay: 1.0s; }
            .news-item:nth-child(11) { animation-delay: 1.1s; }
            
            .news-item:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
                border-left-color: #764ba2;
            }
            
            .news-header {
                display: flex;
                align-items: flex-start;
                gap: 20px;
                margin-bottom: 15px;
            }
            
            .thumbnail {
                width: 300px;
                height: 150px;
                border-radius: 10px;
                object-fit: cover;
                flex-shrink: 0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease;
                padding-right: 10px;
            }
            
            .thumbnail:hover {
                transform: scale(1.05);
            }
            
            .news-info {
                flex: 1;
            }
            
            .source-badge {
                display: inline-block;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                margin-bottom: 10px;
                animation: pulse 2s infinite;
            }
            
            .source-website {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .source-youtube {
                background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
                color: white;
            }
            
            .news-title {
                font-size: 20px;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 12px;
                line-height: 1.4;
            }
            
            .news-link {
                display: inline-block;
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
                font-size: 14px;
                transition: all 0.3s ease;
                position: relative;
            }
            
            .news-link::after {
                content: '→';
                margin-left: 5px;
                transition: transform 0.3s ease;
                display: inline-block;
            }
            
            .news-link:hover::after {
                transform: translateX(5px);
            }
            
            .news-link:hover {
                color: #764ba2;
            }
            
            .news-summary {
                color: #4a5568;
                font-size: 15px;
                line-height: 1.7;
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #e2e8f0;
            }
            
            .news-meta {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 15px;
                font-size: 13px;
                color: #718096;
            }
            
            .footer {
                background: #f8f9fa;
                padding: 30px;
                text-align: center;
                color: #718096;
                font-size: 14px;
            }
            
            @keyframes fadeInDown {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes slideInLeft {
                from {
                    opacity: 0;
                    transform: translateX(-30px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes pulse {
                0%, 100% {
                    opacity: 1;
                }
                50% {
                    opacity: 0.8;
                }
            }
            
            @media (max-width: 600px) {
                .news-header {
                    flex-direction: column;
                }
                
                .thumbnail {
                    width: 100%;
                    height: 200px;
                }
                
                .header h1 {
                    font-size: 24px;
                }
                
                .content {
                    padding: 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1> Top AI News</h1>
                <p>""" + current_date + """</p>
            </div>
            
            <div class="content">
    """
    
    # Add news items
    for idx, item in enumerate(news_items, 1):
        source = item.get("source", "unknown")
        title = item.get("title", "No title")
        summary = item.get("summary", "No summary available")
        source_link = item.get("source_link", "#")
        published_at = item.get("published_at", "")
        
        # Format published date
        try:
            if published_at:
                pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                formatted_date = pub_date.strftime("%B %d, %Y at %I:%M %p")
            else:
                formatted_date = "Date not available"
        except:
            formatted_date = published_at if published_at else "Date not available"
        
        # Get thumbnail for YouTube videos
        thumbnail_html = ""
        if source == "youtube":
            video_id = source_link.split("v=")[-1].split("&")[0] if "v=" in source_link else ""
            if video_id:
                thumbnail_url = get_youtube_thumbnail(video_id)
                thumbnail_html = f'<img src="{thumbnail_url}" alt="Video thumbnail" class="thumbnail">'
        
        source_class = "source-website" if source == "website" else "source-youtube"
        source_label = "📰 Website" if source == "website" else "📺 YouTube"
        
        html_content += f"""
                <div class="news-item">
                    <div class="news-header">
                        {thumbnail_html if thumbnail_html else ''}
                        <div class="news-info">
                            <span class="source-badge {source_class}">{source_label}</span>
                            <h2 class="news-title">{title}</h2>
                            <a href="{source_link}" target="_blank" class="news-link">Read Full Article</a>
                        </div>
                    </div>
                    <div class="news-summary">
                        {summary}
                    </div>
                    <div class="news-meta">
                        <span>#{idx}</span>
                        <span>{formatted_date}</span>
                    </div>
                </div>
        """
    
    html_content += """
            </div>
            
            <div class="footer">
                <p>Generated by AI News Aggregator</p>
                <p style="margin-top: 10px; font-size: 12px;">Stay updated with the latest AI news and developments</p>
                <!--UNSUBSCRIBE_PLACEHOLDER-->
            </div>
        </div>
    </body>
    </html>
    """
    # Insert unsubscribe footer if URL provided
    unsubscribe_html = ""
    if unsubscribe_url:
        unsubscribe_html = (
            '<p style="margin-top: 15px; font-size: 12px;">'
            'If you no longer want to receive these emails, you can '
            f'<a href="{unsubscribe_url}">unsubscribe here</a>.'
            "</p>"
        )
    html_content = html_content.replace("<!--UNSUBSCRIBE_PLACEHOLDER-->", unsubscribe_html)

    return html_content

def validate_email(email: str):
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def _build_unsubscribe_url(token: str | None) -> str | None:
    """Build full unsubscribe URL from token.

    Uses BASE_URL environment variable if present, otherwise falls back to a relative URL.
    """
    if not token:
        return None

    base_url = os.getenv("BASE_URL", "").strip()
    if base_url:
        return f"{base_url.rstrip('/')}/unsubscribe/{token}"
    # Relative path fallback; still useful in plain-text/preview environments
    return f"/unsubscribe/{token}"


def send_raw_html_email(recipient_email: str, subject: str, html_content: str) -> bool:
    """Send a generic HTML email to a single recipient.

    Reuses the same SMTP configuration and validation as the news email.
    Intended for welcome / transactional emails.
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        print("✗ Error: SENDER_EMAIL and SENDER_PASSWORD must be set in .env file")
        return False

    if not recipient_email:
        print("✗ Error: Recipient email not provided")
        return False

    if not validate_email(recipient_email):
        print(f"✗ Error: Invalid email format for transactional email: {recipient_email}")
        return False

    try:
        print(f"\n📧 Preparing transactional email to {recipient_email}...")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient_email

        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        print("📤 Connecting to SMTP server for transactional email...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            print("✉️ Sending transactional email...")
            server.send_message(msg)

        print(f"✓ Transactional email sent successfully to {recipient_email}!")
        return True
    except smtplib.SMTPAuthenticationError:
        print("✗ Authentication failed for transactional email. Check your email and password.")
        return False
    except Exception as e:
        print(f"✗ Error sending transactional email: {e}")
        return False


def send_email(news_items: list, recipient_email: str, unsubscribe_url: str | None = None):
    """Send HTML email with top news to a single recipient."""

    # Email configuration from environment variables
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        print("✗ Error: SENDER_EMAIL and SENDER_PASSWORD must be set in .env file")
        return False
    
    if not recipient_email:
        print("✗ Error: Recipient email not provided")
        return False
    
    # Validate email format
    if not validate_email(recipient_email):
        print(f"✗ Error: Invalid email format: {recipient_email}")
        print("   Please provide a valid email address (e.g., yourname@gmail.com)")
        return False
    
    # Check for placeholder domains
    placeholder_domains = ['example.com', 'test.com', 'example.org', 'test.org']
    recipient_domain = recipient_email.split('@')[1].lower() if '@' in recipient_email else ''
    if recipient_domain in placeholder_domains:
        print(f"✗ Error: '{recipient_email}' is a placeholder email address")
        print("   Please use a real email address (e.g., yourname@gmail.com)")
        return False
    
    try:
        print(f"\n📧 Preparing email to {recipient_email}...")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Top AI News - {datetime.now().strftime('%B %d, %Y')}"
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # Create HTML content
        html_content = create_html_email(news_items, unsubscribe_url=unsubscribe_url)
        
        # Attach HTML part
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        print("📤 Connecting to SMTP server...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            print("🔐 Authenticating...")
            server.login(sender_email, sender_password)
            print("✉️ Sending email...")
            server.send_message(msg)
        
        print(f"✓ Email sent successfully to {recipient_email}!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"✗ SMTP Authentication failed for {recipient_email}. Error: {e}"
        print(error_msg)
        print("   For Gmail, you may need to use an App Password instead of your regular password.")
        logger.error(error_msg, exc_info=True)
        logger.error(f"SMTP Server: {smtp_server}, Port: {smtp_port}, Sender: {sender_email}")
        root_logger.error(f"[EMAIL] SMTP Authentication failed for {recipient_email}: {e}")
        root_logger.error(f"[EMAIL] SMTP Server: {smtp_server}, Port: {smtp_port}, Sender: {sender_email}")
        root_logger.error("[EMAIL] For Gmail, use an App Password instead of regular password")
        return False
    except smtplib.SMTPException as e:
        error_msg = f"✗ SMTP error sending email to {recipient_email}: {e}"
        print(error_msg)
        logger.error(error_msg, exc_info=True)
        logger.error(f"SMTP Server: {smtp_server}, Port: {smtp_port}")
        root_logger.error(f"[EMAIL] SMTP error sending email to {recipient_email}: {e}")
        root_logger.error(f"[EMAIL] SMTP Server: {smtp_server}, Port: {smtp_port}")
        return False
    except smtplib.SMTPServerDisconnected as e:
        error_msg = f"✗ SMTP server disconnected while sending to {recipient_email}: {e}"
        print(error_msg)
        logger.error(error_msg, exc_info=True)
        root_logger.error(f"[EMAIL] SMTP server disconnected while sending to {recipient_email}: {e}")
        return False
    except Exception as e:
        error_msg = f"✗ Unexpected error sending email to {recipient_email}: {type(e).__name__}: {e}"
        print(error_msg)
        logger.error(error_msg, exc_info=True)
        root_logger.error(f"[EMAIL] Unexpected error sending email to {recipient_email}: {type(e).__name__}: {e}")
        return False


def send_news_to_all_subscribers(news_items: list) -> bool:
    """Send news email to all active subscribers from the database."""
    logger.info("="*60)
    logger.info("EMAIL SENDING - STARTING")
    logger.info("="*60)
    root_logger.info("[EMAIL] ============================================================")
    root_logger.info("[EMAIL] EMAIL SENDING - STARTING")
    root_logger.info("[EMAIL] ============================================================")
    
    subscribers = models.get_all_active_subscribers()
    subscriber_count = len(subscribers) if subscribers else 0
    logger.info(f"Retrieved {subscriber_count} subscribers from database")
    root_logger.info(f"[EMAIL] Retrieved {subscriber_count} subscribers from database")

    if not subscribers:
        error_msg = "✗ No active subscribers found. No emails sent."
        print(error_msg)
        logger.error(error_msg)
        root_logger.error("[EMAIL] ✗ No active subscribers found. No emails sent.")
        logger.error("="*60)
        return False

    print(f"📧 Sending news to {len(subscribers)} active subscribers...")
    logger.info(f"Starting to send emails to {len(subscribers)} subscribers")
    root_logger.info(f"[EMAIL] Starting to send emails to {len(subscribers)} subscribers")
    
    # Check email configuration before starting
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    logger.info(f"SENDER_EMAIL configured: {'Yes' if sender_email else 'No'}")
    logger.info(f"SENDER_PASSWORD configured: {'Yes' if sender_password else 'No'}")
    root_logger.info(f"[EMAIL] SENDER_EMAIL configured: {'Yes' if sender_email else 'No'}")
    root_logger.info(f"[EMAIL] SENDER_PASSWORD configured: {'Yes' if sender_password else 'No'}")
    
    if not sender_email or not sender_password:
        error_msg = "✗ SENDER_EMAIL or SENDER_PASSWORD not set in environment variables"
        print(error_msg)
        logger.error("="*60)
        logger.error("EMAIL CONFIGURATION ERROR")
        logger.error("="*60)
        logger.error(error_msg)
        logger.error(f"SENDER_EMAIL: {'SET' if sender_email else 'NOT SET'}")
        logger.error(f"SENDER_PASSWORD: {'SET' if sender_password else 'NOT SET'}")
        root_logger.error("="*60)
        root_logger.error("[EMAIL] EMAIL CONFIGURATION ERROR")
        root_logger.error("="*60)
        root_logger.error(f"[EMAIL] {error_msg}")
        root_logger.error(f"[EMAIL] SENDER_EMAIL: {'SET' if sender_email else 'NOT SET'}")
        root_logger.error(f"[EMAIL] SENDER_PASSWORD: {'SET' if sender_password else 'NOT SET'}")
        logger.error("="*60)
        return False
    
    logger.info(f"Using sender email: {sender_email}")
    logger.info(f"SMTP Server: {os.getenv('SMTP_SERVER', 'smtp.gmail.com')}")
    logger.info(f"SMTP Port: {os.getenv('SMTP_PORT', '587')}")
    root_logger.info(f"[EMAIL] Using sender email: {sender_email}")
    root_logger.info(f"[EMAIL] SMTP Server: {os.getenv('SMTP_SERVER', 'smtp.gmail.com')}")
    root_logger.info(f"[EMAIL] SMTP Port: {os.getenv('SMTP_PORT', '587')}")
    
    success_count = 0
    failed_emails = []
    error_details = []
    
    for idx, subscriber in enumerate(subscribers, 1):
        unsubscribe_url = _build_unsubscribe_url(subscriber.unsubscribe_token)
        try:
            logger.info(f"[{idx}/{len(subscribers)}] Attempting to send email to {subscriber.email}")
            root_logger.info(f"[EMAIL] [{idx}/{len(subscribers)}] Attempting to send email to {subscriber.email}")
            if send_email(news_items, subscriber.email, unsubscribe_url=unsubscribe_url):
                success_count += 1
                logger.info(f"[{idx}/{len(subscribers)}] Successfully sent email to {subscriber.email}")
                root_logger.info(f"[EMAIL] [{idx}/{len(subscribers)}] ✓ Successfully sent email to {subscriber.email}")
            else:
                failed_emails.append(subscriber.email)
                error_details.append(f"{subscriber.email}: send_email returned False")
                logger.warning(f"[{idx}/{len(subscribers)}] Failed to send email to {subscriber.email} - send_email returned False")
                root_logger.warning(f"[EMAIL] [{idx}/{len(subscribers)}] ✗ Failed to send email to {subscriber.email} - send_email returned False")
        except Exception as e:
            failed_emails.append(subscriber.email)
            error_details.append(f"{subscriber.email}: {str(e)}")
            logger.error(f"[{idx}/{len(subscribers)}] Exception sending email to {subscriber.email}: {e}", exc_info=True)
            root_logger.error(f"[EMAIL] [{idx}/{len(subscribers)}] Exception sending email to {subscriber.email}: {e}", exc_info=True)

    result_msg = f"✓ Finished sending emails. Success: {success_count}/{len(subscribers)}"
    print(result_msg)
    logger.info("="*60)
    logger.info("EMAIL SENDING - COMPLETED")
    logger.info("="*60)
    logger.info(result_msg)
    
    if failed_emails:
        error_summary = f"Failed to send emails to {len(failed_emails)}/{len(subscribers)} subscribers"
        logger.error("="*60)
        logger.error("EMAIL SENDING FAILURE SUMMARY")
        logger.error("="*60)
        logger.error(error_summary)
        logger.error(f"Total subscribers: {len(subscribers)}")
        logger.error(f"Successful sends: {success_count}")
        logger.error(f"Failed sends: {len(failed_emails)}")
        logger.error(f"Failed email addresses (first 10): {failed_emails[:10]}")
        logger.error(f"Error details (first 5):")
        for detail in error_details[:5]:
            logger.error(f"  - {detail}")
        logger.error("="*60)
        # Also log to root logger for visibility
        root_logger.error("="*60)
        root_logger.error("[EMAIL] EMAIL SENDING FAILURE SUMMARY")
        root_logger.error("="*60)
        root_logger.error(f"[EMAIL] {error_summary}")
        root_logger.error(f"[EMAIL] Total subscribers: {len(subscribers)}")
        root_logger.error(f"[EMAIL] Successful sends: {success_count}")
        root_logger.error(f"[EMAIL] Failed sends: {len(failed_emails)}")
        root_logger.error(f"[EMAIL] Failed email addresses (first 10): {failed_emails[:10]}")
        root_logger.error(f"[EMAIL] Error details (first 5):")
        for detail in error_details[:5]:
            root_logger.error(f"[EMAIL]   - {detail}")
        root_logger.error("="*60)
        print(f"✗ {error_summary}")
    elif success_count == 0:
        logger.error("="*60)
        logger.error("EMAIL SENDING FAILURE - NO EMAILS SENT")
        logger.error("="*60)
        logger.error(f"Total subscribers: {len(subscribers)}")
        logger.error("All email attempts returned False - check SMTP configuration")
        logger.error("This usually means:")
        logger.error("  1. SMTP authentication failed (wrong password/app password)")
        logger.error("  2. SMTP server connection failed")
        logger.error("  3. All email addresses are invalid")
        logger.error("="*60)
        # Also log to root logger for visibility
        root_logger.error("="*60)
        root_logger.error("[EMAIL] EMAIL SENDING FAILURE - NO EMAILS SENT")
        root_logger.error("="*60)
        root_logger.error(f"[EMAIL] Total subscribers: {len(subscribers)}")
        root_logger.error("[EMAIL] All email attempts returned False - check SMTP configuration")
        root_logger.error("[EMAIL] This usually means:")
        root_logger.error("[EMAIL]   1. SMTP authentication failed (wrong password/app password)")
        root_logger.error("[EMAIL]   2. SMTP server connection failed")
        root_logger.error("[EMAIL]   3. All email addresses are invalid")
        root_logger.error("="*60)
    
    return success_count > 0

if __name__ == "__main__":
    import sys

    print("\n" + "=" * 50)
    print("SENDING TOP AI NEWS VIA EMAIL")
    print("=" * 50)

    # Load top news
    news_items = load_top_news()

    if not news_items:
        print("✗ No news items found. Please run process_top_news.py first.")
        exit(1)

    print(f"✓ Loaded {len(news_items)} news items")

    # Optional: single-recipient mode for testing / ad-hoc sends
    recipient_email = os.getenv("RECIPIENT_EMAIL")
    if len(sys.argv) > 1:
        recipient_email = sys.argv[1]

    if recipient_email:
        # Try to attach unsubscribe link if this email is a known subscriber
        subscriber = models.get_subscriber_by_email(recipient_email)
        unsubscribe_url = None
        if subscriber:
            unsubscribe_url = _build_unsubscribe_url(subscriber.unsubscribe_token)

        success = send_email(news_items, recipient_email, unsubscribe_url=unsubscribe_url)
    else:
        # Default behaviour for pipeline: send to all active subscribers
        success = send_news_to_all_subscribers(news_items)

    if success:
        print("\n" + "=" * 50)
        print("✓ Email send run completed successfully!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("✗ Email send run failed or no emails were sent")
        print("=" * 50)
        exit(1)
