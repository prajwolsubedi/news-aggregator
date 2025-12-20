# AI News Aggregator

An intelligent news aggregator that collects AI-related news from RSS feeds and YouTube channels, ranks them by importance using Google Gemini AI, and automatically sends daily email digests to subscribers.

## Features

- 📰 **RSS Feed Aggregation**: Fetches AI-related news from Techmeme RSS feed
- 📺 **YouTube Integration**: Collects videos from multiple AI-focused YouTube channels
- 🤖 **AI-Powered Ranking**: Uses Google Gemini to rank news by importance/hotness
- 📝 **Smart Summarization**:
  - Website news: Uses existing summaries
  - YouTube videos: Transcribes and summarizes using AI (via distributed worker system)
- 🔄 **Automatic Job Recovery**: Stale transcription jobs (claimed but not completed) are automatically reset after 30 minutes, preventing jobs from getting permanently stuck
- 🎯 **Top News Selection**: Automatically selects and processes top-ranked news items
- 🌐 **Web Interface**: Simple subscription form for users to sign up
- 📧 **Email System**: Automated daily emails sent at 9am to all subscribers
- 🔄 **Automated Pipeline**: Runs daily without manual intervention
- 🗄️ **Database**: PostgreSQL for subscriber management
- 🚀 **Deployment Ready**: Configured for Render.com deployment

## Setup

1. **Clone the repository**

   ```bash
   git clone git@github.com:prajwolsubedi/news-aggregator.git
   cd news-aggregator
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root (see `.env.example` for template):

   ```
   # API Keys
   GEMINI_API_KEY=your_gemini_api_key_here
   YOUTUBE_API_KEY=your_youtube_api_key_here
   SERP_API_KEY=your_serp_api_key_here

   # Database (for local development, use PostgreSQL connection string)
   DATABASE_URL=postgresql://user:password@localhost:5432/ai_news

   # Email configuration (Resend API)
   RESEND_API_KEY=your_resend_api_key_here
   SENDER_EMAIL=ainews@prajwolsubedi.com.np
   REPLY_TO_EMAIL=prajwolsubedi@gmail.com

   # Flask Configuration
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   BASE_URL=http://localhost:5001

   # Scheduler Configuration
   SCHEDULER_TIMEZONE=UTC
   SCHEDULER_LOG_LEVEL=INFO
   ```

   **Note for Email Service**: We use [Resend](https://resend.com) API for sending emails. Sign up at resend.com to get your API key. Make sure your domain (`prajwolsubedi.com.np`) is verified in Resend dashboard.

## Usage

### Automated Daily Pipeline

The system runs automatically every day at 9am. To run manually:

```bash
python run_pipeline.py
```

This orchestrates all steps:

1. Fetches RSS news
2. Fetches YouTube videos
3. Combines all sources
4. Ranks news by importance
5. Processes top news (transcribes & summarizes)
6. Sends emails to all subscribers

### Web Interface

Start the Flask web server:

```bash
python app.py
```

Then visit `http://localhost:5001` to:

- Subscribe to daily AI news emails
- Unsubscribe using the link in any email

### Manual Steps (for testing)

#### 1. Fetch News from RSS and YouTube

```bash
python combine_news.py
```

#### 2. Rank News by Importance

```bash
python rank_news.py
```

#### 3. Process Top News

```bash
python process_top_news.py
```

#### 4. Send News via Email

Send to all subscribers:

```bash
python send_email.py
```

Or send to a specific email:

```bash
python send_email.py recipient@example.com
```

### Scheduler (for automated daily runs)

To run the scheduler locally (runs pipeline at 9am daily):

```bash
python scheduler.py
```

## Project Structure

```
.
├── app.py                    # Flask web application (subscription interface)
├── scheduler.py              # Daily scheduler (runs pipeline at 9am)
├── run_pipeline.py          # Main pipeline orchestrator
├── database.py               # PostgreSQL database connection
├── models.py                # Data models (Subscriber)
├── utils.py                 # Common utility functions
├── config.py                # Centralized configuration
├── email_templates.py       # Email templates (welcome, unsubscribe)
├── check_rss.py             # RSS feed fetching and filtering
├── youtube_fetch.py         # YouTube video fetching
├── combine_news.py          # Combines RSS and YouTube news
├── rank_news.py             # AI-powered news ranking
├── youtube_transcribe.py    # YouTube video transcription
├── process_top_news.py      # Processes top news with summaries
├── send_email.py            # Email sending (batch to subscribers)
├── templates/
│   └── index.html           # Subscription form page
├── migrations/
│   └── 001_init.sql         # Database schema
├── requirements.txt         # Python dependencies
├── Procfile                 # Process definitions for deployment
├── render.yaml              # Render.com deployment config
├── runtime.txt              # Python version
└── README.md                # This file
```

## Output Files

- `combined_news.json`: All news items from RSS and YouTube
- `ranked_news.json`: Ranked news with importance scores
- `top_news.json`: Top 11 news items with summaries
- `gemini_complete_response.json`: Complete Gemini API response for debugging

## YouTube Channels Monitored

- @matthew_berman
- @aiDotEngineer
- @aiadvantage
- @aiexplained-official
- @mreflow
- @Fireship
- @OpenAI
- @anthropic-ai
- @google

## Ranking Criteria

News is ranked based on:

- New AI model launches (GPT, Claude, Gemini, etc.)
- OpenAI and Anthropic AI announcements
- Major model releases and breakthroughs
- Company announcements from major AI companies
- Significant breakthroughs in AI research
- Policy changes and regulations
- Major partnerships or acquisitions

## Deployment

### Deploy to Render.com

1. **Push your code to GitHub**

2. **Create a new Render account** and connect your GitHub repository

3. **Create PostgreSQL Database**:

   - Go to Render Dashboard → New → PostgreSQL
   - Name it `ai-news-db`
   - Note the connection string

4. **Create Web Service**:

   - Go to Render Dashboard → New → Web Service
   - Connect your repository
   - Use the `render.yaml` file (auto-detected) or configure manually:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python app.py`
   - Add environment variables from `.env.example`

5. **Create Worker Service**:

   - Go to Render Dashboard → New → Background Worker
   - Connect your repository
   - Start Command: `python scheduler.py`
   - Add same environment variables as web service

6. **Set BASE_URL**:
   - In environment variables, set `BASE_URL` to your web service URL
   - Example: `https://ai-news-web.onrender.com`

The system will now:

- Run the pipeline daily at 9am UTC
- Serve the subscription web interface
- Send emails to all subscribers automatically

## Requirements

- Python 3.11+
- Google Gemini API key
- YouTube Data API key (for fetching videos)
- SerpAPI key (for YouTube transcriptions)
- PostgreSQL database (provided by Render in production)
- Resend API key (for sending emails) - Sign up at [resend.com](https://resend.com)

## License

MIT License
