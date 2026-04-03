import os
import requests
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()
log = get_logger(__name__)

SEARCH_API_BASE_URL = "https://api.search.brave.com/res/v1/web/search"


def _get_api_key() -> str:
    key = os.environ.get("SEARCH_API_KEY")
    if not key:
        log.step("_get_api_key", "ERR", error="SEARCH_API_KEY not found")
        raise ValueError("SEARCH_API_KEY not found in environment variables.")
    return key


def search(query: str, count: int = 5) -> dict:
    """Submits a search query to the Brave Search API."""
    log.step("search", "IN", query=query, count=count)

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": _get_api_key(),
    }
    params = {"q": query, "count": count}

    try:
        response = requests.get(SEARCH_API_BASE_URL, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        result = response.json()
        n_results = len(result.get("web", {}).get("results", []))
        log.step("search", "OUT", query=query, results_returned=n_results)
        return result
    except requests.exceptions.RequestException as e:
        log.step("search", "ERR", query=query, error=str(e))
        raise
