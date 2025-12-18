import os
import logging
from typing import Tuple, Union
from datetime import datetime, timezone, timedelta, time

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, Response

from core import database, models
from email_templates import get_welcome_email, get_unsubscribe_email, get_welcome_with_news_email
from send_email import validate_email, _build_unsubscribe_url, send_raw_html_email, send_email, load_top_news
from transcription.transcription_jobs import get_pending_jobs, claim_jobs

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv("FLASK_ENV") == "production" else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)

# Secret key for sessions - must be set in production
secret_key = os.getenv("SECRET_KEY")
if not secret_key or secret_key == "change-me-in-production":
    if os.getenv("FLASK_ENV") == "production":
        raise ValueError("SECRET_KEY must be set in production environment")
    logging.warning("Using default SECRET_KEY - not suitable for production")
    secret_key = "change-me-in-production"

app.secret_key = secret_key

_db_initialized = False

# Nepal Standard Time is UTC+5:45
NEPAL_TIMEZONE_OFFSET = timedelta(hours=5, minutes=45)


def _is_after_9am_nepal_time() -> bool:
    """Check if current time is after 9am Nepal Standard Time (UTC+5:45)."""
    utc_now = datetime.now(timezone.utc)
    nepal_time = utc_now + NEPAL_TIMEZONE_OFFSET
    return nepal_time.time() >= time(9, 0)


def _error_response(message: str, status_code: int = 400) -> Tuple[Response, int]:
    """Return a simple JSON error response."""
    return jsonify({"ok": False, "error": message}), status_code


def _success_response(data: dict, status_code: int = 200) -> Tuple[Response, int]:
    """Return a simple JSON success response."""
    payload = {"ok": True}
    payload.update(data)
    return jsonify(payload), status_code


@app.before_request
def ensure_db_initialized() -> None:
    """Ensure database schema exists before handling the first request."""
    global _db_initialized
    if _db_initialized:
        return
    database.init_schema()
    _db_initialized = True


@app.route("/", methods=["GET"])
def index() -> Response:
    """Render the subscription form page using the main template."""
    html = render_template("index.html", mode=None, message=None, message_type=None)
    return Response(html, mimetype="text/html")


@app.route("/subscribe", methods=["POST"])
def subscribe() -> Tuple[Response, int]:
    """Subscribe an email address.

    Accepts either JSON `{ "email": "user@example.com" }`
    or form-encoded `email` from the HTML form.
    """
    email: Union[str, None] = None

    is_json = request.is_json

    if is_json:
        data = request.get_json(silent=True) or {}
        email = data.get("email")
    else:
        email = request.form.get("email")

    if not email:
        if is_json:
            return _error_response("Email is required", 400)
        html = render_template(
            "index.html",
            mode=None,
            message="Email is required.",
            message_type="error",
        )
        return Response(html, mimetype="text/html"), 400

    email = email.strip()
    if not validate_email(email):
        if is_json:
            return _error_response("Invalid email address", 400)
        html = render_template(
            "index.html",
            mode=None,
            message="Please enter a valid email address.",
            message_type="error",
        )
        return Response(html, mimetype="text/html"), 400

    # Check if already subscribed and active
    existing = models.get_subscriber_by_email(email)
    if existing and existing.is_active:
        if is_json:
            return _success_response(
                {"email": existing.email, "is_active": True, "already_subscribed": True},
                200,
            )
        html = render_template(
            "index.html",
            mode=None,
            message="You're already subscribed to AI News.",
            message_type="success",
        )
        return Response(html, mimetype="text/html"), 200

    # Add or reactivate subscriber
    subscriber = models.add_subscriber(email)
    if not subscriber:
        if is_json:
            return _error_response("Unable to subscribe at this time", 500)
        html = render_template(
            "index.html",
            mode=None,
            message="Something went wrong. Please try again later.",
            message_type="error",
        )
        return Response(html, mimetype="text/html"), 500

    # Build unsubscribe URL for welcome email
    unsubscribe_url = _build_unsubscribe_url(subscriber.unsubscribe_token)
    
    # Check if user signed up after 9am Nepal time and send today's news if available
    if _is_after_9am_nepal_time():
        today_news = load_top_news()
        if today_news:
            # Send welcome email with today's daily news
            subject, html_body = get_welcome_with_news_email(unsubscribe_url, today_news)
            send_raw_html_email(subscriber.email, subject, html_body)
        else:
            # No news available yet, send regular welcome email
            subject, html_body = get_welcome_email(unsubscribe_url)
            send_raw_html_email(subscriber.email, subject, html_body)
    else:
        # Before 9am, send regular welcome email
        subject, html_body = get_welcome_email(unsubscribe_url)
        send_raw_html_email(subscriber.email, subject, html_body)

    response_data = {
        "email": subscriber.email,
        "is_active": subscriber.is_active,
    }

    if is_json:
        return _success_response(response_data, 201)

    html = render_template(
        "index.html",
        mode=None,
        message="You're subscribed! Check your inbox for a welcome email.",
        message_type="success",
    )
    return Response(html, mimetype="text/html"), 201


@app.route("/unsubscribe/<token>", methods=["GET"])
def unsubscribe(token: str) -> Response:
    """Unsubscribe using the unique token."""
    if not token:
        return Response("Invalid unsubscribe link.", status=400, mimetype="text/plain")

    # Look up subscriber first so we can both validate and email them
    subscriber = models.get_subscriber_by_token(token)
    if not subscriber or not subscriber.is_active:
        html = render_template(
            "index.html",
            mode=None,
            message="This unsubscribe link is invalid or has already been used.",
            message_type="error",
        )
        return Response(html, mimetype="text/html"), 400

    # Deactivate subscriber
    models.deactivate_subscriber(token)

    # Build link back to the signup page for the confirmation email
    base_url = os.getenv("BASE_URL", "").rstrip("/")
    resubscribe_url = base_url or "/"
    subject, html_body = get_unsubscribe_email(resubscribe_url)
    send_raw_html_email(subscriber.email, subject, html_body)

    html = render_template(
        "index.html",
        mode=None,
        message="You've been unsubscribed. You can subscribe again anytime.",
        message_type="success",
    )
    return Response(html, mimetype="text/html")


@app.route("/api/get-videos", methods=["GET"])
def get_videos():
    """
    Worker endpoint: Returns pending transcription jobs and marks them as CLAIMED.
    Workers call this to get work.
    """
    try:
        worker_id = request.args.get("worker_id", "unknown")
        limit = request.args.get("limit", 5, type=int)
        
        # Ensure limit is valid
        if limit is None or limit < 1:
            limit = 5
        
        # Get pending jobs
        jobs = get_pending_jobs(limit=limit)
        
        # Ensure jobs is a list
        if not isinstance(jobs, list):
            jobs = []
        
        if not jobs:
            return _success_response({"jobs": []})
        
        # Claim the jobs atomically
        job_ids = [job["job_id"] for job in jobs]
        claim_success = claim_jobs(job_ids, worker_id)
        
        # Always return jobs, even if claiming failed (they'll be retried)
        return _success_response({"jobs": jobs})
            
    except Exception as e:
        logging.exception("Error fetching transcription jobs")
        return _error_response(f"Error fetching jobs: {str(e)}", 500)


@app.route("/api/upload-all-transcripts", methods=["POST"])
def upload_all_transcripts() -> Tuple[Response, int]:
    """
    Worker endpoint: Accepts batch transcript uploads from worker.
    Stores transcripts and marks jobs as COMPLETED.
    """
    if not request.is_json:
        return _error_response("Request must be JSON", 400)
    
    data = request.get_json()
    worker_id = data.get("worker_id", "unknown")
    results = data.get("results", [])
    
    if not results:
        return _error_response("No results provided", 400)
    
    try:
        with database.get_db_connection() as conn:
            cursor = conn.cursor()
            success_count = 0
            
            for result in results:
                job_id = result.get("job_id")
                video_id = result.get("video_id")
                transcript = result.get("transcript")
                language = result.get("language", "en")
                duration = result.get("duration", 0)
                
                if not job_id or not video_id or not transcript:
                    continue
                
                try:
                    # Store transcript
                    cursor.execute("""
                        INSERT INTO transcripts
                        (video_id, job_id, transcript, language, duration)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (video_id)
                        DO UPDATE SET
                            transcript = EXCLUDED.transcript,
                            language = EXCLUDED.language,
                            duration = EXCLUDED.duration,
                            job_id = EXCLUDED.job_id
                    """, (video_id, job_id, transcript, language, duration))
                    
                    # Mark job as completed
                    cursor.execute("""
                        UPDATE transcription_jobs
                        SET status = 'COMPLETED',
                            completed_at = %s
                        WHERE job_id = %s
                    """, (datetime.utcnow(), job_id))
                    
                    success_count += 1
                    
                except Exception as e:
                    logging.error(f"Error processing job {job_id}: {e}")
                    # Mark job as failed
                    cursor.execute("""
                        UPDATE transcription_jobs
                        SET status = 'FAILED',
                            error_message = %s
                        WHERE job_id = %s
                    """, (str(e), job_id))
            
            return _success_response({
                "success": True,
                "processed": success_count,
                "total": len(results)
            })
            
    except Exception as e:
        return _error_response(f"Error processing transcripts: {str(e)}", 500)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)


