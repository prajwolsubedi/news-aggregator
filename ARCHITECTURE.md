# AI Newsletter System - Complete Architecture & Workflow Documentation

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Complete Workflow](#complete-workflow)
- [Data Flow](#data-flow)
- [Component Details](#component-details)
- [Scheduling & Automation](#scheduling--automation)
- [Database Schema](#database-schema)
- [Deployment Architecture](#deployment-architecture)

---

## Project Overview

This is an **automated AI-powered newsletter system** that:

1. **Fetches** AI-related news from RSS feeds and YouTube channels
2. **Ranks** content using Google Gemini AI based on importance
3. **Transcribes** YouTube videos using local GPU-accelerated Whisper
4. **Generates** summaries using AI
5. **Sends** curated daily newsletters to subscribers via email

The system runs **twice daily** (morning and evening) to deliver fresh AI news to subscribers.

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (GitHub Pages)                   │
│  - React/TypeScript landing page                                 │
│  - Subscription form                                             │
│  - Unsubscribe functionality                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API (Render.com)                      │
│  - Flask application                                             │
│  - PostgreSQL database (Neon)                                    │
│  - News fetching (RSS + YouTube)                                 │
│  - AI ranking (Google Gemini)                                   │
│  - Email sending (Resend API)                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              LOCAL GPU WORKER (Your Computer)                    │
│  - YouTube audio download (yt-dlp)                               │
│  - Whisper transcription (faster-whisper + CUDA)                │
│  - Scheduled at 8:30 AM daily                                   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              GITHUB ACTIONS (Scheduler)                          │
│  - Preprocessing trigger (8:30 AM NPT)                          │
│  - Pipeline trigger (9:00 AM NPT)                                │
└─────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

1. **Frontend** (`server/docs/`)

   - React + TypeScript + Vite
   - Hosted on GitHub Pages
   - Handles user subscriptions

2. **Backend** (`server/backend/`)

   - Flask REST API
   - Deployed on Render.com
   - Manages all business logic

3. **Worker** (`workers/`)

   - Local Python script
   - Runs on your GPU-enabled machine
   - Handles video transcription

4. **Scheduler** (`.github/workflows/`)

   - GitHub Actions workflows
   - Triggers backend endpoints at scheduled times

5. **Database** (Neon PostgreSQL)
   - Stores subscribers, news, transcripts
   - Managed by Neon cloud service

---

## Technology Stack

### Frontend

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: CSS (custom)
- **Hosting**: GitHub Pages

### Backend

- **Framework**: Flask (Python)
- **Database**: PostgreSQL (Neon)
- **AI Services**:
  - Google Gemini API (for ranking and summarization)
  - YouTube Data API v3 (for video fetching)
- **Email Service**: Resend API
- **RSS Parsing**: feedparser
- **Hosting**: Render.com

### Worker

- **Transcription**: faster-whisper (Whisper model)
- **Model**: distil-large-v3 (optimized for speed)
- **GPU Acceleration**: CUDA
- **Download**: yt-dlp
- **Scheduling**: Windows Task Scheduler / Cron

### Infrastructure

- **CI/CD**: GitHub Actions
- **Database**: Neon PostgreSQL (serverless)
- **Version Control**: Git + GitHub

---

## Complete Workflow

### Daily Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 8:30 AM NPT (02:45 UTC) - PREPROCESSING PHASE                  │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ GitHub Actions: trigger-preprocess.yml                          │
│ → POST /internal/run-preprocess                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Backend: preprocess_jobs.py                                    │
│                                                                 │
│ Step 1: Fetch RSS News                                          │
│   - Parse Techmeme RSS feed                                     │
│   - Filter AI-related news from last 24 hours                  │
│                                                                 │
│ Step 2: Fetch YouTube Videos                                    │
│   - Query YouTube API for configured channels                   │
│   - Get videos published in last 24 hours                       │
│                                                                 │
│ Step 3: Combine All Sources                                     │
│   - Merge RSS news + YouTube videos                             │
│   - Assign sequential IDs                                       │
│                                                                 │
│ Step 4: Rank with Gemini AI                                     │
│   - Send all news titles to Gemini                             │
│   - Get importance scores (1-100)                              │
│   - Select top 10 most important items                          │
│                                                                 │
│ Step 5: Store Ranked News                                       │
│   - Save top 10 to daily_ranked_news table                      │
│                                                                 │
│ Step 6: Create Transcription Jobs                               │
│   - For each YouTube video in top 10                            │
│   - Create job in transcription_jobs table                      │
│   - Status: PENDING                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8:30 AM NPT - LOCAL WORKER STARTS                              │
│ (Scheduled via Windows Task Scheduler)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Worker: worker.py                                               │
│                                                                 │
│ Step 1: Fetch Jobs                                              │
│   - GET /api/get-videos                                         │
│   - Server returns batch of PENDING jobs (max 10)                │
│   - Server marks jobs as CLAIMED                                │
│                                                                 │
│ Step 2: Download Audio                                          │
│   - For each video_id:                                          │
│     * Use yt-dlp to download audio only                         │
│     * Save to ./downloads/{video_id}.mp3                        │
│                                                                 │
│ Step 3: Load Whisper Model                                      │
│   - Load distil-large-v3 model once                            │
│   - Use CUDA for GPU acceleration                               │
│                                                                 │
│ Step 4: Transcribe Videos                                        │
│   - For each downloaded audio:                                  │
│     * Run Whisper transcription                                 │
│     * Generate full transcript text                             │
│                                                                 │
│ Step 5: Upload Transcripts                                      │
│   - POST /api/upload-all-transcripts                            │
│   - Send all results in one batch                              │
│   - Server stores transcripts in database                       │
│   - Server marks jobs as COMPLETED                              │
│                                                                 │
│ Step 6: Cleanup                                                 │
│   - Delete local audio files                                    │
│   - Exit with summary                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9:00 AM NPT (03:15 UTC) - PIPELINE PHASE                       │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ GitHub Actions: trigger-pipeline.yml                            │
│ → POST /internal/run-pipeline                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Backend: run_pipeline.py                                        │
│                                                                 │
│ Step 1: Load Ranked News                                        │
│   - Read top 10 from daily_ranked_news table                    │
│   - Ordered by rank (1-10)                                      │
│                                                                 │
│ Step 2: Process Each Item                                        │
│   For Website News:                                             │
│     - Use stored summary from RSS                                │
│                                                                 │
│   For YouTube Videos:                                           │
│     - Look up transcript from transcripts table                 │
│     - If transcript exists:                                     │
│       * Send to Gemini for summarization                        │
│       * Generate 2-3 paragraph summary                           │
│     - If transcript missing:                                    │
│       * Use placeholder: "Transcription pending"                 │
│                                                                 │
│ Step 3: Save Final Issue                                         │
│   - Store processed news in daily_top_news table                │
│   - JSON format with all summaries                              │
│                                                                 │
│ Step 4: Send Newsletter                                         │
│   - Get all active subscribers from database                     │
│   - For each subscriber:                                        │
│     * Generate HTML email template                              │
│     * Include top 10 news items with summaries                  │
│     * Send via Resend API                                       │
│   - Log success/failure for each email                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. News Collection Flow

```
RSS Feed (Techmeme)                    YouTube Channels
     │                                        │
     │ feedparser.parse()                    │ YouTube API v3
     │                                        │
     ▼                                        ▼
┌─────────────────┐                  ┌─────────────────┐
│  RSS News       │                  │ YouTube Videos  │
│  - Title        │                  │ - Title         │
│  - Link         │                  │ - Video ID      │
│  - Summary      │                  │ - Published At  │
│  - Published At │                  │ - Channel Name  │
└────────┬────────┘                  └────────┬────────┘
         │                                     │
         └──────────────┬──────────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │ combine_news()  │
              │ - Merge sources │
              │ - Assign IDs    │
              └────────┬─────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Combined News   │
              │ (in-memory)     │
              └─────────────────┘
```

### 2. Ranking Flow

```
Combined News (All Sources)
         │
         ▼
┌────────────────────────────┐
│ prepare_news_for_ranking()│
│ - Extract titles + IDs     │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ rank_news_with_gemini()    │
│                            │
│ Prompt to Gemini:          │
│ "Rank these AI news titles │
│  by importance (1-100)"    │
│                            │
│ Response:                  │
│ [                         │
│   {id, source, score,      │
│    reason}, ...            │
│ ]                         │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Top 10 Ranked Items        │
│ - Sorted by score          │
│ - Stored in database       │
└────────────────────────────┘
```

### 3. Transcription Flow

```
Top 10 Ranked News
         │
         │ Filter YouTube videos
         ▼
┌────────────────────────────┐
│ transcription_jobs table   │
│ - video_id                 │
│ - status: PENDING          │
└────────────┬───────────────┘
             │
             │ Worker: GET /api/get-videos
             ▼
┌────────────────────────────┐
│ Worker receives jobs       │
│ - Max 10 per batch         │
└────────────┬───────────────┘
             │
             │ For each video_id:
             ▼
┌────────────────────────────┐
│ yt-dlp downloads audio      │
│ → ./downloads/{video_id}.mp3│
└────────────┬───────────────┘
             │
             │ Load Whisper model (once)
             ▼
┌────────────────────────────┐
│ Whisper transcribes         │
│ - Model: distil-large-v3   │
│ - Device: CUDA (GPU)       │
│ - Output: Full transcript  │
└────────────┬───────────────┘
             │
             │ POST /api/upload-all-transcripts
             ▼
┌────────────────────────────┐
│ transcripts table          │
│ - video_id                 │
│ - transcript (full text)   │
│ - job_id                   │
└────────────────────────────┘
```

### 4. Newsletter Generation Flow

```
daily_ranked_news (Top 10)
         │
         ▼
┌────────────────────────────┐
│ build_issue_from_ranked_  │
│ news()                     │
│                            │
│ For each item:             │
│                            │
│ Website:                   │
│   - Use stored summary     │
│                            │
│ YouTube:                   │
│   - Look up transcript      │
│   - Summarize with Gemini  │
│   - Generate 2-3 paragraphs │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Processed News Items        │
│ - Title                     │
│ - Source link               │
│ - Summary                   │
└────────────┬───────────────┘
             │
             │ Save to daily_top_news
             ▼
┌────────────────────────────┐
│ Generate HTML Email         │
│ - Template with all items   │
│ - Styling                   │
└────────────┬───────────────┘
             │
             │ For each subscriber
             ▼
┌────────────────────────────┐
│ Resend API                  │
│ - Send email                │
│ - Track delivery            │
└────────────────────────────┘
```

---

## Component Details

### Backend Components

#### 1. News Fetching (`server/backend/news/`)

**RSS Fetcher** (`check_rss.py`):

- Parses Techmeme RSS feed
- Filters AI-related news using keyword matching
- Extracts: title, link, summary, published date
- Returns news from last 24 hours

**YouTube Fetcher** (`youtube_fetch.py`):

- Uses YouTube Data API v3
- Searches channels by username/handle
- Fetches videos published in last 24 hours
- Extracts: title, video_id, video_link, published date

**News Combiner** (`combine_news.py`):

- Merges RSS and YouTube sources
- Assigns sequential IDs
- Adds source metadata ("website" or "youtube")
- Saves to JSON (for debugging)

#### 2. AI Ranking (`server/backend/ranking/`)

**Ranking Module** (`rank_news.py`):

- Prepares news titles for Gemini
- Sends structured prompt to Gemini API
- Uses JSON schema for structured response
- Returns importance scores (1-100) with reasoning
- Sorts by score and selects top N

**Model Used**:

- Default: `gemini-2.5-flash-lite` (free tier)
- Configurable via `GEMINI_MODEL` env var

#### 3. Transcription Management (`server/backend/transcription/`)

**Job Creation** (`transcription_jobs.py`):

- Creates transcription jobs for YouTube videos
- Stores in `transcription_jobs` table
- Status: PENDING → CLAIMED → COMPLETED
- Handles job claiming and completion

**API Endpoints**:

- `GET /api/get-videos`: Returns batch of pending jobs
- `POST /api/upload-all-transcripts`: Receives transcription results

#### 4. Pipeline Orchestration

**Preprocessing** (`preprocess_jobs.py`):

- Runs at 8:30 AM NPT
- Fetches and combines all news
- Ranks with Gemini (single ranking step)
- Stores top 10 in database
- Creates transcription jobs

**Main Pipeline** (`run_pipeline.py`):

- Runs at 9:00 AM NPT
- Loads ranked news from database
- Joins with transcripts
- Generates summaries
- Sends newsletters

**News Processing** (`process_top_news.py`):

- Processes ranked items
- Handles website summaries
- Summarizes YouTube transcripts
- Saves final issue

#### 5. Email System (`send_email.py`)

- Generates HTML email templates
- Uses Resend API for delivery
- Handles unsubscribe links
- Tracks delivery status

### Worker Components (`workers/`)

#### 1. Main Worker (`worker.py`)

- Orchestrates batch processing
- Fetches jobs from server
- Coordinates download → transcribe → upload
- Handles errors and cleanup

#### 2. HTTP Client (`http_client.py`)

- Communicates with backend API
- Handles authentication (Bearer token)
- Retries on failure
- Uploads batch results

#### 3. Downloader (`downloader.py`)

- Uses yt-dlp for audio download
- Downloads audio-only format
- Saves to local directory
- Handles download errors

#### 4. Transcriber (`transcriber.py`)

- Wraps faster-whisper library
- Loads Whisper model (lazy loading)
- Uses CUDA for GPU acceleration
- Normalizes transcript text
- Returns structured results

#### 5. Configuration (`config.py`)

- Centralized configuration
- Environment variable management
- Default values
- Worker identification

---

## Scheduling & Automation

### GitHub Actions Workflows

#### 1. Preprocessing Workflow (`.github/workflows/trigger-preprocess.yml`)

**Schedule**: 8:30 AM NPT (02:45 UTC) daily

**Actions**:

1. Runs on `ubuntu-latest` runner
2. Makes HTTP POST to `/internal/run-preprocess`
3. Includes `X-Cron-Token` header for authentication
4. Can be manually triggered via `workflow_dispatch`

**Configuration**:

- `CRON_SECRET`: Secret token (GitHub Secrets)
- `RENDER_BASE_URL`: Backend API URL (GitHub Secrets)

#### 2. Pipeline Workflow (`.github/workflows/trigger-pipeline.yml`)

**Schedule**: 9:00 AM NPT (03:15 UTC) daily

**Actions**:

1. Runs on `ubuntu-latest` runner
2. Makes HTTP POST to `/internal/run-pipeline`
3. Includes `X-Cron-Token` header for authentication
4. Can be manually triggered via `workflow_dispatch`

**Configuration**:

- Same secrets as preprocessing workflow

### Local Worker Scheduling

**Schedule**: 8:30 AM NPT daily (Windows Task Scheduler)

**Setup**:

1. Open Windows Task Scheduler
2. Create basic task: "Whisper Worker Daily"
3. Trigger: Daily at 8:30 AM
4. Action: Run Python script
   - Program: `C:\path\to\python.exe`
   - Arguments: `worker.py`
   - Start in: Project directory
5. Add environment variables:
   - `WORKER_API_TOKEN`
   - `SERVER_BASE_URL` (optional)

**Alternative**: Use cron (Linux/Mac) or Python scheduler script

### Time Zone Notes

- **NPT (Nepal Standard Time)**: UTC+5:45
- **8:30 AM NPT** = **02:45 UTC**
- **9:00 AM NPT** = **03:15 UTC**

---

## Database Schema

### Database: Neon PostgreSQL

#### 1. `subscribers` Table

Stores newsletter subscribers.

```sql
CREATE TABLE subscribers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    subscribed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    unsubscribe_token VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes**:

- `idx_subscribers_email` on `email`
- `idx_subscribers_token` on `unsubscribe_token`
- `idx_subscribers_active` on `is_active`

#### 2. `transcription_jobs` Table

Manages YouTube video transcription jobs.

```sql
CREATE TABLE transcription_jobs (
    job_id VARCHAR(255) PRIMARY KEY,
    video_id VARCHAR(255) NOT NULL,
    video_url TEXT NOT NULL,
    video_title TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    claimed_at TIMESTAMP,
    completed_at TIMESTAMP,
    claimed_by VARCHAR(255),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0
);
```

**Status Flow**: PENDING → CLAIMED → COMPLETED

**Indexes**:

- `idx_transcription_jobs_status` on `status`
- `idx_transcription_jobs_created_at` on `created_at`
- `idx_transcription_jobs_video_id` on `video_id`

#### 3. `transcripts` Table

Stores completed video transcripts.

```sql
CREATE TABLE transcripts (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(255) UNIQUE NOT NULL,
    job_id VARCHAR(255),
    transcript TEXT NOT NULL,
    language VARCHAR(10),
    duration INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES transcription_jobs(job_id)
);
```

**Indexes**:

- `idx_transcripts_video_id` on `video_id`
- `idx_transcripts_job_id` on `job_id`

#### 4. `daily_ranked_news` Table

Stores top 10 ranked news items per day (before transcription).

```sql
CREATE TABLE daily_ranked_news (
    id SERIAL PRIMARY KEY,
    issue_date DATE NOT NULL,
    rank INTEGER NOT NULL,
    source VARCHAR(20) NOT NULL,
    news_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    published_at TEXT,
    source_link TEXT,
    video_id TEXT,
    summary TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(issue_date, rank)
);
```

**Indexes**:

- `idx_daily_ranked_news_issue_date` on `issue_date`
- `idx_daily_ranked_news_rank` on `(issue_date, rank)`

#### 5. `daily_top_news` Table

Stores final processed newsletter issue per day.

```sql
CREATE TABLE daily_top_news (
    id SERIAL PRIMARY KEY,
    issue_date DATE NOT NULL,
    top_items_json JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes**:

- `idx_daily_top_news_issue_date` on `issue_date` (UNIQUE)
- `idx_daily_top_news_created_at` on `created_at`

---

## Deployment Architecture

### Frontend Deployment (GitHub Pages)

**Location**: `server/docs/`

**Build Process**:

1. Vite builds React app
2. GitHub Actions deploys to `gh-pages` branch
3. Served via GitHub Pages

**Configuration**:

- `CNAME` file for custom domain (optional)
- `vite.config.ts` sets base path
- API URL configured in `services/api.ts`

### Backend Deployment (Render.com)

**Location**: `server/backend/`

**Deployment Method**: Render Blueprint (`render.yaml`)

**Services Created**:

1. **Web Service** (`ai-news-web`):
   - Flask application
   - Auto-deploys from GitHub
   - Environment variables configured in Render dashboard

**Database**:

- **PostgreSQL** (Neon):
  - Serverless PostgreSQL
  - Auto-scaling
  - Connection string in `DATABASE_URL`

**Environment Variables** (Render Dashboard):

- `DATABASE_URL` - Neon PostgreSQL connection string
- `RESEND_API_KEY` - Resend email API key
- `SENDER_EMAIL` - Newsletter sender email
- `FRONTEND_URL` - GitHub Pages URL
- `BASE_URL` - Render backend URL
- `CRON_SECRET` - Secret token for internal endpoints
- `SECRET_KEY` - Flask secret key
- `GEMINI_API_KEY` - Google Gemini API key
- `YOUTUBE_API_KEY` - YouTube Data API v3 key

### Worker Deployment (Local Machine)

**Location**: `workers/`

**Requirements**:

- Python 3.x with Conda
- NVIDIA GPU with CUDA
- Internet connection

**Setup**:

1. Create Conda environment
2. Install dependencies: `faster-whisper`, `yt-dlp`, `requests`
3. Configure environment variables
4. Set up Windows Task Scheduler (or cron)

**Environment Variables**:

- `WORKER_API_TOKEN` - Authentication token
- `SERVER_BASE_URL` - Backend API URL (optional)
- `WHISPER_MODEL_NAME` - Model name (default: `distil-large-v3`)
- `WHISPER_DEVICE` - Device (`cuda` or `cpu`)

### GitHub Actions Configuration

**Secrets Required** (GitHub Repository Settings):

- `CRON_SECRET` - Must match Render's `CRON_SECRET`
- `RENDER_BASE_URL` - Backend API URL on Render

**Workflows**:

- `.github/workflows/trigger-preprocess.yml`
- `.github/workflows/trigger-pipeline.yml`
- `.github/workflows/deploy-pages.yml` (frontend deployment)

---

## Key Design Decisions

### 1. Why Two Separate Workflows?

**Preprocessing (8:30 AM)**:

- Fetches and ranks news early
- Creates transcription jobs
- Gives worker time to process videos

**Pipeline (9:00 AM)**:

- Runs after worker has transcribed videos
- Generates summaries
- Sends newsletters

**Benefit**: Ensures transcripts are ready before newsletter generation.

### 2. Why Local GPU Worker?

**Reasons**:

- GPU transcription is expensive in cloud
- Local GPU provides free compute
- Better control over model and settings
- No API rate limits

**Trade-off**: Requires local machine to be running.

### 3. Why In-Memory Data Processing?

**Problem**: Render's free tier has ephemeral filesystem.

**Solution**: Process data in-memory instead of relying on JSON files.

**Benefit**: More reliable on cloud platforms.

### 4. Why Neon Database?

**Reasons**:

- Serverless PostgreSQL
- Auto-scaling
- Generous free tier
- Easy integration with Render

### 5. Why GitHub Actions for Scheduling?

**Reasons**:

- Render free tier doesn't include cron jobs
- GitHub Actions provides free scheduling
- Easy to monitor and debug
- Can trigger manually

---

## API Endpoints

### Public Endpoints

- `GET /` - API information
- `POST /api/subscribe` - Subscribe to newsletter
- `GET /unsubscribe/<token>` - Unsubscribe from newsletter

### Internal Endpoints (Protected)

- `POST /internal/run-preprocess` - Trigger preprocessing
  - Header: `X-Cron-Token: <CRON_SECRET>`
- `POST /internal/run-pipeline` - Trigger main pipeline
  - Header: `X-Cron-Token: <CRON_SECRET>`

### Worker Endpoints (Protected)

- `GET /api/get-videos` - Get batch of transcription jobs
  - Header: `Authorization: Bearer <WORKER_API_TOKEN>`
  - Returns: `{"ok": true, "jobs": [...]}`
- `POST /api/upload-all-transcripts` - Upload transcription results
  - Header: `Authorization: Bearer <WORKER_API_TOKEN>`
  - Body: `{"worker_id": "...", "results": [...]}`
  - Returns: `{"status": "ok", "received": N}`

---

## Error Handling & Resilience

### Backend Error Handling

- **Database Errors**: Rollback transactions, log errors
- **API Errors**: Retry with exponential backoff
- **Missing Data**: Use placeholders, continue processing
- **Email Failures**: Log per-subscriber, continue with others

### Worker Error Handling

- **Download Failures**: Mark job as failed, continue with others
- **Transcription Failures**: Return error status, upload anyway
- **Network Errors**: Retry up to 3 times with backoff
- **Model Loading Errors**: Exit with error code

### Job Recovery

- **Stale Jobs**: If job remains CLAIMED for > 30 minutes, reset to PENDING
- **Failed Jobs**: Can be retried by creating new job
- **Missing Transcripts**: Newsletter shows "Transcription pending"

---

## Monitoring & Logging

### Backend Logging

- Flask application logs to stdout
- Render captures logs automatically
- Log levels: INFO, ERROR, WARNING

### Worker Logging

- Console output for real-time monitoring
- File logs in `logs/` directory
- Timestamped log files: `worker_YYYYMMDD_HHMMSS.log`

### GitHub Actions Logs

- View workflow runs in GitHub Actions tab
- See HTTP request/response details
- Monitor execution times

---

## Performance Considerations

### Backend

- **Database Queries**: Indexed for fast lookups
- **API Calls**: Cached where possible
- **Memory Usage**: In-memory processing for reliability

### Worker

- **Model Loading**: Loaded once per batch (not per video)
- **GPU Usage**: Efficient CUDA operations
- **Batch Processing**: Processes up to 10 videos per run

### Scaling

- **Multiple Workers**: Can run multiple workers in parallel
- **Database**: Neon auto-scales
- **Email**: Resend handles rate limiting

---

## Security

### Authentication

- **Internal Endpoints**: `X-Cron-Token` header (GitHub Actions only)
- **Worker Endpoints**: Bearer token authentication
- **Subscriber Tokens**: Unique unsubscribe tokens

### Data Protection

- **API Keys**: Stored in environment variables
- **Database**: Connection string secured
- **Email**: No sensitive data in emails

---

## Future Enhancements

Potential improvements:

1. **Multiple RSS Sources**: Add more RSS feeds
2. **More YouTube Channels**: Expand channel list
3. **Better Ranking**: Fine-tune Gemini prompts
4. **Caching**: Cache transcripts to avoid re-transcription
5. **Analytics**: Track open rates, click rates
6. **A/B Testing**: Test different email formats
7. **Multi-language**: Support non-English content
8. **Webhooks**: Notify on newsletter sent
9. **Admin Dashboard**: Manage subscribers, view stats
10. **Retry Logic**: Automatic retry for failed transcriptions

---

## Troubleshooting

### Common Issues

1. **No news fetched**

   - Check RSS feed is accessible
   - Verify YouTube API key is valid
   - Check API rate limits

2. **Transcripts not ready**

   - Verify worker is running
   - Check worker logs for errors
   - Ensure GPU/CUDA is working

3. **Emails not sending**

   - Verify Resend API key
   - Check domain verification
   - Review email logs

4. **GitHub Actions not triggering**

   - Check cron syntax
   - Verify secrets are set
   - Check workflow file syntax

5. **Database connection errors**
   - Verify `DATABASE_URL` is correct
   - Check Neon database is active
   - Review connection limits

---

## Conclusion

This system demonstrates a complete end-to-end AI-powered newsletter pipeline:

- **Automated**: Runs twice daily without manual intervention
- **Scalable**: Can handle multiple workers and subscribers
- **Cost-Effective**: Uses free tiers where possible
- **Reliable**: Error handling and job recovery
- **Maintainable**: Clean code structure and documentation

The architecture separates concerns:

- **Frontend**: User interface
- **Backend**: Business logic and orchestration
- **Worker**: Heavy computation (GPU transcription)
- **Scheduler**: Automation (GitHub Actions)
- **Database**: Data persistence (Neon)

This design allows each component to be developed, deployed, and scaled independently.

---

**Last Updated**: December 2024
**Project**: AI Newsletter System
**Author**: Prajwol
