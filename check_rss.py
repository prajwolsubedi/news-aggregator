import feedparser
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta


AI_KEYWORDS = [
    # Core AI terms
    "ai", "artificial intelligence", "machine learning", "ml", "deep learning",
    "neural network", "neural networks", "llm", "large language model",
    "foundation model", "generative ai", "gen ai", "genai",
    
    # Model types and architectures
    "transformer", "gpt", "claude", "gemini", "bert", "diffusion",
    "multimodal", "computer vision", "nlp", "natural language processing",
    
    # Companies and organizations
    "openai", "anthropic", "deepmind", "google ai", "microsoft ai",
    "meta ai", "xai", "cohere", "mistral", "perplexity", "hugging face",
    "nvidia", "intel ai", "qualcomm ai",
    
    # Hardware and infrastructure (more specific)
    "gpu", "tpu", "h100", "a100", "blackwell", "hopper",
    "ai training", "model training", "inference", "ai compute",
    
    # AI applications and concepts (more specific)
    "chatbot", "ai assistant", "ai agent", "autonomous", "robotics",
    "ai prompt", "fine-tuning", "rag", "retrieval augmented generation",
    "ai alignment", "ai safety", "ai regulation", "ai governance",
    "hallucination", "ai bias", "adversarial", "prompt injection"
]

def is_within_last_24_hours(entry, window_start, now_utc):
    if not entry.get("published_parsed"):
        return False
    published_at = datetime(
        *entry.published_parsed[:6],
        tzinfo=timezone.utc
    )
    return window_start <= published_at <= now_utc


def is_ai_related(entry):
    text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
    
    # Use word boundaries for more precise matching
    for keyword in AI_KEYWORDS:
        # For multi-word phrases, use simple substring match
        if " " in keyword:
            if keyword in text:
                return True
        # For single words, use word boundaries to avoid false positives
        else:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text):
                return True
    
    return False

def extract_news(entry):
    published = None
    if entry.get("published_parsed"):
        published = datetime(*entry.published_parsed[:6]).isoformat()

    soup = BeautifulSoup(entry.get("summary", ""), "html.parser")
    summary_text = soup.get_text(" ", strip=True)

    source_link = None
    for a in soup.find_all("a", href=True):
        if "techmeme.com" not in a["href"]:
            source_link = a["href"]
            break

    return {
        "title": entry.get("title"),
        "published_at": published,
        "summary": summary_text,
        "source_link": source_link,
    }

def fetch_rss_news():
    """Fetch AI-related news from RSS feed within the last 24 hours."""
    # Calculate time window
    now_utc = datetime.now(timezone.utc)
    window_start = now_utc - timedelta(hours=24)
    
    # Fetch RSS
    feed = feedparser.parse("https://www.techmeme.com/feed.xml")
    all_news = []
    ai_news = []
    ai_news_last_24h = []

    for entry in feed.entries:
        news_item = extract_news(entry)
        all_news.append(news_item)
        if is_ai_related(entry):
            ai_news.append(news_item)
            if is_within_last_24_hours(entry, window_start, now_utc):
                ai_news_last_24h.append(news_item)

    # Save to JSON files
    from utils import save_json_file
    save_json_file("ai_news.json", ai_news)
    save_json_file("all_news.json", all_news)
    save_json_file("ai_news_last_24h.json", ai_news_last_24h)

    return ai_news_last_24h

if __name__ == "__main__":
    ai_news_last_24h = fetch_rss_news()
    
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"AI news last 24h: {len(ai_news_last_24h)}")
    print("="*50)
    print(f"✓ Saved AI news to: ai_news.json")
    print(f"✓ Saved all news to: all_news.json")
    print(f"✓ Saved AI news last 24h to: ai_news_last_24h.json")
    print("="*50)
