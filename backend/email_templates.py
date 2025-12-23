from datetime import datetime
from typing import Optional, Tuple, List, Dict


def _unsubscribe_footer(unsubscribe_url: Optional[str]) -> str:
    """Return a small unsubscribe footer HTML snippet if URL is provided."""
    if not unsubscribe_url:
        return ""
    return (
        '<p style="margin: 16px 0 0 0; font-size: 13px; color: #a1a1aa;">'
        f'<a href="{unsubscribe_url}" style="color: #71717a; text-decoration: underline;">Unsubscribe</a> from these emails'
        '</p>'
    )


def create_welcome_email_html(unsubscribe_url: Optional[str] = None) -> str:
    """Create HTML content for the welcome/confirmation email."""
    current_date = datetime.now().strftime("%B %d, %Y")
    footer_unsubscribe = _unsubscribe_footer(unsubscribe_url)

    html = f"""
<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Welcome to AI News Digest</title>
    <style type="text/css">
        body, table, td, p, a {{
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}
        body {{
            margin: 0 !important;
            padding: 0 !important;
            background-color: #f4f4f5;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }}
        a {{
            color: #3b82f6;
            text-decoration: none;
        }}
        @media screen and (max-width: 600px) {{
            .mobile-full-width {{
                width: 100% !important;
            }}
            .mobile-padding {{
                padding: 32px 24px !important;
            }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f5;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f4f4f5;">
        <tr>
            <td align="center" style="padding: 40px 16px;">
                
                <!-- Main container -->
                <table role="presentation" class="mobile-full-width" width="560" cellspacing="0" cellpadding="0" border="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%); padding: 40px 32px; text-align: center;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto;">
                                <tr>
                                    <td style="padding-right: 10px;" valign="middle">
                                        <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); border-radius: 8px; text-align: center;">
                                            <span style="font-size: 18px; line-height: 36px; display: block;">✦</span>
                                        </div>
                                    </td>
                                    <td valign="middle">
                                        <span style="font-size: 18px; font-weight: 700; color: #ffffff; letter-spacing: -0.3px;">AI News</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td class="mobile-padding" style="padding: 40px 40px 32px 40px;">
                            <!-- Welcome icon -->
                            <div style="width: 56px; height: 56px; background-color: #f0fdf4; border-radius: 50%; text-align: center; margin-bottom: 24px;">
                                <span style="font-size: 28px; line-height: 56px; display: block;">👋</span>
                            </div>
                            
                            <h1 style="margin: 0 0 16px 0; font-size: 24px; font-weight: 700; color: #18181b; line-height: 1.3;">
                                Welcome to AI News Digest
                            </h1>
                            
                            <p style="margin: 0 0 16px 0; font-size: 15px; color: #52525b; line-height: 1.65;">
                                Thanks for subscribing on <strong style="color: #18181b;">{current_date}</strong>.
                            </p>
                            
                            <p style="margin: 0 0 16px 0; font-size: 15px; color: #52525b; line-height: 1.65;">
                                You'll receive a curated summary of the most important AI news and research highlights in your inbox once a day. No spam, just signal.
                            </p>
                            
                            <p style="margin: 0; font-size: 15px; color: #52525b; line-height: 1.65;">
                                You can unsubscribe at any time using the link in the footer of any email.
                            </p>
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
                        <td style="padding: 24px 40px 32px 40px; text-align: center;">
                            <p style="margin: 0; font-size: 13px; color: #a1a1aa;">
                                Curated with ❤️ by <strong style="color: #71717a;">AI News Digest</strong>
                            </p>
                            {footer_unsubscribe}
                        </td>
                    </tr>
                    
                </table>
                
                <!-- Bottom text -->
                <table role="presentation" width="560" class="mobile-full-width" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                        <td style="padding: 20px 40px; text-align: center;">
                            <p style="margin: 0; font-size: 12px; color: #a1a1aa;">
                                © {datetime.now().year} AI News Digest
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
    return html


WELCOME_EMAIL_SUBJECT = "Welcome to AI News Digest"


def get_welcome_email(unsubscribe_url: Optional[str] = None) -> Tuple[str, str]:
    """Return (subject, html) for the welcome email."""
    return WELCOME_EMAIL_SUBJECT, create_welcome_email_html(unsubscribe_url)


def create_unsubscribe_email_html(resubscribe_url: Optional[str] = None) -> str:
    """Create HTML content for the unsubscribe confirmation email."""
    link_html = ""
    if resubscribe_url:
        link_html = (
            '<p style="margin: 20px 0 0 0; font-size: 15px; color: #52525b; line-height: 1.65;">'
            'Changed your mind? You can '
            f'<a href="{resubscribe_url}" style="color: #3b82f6; text-decoration: underline;">subscribe again</a> '
            'anytime.'
            '</p>'
        )

    html = f"""
<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>You've been unsubscribed</title>
    <style type="text/css">
        body, table, td, p, a {{
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}
        body {{
            margin: 0 !important;
            padding: 0 !important;
            background-color: #f4f4f5;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }}
        @media screen and (max-width: 600px) {{
            .mobile-full-width {{
                width: 100% !important;
            }}
            .mobile-padding {{
                padding: 32px 24px !important;
            }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f5;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f4f4f5;">
        <tr>
            <td align="center" style="padding: 40px 16px;">
                
                <!-- Main container -->
                <table role="presentation" class="mobile-full-width" width="560" cellspacing="0" cellpadding="0" border="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%); padding: 40px 32px; text-align: center;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto;">
                                <tr>
                                    <td style="padding-right: 10px;" valign="middle">
                                        <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); border-radius: 8px; text-align: center;">
                                            <span style="font-size: 18px; line-height: 36px; display: block;">✦</span>
                                        </div>
                                    </td>
                                    <td valign="middle">
                                        <span style="font-size: 18px; font-weight: 700; color: #ffffff; letter-spacing: -0.3px;">AI News</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td class="mobile-padding" style="padding: 40px 40px 32px 40px;">
                            <!-- Icon -->
                            <div style="width: 56px; height: 56px; background-color: #fef2f2; border-radius: 50%; text-align: center; margin-bottom: 24px;">
                                <span style="font-size: 28px; line-height: 56px; display: block;">👋</span>
                            </div>
                            
                            <h1 style="margin: 0 0 16px 0; font-size: 24px; font-weight: 700; color: #18181b; line-height: 1.3;">
                                You've been unsubscribed
                            </h1>
                            
                            <p style="margin: 0; font-size: 15px; color: #52525b; line-height: 1.65;">
                                We're sorry to see you go. You will no longer receive AI News Digest emails at this address.
                            </p>
                            
                            {link_html}
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
                        <td style="padding: 24px 40px 32px 40px; text-align: center;">
                            <p style="margin: 0; font-size: 13px; color: #a1a1aa;">
                                This is an automated message from <strong style="color: #71717a;">AI News Digest</strong>
                            </p>
                        </td>
                    </tr>
                    
                </table>
                
                <!-- Bottom text -->
                <table role="presentation" width="560" class="mobile-full-width" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                        <td style="padding: 20px 40px; text-align: center;">
                            <p style="margin: 0; font-size: 12px; color: #a1a1aa;">
                                © {datetime.now().year} AI News Digest
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
    return html


UNSUBSCRIBE_EMAIL_SUBJECT = "You've been unsubscribed from AI News Digest"


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
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="x-apple-disable-message-reformatting">
    <title>Welcome to AI News Digest - Today's News</title>
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
        body, table, td, p, a, li, blockquote {{
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}
        table, td {{
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }}
        img {{
            -ms-interpolation-mode: bicubic;
            border: 0;
            height: auto;
            line-height: 100%;
            outline: none;
            text-decoration: none;
        }}
        body {{
            margin: 0 !important;
            padding: 0 !important;
            background-color: #f4f4f5;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }}
        a {{
            color: #3b82f6;
            text-decoration: none;
        }}
        @media screen and (max-width: 600px) {{
            .mobile-full-width {{
                width: 100% !important;
                max-width: 100% !important;
            }}
            .mobile-padding {{
                padding-left: 20px !important;
                padding-right: 20px !important;
            }}
            .content-cell {{
                padding: 24px 20px !important;
            }}
            .news-card {{
                margin-bottom: 16px !important;
            }}
            .header-title {{
                font-size: 24px !important;
            }}
            .video-thumbnail {{
                width: 100% !important;
                height: auto !important;
            }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f5;">
    <!-- Preview text -->
    <div style="display: none; max-height: 0; overflow: hidden;">
        Welcome! Here's today's AI news digest curated just for you
        &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
    </div>
    
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
                                        <p style="margin: 0 0 6px 0; font-size: 13px; font-weight: 500; color: #94a3b8; text-transform: uppercase; letter-spacing: 2px;">
                                            Daily Digest
                                        </p>
                                        <p style="margin: 0; font-size: 15px; color: #64748b; font-weight: 400;">
                                            {current_date}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Welcome message -->
                    <tr>
                        <td style="padding: 32px 40px; background-color: #f0fdf4; border-bottom: 1px solid #dcfce7;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td width="48" valign="top" style="padding-right: 16px;">
                                        <div style="width: 40px; height: 40px; background-color: #ffffff; border-radius: 50%; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                                            <span style="font-size: 20px; line-height: 40px; display: block;">👋</span>
                                        </div>
                                    </td>
                                    <td valign="top">
                                        <h2 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 600; color: #166534;">
                                            Welcome to AI News Digest!
                                        </h2>
                                        <p style="margin: 0; font-size: 14px; color: #15803d; line-height: 1.5;">
                                            Thanks for signing up. Here's today's top AI news — you'll receive these daily.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Intro section -->
                    <tr>
                        <td class="content-cell" style="padding: 28px 40px 20px 40px;">
                            <p style="margin: 0; font-size: 15px; color: #52525b; line-height: 1.6;">
                                Today's top stories, carefully curated to keep you informed about the latest developments in AI.
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
                                        <img src="{thumbnail_url}" alt="Video thumbnail" class="video-thumbnail" width="520" style="width: 100%; height: auto; display: block; border-radius: 8px;">
                                    </a>
                                </td>
                            </tr>
                """
        
        html += f"""
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
    
    html += f"""
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
                            {footer_unsubscribe}
                        </td>
                    </tr>
                    
                </table>
                
                <!-- Bottom branding -->
                <table role="presentation" width="600" class="mobile-full-width" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                        <td style="padding: 24px 40px; text-align: center;">
                            <p style="margin: 0; font-size: 12px; color: #a1a1aa;">
                                © {datetime.now().year} AI News Digest. All rights reserved.
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
    
    return html


WELCOME_WITH_NEWS_EMAIL_SUBJECT = "Welcome to AI News Digest - Here's Today's News"


def get_welcome_with_news_email(unsubscribe_url: Optional[str], news_items: List[Dict]) -> Tuple[str, str]:
    """Return (subject, html) for welcome email with today's daily news.
    
    Args:
        unsubscribe_url: Optional unsubscribe URL
        news_items: List of news item dicts
    """
    return WELCOME_WITH_NEWS_EMAIL_SUBJECT, create_welcome_with_news_email_html(unsubscribe_url, news_items)
