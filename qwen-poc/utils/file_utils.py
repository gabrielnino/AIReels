import os
import requests
import uuid

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_image(url: str, suffix: str = ".png") -> str:
    """
    Downloads an image from a URL and saves it to the local outputs directory.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        filename = f"{uuid.uuid4()}{suffix}"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return filepath
    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return None

def to_file_uri(local_path: str) -> str:
    """
    Converts a local file path to a file:// URI.
    """
    abs_path = os.path.abspath(local_path)
    # DashScope SDK uses urlparse. On Windows, file://F:/path parses F: as netloc, 
    # which avoids the leading slash issue.
    return f"file://{abs_path.replace(chr(92), '/')}"
