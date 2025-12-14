import json
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini API client
# The client automatically picks up the GEMINI_API_KEY environment variable
# Or you can explicitly pass the key: client = genai.Client(api_key="YOUR_API_KEY")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) if os.getenv("GEMINI_API_KEY") else genai.Client()

def load_combined_news(json_file: str = "combined_news.json"):
    """
    Load combined news from JSON file.
    Handles both old format (list) and new format (dict with metadata).
    
    Args:
        json_file: Path to the combined news JSON file
    
    Returns:
        tuple: (news_items list, metadata dict or None)
    """
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Handle both old format (list) and new format (dict with metadata)
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
    """
    Prepare news items for ranking by extracting titles and sequential IDs.
    
    Args:
        news_items: List of news items
    
    Returns:
        list: List of dicts with title, source, and sequential id
    """
    prepared = []
    for item in news_items:
        title = item.get("title", "")
        source = item.get("source", "unknown")
        # Use the sequential id (1, 2, 3, ...) instead of news_id/video_id
        item_id = item.get("id", None)
        
        if title and item_id is not None:
            prepared.append({
                "title": title,
                "source": source,
                "id": item_id
            })
    
    return prepared

def rank_news_with_gemini(news_items: list, top_n: int = 20):
    """
    Send news titles to Google Gemini 3 Pro for ranking based on importance.
    
    Args:
        news_items: List of news items with title, source, and id
        top_n: Number of top news items to return
    
    Returns:
        tuple: (top_ranked_list, ranked_output_dict) or ([], None) on error
    """
    if not news_items:
        print("✗ No news items to rank")
        return [], None
    
    # Prepare prompt for Gemini
    # Use the sequential id directly (already numbered 1, 2, 3...)
    news_list = "\n".join([
        f"ID {item['id']}: [{item['source']}] {item['title']}"
        for item in news_items
    ])
    
    # Gemini 3 prefers concise, direct instructions
    prompt = f"""Rank these AI news titles by importance (1-100). Consider: new model launches, OpenAI/Anthropic announcements, major releases, breakthroughs, policy changes, partnerships.

Return JSON array with the same id (number) from the input, source, importance_score, and reason for each item. Sort by importance_score descending.

News items:
{news_list}"""
    
    # Use Gemini 2.5 Flash-Lite as the default model (free tier)
    # Allow override via environment variable
    preferred_model = os.getenv("GEMINI_MODEL", None)
    
    if preferred_model:
        model_name = preferred_model
        # Try to determine if it supports thinking_level (paid models)
        supports_thinking = 'pro' in preferred_model.lower() or '3' in preferred_model.lower()
        model_display = f'Custom Model: {preferred_model}'
    else:
        # Default to Gemini 2.5 Flash-Lite
        model_name = 'gemini-2.5-flash-lite'
        model_display = 'Gemini 2.5 Flash-Lite (Free Tier)'
        supports_thinking = False
    
    # Define JSON schema for structured output
    json_schema = {
        "type": "array",
        "items": {
            "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The sequential ID number (1, 2, 3, ...) from the input news item"
                    },
                "source": {
                    "type": "string",
                    "enum": ["website", "youtube"],
                    "description": "Source of the news item"
                },
                "importance_score": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Importance score from 1-100 (100 = most important/hottest)"
                },
                "reason": {
                    "type": "string",
                    "description": "Brief explanation of why this is important"
                }
            },
            "required": ["id", "source", "importance_score", "reason"]
        }
    }
    
    print(f"\n🤖 Using {model_display} for ranking...")
    
    try:
        # Build config - only add thinking_config for models that support it
        config_params = {
            "response_mime_type": "application/json",
            "response_json_schema": json_schema
        }
        
        # Only add thinking_level for paid models (Gemini 3 Pro)
        if supports_thinking:
            config_params["thinking_config"] = types.ThinkingConfig(thinking_level="high")
        
        # Generate response using the new API format with structured outputs
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(**config_params)
        )
        
        # Store complete response for inspection
        complete_response = {
            "model": model_name,
            "prompt": prompt,
            "raw_response_text": response.text if hasattr(response, 'text') else str(response),
            "response_metadata": {
                "candidates": [],
                "usage_metadata": {},
                "prompt_feedback": {},
                "response_object_attributes": []
            }
        }
        
        # Store all available attributes from response object
        if hasattr(response, '__dict__'):
            complete_response["response_metadata"]["response_object_attributes"] = list(response.__dict__.keys())
        
        # Try to extract metadata if available (new API format may have different structure)
        try:
            # Store the entire response object as dict if possible
            if hasattr(response, 'to_dict'):
                complete_response["response_metadata"]["full_response"] = response.to_dict()
            elif hasattr(response, '__dict__'):
                complete_response["response_metadata"]["full_response"] = {
                    k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                    for k, v in response.__dict__.items()
                }
        except Exception as e:
            complete_response["response_metadata"]["extraction_error"] = str(e)
        
        # Try to extract common metadata fields
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            complete_response["response_metadata"]["usage_metadata"] = {
                "prompt_token_count": getattr(usage, 'prompt_token_count', None) if usage else None,
                "candidates_token_count": getattr(usage, 'candidates_token_count', None) if usage else None,
                "total_token_count": getattr(usage, 'total_token_count', None) if usage else None
            }
        
        # Store candidates if available
        if hasattr(response, 'candidates') and response.candidates:
            complete_response["response_metadata"]["candidates"] = []
            for candidate in response.candidates:
                candidate_data = {
                    "index": getattr(candidate, 'index', None),
                    "finish_reason": str(getattr(candidate, 'finish_reason', None)),
                }
                if hasattr(candidate, 'content'):
                    candidate_data["content"] = str(candidate.content)
                if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings is not None:
                    candidate_data["safety_ratings"] = [
                        {
                            "category": str(getattr(rating, 'category', None)),
                            "probability": str(getattr(rating, 'probability', None))
                        }
                        for rating in candidate.safety_ratings
                    ]
                complete_response["response_metadata"]["candidates"].append(candidate_data)
        
        # Save complete response to file
        complete_response_file = "gemini_complete_response.json"
        with open(complete_response_file, "w", encoding="utf-8") as f:
            json.dump(complete_response, f, indent=2, ensure_ascii=False, default=str)
        print(f"✓ Saved complete Gemini response to: {complete_response_file}")
        
        # Extract JSON from response
        # With structured outputs, response.text should be valid JSON directly
        response_text = response.text.strip() if hasattr(response, 'text') else str(response)
        
        # Parse JSON response (should be valid JSON with structured outputs)
        try:
            ranked_news = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Fallback: Try to extract JSON if wrapped in markdown or other formatting
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                parts = response_text.split("```")
                for part in parts:
                    part = part.strip()
                    if part.startswith("{") or part.startswith("["):
                        response_text = part
                        break
            
            # Try to find JSON array in the response
            if not response_text.startswith("["):
                start_idx = response_text.find("[")
                end_idx = response_text.rfind("]")
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    response_text = response_text[start_idx:end_idx+1]
            
            # Try parsing again
            try:
                ranked_news = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to fix common JSON issues
                response_text = response_text.replace(",}", "}").replace(",]", "]")
                try:
                    ranked_news = json.loads(response_text)
                except json.JSONDecodeError:
                    print(f"✗ Failed to parse JSON response: {e}")
                    print(f"Response preview: {response_text[:500]}")
                    return [], None
        
        # Validate response format
        if not isinstance(ranked_news, list):
            print(f"✗ Expected list but got {type(ranked_news)}")
            return [], None
        
        # Validate and filter items with required fields
        valid_ranked = []
        for item in ranked_news:
            if isinstance(item, dict) and "id" in item and "source" in item:
                # Ensure importance_score exists, default to 0
                if "importance_score" not in item:
                    item["importance_score"] = 0
                valid_ranked.append(item)
        
        if not valid_ranked:
            print("✗ No valid ranked news items found in response")
            return [], None
        
        ranked_news = valid_ranked
        
        # Sort by importance_score descending
        ranked_news.sort(key=lambda x: x.get("importance_score", 0), reverse=True)
        
        # Return top N
        top_ranked = ranked_news[:top_n]
        
        print(f"✓ Successfully ranked news. Top {len(top_ranked)} items selected.")
        
        # Also save the parsed and ranked results with metadata
        ranked_output = {
            "model_used": model_name,
            "total_items_ranked": len(ranked_news),
            "top_n_requested": top_n,
            "top_n_returned": len(top_ranked),
            "ranked_news": top_ranked,
            "all_ranked_news": ranked_news  # Include all ranked items, not just top N
        }
        
        return top_ranked, ranked_output
        
    except json.JSONDecodeError as e:
        print(f"✗ Error parsing JSON response: {e}")
        if 'response_text' in locals():
            print(f"Response text: {response_text[:500]}")
        return [], None
    except Exception as e:
        print(f"✗ Error ranking news with Gemini: {e}")
        import traceback
        traceback.print_exc()
        return [], None

def get_top_news(json_file: str = "combined_news.json", top_n: int = 20):
    """
    Main function to load news, rank them, and return top news.
    
    Args:
        json_file: Path to the combined news JSON file
        top_n: Number of top news items to return
    
    Returns:
        list: Top ranked news items
    """
    print("\n" + "="*50)
    print("RANKING NEWS WITH GOOGLE GEMINI")
    print("="*50)
    
    # Load news
    news_items, metadata = load_combined_news(json_file)
    
    if not news_items:
        print("✗ No news items found")
        return []
    
    if metadata:
        print(f"\n📊 News Statistics:")
        print(f"  Total news: {metadata.get('total_news', len(news_items))}")
        print(f"  Website news: {metadata.get('website_count', 0)}")
        print(f"  YouTube videos: {metadata.get('youtube_count', 0)}")
    
    # Prepare news for ranking
    prepared_news = prepare_news_for_ranking(news_items)
    
    if not prepared_news:
        print("✗ No valid news items to rank")
        return []
    
    # Rank news with Gemini
    ranked_news, ranked_output = rank_news_with_gemini(prepared_news, top_n)
    
    if not ranked_news or ranked_output is None:
        print("✗ Failed to rank news")
        return []
    
    # Print top ranked news
    print("\n" + "="*50)
    print(f"TOP {len(ranked_news)} RANKED NEWS")
    print("="*50)
    for i, item in enumerate(ranked_news, 1):
        print(f"\n{i}. [{item['source'].upper()}] Score: {item['importance_score']}/100")
        print(f"   ID: {item['id']}")
        print(f"   Reason: {item.get('reason', 'N/A')}")
    
    # Save ranked news to file with complete output
    output_file = "ranked_news.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ranked_output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved ranked news to: {output_file}")
    print("="*50)
    
    return ranked_news

if __name__ == "__main__":
    try:
        # Check if API key is set
        if not os.getenv("GEMINI_API_KEY"):
            print("✗ Error: GEMINI_API_KEY not found in environment variables")
            print("   Please set GEMINI_API_KEY in your .env file")
            exit(1)
        
        top_news = get_top_news(top_n=20)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
