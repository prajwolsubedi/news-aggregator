---
name: Automate and Deploy AI News System
overview: Automate the entire news pipeline to run daily at 9am, deploy to Render, create a simple web interface for email subscriptions/unsubscriptions, and simplify all code for maintainability.
todos:
  - id: setup_database
    content: Create database.py with PostgreSQL connection and schema setup (subscribers table)
    status: completed
  - id: create_models
    content: Create models.py with Subscriber model and helper functions
    status: completed
  - id: build_flask_app
    content: "Create app.py with Flask routes: POST /subscribe, GET /unsubscribe/<token>, GET /"
    status: completed
  - id: create_templates
    content: Create templates/index.html with minimal subscription form and unsubscribe page
    status: completed
  - id: update_email_system
    content: Update send_email.py to query database for subscribers, add unsubscribe links, create welcome email
    status: completed
  - id: create_scheduler
    content: Create scheduler.py using APScheduler to run pipeline daily at 9am
    status: completed
  - id: create_pipeline
    content: Create run_pipeline.py to orchestrate all steps sequentially
    status: completed
  - id: simplify_code
    content: Create utils.py with common functions, simplify all existing Python files
    status: completed
  - id: deployment_config
    content: Create render.yaml, Procfile, runtime.txt, migrations/001_init.sql, .env.example
    status: completed
  - id: update_requirements
    content: Update requirements.txt with Flask, APScheduler, psycopg2-binary
    status: completed
  - id: todo-1765820822177-6tkz5v4yl
    content: |-
      check if everything is completed and mange the file structure to follow a design pattern and make code as simple and possible.
      Then explain user how to deploy the project on render.
    status: pending
---

# Automate and Deploy AI News System

## Overview

Transform the current manual pipeline into an automated system that runs daily at 9am, includes a web interface for email subscriptions, and is deployed to Render.

## Current Workflow Analysis

The current pipeline consists of:

1. `check_rss.py` - Fetch RSS news
2. `youtube_fetch.py` - Fetch YouTube videos  
3. `combine_news.py` - Combine sources
4. `rank_news.py` - Rank news with Gemini
5. `process_top_news.py` - Process top news (transcribe/summarize)
6. `send_email.py` - Send email

## Architecture Changes

### 1. Automation & Scheduling

- Create `scheduler.py` that orchestrates the entire pipeline
- Use APScheduler for in-process scheduling (runs at 9am daily)
- Add error handling and logging
- Create `run_pipeline.py` as entry point for scheduled execution

### 2. Web Interface (Flask + Minimal HTML)

- **Backend API** (`app.py`):
  - `POST /subscribe` - Subscribe email
  - `GET /unsubscribe/<token>` - Unsubscribe with token
  - `GET /` - Simple subscription form page
  - Email confirmation on subscription
- **Frontend**: Minimal HTML/CSS/JS form
- **Database**: PostgreSQL for subscribers table (email, subscribed_at, unsubscribe_token, is_active)

### 3. Email Subscription System

- Generate unique unsubscribe tokens (UUID)
- Send welcome/confirmation email on subscription
- Store subscribers in PostgreSQL
- Add unsubscribe link to all news emails
- Update `send_email.py` to send to all active subscribers

### 4. Code Simplification

- Consolidate common functions into `utils.py`
- Simplify error handling patterns
- Remove redundant code
- Add clear docstrings
- Standardize JSON file handling

### 5. Deployment Setup

- Create `render.yaml` for Render deployment
- Add `Procfile` for process management
- Create `runtime.txt` for Python version
- Environment variables setup guide
- Database migration script

## Implementation Plan

### Phase 1: Database & Subscription System

**Files to create/modify:**

- `database.py` - PostgreSQL connection and schema
- `models.py` - Subscriber model
- `app.py` - Flask web app with subscription endpoints
- `templates/index.html` - Minimal subscription form
- `static/style.css` - Simple styling

**Key features:**

- PostgreSQL connection using `psycopg2`
- Subscriber table: `id`, `email`, `subscribed_at`, `unsubscribe_token`, `is_active`
- Email validation
- Token generation for unsubscribe links

### Phase 2: Email System Updates

**Files to modify:**

- `send_email.py` - Add function to get all active subscribers, add unsubscribe link to emails
- `email_templates.py` - Create welcome email template

**Changes:**

- Query database for active subscribers
- Send batch emails
- Include unsubscribe link in footer
- Welcome email on subscription

### Phase 3: Automation Pipeline

**Files to create:**

- `scheduler.py` - Main scheduler using APScheduler
- `run_pipeline.py` - Orchestrates all steps sequentially
- `config.py` - Centralized configuration

**Pipeline flow:**

```
1. Fetch RSS news (check_rss.py)
2. Fetch YouTube videos (youtube_fetch.py)
3. Combine news (combine_news.py)
4. Rank news (rank_news.py)
5. Process top news (process_top_news.py)
6. Send emails to all subscribers (send_email.py)
```

### Phase 4: Code Simplification

**Files to refactor:**

- Extract common JSON loading/saving to `utils.py`
- Simplify error messages
- Consolidate duplicate code
- Add type hints where helpful
- Improve function naming

### Phase 5: Deployment Configuration

**Files to create:**

- `render.yaml` - Render deployment config
- `Procfile` - Process definitions (web + worker)
- `runtime.txt` - Python version
- `migrations/001_init.sql` - Database schema
- `.env.example` - Environment variable template

## File Structure After Implementation

```
.
├── app.py                    # Flask web app
├── scheduler.py              # Daily scheduler
├── run_pipeline.py          # Pipeline orchestrator
├── database.py              # Database connection & queries
├── models.py                # Data models
├── utils.py                 # Common utilities
├── config.py                # Configuration
├── email_templates.py       # Email templates
├── check_rss.py            # (simplified)
├── youtube_fetch.py         # (simplified)
├── combine_news.py          # (simplified)
├── rank_news.py            # (simplified)
├── process_top_news.py     # (simplified)
├── youtube_transcribe.py   # (simplified)
├── send_email.py           # (updated for batch sending)
├── templates/
│   └── index.html          # Subscription form
├── static/
│   └── style.css           # Minimal styling
├── migrations/
│   └── 001_init.sql        # Database schema
├── requirements.txt        # (updated with Flask, APScheduler, psycopg2)
├── render.yaml            # Render config
├── Procfile               # Process file
├── runtime.txt            # Python version
└── .env.example           # Environment template
```

## Key Dependencies to Add

- `flask` - Web framework
- `apscheduler` - Task scheduling
- `psycopg2-binary` - PostgreSQL adapter
- `python-dotenv` - Environment variables (already have)

## Environment Variables Needed

```
# Existing
GEMINI_API_KEY=
YOUTUBE_API_KEY=
SERP_API_KEY=
SENDER_EMAIL=
SENDER_PASSWORD=
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# New
DATABASE_URL=postgresql://...  # Provided by Render
FLASK_ENV=production
SECRET_KEY=...  # For Flask sessions
```

## Deployment Strategy

1. **Web Service**: Flask app (handles subscriptions)
2. **Worker Service**: Scheduled task runner (runs pipeline at 9am)
3. **PostgreSQL**: Database addon on Render

## Testing Considerations

- Test subscription flow locally
- Test unsubscribe flow
- Test pipeline execution
- Verify email sending
- Test database operations

## Security Considerations

- Validate email addresses
- Rate limit subscription endpoint
- Secure unsubscribe tokens
- Sanitize user inputs
- Use environment variables for secrets