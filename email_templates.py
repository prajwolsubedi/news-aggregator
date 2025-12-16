from datetime import datetime
from typing import Optional, Tuple


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


