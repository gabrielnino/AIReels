import os
import requests
import uuid
from utils.logger import get_logger

log = get_logger(__name__)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def download_image(url: str, suffix: str = ".png") -> str:
    """Downloads an image from a URL and saves it to the local outputs directory."""
    log.step("download_image", "IN", url=url, suffix=suffix)
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        filename = f"{uuid.uuid4()}{suffix}"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        size_kb = round(os.path.getsize(filepath) / 1024)
        log.step("download_image", "OUT", filepath=filepath, size_kb=size_kb)
        return filepath
    except Exception as e:
        log.step("download_image", "ERR", url=url, error=str(e))
        return None


def to_file_uri(local_path: str) -> str:
    """Converts a local file path to a file:// URI."""
    log.step("to_file_uri", "IN", local_path=local_path)
    abs_path = os.path.abspath(local_path)
    # DashScope SDK uses urlparse. On Windows, file://F:/path parses F: as netloc,
    # which avoids the leading slash issue.
    uri = f"file://{abs_path.replace(chr(92), '/')}"
    log.step("to_file_uri", "OUT", uri=uri)
    return uri
