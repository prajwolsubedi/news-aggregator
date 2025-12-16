import os
from typing import Tuple, Union

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, Response

import database
import models
from email_templates import get_welcome_email, get_unsubscribe_email
from send_email import validate_email, _build_unsubscribe_url, send_raw_html_email


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-me-in-production")

_db_initialized = False


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

    # Build unsubscribe URL for welcome email and send it
    unsubscribe_url = _build_unsubscribe_url(subscriber.unsubscribe_token)
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)


