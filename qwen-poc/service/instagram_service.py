import os
import time
import json
import shutil
import requests
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()

log = get_logger(__name__)

INSTAGRAM_GRAPH_API = "https://graph.facebook.com/v22.0"


def _get_access_token():
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
    if not token:
        raise ValueError("INSTAGRAM_ACCESS_TOKEN not found in environment variables.")
    return token


def _serve_video_temp(video_path, port=9876):
    """Start a local HTTP server serving only the video file. Returns (server, thread)."""
    filename = os.path.basename(video_path)

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/" or self.path == "/" + filename:
                self.send_response(200)
                file_size = os.path.getsize(video_path)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Length", str(file_size))
                # Instagram may send Range requests
                range_header = self.headers.get("Range")
                if range_header:
                    start_str = range_header.split("=")[1].split("-")[0]
                    start = int(start_str)
                    end = file_size - 1
                    self.send_response(206)
                    self.send_header("Content-Type", "video/mp4")
                    self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                    self.send_header("Content-Length", str(end - start + 1))
                    self.send_header("Accept-Ranges", "bytes")
                    self.end_headers()
                    with open(video_path, "rb") as f:
                        f.seek(start)
                        shutil.copyfileobj(f, self.wfile)
                    return
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                with open(video_path, "rb") as f:
                    shutil.copyfileobj(f, self.wfile)
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, *_a):
            pass  # Suppress server logs

    server = HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _run_ngrok(port, timeout=10):
    """Start ngrok and return the public URL."""
    try:
        import subprocess
        proc = subprocess.Popen(
            ["ngrok", "http", str(port), "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Poll ngrok local API for the tunnel URL
        url = None
        deadline = time.time() + timeout
        ngrok_api = "http://127.0.0.1:4040/api/tunnels"
        while time.time() < deadline:
            try:
                resp = requests.get(ngrok_api, timeout=2)
                tunnels = resp.json().get("tunnels", [])
                if tunnels:
                    # ngrok creates both http and https tunnels
                    for t in tunnels:
                        if t.get("proto") == "https":
                            url = t["public_url"]
                            return url, proc
                    url = tunnels[0]["public_url"]
                    return url, proc
            except Exception:
                pass
            time.sleep(0.5)
        if url:
            return url, proc
        raise RuntimeError("ngrok did not create a tunnel in time")
    except FileNotFoundError:
        raise RuntimeError(
            "ngrok is not installed. Install it: "
            "https://ngrok.com/download\n"
            "Or set VIDEO_PUBLIC_URL env var to a public URL instead."
        )


def _create_media_container(video_url, caption, access_token):
    """Create an Instagram Reels media container. Returns container_id."""
    endpoint = f"{INSTAGRAM_GRAPH_API}/me/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": access_token,
    }
    try:
        resp = requests.post(endpoint, json=payload, timeout=30)
        result = resp.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to create media container: {e}")

    if "error" in result:
        raise RuntimeError(
            f"Instagram API error creating container: "
            f"{result['error'].get('error_user_message', result['error'].get('message', json.dumps(result['error'])))}"
        )

    container_id = result.get("id")
    if not container_id:
        raise RuntimeError(f"No container ID returned: {result}")

    log.step("ig_upload", "INFO", container_id=container_id, message="Media container created")
    return str(container_id)


def _wait_for_container(container_id, access_token, timeout=300):
    """Poll container status until OK or error."""
    endpoint = f"{INSTAGRAM_GRAPH_API}/{container_id}"
    params = {"fields": "status_code", "access_token": access_token}
    log.step("ig_upload", "INFO", message="Waiting for container processing...")

    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(endpoint, params=params, timeout=15)
            status = resp.json().get("status_code", "")
        except requests.RequestException as e:
            log.step("ig_upload", "WARN", polling_error=str(e))
            time.sleep(5)
            continue

        log.step("ig_upload", "INFO", container_status=status, elapsed_s=int(time.time() - start))

        if status in ("OK", "FINISHED"):
            return True
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Container processing failed: {status}")
        time.sleep(10)

    raise RuntimeError(f"Container did not finish processing within {timeout}s")


def _publish_reel(container_id, access_token):
    """Publish the media container. Returns publishing_id."""
    endpoint = f"{INSTAGRAM_GRAPH_API}/me/media_publish"
    payload = {
        "creation_id": container_id,
        "access_token": access_token,
    }
    try:
        resp = requests.post(endpoint, json=payload, timeout=30)
        result = resp.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to publish reel: {e}")

    if "error" in result:
        raise RuntimeError(
            f"Instagram API error publishing: "
            f"{result['error'].get('error_user_message', result['error'].get('message', json.dumps(result['error'])))}"
        )

    pub_id = result.get("id")
    if not pub_id:
        log.step("ig_upload", "WARN", message="No publishing ID returned. May still be processing.", raw=result)
        return None

    log.step("ig_upload", "INFO", publishing_id=pub_id, message="Reel published successfully")
    return str(pub_id)


def upload_reel_to_instagram(video_path, caption=None, hashtags=None):
    """
    Upload a video as an Instagram Reel.

    This function serves the local video file via HTTP, creates a temporary
    ngrok tunnel for public access, and uses the Instagram Graph API to
    create, wait for processing, and publish the reel.

    Args:
        video_path: Path to the MP4 video file.
        caption: Caption text (without hashtags).
        hashtags: List of hashtag strings.
        language: Language for logging ("en" or "es").

    Returns:
        The publishing_id if successful, or the container_id as fallback.

    Environment variables required:
        INSTAGRAM_ACCESS_TOKEN: Your IG access token.

    Optional:
        ngrok must be installed and in PATH for local serving.
        Or set VIDEO_PUBLIC_URL instead to skip ngrok.
    """
    # Build the full caption text
    caption = caption or ""
    hashtags = hashtags or []
    if hashtags:
        tag_text = " ".join([h if h.startswith("#") else f"#{h}" for h in hashtags])
        if caption:
            caption = f"{caption}\n\n{tag_text}"
        else:
            caption = tag_text

    access_token = _get_access_token()

    # Check for a direct public URL first (simpler, no ngrok needed)
    video_url = os.environ.get("VIDEO_PUBLIC_URL")
    use_ngrok = False
    server = None
    ngrok_proc = None

    if not video_url:
        use_ngrok = True

    try:
        if use_ngrok:
            port = 9876
            server, _thread = _serve_video_temp(video_path, port=port)
            public_url, ngrok_proc = _run_ngrok(port)
            video_url = f"{public_url}/{os.path.basename(video_path)}"
            log.step("ig_upload", "INFO", message="ngrok tunnel ready", public_url=video_url)

        log.step("ig_upload", "INFO", message="Uploading to Instagram...", video_url=video_url[:80], caption_preview=caption[:60])

        # Step 1: Create media container
        container_id = _create_media_container(video_url, caption, access_token)

        # Step 2: Wait for container to finish processing
        _wait_for_container(container_id, access_token)

        # Step 3: Publish
        pub_id = _publish_reel(container_id, access_token)

        log.step("ig_upload", "OUT", message="Reel uploaded to Instagram!", container_id=container_id, publishing_id=pub_id)
        return pub_id or container_id

    finally:
        # Clean up ngrok and local server
        if ngrok_proc:
            try:
                ngrok_proc.terminate()
                ngrok_proc.wait(timeout=5)
            except Exception:
                pass
        if server:
            try:
                server.shutdown()
            except Exception:
                pass
