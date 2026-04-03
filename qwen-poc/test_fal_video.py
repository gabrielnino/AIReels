import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()

print("=" * 45)
print("  TEST: fal.ai video_service")
print("=" * 45)

from service.video_service import _get_api_key, _get_headers, submit_video_task, poll_video_task, download_video

# 1. API Key
key = _get_api_key()
print(f"[1] API Key:    OK ({key[:10]}...)")

# 2. Headers
headers = _get_headers()
print(f"[2] Headers:    OK")

# 3. Submit task
print(f"[3] Submitting task to fal.ai (480p, 3s)...")
task = submit_video_task(
    img_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=720&q=80",
    prompt="gentle motion, cinematic camera pan, soft natural light",
    resolution="480p",
    duration=3
)
print(f"[3] request_id: {task['request_id']}")

# 4. Poll
print(f"[4] Polling task status...")
video_url = poll_video_task(task, timeout=300, interval=8)
print(f"[4] video_url:  {video_url[:80]}...")

# 5. Download
path = download_video(video_url)
print(f"[5] Saved to:   {path}")

print()
print("=" * 45)
print("  ALL TESTS PASSED")
print("=" * 45)
