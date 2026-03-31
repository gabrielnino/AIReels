import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

SEARCH_API_BASE_URL = "https://api.search.brave.com/res/v1/web/search"

def _get_api_key() -> str:
    key = os.environ.get("SEARCH_API_KEY")
    if not key:
        raise ValueError("SEARCH_API_KEY not found in environment variables.")
    return key

def search(query: str, count: int = 5) -> dict:
    """
    Submits a search query to the Brave Search API.
    
    Args:
        query: The search term.
        count: Max number of results.
        
    Returns:
        JSON response dictionary from the Brave Search API.
    """
    logging.info(f"[search_service.search] input values - query: {query}, count: {count}")
    api_key = _get_api_key()
    
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    
    params = {
        "q": query,
        "count": count # Brave search specific parameter for limits (if supported, else it just ignores it. Usually it's 'count' or 'limit')
    }
    
    print(f"[search] Querying Brave Search for: '{query}'")
    
    try:
        response = requests.get(SEARCH_API_BASE_URL, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        result = response.json()
        logging.info(f"[search_service.search] output values: {result}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"[search] Failed to reach Brave Search API. Error: {e}")
        # Re-raise so the caller can handle it
        raise
