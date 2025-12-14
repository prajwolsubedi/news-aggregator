# AI News Aggregator

An intelligent news aggregator that collects AI-related news from RSS feeds and YouTube channels, ranks them by importance using Google Gemini AI, and provides summaries for top news items.

## Features

- 📰 **RSS Feed Aggregation**: Fetches AI-related news from Techmeme RSS feed
- 📺 **YouTube Integration**: Collects videos from multiple AI-focused YouTube channels
- 🤖 **AI-Powered Ranking**: Uses Google Gemini to rank news by importance/hotness
- 📝 **Smart Summarization**: 
  - Website news: Uses existing summaries
  - YouTube videos: Transcribes and summarizes using AI
- 🎯 **Top News Selection**: Automatically selects and processes top-ranked news items

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
   Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   YOUTUBE_API_KEY=your_youtube_api_key_here
   ```

## Usage

### 1. Fetch News from RSS and YouTube
```bash
python combine_news.py
```
This will:
- Fetch AI-related news from RSS feed
- Fetch videos from YouTube channels
- Combine and save to `combined_news.json`

### 2. Rank News by Importance
```bash
python rank_news.py
```
This will:
- Send news titles to Google Gemini for ranking
- Rank news by importance score (1-100)
- Save ranked results to `ranked_news.json`

### 3. Process Top News
```bash
python process_top_news.py
```
This will:
- Select top 11 ranked news items
- Transcribe YouTube videos
- Generate AI summaries for YouTube content
- Save processed news to `top_news.json`

## Project Structure

```
.
├── check_rss.py              # RSS feed fetching and filtering
├── youtube_fetch.py          # YouTube video fetching
├── combine_news.py           # Combines RSS and YouTube news
├── rank_news.py              # AI-powered news ranking
├── youtube_transcribe.py     # YouTube video transcription
├── process_top_news.py       # Processes top news with summaries
├── requirements.txt          # Python dependencies
└── README.md                 # This file
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

## Requirements

- Python 3.9+
- Google Gemini API key
- YouTube Data API key (for fetching videos)

## License

MIT License
