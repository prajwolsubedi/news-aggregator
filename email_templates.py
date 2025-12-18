from datetime import datetime
from typing import Optional, Tuple, List, Dict


def _unsubscribe_footer(unsubscribe_url: Optional[str]) -> str:
    """Return a small unsubscribe footer HTML snippet if URL is provided."""
    if not unsubscribe_url:
        return ""
    return (
        '<p style="margin-top: 15px; font-size: 12px;">'
        'If you no longer want to receive these emails, you can '
        f'<a href="{unsubscribe_url}">unsubscribe here</a>.'
        "</p>"
    )


def create_welcome_email_html(unsubscribe_url: Optional[str] = None) -> str:
    """Create HTML content for the welcome/confirmation email."""
    current_date = datetime.now().strftime("%B %d, %Y")
    footer_unsubscribe = _unsubscribe_footer(unsubscribe_url)

    # Keep this template simple and lightweight so it's safe for most email clients.
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to AI News Daily</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                background-color: #f5f5f7;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 24px 16px;
            }}
            .card {{
                background-color: #ffffff;
                border-radius: 16px;
                padding: 24px 20px;
                box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
            }}
            h1 {{
                font-size: 24px;
                margin: 0 0 8px 0;
                color: #111827;
            }}
            p {{
                font-size: 14px;
                color: #4b5563;
                line-height: 1.6;
                margin: 8px 0;
            }}
            .pill {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: 999px;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                background: #eef2ff;
                color: #4f46e5;
                margin-bottom: 12px;
                font-weight: 600;
            }}
            .footer {{
                margin-top: 16px;
                font-size: 11px;
                color: #9ca3af;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <div class="pill">AI News Daily</div>
                <h1>Welcome aboard 👋</h1>
                <p>
                    Thanks for subscribing to <strong>AI News Daily</strong> on {current_date}.
                </p>
                <p>
                    A curated summary of the most important AI news and research highlights will land in
                    your inbox once a day. No spam, just signal.
                </p>
                <p>
                    You can unsubscribe at any time using the link in the footer of any email.
                </p>
                {footer_unsubscribe}
                <p style="margin-top: 18px; font-size: 13px; color: #6b7280;">
                    — AI News Daily
                </p>
            </div>
            <div class="footer">
                Sent by AI News Daily · Generated automatically
            </div>
        </div>
    </body>
    </html>
    """
    return html


WELCOME_EMAIL_SUBJECT = "Welcome to AI News Daily"


def get_welcome_email(unsubscribe_url: Optional[str] = None) -> Tuple[str, str]:
    """Return (subject, html) for the welcome email."""
    return WELCOME_EMAIL_SUBJECT, create_welcome_email_html(unsubscribe_url)


def create_unsubscribe_email_html(resubscribe_url: Optional[str] = None) -> str:
    """Create HTML content for the unsubscribe confirmation email."""
    link_html = ""
    if resubscribe_url:
        link_html = (
            f'<p style="margin: 12px 0 0 0; font-size: 14px;">'
            f'If you change your mind, you can subscribe again any time '
            f'<a href="{resubscribe_url}">on this page</a>.'
            f"</p>"
        )

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>You've been unsubscribed</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                background-color: #f9fafb;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 24px 16px;
            }}
            .card {{
                background-color: #ffffff;
                border-radius: 16px;
                padding: 24px 20px;
                box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            }}
            h1 {{
                font-size: 22px;
                margin: 0 0 8px 0;
                color: #111827;
            }}
            p {{
                font-size: 14px;
                color: #4b5563;
                line-height: 1.6;
                margin: 6px 0;
            }}
            .footer {{
                margin-top: 16px;
                font-size: 11px;
                color: #9ca3af;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1>You've been unsubscribed</h1>
                <p>
                    We're sorry to see you go. You will no longer receive AI News Daily emails at this address.
                </p>
                {link_html}
            </div>
            <div class="footer">
                Sent by AI News Daily · This is an automated message
            </div>
        </div>
    </body>
    </html>
    """
    return html


UNSUBSCRIBE_EMAIL_SUBJECT = "You've been unsubscribed from AI News Daily"


def get_unsubscribe_email(resubscribe_url: Optional[str] = None) -> Tuple[str, str]:
    """Return (subject, html) for the unsubscribe confirmation email."""
    return UNSUBSCRIBE_EMAIL_SUBJECT, create_unsubscribe_email_html(resubscribe_url)


def get_youtube_thumbnail(video_id: str) -> str:
    """Get YouTube thumbnail URL from video ID."""
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"


def create_welcome_with_news_email_html(unsubscribe_url: Optional[str], news_items: List[Dict]) -> str:
    """Create HTML content for welcome email that includes today's daily news.
    
    Args:
        unsubscribe_url: Optional unsubscribe URL
        news_items: List of news item dicts with keys: title, summary, source_link, source, published_at, etc.
    """
    current_date = datetime.now().strftime("%B %d, %Y")
    footer_unsubscribe = _unsubscribe_footer(unsubscribe_url)
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to AI News Daily - Today's News</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                line-height: 1.6;
            }}
            
            .email-container {{
                max-width: 700px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }}
            
            .welcome-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            
            .welcome-header h1 {{
                font-size: 32px;
                font-weight: 700;
                margin-bottom: 10px;
            }}
            
            .welcome-header p {{
                font-size: 16px;
                opacity: 0.9;
                margin-top: 10px;
            }}
            
            .welcome-message {{
                padding: 30px;
                background: #f8f9fa;
                border-bottom: 2px solid #e2e8f0;
            }}
            
            .welcome-message h2 {{
                font-size: 22px;
                color: #2d3748;
                margin-bottom: 15px;
            }}
            
            .welcome-message p {{
                font-size: 15px;
                color: #4a5568;
                line-height: 1.7;
                margin-bottom: 10px;
            }}
            
            .content {{
                padding: 40px 30px;
            }}
            
            .news-item {{
                background: #f8f9fa;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 25px;
                border-left: 4px solid #667eea;
                transition: all 0.3s ease;
            }}
            
            .news-item:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
                border-left-color: #764ba2;
            }}
            
            .news-header {{
                display: flex;
                align-items: flex-start;
                gap: 20px;
                margin-bottom: 15px;
            }}
            
            .thumbnail {{
                width: 300px;
                height: 150px;
                border-radius: 10px;
                object-fit: cover;
                flex-shrink: 0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}
            
            .news-info {{
                flex: 1;
            }}
            
            .source-badge {{
                display: inline-block;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                margin-bottom: 10px;
            }}
            
            .source-website {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            
            .source-youtube {{
                background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
                color: white;
            }}
            
            .news-title {{
                font-size: 20px;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 12px;
                line-height: 1.4;
            }}
            
            .news-link {{
                display: inline-block;
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
                font-size: 14px;
            }}
            
            .news-summary {{
                color: #4a5568;
                font-size: 15px;
                line-height: 1.7;
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #e2e8f0;
            }}
            
            .news-meta {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 15px;
                font-size: 13px;
                color: #718096;
            }}
            
            .footer {{
                background: #f8f9fa;
                padding: 30px;
                text-align: center;
                color: #718096;
                font-size: 14px;
            }}
            
            @media (max-width: 600px) {{
                .news-header {{
                    flex-direction: column;
                }}
                
                .thumbnail {{
                    width: 100%;
                    height: 200px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="welcome-header">
                <h1>Welcome to AI News Daily 👋</h1>
                <p>{current_date}</p>
            </div>
            
            <div class="welcome-message">
                <h2>Thanks for signing up!</h2>
                <p>Here's the daily news you missed today:</p>
                <p style="margin-top: 10px; font-size: 14px; color: #6b7280;">
                    You'll receive a curated summary of the most important AI news and research highlights 
                    in your inbox once a day. No spam, just signal.
                </p>
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
        
        html += f"""
                <div class="news-item">
                    <div class="news-header">
                        {thumbnail_html if thumbnail_html else ''}
                        <div class="news-info">
                            <span class="source-badge {source_class}">{source_label}</span>
                            <h2 class="news-title">{title}</h2>
                            <a href="{source_link}" target="_blank" class="news-link">Read Full Article →</a>
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
    
    html += """
            </div>
            
            <div class="footer">
                <p>Generated by AI News Aggregator</p>
                <p style="margin-top: 10px; font-size: 12px;">Stay updated with the latest AI news and developments</p>
                """ + footer_unsubscribe + """
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


WELCOME_WITH_NEWS_EMAIL_SUBJECT = "Welcome to AI News Daily - Here's Today's News"


def get_welcome_with_news_email(unsubscribe_url: Optional[str], news_items: List[Dict]) -> Tuple[str, str]:
    """Return (subject, html) for welcome email with today's daily news.
    
    Args:
        unsubscribe_url: Optional unsubscribe URL
        news_items: List of news item dicts
    """
    return WELCOME_WITH_NEWS_EMAIL_SUBJECT, create_welcome_with_news_email_html(unsubscribe_url, news_items)


