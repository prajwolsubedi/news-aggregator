import json
import os
import re
import logging
from datetime import datetime

from dotenv import load_dotenv
import resend

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
    """Create professional minimalist HTML email with responsive design."""
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    html_content = """
<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="x-apple-disable-message-reformatting">
    <title>AI News Digest - """ + current_date + """</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <style type="text/css">
        /* Reset styles */
        body, table, td, p, a, li, blockquote {
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }
        table, td {
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }
        img {
            -ms-interpolation-mode: bicubic;
            border: 0;
            height: auto;
            line-height: 100%;
            outline: none;
            text-decoration: none;
        }
        
        /* Base styles */
        body {
            margin: 0 !important;
            padding: 0 !important;
            background-color: #f4f4f5;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }
        
        /* Link styles */
        a {
            color: #2563eb;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        
        /* Responsive styles */
        @media screen and (max-width: 600px) {
            .mobile-full-width {
                width: 100% !important;
                max-width: 100% !important;
            }
            .mobile-padding {
                padding-left: 20px !important;
                padding-right: 20px !important;
            }
            .mobile-stack {
                display: block !important;
                width: 100% !important;
            }
            .mobile-center {
                text-align: center !important;
            }
            .mobile-hide {
                display: none !important;
            }
            .video-thumbnail {
                width: 100% !important;
                height: auto !important;
                max-width: 100% !important;
            }
            .content-cell {
                padding: 24px 20px !important;
            }
            .news-card {
                margin-bottom: 16px !important;
            }
            .header-title {
                font-size: 24px !important;
            }
        }
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f5;">
    <!-- Preview text -->
    <div style="display: none; max-height: 0; overflow: hidden;">
        Your daily AI news digest is here - Top stories curated for you
        &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
    </div>
    
    <!-- Email wrapper -->
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f4f4f5;">
        <tr>
            <td align="center" style="padding: 40px 16px;">
                
                <!-- Main container -->
                <table role="presentation" class="mobile-full-width" width="600" cellspacing="0" cellpadding="0" border="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%); padding: 52px 40px; text-align: center;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td align="center">
                                        <!-- Logo -->
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto 24px;">
                                            <tr>
                                                <td style="padding-right: 12px;" valign="middle">
                                                    <div style="width: 44px; height: 44px; background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); border-radius: 10px; text-align: center;">
                                                        <span style="font-size: 22px; line-height: 44px; display: block;">✦</span>
                                                    </div>
                                                </td>
                                                <td valign="middle">
                                                    <span style="font-size: 22px; font-weight: 700; color: #ffffff; letter-spacing: -0.3px;">AI News</span>
                                                </td>
                                            </tr>
                                        </table>
                                        <!-- Tagline -->
                                        <p style="margin: 0 0 6px 0; font-size: 13px; font-weight: 500; color: #94a3b8; text-transform: uppercase; letter-spacing: 2px;">
                                            Daily Digest
                                        </p>
                                        <p style="margin: 0; font-size: 15px; color: #64748b; font-weight: 400;">
                                            """ + current_date + """
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Intro section -->
                    <tr>
                        <td class="content-cell" style="padding: 32px 40px 24px 40px;">
                            <p style="margin: 0; font-size: 16px; color: #52525b; line-height: 1.6;">
                                Here are today's top AI stories, carefully curated to keep you informed about the latest developments in artificial intelligence.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- News items container -->
                    <tr>
                        <td class="content-cell" style="padding: 0 40px 32px 40px;">
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
                formatted_date = pub_date.strftime("%b %d, %Y")
            else:
                formatted_date = ""
        except:
            formatted_date = ""
        
        # Determine source styling
        is_youtube = source == "youtube"
        source_bg = "#dc2626" if is_youtube else "#2563eb"
        source_label = "VIDEO" if is_youtube else "ARTICLE"
        source_icon = "▶" if is_youtube else "◉"
        
        # Build YouTube thumbnail section
        thumbnail_section = ""
        if is_youtube:
            video_id = source_link.split("v=")[-1].split("&")[0] if "v=" in source_link else ""
            if video_id:
                thumbnail_url = get_youtube_thumbnail(video_id)
                thumbnail_section = f"""
                            <!-- YouTube Thumbnail -->
                            <tr>
                                <td style="padding-bottom: 16px;">
                                    <a href="{source_link}" target="_blank" style="display: block; text-decoration: none;">
                                        <div style="position: relative; border-radius: 8px; overflow: hidden;">
                                            <img src="{thumbnail_url}" alt="Video thumbnail" class="video-thumbnail" width="520" style="width: 100%; height: auto; display: block; border-radius: 8px;">
                                            <!-- Play button overlay -->
                                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 64px; height: 64px; background-color: rgba(0, 0, 0, 0.7); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                                <span style="color: #ffffff; font-size: 24px; margin-left: 4px;">▶</span>
                                            </div>
                                        </div>
                                    </a>
                                </td>
                            </tr>
                """
        
        # Build the news card
        html_content += f"""
                            <!-- News Item {idx} -->
                            <table role="presentation" class="news-card" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 24px; background-color: #fafafa; border-radius: 12px; overflow: hidden;">
                                <tr>
                                    <td style="padding: 24px;">
                                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                            <!-- Header row with number and source badge -->
                                            <tr>
                                                <td style="padding-bottom: 14px;">
                                                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                                        <tr>
                                                            <td width="36" valign="middle">
                                                                <span style="display: inline-block; font-size: 15px; font-weight: 700; color: #3b82f6; letter-spacing: -0.5px;">#{idx}</span>
                                                            </td>
                                                            <td align="right" valign="middle">
                                                                <span style="display: inline-block; padding: 5px 12px; background-color: {source_bg}; color: #ffffff; font-size: 10px; font-weight: 600; letter-spacing: 0.8px; border-radius: 20px; text-transform: uppercase;">
                                                                    {source_icon} {source_label}
                                                                </span>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                            
                                            {thumbnail_section}
                                            
                                            <!-- Title -->
                                            <tr>
                                                <td style="padding-bottom: 12px;">
                                                    <a href="{source_link}" target="_blank" style="text-decoration: none;">
                                                        <h2 style="margin: 0; font-size: 18px; font-weight: 600; color: #18181b; line-height: 1.4;">
                                                            {title}
                                                        </h2>
                                                    </a>
                                                </td>
                                            </tr>
                                            
                                            <!-- Summary -->
                                            <tr>
                                                <td style="padding-bottom: 16px;">
                                                    <p style="margin: 0; font-size: 15px; color: #52525b; line-height: 1.65;">
                                                        {summary}
                                                    </p>
                                                </td>
                                            </tr>
                                            
                                            <!-- Footer with link and date -->
                                            <tr>
                                                <td>
                                                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                                        <tr>
                                                            <td>
                                                                <a href="{source_link}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #18181b; color: #ffffff; font-size: 13px; font-weight: 500; text-decoration: none; border-radius: 6px;">
                                                                    {"Watch Video" if is_youtube else "Read More"} →
                                                                </a>
                                                            </td>
                                                            <td align="right" style="font-size: 13px; color: #a1a1aa;">
                                                                {formatted_date}
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
        """
    
    html_content += """
                        </td>
                    </tr>
                    
                    <!-- Divider -->
                    <tr>
                        <td style="padding: 0 40px;">
                            <div style="height: 1px; background-color: #e4e4e7;"></div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 32px 40px; text-align: center;">
                            <p style="margin: 0 0 8px 0; font-size: 14px; color: #71717a;">
                                Curated with ❤️ by <strong style="color: #18181b;">AI News Digest</strong>
                            </p>
                            <p style="margin: 0; font-size: 13px; color: #a1a1aa;">
                                Keeping you informed about the future of AI
                            </p>
                            <!--UNSUBSCRIBE_PLACEHOLDER-->
                        </td>
                    </tr>
                    
                </table>
                <!-- End main container -->
                
                <!-- Bottom branding -->
                <table role="presentation" width="600" class="mobile-full-width" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                        <td style="padding: 24px 40px; text-align: center;">
                            <p style="margin: 0; font-size: 12px; color: #a1a1aa;">
                                © """ + str(datetime.now().year) + """ AI News Digest. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
                
            </td>
        </tr>
    </table>
</body>
</html>
    """
    
    # Insert unsubscribe footer if URL provided
    unsubscribe_html = ""
    if unsubscribe_url:
        unsubscribe_html = (
            '<p style="margin: 16px 0 0 0; font-size: 13px; color: #a1a1aa;">'
            '<a href="' + unsubscribe_url + '" style="color: #71717a; text-decoration: underline;">Unsubscribe</a> from these emails'
            '</p>'
        )
    html_content = html_content.replace("<!--UNSUBSCRIBE_PLACEHOLDER-->", unsubscribe_html)

    return html_content

def validate_email(email: str):
    """Validate email address format with security checks.
    
    Prevents:
    - Email header injection (newlines, carriage returns)
    - Extremely long emails
    - Invalid characters
    """
    if not email or not isinstance(email, str):
        return False
    
    # Length check (RFC 5321: max 320 chars for email address)
    if len(email) > 320:
        return False
    
    # Prevent email header injection attacks
    if '\n' in email or '\r' in email or '\0' in email:
        return False
    
    # Basic format validation (more strict than before)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    
    # Additional checks: no consecutive dots, no leading/trailing dots
    if '..' in email or email.startswith('.') or email.endswith('.'):
        return False
    
    # Ensure @ appears only once
    if email.count('@') != 1:
        return False
    
    return True

def _build_unsubscribe_url(token: str | None) -> str | None:
    """Build full unsubscribe URL from token.

    Uses FRONTEND_URL environment variable (GitHub Pages) if present,
    otherwise falls back to BASE_URL, then relative URL.
    """
    if not token:
        return None

    # Prefer FRONTEND_URL for unsubscribe links (points to GitHub Pages frontend)
    frontend_url = os.getenv("FRONTEND_URL", "").strip()
    if frontend_url:
        # Use hash router format for React Router
        return f"{frontend_url.rstrip('/')}/#/unsubscribe/{token}"
    
    # Fallback to BASE_URL if FRONTEND_URL not set
    base_url = os.getenv("BASE_URL", "").strip()
    if base_url:
        return f"{base_url.rstrip('/')}/unsubscribe/{token}"
    
    # Relative path fallback; still useful in plain-text/preview environments
    return f"/unsubscribe/{token}"


def send_raw_html_email(recipient_email: str, subject: str, html_content: str) -> bool:
    """Send a generic HTML email to a single recipient using Resend API.

    Intended for welcome / transactional emails.
    """
    resend_api_key = os.getenv("RESEND_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL", "ainews@prajwolsubedi.com.np")
    reply_to_email = os.getenv("REPLY_TO_EMAIL", "prajwolsubedi@gmail.com")

    if not resend_api_key:
        root_logger.error("[EMAIL] RESEND_API_KEY not set in environment variables")
        return False

    if not recipient_email:
        root_logger.error("[EMAIL] Recipient email not provided")
        return False

    if not validate_email(recipient_email):
        root_logger.error(f"[EMAIL] Invalid email format: {recipient_email}")
        return False

    try:
        # Set Resend API key
        resend.api_key = resend_api_key

        # Format sender email with display name
        from_email = f"AI News <{sender_email}>" if "@" in sender_email else sender_email
        
        params = {
            "from": from_email,
            "to": [recipient_email],
            "subject": subject,
            "html": html_content,
            "reply_to": reply_to_email,
        }
        
        result = resend.Emails.send(params)
        
        # Resend API returns a dict with 'id' key on success
        if result and isinstance(result, dict) and 'id' in result:
            root_logger.info(f"[EMAIL] Transactional email sent to {recipient_email} (ID: {result['id']})")
            return True
        else:
            root_logger.error(f"[EMAIL] Resend API returned unexpected response: {result}")
            return False
            
    except Exception as e:
        root_logger.error(f"[EMAIL] Error sending transactional email to {recipient_email}: {type(e).__name__}: {e}", exc_info=True)
        return False


def send_email(news_items: list, recipient_email: str, unsubscribe_url: str | None = None):
    """Send HTML email with top news to a single recipient using Resend API."""

    # Email configuration from environment variables
    resend_api_key = os.getenv("RESEND_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL", "ainews@prajwolsubedi.com.np")
    reply_to_email = os.getenv("REPLY_TO_EMAIL", "prajwolsubedi@gmail.com")
    
    if not resend_api_key:
        root_logger.error("[EMAIL] RESEND_API_KEY not set in environment variables")
        return False
    
    if not recipient_email:
        root_logger.error("[EMAIL] Recipient email not provided")
        return False
    
    # Validate email format
    if not validate_email(recipient_email):
        root_logger.error(f"[EMAIL] Invalid email format: {recipient_email}")
        return False
    
    # Check for placeholder domains
    placeholder_domains = ['example.com', 'test.com', 'example.org', 'test.org']
    recipient_domain = recipient_email.split('@')[1].lower() if '@' in recipient_email else ''
    if recipient_domain in placeholder_domains:
        root_logger.error(f"[EMAIL] Placeholder email address: {recipient_email}")
        return False
    
    try:
        # Create HTML content
        html_content = create_html_email(news_items, unsubscribe_url=unsubscribe_url)
        
        # Set Resend API key
        resend.api_key = resend_api_key
        
        # Format sender email with display name
        from_email = f"AI News <{sender_email}>" if "@" in sender_email else sender_email
        
        subject = f"Top AI News - {datetime.now().strftime('%B %d, %Y')}"
        
        params = {
            "from": from_email,
            "to": [recipient_email],
            "subject": subject,
            "html": html_content,
            "reply_to": reply_to_email,
        }
        
        result = resend.Emails.send(params)
        
        # Resend API returns a dict with 'id' key on success
        if result and isinstance(result, dict) and 'id' in result:
            root_logger.info(f"[EMAIL] Email sent to {recipient_email} (ID: {result['id']})")
            return True
        else:
            root_logger.error(f"[EMAIL] Resend API returned unexpected response: {result}")
            return False
            
    except Exception as e:
        root_logger.error(f"[EMAIL] Error sending email to {recipient_email}: {type(e).__name__}: {e}", exc_info=True)
        return False


def send_news_to_all_subscribers(news_items: list) -> bool:
    """Send news email to all active subscribers from the database."""
    root_logger.info("[EMAIL] Starting email sending process")
    
    try:
        subscribers = models.get_all_active_subscribers()
        subscriber_count = len(subscribers) if subscribers else 0
        root_logger.info(f"[EMAIL] Retrieved {subscriber_count} subscribers from database")
    except Exception as e:
        root_logger.error(f"[EMAIL] Error getting subscribers: {type(e).__name__}: {e}", exc_info=True)
        raise

    if not subscribers:
        root_logger.error("[EMAIL] No active subscribers found")
        return False

    root_logger.info(f"[EMAIL] Sending emails to {len(subscribers)} subscribers")
    
    # Check email configuration before starting (Resend API)
    resend_api_key = os.getenv("RESEND_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL", "ainews@prajwolsubedi.com.np")
    
    if not resend_api_key:
        root_logger.error("[EMAIL] RESEND_API_KEY not set in environment variables")
        return False
    
    success_count = 0
    failed_emails = []
    error_details = []
    
    for idx, subscriber in enumerate(subscribers, 1):
        unsubscribe_url = _build_unsubscribe_url(subscriber.unsubscribe_token)
        try:
            if send_email(news_items, subscriber.email, unsubscribe_url=unsubscribe_url):
                success_count += 1
            else:
                failed_emails.append(subscriber.email)
                error_details.append(f"{subscriber.email}: send_email returned False")
        except Exception as e:
            failed_emails.append(subscriber.email)
            error_details.append(f"{subscriber.email}: {str(e)}")
            root_logger.error(f"[EMAIL] Exception sending email to {subscriber.email}: {type(e).__name__}: {e}", exc_info=True)

    root_logger.info(f"[EMAIL] Finished: {success_count}/{len(subscribers)} emails sent successfully")
    
    if failed_emails:
        root_logger.error(f"[EMAIL] Failed to send to {len(failed_emails)}/{len(subscribers)} subscribers")
        root_logger.error(f"[EMAIL] Failed emails (first 5): {failed_emails[:5]}")
        if error_details:
            root_logger.error(f"[EMAIL] Error details (first 3): {error_details[:3]}")
    elif success_count == 0:
        root_logger.error("[EMAIL] No emails sent - all attempts failed")
        root_logger.error("[EMAIL] Check: RESEND_API_KEY, domain verification, rate limits")
    
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
