import json
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini API client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) if os.getenv("GEMINI_API_KEY") else genai.Client()


def load_combined_news(json_file: str = "combined_news.json"):
    """Load combined news from JSON file."""
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "news" in data:
            return data["news"], data.get("metadata")
        else:
            return data, None
    except FileNotFoundError:
        print(f"✗ File not found: {json_file}")
        return [], None
    except Exception as e:
        print(f"✗ Error loading news: {e}")
        return [], None


def prepare_news_for_ranking(news_items: list):
    """Prepare news items for ranking by extracting titles and IDs."""
    prepared = []
    for item in news_items:
        title = item.get("title", "")
        source = item.get("source", "unknown")
        item_id = item.get("id", None)
        if title and item_id is not None:
            prepared.append({"title": title, "source": source, "id": item_id})
    return prepared


def rank_news_with_gemini(news_items: list, top_n: int = 20):
    """Rank news items using Gemini and return top N."""
    if not news_items:
        print("✗ No news items to rank")
        return [], None

    news_list = "\n".join([
        f"ID {item['id']}: [{item['source']}] {item['title']}" for item in news_items
    ])

    prompt = f"""Rank these AI news titles by importance (1-100). Consider: new model launches, OpenAI/Anthropic announcements, major releases, breakthroughs, policy changes, partnerships.

Return JSON array with the same id (number) from the input, source, importance_score, and reason for each item. Sort by importance_score descending.

News items:
{news_list}"""

    preferred_model = os.getenv("GEMINI_MODEL", None)
    if preferred_model:
        model_name = preferred_model
        supports_thinking = "pro" in preferred_model.lower() or "3" in preferred_model.lower()
        model_display = f"Custom Model: {preferred_model}"
    else:
        model_name = "gemini-2.5-flash-lite"
        model_display = "Gemini 2.5 Flash-Lite (Free Tier)"
        supports_thinking = False

    json_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "source": {"type": "string", "enum": ["website", "youtube"]},
                "importance_score": {"type": "integer", "minimum": 1, "maximum": 100},
                "reason": {"type": "string"},
            },
            "required": ["id", "source", "importance_score", "reason"],
        },
    }

    print(f"\n🤖 Using {model_display} for ranking...")

    try:
        config_params = {
            "response_mime_type": "application/json",
            "response_json_schema": json_schema,
        }
        if supports_thinking:
            config_params["thinking_config"] = types.ThinkingConfig(thinking_level="high")

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(**config_params),
        )

        response_text = response.text.strip() if hasattr(response, "text") else str(response)

        try:
            ranked_news = json.loads(response_text)
        except json.JSONDecodeError as e:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                parts = response_text.split("```")
                for part in parts:
                    part = part.strip()
                    if part.startswith("{") or part.startswith("["):
                        response_text = part
                        break

            if not response_text.startswith("["):
                start_idx = response_text.find("[")
                end_idx = response_text.rfind("]")
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    response_text = response_text[start_idx : end_idx + 1]

            try:
                ranked_news = json.loads(response_text)
            except json.JSONDecodeError:
                response_text = response_text.replace(",}", "}").replace(",]", "]")
                try:
                    ranked_news = json.loads(response_text)
                except json.JSONDecodeError:
                    print(f"✗ Failed to parse JSON response: {e}")
                    print(f"Response preview: {response_text[:500]}")
                    return [], None

        if not isinstance(ranked_news, list):
            print(f"✗ Expected list but got {type(ranked_news)}")
            return [], None

        valid_ranked = []
        for item in ranked_news:
            if isinstance(item, dict) and "id" in item and "source" in item:
                if "importance_score" not in item:
                    item["importance_score"] = 0
                valid_ranked.append(item)

        if not valid_ranked:
            print("✗ No valid ranked news items found in response")
            return [], None

        ranked_news = valid_ranked
        ranked_news.sort(key=lambda x: x.get("importance_score", 0), reverse=True)

        top_ranked = ranked_news[:top_n]

        print(f"✓ Successfully ranked news. Top {len(top_ranked)} items selected.")

        ranked_output = {
            "model_used": model_name,
            "total_items_ranked": len(ranked_news),
            "top_n_requested": top_n,
            "top_n_returned": len(top_ranked),
            "ranked_news": top_ranked,
            "all_ranked_news": ranked_news,
        }

        return top_ranked, ranked_output

    except json.JSONDecodeError as e:
        print(f"✗ Error parsing JSON response: {e}")
        return [], None
    except Exception as e:
        print(f"✗ Error ranking news with Gemini: {e}")
        import traceback

        traceback.print_exc()
        return [], None


def get_top_news(json_file: str = "combined_news.json", top_n: int = 20):
    """Convenience wrapper to load, rank, and return top news."""
    print("\n" + "=" * 50)
    print("RANKING NEWS WITH GOOGLE GEMINI")
    print("=" * 50)

    news_items, metadata = load_combined_news(json_file)
    if not news_items:
        print("✗ No news items found")
        return []

    if metadata:
        print("\n📊 News Statistics:")
        print(f"  Total news: {metadata.get('total_news', len(news_items))}")
        print(f"  Website news: {metadata.get('website_count', 0)}")
        print(f"  YouTube videos: {metadata.get('youtube_count', 0)}")

    prepared_news = prepare_news_for_ranking(news_items)
    if not prepared_news:
        print("✗ No valid news items to rank")
        return []

    ranked_news, ranked_output = rank_news_with_gemini(prepared_news, top_n)
    if not ranked_news or ranked_output is None:
        print("✗ Failed to rank news")
        return []

    print("\n" + "=" * 50)
    print(f"TOP {len(ranked_news)} RANKED NEWS")
    print("=" * 50)
    for i, item in enumerate(ranked_news, 1):
        print(f"\n{i}. [{item['source'].upper()}] Score: {item['importance_score']}/100")
        print(f"   ID: {item['id']}")
        print(f"   Reason: {item.get('reason', 'N/A')}")

    output_file = "ranked_news.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ranked_output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved ranked news to: {output_file}")
    print("=" * 50)

    return ranked_news


if __name__ == "__main__":
    try:
        if not os.getenv("GEMINI_API_KEY"):
            print("✗ Error: GEMINI_API_KEY not found in environment variables")
            print("   Please set GEMINI_API_KEY in your .env file")
            exit(1)

        top_news = get_top_news(top_n=20)
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
