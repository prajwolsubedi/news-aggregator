"""Centralized configuration for the application."""

import os
from dotenv import load_dotenv

load_dotenv()


# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Flask Configuration
FLASK_ENV = os.getenv("FLASK_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")

# Scheduler Configuration
SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE")
SCHEDULER_LOG_LEVEL = os.getenv("SCHEDULER_LOG_LEVEL", "INFO")

# YouTube Channels to Monitor
YOUTUBE_CHANNELS = [
    "@matthew_berman",
    "@aiDotEngineer",
    "@aiadvantage",
    "@aiexplained-official",
    "@mreflow",
    "@Fireship",
    "@IshanSharma7390",
    "@OpenAI",
    "@anthropic-ai",
    "@google"
]

# News Processing Configuration
TOP_NEWS_COUNT = 11  # Number of top news items to process and send
