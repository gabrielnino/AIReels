import os
from utils.logger import get_logger

log = get_logger(__name__)

FAL_API_BASE = "https://queue.fal.run"


def get_fal_api_key() -> str:
    key = os.environ.get("FAL_API_KEY")
    if not key:
        log.step("get_fal_api_key", "ERR", error="FAL_API_KEY not found")
        raise ValueError("FAL_API_KEY not found in environment variables.")
    return key


def get_fal_headers() -> dict:
    return {
        "Authorization": f"Key {get_fal_api_key()}",
        "Content-Type": "application/json",
    }
